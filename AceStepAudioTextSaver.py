import os
import re

import av
import folder_paths


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
            },
            "optional": {
                "sub_folder": ("STRING", {"default": "AceStep_Output"}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "save_all"
    OUTPUT_NODE = True
    CATEGORY = "AceStep/Audio"

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
        pattern = re.compile(r"^" + re.escape(prefix) + r"(\d+)\.mp3$")
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

    def save_all(self, audio, genre, mood, language, bpm, keyscale, prompt, lyrics, sub_folder="AceStep_Output"):
        safe_subfolder = self._safe_subfolder(sub_folder)
        full_output_path = os.path.join(self.output_dir, safe_subfolder)
        os.makedirs(full_output_path, exist_ok=True)

        prefix = "{}_{}_{}_".format(
            self._safe_component(genre),
            self._safe_component(mood),
            self._safe_component(language),
        )
        next_idx = self._next_index(full_output_path, prefix)
        filename = f"{prefix}{next_idx:03d}.mp3"
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        full_audio_path = os.path.join(full_output_path, filename)
        full_text_path = os.path.join(full_output_path, txt_filename)

        if not isinstance(audio, dict) or "waveform" not in audio or "sample_rate" not in audio:
            raise ValueError("audio must contain waveform and sample_rate")
        waveform = self._normalise_waveform(audio["waveform"])
        sample_rate = int(audio["sample_rate"])
        if sample_rate <= 0:
            raise ValueError(f"Invalid sample rate: {sample_rate}")

        layout = "stereo" if waveform.shape[0] == 2 else "mono"
        try:
            with av.open(full_audio_path, mode="w", format="mp3") as container:
                stream = container.add_stream("mp3", rate=sample_rate)
                stream.bit_rate = 320000
                frame = av.AudioFrame.from_ndarray(
                    waveform.numpy(),
                    format="fltp",
                    layout=layout,
                )
                frame.sample_rate = sample_rate
                for packet in stream.encode(frame):
                    container.mux(packet)
                for packet in stream.encode():
                    container.mux(packet)
        except Exception:
            # Do not leave a misleading partial MP3 behind after an encode failure.
            if os.path.exists(full_audio_path):
                os.remove(full_audio_path)
            raise

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

        return {
            "ui": {
                "audio": [
                    {
                        "filename": filename,
                        "subfolder": safe_subfolder,
                        "type": self.type,
                    }
                ]
            },
            "result": (audio,),
        }


NODE_CLASS_MAPPINGS = {
    "AceStepAudioTextSaver": AceStepAudioTextSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceStepAudioTextSaver": "💾 ACE-Step Audio & Metadata Saver",
}
