"""
1_can_version_request.py — verify the firmware reports the expected version.

Given   the Control Board is running and connected over CAN FD
When    the HIL sends a version-request RPDO
Then    the Control Board responds with a TPDO containing the expected version
"""

from common.can_protocol import BoardVersionResponse, L0_CB_COB_RECEIVED_BOARD_VERSION, encode_request_version

# Update whenever VersionDetails.md increments the version.
# Current: 0.2 — "Split Vat 2 basket cook" (2025-05-02)
EXPECTED_VERSION = BoardVersionResponse(major=0, minor=2, patch=0)


def test_control_board_version(can_interface) -> None:
    # Step 1: request version from Control Board
    can_interface.send(encode_request_version())

    # Step 2: wait for the version response TPDO
    reply = can_interface.recv_matching(L0_CB_COB_RECEIVED_BOARD_VERSION,
                                    2.0,)

    # Step 3: decode and assert
    version = BoardVersionResponse.from_can(reply)
    assert version == EXPECTED_VERSION, (f"Expected v{EXPECTED_VERSION}, got v{version}. "
                                         "Update EXPECTED_VERSION or rebuild firmware from the correct commit.")
