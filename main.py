#!/usr/bin/env python3
"""
HikmahYT - Modern YouTube Video Downloader
A beautiful, smooth, and feature-rich YouTube downloader.
"""

import sys
import os
import customtkinter as ctk
from ui.main_window import HikmahYTApp

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = HikmahYTApp()
    app.mainloop()

if __name__ == "__main__":
    main()