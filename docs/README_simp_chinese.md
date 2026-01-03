<p align="center">
  <img src="../front/public/icon.png" width = "150" height = "auto"/>
</p>
<h1 align="center">YouTube Download WebUI</h1>

<p align="center">
一个基于 FastAPI + React 的 YouTube 视频与音频下载网页界面。
</p>

<div align="center">

![Stars](https://img.shields.io/github/stars/NotKeKe/YouTube-Download-WebUI?style=social)

[![License](https://img.shields.io/badge/license-Apache%20License%202.0-yellow)](../LICENSE) <br>
[![Docs](https://img.shields.io/badge/Docs-繁體中文-blue.svg)](../README.md) 
[![Docs](https://img.shields.io/badge/Docs-English-blue.svg)](README_en.md)

</div>

## ✨ 特色

- **视频下载**：支持下载 YouTube 视频。
- **音频下载**：可单独提取并下载音频。
- **现代化界面**：干净、直观的网页操作体验。
- **双媒体下载核心**：使用 **yt-dlp + pytubefix**。在 yt-dlp 失效时，自动切换为 pytubefix 以提供稳定的下载体验。
- **Docker 支持**：提供 Docker 镜像文件，便于部署。
- **自动开启**：启动程序时自动开启浏览器 (在非 Docker 环境时生效)。

## 🚀 快速开始

<details>
    <summary>🔧 使用非 Docker 环境部署</summary>

### 前置需求
- Python 3.14 (尚未在更低或更高版本测试过兼容性)
- Node.js (用于构建前端)
- [uv](https://github.com/astral-sh/uv)

### 1. 安装与构建前端

首先进入前端目录并安装依赖包：

```bash
cd front
npm install
```

构建生产环境文件：

```bash
npm run build
```

### 2. 设置后端环境

回到项目根目录，使用 `uv` 同步环境并安装依赖包：

```bash
cd ..
uv sync
```

### 3. 启动应用程序

执行主程序：

```bash
uv run main.py
```

程序启动后，浏览器应会自动开启 `http://localhost:8127`

</details>

<details>
    <summary>🐳 使用 Docker 部署</summary>

- **clone 项目后，如果缺少 data 与 logs 文件夹，请先手动创建。**
- 在终端使用以下命令:
    ```bash
    docker-compose up -d --build
    ```

</details>

## ⚠️ 免责声明
本项目仅供**学习用途**，请勿用于商业用途或将其暴露于公共网络上。
如果使用者做出了任何违法之行为，本项目的开发者不负任何法律责任。

## 📄 授权
[Apache License 2.0](../LICENSE)
