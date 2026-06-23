# @file    can_interface.py
# @brief   CAN interface abstraction and SocketCAN implementation.
# @details Defines the CanMessage dataclass and the CanInterface protocol
#          used by all test layers. SocketCanInterface provides a real
#          hardware backend via python-can.

from __future__ import annotations
import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional, Protocol

import can


@dataclass
class CanMessage:
    arbitration_id: int        # CANopen COB-ID
    data: bytes
    is_fd: bool = True
    timestamp: float = 0.0     # seconds since epoch; 0 = not set


class CanInterface(Protocol):
    def send(self, msg: CanMessage) -> None:
        # Transmit a CAN FD frame. Raises CanSendError on bus-off.
        ...

    def recv(self, timeout_s: float) -> Optional[CanMessage]:
        # Block up to timeout_s for the next received frame. Returns None on timeout.
        ...

    def recv_matching(self, arbitration_id: int, timeout_s: float) -> CanMessage:
        # Block until a frame with the given COB-ID arrives. Raises TimeoutError if timeout_s elapses first.
        ...

    def flush(self) -> None:
        # Discard all buffered received frames.
        ...

    def close(self) -> None:
        # Release the CAN interface. Safe to call multiple times.
        ...


class SocketCanInterface:
    """
    Real SocketCAN implementation of CanInterface.
    Wraps python-can Bus with a background listener thread so that frames
    arriving before recv() is called are never dropped.
    """

    def __init__(self, channel: str = "can0", bitrate: int = 500_000,
                 data_bitrate: int = 2_000_000) -> None:
        self._channel = channel
        self._bitrate = bitrate
        self._data_bitrate = data_bitrate
        self._bus: Optional[can.Bus] = None
        self._rx: queue.Queue[CanMessage] = queue.Queue()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def open(self) -> None:
        self._bus = can.Bus(channel=self._channel,
                            interface="socketcan",
                            bitrate=self._bitrate,
                            data_bitrate=self._data_bitrate,
                            fd=True,)
        self._stop.clear()
        self._thread = threading.Thread(target=self._listener,
                                        daemon=True,
                                        name=f"can-rx-{self._channel}")
        self._thread.start()

    def _listener(self) -> None:
        while not self._stop.is_set():
            raw = self._bus.recv(timeout=0.05)
            if raw is not None:
                self._rx.put(CanMessage(arbitration_id=raw.arbitration_id,
                                        data=bytes(raw.data),
                                        is_fd=raw.is_fd,
                                        timestamp=raw.timestamp,))

    def send(self, msg: CanMessage) -> None:
        assert self._bus is not None, "call open() before send()"
        self._bus.send(can.Message(arbitration_id=msg.arbitration_id,
                                   data=msg.data,
                                   is_fd=msg.is_fd,
                                   is_extended_id=False,))

    def recv(self, timeout_s: float) -> Optional[CanMessage]:
        try:
            return self._rx.get(timeout=timeout_s)
        except queue.Empty:
            return None

    def recv_matching(self, arbitration_id: int, timeout_s: float) -> CanMessage:
        deadline = time.monotonic() + timeout_s
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            msg = self.recv(remaining)
            if msg is None:
                break
            if msg.arbitration_id == arbitration_id:
                return msg
        raise TimeoutError(
            f"No frame with COB-ID 0x{arbitration_id:04X} within {timeout_s}s"
        )

    def flush(self) -> None:
        while not self._rx.empty():
            try:
                self._rx.get_nowait()
            except queue.Empty:
                break

    def close(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._bus:
            self._bus.shutdown()
            self._bus = None
