# ▶ HikmahYT Pro - Modern Video Downloader

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Version](https://img.shields.io/badge/Version-v5%20Pro-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A beautiful, modern video downloader with a smooth dark UI, playlist support,
and deep download options — powered by yt-dlp.

> **"Hikmah"** means *wisdom* in Arabic — Download with Wisdom! ✨

## ✨ Features

**Works with 1000+ sites** — YouTube, Facebook, TikTok, Instagram, X/Twitter,
Twitch, Telegram, Vimeo, Dailymotion, Reddit, Pinterest, LinkedIn, Tumblr,
Flickr, VK, Kick, Rumble, Odysee, SoundCloud, Bandcamp, Mixcloud, YouTube
Music, Internet Archive & more. Paste any URL.

- 🎬 **Full Quality Ladder** — 8K, 4K, 2K, 1080p, 720p, 480p, 360p, 240p, 144p
  plus a full per-resolution format list (size, fps, HDR labels)
- 🎥 **Codec Selection** — H.264 / H.265 / AV1 / VP9 / VP8 with hard format
  sorting
- 🌞 **HDR + 60fps** preferences
- 🎵 **Audio Extract** — MP3, AAC, M4A, OPUS, VORBIS, FLAC, ALAC, WAV
  (128–320 kbps)
- 📦 **Container Conversion** — MP4, MKV, WebM, AVI, MOV, FLV (remux, no
  re-encode)
- 💬 **Subtitles** — manual + auto captions, any language, convert to
  SRT / VTT / ASS / LRC, or embed them into the file
- 🖼 **Thumbnails + Metadata** — download/embed thumbnail, embed tags, and
  export full `.info.json` sidecar
- 📋 **Playlist & Channels** — full/partial (index range `1-50`), reverse
  order, skip already downloaded (archive), keyword / min-length / min-views /
  uploaded-after filters; works with `/channel/`, `/user/`, `/c/`, `@handle`
- 🔍 **Built-in YouTube Search** — search from inside the app, then download
  straight from the results
- 🧾 **Batch Download** — paste a list of URLs, all queued automatically
- 📎 **Clipboard Detection** — pasting a link anywhere shows a one-click
  download suggestion
- 🔔 **Desktop Notifications** — get notified when a download completes
- ⚡ **Concurrent Downloads** — 1–6 parallel downloads with
  pause / resume / retry / cancel
- 📊 **Real-time Progress** — live speed, ETA, and percentage per download
- 🎨 **Modern Dark/Light UI** — smooth interface with hover effects
- 📁 **Custom Save Location**, custom filename templates, per-download folder
  naming
- 🛡 **Extras** — proxy support, download speed limit, cookies file for
  logged-in sites, `archive` skip of already-downloaded files

## 🚀 Installation

### Option A — Prebuilt Windows app (recommended)
1. Download the latest release zip (`HikmahYT-v5-pro-win64.zip`) from the
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
   Twitch, Vimeo, Telegram, etc.) into the box — a clipboard link is suggested
   automatically.
3. Click **Analyze** — the app fetches the title, thumbnail, duration, views
   and all available formats.
4. Pick a format:
   - ⚡ **Best Quality (Auto)** — fastest choice
   - 🎬 a specific resolution (**144p → 8K**) — shows file size and fps
   - 🎵 an audio-only option (e.g. MP3 320 kbps)
5. Tune the **advanced options bar**: video codec, container, audio codec,
   subtitles (language + format + embed), thumbnail, metadata, HDR, 60fps and
   JSON export.
6. Click **Download Now**. A progress card shows speed, ETA and percentage.
7. When it finishes, you get a desktop notification and the file is saved to
   your download folder (default `~/Downloads/HikmahYT`).

### Search YouTube
1. On the **Home** page toggle **🔍 Search**.
2. Type a query and hit Enter — results appear with title, channel and length.
3. Click **Download** on any result (or **Info** to preview it first).

### Batch download
1. Click **Batch** on the Home page.
2. Paste multiple URLs (one per line) and click **Start Batch Download**.
3. Each valid URL is fetched and queued with the current format settings.

### Download a playlist / channel
1. Click **Playlist** in the sidebar (or paste a playlist/channel URL on the
   Home page — it is detected automatically).
2. Paste the URL and click **Load Playlist**.
3. Use **Select All** / **Deselect All** or toggle individual videos.
4. Open **Advanced** to filter: index range, title keyword, minimum length,
   uploaded after, reverse order, or skip already downloaded.
5. Choose a format and click **Download N Videos**. Files are saved in a
   subfolder named after the playlist.

### Change where files are saved
- **Settings** → **Download Location** → **Change**. Applies to all downloads.

### Concurrency, speed & proxy
- **Settings** → **Concurrent Downloads** (1–6), **Speed Limit** (KB/s) and
  **Proxy** — apply immediately.

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
`dist\HikmahYT-v5-pro-win64.zip`. The build bundles yt-dlp (with all
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
| Downloads keep failing / site requires login | Add your **cookies file** in Settings, or run from source and `python -m pip install -U yt-dlp` for the latest extractors. |
| Low-quality or missing resolution | Pick ⚡ **Best Quality** — some sites only expose what the player offers. |
| "ffmpeg is required..." error | The build bundles ffmpeg; if running from source, install `imageio-ffmpeg` (already in `requirements.txt`). |
| Video + audio won't merge | Make sure ffmpeg is found; use a combined format (⚡ Best Quality) as fallback. |
| DRM/paid content (Netflix, Spotify...) | Not supported — such sites encrypt streams by design. |

## ⚠️ Legal Notice

Only download content you have the right to, and respect each site's Terms of
Service and the copyright laws of your country.

## 🤝 License

[MIT](LICENSE)
