# test_can_version.py - verify version request/response encoding w/out hardware

from common.can_interface import CanMessage
from common.can_protocol import BoardVersionResponse, L0_HMI_COB, L0_CB_COB, encode_request_version
from common.version import PLATFORM_CB_VERSION

EXPECTED_VERSION = BoardVersionResponse(*PLATFORM_CB_VERSION)


def test_control_board_version(can_interface) -> None:
    """
    Given  an initialized CAN interface
    When   HIL requests the Control Board version
    Then   the response matches PLATFORM_CB_VERSION
    """
    can_interface.flush()

    can_interface.send(encode_request_version())

    reply = can_interface.recv_matching(arbitration_id=L0_CB_COB.RECEIVED_BOARD_VERSION,
                                        timeout_s=2.0,)

    version = BoardVersionResponse.from_can(reply)
    assert version == EXPECTED_VERSION, (f"Expected v{EXPECTED_VERSION}, got v{version}. "
                                         "Update EXPECTED_VERSION or rebuild firmware from the correct commit.")


def test_encode_version_request() -> None:
    """
    Given  a version-request encoder
    When   HIL builds a request frame
    Then   COB-ID and payload match protocol defaults
    """
    msg = encode_request_version()

    assert msg.arbitration_id == L0_HMI_COB.REQUEST_BOARD_VERSION, (f"Wrong COB-ID: expected 0x{L0_HMI_COB.REQUEST_BOARD_VERSION:03X}, "
                                                                    f"got 0x{msg.arbitration_id:03X}")
    assert len(msg.data) == 8, f"Payload must be 8 bytes, got {len(msg.data)}"
    assert msg.data == bytes(8), f"Payload must be all zeros, got {msg.data.hex()}"


def test_decode_version_response() -> None:
    """
    Given  a raw version-response frame
    When   HIL decodes it via BoardVersionResponse.from_can
    Then   major, minor, and patch are parsed correctly
    """
    raw_data = bytearray(8)
    raw_data[0] = 1   # major
    raw_data[1] = 3   # minor
    raw_data[2] = 7   # patch
    raw_msg = CanMessage(arbitration_id=L0_CB_COB.RECEIVED_BOARD_VERSION,
                         data=bytes(raw_data))

    version = BoardVersionResponse.from_can(raw_msg)

    assert version.major == 1, f"major: expected 1, got {version.major}"
    assert version.minor == 3, f"minor: expected 3, got {version.minor}"
    assert version.patch == 7, f"patch: expected 7, got {version.patch}"

