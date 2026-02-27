import os
import folder_paths
import numpy as np
import torch
import av  

class AceStepAudioTextSaver:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

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

    # 修改 1: 雖然是存檔節點，但回傳 UI 數據需要定義 return_types
    # 我們可以回傳原本的 AUDIO，方便鏈接其他節點
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "save_all"
    OUTPUT_NODE = True  # 這點非常重要，標記為輸出節點
    CATEGORY = "AceStep/Audio"

    def save_all(self, audio, genre, mood, language, bpm, keyscale, prompt, lyrics, sub_folder):
        # 1. 處理路徑
        full_output_path = os.path.join(self.output_dir, sub_folder)
        os.makedirs(full_output_path, exist_ok=True)

        # 2. 自動編號檔名邏輯 (保持你的原始邏輯)
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

        # 3. 音頻處理與存檔 (PyAV)
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

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

        # 修改 2: 回傳關鍵的 UI 字典
        # filename 必須是相對於 output 目錄的相對路徑
        return {
            "ui": {
                "audio": [
                    {
                        "filename": filename,
                        "subfolder": sub_folder,
                        "type": self.type
                    }
                ]
            },
            "result": (audio,) 
        }

# 記得在 __init__.py 中註冊此類