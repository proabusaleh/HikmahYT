"""
HikmahYT - Download Engine
Powered by yt-dlp for reliable downloads
"""

import os
import threading
import queue
import yt_dlp
from utils.helpers import (
    get_default_download_path,
    sanitize_filename,
    get_ffmpeg_location,
)


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def base_ydl_opts(**overrides):
    """Base options shared across all operations."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'retries': 10,
        'fragment_retries': 10,
        'extractor_retries': 3,
        'socket_timeout': 30,
        'http_headers': {'User-Agent': USER_AGENT},
    }
    ffmpeg = get_ffmpeg_location()
    if ffmpeg:
        opts['ffmpeg_location'] = ffmpeg
    opts.update(overrides)
    return opts


class DownloadTask:
    """Represents a single download task."""

    def __init__(self, url, title="", video_id=""):
        self.url = url
        self.title = title
        self.video_id = video_id
        self.status = "pending"  # pending, downloading, paused, completed, error
        self.progress = 0.0
        self.speed = ""
        self.eta = ""
        self.filesize = ""
        self.downloaded = ""
        self.error_message = ""
        self.output_path = ""
        self.thumbnail_url = ""


class DownloadEngine:
    """Core download engine using yt-dlp."""

    def __init__(self):
        self.download_path = get_default_download_path()
        self.active_downloads = {}
        self.download_queue = queue.Queue()
        self.callbacks = {
            'on_progress': None,
            'on_complete': None,
            'on_error': None,
            'on_info': None,
            'on_playlist_info': None,
        }
        self._cancel_flags = {}
        self._completed = set()
        self._uses_postprocessor = {}

    def set_callback(self, event, callback):
        """Set callback for download events."""
        if event in self.callbacks:
            self.callbacks[event] = callback

    def set_download_path(self, path):
        """Set download directory."""
        os.makedirs(path, exist_ok=True)
        self.download_path = path

    # ==================== Info ====================

    def fetch_info(self, url, playlist=False):
        """Fetch video/playlist information without downloading."""
        def _fetch():
            try:
                ydl_opts = base_ydl_opts(skip_download=True)
                if playlist:
                    ydl_opts['extract_flat'] = 'in_playlist'
                else:
                    ydl_opts['noplaylist'] = True

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    if info and self.callbacks['on_info']:
                        self.callbacks['on_info'](info)

                    return info

            except Exception as e:
                if self.callbacks['on_error']:
                    self.callbacks['on_error'](str(e), url)
                return None

        thread = threading.Thread(target=_fetch, daemon=True)
        thread.start()
        return thread

    def fetch_playlist_info(self, url):
        """Fetch playlist information."""
        def _fetch():
            try:
                ydl_opts = base_ydl_opts(
                    skip_download=True,
                    extract_flat='in_playlist',
                )

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    if info and self.callbacks['on_playlist_info']:
                        self.callbacks['on_playlist_info'](info)

                    return info

            except Exception as e:
                if self.callbacks['on_error']:
                    self.callbacks['on_error'](str(e), url)
                return None

        thread = threading.Thread(target=_fetch, daemon=True)
        thread.start()
        return thread

    # ==================== Download ====================

    def download(self, url, format_id='best', audio_only=False,
                 quality='1080', task_id=None):
        """Start downloading a video.

        ``format_id`` can be:
          - ``'best'``                 -> auto pick the best available video
          - ``'bestaudio/best'``       -> best audio stream
          - a yt-dlp format id         -> e.g. ``'22'`` or ``'137+140'``
          - a format selector string   -> e.g. ``'bv*[height<=1080]+ba'``
        """
        if task_id is None:
            task_id = url

        self._cancel_flags[task_id] = False
        self._completed.discard(task_id)

        attempts = self._build_attempts(format_id, audio_only, quality)

        # Completion must wait for post-processing (merge / audio extract)
        needs_pp = audio_only or any('+' in (fmt or '') for fmt in attempts)
        self._uses_postprocessor[task_id] = needs_pp

        def _download():
            last_error = None

            for fmt in attempts:
                try:
                    ydl_opts = base_ydl_opts(
                        format=fmt,
                        outtmpl=os.path.join(
                            self.download_path, '%(title)s.%(ext)s'),
                        progress_hooks=[
                            lambda d: self._progress_hook(d, task_id)
                        ],
                        noplaylist=True,
                    )

                    if audio_only:
                        preferred = str(quality) if str(quality).isdigit() else '192'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': preferred,
                        }]

                    if self._uses_postprocessor.get(task_id, False):
                        ydl_opts['postprocessor_hooks'] = [
                            lambda d: self._postproc_hook(d, task_id)
                        ]

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        if self._cancel_flags.get(task_id):
                            return
                        ydl.download([url])
                    return

                except yt_dlp.utils.DownloadCancelled:
                    return
                except Exception as e:
                    last_error = e
                    msg = str(e).lower()
                    if 'ffmpeg' in msg and ('not' in msg or 'missing' in msg or 'install' in msg):
                        last_error = (
                            "ffmpeg is required to merge video + audio. "
                            "Install ffmpeg or choose a combined format."
                        )
                        break

            if last_error is not None and self.callbacks['on_error']:
                self.callbacks['on_error'](str(last_error), task_id)

        thread = threading.Thread(target=_download, daemon=True)
        thread.start()
        self.active_downloads[task_id] = thread
        return thread

    def _build_attempts(self, format_id, audio_only, quality):
        """Return a list of format selector strings (tried in order).

        Merge is done natively (the output keeps the video stream's
        container, e.g. mp4/webm) so no slow re-encoding ever happens.
        """
        quality = str(quality)
        is_digit = quality.isdigit()

        if audio_only:
            fmt = format_id
            if not fmt or fmt in ('best', 'bestvideo'):
                fmt = 'bestaudio/best'
            return [fmt]

        if format_id and format_id != 'best':
            if '+' in format_id and get_ffmpeg_location() is None:
                # No ffmpeg -> force a single-file combined format
                return [
                    f'b[height<={quality}]/b' if is_digit else 'b',
                    'b',
                ]
            return [format_id]

        # Auto / best quality
        if is_digit:
            h_selector = f'bv*[height<={quality}]+ba/b[height<={quality}]/b'
            combined = f'b[height<={quality}]/b'
        else:
            h_selector = 'bv*+ba/b'
            combined = 'b'

        if get_ffmpeg_location() is not None:
            return [h_selector, combined, 'b']
        return [combined, 'b']

    def download_playlist(self, url, format_id='best', audio_only=False,
                          quality='1080', selected_indices=None,
                          task_id='playlist'):
        """Download entire playlist or selected videos."""
        self._cancel_flags[task_id] = False
        self._completed.discard(task_id)
        attempts = self._build_attempts(format_id, audio_only, quality)
        needs_pp = audio_only or any('+' in (fmt or '') for fmt in attempts)
        self._uses_postprocessor[task_id] = needs_pp

        def _download():
            try:
                fmt = attempts[0]

                ydl_opts = base_ydl_opts(
                    format=fmt,
                    outtmpl=os.path.join(
                        self.download_path,
                        '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'
                    ),
                    progress_hooks=[
                        lambda d: self._progress_hook(d, task_id)
                    ],
                )

                if audio_only:
                    preferred = str(quality) if str(quality).isdigit() else '192'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': preferred,
                    }]

                if self._uses_postprocessor.get(task_id, False):
                    ydl_opts['postprocessor_hooks'] = [
                        lambda d: self._postproc_hook(d, task_id)
                    ]

                if selected_indices:
                    ydl_opts['playlist_items'] = ','.join(
                        str(i) for i in selected_indices
                    )

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if self._cancel_flags.get(task_id):
                        return
                    ydl.download([url])

            except yt_dlp.utils.DownloadCancelled:
                return
            except Exception as e:
                if self.callbacks['on_error']:
                    self.callbacks['on_error'](str(e), task_id)

        thread = threading.Thread(target=_download, daemon=True)
        thread.start()
        self.active_downloads[task_id] = thread
        return thread

    # ==================== Hooks ====================

    def _progress_hook(self, d, task_id):
        """Handle download progress updates."""
        if self._cancel_flags.get(task_id):
            raise yt_dlp.utils.DownloadCancelled("Download cancelled")

        if self.callbacks['on_progress']:
            progress_data = {
                'task_id': task_id,
                'status': d.get('status', ''),
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes')
                    or d.get('total_bytes_estimate', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'filename': d.get('filename', ''),
            }

            if progress_data['total_bytes'] > 0:
                progress_data['progress'] = (
                    progress_data['downloaded_bytes']
                    / progress_data['total_bytes']
                ) * 100
            else:
                progress_data['progress'] = 0

            self.callbacks['on_progress'](progress_data)

        if d['status'] == 'finished':
            # If post-processing will run, completion is signalled by
            # _postproc_hook so we report the final converted/merged file.
            if not self._uses_postprocessor.get(task_id, False):
                self._mark_complete(task_id, d.get('filename', ''))

    def _postproc_hook(self, d, task_id):
        """Handle post-processor (merge / audio extract) completion.

        Only the final 'MoveFiles' postprocessor carries the definitive
        output path (e.g. the converted .mp3 or merged .mp4/.webm).
        """
        if d.get('status') == 'finished' and d.get('postprocessor') == 'MoveFiles':
            info = d.get('info_dict') or {}
            final_path = info.get('filepath') or d.get('filename', '')
            self._mark_complete(task_id, final_path)

    def _mark_complete(self, task_id, filename):
        if task_id in self._completed:
            return
        self._completed.add(task_id)
        if self.callbacks['on_complete']:
            self.callbacks['on_complete'](task_id, filename)

    def cancel_download(self, task_id):
        """Cancel a download."""
        self._cancel_flags[task_id] = True

    def cancel_all(self):
        """Cancel all active downloads."""
        for task_id in self._cancel_flags:
            self._cancel_flags[task_id] = True
