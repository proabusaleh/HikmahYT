# ▶ HikmahYT - Modern Video Downloader

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A beautiful, modern video downloader with a smooth dark UI, playlist 
support, and multiple quality options.

> **"Hikmah"** means *wisdom* in Arabic — Download with Wisdom! ✨

## ✨ Features

- 🌐 **Multi-site Support** — YouTube, Facebook, TikTok, Telegram, Instagram, X/Twitter, Twitch, Vimeo, Dailymotion, Reddit, SoundCloud, Spotify, Tumblr, Bilibili, VK, Rutube, OK.ru & more
- 🎬 **Video Download** — Download videos in 360p to 4K quality
- 🎵 **Audio Extract** — Extract audio as MP3 (128-320kbps)
- 📋 **Playlist Support** — Download entire playlists with selective video picking
- 🎨 **Modern Dark UI** — Beautiful, smooth interface with hover effects
- 📊 **Real-time Progress** — Live download speed, ETA, and progress tracking
- 📁 **Custom Save Location** — Choose where to save your downloads
- 🔍 **Video Preview** — See video details before downloading

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/HikmahYT.git
cd HikmahYT
```

### 2. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Run from source
```bash
python main.py
```

## 📦 Build (Windows)

Requires Python 3.10+ with PyInstaller.

```bash
build.bat
```

Or manually:

```bash
python -m pip install -r requirements.txt -r requirements-build.txt
python -m PyInstaller --noconfirm --clean HikmahYT.spec
```

The executable is written to `dist\HikmahYT\HikmahYT.exe` and packaged as
`dist\HikmahYT-v1.0.0-win64.zip`. The build bundles yt-dlp (with all
extractors), an ffmpeg binary (via imageio-ffmpeg), and pycryptodomex for
reliable YouTube signature deciphering — no runtime dependencies required.

> **Note:** the exe needs the `_internal` folder beside it. Keep the whole
> `dist\HikmahYT` folder together (or use the zip). The `HikmahYT.exe` under
> the intermediate `build\` folder is NOT runnable — always run from `dist`.