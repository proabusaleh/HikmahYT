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
    SidebarButton, FormatSelector, StatsWidget, GradientFrame,
    DownloadOptionsBar,
)
from downloader import DownloadEngine
from utils.helpers import (
    is_valid_url, is_playlist_url, format_size,
    format_duration, format_views, get_default_download_path,
    get_site_name
)

APP_VERSION = "5.0.0"


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
        self.engine.set_callback('on_search', self._on_search_results)
        
        # State
        self.current_page = "home"
        self.current_info = None
        self.playlist_items = []
        self.playlist_selected = {}
        self.download_count = 0
        self.progress_cards = {}
        self.downloads_cards = {}
        self.task_states = {}
        self.sidebar_buttons = {}
        self._batch_mode = False
        self._batch_pending = []
        self._batch_settings = None
        self._batch_opts = None
        
        # Build UI
        self._build_ui()
        
        # Watch the clipboard for URLs
        self.after(1200, self._start_clipboard_polling)
    
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
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 10),
            text_color=COLORS["text_muted"],
        ).pack(side="bottom", pady=(0, 10))
    
    def _build_home_page(self):
        """Build the home/main download page with video & playlist modes."""
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
        header.pack(fill="x", padx=25, pady=(25, 15))
        
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
        
        # Download type toggle (single video / playlist)
        mode_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        mode_card.pack(fill="x", padx=25, pady=(0, 15))
        
        mode_inner = ctk.CTkFrame(mode_card, fg_color="transparent")
        mode_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            mode_inner,
            text="Choose Download Type",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))
        
        toggle_frame = ctk.CTkFrame(
            mode_inner,
            fg_color=COLORS["bg_secondary"],
            corner_radius=10,
        )
        toggle_frame.pack(fill="x")
        
        self.home_mode_video_btn = ctk.CTkButton(
            toggle_frame,
            text="🎬  Single Video",
            font=("Segoe UI Semibold", 14),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            corner_radius=8,
            height=42,
            text_color="white",
            command=lambda: self._set_home_mode("video"),
        )
        self.home_mode_video_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)
        
        self.home_mode_playlist_btn = ctk.CTkButton(
            toggle_frame,
            text="📋  Playlist",
            font=("Segoe UI Semibold", 14),
            fg_color="transparent",
            hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            height=42,
            text_color=COLORS["text_secondary"],
            command=lambda: self._set_home_mode("playlist"),
        )
        self.home_mode_playlist_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)
        
        self.home_mode_search_btn = ctk.CTkButton(
            toggle_frame,
            text="🔍  Search",
            font=("Segoe UI Semibold", 14),
            fg_color="transparent",
            hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            height=42,
            text_color=COLORS["text_secondary"],
            command=lambda: self._set_home_mode("search"),
        )
        self.home_mode_search_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)
        
        # Active downloads section (packed first so mode sections can sit above)
        self.home_downloads_header = ctk.CTkFrame(scroll, fg_color="transparent")
        self.home_downloads_header.pack(fill="x", padx=25, pady=(10, 10))
        
        self.home_downloads_label = ctk.CTkLabel(
            self.home_downloads_header,
            text="",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.home_downloads_label.pack(side="left")
        
        self.downloads_shortcut_btn = AccentButton(
            self.home_downloads_header,
            text="Downloads",
            icon="📥",
            command=lambda: self._show_page("downloads"),
            color="dark",
            size="small",
            width=130,
        )
        self.downloads_shortcut_btn.pack(side="right")
        
        self.home_progress_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.home_progress_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # ================== Single Video mode ==================
        self.home_video_section = ctk.CTkFrame(scroll, fg_color="transparent")
        
        input_section = ctk.CTkFrame(
            self.home_video_section,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        input_section.pack(fill="x", pady=(0, 15))
        
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
        
        # Clipboard suggestion bar (hidden until a URL is detected)
        self.clipboard_bar = ctk.CTkFrame(
            input_inner,
            fg_color=COLORS["bg_secondary"],
            corner_radius=8,
        )
        
        self.clipboard_bar_label = ctk.CTkLabel(
            self.clipboard_bar,
            text="📋 Clipboard URL detected",
            font=("Segoe UI", 12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.clipboard_bar_label.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=8)
        
        AccentButton(
            self.clipboard_bar,
            text="Use",
            icon="✅",
            command=self._use_clipboard_url,
            color="green",
            size="small",
            width=80,
        ).pack(side="left", padx=(0, 6))
        
        IconButton(
            self.clipboard_bar,
            icon="✖",
            command=self._dismiss_clipboard_bar,
            tooltip="Dismiss",
            size=28,
        ).pack(side="left", padx=(0, 6))
        
        self.clipboard_bar.pack_forget()
        self._last_clipboard_url = ""
        
        # Button row
        self.url_btn_row = ctk.CTkFrame(input_inner, fg_color="transparent")
        self.url_btn_row.pack(fill="x")
        
        self.fetch_btn = AccentButton(
            self.url_btn_row,
            text="Analyze",
            icon="🔍",
            command=self._fetch_info,
            color="primary",
            width=160,
        )
        self.fetch_btn.pack(side="left", padx=(0, 10))
        
        AccentButton(
            self.url_btn_row,
            text="Paste",
            icon="📋",
            command=self._paste_url,
            color="dark",
            width=120,
        ).pack(side="left", padx=(0, 10))
        
        AccentButton(
            self.url_btn_row,
            text="Clear",
            icon="🗑",
            command=self._clear_url,
            color="dark",
            width=120,
        ).pack(side="left")
        
        AccentButton(
            self.url_btn_row,
            text="Batch",
            icon="📋",
            command=self._open_batch_dialog,
            color="green",
            width=120,
        ).pack(side="left", padx=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.home_video_section,
            text="",
            font=("Segoe UI", 13),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(anchor="w", pady=(0, 10))
        
        self.loading_frame = ctk.CTkFrame(
            self.home_video_section,
            fg_color="transparent",
        )
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="⏳ Fetching video information...",
            font=("Segoe UI", 14),
            text_color=COLORS["accent_blue"],
        )
        self.loading_label.pack(pady=20)
        
        self.info_container = ctk.CTkFrame(
            self.home_video_section,
            fg_color="transparent",
        )
        self.info_container.pack(fill="x", pady=(0, 15))
        
        self.quality_container = ctk.CTkFrame(
            self.home_video_section,
            fg_color="transparent",
        )
        self.quality_container.pack(fill="x", pady=(0, 15))
        
        self.download_btn_container = ctk.CTkFrame(
            self.home_video_section,
            fg_color="transparent",
        )
        self.download_btn_container.pack(fill="x", pady=(0, 15))
        
        # ================== Playlist mode ==================
        self.home_playlist_section = ctk.CTkFrame(scroll, fg_color="transparent")
        
        pl_input_card = ctk.CTkFrame(
            self.home_playlist_section,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        pl_input_card.pack(fill="x", pady=(0, 15))
        
        pl_inner = ctk.CTkFrame(pl_input_card, fg_color="transparent")
        pl_inner.pack(fill="x", padx=20, pady=20)
        
        self.home_playlist_url_entry = ModernEntry(
            pl_inner,
            placeholder="Paste playlist URL here...",
            icon="📋",
        )
        self.home_playlist_url_entry.pack(fill="x", pady=(0, 15))
        self.home_playlist_url_entry.bind_entry(
            "<Return>", lambda e: self._fetch_home_playlist()
        )
        
        pl_btn_row = ctk.CTkFrame(pl_inner, fg_color="transparent")
        pl_btn_row.pack(fill="x")
        
        self.home_playlist_load_btn = AccentButton(
            pl_btn_row,
            text="Load Playlist",
            icon="🔄",
            command=self._fetch_home_playlist,
            color="purple",
            width=180,
        )
        self.home_playlist_load_btn.pack(side="left", padx=(0, 10))
        
        AccentButton(
            pl_btn_row,
            text="Paste",
            icon="📋",
            command=self._paste_home_playlist_url,
            color="dark",
            width=120,
        ).pack(side="left")
        
        self.home_playlist_status = ctk.CTkLabel(
            self.home_playlist_section,
            text="",
            font=("Segoe UI", 13),
            text_color=COLORS["text_muted"],
        )
        self.home_playlist_status.pack(anchor="w", pady=(0, 10))
        
        self.home_playlist_container = ctk.CTkFrame(
            self.home_playlist_section,
            fg_color="transparent",
        )
        self.home_playlist_container.pack(fill="x", pady=(0, 15))
        
        # ================== Search mode ==================
        self.home_search_section = ctk.CTkFrame(scroll, fg_color="transparent")
        
        search_card = ctk.CTkFrame(
            self.home_search_section,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        search_card.pack(fill="x", pady=(0, 15))
        
        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            search_inner,
            text="🔍  Search YouTube",
            font=("Segoe UI Semibold", 16),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 12))
        
        self.search_entry = ModernEntry(
            search_inner,
            placeholder="Search videos, music, lectures...",
            icon="🔍",
        )
        self.search_entry.pack(fill="x", pady=(0, 12))
        self.search_entry.bind_entry("<Return>", lambda e: self._do_search())
        
        search_btn_row = ctk.CTkFrame(search_inner, fg_color="transparent")
        search_btn_row.pack(fill="x")
        
        self.search_btn = AccentButton(
            search_btn_row,
            text="Search",
            icon="🔍",
            command=self._do_search,
            color="blue",
            width=140,
        )
        self.search_btn.pack(side="left", padx=(0, 10))
        
        AccentButton(
            search_btn_row,
            text="Paste",
            icon="📋",
            command=self._paste_search_query,
            color="dark",
            width=110,
        ).pack(side="left")
        
        self.search_status = ctk.CTkLabel(
            self.home_search_section,
            text="",
            font=("Segoe UI", 13),
            text_color=COLORS["text_muted"],
        )
        self.search_status.pack(anchor="w", pady=(0, 10))
        
        self.search_results_container = ctk.CTkFrame(
            self.home_search_section,
            fg_color="transparent",
        )
        self.search_results_container.pack(fill="x", pady=(0, 15))
        
        # Show single video mode by default
        self.home_mode = "video"
        self.home_video_section.pack(
            fill="x", padx=25, pady=(0, 10),
            before=self.home_downloads_header,
        )
    
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
        
        # ================== Parallel / active downloads ==================
        self.downloads_active_label = ctk.CTkLabel(
            scroll,
            text="⚡  Parallel Downloads",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.downloads_active_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        self.downloads_active_container = ctk.CTkFrame(
            scroll, fg_color="transparent"
        )
        self.downloads_active_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # ================== Completed downloads ==================
        self.downloads_completed_label = ctk.CTkLabel(
            scroll,
            text="✅  Completed",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.downloads_completed_label.pack(anchor="w", padx=25, pady=(0, 10))
        
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
        
        # Hide the parallel section until downloads actually start
        self._refresh_downloads_section()
    
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
        
        # Concurrent Downloads
        concurrent_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        concurrent_card.pack(fill="x", padx=25, pady=(0, 15))
        
        concurrent_inner = ctk.CTkFrame(concurrent_card, fg_color="transparent")
        concurrent_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            concurrent_inner,
            text="⚡  Concurrent Downloads",
            font=("Segoe UI Semibold", 16),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        
        ctk.CTkLabel(
            concurrent_inner,
            text="How many downloads run at the same time",
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 12))
        
        threads_row = ctk.CTkFrame(concurrent_inner, fg_color="transparent")
        threads_row.pack(fill="x")
        
        ctk.CTkLabel(
            threads_row,
            text="Parallel Threads",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")
        
        self.concurrent_menu = ctk.CTkOptionMenu(
            threads_row,
            values=["1", "2", "3", "4", "5", "6"],
            font=("Segoe UI", 13),
            fg_color=COLORS["bg_secondary"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_secondary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            command=self._set_concurrent,
            width=120,
        )
        self.concurrent_menu.set(str(self.engine.max_concurrent))
        self.concurrent_menu.pack(side="right")
        
        # Download Options (network + filenames)
        net_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=15,
        )
        net_card.pack(fill="x", padx=25, pady=(0, 15))
        
        net_inner = ctk.CTkFrame(net_card, fg_color="transparent")
        net_inner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            net_inner,
            text="🌐  Network & Files",
            font=("Segoe UI Semibold", 16),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 12))
        
        # Cookies
        cookies_row = ctk.CTkFrame(net_inner, fg_color="transparent")
        cookies_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            cookies_row,
            text="Cookies File",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            width=140,
            anchor="w",
        ).pack(side="left")
        
        self.cookies_entry = ctk.CTkEntry(
            cookies_row,
            placeholder_text="cookies.txt (for age-restricted / private videos)",
            font=("Segoe UI", 12),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=34,
        )
        self.cookies_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.cookies_entry.insert(0, self.engine.cookiefile)
        
        AccentButton(
            cookies_row,
            text="Browse",
            icon="📂",
            command=self._browse_cookies,
            color="dark",
            size="small",
            width=90,
        ).pack(side="right")
        
        # Proxy
        proxy_row = ctk.CTkFrame(net_inner, fg_color="transparent")
        proxy_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            proxy_row,
            text="Proxy",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            width=140,
            anchor="w",
        ).pack(side="left")
        
        self.proxy_entry = ctk.CTkEntry(
            proxy_row,
            placeholder_text="http://host:port or socks5://host:port",
            font=("Segoe UI", 12),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=34,
        )
        self.proxy_entry.pack(side="left", fill="x", expand=True)
        self.proxy_entry.insert(0, self.engine.proxy)
        
        # Speed limit
        speed_row = ctk.CTkFrame(net_inner, fg_color="transparent")
        speed_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            speed_row,
            text="Speed Limit",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            width=140,
            anchor="w",
        ).pack(side="left")
        
        self.speed_entry = ctk.CTkEntry(
            speed_row,
            placeholder_text="KB/s (0 = no limit)",
            font=("Segoe UI", 12),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=34,
            width=160,
        )
        self.speed_entry.pack(side="left")
        speed_kb = self.engine.limit_rate // 1024 if self.engine.limit_rate else 0
        self.speed_entry.insert(0, str(speed_kb) if speed_kb else "0")
        
        ctk.CTkLabel(
            speed_row,
            text=" KB/s",
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"],
        ).pack(side="left")
        
        # Filename template
        tmpl_row = ctk.CTkFrame(net_inner, fg_color="transparent")
        tmpl_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            tmpl_row,
            text="Filename",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            width=140,
            anchor="w",
        ).pack(side="left")
        
        self.template_entry = ctk.CTkEntry(
            tmpl_row,
            placeholder_text="%(title)s.%(ext)s",
            font=("Segoe UI", 12),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=34,
        )
        self.template_entry.pack(side="left", fill="x", expand=True)
        self.template_entry.insert(0, self.engine.filename_template)
        
        # Audio subfolder + save button
        opt_row = ctk.CTkFrame(net_inner, fg_color="transparent")
        opt_row.pack(fill="x", pady=(10, 0))
        
        self.audio_subfolder_var = ctk.BooleanVar(
            value=self.engine.audio_subfolder
        )
        ctk.CTkCheckBox(
            opt_row,
            text="Save audio in a 'Music' subfolder",
            variable=self.audio_subfolder_var,
            font=("Segoe UI", 12),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
        ).pack(side="left")
        
        AccentButton(
            opt_row,
            text="Apply",
            icon="💾",
            command=self._apply_network_settings,
            color="primary",
            size="small",
            width=110,
        ).pack(side="right")
        
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
    
    def _set_home_mode(self, mode):
        """Switch between single-video / playlist / search modes."""
        self.home_mode = mode
        
        self.home_mode_video_btn.configure(
            fg_color=COLORS["accent_primary"] if mode == "video" else "transparent",
            text_color="white" if mode == "video" else COLORS["text_secondary"],
        )
        self.home_mode_playlist_btn.configure(
            fg_color=COLORS["accent_primary"] if mode == "playlist" else "transparent",
            text_color="white" if mode == "playlist" else COLORS["text_secondary"],
        )
        self.home_mode_search_btn.configure(
            fg_color=COLORS["accent_primary"] if mode == "search" else "transparent",
            text_color="white" if mode == "search" else COLORS["text_secondary"],
        )
        
        self.home_video_section.pack_forget()
        self.home_playlist_section.pack_forget()
        self.home_search_section.pack_forget()
        
        if mode == "video":
            self.home_video_section.pack(
                fill="x", padx=25, pady=(0, 10),
                before=self.home_downloads_header,
            )
        elif mode == "playlist":
            self.home_playlist_section.pack(
                fill="x", padx=25, pady=(0, 10),
                before=self.home_downloads_header,
            )
        else:
            self.home_search_section.pack(
                fill="x", padx=25, pady=(0, 10),
                before=self.home_downloads_header,
            )
        
        self._clear_results()
    
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
            self.playlist_status_label.configure(
                text="⚠️ Nothing to paste from clipboard",
                text_color=COLORS["warning"]
            )
    
    def _paste_home_playlist_url(self):
        """Paste URL to the home playlist entry."""
        try:
            url = self.clipboard_get()
            self.home_playlist_url_entry.delete(0, "end")
            self.home_playlist_url_entry.insert(0, url)
        except Exception:
            self.home_playlist_status.configure(
                text="⚠️ Nothing to paste from clipboard",
                text_color=COLORS["warning"]
            )
    
    def _fetch_home_playlist(self):
        """Fetch playlist information from the home page."""
        url = self.home_playlist_url_entry.get().strip()
        
        if not url:
            self.home_playlist_status.configure(
                text="⚠️ Please enter a playlist URL",
                text_color=COLORS["warning"]
            )
            return
        
        if not is_valid_url(url):
            self.home_playlist_status.configure(
                text="❌ Invalid or unsupported URL",
                text_color=COLORS["error"]
            )
            return
        
        self._clear_results()
        
        self.home_playlist_status.configure(
            text="⏳ Loading playlist...",
            text_color=COLORS["accent_blue"]
        )
        self.home_playlist_load_btn.configure(state="disabled", text="⏳  Loading...")
        
        self.playlist_status_label = self.home_playlist_status
        self.playlist_view_target = self.home_playlist_container
        self._current_playlist_url = url
        self.engine.fetch_playlist_info(url)
    
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
    
    # ==================== Batch Download ====================
    
    def _open_batch_dialog(self):
        """Open a dialog to paste multiple URLs (one per line)."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Batch Download - HikmahYT")
        dialog.geometry("560x460")
        dialog.configure(fg_color=COLORS["bg_main"])
        dialog.transient(self)
        dialog.grab_set()
        
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="📋  Batch Download",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            container,
            text="Paste one URL per line. Videos use the format & options "
                 "currently selected on the Home page.",
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"],
            anchor="w",
            justify="left",
            wraplength=520,
        ).pack(anchor="w", pady=(5, 10))
        
        textbox = ctk.CTkTextbox(
            container,
            font=("Consolas", 13),
            fg_color=COLORS["bg_secondary"],
            corner_radius=10,
            border_width=0,
            text_color=COLORS["text_primary"],
        )
        textbox.pack(fill="both", expand=True, pady=(0, 12))
        
        # Prefill with clipboard text if it looks like a URL list
        try:
            clip = self.clipboard_get()
            if '\n' in clip and any(is_valid_url(l.strip()) for l in clip.splitlines()):
                textbox.insert("1.0", clip)
        except Exception:
            pass
        
        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x")
        
        AccentButton(
            btn_row,
            text="Download All",
            icon="⬇️",
            command=lambda: self._do_batch(textbox, dialog),
            color="green",
            width=160,
        ).pack(side="right")
        
        AccentButton(
            btn_row,
            text="Cancel",
            icon="✖",
            command=dialog.destroy,
            color="dark",
            width=120,
        ).pack(side="right", padx=(0, 10))
    
    def _do_batch(self, textbox, dialog):
        """Collect URLs from the dialog and start the batch."""
        raw = textbox.get("1.0", "end")
        urls = []
        for line in raw.splitlines():
            line = line.strip()
            if line and is_valid_url(line):
                urls.append(line)
        
        dialog.destroy()
        
        if not urls:
            self._set_status("⚠️ No valid URLs found in batch list", "warning")
            return
        
        settings, opts = self._current_download_settings()
        self._batch_mode = True
        self._batch_settings = settings
        self._batch_opts = opts
        self._batch_pending = list(urls)
        self._set_status(
            f"📋 Starting batch download of {len(urls)} videos...", "info"
        )
        self._batch_fetch_next()
    
    def _batch_fetch_next(self):
        """Fetch the next pending batch URL."""
        if self._batch_pending:
            url = self._batch_pending.pop(0)
            self._set_status(
                f"📋 Batch: {len(self._batch_pending) + 1} video(s) remaining...",
                "info",
            )
            self.engine.fetch_info(url)
        else:
            self._batch_mode = False
            self._set_status("✅ Batch download started", "success")
    
    def _batch_start_download(self, info):
        """Start the actual download for the fetched batch item."""
        title = info.get('title', 'Video')
        url = info.get('webpage_url', '')
        if not url:
            self._batch_fetch_next()
            return
        
        task_id = f"{title}_{self.download_count}"
        self.download_count += 1
        
        self._create_progress_cards(task_id, title)
        self.task_states[task_id] = "downloading"
        self.home_downloads_label.configure(text="📥  Active Downloads")
        self.stats_widget.update_stats(
            downloads=self.download_count,
            active=len(self.progress_cards),
        )
        
        settings = self._batch_settings or {
            'format_id': 'best', 'quality': 'best', 'audio_only': False,
        }
        opts = self._batch_opts or {}
        
        self.engine.download(
            url=url,
            format_id=settings['format_id'],
            audio_only=settings['audio_only'],
            quality=settings['quality'],
            task_id=task_id,
            **opts,
        )
        
        self._scroll_home_to_bottom()
        self._batch_fetch_next()
    
    def _current_download_settings(self):
        """Get the format + options currently selected on the Home page."""
        try:
            if (hasattr(self, 'format_selector')
                    and self.format_selector.winfo_exists()):
                settings = self.format_selector.get_settings()
            else:
                settings = {
                    'format_id': 'best',
                    'quality': 'best',
                    'audio_only': False,
                }
        except Exception:
            settings = {
                'format_id': 'best', 'quality': 'best', 'audio_only': False,
            }
        
        try:
            if (hasattr(self, 'options_bar')
                    and self.options_bar.winfo_exists()):
                opts = self.options_bar.get_settings()
            else:
                opts = {}
        except Exception:
            opts = {}
        
        return settings, opts
    
    # ==================== Search ====================
    
    def _paste_search_query(self):
        """Paste clipboard text into the search box."""
        try:
            query = self.clipboard_get()
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, query)
        except Exception:
            self.search_status.configure(
                text="⚠️ Nothing to paste from clipboard",
                text_color=COLORS["warning"],
            )
    
    def _do_search(self):
        """Run a YouTube search."""
        query = self.search_entry.get().strip()
        if not query:
            self.search_status.configure(
                text="⚠️ Enter a search query",
                text_color=COLORS["warning"],
            )
            return
        
        for widget in self.search_results_container.winfo_children():
            widget.destroy()
        
        self.search_status.configure(
            text="⏳ Searching...",
            text_color=COLORS["accent_blue"],
        )
        self.search_btn.configure(state="disabled", text="⏳  Searching...")
        self.engine.search(query)
    
    def _on_search_results(self, results):
        """Handle search results from the worker thread."""
        self.after(0, lambda: self._display_search_results(results))
    
    def _display_search_results(self, results):
        """Render search results on the home page."""
        self.search_btn.configure(state="normal", text="🔍  Search")
        
        for widget in self.search_results_container.winfo_children():
            widget.destroy()
        
        if not results:
            self.search_status.configure(
                text="❌ No results found",
                text_color=COLORS["error"],
            )
            return
        
        self.search_status.configure(
            text=f"✅ Found {len(results)} results",
            text_color=COLORS["accent_green"],
        )
        
        for res in results:
            self._search_result_item(res)
    
    def _search_result_item(self, res):
        """Create a single search result row."""
        item = ctk.CTkFrame(
            self.search_results_container,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
        )
        item.pack(fill="x", pady=(0, 8))
        
        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        
        # Info
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        title = res.get('title', 'Unknown')
        ctk.CTkLabel(
            info_frame,
            text=title[:70] + "..." if len(title) > 70 else title,
            font=("Segoe UI Semibold", 13),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")
        
        meta_bits = []
        if res.get('channel'):
            meta_bits.append(f"👤 {res['channel']}")
        duration = res.get('duration', 0)
        if duration:
            m, s = divmod(int(duration), 60)
            meta_bits.append(f"⏱ {m}:{s:02d}")
        if res.get('views'):
            meta_bits.append(f"👁 {format_views(res['views'])}")
        
        if meta_bits:
            ctk.CTkLabel(
                info_frame,
                text="  •  ".join(meta_bits),
                font=("Segoe UI", 11),
                text_color=COLORS["text_muted"],
                anchor="w",
            ).pack(anchor="w", pady=(3, 0))
        
        # Actions
        url = res.get('url', '')
        AccentButton(
            inner,
            text="Download",
            icon="⬇️",
            command=lambda: self._search_download(url, title),
            color="green",
            size="small",
            width=110,
        ).pack(side="right", padx=(8, 0))
        
        AccentButton(
            inner,
            text="Info",
            icon="🔍",
            command=lambda: self._search_open_info(url),
            color="dark",
            size="small",
            width=90,
        ).pack(side="right")
    
    def _search_download(self, url, title):
        """Download a search result directly."""
        if not url:
            return
        settings, opts = self._current_download_settings()
        
        task_id = f"{title}_{self.download_count}"
        self.download_count += 1
        
        self._create_progress_cards(task_id, title)
        self.task_states[task_id] = "downloading"
        self.home_downloads_label.configure(text="📥  Active Downloads")
        self.stats_widget.update_stats(
            downloads=self.download_count,
            active=len(self.progress_cards),
        )
        
        self.engine.download(
            url=url,
            format_id=settings['format_id'],
            audio_only=settings['audio_only'],
            quality=settings['quality'],
            task_id=task_id,
            **opts,
        )
        self._scroll_home_to_bottom()
    
    def _search_open_info(self, url):
        """Load a search result into the video info view."""
        if not url:
            return
        self._set_home_mode("video")
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self._fetch_info()
    
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
            self.playlist_status_label = self.home_playlist_status
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
        if self._batch_mode:
            self.after(0, lambda: self._batch_start_download(info))
        else:
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

        # Advanced options (container, audio codec, thumb, subtitles)
        self.options_bar = DownloadOptionsBar(quality_inner)
        self.options_bar.pack(fill="x", pady=(15, 0))
        
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
    
    def _create_progress_cards(self, task_id, title):
        """Create a progress card on both the Home and Downloads pages."""
        home_card = ProgressCard(
            self.home_progress_container,
            title=title,
            task_id=task_id,
            on_pause=lambda: self._pause_task(task_id),
            on_resume=lambda: self._resume_task(task_id),
            on_retry=lambda: self._retry_task(task_id),
            on_skip=lambda: self._skip_task(task_id),
        )
        home_card.pack(fill="x", pady=(0, 8))
        self.progress_cards[task_id] = home_card
        
        dl_card = ProgressCard(
            self.downloads_active_container,
            title=title,
            task_id=task_id,
            on_pause=lambda: self._pause_task(task_id),
            on_resume=lambda: self._resume_task(task_id),
            on_retry=lambda: self._retry_task(task_id),
            on_skip=lambda: self._skip_task(task_id),
        )
        dl_card.pack(fill="x", pady=(0, 8))
        self.downloads_cards[task_id] = dl_card
        
        self._refresh_downloads_section()
    
    def _update_all_cards(self, task_id, **kwargs):
        """Apply a progress update to both the Home and Downloads cards."""
        if task_id in self.progress_cards:
            self.progress_cards[task_id].update_progress(**kwargs)
        if task_id in self.downloads_cards:
            self.downloads_cards[task_id].update_progress(**kwargs)
    
    def _retry_task(self, task_id):
        """Retry a failed download."""
        if self.engine.retry_download(task_id):
            self.task_states[task_id] = "downloading"
            self._update_all_cards(task_id, status="downloading")
            self._set_status(f"🔄 Retrying: {task_id[:40]}...", "info")
    
    def _skip_task(self, task_id):
        """Dismiss a failed download from the lists."""
        for d in (self.progress_cards, self.downloads_cards):
            card = d.pop(task_id, None)
            if card is not None:
                card.destroy()
        self.task_states.pop(task_id, None)
        self._refresh_downloads_section()
        self._update_active_stats()
        self._set_status("⏭ Skipped download", "info")
    
    def _refresh_downloads_section(self):
        """Show/hide the Parallel Downloads section based on active cards."""
        has_active = bool(self.downloads_cards)
        if has_active:
            self.downloads_active_label.pack(
                anchor="w", padx=25, pady=(0, 10),
                before=self.downloads_completed_label,
            )
            self.downloads_active_container.pack(
                fill="x", padx=25, pady=(0, 20),
                before=self.downloads_completed_label,
            )
        else:
            self.downloads_active_label.pack_forget()
            self.downloads_active_container.pack_forget()
    
    def _start_download(self):
        """Start downloading the current video."""
        if not self.current_info:
            self._set_status("⚠️ No video loaded", "warning")
            return
        
        settings = self.format_selector.get_settings()
        opts = self.options_bar.get_settings()
        url = self.current_info.get('webpage_url', self.url_entry.get().strip())
        title = self.current_info.get('title', 'Unknown')
        task_id = f"{title}_{self.download_count}"
        
        self.download_count += 1
        
        # Create progress card on Home + Downloads pages
        self._create_progress_cards(task_id, title)
        self.task_states[task_id] = "downloading"
        
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
            **opts,
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
            if task_id in self.progress_cards or task_id in self.downloads_cards:
                status = data.get('status', '')
                self.task_states[task_id] = status
                
                if status == 'paused':
                    self._update_all_cards(task_id, status="paused")
                    self._update_active_stats()
                    return
                
                progress = data.get('progress', 0)
                speed = data.get('speed', 0)
                eta = data.get('eta', 0)
                
                speed_str = ""
                if speed:
                    speed_str = format_size(speed) + "/s"
                
                eta_str = ""
                if eta:
                    eta_str = f"ETA: {int(eta)}s"
                
                self._update_all_cards(
                    task_id,
                    progress=progress,
                    speed=speed_str,
                    eta=eta_str,
                    status=status,
                )
        
        self.after(0, update)
    
    def _pause_task(self, task_id):
        """Pause a running download."""
        if self.engine.pause_download(task_id):
            self.task_states[task_id] = "paused"
            self._set_status("⏸ Pausing download...", "warning")
    
    def _resume_task(self, task_id):
        """Resume a paused download."""
        if self.engine.resume_download(task_id):
            self.task_states[task_id] = "downloading"
            self._set_status("▶ Resuming download...", "info")
    
    def _update_active_stats(self):
        """Refresh the active download count on the sidebar stats."""
        active = sum(
            1 for s in self.task_states.values()
            if s in ("downloading", "paused", "pending")
        )
        self.stats_widget.update_stats(
            downloads=self.download_count,
            active=active,
        )
    
    def _on_complete(self, task_id, filename):
        """Handle download completion."""
        def update():
            self._update_all_cards(task_id, progress=100, status="finished")
            
            self.task_states[task_id] = "finished"
            self._set_status(f"✅ Download complete!", "success")
            self.stats_widget.update_stats(downloads=self.download_count)
            
            name = os.path.basename(filename) if filename else task_id
            self._notify("HikmahYT - Download Complete", name)
            
            # Remove the card from the Downloads "Parallel" list (the
            # completed item below replaces it), keep the Home card.
            dl_card = self.downloads_cards.pop(task_id, None)
            if dl_card is not None:
                dl_card.destroy()
            self._refresh_downloads_section()
            
            # Add to downloads page
            self._add_to_downloads_list(task_id, filename)
        
        self.after(0, update)
    
    def _on_error(self, error_msg, task_id):
        """Handle download errors."""
        def update():
            if task_id in self.progress_cards or task_id in self.downloads_cards:
                self._update_all_cards(task_id, progress=0, status="error")
                self.task_states[task_id] = "error"
                self._update_active_stats()
            elif self._batch_mode:
                # A batch fetch failed: skip to the next URL.
                self._set_status(f"❌ Batch item failed: {error_msg[:80]}", "error")
                self._batch_fetch_next()
                return
            else:
                # Fetch-related error: restore the UI
                self.loading_frame.pack_forget()
                self.fetch_btn.configure(state="normal", text="🔍  Analyze")
                self.playlist_fetch_btn.configure(
                    state="normal", text="🔄  Load Playlist"
                )
                if hasattr(self, 'home_playlist_load_btn'):
                    self.home_playlist_load_btn.configure(
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
        
        self.playlist_status_label = self.playlist_status
        self.playlist_view_target = self.playlist_view_container
        self._current_playlist_url = url
        self.engine.fetch_playlist_info(url)
    
    def _on_playlist_info(self, info):
        """Handle playlist info received."""
        self.after(0, lambda: self._display_playlist(info))
    
    def _display_playlist(self, info):
        """Display playlist information in the target container."""
        self.playlist_fetch_btn.configure(state="normal", text="🔄  Load Playlist")
        if hasattr(self, 'home_playlist_load_btn'):
            self.home_playlist_load_btn.configure(
                state="normal", text="🔄  Load Playlist"
            )
        
        entries = info.get('entries', [])
        if not entries:
            self.playlist_status_label.configure(
                text="❌ No videos found in playlist",
                text_color=COLORS["error"]
            )
            return
        
        target = getattr(self, 'playlist_view_target', self.playlist_view_container)
        
        for widget in target.winfo_children():
            widget.destroy()
        
        playlist_title = info.get('title', 'Unknown Playlist')
        count = len(entries)
        
        self.playlist_status_label.configure(
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
        
        # ============ Advanced playlist / channel options ============
        adv_card = ctk.CTkFrame(
            target,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
        )
        adv_card.pack(fill="x", pady=(0, 10))
        
        adv_inner = ctk.CTkFrame(adv_card, fg_color="transparent")
        adv_inner.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            adv_inner,
            text="🧠  Advanced (channels & playlists)",
            font=("Segoe UI Semibold", 13),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        
        adv_row1 = ctk.CTkFrame(adv_inner, fg_color="transparent")
        adv_row1.pack(fill="x", pady=(0, 8))
        
        # Index range
        range_frame = ctk.CTkFrame(adv_row1, fg_color="transparent")
        range_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(
            range_frame,
            text="Items",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))
        self.pl_range_entry = ctk.CTkEntry(
            range_frame,
            placeholder_text="1-50  (overrides selection)",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=30,
        )
        self.pl_range_entry.pack(fill="x")
        
        # Keyword filter
        kw_frame = ctk.CTkFrame(adv_row1, fg_color="transparent")
        kw_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(
            kw_frame,
            text="Title contains",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))
        self.pl_keyword_entry = ctk.CTkEntry(
            kw_frame,
            placeholder_text="keyword",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=30,
        )
        self.pl_keyword_entry.pack(fill="x")
        
        # Min duration
        dur_frame = ctk.CTkFrame(adv_row1, fg_color="transparent")
        dur_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(
            dur_frame,
            text="Min length (min)",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))
        self.pl_mindur_entry = ctk.CTkEntry(
            dur_frame,
            placeholder_text="0",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=30,
        )
        self.pl_mindur_entry.pack(fill="x")
        
        # Uploaded after
        date_frame = ctk.CTkFrame(adv_row1, fg_color="transparent")
        date_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            date_frame,
            text="Uploaded after",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))
        self.pl_dateafter_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="2024-01-01",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_secondary"],
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=30,
        )
        self.pl_dateafter_entry.pack(fill="x")
        
        adv_row2 = ctk.CTkFrame(adv_inner, fg_color="transparent")
        adv_row2.pack(fill="x", pady=(6, 0))
        
        self.pl_reverse_var = ctk.BooleanVar(value=False)
        self.pl_archive_var = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(
            adv_row2,
            text="🔃 Reverse order",
            variable=self.pl_reverse_var,
            font=("Segoe UI", 11),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 18))
        
        ctk.CTkCheckBox(
            adv_row2,
            text="⏭ Skip already downloaded",
            variable=self.pl_archive_var,
            font=("Segoe UI", 11),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
        ).pack(side="left")
        
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

        # Advanced options (container, audio codec, thumb, subtitles)
        self.playlist_options_bar = DownloadOptionsBar(quality_inner)
        self.playlist_options_bar.pack(fill="x", pady=(15, 0))
        
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
            self.playlist_status_label.configure(
                text="⚠️ No videos selected",
                text_color=COLORS["warning"]
            )
            return
        
        settings = self.playlist_format_selector.get_settings()
        opts = self.playlist_options_bar.get_settings()
        url = getattr(self, '_current_playlist_url', '') or self.playlist_url_entry.get().strip()
        
        # Advanced options
        range_str = self.pl_range_entry.get().strip()
        reverse = self.pl_reverse_var.get()
        archive = self.pl_archive_var.get()
        
        match_filters = {}
        keyword = self.pl_keyword_entry.get().strip()
        if keyword:
            match_filters['keyword'] = keyword
        
        try:
            min_dur_min = int(self.pl_mindur_entry.get().strip() or "0")
        except ValueError:
            min_dur_min = 0
        if min_dur_min > 0:
            match_filters['min_duration_sec'] = min_dur_min * 60
        
        date_after = self.pl_dateafter_entry.get().strip()
        if date_after:
            # Normalize YYYY-MM-DD or YYYY/MM/DD to yt-dlp's YYYYMMDD
            date_after = date_after.replace('-', '').replace('/', '')
            if date_after.isdigit():
                match_filters['date_after'] = date_after
        
        self.playlist_status_label.configure(
            text=f"⬇️ Downloading {len(selected)} videos...",
            text_color=COLORS["accent_blue"]
        )
        
        # Create progress card on home
        self._show_page("home")
        
        title = info.get('title', 'Playlist')
        task_id = f"playlist_{title}"
        
        self._create_progress_cards(
            task_id, f"📋 {title} ({len(selected)} videos)"
        )
        self.task_states[task_id] = "downloading"
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
            reverse=reverse,
            archive=archive,
            range_str=range_str,
            match_filters=match_filters or None,
            **opts,
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
    
    def _set_concurrent(self, n):
        """Set how many downloads run in parallel."""
        self.engine.set_max_concurrent(int(n))
        self._set_status(f"⚡ Concurrent downloads set to {n}", "info")
    
    def _browse_cookies(self):
        """Pick a Netscape cookies file."""
        path = filedialog.askopenfilename(
            title="Select Cookies File",
            filetypes=[("Cookies", "*.txt"), ("All Files", "*.*")],
        )
        if path:
            self.cookies_entry.delete(0, "end")
            self.cookies_entry.insert(0, path)
    
    def _apply_network_settings(self):
        """Apply cookies / proxy / speed / filename settings to the engine."""
        self.engine.set_cookiefile(self.cookies_entry.get())
        self.engine.set_proxy(self.proxy_entry.get())
        
        try:
            kb = int(self.speed_entry.get() or "0")
        except ValueError:
            kb = 0
        self.engine.set_limit_rate(kb * 1024)
        
        self.engine.set_filename_template(self.template_entry.get())
        self.engine.set_audio_subfolder(self.audio_subfolder_var.get())
        
        self._set_status("💾 Settings applied", "success")
    
    def _open_download_folder(self):
        """Open the download folder in file explorer."""
        path = self.engine.download_path
        if os.path.exists(path):
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                subprocess.Popen(['xdg-open', path])
    
    # ==================== Clipboard + Notifications ====================
    
    def _start_clipboard_polling(self):
        """Poll the clipboard for URLs and show a suggestion bar."""
        try:
            clip = self.clipboard_get()
        except Exception:
            clip = ""
        
        url = ""
        if clip:
            for line in clip.splitlines():
                line = line.strip()
                if line and is_valid_url(line):
                    url = line
                    break
        
        if url and url != self._last_clipboard_url:
            self._last_clipboard_url = url
            self._pending_clipboard_url = url
            self.clipboard_bar_label.configure(
                text=f"📋 Clipboard URL detected: {url[:60]}..."
                if len(url) > 60 else f"📋 Clipboard URL detected: {url}"
            )
            self.clipboard_bar.pack(
                fill="x", pady=(0, 12), before=self.url_btn_row
            )
        
        self.after(1200, self._start_clipboard_polling)
    
    def _use_clipboard_url(self):
        """Use the detected clipboard URL."""
        url = getattr(self, '_pending_clipboard_url', '')
        if not url:
            self._dismiss_clipboard_bar()
            return
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self._dismiss_clipboard_bar()
    
    def _dismiss_clipboard_bar(self):
        """Hide the clipboard suggestion bar."""
        self.clipboard_bar.pack_forget()
    
    def _notify(self, title, message):
        """Show a system notification when a download finishes."""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="HikmahYT",
                timeout=5,
            )
        except Exception:
            pass
    
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