from __future__ import annotations
import logging
from typing import Dict, Tuple

log = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    _GPIO_AVAILABLE = True
except ImportError:
    _GPIO_AVAILABLE = False

# GPIO signal mapping (BCM numbering).
class GPIO_SIGNALS:
    # (name, bcm_pin, direction)
    FILL_VALVE_LEFT_FEEDBACK  = ("FILL_VALVE_LEFT_FEEDBACK",  4, 0)       # B_SW_1 from Platform Control Board
    FILL_VALVE_RIGHT_FEEDBACK = ("FILL_VALVE_RIGHT_FEEDBACK", 5, 0)       # B_SW_2 from Platform Control Board
    AUX_SIGNAL_1              = ("AUX_SIGNAL_1",              6, 0)       # B_SW_3 from Platform Control Board

    ALL: Tuple[Tuple[str, int, int], ...] = (
        FILL_VALVE_LEFT_FEEDBACK,
        FILL_VALVE_RIGHT_FEEDBACK,
        AUX_SIGNAL_1,
    )

# Derived lookup maps.
SIGNAL_PINS: Dict[str, int] = {
    name: bcm_pin for name, bcm_pin, _ in GPIO_SIGNALS.ALL
}

SIGNAL_DIRECTIONS: Dict[str, int] = {
    name: direction for name, _, direction in GPIO_SIGNALS.ALL
}


class RpiGpioSim:
    """
    Drives and reads discrete GPIO signals on the HIL controller.
    Requires RPi with RPi.GPIO installed.
    """

    def __init__(self):
        # Fail fast if GPIO lib is missing.
        if not _GPIO_AVAILABLE:
            raise RuntimeError("RPi.GPIO not installed. Run: pip install RPi.GPIO")

        # Use BCM numbering.
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Configure pins from mapping.
        for signal, pin in SIGNAL_PINS.items():
            direction = SIGNAL_DIRECTIONS.get(signal, GPIO.OUT)
            if direction == GPIO.OUT:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        log.info(f"GPIO initialised: {list(SIGNAL_PINS.keys())}")

    def set_gpio(self, signal: str, value: bool) -> None:
        # Set one signal HIGH/LOW.
        if signal not in SIGNAL_PINS:
            raise ValueError(f"Unknown signal '{signal}'. Known: {list(SIGNAL_PINS.keys())}")
        pin = SIGNAL_PINS[signal]
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
        log.debug(f"GPIO {signal} (pin {pin}) = {'HIGH' if value else 'LOW'}")

    def get_gpio(self, signal: str) -> bool:
        # Read one signal level.
        if signal not in SIGNAL_PINS:
            raise ValueError(f"Unknown signal '{signal}'")
        return bool(GPIO.input(SIGNAL_PINS[signal]))

    def _release_all_outputs(self) -> None:
        # Drive all outputs LOW.
        for signal, pin in SIGNAL_PINS.items():
            if SIGNAL_DIRECTIONS.get(signal) == GPIO.OUT:
                GPIO.output(pin, GPIO.LOW)

    def close(self) -> None:
        # Drive outputs LOW and cleanup.
        self._release_all_outputs()
        GPIO.cleanup(list(SIGNAL_PINS.values()))


class PlatformControlBoardGpioSim(RpiGpioSim):
    # Platform-control-board specific GPIO helper methods.

    # Convenience wrappers.
    def set_fill_valve_left_feedback(self, value: bool) -> None:
        self.set_gpio("FILL_VALVE_LEFT_FEEDBACK", value)

    def set_fill_valve_right_feedback(self, value: bool) -> None:
        self.set_gpio("FILL_VALVE_RIGHT_FEEDBACK", value)

    def set_aux_signal_1(self, value: bool) -> None:
        self.set_gpio("AUX_SIGNAL_1", value)

    def release_all(self) -> None:
        self._release_all_outputs()
