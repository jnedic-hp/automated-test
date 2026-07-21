# @file    connection_widget.py
# @brief   connection widget - owns the bus, RX thread, and handler dispatch.

import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from common_cfg import Common

import can

# Alias
COLOR = Common.Color
STATE = Common.State
TAG = Common.Tag

INTERFACE_DEFAULTS: dict[str, str] ={
    "socketcan": "can0",
    "slcan":     "/dev/ttyUSB0",
}

BITRATES = ["125000", "250000", "500000", "1000000"]


class ConnectionWidget(ttk.LabelFrame):
    TXT_CAN_CONNECTION      = "CAN Connection"
    TXT_INTERFACE           = "Interface:"
    TXT_CHANNEL             = "Channel:"
    TXT_BITRATE             = "Bitrate:"
    TXT_CONNECT_BTN         = "Connect"
    TXT_STATUS_DISCONNECTED = "● Disconnected"

    def __init__(self, parent, log_fn: Optional[Callable] = None, **kwargs) -> None:
        super().__init__(parent, text=self.TXT_CAN_CONNECTION, padding=10, **kwargs)

        self._log_fn = log_fn or (lambda text, tag="info": None)
        self._bus: can.BusABC | None = None
        self._rx_thread: threading.Thread | None = None
        self._stop_rx = threading.Event()
        self._connected = False
        self._rx_handlers: dict[int, list] = {}
        self._rx_all_handlers: list = []

        self._build_ui()

    def _build_ui(self) -> None:
        interface_label = ttk.Label(self, text=self.TXT_INTERFACE)
        interface_label.grid(row=0, column=0, sticky=tk.W, padx=4)

        self.interface_var = tk.StringVar(value="socketcan")
        interface_combobox = ttk.Combobox(self, textvariable=self.interface_var,
                                          width=13,values=list(INTERFACE_DEFAULTS.keys()),
                                          state=STATE.RO,)
        interface_combobox.grid(row=0, column=1, padx=4)
        interface_combobox.bind("<<ComboboxSelected>>", self._on_interface_changed)

        channel_label = ttk.Label(self, text=self.TXT_CHANNEL)
        channel_label.grid(row=0, column=2, sticky=tk.W, padx=4)

        self.channel_var = tk.StringVar(value=INTERFACE_DEFAULTS["socketcan"])

        channel_entry = ttk.Entry(self, textvariable=self.channel_var, width=16)
        channel_entry.grid(row=0, column=3, padx=4)

        bitrate_label = ttk.Label(self, text=self.TXT_BITRATE)
        bitrate_label.grid(row=0, column=4, sticky=tk.W, padx=4)

        self.bitrate_var = tk.StringVar(value="500000")

        bitrate_combobox = ttk.Combobox(self, textvariable=self.bitrate_var,
                                        width=9, values=BITRATES, state=STATE.RO,)
        bitrate_combobox.grid(row=0, column=5, padx=4)

        self._connect_btn = ttk.Button(self, text=self.TXT_CONNECT_BTN, command=self._toggle_connection)
        self._connect_btn.grid(row=0, column=6, padx=8)

        self._status_lbl = ttk.Label(self, text=self.TXT_STATUS_DISCONNECTED, foreground=COLOR.HP_RED)
        self._status_lbl.grid(row=1, column=0, columnspan=7, sticky=tk.W, padx=4, pady=(4, 0))

    def bus_getter(self) -> can.BusABC | None:
        return self._bus

    def register_rx(self, cob_id: int, callback: Callable) -> None:
        self._rx_handlers.setdefault(cob_id, []).append(callback)

    def register_rx_all(self, callback: Callable) -> None:
        self._rx_all_handlers.append(callback)

    def disconnect(self) -> None:
        if self._connected:
            self._disconnect()

    # Connection logic
    def _on_interface_changed(self, _event=None) -> None:
        self.channel_var.set(INTERFACE_DEFAULTS.get(self.interface_var.get(), ""))

    def _toggle_connection(self) -> None:
        if not self._connected:
            self._connect()
        else:
            self._disconnect()

    def _connect(self) -> None:
        iface   = self.interface_var.get()
        channel = self.channel_var.get().strip()
        bitrate = int(self.bitrate_var.get())

        try:
            self._bus = can.Bus(interface=iface, channel=channel, bitrate=bitrate)
        except Exception as exc:
            self._log_fn(f"Connection failed: {exc}", tag=TAG.ERR)
            return

        self._connected = True
        self._stop_rx.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True, name="can-rx")
        self._rx_thread.start()

        self._connect_btn.config(text="Disconnect")
        self._status_lbl.config(text=f"● Connected — {iface} : {channel}", foreground="green")
        self._log_fn(f"Connected to {iface}:{channel}  bitrate={bitrate}", tag="info")

    def _disconnect(self) -> None:
        self._stop_rx.set()
        if self._bus:
            try:
                self._bus.shutdown()
            except Exception:
                pass
            self._bus = None

        self._connected = False
        self._connect_btn.config(text="Connect")
        self._status_lbl.config(text="● Disconnected", foreground="red")
        self._log_fn("Disconnected", tag="info")

    # RX thread + dispatch
    def _rx_loop(self) -> None:
        while not self._stop_rx.is_set():
            try:
                raw = self._bus.recv(timeout=0.05)
            except Exception:
                break
            if raw is not None:
                self.after(0, self._dispatch_rx, raw)

    def _dispatch_rx(self, raw: can.Message) -> None:
        self._log_fn(f"RX  0x{raw.arbitration_id:04X}  data={bytes(raw.data).hex()}",
                     tag="rx",)
        for cb in self._rx_handlers.get(raw.arbitration_id, []):
            cb(raw)
        for cb in self._rx_all_handlers:
            cb(raw)
