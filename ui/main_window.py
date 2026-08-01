"""
HikmahYT - Main Application Window
The heart of the application
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ui.styles import COLORS, FONTS, DIMENSIONS
from ui.widgets import (
    LogoWidget, ModernEntry, AccentButton, IconButton,
    ModernCard, VideoInfoCard, ProgressCard, PlaylistItemCard,
    SidebarButton, FormatSelector, StatsWidget, GradientFrame
)
from downloader import DownloadEngine
from utils.helpers import (
    is_valid_url, is_playlist_url, format_size, 
    format_duration, format_views, get_default_download_path,
    get_site_name
)


class HikmahYTApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("HikmahYT - Video Downloader")
        self.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.minsize(DIMENSIONS['min_width'], DIMENSIONS['min_height'])
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Center window
        self._center_window()
        
        # Initialize engine
        self.engine = DownloadEngine()
        self.engine.set_callback('on_progress', self._on_progress)
        self.engine.set_callback('on_complete', self._on_complete)
        self.engine.set_callback('on_error', self._on_error)
        self.engine.set_callback('on_info', self._on_info_received)
        self.engine.set_callback('on_playlist_info', self._on_playlist_info)
        
        # State
        self.current_page = "home"
        self.current_info = None
        self.playlist_items = []
        self.playlist_selected = {}
        self.download_count = 0
        self.progress_cards = {}
        self.sidebar_buttons = {}
        
        # Build UI
        self._build_ui()
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = DIMENSIONS['window_width']
        height = DIMENSIONS['window_height']
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _build_ui(self):
        """Build the main UI layout."""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self._build_sidebar(main_container)
        
        # Content area
        self.content_area = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["bg_main"],
            corner_radius=20,
        )
        self.content_area.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Pages
        self.pages = {}
        self._build_home_page()
        self._build_downloads_page()
        self._build_playlist_page()
        self._build_settings_page()
        
        # Show home page
        self._show_page("home")
    
    def _build_sidebar(self, parent):
        """Build the sidebar navigation."""
        sidebar = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_dark"],
            width=DIMENSIONS["sidebar_width"],
        )
        sidebar.pack(side="left", fill="y", padx=(10, 5), pady=10)
        sidebar.pack_propagate(False)
        
        # Logo
        logo = LogoWidget(sidebar, size="medium")
        logo.pack(pady=(20, 5))
        
        # Tagline
        ctk.CTkLabel(
            sidebar,
            text="Download with Wisdom",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, 30))
        
        # Navigation buttons
        nav_items = [
            ("home", "🏠", "Home"),
            ("downloads", "📥", "Downloads"),
            ("playlist", "📋", "Playlist"),
            ("settings", "⚙️", "Settings"),
        ]
        
        for page_id, icon, label in nav_items:
            btn = SidebarButton(
                sidebar,
                text=label,
                icon=icon,
                active=(page_id == "home"),
                command=lambda p=page_id: self._show_page(p),
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.sidebar_buttons[page_id] = btn
        
        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent", height=20).pack(fill="x")
        
        # Stats widget at bottom
        self.stats_widget = StatsWidget(sidebar)
        self.stats_widget.pack(fill="x", padx=10, pady=(0, 10), side="bottom")
        
        # Version
        ctk.CTkLabel(
            sidebar,
            text="v1.0.0",
            font=("Segoe UI", 10),
            text_color=COLORS["text_muted"],
        ).pack(side="bottom", pady=(0, 10))
    
    def _build_home_page(self):
        """Build the home/main download page."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.pages["home"] = page
        
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"],
        )
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.home_scroll_frame = scroll
        
        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 20))
        
        ctk.CTkLabel(
            header,
            text="Download Video",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Paste a URL from YouTube, Facebook, TikTok, Telegram & more",
            font=("Segoe UI", 14),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(5, 0))
        
        # URL Input Section
        input_section = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        input_section.pack(fill="x", padx=25, pady=(0, 20))
        
        input_inner = ctk.CTkFrame(input_section, fg_color="transparent")
        input_inner.pack(fill="x", padx=20, pady=20)
        
        # URL Entry
        self.url_entry = ModernEntry(
            input_inner,
            placeholder="Paste video URL here...",
            icon="🔗",
        )
        self.url_entry.pack(fill="x", pady=(0, 15))
        self.url_entry.bind_entry("<Return>", lambda e: self._fetch_info())
        
        # Button row
        btn_row = ctk.CTkFrame(input_inner, fg_color="transparent")
        btn_row.pack(fill="x")
        
        # Fetch button
        self.fetch_btn = AccentButton(
            btn_row,
            text="Analyze",
            icon="🔍",
            command=self._fetch_info,
            color="primary",
            width=160,
        )
        self.fetch_btn.pack(side="left", padx=(0, 10))
        
        # Paste button
        AccentButton(
            btn_row,
            text="Paste",
            icon="📋",
            command=self._paste_url,
            color="dark",
            width=120,
        ).pack(side="left", padx=(0, 10))
        
        # Clear button
        AccentButton(
            btn_row,
            text="Clear",
            icon="🗑",
            command=self._clear_url,
            color="dark",
            width=120,
        ).pack(side="left")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            scroll,
            text="",
            font=("Segoe UI", 13),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        # Loading indicator
        self.loading_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="⏳ Fetching video information...",
            font=("Segoe UI", 14),
            text_color=COLORS["accent_blue"],
        )
        self.loading_label.pack(pady=20)
        
        # Video info container
        self.info_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.info_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Quality selector container
        self.quality_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.quality_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Download button container
        self.download_btn_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.download_btn_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Playlist results (merged video + playlist URL support)
        self.home_playlist_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.home_playlist_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Active downloads section
        self.home_downloads_label = ctk.CTkLabel(
            scroll,
            text="",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.home_downloads_label.pack(anchor="w", padx=25, pady=(10, 10))
        
        self.home_progress_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.home_progress_container.pack(fill="x", padx=25, pady=(0, 20))
    
    def _build_downloads_page(self):
        """Build the downloads history page."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.pages["downloads"] = page
        
        scroll = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"],
        )
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 20))
        
        ctk.CTkLabel(
            header,
            text="📥  Downloads",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        
        AccentButton(
            header,
            text="Open Folder",
            icon="📁",
            command=self._open_download_folder,
            color="dark",
            size="small",
            width=140,
        ).pack(side="right")
        
        # Downloads container
        self.downloads_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.downloads_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Empty state
        self.downloads_empty = ctk.CTkFrame(scroll, fg_color="transparent")
        
        ctk.CTkLabel(
            self.downloads_empty,
            text="📭",
            font=("Segoe UI", 64),
        ).pack(pady=(50, 10))
        
        ctk.CTkLabel(
            self.downloads_empty,
            text="No downloads yet",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["text_secondary"],
        ).pack()
        
        ctk.CTkLabel(
            self.downloads_empty,
            text="Paste a URL on the Home page to start downloading",
            font=("Segoe UI", 14),
            text_color=COLORS["text_muted"],
        ).pack(pady=(5, 0))
        
        self.downloads_empty.pack(fill="x", padx=25)
    
    def _build_playlist_page(self):
        """Build the playlist download page."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.pages["playlist"] = page
        
        scroll = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"],
        )
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 20))
        
        ctk.CTkLabel(
            header,
            text="📋  Playlist Downloader",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Download entire playlists or select specific videos",
            font=("Segoe UI", 14),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(5, 0))
        
        # URL Input
        input_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        input_card.pack(fill="x", padx=25, pady=(0, 20))
        
        input_inner = ctk.CTkFrame(input_card, fg_color="transparent")
        input_inner.pack(fill="x", padx=20, pady=20)
        
        self.playlist_url_entry = ModernEntry(
            input_inner,
            placeholder="Paste playlist URL here...",
            icon="📋",
        )
        self.playlist_url_entry.pack(fill="x", pady=(0, 15))
        self.playlist_url_entry.bind_entry("<Return>", lambda e: self._fetch_playlist())
        
        btn_row = ctk.CTkFrame(input_inner, fg_color="transparent")
        btn_row.pack(fill="x")
        
        self.playlist_fetch_btn = AccentButton(
            btn_row,
            text="Load Playlist",
            icon="🔄",
            command=self._fetch_playlist,
            color="purple",
            width=180,
        )
        self.playlist_fetch_btn.pack(side="left", padx=(0, 10))
        
        AccentButton(
            btn_row,
            text="Paste",
            icon="📋",
            command=self._paste_playlist_url,
            color="dark",
            width=120,
        ).pack(side="left")
        
        # Playlist status
        self.playlist_status = ctk.CTkLabel(
            scroll,
            text="",
            font=("Segoe UI", 13),
            text_color=COLORS["text_muted"],
        )
        self.playlist_status.pack(anchor="w", padx=25, pady=(0, 10))
        
        # Playlist view (info card, items, quality, download) rendered here
        self.playlist_view_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.playlist_view_container.pack(fill="x", padx=25, pady=(0, 20))
    
    def _build_settings_page(self):
        """Build the settings page."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.pages["settings"] = page
        
        scroll = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"],
        )
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        ctk.CTkLabel(
            scroll,
            text="⚙️  Settings",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=25, pady=(25, 20))
        
        # Download Location
        loc_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        loc_card.pack(fill="x", padx=25, pady=(0, 15))
        
        loc_inner = ctk.CTkFrame(loc_card, fg_color="transparent")
        loc_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            loc_inner,
            text="📁  Download Location",
            font=("Segoe UI Semibold", 16),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))
        
        path_row = ctk.CTkFrame(loc_inner, fg_color="transparent")
        path_row.pack(fill="x")
        
        self.path_label = ctk.CTkLabel(
            path_row,
            text=self.engine.download_path,
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.path_label.pack(side="left", fill="x", expand=True)
        
        AccentButton(
            path_row,
            text="Change",
            icon="📂",
            command=self._change_download_path,
            color="dark",
            size="small",
            width=120,
        ).pack(side="right")
        
        # Appearance
        appear_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        appear_card.pack(fill="x", padx=25, pady=(0, 15))
        
        appear_inner = ctk.CTkFrame(appear_card, fg_color="transparent")
        appear_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            appear_inner,
            text="🎨  Appearance",
            font=("Segoe UI Semibold", 16),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))
        
        theme_row = ctk.CTkFrame(appear_inner, fg_color="transparent")
        theme_row.pack(fill="x")
        
        ctk.CTkLabel(
            theme_row,
            text="Theme Mode",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")
        
        self.theme_menu = ctk.CTkOptionMenu(
            theme_row,
            values=["Dark", "Light", "System"],
            font=("Segoe UI", 13),
            fg_color=COLORS["bg_secondary"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_secondary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            command=self._change_theme,
            width=140,
        )
        self.theme_menu.set("Dark")
        self.theme_menu.pack(side="right")
        
        # About
        about_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        about_card.pack(fill="x", padx=25, pady=(0, 15))
        
        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            about_inner,
            text="ℹ️  About HikmahYT",
            font=("Segoe UI Semibold", 16),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))
        
        LogoWidget(about_inner, size="medium").pack(anchor="w", pady=(0, 10))
        
        about_text = (
            "HikmahYT is a modern, feature-rich video downloader.\n"
            "Built with Python, CustomTkinter, and yt-dlp.\n\n"
            "Features:\n"
            "• Download videos from YouTube, Facebook, TikTok, Telegram\n"
            "  Instagram, Twitter/X, Twitch, Vimeo and 1000+ more sites\n"
            "• Download videos in multiple qualities (360p - 4K)\n"
            "• Extract audio as MP3 (128kbps - 320kbps)\n"
            "• Full playlist support with selective download\n"
            "• Beautiful modern dark UI\n"
            "• Real-time download progress tracking\n\n"
            "\"Hikmah\" means wisdom — download wisely! ✨"
        )
        
        ctk.CTkLabel(
            about_inner,
            text=about_text,
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            anchor="w",
            justify="left",
        ).pack(anchor="w")
    
    # ==================== Navigation ====================
    
    def _show_page(self, page_id):
        """Switch to a different page."""
        # Hide all pages
        for pid, page in self.pages.items():
            page.pack_forget()
        
        # Show selected page
        if page_id in self.pages:
            self.pages[page_id].pack(fill="both", expand=True)
        
        # Update sidebar
        for pid, btn in self.sidebar_buttons.items():
            btn.set_active(pid == page_id)
        
        self.current_page = page_id
    
    # ==================== URL Actions ====================
    
    def _paste_url(self):
        """Paste URL from clipboard."""
        try:
            url = self.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)
        except Exception:
            self._set_status("⚠️ Nothing to paste from clipboard", "warning")
    
    def _paste_playlist_url(self):
        """Paste URL to playlist entry."""
        try:
            url = self.clipboard_get()
            self.playlist_url_entry.delete(0, "end")
            self.playlist_url_entry.insert(0, url)
        except Exception:
            self.playlist_status.configure(
                text="⚠️ Nothing to paste from clipboard",
                text_color=COLORS["warning"]
            )
    
    def _clear_url(self):
        """Clear URL and info."""
        self.url_entry.delete(0, "end")
        self.current_info = None
        self._set_status("", "")
        self._clear_results()
    
    def _clear_results(self):
        """Clear all fetched result containers."""
        for widget in self.info_container.winfo_children():
            widget.destroy()
        for widget in self.quality_container.winfo_children():
            widget.destroy()
        for widget in self.download_btn_container.winfo_children():
            widget.destroy()
        for widget in self.home_playlist_container.winfo_children():
            widget.destroy()
    
    # ==================== Fetch Info ====================
    
    def _fetch_info(self):
        """Fetch video OR playlist information (merged URL handling)."""
        url = self.url_entry.get().strip()
        
        if not url:
            self._set_status("⚠️ Please enter a URL", "warning")
            return
        
        if not is_valid_url(url):
            self._set_status("❌ Invalid or unsupported URL", "error")
            return
        
        self._clear_results()
        
        if is_playlist_url(url):
            self._set_status("📋 Playlist detected. Loading videos...", "info")
            self.fetch_btn.configure(state="disabled", text="⏳  Loading...")
            self.playlist_view_target = self.home_playlist_container
            self._current_playlist_url = url
            self.engine.fetch_playlist_info(url)
            return
        
        self._set_status(f"⏳ Fetching {get_site_name(url)} video information...", "info")
        self.fetch_btn.configure(state="disabled", text="⏳  Analyzing...")
        
        # Show loading
        self.loading_frame.pack(fill="x", padx=25, pady=10)
        
        self.engine.fetch_info(url)
    
    def _on_info_received(self, info):
        """Handle received video information."""
        self.current_info = info
        self.after(0, lambda: self._display_video_info(info))
    
    def _display_video_info(self, info):
        """Display video info on the UI."""
        self.loading_frame.pack_forget()
        self.fetch_btn.configure(state="normal", text="🔍  Analyze")
        self._set_status("✅ Video information loaded!", "success")
        
        # Clear containers
        for widget in self.info_container.winfo_children():
            widget.destroy()
        for widget in self.quality_container.winfo_children():
            widget.destroy()
        for widget in self.download_btn_container.winfo_children():
            widget.destroy()
        
        # Video info card
        info_card = VideoInfoCard(self.info_container, info=info)
        info_card.pack(fill="x")
        
        # Format selector (all available formats with sizes)
        quality_card = ctk.CTkFrame(
            self.quality_container,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        quality_card.pack(fill="x")
        
        quality_inner = ctk.CTkFrame(quality_card, fg_color="transparent")
        quality_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            quality_inner,
            text="🎯  Choose Format",
            font=("Segoe UI Semibold", 18),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 15))
        
        self.format_selector = FormatSelector(
            quality_inner,
            formats=info.get('formats', []),
        )
        self.format_selector.pack(fill="x")
        
        # Download button
        download_btn = AccentButton(
            self.download_btn_container,
            text="Download Now",
            icon="⬇️",
            command=self._start_download,
            color="primary",
            size="large",
        )
        download_btn.pack(fill="x", ipady=5)
    
    # ==================== Download ====================
    
    def _start_download(self):
        """Start downloading the current video."""
        if not self.current_info:
            self._set_status("⚠️ No video loaded", "warning")
            return
        
        settings = self.format_selector.get_settings()
        url = self.current_info.get('webpage_url', self.url_entry.get().strip())
        title = self.current_info.get('title', 'Unknown')
        task_id = f"{title}_{self.download_count}"
        
        self.download_count += 1
        
        # Create progress card
        progress_card = ProgressCard(
            self.home_progress_container,
            title=title,
            task_id=task_id,
        )
        progress_card.pack(fill="x", pady=(0, 8))
        self.progress_cards[task_id] = progress_card
        
        # Update header
        self.home_downloads_label.configure(text="📥  Active Downloads")
        
        # Update stats
        self.stats_widget.update_stats(
            downloads=self.download_count,
            active=len(self.progress_cards)
        )
        
        fmt_label = "🎵 MP3" if settings['audio_only'] else \
            (settings['quality'] + "p" if settings['quality'] != 'best' else "Best")
        self._set_status(f"⬇️ Downloading {fmt_label}: {title[:40]}...", "info")
        
        # Start download
        self.engine.download(
            url=url,
            format_id=settings['format_id'],
            audio_only=settings['audio_only'],
            quality=settings['quality'],
            task_id=task_id,
        )
        
        # Scroll the home page down so the new progress card is visible
        self._scroll_home_to_bottom()
    
    def _scroll_home_to_bottom(self):
        """Scroll the home page to reveal newly added progress cards."""
        def do_scroll():
            sf = getattr(self, 'home_scroll_frame', None)
            if sf is not None:
                try:
                    sf._parent_canvas.yview_moveto(1.0)
                except Exception:
                    pass
        self.after(50, do_scroll)
    
    def _on_progress(self, data):
        """Handle progress updates."""
        task_id = data.get('task_id', '')
        
        def update():
            if task_id in self.progress_cards:
                card = self.progress_cards[task_id]
                
                progress = data.get('progress', 0)
                speed = data.get('speed', 0)
                eta = data.get('eta', 0)
                status = data.get('status', '')
                
                speed_str = ""
                if speed:
                    speed_str = format_size(speed) + "/s"
                
                eta_str = ""
                if eta:
                    eta_str = f"ETA: {int(eta)}s"
                
                card.update_progress(
                    progress=progress,
                    speed=speed_str,
                    eta=eta_str,
                    status=status,
                )
        
        self.after(0, update)
    
    def _on_complete(self, task_id, filename):
        """Handle download completion."""
        def update():
            if task_id in self.progress_cards:
                self.progress_cards[task_id].update_progress(
                    progress=100, status="finished"
                )
            
            self._set_status(f"✅ Download complete!", "success")
            self.stats_widget.update_stats(downloads=self.download_count)
            
            # Add to downloads page
            self._add_to_downloads_list(task_id, filename)
        
        self.after(0, update)
    
    def _on_error(self, error_msg, task_id):
        """Handle download errors."""
        def update():
            if task_id in self.progress_cards:
                self.progress_cards[task_id].update_progress(
                    progress=0, status="error"
                )
            else:
                # Fetch-related error: restore the UI
                self.loading_frame.pack_forget()
                self.fetch_btn.configure(state="normal", text="🔍  Analyze")
                self.playlist_fetch_btn.configure(
                    state="normal", text="🔄  Load Playlist"
                )
            
            short_error = error_msg[:150] if len(error_msg) > 150 else error_msg
            self._set_status(f"❌ {short_error}", "error")
        
        self.after(0, update)
    
    def _add_to_downloads_list(self, task_id, filename):
        """Add completed download to the downloads page."""
        self.downloads_empty.pack_forget()
        
        item = ctk.CTkFrame(
            self.downloads_container,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
        )
        item.pack(fill="x", pady=(0, 8))
        
        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        
        # Icon
        ctk.CTkLabel(
            inner,
            text="✅",
            font=("Segoe UI", 18),
        ).pack(side="left", padx=(0, 12))
        
        # Info
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        name = os.path.basename(filename) if filename else task_id
        ctk.CTkLabel(
            info_frame,
            text=name[:60] + "..." if len(name) > 60 else name,
            font=("Segoe UI Semibold", 13),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text="Downloaded successfully",
            font=("Segoe UI", 11),
            text_color=COLORS["accent_green"],
            anchor="w",
        ).pack(anchor="w")
    
    # ==================== Playlist ====================
    
    def _fetch_playlist(self):
        """Fetch playlist information."""
        url = self.playlist_url_entry.get().strip()
        
        if not url:
            self.playlist_status.configure(
                text="⚠️ Please enter a playlist URL",
                text_color=COLORS["warning"]
            )
            return
        
        self.playlist_status.configure(
            text="⏳ Loading playlist...",
            text_color=COLORS["accent_blue"]
        )
        self.playlist_fetch_btn.configure(state="disabled", text="⏳  Loading...")
        
        # Clear previous
        for widget in self.playlist_view_container.winfo_children():
            widget.destroy()
        
        self.playlist_view_target = self.playlist_view_container
        self._current_playlist_url = url
        self.engine.fetch_playlist_info(url)
    
    def _on_playlist_info(self, info):
        """Handle playlist info received."""
        self.after(0, lambda: self._display_playlist(info))
    
    def _display_playlist(self, info):
        """Display playlist information in the target container."""
        self.playlist_fetch_btn.configure(state="normal", text="🔄  Load Playlist")
        
        entries = info.get('entries', [])
        if not entries:
            self.playlist_status.configure(
                text="❌ No videos found in playlist",
                text_color=COLORS["error"]
            )
            return
        
        target = getattr(self, 'playlist_view_target', self.playlist_view_container)
        
        for widget in target.winfo_children():
            widget.destroy()
        
        playlist_title = info.get('title', 'Unknown Playlist')
        count = len(entries)
        
        self.playlist_status.configure(
            text=f"✅ Loaded {count} videos",
            text_color=COLORS["accent_green"]
        )
        
        # Playlist info card
        info_card = ctk.CTkFrame(
            target,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        info_card.pack(fill="x")
        
        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            info_inner,
            text=f"📋  {playlist_title}",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")
        
        stats_row = ctk.CTkFrame(info_inner, fg_color="transparent")
        stats_row.pack(anchor="w", pady=(8, 0))
        
        ctk.CTkLabel(
            stats_row,
            text=f"🎬 {count} videos",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 20))
        
        channel = info.get('channel', info.get('uploader', ''))
        if channel:
            ctk.CTkLabel(
                stats_row,
                text=f"👤 {channel}",
                font=("Segoe UI", 13),
                text_color=COLORS["text_secondary"],
            ).pack(side="left")
        
        # Selection controls
        sel_frame = ctk.CTkFrame(
            target,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
        )
        sel_frame.pack(fill="x", pady=(15, 10))
        
        sel_inner = ctk.CTkFrame(sel_frame, fg_color="transparent")
        sel_inner.pack(fill="x", padx=15, pady=10)
        
        AccentButton(
            sel_inner,
            text="Select All",
            icon="☑️",
            command=lambda: self._select_all_playlist(True),
            color="blue",
            size="small",
            width=130,
        ).pack(side="left", padx=(0, 8))
        
        AccentButton(
            sel_inner,
            text="Deselect All",
            icon="⬜",
            command=lambda: self._select_all_playlist(False),
            color="dark",
            size="small",
            width=140,
        ).pack(side="left")
        
        self.playlist_count_label = ctk.CTkLabel(
            sel_inner,
            text=f"{count}/{count} selected",
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"],
        )
        self.playlist_count_label.pack(side="right")
        
        # Video items
        self.playlist_items = []
        self.playlist_selected = {}
        self.playlist_item_cards = []
        
        for i, entry in enumerate(entries):
            idx = i + 1
            title = entry.get('title', f'Video {idx}')
            duration = format_duration(entry.get('duration'))
            
            self.playlist_selected[idx] = True
            
            card = PlaylistItemCard(
                target,
                index=idx,
                title=title,
                duration=duration if duration != "Unknown" else "",
                selected=True,
                on_toggle=self._on_playlist_item_toggle,
            )
            card.pack(fill="x", pady=(0, 4))
            self.playlist_item_cards.append(card)
            self.playlist_items.append(entry)
        
        # Format/quality selector
        quality_card = ctk.CTkFrame(
            target,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        quality_card.pack(fill="x", pady=(15, 15))
        
        quality_inner = ctk.CTkFrame(quality_card, fg_color="transparent")
        quality_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            quality_inner,
            text="🎯  Choose Format",
            font=("Segoe UI Semibold", 18),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 15))
        
        self.playlist_format_selector = FormatSelector(quality_inner)
        self.playlist_format_selector.pack(fill="x")
        
        # Download button
        dl_btn = AccentButton(
            target,
            text=f"Download {count} Videos",
            icon="⬇️",
            command=lambda: self._download_playlist(info),
            color="purple",
            size="large",
        )
        dl_btn.pack(fill="x", ipady=5)
        self.playlist_dl_btn = dl_btn
    
    def _on_playlist_item_toggle(self, index, selected):
        """Handle playlist item selection toggle."""
        self.playlist_selected[index] = selected
        selected_count = sum(1 for v in self.playlist_selected.values() if v)
        total = len(self.playlist_selected)
        self.playlist_count_label.configure(text=f"{selected_count}/{total} selected")
        
        if hasattr(self, 'playlist_dl_btn'):
            self.playlist_dl_btn.configure(
                text=f"⬇️  Download {selected_count} Videos"
            )
    
    def _select_all_playlist(self, select):
        """Select or deselect all playlist items."""
        for card in self.playlist_item_cards:
            card.set_selected(select)
        
        for key in self.playlist_selected:
            self.playlist_selected[key] = select
        
        selected_count = sum(1 for v in self.playlist_selected.values() if v)
        total = len(self.playlist_selected)
        self.playlist_count_label.configure(text=f"{selected_count}/{total} selected")
        
        if hasattr(self, 'playlist_dl_btn'):
            self.playlist_dl_btn.configure(
                text=f"⬇️  Download {selected_count} Videos"
            )
    
    def _download_playlist(self, info):
        """Start playlist download."""
        selected = [k for k, v in self.playlist_selected.items() if v]
        
        if not selected:
            self.playlist_status.configure(
                text="⚠️ No videos selected",
                text_color=COLORS["warning"]
            )
            return
        
        settings = self.playlist_format_selector.get_settings()
        url = getattr(self, '_current_playlist_url', '') or self.playlist_url_entry.get().strip()
        
        self.playlist_status.configure(
            text=f"⬇️ Downloading {len(selected)} videos...",
            text_color=COLORS["accent_blue"]
        )
        
        # Create progress card on home
        self._show_page("home")
        
        title = info.get('title', 'Playlist')
        task_id = f"playlist_{title}"
        
        progress_card = ProgressCard(
            self.home_progress_container,
            title=f"📋 {title} ({len(selected)} videos)",
            task_id=task_id,
        )
        progress_card.pack(fill="x", pady=(0, 8))
        self.progress_cards[task_id] = progress_card
        self.home_downloads_label.configure(text="📥  Active Downloads")
        
        self.download_count += len(selected)
        self.stats_widget.update_stats(
            downloads=self.download_count,
            active=len(self.progress_cards)
        )
        
        self.engine.download_playlist(
            url=url,
            format_id=settings['format_id'],
            audio_only=settings['audio_only'],
            quality=settings['quality'],
            selected_indices=selected,
            task_id=task_id,
        )
        
        self._scroll_home_to_bottom()
    
    # ==================== Settings ====================
    
    def _change_download_path(self):
        """Change download directory."""
        path = filedialog.askdirectory(
            title="Select Download Folder",
            initialdir=self.engine.download_path,
        )
        
        if path:
            self.engine.set_download_path(path)
            self.path_label.configure(text=path)
    
    def _change_theme(self, theme):
        """Change appearance theme."""
        ctk.set_appearance_mode(theme.lower())
    
    def _open_download_folder(self):
        """Open the download folder in file explorer."""
        path = self.engine.download_path
        if os.path.exists(path):
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                subprocess.Popen(['xdg-open', path])
    
    # ==================== Helpers ====================
    
    def _set_status(self, text, status_type=""):
        """Update the status label."""
        color_map = {
            "success": COLORS["accent_green"],
            "error": COLORS["error"],
            "warning": COLORS["warning"],
            "info": COLORS["accent_blue"],
            "": COLORS["text_muted"],
        }
        
        self.status_label.configure(
            text=text,
            text_color=color_map.get(status_type, COLORS["text_muted"])
        )