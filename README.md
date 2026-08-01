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

### Option A — Prebuilt Windows app (recommended)
1. Download the latest release zip (`HikmahYT-v1.0.0-win64.zip`) from the
   [Releases](https://github.com/mdabusaleh1/HikmahYT/releases) page.
2. Extract the zip anywhere (e.g. `C:\Programs\HikmahYT` or your Desktop).
3. Run `HikmahYT.exe`. No Python or other software is required.

> First launch may show a Windows SmartScreen warning (the app is not
> code-signed). Click **More info → Run anyway** — it appears only once.

### Option B — Run from source
```bash
git clone https://github.com/mdabusaleh1/HikmahYT.git
cd HikmahYT
python -m pip install -r requirements.txt
python main.py
```

## 🎯 How to Use

### Download a video
1. Open the app — the **Home** page is shown.
2. Paste any video URL (YouTube, Facebook, TikTok, Instagram, X/Twitter,
   Twitch, Vimeo, Telegram, etc.) into the box.
3. Click **Analyze** — the app fetches the title, thumbnail, duration,
   views and all available formats.
4. Pick a format:
   - ⚡ **Best Quality (Auto)** — fastest choice
   - 🎬 a specific resolution (e.g. **1080p**, **4K**) — shows file size and
     fps; entries marked *(merge)* combine separate video + audio streams
   - 🎵 an audio-only option (MP3 128–320 kbps)
5. Click **Download Now**. A progress card shows speed, ETA and percentage.
6. When it finishes, the file is saved to your download folder (default
   `~/Downloads/HikmahYT`).

### Download a playlist
1. Click **Playlist** in the sidebar (or paste a playlist URL on the Home page
   — it is detected automatically).
2. Paste the playlist URL and click **Load Playlist**.
3. Use **Select All** / **Deselect All** or toggle individual videos.
4. Choose a format and click **Download N Videos**. Files are saved in a
   subfolder named after the playlist.

### Change where files are saved
1. Open **Settings** → **Download Location** → **Change**.
2. Pick any folder. The choice applies to all future downloads.

### Switch theme
- **Settings** → **Theme Mode** → `Dark`, `Light`, or `System`.

### View completed downloads
- The **Downloads** page lists finished files; **Open Folder** jumps to them.

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

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| "Windows protected your PC" on first run | **More info → Run anyway** (unsigned app; appears once) |
| "The specified module could not be found" | You launched the wrong exe or moved `HikmahYT.exe` without its `_internal` folder. Run from the extracted folder. |
| Downloads keep failing / site requires login | Use the **Run from source** option, then `python -m pip install -U yt-dlp` for the latest extractors. |
| Low-quality or missing resolution | Pick ⚡ **Best Quality** — some sites only expose what the player offers. |
| "ffmpeg is required..." error | The build bundles ffmpeg; if running from source, install `imageio-ffmpeg` (already in `requirements.txt`). |

## ⚠️ Legal Notice

Only download content you have the right to, and respect each site's Terms of
Service and the copyright laws of your country.

## 🤝 License

[MIT](LICENSE)