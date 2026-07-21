# @file    hp_tool.py
# @brief   Henny Penny Tool

import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from common_cfg import Common
from widgets.connection_widget import ConnectionWidget
from widgets.log_widget import LogWidget
from tabs.can_requests import CanRequests
from tabs.flash_firmware import FlashFirmware

# Alias
COLOR = Common.Color

# Add Tabs here
_TABS = [
    ("Flash Firmware", FlashFirmware),
    ("CAN Requests",  CanRequests),
]

class HPTool:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(Common.TOOL_NAME)
        self.root.resizable(True, True)
        self._build_ui()
        self._register_tabs()
        self._maximize()

    def _maximize(self) -> None:
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                w = self.root.winfo_screenwidth()
                h = self.root.winfo_screenheight()
                self.root.geometry(f"{w}x{h}+0+0")

    def _build_ui(self) -> None:
        self.root.configure(bg=COLOR.HP_RED)

        # Style for ttk frames
        style = ttk.Style()
        style.configure("Outer.TFrame", background=COLOR.HP_RED)
        style.configure("Left.TFrame", background=COLOR.HP_BLACK)
        style.configure("Right.TFrame", background=COLOR.HP_BLACK)

        # Main frame
        m_frame = ttk.Frame(self.root, padding=6, style="Outer.TFrame")
        m_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        m_frame.columnconfigure(0, weight=2)
        m_frame.columnconfigure(1, weight=1)
        m_frame.rowconfigure(0, weight=1)

        # Left frame
        l_frame = ttk.Frame(m_frame, padding=3, style="Left.TFrame")
        l_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))

        self.log = LogWidget(l_frame)
        self.con = ConnectionWidget(l_frame, log_fn=self.log.log)

        self.con.pack(fill=tk.X, pady=(0, 6))
        self.log.pack(fill=tk.BOTH, expand=True)

        # Right frame
        r_frame = ttk.Frame(m_frame, padding=3, style="Right.TFrame")
        r_frame.grid(row=0, column=1, sticky="nsew", padx=(3, 0))

        self.nb = ttk.Notebook(r_frame, width=300)
        self.nb.pack(fill=tk.BOTH, expand=True)

    def _register_tabs(self) -> None:
        for tab_name, PanelClass in _TABS:
            frame = ttk.Frame(self.nb, padding=10)
            self.nb.add(frame, text=tab_name)
            PanelClass(parent=frame,
                       bus_getter=self.con.bus_getter,
                       log_fn=self.log.log,
                       register_rx=self.con.register_rx,
                       register_rx_all=self.con.register_rx_all,)

    def run(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self) -> None:
        self.con.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    HPTool().run()

