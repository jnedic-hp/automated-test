# test_can_version_request.py - verify the firmware reports the expected version.

from common.can_protocol import BoardVersionResponse, L0_CB_COB_RECEIVED_BOARD_VERSION, encode_request_version

# Update whenever VersionDetails.md increments the version.
# Current: 0.2 — "Split Vat 2 basket cook" (2025-05-02)
EXPECTED_VERSION = BoardVersionResponse(major=0, minor=2, patch=0)


def test_control_board_version(can_interface) -> None:
    """
    Given  the Control Board is running and reachable over CAN FD
    When   the HIL sends a version-request RPDO
    Then   the Control Board responds with a TPDO containing the expected version
    """
    can_interface.send(encode_request_version())

    reply = can_interface.recv_matching(arbitration_id=L0_CB_COB_RECEIVED_BOARD_VERSION,
                                        timeout_s=2.0,)

    version = BoardVersionResponse.from_can(reply)
    assert version == EXPECTED_VERSION, (f"Expected v{EXPECTED_VERSION}, got v{version}. "
                                         "Update EXPECTED_VERSION or rebuild firmware from the correct commit.")
