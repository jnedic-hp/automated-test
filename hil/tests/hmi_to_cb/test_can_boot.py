# @file    test_can_boot.py
# @brief   HIL tests for the Control Board CAN boot sequence.
# @details Verifies that the board sends a BackendReady response after
#          receiving a UiReady frame over the L0 CAN line.

import pytest
from common.can_protocol import L0_CB_COB, L0_HMI_RequestMessages

@pytest.mark.timeout(20)
def test_can_boot_backend_ready_after_ui(can_interface):
    """
    Given  the Control Board is in OPERATIONAL state
    When   the HIL sends L0_RequestUiReady
    Then   the Control Board responds with L0_ResponseBackendReady (COB-ID 0x1829)
    """

    can_interface.send(L0_HMI_RequestMessages.UiReady().encode())
    msg = can_interface.recv_matching(arbitration_id=L0_CB_COB.ResponseMessage.RSP_BACKEND_READY,
                                      timeout_s=5.0,)
    assert msg is not None, ("No BackendReady response received within 5s after UiReady. "
                             "Check firmware boot sequence.")
