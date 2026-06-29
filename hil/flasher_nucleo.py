# @file    flasher_nucleo.py
# @brief   Firmware flashing utility for the Nucleo-G071RB board via OpenOCD.
# @details Uses OpenOCD with an on-board STLINK to program and reset the
#          STM32G071RB over SWD. For the Platform Control Board see flasher.py.

from __future__ import annotations
import subprocess
import time
import logging
from pathlib import Path

log = logging.getLogger(__name__)

NUCLEO_CFG = Path(__file__).parent.parent / "boards" / "cfg" / "nucleo-g071rb.cfg"

FLASH_TIMEOUT_S = 60


class NucleoFlasher:
    """Flash and control the Nucleo-G071RB (STM32G071RB, single-core)."""

    def __init__(self):
        if not NUCLEO_CFG.exists():
            raise FileNotFoundError(f"OpenOCD config not found: {NUCLEO_CFG}")

    def flash(self, elf_path: Path) -> None:
        """Program and verify the ELF, then reset the target.

        Args:
            elf_path: ELF to flash.
        """
        elf = Path(elf_path)
        if not elf.exists():
            raise FileNotFoundError(f"ELF not found: {elf}")

        log.info(f"Flashing Nucleo — {elf.name}")
        t0 = time.monotonic()

        result = self._run_openocd(f"program {elf} verify reset exit")

        elapsed = time.monotonic() - t0
        log.info(f"Flash completed in {elapsed:.1f}s (exit code {result.returncode})")
        self._check_result(result, label=elf.name)

    def reset(self) -> None:
        """Hardware reset via SWD SRST."""
        log.info("Resetting Nucleo via SRST...")
        result = self._run_openocd("init; reset run; shutdown", timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"Reset failed (exit {result.returncode}).\nstderr: {result.stderr}")

    def halt(self) -> None:
        """Halt the CPU — used for post-test memory inspection if needed."""
        self._run_openocd("init; halt; shutdown", timeout=10)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_openocd(self, cmds: str, timeout: int = FLASH_TIMEOUT_S) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["openocd", "-f", str(NUCLEO_CFG), "-c", cmds],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def _check_result(self, result: subprocess.CompletedProcess, label: str) -> None:
        print(result.stderr)  # show raw OpenOCD output

        if result.returncode != 0:
            stderr = result.stderr
            if "Error: open failed" in stderr or "LIBUSB_ERROR" in stderr:
                raise RuntimeError(
                    f"STLINK not found or not connected.\n"
                    f"Run: lsusb | grep STMicro\n"
                    f"OpenOCD stderr:\n{stderr}"
                )
            if "Warn : target not halted" in stderr:
                raise RuntimeError(
                    f"Target did not halt after flash — possible hardware issue.\n"
                    f"OpenOCD stderr:\n{stderr}"
                )
            raise RuntimeError(
                f"{label} flash failed (exit {result.returncode}).\n"
                f"OpenOCD stderr:\n{stderr}"
            )

        if "Verified OK" not in result.stdout and "Verified OK" not in result.stderr:
            raise RuntimeError(
                f"'Verified OK' not found for {label} — flash may be corrupt.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        description="Flash firmware to the Nucleo-G071RB via OpenOCD."
    )
    parser.add_argument("elf", type=Path, help="Firmware ELF")
    args = parser.parse_args()

    NucleoFlasher().flash(args.elf)
