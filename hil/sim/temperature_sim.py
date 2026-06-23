# @file    temperature_sim.py
# @brief   Per-zone oil temperature simulator using MCP4922 SPI DAC.
# @details Converts temperature values to 12-bit DAC counts and sends
#          them over SPI to the MCP4922. Supports per-zone calibration
#          correction, ramp control, and multi-zone commands.

from __future__ import annotations
import logging
from typing import Dict

log = logging.getLogger(__name__)

try:
    import spidev
    _SPIDEV_AVAILABLE = True
except ImportError:
    _SPIDEV_AVAILABLE = False

VREF_V = 3.3
TEMP_AT_ZERO_V_F = 0.0
TEMP_AT_FULL_SCALE_F = 500.0

try:
    from hil.sim.calibration import ZONE_CALIBRATION
except ImportError:
    ZONE_CALIBRATION: Dict[int, tuple[float, float]] = {}
    log.warning("hil.sim.calibration not found; using default temperature calibration")


def _temp_f_to_dac_counts(temp_f: float) -> int:
    fraction = (temp_f - TEMP_AT_ZERO_V_F) / (TEMP_AT_FULL_SCALE_F - TEMP_AT_ZERO_V_F)
    counts = int(fraction * 4095)
    return max(0, min(4095, counts))


def _build_mcp4922_command(channel_b: bool, counts: int) -> list[int]:
    word = 0
    if channel_b:
        word |= (1 << 15)
    word |= (1 << 13)   # gain = 1x
    word |= (1 << 12)   # active (not shutdown)
    word |= (counts & 0x0FFF)
    return [(word >> 8) & 0xFF, word & 0xFF]


class ZoneConfig:
    def __init__(self, spi_cs: int, channel_b: bool):
        self.spi_cs = spi_cs
        self.channel_b = channel_b


# Zone layout — update to match HIL controller wiring after Step 3.10 calibration
ZONE_CONFIG: Dict[int, ZoneConfig] = {
    0: ZoneConfig(spi_cs=0, channel_b=False),
    1: ZoneConfig(spi_cs=0, channel_b=True),
    2: ZoneConfig(spi_cs=1, channel_b=False),
    3: ZoneConfig(spi_cs=1, channel_b=True),
}


class SpiDacTemperatureSim:
    """
    Controls per-zone oil temperature simulation via MCP4922 SPI DAC(s).
    Requires RPi with SPI enabled and spidev installed.
    """

    def __init__(self, spi_bus: int = 0, spi_hz: int = 1_000_000):
        # Check if spidev is available
        if not _SPIDEV_AVAILABLE:
            raise RuntimeError("spidev not installed. Run: pip install spidev")
        self._spi = spidev.SpiDev()
        self._spi_bus = spi_bus
        self._spi_hz = spi_hz
        self._current_temps: Dict[int, float] = {}
        self._spi.open(self._spi_bus, 0)
        self._spi.max_speed_hz = self._spi_hz

        # Set SPI mode MCP4922: CPOL=0, CPHA=0
        self._spi.mode = 0b00

    def set_temperature(self, zone: int, temp_f: float) -> None:
        if zone not in ZONE_CONFIG:
            raise ValueError(f"Unknown zone {zone}. Valid zones: {list(ZONE_CONFIG.keys())}")
        offset, scale = ZONE_CALIBRATION.get(zone, (0.0, 1.0))
        corrected_f = (temp_f - offset) / scale
        cfg = ZONE_CONFIG[zone]
        counts = _temp_f_to_dac_counts(corrected_f)
        cmd = _build_mcp4922_command(cfg.channel_b, counts)
        self._spi.open(self._spi_bus, cfg.spi_cs)
        self._spi.xfer2(cmd)
        self._current_temps[zone] = temp_f
        log.debug(f"Zone {zone}: {temp_f:.1f}°F (corrected {corrected_f:.1f}°F) → DAC counts {counts}")

    def set_all_zones(self, temp_f: float) -> None:
        for zone in ZONE_CONFIG:
            self.set_temperature(zone, temp_f)

    def get_current_temperature(self, zone: int) -> float:
        return self._current_temps.get(zone, 0.0)

    def ramp_to(self, zone: int, target_f: float, rate_f_per_s: float = 2.0,
                step_interval_s: float = 0.5) -> None:
        import time
        current = self.get_current_temperature(zone)
        step_f = rate_f_per_s * step_interval_s
        if current < target_f:
            while current < target_f:
                current = min(current + step_f, target_f)
                self.set_temperature(zone, current)
                time.sleep(step_interval_s)
        else:
            while current > target_f:
                current = max(current - step_f, target_f)
                self.set_temperature(zone, current)
                time.sleep(step_interval_s)

    def close(self) -> None:
        try:
            self._spi.close()
        except Exception:
            pass
