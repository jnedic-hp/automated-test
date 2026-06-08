import pytest

from offtarget.mocks.can_mock import CanMock


@pytest.fixture(scope="session")
def can_interface():
    """Provides CanMock for the test session. No hardware required."""
    iface = CanMock()
    yield iface
    iface.close()
