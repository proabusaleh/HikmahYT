"""
HikmahYT - Utility Helpers
"""

import os
import re
import math
import shutil
from datetime import timedelta


def format_size(bytes_size):
    """Format bytes to human readable size."""
    if bytes_size is None or bytes_size == 0:
        return "Unknown"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(bytes_size)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds):
    """Format seconds to HH:MM:SS or MM:SS."""
    if seconds is None:
        return "Unknown"
    
    seconds = int(seconds)
    if seconds < 3600:
        return f"{seconds // 60}:{seconds % 60:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"


def format_views(views):
    """Format view count to human readable."""
    if views is None:
        return "N/A"
    
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B views"
    elif views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M views"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K views"
    else:
        return f"{views} views"


def format_date(date_str):
    """Format upload date."""
    if not date_str or len(date_str) != 8:
        return "Unknown"
    
    try:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{months[int(month)-1]} {int(day)}, {year}"
    except (ValueError, IndexError):
        return date_str


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    sanitized = sanitized.strip('. ')
    return sanitized[:200] if sanitized else "video"


def is_valid_url(url):
    """Check if URL is plausibly a video URL for a supported site."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if len(url) < 10:
        return False
    pattern = r'^https?://[^\s/$.?#][^\s]*$'
    if not re.match(pattern, url):
        return False
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc
        return bool(host) and '.' in host
    except Exception:
        return False


SITE_NAMES = [
    ("youtube.com", "YouTube"), ("youtu.be", "YouTube"),
    ("facebook.com", "Facebook"), ("fb.watch", "Facebook"), ("fb.com", "Facebook"),
    ("tiktok.com", "TikTok"),
    ("t.me", "Telegram"),
    ("instagram.com", "Instagram"),
    ("twitter.com", "X (Twitter)"), ("x.com", "X (Twitter)"),
    ("twitch.tv", "Twitch"),
    ("vimeo.com", "Vimeo"),
    ("dailymotion.com", "Dailymotion"),
    ("reddit.com", "Reddit"),
    ("soundcloud.com", "SoundCloud"),
    ("spotify.com", "Spotify"),
    ("tumblr.com", "Tumblr"),
    ("bilibili.com", "Bilibili"),
    ("vk.com", "VK"),
    ("rutube.ru", "Rutube"),
    ("ok.ru", "OK.ru"),
]


def get_site_name(url):
    """Return a friendly platform name for a URL."""
    if not url:
        return "video"
    url = url.strip().lower()
    for domain, name in SITE_NAMES:
        if domain in url:
            return name
    return "video"


def is_playlist_url(url):
    """Check if URL is a playlist URL."""
    if not url:
        return False
    url = url.strip().lower()
    if 'playlist?list=' in url:
        return True
    if 'list=' in url:
        # A plain video link with a list param is still a single video
        if 'watch?v=' in url or '/shorts/' in url:
            return False
        if 'youtu.be/' in url:
            return False
        return True
    return False


def is_ffmpeg_available():
    """Check if ffmpeg is available on the system PATH."""
    return shutil.which("ffmpeg") is not None


def get_ffmpeg_location():
    """Return a usable ffmpeg path, preferring the bundled binary.

    Uses imageio-ffmpeg's bundled ffmpeg when the system does not have
    ffmpeg installed. Returns None if neither is available.
    """
    if is_ffmpeg_available():
        return shutil.which("ffmpeg")
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass
    return None


def get_default_download_path():
    """Get default download directory."""
    download_path = os.path.join(os.path.expanduser("~"), "Downloads", "HikmahYT")
    os.makedirs(download_path, exist_ok=True)
    return download_path


def truncate_text(text, max_length=50):
    """Truncate text with ellipsis."""
    if not text:
        return ""
    return text[:max_length-3] + "..." if len(text) > max_length else text