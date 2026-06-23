# test_can_boot.py - verify the Control Board boot sequence over CAN

import pytest
from common.can_protocol import L0_CB_COB, L0_UiReady

@pytest.mark.timeout(20)
def test_can_boot_backend_ready_after_ui(can_interface):
    """
    Given  the Control Board is in OPERATIONAL state
    When   the HIL sends L0_UiReady
    Then   the Control Board responds with L0_BackendReady (COB-ID 0x1829)
    """

    can_interface.send(L0_UiReady().encode())
    msg = can_interface.recv_matching(arbitration_id=L0_CB_COB.BACKEND_READY,
                                      timeout_s=5.0,)
    assert msg is not None, ("No BackendReady response received within 5s after UiReady. "
                             "Check firmware boot sequence.")
