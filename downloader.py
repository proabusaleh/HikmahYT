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

AUDIO_CODECS = ('mp3', 'aac', 'm4a', 'opus', 'vorbis', 'flac', 'alac', 'wav')
CONTAINERS = ('mp4', 'mkv', 'webm', 'avi', 'mov', 'flv')
SUB_FORMATS = ('srt', 'vtt', 'ass', 'lrc')

VIDEO_CODECS = {
    'h264': 'vcodec:h264',
    'h265': 'vcodec:h265',
    'av1': 'vcodec:av1',
    'vp9': 'vcodec:vp9',
    'vp8': 'vcodec:vp8',
}

AUDIO_CODEC_ALIASES = {
    'ogg': 'vorbis',
    'mp4a': 'm4a',
    'm4a': 'm4a',
    'mp3': 'mp3',
    'aac': 'aac',
    'opus': 'opus',
    'vorbis': 'vorbis',
    'flac': 'flac',
    'alac': 'alac',
    'wav': 'wav',
}


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
        self.params = {}


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
            'on_search': None,
        }
        self._cancel_flags = {}
        self._pause_flags = {}
        self._completed = set()
        self._uses_postprocessor = {}
        self._task_params = {}
        self.max_concurrent = 3
        self._active_count = 0
        self._cond = threading.Condition()

        # User settings
        self.cookiefile = ""
        self.proxy = ""
        self.limit_rate = 0
        self.filename_template = "%(title)s.%(ext)s"
        self.audio_subfolder = False

    def set_callback(self, event, callback):
        """Set callback for download events."""
        if event in self.callbacks:
            self.callbacks[event] = callback

    def set_download_path(self, path):
        """Set download directory."""
        os.makedirs(path, exist_ok=True)
        self.download_path = path

    def set_max_concurrent(self, n):
        """Set how many downloads may run in parallel (1+)."""
        try:
            n = max(1, int(n))
        except (TypeError, ValueError):
            n = 3
        self.max_concurrent = n
        with self._cond:
            self._cond.notify_all()

    def set_cookiefile(self, path):
        """Set a Netscape cookies file for private/age-restricted content."""
        self.cookiefile = (path or "").strip()

    def set_proxy(self, proxy):
        """Set an HTTP/SOCKS5 proxy for the downloader."""
        self.proxy = (proxy or "").strip()

    def set_limit_rate(self, rate):
        """Set a speed limit in bytes/sec (0 = no limit)."""
        try:
            self.limit_rate = max(0, int(rate))
        except (TypeError, ValueError):
            self.limit_rate = 0

    def set_filename_template(self, template):
        """Set the custom output filename template."""
        template = (template or "").strip()
        self.filename_template = template or "%(title)s.%(ext)s"

    def set_audio_subfolder(self, enabled):
        """Save audio downloads into a Music/ subfolder."""
        self.audio_subfolder = bool(enabled)

    # ==================== Concurrency slots ====================

    def _acquire_slot(self):
        with self._cond:
            while self._active_count >= self.max_concurrent:
                self._cond.wait()
            self._active_count += 1

    def _release_slot(self):
        with self._cond:
            if self._active_count > 0:
                self._active_count -= 1
            self._cond.notify_all()

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

                self._apply_settings(ydl_opts)

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

                self._apply_settings(ydl_opts)

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

    def search(self, query, limit=10):
        """Search YouTube and return a list of lightweight result dicts."""
        def _search():
            try:
                url = f'ytsearch{limit}:{query}'
                ydl_opts = base_ydl_opts(
                    skip_download=True,
                    extract_flat=True,
                    noplaylist=True,
                )
                self._apply_settings(ydl_opts)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                results = []
                for e in (info.get('entries') or []):
                    if not e:
                        continue
                    results.append({
                        'title': e.get('title', 'Untitled'),
                        'url': e.get('url') or e.get('webpage_url', ''),
                        'id': e.get('id', ''),
                        'duration': e.get('duration', 0),
                        'channel': e.get('channel') or e.get('uploader', ''),
                        'views': e.get('view_count', 0),
                    })

                if self.callbacks.get('on_search'):
                    self.callbacks['on_search'](results)

            except Exception as e:
                if self.callbacks['on_error']:
                    self.callbacks['on_error'](str(e), 'search')

        thread = threading.Thread(target=_search, daemon=True)
        thread.start()
        return thread

    # ==================== Download ====================

    def download(self, url, format_id='best', audio_only=False,
                 quality='1080', task_id=None, container='',
                 audio_codec='mp3', download_thumb=False, embed_meta=False,
                 download_subs=False, subs_langs='en', embed_subs=False,
                 codec='', hdr=False, fps60=False, sub_format='',
                 write_json=False, archive=False, match_filters=None):
        """Start downloading a video."""
        if task_id is None:
            task_id = url

        self._cancel_flags[task_id] = False
        self._pause_flags[task_id] = False
        self._completed.discard(task_id)

        self._task_params[task_id] = {
            'url': url,
            'format_id': format_id,
            'audio_only': audio_only,
            'quality': quality,
            'container': container,
            'audio_codec': audio_codec,
            'download_thumb': download_thumb,
            'embed_meta': embed_meta,
            'download_subs': download_subs,
            'subs_langs': subs_langs,
            'embed_subs': embed_subs,
            'codec': codec,
            'hdr': hdr,
            'fps60': fps60,
            'sub_format': sub_format,
            'write_json': write_json,
            'archive': archive,
            'match_filters': match_filters,
            'playlist': False,
        }

        return self._spawn_worker(task_id)

    def download_playlist(self, url, format_id='best', audio_only=False,
                          quality='1080', selected_indices=None,
                          task_id='playlist', container='',
                          audio_codec='mp3', download_thumb=False,
                          embed_meta=False, download_subs=False,
                          subs_langs='en', embed_subs=False,
                          codec='', hdr=False, fps60=False, sub_format='',
                          write_json=False, archive=False, reverse=False,
                          range_str='', match_filters=None):
        """Download entire playlist or selected videos."""
        self._cancel_flags[task_id] = False
        self._pause_flags[task_id] = False
        self._completed.discard(task_id)

        self._task_params[task_id] = {
            'url': url,
            'format_id': format_id,
            'audio_only': audio_only,
            'quality': quality,
            'selected_indices': selected_indices,
            'container': container,
            'audio_codec': audio_codec,
            'download_thumb': download_thumb,
            'embed_meta': embed_meta,
            'download_subs': download_subs,
            'subs_langs': subs_langs,
            'embed_subs': embed_subs,
            'codec': codec,
            'hdr': hdr,
            'fps60': fps60,
            'sub_format': sub_format,
            'write_json': write_json,
            'archive': archive,
            'reverse': reverse,
            'range_str': range_str,
            'match_filters': match_filters,
            'playlist': True,
        }

        return self._spawn_worker(task_id)

    def _spawn_worker(self, task_id):
        thread = threading.Thread(
            target=self._worker, args=(task_id,), daemon=True
        )
        thread.start()
        self.active_downloads[task_id] = thread
        return thread

    def _worker(self, task_id):
        params = self._task_params.get(task_id)
        if params is None:
            return

        self._acquire_slot()
        try:
            if self._cancel_flags.get(task_id):
                return
            if self._pause_flags.get(task_id):
                self._report_paused(task_id)
                return

            if params.get('playlist'):
                self._run_playlist(task_id, params)
            else:
                self._run_video(task_id, params)
        finally:
            self._release_slot()
            if self.active_downloads.get(task_id) is threading.current_thread():
                self.active_downloads.pop(task_id, None)

    # ==================== Option builders ====================

    def _apply_settings(self, ydl_opts):
        """Inject global settings (cookies, proxy, speed limit)."""
        if self.cookiefile:
            ydl_opts['cookiefile'] = self.cookiefile
        if self.proxy:
            ydl_opts['proxy'] = self.proxy
        if self.limit_rate:
            ydl_opts['limit_rate'] = self.limit_rate

    def _build_outtmpl(self, params):
        """Build the output path template for a task."""
        if params.get('playlist'):
            base = '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'
        else:
            base = self.filename_template

        if params.get('audio_only') and self.audio_subfolder:
            return os.path.join(self.download_path, 'Music', base)
        return os.path.join(self.download_path, base)

    def _build_postprocessors(self, params):
        """Return the postprocessor list for a task."""
        pps = []

        if params.get('audio_only'):
            codec = str(params.get('audio_codec', 'mp3')).lower()
            codec = AUDIO_CODEC_ALIASES.get(codec, codec)
            if codec not in AUDIO_CODECS:
                codec = 'mp3'
            preferred = str(params.get('quality', '192'))
            if not preferred.isdigit():
                preferred = '192'
            pps.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': preferred,
            })

        # Container conversion: remux single-file streams too.
        container = str(params.get('container', '')).lower()
        if (
            not params.get('audio_only')
            and container in CONTAINERS
            and get_ffmpeg_location() is not None
        ):
            pps.append({'key': 'FFmpegVideoRemuxer', 'remux': container})

        if params.get('download_thumb') or params.get('embed_meta'):
            if params.get('embed_meta'):
                pps.append({'key': 'EmbedThumbnail'})
            else:
                pps.append({
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                })

        # Subtitle format conversion (SRT / VTT / ASS / LRC)
        sub_format = str(params.get('sub_format', '')).lower()
        if (
            params.get('download_subs')
            and sub_format in SUB_FORMATS
            and sub_format != 'srt'
        ):
            pps.append({
                'key': 'FFmpegSubtitlesConvertor',
                'format': sub_format,
            })

        return pps

    def _apply_format_opts(self, ydl_opts, params):
        """Inject per-download format options (container, subs, thumb, meta)."""
        container = str(params.get('container', '')).lower()
        if container in CONTAINERS:
            ydl_opts['merge_output_format'] = container

        if params.get('download_subs'):
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            langs = params.get('subs_langs', 'en')
            ydl_opts['subtitleslangs'] = [langs] if isinstance(langs, str) else langs
            if params.get('embed_subs'):
                ydl_opts['embedsubs'] = True

        if params.get('download_thumb') or params.get('embed_meta'):
            ydl_opts['writethumbnail'] = True

        if params.get('embed_meta'):
            ydl_opts['addmetadata'] = True

        # Codec / HDR / FPS preference via format sorting
        sort = []
        codec = str(params.get('codec', '')).lower()
        if codec in VIDEO_CODECS:
            sort.append(VIDEO_CODECS[codec])
        if params.get('hdr'):
            sort.append('hdr:10')
        if params.get('fps60'):
            sort.append('fps')
        if sort:
            ydl_opts['format_sort'] = sort
            # Make the codec/HDR choice a hard preference, not a tie-break
            if codec or params.get('hdr'):
                ydl_opts['format_sort_force'] = True

        # JSON metadata sidecar
        if params.get('write_json'):
            ydl_opts['writeinfojson'] = True

        # Skip already downloaded (archive)
        if params.get('archive'):
            ydl_opts['download_archive'] = os.path.join(
                self.download_path, '.hikmahyt_archive.txt'
            )

        # Playlist ordering
        if params.get('reverse'):
            ydl_opts['playlist_reverse'] = True

        # Date filters
        mf = params.get('match_filters') or {}
        if mf.get('date_after'):
            ydl_opts['dateafter'] = mf['date_after']
        if mf.get('date_before'):
            ydl_opts['datebefore'] = mf['date_before']

    def _build_match_filter(self, params):
        """Build a yt-dlp match_filter callable from task filters."""
        mf = params.get('match_filters') or {}
        keyword = str(mf.get('keyword', '')).strip().lower()
        min_dur = mf.get('min_duration_sec') or 0
        min_views = mf.get('min_views') or 0

        if not any([keyword, min_dur, min_views]):
            return None

        def match_filter(info, *args, **kwargs):
            if keyword and keyword not in (info.get('title') or '').lower():
                return 'Filtered: title does not match keyword'
            if min_dur and info.get('duration') and info['duration'] < min_dur:
                return 'Filtered: shorter than minimum duration'
            if min_views and info.get('view_count') \
                    and info['view_count'] < min_views:
                return 'Filtered: fewer than minimum views'
            return None

        return match_filter

    # ==================== Download runners ====================

    def _run_video(self, task_id, params):
        url = params['url']
        format_id = params['format_id']
        audio_only = params['audio_only']
        quality = params['quality']

        attempts = self._build_attempts(format_id, audio_only, quality)
        pps = self._build_postprocessors(params)

        # Completion must wait for post-processing (merge / extract / embed)
        needs_pp = bool(pps) or any('+' in (fmt or '') for fmt in attempts)
        self._uses_postprocessor[task_id] = needs_pp

        last_error = None

        for fmt in attempts:
            try:
                ydl_opts = base_ydl_opts(
                    format=fmt,
                    outtmpl=self._build_outtmpl(params),
                    progress_hooks=[
                        lambda d: self._progress_hook(d, task_id)
                    ],
                    noplaylist=True,
                )

                self._apply_settings(ydl_opts)
                self._apply_format_opts(ydl_opts, params)
                if pps:
                    ydl_opts['postprocessors'] = pps

                mf = self._build_match_filter(params)
                if mf is not None:
                    ydl_opts['match_filter'] = mf

                if needs_pp:
                    ydl_opts['postprocessor_hooks'] = [
                        lambda d: self._postproc_hook(d, task_id)
                    ]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if self._cancel_flags.get(task_id):
                        return
                    if self._pause_flags.get(task_id):
                        self._report_paused(task_id)
                        return
                    ydl.download([url])
                return

            except yt_dlp.utils.DownloadCancelled:
                if self._pause_flags.get(task_id):
                    self._report_paused(task_id)
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

    def _run_playlist(self, task_id, params):
        url = params['url']
        format_id = params['format_id']
        audio_only = params['audio_only']
        quality = params['quality']
        selected_indices = params.get('selected_indices')

        attempts = self._build_attempts(format_id, audio_only, quality)
        pps = self._build_postprocessors(params)
        needs_pp = bool(pps) or any('+' in (fmt or '') for fmt in attempts)
        self._uses_postprocessor[task_id] = needs_pp

        try:
            fmt = attempts[0]

            ydl_opts = base_ydl_opts(
                format=fmt,
                outtmpl=self._build_outtmpl(params),
                progress_hooks=[
                    lambda d: self._progress_hook(d, task_id)
                ],
            )

            self._apply_settings(ydl_opts)
            self._apply_format_opts(ydl_opts, params)
            if pps:
                ydl_opts['postprocessors'] = pps

            mf = self._build_match_filter(params)
            if mf is not None:
                ydl_opts['match_filter'] = mf

            if needs_pp:
                ydl_opts['postprocessor_hooks'] = [
                    lambda d: self._postproc_hook(d, task_id)
                ]

            range_str = str(params.get('range_str', '') or '').strip()
            if range_str:
                ydl_opts['playlist_items'] = range_str
            elif selected_indices:
                ydl_opts['playlist_items'] = ','.join(
                    str(i) for i in selected_indices
                )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self._cancel_flags.get(task_id):
                    return
                if self._pause_flags.get(task_id):
                    self._report_paused(task_id)
                    return
                ydl.download([url])

        except yt_dlp.utils.DownloadCancelled:
            if self._pause_flags.get(task_id):
                self._report_paused(task_id)
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](str(e), task_id)

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

    # ==================== Hooks ====================

    def _progress_hook(self, d, task_id):
        """Handle download progress updates."""
        if self._pause_flags.get(task_id):
            raise yt_dlp.utils.DownloadCancelled("Download paused")
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

    def _report_paused(self, task_id):
        """Notify the UI that a task is now paused."""
        if self.callbacks['on_progress']:
            self.callbacks['on_progress']({
                'task_id': task_id,
                'status': 'paused',
                'downloaded_bytes': 0,
                'total_bytes': 0,
                'speed': 0,
                'eta': 0,
                'progress': 0,
                'filename': '',
            })

    def _mark_complete(self, task_id, filename):
        if task_id in self._completed:
            return
        self._completed.add(task_id)
        if self.callbacks['on_complete']:
            self.callbacks['on_complete'](task_id, filename)

    # ==================== Control ====================

    def pause_download(self, task_id):
        """Pause a download (the partial file is kept for resuming)."""
        if task_id not in self._task_params:
            return False
        self._pause_flags[task_id] = True
        return True

    def resume_download(self, task_id):
        """Resume a paused download from where it left off."""
        if task_id not in self._task_params:
            return False
        if not self._pause_flags.get(task_id):
            return False
        self._pause_flags[task_id] = False
        self._completed.discard(task_id)
        self._spawn_worker(task_id)
        return True

    def cancel_download(self, task_id):
        """Cancel a download."""
        self._cancel_flags[task_id] = True
        self._pause_flags[task_id] = False

    def retry_download(self, task_id):
        """Restart a failed download from where it left off."""
        if task_id not in self._task_params:
            return False
        self._cancel_flags[task_id] = False
        self._pause_flags[task_id] = False
        self._completed.discard(task_id)
        self._spawn_worker(task_id)
        return True

    def cancel_all(self):
        """Cancel all active downloads."""
        for task_id in self._cancel_flags:
            self._cancel_flags[task_id] = True
            self._pause_flags[task_id] = False
