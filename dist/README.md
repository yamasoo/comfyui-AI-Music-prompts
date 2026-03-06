# 🎵 AI Music Pro

> 現代玻璃風格桌面音樂播放器，支援智慧曲風篩選、頻譜視覺化與 AI Metadata 解析。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)
![Pygame](https://img.shields.io/badge/Pygame-Audio-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 功能簡介

### 🎧 音樂播放
- 支援 MP3、WAV、OGG、FLAC、M4A 格式
- 播放 / 暫停 / 停止 / 上一首 / 下一首
- 點擊進度條任意位置跳轉（ClickableSlider）
- 音量滑桿即時調整

### 🔁 播放模式
- 不循環 / 清單循環 / 單曲循環 三種模式切換
- 隨機播放（Shuffle），自動避免連續播同一首

### 📂 播放清單管理
- 開啟整個音樂資料夾，自動掃描所有音樂檔案
- 單獨加入多個音樂檔案
- 支援**拖曳檔案或資料夾**直接加入清單
- 儲存 / 載入播放清單（`.json` 格式）
- 自動記錄播放歷史（最近 50 首）

### 🎼 曲風篩選
- 左側面板提供**曲風下拉選單**，依 Genre 快速過濾播放清單
- 選單選項從曲目 Metadata 動態產生，無需手動輸入

### 📝 Metadata 解析
- 自動讀取同名 `.txt` 檔案中的 Metadata：
  - `Genre`（曲風）
  - `BPM`
  - `Artist`（演出者）
  - `Album`（專輯）
  - `Lyrics`（歌詞，顯示前 500 字）
- 支援 [mutagen](https://mutagen.readthedocs.io/) 精確讀取 MP3 播放時長

### 📊 頻譜視覺化
- 即時模擬音頻頻譜波形動畫（Matplotlib）
- 根據音量動態調整波形高度
- 播放中 20fps 更新，停止時歸零

### 🖼️ 背景自訂
- 可設定任意圖片作為視窗背景（PNG / JPG / WEBP / BMP）
- 自動縮放裁切置中，加上半透明遮罩保持可讀性
- 支援拖曳圖片直接設定背景

### 🎚️ 等化器
- 10 段頻率等化器（32Hz ～ 16kHz）
- 獨立浮動視窗，可一鍵重置

### ⚙️ 設定記憶
- 自動儲存音樂目錄、背景圖、音量、循環模式、隨機模式、視窗位置與大小
- 下次啟動自動還原上次狀態（`player_config.json`）

---

## 🖥️ 系統需求

| 項目 | 需求 |
|---|---|
| 作業系統 | Windows 10 / 11（macOS / Linux 未測試） |
| Python | 3.10 以上 |
| 主要套件 | PyQt6、pygame、matplotlib、numpy |
| 選用套件 | mutagen（精確 MP3 長度） |

---

## 🚀 安裝與執行

```bash
# 安裝相依套件
pip install PyQt6 pygame matplotlib numpy mutagen

# 執行
python MP5.py
```

---


## 📁 Metadata 格式範例

與音樂檔案同名的 `.txt` 檔案（例如 `song.mp3` → `song.txt`）：

```
Artist: 演出者名稱
Album: 專輯名稱
Genre: Electronic
BPM: 128

[Lyrics]
歌詞內容寫在這裡...
```

---

## ⌨️ 快捷鍵

| 按鍵 | 功能 |
|---|---|
| `Space` | 播放 / 暫停 |
| `Ctrl + Left` | 上一首 |
| `Ctrl + Right` | 下一首 |

---

## 📜 License

MIT License
