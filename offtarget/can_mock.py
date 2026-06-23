# @file    can_mock.py
# @brief   In-process virtual CAN bus for off-target testing.
# @details Implements the CanInterface protocol without hardware. Scripted
#          replies are automatically queued when a matching COB-ID is sent.

from __future__ import annotations

import queue
import time
from typing import Optional

from common.can_interface import CanMessage
from common.can_protocol import L0_HMI_COB, encode_version_response


# Maps an outgoing COB-ID to the scripted reply the mock queues automatically.
# Extend this dict as more off-target tests are added.
_SCRIPTED_REPLIES: dict[int, CanMessage] = {
    L0_HMI_COB.REQUEST_BOARD_VERSION: encode_version_response(0, 2, 0),
}


class CanMock:
    """In-process virtual CAN bus. No hardware required.

    For every frame sent whose COB-ID has a scripted reply, the reply is
    immediately queued in the receive buffer so recv / recv_matching can
    return it.
    """

    def __init__(self) -> None:
        self._rx: queue.Queue[CanMessage] = queue.Queue()

    def send(self, msg: CanMessage) -> None:
        reply = _SCRIPTED_REPLIES.get(msg.arbitration_id)
        if reply is not None:
            self._rx.put(reply)

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
        pass
