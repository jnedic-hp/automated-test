# @file    log_widget.py
# @brief   Shared message log widget.

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from datetime import datetime
from common_cfg import Common

# Alias
STATE = Common.State
TAG   = Common.Tag

class LogWidget(ttk.LabelFrame):
    _TAGS = {
        TAG.TX:   {"foreground": "#1a6ecc"},
        TAG.RX:   {"foreground": "#267326"},
        TAG.VER:  {"foreground": "#267326", "font": ("Courier", 9, "bold")},
        TAG.ERR:  {"foreground": "red"},
        TAG.WARN: {"foreground": "orange"},
        TAG.SUC:  {"foreground": "#267326"},
        TAG.INF:  {"foreground": "#555555"},
    }

    DEFAULT_FILE_EXTENSION = ".txt"

    FILE_TYPES = (
        ("Text Files", "*.txt"),
        ("Log Files", "*.log"),
        ("All Files", "*.*"),
    )

    TXT_MSG_LOG   = "Message Log"
    TXT_CLEAR_LOG = "Clear Log"
    TXT_SAVE_LOG  = "Save Log"

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, text=self.TXT_MSG_LOG, padding=8, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        self._text = scrolledtext.ScrolledText(self, height=8, state=STATE.DIS, font=("Courier", 9),)
        self._text.pack(fill=tk.BOTH, expand=True)

        for tag, cfg in self._TAGS.items():
            self._text.tag_config(tag, **cfg)

        log_btn_frame = ttk.Frame(self)
        log_btn_frame.pack(anchor=tk.E, pady=(4, 0))

        save_log_btn = ttk.Button(log_btn_frame, text=self.TXT_SAVE_LOG, command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=(0, 4))

        clear_log_btn = ttk.Button(log_btn_frame, text=self.TXT_CLEAR_LOG, command=self.clear)
        clear_log_btn.pack(side=tk.LEFT)

    def log(self, text: str, tag: str = "info") -> None:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"[{ts}] [{tag.upper()}] {text}\n"

        self._text.config(state=STATE.NORM)
        self._text.insert(tk.END, line, tag)
        self._text.see(tk.END)
        self._text.config(state=STATE.DIS)

    def clear(self) -> None:
        self._text.config(state=STATE.NORM)
        self._text.delete("1.0", tk.END)
        self._text.config(state=STATE.DIS)

    def save_log(self) -> None:
        file_path = filedialog.asksaveasfilename(title=self.TXT_SAVE_LOG,
                                                 defaultextension=self.DEFAULT_FILE_EXTENSION,
                                                 filetypes=self.FILE_TYPES)

        if not file_path:
            return

        content = self._text.get("1.0", tk.END)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.log(f"Log saved to: {file_path}", "info")
