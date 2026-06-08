import pytest

from common.can_interface import SocketCanInterface


@pytest.fixture(scope="session")
def can_interface():
    """Provides a SocketCanInterface on can0 for the test session."""
    channel = "can0"
    iface = SocketCanInterface(channel=channel)
    try:
        iface.open()
    except OSError as exc:
        pytest.exit(
            f"\n\n  HIL setup failed — SocketCAN device '{channel}' not found.\n"
            f"  Bring up the interface before running HIL tests:\n\n"
            f"    sudo ip link set {channel} up type can bitrate 500000 dbitrate 2000000 fd on\n\n"
            f"  (original error: {exc})\n",
            returncode=3,
        )
    yield iface
    iface.close()


@pytest.fixture(autouse=True)
def flush_can(can_interface):
    """Discard stale frames before every test."""
    can_interface.flush()
