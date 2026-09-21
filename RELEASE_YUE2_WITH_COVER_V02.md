# YuE2 with Cover V02 發布說明

## 版本資訊

- 版本：V02
- 工作流程：`yue2-with-cover_V02.json`
- 類型：ComfyUI workflow
- 主題：YuE2 音樂生成與 Anima-Base-1.0 封面生成
- 預設音訊格式：FLAC
- 預設輸出資料夾：`yue2`
- 影像尺寸：1280 × 720（16:9）

## 版本摘要

V02 是 YuE2 音樂與封面生成流程的簡化修正版。此版本保留 ACE-Step 1.5 Prompt Generator、YuE2 音樂生成與 metadata 保存流程，並將封面生成鏈路改為 Anima-Base-1.0，移除不必要的 LoRA 與快取節點，降低外部模型依賴，使流程更容易安裝、移植與維護。

## 主要功能

- 使用 ACE-Step 1.5 自動產生音樂風格 Prompt、歌詞、BPM、Key、語言、曲風與情緒資訊。
- 透過 YuE2 生成最長約 300 秒的音樂內容。
- 支援 ABC planning 與 YuE2 full generation 模式。
- 使用 DeepSeek 將音樂風格與歌詞整理為封面生成 Prompt。
- 使用 Anima-Base-1.0 生成 1280 × 720 的 16:9 封面圖。
- 將音訊、Prompt、歌詞與生成 metadata 交由 ACE-Step Audio & Metadata Saver 保存。
- 預設產生 FLAC 音訊、同名 TXT metadata，以及 PNG 封面圖。
- 使用集中式 seed 控制，方便重現或重新隨機生成結果。

## V02 變更內容

### 封面生成流程

- 將封面生成模型由舊版流程改為 `anima-base-v1.0.safetensors`。
- 移除 `WanCacheOptimizer`。
- 移除兩個 `LoraLoaderModelOnly` 節點及其外部 LoRA 依賴。
- 保留標準的 UNet、CLIP、VAE、KSampler 與 VAE Decode 流程。
- 將封面生成流程收斂為較簡單、可攜性更高的 Anima-Base pipeline。

### Prompt 整理流程

- 新增並標示 `LLM graphic prompting` 子流程。
- 使用 `StringConcatenate` 將音樂風格與歌詞資料組合後送入 DeepSeek。
- 由 DeepSeek 產生藝術風格、Danbooru tags 與構圖說明。
- 封面 Prompt 規則要求優先使用單一主體；純器樂或抽象內容則可使用無人物場景。

### 音樂輸出流程

- 保留 `AceStep15PromptGenerator` 與 `AceStepAudioTextSaver`。
- 預設音訊輸出維持 FLAC。
- metadata 會保存 Genre、Mood、Language、BPM、Key、Prompt 與 Lyrics。
- 封面以獨立 PNG 保存；本版本並未將封面嵌入 MP4。

## 使用到的客製化節點

### 本專案

- `AceStep15PromptGenerator`
- `AceStepAudioTextSaver`

專案：`yamasoo/comfyui-AI-Music-prompts`

### 外部客製化節點

- `DeepSeekChatNode`
  - 用於音樂 Prompt、歌詞與封面 Prompt 的文字處理。
  - 來源：`linjian-ufo/comfyui_deepseek_lj257_update`
- `ShowText|pysssss`
  - 用於預覽音樂 Prompt、歌詞與封面 Prompt。
  - 來源：ComfyUI Custom Scripts。
- `Global Seed Controller (Focus Nodes)`
  - 用於集中管理 seed。
  - 來源：Focus Nodes。
- `StringConcatenate`
  - 用於組合風格 Prompt 與歌詞輸入。
  - 需安裝提供此節點的對應 custom node 套件。

### YuE2 相關節點

工作流程使用以下 YuE2 節點，需使用包含 YuE2 支援的 ComfyUI 版本或相關擴充：

- `YuE2GenerateABC`
- `YuE2GenerateMusic`
- `EmptyYuE2LatentAudio`
- `VAEDecodeAudio`

## 需要的模型

### YuE2

```text
yue2_3b_int8_convrot.safetensors
```

### Anima-Base

```text
anima-base-v1.0.safetensors
```

### 文字編碼器與 VAE

工作流程同時使用對應的 CLIP / text encoder 與 VAE。請依本機 ComfyUI 的模型分類與節點清單放置，並確認 workflow 中的模型名稱與實際檔名一致。

## 安裝需求

本專案的音訊保存節點需要 PyAV：

```bash
pip install av
```

此外，使用者必須自行安裝 YuE2、Anima-Base、DeepSeek 節點及其他列出的 custom nodes。DeepSeek 節點通常也需要有效的 API 設定。

## 輸出範例

```text
ComfyUI/output/yue2/
├── Genre_Mood_Language_001.flac
├── Genre_Mood_Language_001.txt
└── Genre_Mood_Language_001.png
```

## 注意事項

- `yue2-with-cover_V02.json` 的封面輸出是 FLAC + PNG，不是 MP4 影片。
- 若缺少 DeepSeek API 或 custom node，封面 Prompt 生成階段將無法執行。
- 若缺少 YuE2 或 Anima-Base 模型，對應的音樂或封面生成階段會失敗。
- workflow 中的 seed 可固定以重現結果，也可設定為 randomize 以產生不同作品。
- 不同 ComfyUI 版本、YuE2 擴充版本或節點版本可能造成介面與模型名稱差異。

## 下載

- Repository：https://github.com/yamasoo/comfyui-AI-Music-prompts
- Workflow：`yue2-with-cover_V02.json`
