"""
HikmahYT - Custom Widgets
Beautiful, reusable UI components
"""

import customtkinter as ctk
from ui.styles import COLORS, FONTS, DIMENSIONS
from PIL import Image, ImageDraw, ImageFont
import io
import math


class GradientFrame(ctk.CTkFrame):
    """A frame with simulated gradient background."""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_main"],
            corner_radius=0,
            **kwargs
        )


class LogoWidget(ctk.CTkFrame):
    """HikmahYT Logo Widget."""
    
    def __init__(self, master, size="large", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        if size == "large":
            font_size = 28
        elif size == "medium":
            font_size = 22
        else:
            font_size = 16
        
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(anchor="center")
        
        # Icon part
        icon_label = ctk.CTkLabel(
            logo_frame,
            text="▶",
            font=("Segoe UI", font_size + 4, "bold"),
            text_color=COLORS["accent_primary"],
        )
        icon_label.pack(side="left", padx=(0, 5))
        
        # "Hikmah" part
        name_label = ctk.CTkLabel(
            logo_frame,
            text="Hikmah",
            font=("Segoe UI Black", font_size, "bold"),
            text_color=COLORS["text_primary"],
        )
        name_label.pack(side="left")
        
        # "YT" part
        yt_label = ctk.CTkLabel(
            logo_frame,
            text="YT",
            font=("Segoe UI Black", font_size, "bold"),
            text_color=COLORS["accent_primary"],
        )
        yt_label.pack(side="left")


class ModernEntry(ctk.CTkFrame):
    """Modern styled entry with icon."""
    
    def __init__(self, master, placeholder="", icon="🔗", **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_input"],
            corner_radius=DIMENSIONS["input_corner"],
            border_width=2,
            border_color=COLORS["border"],
            **kwargs
        )
        
        self._focused = False
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI", 18),
            text_color=COLORS["text_muted"],
            width=40,
        )
        icon_label.pack(side="left", padx=(15, 5), pady=5)
        
        # Entry
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=("Segoe UI", 14),
            fg_color="transparent",
            border_width=0,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            height=DIMENSIONS["entry_height"] - 10,
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=5)
        
        # Bind focus events
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        self._focused = True
        self.configure(border_color=COLORS["accent_primary"])
    
    def _on_focus_out(self, event):
        self._focused = False
        self.configure(border_color=COLORS["border"])
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last):
        self.entry.delete(first, last)
    
    def insert(self, index, text):
        self.entry.insert(index, text)
    
    def bind_entry(self, event, callback):
        self.entry.bind(event, callback)


class AccentButton(ctk.CTkButton):
    """Modern accent-colored button."""
    
    def __init__(self, master, text="", icon="", command=None, 
                 color="primary", size="normal", **kwargs):
        
        color_map = {
            "primary": (COLORS["accent_primary"], COLORS["accent_secondary"]),
            "blue": (COLORS["accent_blue"], "#2d8fd4"),
            "green": (COLORS["accent_green"], "#27ae60"),
            "purple": (COLORS["accent_purple"], "#8e44ad"),
            "orange": (COLORS["accent_orange"], "#e55d2b"),
            "dark": (COLORS["bg_card"], COLORS["bg_card_hover"]),
        }
        
        fg_color, hover_color = color_map.get(color, color_map["primary"])
        
        height = 45 if size == "normal" else (38 if size == "small" else 52)
        font_size = 14 if size == "normal" else (12 if size == "small" else 16)
        
        display_text = f"{icon}  {text}" if icon else text
        
        super().__init__(
            master,
            text=display_text,
            command=command,
            font=("Segoe UI Semibold", font_size),
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=DIMENSIONS["button_corner"],
            height=height,
            text_color="white",
            **kwargs
        )


class IconButton(ctk.CTkButton):
    """Small icon-only button."""
    
    def __init__(self, master, icon="", command=None, 
                 tooltip="", size=35, **kwargs):
        super().__init__(
            master,
            text=icon,
            command=command,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            width=size,
            height=size,
            text_color=COLORS["text_secondary"],
            **kwargs
        )


class ModernCard(ctk.CTkFrame):
    """Modern card container with hover effect."""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=DIMENSIONS["card_corner"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(
            fg_color=COLORS["bg_card_hover"],
            border_color=COLORS["accent_primary"]
        )
    
    def _on_leave(self, event):
        self.configure(
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"]
        )


class VideoInfoCard(ctk.CTkFrame):
    """Card displaying video information."""
    
    def __init__(self, master, info=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=DIMENSIONS["card_corner"],
            **kwargs
        )
        
        if info:
            self.display_info(info)
    
    def display_info(self, info):
        """Display video information."""
        from utils.helpers import format_duration, format_views, format_date
        
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Thumbnail placeholder
        thumb_frame = ctk.CTkFrame(
            container,
            fg_color=COLORS["bg_secondary"],
            corner_radius=12,
            width=320,
            height=180,
        )
        thumb_frame.pack(side="left", padx=(0, 20))
        thumb_frame.pack_propagate(False)
        
        # Play icon on thumbnail
        play_label = ctk.CTkLabel(
            thumb_frame,
            text="▶",
            font=("Segoe UI", 48),
            text_color=COLORS["accent_primary"],
        )
        play_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Duration badge
        duration = format_duration(info.get('duration'))
        if duration != "Unknown":
            dur_badge = ctk.CTkLabel(
                thumb_frame,
                text=f" {duration} ",
                font=("Segoe UI", 11, "bold"),
                fg_color=COLORS["bg_dark"],
                corner_radius=5,
                text_color="white",
            )
            dur_badge.place(relx=0.95, rely=0.92, anchor="se")
        
        # Info section
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Title
        title = info.get('title', 'Unknown Title')
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
            wraplength=400,
            justify="left",
        )
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Channel
        channel = info.get('channel', info.get('uploader', 'Unknown'))
        channel_label = ctk.CTkLabel(
            info_frame,
            text=f"👤  {channel}",
            font=("Segoe UI", 13),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        channel_label.pack(anchor="w", pady=(0, 5))
        
        # Stats row
        stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        stats_frame.pack(anchor="w", pady=(5, 10))
        
        views = format_views(info.get('view_count'))
        date = format_date(info.get('upload_date', ''))
        
        for i, (icon, text) in enumerate([
            ("👁", views),
            ("📅", date),
        ]):
            if text and text != "N/A" and text != "Unknown":
                stat = ctk.CTkLabel(
                    stats_frame,
                    text=f"{icon}  {text}",
                    font=("Segoe UI", 12),
                    text_color=COLORS["text_muted"],
                )
                stat.pack(side="left", padx=(0, 20))
        
        # Tags
        tags_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        tags_frame.pack(anchor="w", pady=(5, 0))
        
        # Quality tag
        height = info.get('height', 0)
        if height:
            quality_text = f"{height}p"
            if height >= 2160:
                quality_text = "4K"
            elif height >= 1440:
                quality_text = "2K"
            
            tag = ctk.CTkLabel(
                tags_frame,
                text=f" {quality_text} ",
                font=("Segoe UI", 10, "bold"),
                fg_color=COLORS["accent_primary"],
                corner_radius=5,
                text_color="white",
            )
            tag.pack(side="left", padx=(0, 8))
        
        # Format tag
        ext = info.get('ext', 'mp4')
        fmt_tag = ctk.CTkLabel(
            tags_frame,
            text=f" {ext.upper()} ",
            font=("Segoe UI", 10, "bold"),
            fg_color=COLORS["accent_blue"],
            corner_radius=5,
            text_color="white",
        )
        fmt_tag.pack(side="left", padx=(0, 8))


class ProgressCard(ctk.CTkFrame):
    """Download progress card."""
    
    def __init__(self, master, title="", task_id="", 
                 on_pause=None, on_resume=None, on_retry=None, on_skip=None,
                 **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            **kwargs
        )
        
        self.task_id = task_id
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_retry = on_retry
        self.on_skip = on_skip
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=12)
        
        # Top row: title and status
        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 8))
        
        self.title_label = ctk.CTkLabel(
            top_row,
            text=title[:60] + "..." if len(title) > 60 else title,
            font=("Segoe UI Semibold", 13),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True)
        
        self.status_label = ctk.CTkLabel(
            top_row,
            text="⏳ Preparing...",
            font=("Segoe UI", 11),
            text_color=COLORS["accent_orange"],
        )
        self.status_label.pack(side="right")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            container,
            height=6,
            corner_radius=3,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent_primary"],
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)
        
        # Bottom row: stats
        bottom_row = ctk.CTkFrame(container, fg_color="transparent")
        bottom_row.pack(fill="x")
        
        self.progress_label = ctk.CTkLabel(
            bottom_row,
            text="0%",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        )
        self.progress_label.pack(side="left")
        
        self.speed_label = ctk.CTkLabel(
            bottom_row,
            text="",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        )
        self.speed_label.pack(side="left", padx=(20, 0))
        
        self.eta_label = ctk.CTkLabel(
            bottom_row,
            text="",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        )
        self.eta_label.pack(side="right")
        
        # Control row: pause / resume toggle
        control_row = ctk.CTkFrame(container, fg_color="transparent")
        control_row.pack(fill="x", pady=(8, 0))
        
        self._is_paused = False
        
        self.toggle_btn = ctk.CTkButton(
            control_row,
            text="⏸  Pause",
            font=("Segoe UI Semibold", 11),
            fg_color=COLORS["accent_orange"],
            hover_color="#e55d2b",
            corner_radius=8,
            height=28,
            width=110,
            text_color="white",
            command=self._toggle_pause,
        )
        self.toggle_btn.pack(side="left")
        
        # Error actions: retry / skip (only shown when the task fails)
        self.retry_btn = ctk.CTkButton(
            control_row,
            text="🔄  Retry",
            font=("Segoe UI Semibold", 11),
            fg_color=COLORS["accent_blue"],
            hover_color="#2d8fd4",
            corner_radius=8,
            height=28,
            width=90,
            text_color="white",
            command=self._retry,
        )
        
        self.skip_btn = ctk.CTkButton(
            control_row,
            text="⏭  Skip",
            font=("Segoe UI Semibold", 11),
            fg_color=COLORS["bg_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            height=28,
            width=90,
            text_color=COLORS["text_secondary"],
            command=self._skip,
        )
    
    def _retry(self):
        if self.on_retry:
            self.on_retry()
    
    def _skip(self):
        if self.on_skip:
            self.on_skip()
    
    def _toggle_pause(self):
        if self._is_paused:
            if self.on_resume:
                self.on_resume()
            self._is_paused = False
            self.toggle_btn.configure(
                text="⏸  Pause",
                fg_color=COLORS["accent_orange"],
                hover_color="#e55d2b",
            )
        else:
            if self.on_pause:
                self.on_pause()
            self._is_paused = True
            self.toggle_btn.configure(
                text="▶  Resume",
                fg_color=COLORS["accent_green"],
                hover_color="#27ae60",
            )
    
    def update_progress(self, progress=None, speed="", eta="", status="downloading"):
        """Update progress display."""
        if progress is not None:
            self.progress_bar.set(progress / 100)
            self.progress_label.configure(text=f"{progress:.1f}%")
        
        if speed:
            self.speed_label.configure(text=f"⚡ {speed}")
        
        if eta:
            self.eta_label.configure(text=f"⏱ {eta}")
        
        if status == "downloading":
            self.status_label.configure(
                text="⬇️ Downloading",
                text_color=COLORS["accent_blue"]
            )
            self._is_paused = False
            self.toggle_btn.configure(
                state="normal",
                text="⏸  Pause",
                fg_color=COLORS["accent_orange"],
                hover_color="#e55d2b",
            )
            self.retry_btn.pack_forget()
            self.skip_btn.pack_forget()
        elif status == "paused":
            self.status_label.configure(
                text="⏸ Paused",
                text_color=COLORS["warning"]
            )
            self._is_paused = True
            self.toggle_btn.configure(
                state="normal",
                text="▶  Resume",
                fg_color=COLORS["accent_green"],
                hover_color="#27ae60",
            )
            self.retry_btn.pack_forget()
            self.skip_btn.pack_forget()
        elif status == "finished":
            self.status_label.configure(
                text="✅ Complete",
                text_color=COLORS["accent_green"]
            )
            self.progress_bar.configure(progress_color=COLORS["accent_green"])
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="100%")
            self._is_paused = False
            self.toggle_btn.configure(state="disabled")
            self.retry_btn.pack_forget()
            self.skip_btn.pack_forget()
        elif status == "error":
            self.status_label.configure(
                text="❌ Error",
                text_color=COLORS["error"]
            )
            self.progress_bar.configure(progress_color=COLORS["error"])
            self._is_paused = False
            self.toggle_btn.configure(state="disabled")
            self.retry_btn.pack(side="left", padx=(8, 0))
            self.skip_btn.pack(side="left", padx=(8, 0))


class PlaylistItemCard(ctk.CTkFrame):
    """Individual playlist item card."""
    
    def __init__(self, master, index, title, duration="", 
                 selected=True, on_toggle=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            corner_radius=10,
            height=50,
            **kwargs
        )
        self.pack_propagate(False)
        
        self.index = index
        self.selected = selected
        self.on_toggle = on_toggle
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Checkbox
        self.checkbox = ctk.CTkCheckBox(
            container,
            text="",
            width=24,
            height=24,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=5,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            border_color=COLORS["border"],
            command=self._toggle,
        )
        if selected:
            self.checkbox.select()
        self.checkbox.pack(side="left", padx=(0, 10))
        
        # Index
        idx_label = ctk.CTkLabel(
            container,
            text=f"{index}.",
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"],
            width=35,
        )
        idx_label.pack(side="left", padx=(0, 8))
        
        # Title
        title_text = title[:65] + "..." if len(str(title)) > 65 else title
        title_label = ctk.CTkLabel(
            container,
            text=title_text,
            font=("Segoe UI", 12),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Duration
        if duration:
            dur_label = ctk.CTkLabel(
                container,
                text=duration,
                font=("Segoe UI", 11),
                text_color=COLORS["text_muted"],
            )
            dur_label.pack(side="right", padx=(10, 0))
    
    def _toggle(self):
        self.selected = self.checkbox.get() == 1
        if self.on_toggle:
            self.on_toggle(self.index, self.selected)
    
    def set_selected(self, selected):
        self.selected = selected
        if selected:
            self.checkbox.select()
        else:
            self.checkbox.deselect()


class SidebarButton(ctk.CTkButton):
    """Sidebar navigation button."""
    
    def __init__(self, master, text="", icon="", active=False,
                 command=None, **kwargs):
        
        self._active = active
        
        super().__init__(
            master,
            text=f"  {icon}   {text}",
            command=command,
            font=("Segoe UI Semibold", 13),
            fg_color=COLORS["accent_primary"] if active else "transparent",
            hover_color=COLORS["bg_card_hover"],
            corner_radius=10,
            height=45,
            anchor="w",
            text_color=COLORS["text_primary"] if active else COLORS["text_secondary"],
            **kwargs
        )
    
    def set_active(self, active):
        self._active = active
        if active:
            self.configure(
                fg_color=COLORS["accent_primary"],
                text_color=COLORS["text_primary"]
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"]
            )


class QualitySelector(ctk.CTkFrame):
    """Quality selection widget."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.selected_quality = ctk.StringVar(value="1080")
        self.selected_format = ctk.StringVar(value="video")
        
        # Format toggle
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            format_frame,
            text="Format",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))
        
        toggle_frame = ctk.CTkFrame(
            format_frame,
            fg_color=COLORS["bg_secondary"],
            corner_radius=10,
        )
        toggle_frame.pack(fill="x")
        
        self.video_btn = ctk.CTkButton(
            toggle_frame,
            text="🎬  Video",
            font=("Segoe UI Semibold", 13),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            corner_radius=8,
            height=40,
            command=lambda: self._set_format("video"),
        )
        self.video_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)
        
        self.audio_btn = ctk.CTkButton(
            toggle_frame,
            text="🎵  Audio",
            font=("Segoe UI Semibold", 13),
            fg_color="transparent",
            hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            height=40,
            text_color=COLORS["text_secondary"],
            command=lambda: self._set_format("audio"),
        )
        self.audio_btn.pack(side="left", fill="x", expand=True, padx=3, pady=3)
        
        # Quality options
        self.quality_label = ctk.CTkLabel(
            self,
            text="Quality",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        )
        self.quality_label.pack(anchor="w", pady=(10, 8))
        
        self.quality_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quality_frame.pack(fill="x")
        
        self._create_quality_buttons()
    
    def _create_quality_buttons(self):
        """Create quality selection buttons."""
        for widget in self.quality_frame.winfo_children():
            widget.destroy()
        
        if self.selected_format.get() == "video":
            qualities = [
                ("8K", "4320", "🌈"),
                ("4K", "2160", "🟣"),
                ("2K", "1440", "🔵"),
                ("1080p", "1080", "🟢"),
                ("720p", "720", "🟡"),
                ("480p", "480", "🟠"),
                ("360p", "360", "🔴"),
                ("240p", "240", "⚪"),
                ("144p", "144", "⬜"),
            ]
        else:
            qualities = [
                ("320kbps", "320", "🟣"),
                ("256kbps", "256", "🔵"),
                ("192kbps", "192", "🟢"),
                ("128kbps", "128", "🟡"),
            ]
        
        row_frame = None
        for i, (label, value, icon) in enumerate(qualities):
            if i % 3 == 0:
                row_frame = ctk.CTkFrame(self.quality_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
            
            is_selected = self.selected_quality.get() == value
            
            btn = ctk.CTkButton(
                row_frame,
                text=f"{icon} {label}",
                font=("Segoe UI Semibold", 12),
                fg_color=COLORS["accent_primary"] if is_selected else COLORS["bg_secondary"],
                hover_color=COLORS["bg_card_hover"],
                corner_radius=8,
                height=38,
                text_color="white" if is_selected else COLORS["text_secondary"],
                command=lambda v=value: self._set_quality(v),
            )
            btn.pack(side="left", fill="x", expand=True, padx=2)
    
    def _set_format(self, fmt):
        self.selected_format.set(fmt)
        
        if fmt == "video":
            self.video_btn.configure(
                fg_color=COLORS["accent_primary"],
                text_color="white"
            )
            self.audio_btn.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"]
            )
            self.selected_quality.set("1080")
        else:
            self.audio_btn.configure(
                fg_color=COLORS["accent_primary"],
                text_color="white"
            )
            self.video_btn.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"]
            )
            self.selected_quality.set("320")
        
        self._create_quality_buttons()
    
    def _set_quality(self, quality):
        self.selected_quality.set(quality)
        self._create_quality_buttons()
    
    def get_settings(self):
        return {
            'format': self.selected_format.get(),
            'quality': self.selected_quality.get(),
            'audio_only': self.selected_format.get() == "audio",
        }


class FormatSelector(ctk.CTkFrame):
    """Format selection widget showing all available formats with sizes.

    Lists real video formats (resolution, extension, file size) and audio
    formats from yt-dlp, plus a "Best Quality" auto option. Falls back to
    classic quality buttons when no format list is provided (e.g. playlists).
    """

    def __init__(self, master, formats=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.formats = formats or []
        self.selected_format_id = ctk.StringVar(value="best")
        self.selected_audio = ctk.BooleanVar(value=False)
        self.selected_quality = ctk.StringVar(value="best")
        self._option_rows = []
        self._build_layout()

    # ==================== Build ====================

    def _build_layout(self):
        """(Re)build the entire selector."""
        for widget in self.winfo_children():
            widget.destroy()
        self._option_rows = []

        best_frame = ctk.CTkFrame(self, fg_color="transparent")
        best_frame.pack(fill="x", pady=(0, 10))
        self._create_option_button(
            best_frame,
            label="⚡  Best Quality (Auto)",
            value="best",
            is_audio=False,
            quality="best",
        )

        if self.formats:
            self._build_video_section()
            self._build_audio_section()
        else:
            self._build_quality_fallback()

    def _build_video_section(self):
        """Build video format options grouped by resolution."""
        from utils.helpers import format_size

        video = self._group_video_formats()
        if not video:
            return

        ctk.CTkLabel(
            self,
            text="🎬  Video Formats",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(6, 8))

        for item in video:
            label = f"📺  {item['height']}p"
            if item.get('ext'):
                label += f"  •  {item['ext']}"
            if item.get('size') and item['size'] != "Unknown":
                label += f"  •  {item['size']}"
            if item.get('fps') and item['fps'] > 30:
                label += f"  •  {item['fps']}fps"
            if item.get('merge'):
                label += "  (merge)"

            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", pady=1)
            self._create_option_button(
                frame,
                label=label,
                value=item['value'],
                is_audio=False,
                quality=item['quality'],
            )

    def _build_audio_section(self):
        """Build audio format options."""
        from utils.helpers import format_size

        audio = self._group_audio_formats()
        if not audio:
            return

        ctk.CTkLabel(
            self,
            text="🎵  Audio Formats",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(10, 8))

        for item in audio:
            label = f"🎵  {item['label']}"
            if item.get('size') and item['size'] != "Unknown":
                label += f"  •  {item['size']}"

            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", pady=1)
            self._create_option_button(
                frame,
                label=label,
                value=item['value'],
                is_audio=True,
                quality=item['quality'],
            )

    def _build_quality_fallback(self):
        """Fallback quality buttons used when no format list is available."""
        ctk.CTkLabel(
            self,
            text="🎬  Video Quality",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(6, 8))

        for label, h in [
            ("8K", "4320"), ("4K", "2160"), ("2K", "1440"),
            ("1080p", "1080"), ("720p", "720"), ("480p", "480"),
            ("360p", "360"), ("240p", "240"), ("144p", "144"),
        ]:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", pady=1)
            self._create_option_button(
                frame,
                label=f"🎬  {label}",
                value=f"bv*[height<={h}]+ba/b[height<={h}]/b",
                is_audio=False,
                quality=h,
            )

        ctk.CTkLabel(
            self,
            text="🎵  Audio Quality (MP3)",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(10, 8))

        for label in ["320kbps", "256kbps", "192kbps", "128kbps"]:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", pady=1)
            self._create_option_button(
                frame,
                label=f"🎵  {label}",
                value="bestaudio/best",
                is_audio=True,
                quality=label.replace("kbps", ""),
            )

    # ==================== Options ====================

    def _create_option_button(self, master, label, value, is_audio, quality):
        selected = (
            value == self.selected_format_id.get()
            and is_audio == self.selected_audio.get()
        )
        btn = ctk.CTkButton(
            master,
            text=label,
            anchor="w",
            font=("Segoe UI Semibold", 12),
            fg_color=COLORS["accent_primary"] if selected else COLORS["bg_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            height=38,
            text_color="white" if selected else COLORS["text_secondary"],
            command=lambda v=value, a=is_audio: self._select(v, a),
        )
        btn.pack(fill="x")
        self._option_rows.append({
            'btn': btn,
            'value': value,
            'audio': is_audio,
            'quality': quality,
        })

    def _select(self, value, is_audio):
        self.selected_format_id.set(value)
        self.selected_audio.set(is_audio)
        self._refresh_buttons()

    def _refresh_buttons(self):
        for opt in self._option_rows:
            selected = (
                opt['value'] == self.selected_format_id.get()
                and opt['audio'] == self.selected_audio.get()
            )
            if selected:
                opt['btn'].configure(
                    fg_color=COLORS["accent_primary"], text_color="white"
                )
            else:
                opt['btn'].configure(
                    fg_color=COLORS["bg_secondary"],
                    text_color=COLORS["text_secondary"],
                )

    # ==================== Data ====================

    def _group_video_formats(self):
        """Return per-resolution best video format entries (sorted desc)."""
        from utils.helpers import format_size

        grouped = {}
        for f in self.formats:
            vcodec = f.get('vcodec')
            if not vcodec or vcodec == 'none':
                continue
            height = f.get('height')
            if not height:
                continue
            combined = f.get('acodec') != 'none'

            cur = grouped.get(height)
            if cur is None:
                grouped[height] = {'format': f, 'combined': combined}
            else:
                cur_combined = cur['combined']
                if combined and not cur_combined:
                    grouped[height] = {'format': f, 'combined': combined}
                elif combined == cur_combined:
                    fsize = f.get('filesize') or f.get('filesize_approx') or 0
                    csize = cur['format'].get('filesize') \
                        or cur['format'].get('filesize_approx') or 0
                    if fsize > csize:
                        grouped[height] = {'format': f, 'combined': combined}

        items = []
        for height in sorted(grouped.keys(), reverse=True):
            entry = grouped[height]
            f = entry['format']
            size = f.get('filesize') or f.get('filesize_approx')
            if not entry['combined']:
                bsize = self._best_audio_size()
                if size and bsize:
                    size = size + bsize

            # Use a robust yt-dlp selector rather than a bare format id,
            # which can be unavailable on some player clients.
            value = f"bv*[height<={height}]+ba/b[height<={height}]/b"

            items.append({
                'height': height,
                'ext': f.get('ext', ''),
                'fps': f.get('fps') or 0,
                'size': format_size(size) if size else "Unknown",
                'merge': not entry['combined'],
                'value': value,
                'quality': str(height),
            })
        return items

    def _best_audio_size(self):
        best = None
        for f in self.formats:
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                fsize = f.get('filesize') or f.get('filesize_approx')
                if fsize and (best is None or fsize > best):
                    best = fsize
        return best

    def _group_audio_formats(self):
        """Return audio formats grouped by bitrate (sorted desc)."""
        from utils.helpers import format_size

        grouped = {}
        for f in self.formats:
            if f.get('vcodec') != 'none' or f.get('acodec') == 'none':
                continue
            abr = f.get('abr') or f.get('tbr')
            if not abr:
                continue
            key = int(round(abr))
            cur = grouped.get(key)
            if cur is None or abr > cur.get('_abr', 0):
                grouped[key] = {'format': f, '_abr': abr}

        items = []
        for abr in sorted(grouped.keys(), reverse=True):
            f = grouped[abr]['format']
            ext = f.get('ext', '')
            size = f.get('filesize') or f.get('filesize_approx')
            label = f"{abr} kbps" + (f"  •  {ext}" if ext else "")
            items.append({
                'label': label,
                'size': format_size(size) if size else "Unknown",
                'value': 'bestaudio/best',
                'quality': str(abr),
            })

        if not items:
            items.append({
                'label': "Best Audio",
                'size': "Unknown",
                'value': 'bestaudio/best',
                'quality': '192',
            })
        return items

    def get_settings(self):
        """Return the current selection as engine download settings."""
        for opt in self._option_rows:
            if (opt['value'] == self.selected_format_id.get()
                    and opt['audio'] == self.selected_audio.get()):
                return {
                    'format_id': opt['value'],
                    'quality': opt['quality'],
                    'audio_only': opt['audio'],
                }
        return {
            'format_id': 'best',
            'quality': 'best',
            'audio_only': False,
        }


class DownloadOptionsBar(ctk.CTkFrame):
    """Advanced download options (container, codecs, thumb, subs, HDR...)."""

    CONTAINERS = ("Auto", "MP4", "MKV", "WebM", "AVI", "MOV", "FLV")
    CODECS = ("MP3", "AAC", "M4A", "OPUS", "VORBIS", "FLAC", "ALAC", "WAV")
    VCODECS = ("Auto", "H.264", "H.265/HEVC", "AV1", "VP9", "VP8")
    FPS = ("Auto", "60fps")
    SUBS_FMT = ("SRT", "VTT", "ASS", "LRC")

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self,
            text="⚙️  Options",
            font=("Segoe UI Semibold", 14),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))

        # Row 1: video codec + container
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))

        self._create_dropdown(
            row1, "Video Codec", self.VCODECS, "vcodec_menu"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        self._create_dropdown(
            row1, "Container", self.CONTAINERS, "container_menu"
        ).pack(side="left", fill="x", expand=True)

        # Row 2: audio codec + fps + subtitle format
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 8))

        self._create_dropdown(
            row2, "Audio Codec", self.CODECS, "codec_menu"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        self._create_dropdown(
            row2, "FPS", self.FPS, "fps_menu"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        self._create_dropdown(
            row2, "Sub Format", self.SUBS_FMT, "subfmt_menu"
        ).pack(side="left", fill="x", expand=True)

        # Row 3: checkboxes + language
        row3 = ctk.CTkFrame(self, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 8))

        self.thumb_var = ctk.BooleanVar(value=False)
        self.meta_var = ctk.BooleanVar(value=False)
        self.subs_var = ctk.BooleanVar(value=False)
        self.embed_subs_var = ctk.BooleanVar(value=False)
        self.hdr_var = ctk.BooleanVar(value=False)
        self.json_var = ctk.BooleanVar(value=False)

        for text, var in [
            ("🖼 Thumbnail", self.thumb_var),
            ("🏷 Metadata", self.meta_var),
            ("💬 Subtitles", self.subs_var),
            ("🔤 Embed Subs", self.embed_subs_var),
            ("🌞 HDR", self.hdr_var),
            ("📄 JSON", self.json_var),
        ]:
            ctk.CTkCheckBox(
                row3,
                text=text,
                variable=var,
                font=("Segoe UI", 11),
                fg_color=COLORS["accent_primary"],
                hover_color=COLORS["accent_secondary"],
                border_color=COLORS["border"],
                text_color=COLORS["text_secondary"],
                checkbox_width=16,
                checkbox_height=16,
                corner_radius=4,
            ).pack(side="left", padx=(0, 10))

        self.lang_entry = ModernEntry(row3, placeholder="en", icon="🌐")
        self.lang_entry.configure(width=110)
        self.lang_entry.pack(side="left")
        self.lang_entry.insert(0, "en")

    def _create_dropdown(self, master, label, values, attr):
        frame = ctk.CTkFrame(master, fg_color="transparent")

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))

        menu = ctk.CTkOptionMenu(
            frame,
            values=list(values),
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_secondary"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_secondary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            corner_radius=8,
            height=30,
            width=110,
        )
        menu.set(values[0])
        menu.pack(fill="x")
        setattr(self, attr, menu)
        return frame

    def get_settings(self):
        """Return engine-compatible download options."""
        container = self.container_menu.get().strip().lower()
        codec = self.codec_menu.get().strip().lower()
        lang = self.lang_entry.get().strip() or "en"

        vcodec = self.vcodec_menu.get().strip()
        if vcodec == "H.265/HEVC":
            vcodec = "h265"
        elif vcodec == "H.264":
            vcodec = "h264"
        elif vcodec == "AV1":
            vcodec = "av1"
        elif vcodec == "VP9":
            vcodec = "vp9"
        elif vcodec == "VP8":
            vcodec = "vp8"
        else:
            vcodec = ""

        fps = self.fps_menu.get().strip()
        fps60 = fps == "60fps"

        sub_format = self.subfmt_menu.get().strip().lower()
        if sub_format == "srt":
            sub_format = ""

        return {
            'container': '' if container == 'auto' else container,
            'audio_codec': codec if codec in ('mp3', 'aac', 'm4a', 'opus', 'vorbis', 'flac', 'alac', 'wav') else 'mp3',
            'download_thumb': self.thumb_var.get(),
            'embed_meta': self.meta_var.get(),
            'download_subs': self.subs_var.get(),
            'subs_langs': lang,
            'embed_subs': self.embed_subs_var.get(),
            'codec': vcodec,
            'hdr': self.hdr_var.get(),
            'fps60': fps60,
            'sub_format': sub_format,
            'write_json': self.json_var.get(),
        }


class StatsWidget(ctk.CTkFrame):
    """Statistics display widget."""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            **kwargs
        )
        
        self.stats = {
            'downloaded': 0,
            'total_size': 0,
            'active': 0,
        }
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=12)
        
        stats_data = [
            ("📥", "Downloads", "0", COLORS["accent_green"]),
            ("📊", "Total Size", "0 MB", COLORS["accent_blue"]),
            ("⚡", "Active", "0", COLORS["accent_orange"]),
        ]
        
        self.stat_labels = {}
        
        for icon, label, value, color in stats_data:
            stat_frame = ctk.CTkFrame(container, fg_color="transparent")
            stat_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                stat_frame,
                text=icon,
                font=("Segoe UI", 20),
            ).pack()
            
            val_label = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Segoe UI Bold", 16),
                text_color=color,
            )
            val_label.pack()
            self.stat_labels[label] = val_label
            
            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Segoe UI", 11),
                text_color=COLORS["text_muted"],
            ).pack()
    
    def update_stats(self, downloads=None, total_size=None, active=None):
        if downloads is not None:
            self.stat_labels["Downloads"].configure(text=str(downloads))
        if total_size is not None:
            self.stat_labels["Total Size"].configure(text=total_size)
        if active is not None:
            self.stat_labels["Active"].configure(text=str(active))