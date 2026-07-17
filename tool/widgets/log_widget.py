# @file    log_widget.py
# @brief   Shared message log widget.

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from datetime import datetime


class LogWidget(ttk.LabelFrame):
    _TAGS = {
        "tx":    {"foreground": "#1a6ecc"},
        "rx":    {"foreground": "#267326"},
        "ver":   {"foreground": "#267326", "font": ("Courier", 9, "bold")},
        "error": {"foreground": "red"},
        "info":  {"foreground": "#555555"},
    }

    DEFAULT_FILE_EXTENSION = ".txt"

    FILE_TYPES = (
        ("Text Files", "*.txt"),
        ("Log Files", "*.log"),
        ("All Files", "*.*"),
    )

    TXT_MSG_LOG     = "Message Log"
    TXT_CLEAR_LOG   = "Clear Log"
    TXT_SAVE_LOG    = "Save Log"

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, text=self.TXT_MSG_LOG, padding=8, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        self._text = scrolledtext.ScrolledText(self, height=8, state="disabled", font=("Courier", 9),)
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
        ts   = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"[{ts}]  {text}\n"
        self._text.config(state="normal")
        self._text.insert(tk.END, line, tag)
        self._text.see(tk.END)
        self._text.config(state="disabled")

    def clear(self) -> None:
        self._text.config(state="normal")
        self._text.delete("1.0", tk.END)
        self._text.config(state="disabled")

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
