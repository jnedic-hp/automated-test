from __future__ import annotations
import subprocess
import time
import logging
from pathlib import Path

log = logging.getLogger(__name__)

OPENOCD_CFG = Path(__file__).parent.parent / "boards" / "cfg" / "nucleo-g071rb.cfg"
FLASH_TIMEOUT_S = 60   # abort if flash takes longer than this


class OpenOCDFlasher:
    """
    Flashes and resets the DUT via STLINK-V3SET using OpenOCD.
    Implements IFlasher.
    """

    def __init__(self, cfg: Path = OPENOCD_CFG):
        self._cfg = Path(cfg)
        if not self._cfg.exists():
            raise FileNotFoundError(f"OpenOCD config not found: {self._cfg}")

    def flash(self, elf_path: Path) -> None:
        elf = Path(elf_path)
        if not elf.exists():
            raise FileNotFoundError(f"ELF not found: {elf}")

        log.info(f"Flashing {elf.name} via OpenOCD...")
        t0 = time.monotonic()

        result = subprocess.run(
            [
                "openocd",
                "-f", str(self._cfg),
                "-c", f"program {elf} verify reset exit",
            ],
            capture_output=True,
            text=True,
            timeout=FLASH_TIMEOUT_S,
        )

        elapsed = time.monotonic() - t0
        log.info(f"Flash completed in {elapsed:.1f}s (exit code {result.returncode})")
        print(result.stderr)  # show raw OpenOCD output

        if result.returncode != 0:
            stderr = result.stderr
            if "Error: open failed" in stderr or "LIBUSB_ERROR" in stderr:
                raise RuntimeError(
                    f"STLINK-V3SET not found or not connected.\n"
                    f"Run: lsusb | grep STMicro\n"
                    f"OpenOCD stderr:\n{stderr}"
                )
            if "Warn : target not halted" in stderr:
                raise RuntimeError(
                    f"Target did not halt after flash — possible hardware issue.\n"
                    f"OpenOCD stderr:\n{stderr}"
                )
            raise RuntimeError(
                f"Flash failed (exit {result.returncode}).\n"
                f"OpenOCD stderr:\n{stderr}"
            )

        if "Verified OK" not in result.stdout and "Verified OK" not in result.stderr:
            raise RuntimeError(
                f"OpenOCD completed but 'Verified OK' not found — flash may be corrupt.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

    def reset(self) -> None:
        """Hardware reset via SWD SRST — board starts executing from reset vector."""
        log.info("Resetting DUT via SRST...")
        result = subprocess.run(
            [
                "openocd",
                "-f", str(self._cfg),
                "-c", "init; reset run; shutdown",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Reset failed (exit {result.returncode}).\n"
                f"stderr: {result.stderr}"
            )

    def halt(self) -> None:
        """Halt the CPU — used for post-test memory inspection if needed."""
        subprocess.run(
            ["openocd", "-f", str(self._cfg), "-c", "init; halt; shutdown"],
            capture_output=True, timeout=10, check=True,
        )


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if len(sys.argv) != 2:
        print("Usage: python3 -m hil.flasher <path/to/firmware.elf>")
        sys.exit(1)
    elf = Path(sys.argv[1])
    flasher = OpenOCDFlasher()
    flasher.flash(elf)
    print("Flash OK")
    flasher.reset()
    print("Reset OK")
