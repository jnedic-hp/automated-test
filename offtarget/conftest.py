# @file    conftest.py
# @brief   pytest fixtures for the off-target test suite.
# @details Provides a session-scoped CanMock instance. No hardware required.

import pytest

from offtarget.can_mock import CanMock


@pytest.fixture(scope="session")
def can_interface():
    # Provides CanMock for the test session. No hardware required.
    iface = CanMock()
    yield iface
    iface.close()
