# @file    test_can_prereq.py
# @brief   Preflight HIL checks that must pass before the main test suite.
# @details Verifies the Control Board reaches NMT OPERATIONAL state and
#          responds with the expected firmware version over CAN FD.

import pytest

from common.can_protocol import BoardVersionResponse, L0_CB_COB, encode_request_version
from common.version import PLATFORM_CB_VERSION

CB_HEARTBEAT_COB_ID = 0x701
CB_NMT_OPERATIONAL = 0x05
BOOT_TIMEOUT_S = 15.0

EXPECTED_VERSION = BoardVersionResponse(*PLATFORM_CB_VERSION)


@pytest.mark.timeout(20)
def test_can_boot_enters_operational(can_interface):
    """
    Given  the Control Board is freshly reset
    When   HIL waits up to 15 s
    Then   an NMT heartbeat in OPERATIONAL state (0x05) is received
    """
    msg = can_interface.recv_matching(arbitration_id=CB_HEARTBEAT_COB_ID,
                                      timeout_s=BOOT_TIMEOUT_S,)
    assert msg is not None, (f"No NMT heartbeat received within {BOOT_TIMEOUT_S}s. "
                             "Check: 24 VAC supply on? CAN wired correctly? Firmware flashed?")
    nmt_state = msg.data[0] if msg.data else 0xFF
    assert nmt_state == CB_NMT_OPERATIONAL, (f"Board heartbeat received but NMT state = 0x{nmt_state:02X}, expected 0x05 (OPERATIONAL). "
                                             "Board may be in PRE-OPERATIONAL or STOPPED state.")


@pytest.mark.timeout(10)
def test_control_board_version(can_interface) -> None:
    """
    Given  the Control Board is running and reachable over CAN FD
    When   the HIL sends a version-request RPDO
    Then   the Control Board responds with a TPDO containing the expected version
    """
    can_interface.send(encode_request_version())

    reply = can_interface.recv_matching(arbitration_id=L0_CB_COB.ResponseMessage.RSP_BOARD_VERSION,
                                        timeout_s=2.0,)

    version = BoardVersionResponse.from_can(reply)
    assert version == EXPECTED_VERSION, (f"Expected v{EXPECTED_VERSION}, got v{version}. "
                                         "Update EXPECTED_VERSION or rebuild firmware from the correct commit.")