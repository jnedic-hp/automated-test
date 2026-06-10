"""
test_version.py — verify version request/response encoding without hardware.

Given   a CanMock scripted to return firmware version 0.2.0
When    the HIL sends a version-request RPDO
Then    the decoded response matches the expected version constant
"""

from common.can_interface import CanMessage
from common.can_protocol import BoardVersionResponse, L0_HMI_COB_REQUEST_BOARD_VERSION, L0_CB_COB_RECEIVED_BOARD_VERSION, encode_request_version

# Update whenever VersionDetails.md increments the version.
# Current: 0.2 — "Split Vat 2 basket cook" (2025-05-02)
EXPECTED_VERSION = BoardVersionResponse(major=0, minor=2, patch=0)


def test_control_board_version(can_interface) -> None:
    can_interface.flush()

    # Step 1: request version from Control Board
    can_interface.send(encode_request_version())

    # Step 2: wait for the version response TPDO
    reply = can_interface.recv_matching(arbitration_id=L0_CB_COB_RECEIVED_BOARD_VERSION,
                                    timeout_s=2.0,)

    # Step 3: decode and assert
    version = BoardVersionResponse.from_can(reply)
    assert version == EXPECTED_VERSION, (f"Expected v{EXPECTED_VERSION}, got v{version}. "
                                         "Update EXPECTED_VERSION or rebuild firmware from the correct commit.")


def test_encode_version_request() -> None:
    # Given / When
    msg = encode_request_version()

    # Then
    assert msg.arbitration_id == L0_HMI_COB_REQUEST_BOARD_VERSION, (f"Wrong COB-ID: expected 0x{L0_HMI_COB_REQUEST_BOARD_VERSION:03X}, "
                                                                f"got 0x{msg.arbitration_id:03X}")
    assert len(msg.data) == 8, f"Payload must be 8 bytes, got {len(msg.data)}"
    assert msg.data == bytes(8), f"Payload must be all zeros, got {msg.data.hex()}"


def test_decode_version_response() -> None:
    # Given: a raw frame as the firmware would send it (major/minor/patch at bytes 0/1/2)
    raw_data = bytearray(8)
    raw_data[0] = 1   # major
    raw_data[1] = 3   # minor
    raw_data[2] = 7   # patch
    raw_msg = CanMessage(arbitration_id=L0_CB_COB_RECEIVED_BOARD_VERSION, data=bytes(raw_data))

    # When
    version = BoardVersionResponse.from_can(raw_msg)

    # Then
    assert version.major == 1, f"major: expected 1, got {version.major}"
    assert version.minor == 3, f"minor: expected 3, got {version.minor}"
    assert version.patch == 7, f"patch: expected 7, got {version.patch}"

