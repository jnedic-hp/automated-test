# @file    test_can_periodic_messages.py
# @brief   HIL tests for Control Board periodic CAN FD broadcasts.
# @details Verifies that the 3 periodic TPDOs - IO_STATS, RTC_DATE_TIME,
#          and BOARD_STATUS - are received within the expected interval after
#          the board reaches OPERATIONAL state.  No commands are sent; these
#          tests only listen.

import pytest

from common.can_protocol import L0_CB_COB

# Maximum time allowed to receive a single periodic frame.
# Increase if the firmware broadcast period is longer than 2 s.
PERIODIC_TIMEOUT_S = 2.0


@pytest.mark.timeout(10)
def test_can_periodic_messages_io_stats(can_interface):
    """
    Given  the Control Board is in OPERATIONAL state
    When   the HIL listens on can0
    Then   an IO_STATS frame (COB-ID 0x1800) is received within 2 s
    """
    msg = can_interface.recv_matching(arbitration_id=L0_CB_COB.PeriodicMessage.PRD_IO_STATS,
                                      timeout_s=PERIODIC_TIMEOUT_S,)
    assert msg is not None, (f"No IO_STATS frame (0x{L0_CB_COB.PeriodicMessage.PRD_IO_STATS:04X}) received within {PERIODIC_TIMEOUT_S}s.")
    assert len(msg.data) > 0, "IO_STATS frame has empty payload."


@pytest.mark.timeout(10)
def test_can_periodic_messages_rtc_date_time(can_interface):
    """
    Given  the Control Board is in OPERATIONAL state
    When   the HIL listens on can0
    Then   an RTC_DATE_TIME frame (COB-ID 0x1801) is received within 2 s
    """
    msg = can_interface.recv_matching(arbitration_id=L0_CB_COB.PeriodicMessage.PRD_RTC_DATE_TIME,
                                      timeout_s=PERIODIC_TIMEOUT_S,)
    assert msg is not None, (f"No RTC_DATE_TIME frame (0x{L0_CB_COB.PeriodicMessage.PRD_RTC_DATE_TIME:04X}) received within {PERIODIC_TIMEOUT_S}s.")
    assert len(msg.data) > 0, "RTC_DATE_TIME frame has empty payload."


@pytest.mark.timeout(10)
def test_can_periodic_messages_board_status(can_interface):
    """
    Given  the Control Board is in OPERATIONAL state
    When   the HIL listens on can0
    Then   a BOARD_STATUS frame (COB-ID 0x1802) is received within 2 s
    """
    msg = can_interface.recv_matching(
        arbitration_id=L0_CB_COB.PeriodicMessage.PRD_BOARD_STATUS,
        timeout_s=PERIODIC_TIMEOUT_S,
    )
    assert msg is not None, (
        f"No BOARD_STATUS frame (0x{L0_CB_COB.PeriodicMessage.PRD_BOARD_STATUS:04X}) received within "
        f"{PERIODIC_TIMEOUT_S}s. Check firmware state machine is running."
    )
    assert len(msg.data) > 0, "BOARD_STATUS frame has empty payload."


@pytest.mark.timeout(15)
def test_periodic_messages_all_arrive(can_interface):
    """
    Given  the Control Board is in OPERATIONAL state
    When   the HIL collects frames for up to 5 s
    Then   all three periodic COB-IDs are observed at least once
    """
    import time

    expected = {
        L0_CB_COB.PeriodicMessage.PRD_IO_STATS,
        L0_CB_COB.PeriodicMessage.PRD_RTC_DATE_TIME,
        L0_CB_COB.PeriodicMessage.PRD_BOARD_STATUS,
    }
    seen = set()
    deadline = time.monotonic() + 5.0

    while seen != expected:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        msg = can_interface.recv(timeout_s=remaining)
        if msg is not None and msg.arbitration_id in expected:
            seen.add(msg.arbitration_id)

    missing = expected - seen
    assert not missing, (
        "The following periodic COB-IDs were not observed within 5 s: "
        + ", ".join(f"0x{cob:04X}" for cob in missing)
    )
