<p align="center">
  <img src="front/public/icon.png" width = "150" height = "auto"/>
</p>
<h1 align="center">YouTube Download WebUI</h1>

<p align="center">
一個基於 FastAPI + React 的 YouTube 影片與音訊下載網頁介面。
</p>

<div align="center">

![Stars](https://img.shields.io/github/stars/NotKeKe/YouTube-Download-WebUI?style=social)

[![License](https://img.shields.io/badge/license-Apache%20License%202.0-yellow)](LICENSE) <br>
[![Docs](https://img.shields.io/badge/Docs-简体中文-blue.svg)](docs/README_simp_chinese.md) 
[![Docs](https://img.shields.io/badge/Docs-English-blue.svg)](docs/README_en.md)

</div>

## ✨ 特色

- **影片下載**：支援下載 YouTube 影片。
- **音訊下載**：可單獨提取並下載音訊。
- **現代化介面**：乾淨、直觀的網頁操作體驗。
- **雙媒體下載核心**：使用 **yt-dlp + pytubefix**。在 yt-dlp 失效時，自動切換為 pytubefix 以提供穩定的下載體驗。
- **Docker 支援**：提供 Docker 映像檔，便於部署。
- **自動開啟**：啟動程式時自動開啟瀏覽器 (在非 Docker 環境時生效)。

## 🚀 快速開始

<details>
    <summary>🔧 使用非 Docker 環境部署</summary>

### 前置需求
- Python 3.14 (尚未在更低或更高版本測試過相容性)
- Node.js (用於構建前端)
- [uv](https://github.com/astral-sh/uv)

### 1. 安裝與構建前端

首先進入前端目錄並安裝相依套件：

```bash
cd front
npm install
```

構建生產環境檔案：

```bash
npm run build
```

### 2. 設定後端環境

回到專案根目錄，使用 `uv` 同步環境與安裝相依套件：

```bash
cd ..
uv sync
```

### 3. 啟動應用程式

執行主程式：

```bash
uv run main.py
```

程式啟動後，瀏覽器應會自動開啟 `http://localhost:8127`

</details>

<details>
    <summary>🐳 使用 Docker 部署</summary>

### 方式 A：直接運行
直接使用 docker run 運行：
```bash
docker run -d \
  -p 8127:8127 \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  --name yt-download-webui \
  ghcr.io/notkeke/youtube-download-webui:latest
```
<small>注意：請確保 data 與 logs 資料夾存在，否則會導致容器無法正常運行。</small>

### 方式 B：使用 Docker Compose 自行編譯
1. **Clone 專案後，請先手動創建 data 與 logs 資料夾：**
   ```bash
   mkdir data logs
   ```
2. **在終端執行：**
   ```bash
   docker-compose up -d
   ```

</details>

## ⚠️ 免責聲明
本專案僅供**學習用途**，請勿用於商業用途或將其暴露於公共網絡上。
如果使用者做出了任何違法之行為，本專案的開發者不負任何法律責任。

## 📄 授權
[Apache License 2.0](LICENSE)