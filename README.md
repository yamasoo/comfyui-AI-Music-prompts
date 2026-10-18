# ACE-Step 1.5 Auto-Producer

專為 ComfyUI 設計的 AI 音樂生成輔助節點：自動產生自然語言音樂 Prompt、支援多語言歌詞，並把生成結果連同封面與 metadata 一起保存。適用於 ACE-Step 1.5 與 YuE2 工作流程。

- 範例工作流程：[`example_workflows/yue2-with-cover_V02.json`](example_workflows/yue2-with-cover_V02.json)（說明見 [RELEASE_YUE2_WITH_COVER_V02.md](RELEASE_YUE2_WITH_COVER_V02.md)）
- 版本紀錄：[CHANGELOG.md](CHANGELOG.md)

## 功能亮點

- 自動生成專業風格的音樂 Prompt（61 種曲風 × 22 種情緒）
- 支援英文 / 繁體中文 / 日本語歌詞
- 可選擇 Full Lyrics、All Lyrics、Instrumental、Choir/Humming
- 可指定 vocal_timbre 與 prompt_style
- 輸出 MP3 / FLAC / MP4，並附同名 `.txt` metadata
- 可接入封面圖：另存 `.png`、嵌入 MP3/FLAC 專輯封面，或做成 YouTube 用的靜態影片 MP4
- 內建 fallback 機制，wildcard JSON 缺失時不會讓節點崩潰

## 安裝方式

1. 將本專案 clone 到 ComfyUI 的 `custom_nodes` 資料夾（或用 ComfyUI Manager 安裝）。
2. 安裝依賴（ComfyUI Manager 會自動處理）：
   ```bash
   pip install -r requirements.txt
   ```
   `av` 為必要套件；`mutagen` 用於把封面嵌入 MP3/FLAC，未安裝時封面仍會另存為 `.png`。
3. （選用）要使用真實歌詞，請把 `lyrics_wildcards_zh.7z` 解壓縮到本節點資料夾，解壓後應得到 `lyrics_wildcards_zh/` 資料夾。英文與日文歌詞請以相同方式放入 `lyrics_wildcards_en/`、`lyrics_wildcards_jp/`。沒有歌詞資料夾時，節點會改用內建的 fallback 歌詞。
4. 重新啟動 ComfyUI，在節點面板搜尋：
   - **ACE-Step 1.5 Prompt Generator**
   - **ACE-Step Audio & Metadata Saver**

範例工作流程放在 `example_workflows/`，新版 ComfyUI 會在範本瀏覽器中直接列出。

## 節點列表

### 1) 🎵 ACE-Step 1.5 Prompt Generator（`AceStep15PromptGenerator`）

用途：產生 Prompt、BPM、Key、Language、Genre、Mood 與歌詞內容。

| 輸入 | 說明 |
| --- | --- |
| seed | 固定種子可重現結果 |
| genre / mood | 曲風與情緒，`Random` 隨機 |
| vocal_mode | Full Lyrics、All Lyrics、Instrumental、Choir/Humming |
| language | en / zh / jp / Random |
| prompt_style | Prompt 句型風格 |
| vocal_timbre | 人聲音色 |
| extra_prompt | 附加在 Prompt 結尾的文字（選填） |

輸出：`prompt`、`lyrics`、`bpm`、`keyscale`、`language`、`genre`、`mood`

### 2) 💾 ACE-Step Audio & Metadata Saver（`AceStepAudioTextSaver`）

用途：將音訊、封面與 metadata 一併保存到輸出資料夾。

| 輸入 | 說明 |
| --- | --- |
| audio | 要保存的音訊 |
| genre / mood / language / bpm / keyscale / prompt / lyrics | 寫入檔名與 `.txt` metadata |
| output_format | `mp3`（320 kbps）、`flac`、`mp4`（靜態封面 + AAC，需接 `image`） |
| sub_folder | ComfyUI output 底下的子資料夾（選填，預設 `AceStep_Output`） |
| image | 封面圖（選填） |
| embed_cover | 是否把封面嵌入 MP3/FLAC（選填，預設開啟） |

輸出：`audio`（原樣傳出，可接續其他節點）

輸出範例（`output_format = flac`，有接封面）：

```text
ComfyUI/output/AceStep_Output/
├── Pop_Happy_en_001.flac   ← 已嵌入封面
├── Pop_Happy_en_001.png
└── Pop_Happy_en_001.txt
```

檔名編號會跨格式共用，切換 mp3 / flac / mp4 時不會覆蓋前一首的 `.txt` 或 `.png`。

## metadata 格式

`.txt` 內容包含：Genre、Mood、Language、BPM、Key、Prompt、Lyrics。

## wildcards / lyrics JSON

當 vocal_mode 為 Full Lyrics 或 All Lyrics 時，節點會讀取 `lyrics_wildcards_en` / `lyrics_wildcards_zh` / `lyrics_wildcards_jp` 下的 JSON 檔案（安裝步驟 3）。

找不到對應檔案或 JSON 內容錯誤時，會改用 fallback 歌詞，並在主控台對每組「語言 + 模式 + 曲風」提示一次。需要追查路徑時，可把 `AceStep15Generator.py` 中的 `DEBUG_WILDCARD` 改為 `True`，主控台會列出每個搜尋過的目錄與檔名。

新增曲風時，請在 `prompt_data.py` 的 `GENRE_DATA` / `MOOD_DATA` 加入定義，並放上對應的 wildcard JSON。

## 常見問題

### 1) 找不到 JSON 檔

通常是因為目錄名稱不一致、檔名大小寫不同，或 genre 名稱與 JSON 檔名略有差異。節點已內建候選檔名解析，能容忍小幅差異；仍找不到時請開啟 `DEBUG_WILDCARD` 檢查。

### 2) 節點載入失敗

請確認：

- 資料夾位於 `custom_nodes` 下
- 已執行 `pip install -r requirements.txt`
- 主控台沒有 `❌ ACE-Step 1.5 Load Failed` 及其後的錯誤訊息

### 3) 封面沒有嵌入 MP3/FLAC

請確認已安裝 `mutagen`，且 `embed_cover` 為開啟狀態。未安裝時主控台會提示，封面仍會另存為 `.png`。

### 4) Prompt 或歌詞不符合預期

請確認 genre、mood、language（en / zh / jp）與 vocal_mode 的設定，以及歌詞資料夾是否已解壓縮。

## 相關工具

`dist/` 內的 AI Music Pro 桌面播放器可依 `.txt` metadata 篩選與播放生成的曲目，執行檔請至 [Releases](https://github.com/yamasoo/comfyui-AI-Music-prompts/releases) 下載。
