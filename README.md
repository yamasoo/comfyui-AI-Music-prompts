v1.1.0 音訊輸出強化與生成流程修正

這次更新主要提升音訊輸出穩定性與功能完整性，新增 MP3 / FLAC / MP4 輸出格式支援，並優化同格式來源直接複製的流程，避免不必要的重編碼與品質損失。

此外，我們也:

強化 prompt 資料載入與 JSON 搜尋可靠性
擴充 genre / mood 資料與歌詞相關支援
改進 waveform、檔名與路徑處理
修正 MP3/FLAC 時間戳與輸出清理問題
整理 README 文件，讓工作流程與 fallback 行為更清楚

# ACE-Step 1.5 Auto-Producer

這是一個專為 ComfyUI 設計的 AI 音樂生成輔助節點，能自動產生自然語言 Prompt、支援多語言歌詞、並可將生成結果直接保存為 MP3 與 metadata 文本。

## 功能亮點

- 自動生成專業風格的音樂 Prompt
- 支援多種音樂曲風與情緒設定
- 支援英文 / 繁體中文 / 日本語
- 可選擇 Full Lyrics、All Lyrics、Instrumental、Choir/Humming
- 可輸入 vocal_timbre 與 prompt_style
- 可將生成結果直接輸出為 MP3 與 .txt metadata
- 內建 fallback 機制，避免 wildcard JSON 缺失時直接崩潰

## 節點列表

### 1) AceStep15PromptGenerator

用途：產生 Prompt、BPM、Key、Language、Genre、Mood 與歌詞內容。

輸入：
- seed
- genre
- mood
- vocal_mode
- language
- prompt_style
- vocal_timbre
- extra_prompt

輸出：
- prompt
- lyrics
- bpm
- keyscale
- language
- genre
- mood

### 2) AceStepAudioTextSaver

用途：將音訊與 metadata 一併保存到輸出資料夾。

輸入：
- audio
- genre
- mood
- language
- bpm
- keyscale
- prompt
- lyrics
- sub_folder

輸出：
- audio

## 安裝方式

1. 將本專案放進 ComfyUI 的 custom_nodes 資料夾。
2. 確認已安裝依賴：
   ```bash
   pip install av
   ```
3. 啟動 ComfyUI 後，在節點面板中搜尋：
   - ACE-Step 1.5 Auto-Producer
   - ACE-Step Audio & Metadata Saver

## 使用流程

1. 先使用 AceStep15PromptGenerator 產生 Prompt 與 Lyrics。
2. 將輸出接到後續的音樂生成流程。
3. 以音訊輸出接到 AceStepAudioTextSaver。
4. 儲存後，系統會自動生成：
   - .mp3
   - 同名 .txt metadata 檔

## metadata 格式

產生的 .txt 內容會包含：
- Genre
- Mood
- Language
- BPM
- Key
- Prompt
- Lyrics

## wildcards / lyrics JSON

當 vocal_mode 為 Full Lyrics 或 All Lyrics 時，系統會嘗試讀取 lyrics_wildcards_en / lyrics_wildcards_zh / lyrics_wildcards_jp 下的 JSON 檔案。

如果找不到對應檔案或 JSON 內容錯誤，會自動使用 fallback 歌詞，不會導致整個節點失效。

## 常見問題

### 1) 找不到 JSON 檔

這通常是因為：
- 目錄名稱不一致
- 檔名大小寫不同
- genre 名稱與實際 JSON 檔名略有差異

現在已增加 fallback 與候選檔名解析，能容忍小幅差異。

### 2) 節點載入失敗

請確認：
- 檔案位於 custom_nodes 下
- Python 可正常 import 本模組
- 沒有語法錯誤
- av 套件已安裝

### 3) Prompt 或歌詞不符合預期

請確認：
- genre 是否為可用值
- mood 是否為可用值
- language 是否為 en / zh / jp
- vocal_mode 是否正確

## 注意事項

- 本插件依賴 ComfyUI 的節點執行環境。
- 若你自行新增曲風或歌詞 JSON，建議維持清楚的命名規則。
- 若要長期維護，建議將 wildcards JSON 做成穩定命名與資料結構規範。

## 結論

這個專案的核心價值在於：
- 將 AI 音樂創作流程自動化
- 讓 Prompt 與 Lyrics 能更可控
- 並保留可維護與可擴充的結構

如需擴充曲風或語言，請直接新增對應的 genre 定義與 wildcard JSON。
