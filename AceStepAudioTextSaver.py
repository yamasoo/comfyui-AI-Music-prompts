import os
import folder_paths
import numpy as np
import torch
import av  

class AceStepAudioTextSaver:
    @classmethod
    def INPUT_TYPES(s):
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
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "save_all"
    OUTPUT_NODE = True
    CATEGORY = "AceStep/Audio"

    def save_all(self, audio, genre, mood, language, bpm, keyscale, prompt, lyrics, sub_folder):

        # 1. 取得 ComfyUI 標準輸出目錄
        output_dir = folder_paths.get_output_directory()

        full_output_path = os.path.join(output_dir, sub_folder)
        os.makedirs(full_output_path, exist_ok=True)

        # 2. 自動編號檔名
        prefix = f"{genre}_{mood}_{language}_"

        try:
            existing = [
                f for f in os.listdir(full_output_path)
                if f.startswith(prefix) and f.endswith(".mp3")
            ]
            indices = [
                int(f.split('_')[-1].replace('.mp3', ''))
                for f in existing
                if f.split('_')[-1].replace('.mp3', '').isdigit()
            ]
            next_idx = max(indices) + 1 if indices else 1
        except:
            next_idx = 1

        filename = f"{prefix}{next_idx:03d}.mp3"
        txt_filename = filename.replace(".mp3", ".txt")

        full_audio_path = os.path.join(full_output_path, filename)
        full_text_path = os.path.join(full_output_path, txt_filename)

        # 3. 音頻處理
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        # 保證 tensor 形狀正確
        if waveform.dim() == 3:
            waveform = waveform.squeeze(0)

        audio_data = waveform.detach().cpu().float()

        container = av.open(full_audio_path, mode='w', format="mp3")
        stream = container.add_stream("mp3", rate=sample_rate)
        stream.bit_rate = 320000

        layout = "stereo" if audio_data.shape[0] == 2 else "mono"

        frame = av.AudioFrame.from_ndarray(
            audio_data.numpy(),
            format="fltp",
            layout=layout
        )
        frame.sample_rate = sample_rate

        for packet in stream.encode(frame):
            container.mux(packet)

        for packet in stream.encode():
            container.mux(packet)

        container.close()

        # 4. 儲存 metadata 文字
        metadata_content = (
            f"Genre: {genre}\n"
            f"Mood: {mood}\n"
            f"Language: {language}\n"
            f"BPM: {bpm}\n"
            f"Key: {keyscale}\n\n"
            f"[Prompt]:\n{prompt}\n\n"
            f"[Lyrics]:\n{lyrics}"
        )

        with open(full_text_path, "w", encoding="utf-8") as f:
            f.write(metadata_content)

        # ★ 必須回傳 tuple（不能是 None）
        return ()