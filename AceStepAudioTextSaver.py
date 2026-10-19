import io
import math
import os
import re
import shutil
from fractions import Fraction

import av
import folder_paths
import numpy as np
import torch
from PIL import Image

SUPPORTED_FORMATS = ("mp3", "flac", "mp4")
# Every file that shares a base name with a saved track. The index is shared
# across all of them so that switching formats never reuses an existing number
# (which would overwrite the previous track's .txt / .png).
SIDECAR_EXTENSIONS = SUPPORTED_FORMATS + ("txt", "png")


class AceStepAudioTextSaver:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "genre": ("STRING", {"forceInput": True}),
                "mood": ("STRING", {"forceInput": True}),
                "language": ("STRING", {"forceInput": True}),
                "bpm": ("INT", {"forceInput": True}),
                "keyscale": ("STRING", {"forceInput": True}),
                "prompt": ("STRING", {"forceInput": True}),
                "lyrics": ("STRING", {"forceInput": True}),
                "output_format": (list(SUPPORTED_FORMATS), {"default": "mp3"}),
            },
            "optional": {
                "sub_folder": ("STRING", {"default": "AceStep_Output"}),
                "image": ("IMAGE", {"tooltip": "Cover image. Saved as a .png next to the track; "
                                               "embedded as album art for mp3/flac and used as the "
                                               "video frame for mp4 (mp4 requires it)."}),
                "embed_cover": ("BOOLEAN", {"default": True,
                                            "tooltip": "Embed the cover into mp3/flac files (needs mutagen)."}),
                "fade_out_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 30.0, "step": 0.5,
                                               "tooltip": "Fade the last N seconds to silence before saving "
                                                          "(0 = off). Gives tracks cut off by YuE2's "
                                                          "max_duration a clean ending; tracks that already "
                                                          "end quietly are barely affected."}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "save_all"
    OUTPUT_NODE = True
    CATEGORY = "AceStep/Audio"

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _safe_component(value, fallback="unknown"):
        """Make metadata suitable for use in a filename."""
        value = str(value or "").strip()
        value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value)
        value = re.sub(r"\s+", "_", value)
        value = value.strip("._")
        return value or fallback

    def _safe_subfolder(self, sub_folder):
        """Allow nested output folders without permitting path traversal."""
        sub_folder = str(sub_folder or "AceStep_Output").strip()
        normalized = os.path.normpath(sub_folder)
        if os.path.isabs(normalized) or normalized in (".", "..") or normalized.startswith(".." + os.sep):
            raise ValueError("sub_folder must stay inside ComfyUI's output directory")
        return normalized

    @staticmethod
    def _next_index(output_dir, prefix):
        """Next free index for ``prefix``, counting every format and sidecar file."""
        extensions = "|".join(re.escape(ext) for ext in SIDECAR_EXTENSIONS)
        pattern = re.compile(r"^" + re.escape(prefix) + r"(\d+)\.(?:" + extensions + r")$", re.IGNORECASE)
        indices = []
        for name in os.listdir(output_dir):
            match = pattern.match(name)
            if match:
                indices.append(int(match.group(1)))
        return max(indices, default=0) + 1

    @staticmethod
    def _normalise_waveform(waveform):
        """Convert common ComfyUI AUDIO shapes to [channels, samples]."""
        if waveform.dim() == 3:
            if waveform.shape[0] != 1:
                raise ValueError(f"Expected a single audio batch, got shape {tuple(waveform.shape)}")
            waveform = waveform.squeeze(0)
        if waveform.dim() != 2:
            raise ValueError(f"Expected waveform with 2 dimensions, got shape {tuple(waveform.shape)}")

        # ComfyUI normally uses [channels, samples]. Handle the common transposed form too.
        if waveform.shape[0] > waveform.shape[1]:
            waveform = waveform.transpose(0, 1)
        if waveform.shape[0] not in (1, 2):
            raise ValueError(f"Expected mono or stereo audio, got shape {tuple(waveform.shape)}")
        return waveform.detach().cpu().float().contiguous()

    @staticmethod
    def _apply_fade_out(audio, seconds):
        """Return a copy of ``audio`` whose last ``seconds`` fade to silence (cosine curve)."""
        sample_rate = int(audio["sample_rate"])
        waveform = audio["waveform"]
        length = waveform.shape[-1]
        n = min(length, int(round(seconds * sample_rate)))
        if n <= 1:
            return audio
        t = torch.linspace(0.0, 1.0, n, dtype=torch.float32, device=waveform.device)
        curve = (0.5 * (1.0 + torch.cos(math.pi * t))).to(waveform.dtype)
        faded = waveform.clone()
        faded[..., length - n:] *= curve
        result = dict(audio)
        result["waveform"] = faded
        # The faded audio no longer matches any source file on disk.
        for key in ("path", "filename", "subfolder"):
            result.pop(key, None)
        return result

    @staticmethod
    def _source_path(audio):
        """Return a source file path when an upstream node provides one."""
        if not isinstance(audio, dict):
            return None
        path = audio.get("path")
        if path and os.path.isfile(path):
            return path
        filename = audio.get("filename")
        if not filename:
            return None
        subfolder = audio.get("subfolder", "")
        for base in (folder_paths.get_input_directory(), folder_paths.get_output_directory()):
            candidate = os.path.join(base, subfolder, filename)
            if os.path.isfile(candidate):
                return candidate
        return None

    # ------------------------------------------------------------------ cover image

    @staticmethod
    def _image_to_array(image):
        """Convert a ComfyUI IMAGE tensor ([B, H, W, C], 0..1) to an RGB uint8 array."""
        if image is None:
            return None
        img = image[0] if image.dim() == 4 else image
        if img.dim() != 3 or img.shape[-1] < 3:
            raise ValueError(f"Expected RGB image with shape [H, W, C], got {tuple(img.shape)}")
        arr = (img.detach().cpu().float().clamp(0, 1).numpy() * 255.0).round().astype(np.uint8)
        return np.ascontiguousarray(arr[..., :3])

    @staticmethod
    def _even_sized(arr):
        """H.264 with yuv420p requires even width and height."""
        if arr.shape[0] % 2:
            arr = arr[:-1]
        if arr.shape[1] % 2:
            arr = arr[:, :-1]
        if arr.shape[0] < 2 or arr.shape[1] < 2:
            raise ValueError("image is too small for MP4 encoding")
        return np.ascontiguousarray(arr)

    @staticmethod
    def _embed_cover(audio_path, output_format, png_bytes, size):
        """Embed a PNG as front-cover art. Never fails the save: the audio is already written."""
        try:
            if output_format == "mp3":
                from mutagen.id3 import APIC, ID3
                from mutagen.mp3 import MP3

                mp3 = MP3(audio_path, ID3=ID3)
                if mp3.tags is None:
                    mp3.add_tags()
                mp3.tags.delall("APIC")
                mp3.tags.add(APIC(encoding=3, mime="image/png", type=3, desc="Cover", data=png_bytes))
                mp3.save()
            elif output_format == "flac":
                from mutagen.flac import FLAC, Picture

                flac = FLAC(audio_path)
                flac.clear_pictures()
                picture = Picture()
                picture.type = 3
                picture.mime = "image/png"
                picture.width, picture.height = size
                picture.depth = 24
                picture.data = png_bytes
                flac.add_picture(picture)
                flac.save()
        except ImportError:
            print("[AceStepAudioTextSaver] mutagen is not installed; cover saved as .png only. "
                  "Run: pip install mutagen")
        except Exception as error:
            print(f"[AceStepAudioTextSaver] Could not embed cover (audio was saved): {error}")

    # ------------------------------------------------------------------ encoders

    @staticmethod
    def _encode_audio(output_path, output_format, waveform, sample_rate):
        layout = "stereo" if waveform.shape[0] == 2 else "mono"
        with av.open(output_path, mode="w", format=output_format) as container:
            stream = container.add_stream(output_format, rate=sample_rate)
            stream.time_base = Fraction(1, sample_rate)
            if output_format == "mp3":
                stream.bit_rate = 320000

            frame = av.AudioFrame.from_ndarray(waveform.numpy(), format="fltp", layout=layout)
            frame.sample_rate = sample_rate
            frame.time_base = Fraction(1, sample_rate)
            frame.pts = 0

            for packet in stream.encode(frame):
                container.mux(packet)
            for packet in stream.encode():
                container.mux(packet)

    @staticmethod
    def _encode_mp4(output_path, waveform, sample_rate, image_np, fps=1):
        """Encode a static-image + audio MP4 suitable for YouTube uploads."""
        duration = waveform.shape[1] / float(sample_rate)
        n_frames = max(1, int(round(duration * fps)))
        layout = "stereo" if waveform.shape[0] == 2 else "mono"
        h, w = image_np.shape[:2]

        with av.open(output_path, mode="w", format="mp4") as container:
            astream = container.add_stream("aac", rate=sample_rate)
            astream.layout = layout
            astream.bit_rate = 192000
            astream.time_base = Fraction(1, sample_rate)

            vstream = container.add_stream("libx264", rate=fps)
            vstream.width = w
            vstream.height = h
            vstream.pix_fmt = "yuv420p"
            vstream.time_base = Fraction(1, fps)
            vstream.options = {"preset": "medium", "crf": "20"}

            aframe = av.AudioFrame.from_ndarray(waveform.numpy(), format="fltp", layout=layout)
            aframe.sample_rate = sample_rate
            aframe.time_base = Fraction(1, sample_rate)
            aframe.pts = 0
            for packet in astream.encode(aframe):
                container.mux(packet)
            for packet in astream.encode():
                container.mux(packet)

            # The picture never changes, so convert it to yuv420p once and reuse it.
            yuv_planes = av.VideoFrame.from_ndarray(image_np, format="rgb24").reformat(format="yuv420p").to_ndarray()
            for i in range(n_frames):
                frame = av.VideoFrame.from_ndarray(yuv_planes, format="yuv420p")
                frame.pts = i
                frame.time_base = Fraction(1, fps)
                for packet in vstream.encode(frame):
                    container.mux(packet)
            for packet in vstream.encode():
                container.mux(packet)

    # ------------------------------------------------------------------ main

    def save_all(self, audio, genre, mood, language, bpm, keyscale, prompt, lyrics,
                 output_format="mp3", sub_folder="AceStep_Output", image=None, embed_cover=True,
                 fade_out_seconds=0.0):
        output_format = str(output_format or "mp3").lower().lstrip(".")
        if output_format not in SUPPORTED_FORMATS:
            raise ValueError("output_format must be mp3, flac, or mp4")

        if not isinstance(audio, dict) or "waveform" not in audio or "sample_rate" not in audio:
            raise ValueError("audio must contain waveform and sample_rate")

        if fade_out_seconds and fade_out_seconds > 0:
            audio = self._apply_fade_out(audio, float(fade_out_seconds))

        safe_subfolder = self._safe_subfolder(sub_folder)
        full_output_path = os.path.join(self.output_dir, safe_subfolder)
        os.makedirs(full_output_path, exist_ok=True)

        prefix = "{}_{}_{}_".format(
            self._safe_component(genre),
            self._safe_component(mood),
            self._safe_component(language),
        )
        base_name = f"{prefix}{self._next_index(full_output_path, prefix):03d}"
        filename = f"{base_name}.{output_format}"
        png_filename = f"{base_name}.png"
        full_audio_path = os.path.join(full_output_path, filename)
        full_text_path = os.path.join(full_output_path, f"{base_name}.txt")
        full_png_path = os.path.join(full_output_path, png_filename)

        cover_np = self._image_to_array(image)

        # An encoded source can be copied without decoding/re-encoding when its
        # extension matches the requested output format.
        source_path = self._source_path(audio)
        source_format = os.path.splitext(source_path)[1].lower().lstrip(".") if source_path else None

        try:
            if source_path and source_format == output_format and (output_format != "mp4" or cover_np is None):
                shutil.copyfile(source_path, full_audio_path)
            else:
                if output_format == "mp4" and cover_np is None:
                    raise ValueError("MP4 output requires an 'image' input "
                                     "(an upstream MP4 source can be copied as-is instead)")
                waveform = self._normalise_waveform(audio["waveform"])
                sample_rate = int(audio["sample_rate"])
                if sample_rate <= 0:
                    raise ValueError(f"Invalid sample rate: {sample_rate}")
                if output_format == "mp4":
                    self._encode_mp4(full_audio_path, waveform, sample_rate, self._even_sized(cover_np))
                else:
                    self._encode_audio(full_audio_path, output_format, waveform, sample_rate)
        except Exception:
            # Do not leave a misleading partial file behind after an encode failure.
            if os.path.exists(full_audio_path):
                os.remove(full_audio_path)
            raise

        ui = {"audio": [{"filename": filename, "subfolder": safe_subfolder, "type": self.type}]}

        if cover_np is not None:
            cover = Image.fromarray(cover_np, "RGB")
            cover.save(full_png_path, format="PNG")
            ui["images"] = [{"filename": png_filename, "subfolder": safe_subfolder, "type": self.type}]
            if embed_cover and output_format in ("mp3", "flac"):
                buffer = io.BytesIO()
                cover.save(buffer, format="PNG")
                self._embed_cover(full_audio_path, output_format, buffer.getvalue(), cover.size)

        metadata_content = (
            f"Genre: {genre}\n"
            f"Mood: {mood}\n"
            f"Language: {language}\n"
            f"BPM: {bpm}\n"
            f"Key: {keyscale}\n\n"
            f"[Prompt]:\n{prompt}\n\n"
            f"[Lyrics]:\n{lyrics}"
        )
        with open(full_text_path, "w", encoding="utf-8") as file:
            file.write(metadata_content)

        return {"ui": ui, "result": (audio,)}


NODE_CLASS_MAPPINGS = {
    "AceStepAudioTextSaver": AceStepAudioTextSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceStepAudioTextSaver": "💾 ACE-Step Audio & Metadata Saver",
}
