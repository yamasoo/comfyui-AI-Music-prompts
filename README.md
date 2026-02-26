# ComfyUI-AI-Music-prompts (ACE-Step 1.5)

這是一個專為 **ACE-Step 1.5** 音樂生成模型設計的 ComfyUI 擴充節點。它能自動生成高質量的自然語言 Prompt，並支持多語言歌詞與自動化存檔功能。

## ✨ 功能亮點
- **專業級 Prompt 生成**：針對 16 種不同音樂曲風（如 Pop, Rock, Lo-fi, Metal 等）自動適配 BPM、樂器組合與動態描述。
- **多語言歌詞支持**：支持 English (EN)、繁體中文 (ZH)、日本語 (JP)，並可透過外部 JSON 詞庫自定義擴充。
- **自動化存檔系統**：一鍵儲存 MP3 音檔與對應的 Metadata（包含歌詞、BPM、Key、Prompt），方便後續管理。
- **防呆機制**：內建備用語料庫，即使外部 JSON 讀取失敗也能正常運作。

## 🛠 安裝方法
1. 進入你的 ComfyUI 安裝目錄下的 `custom_nodes` 資料夾。
2. 開啟終端機並執行：
   ```bash
   git clone https://github.com/yamasoo/comfyui-AI-Music-prompts.git
