# @file    calibration.py
# @brief   Per-zone calibration values for temperature simulation.
# @details Applies per-zone linear correction so requested temperatures
#          map more accurately through the analog path. Each tuple is (offset_f, scale).
#          Use defaults (0.0, 1.0) when no calibration data is available.

from __future__ import annotations

from typing import Dict, Tuple

# Global transfer constants for temperature-to-DAC conversion.
VREF_V = 3.3
TEMP_AT_ZERO_V_F = 0.0
TEMP_AT_FULL_SCALE_F = 500.0

# Zone -> (offset_f, scale)
ZONE_CALIBRATION: Dict[int, Tuple[float, float]] = {
    0: (0.0, 1.0),
    1: (0.0, 1.0),
    2: (0.0, 1.0),
    3: (0.0, 1.0),
}
