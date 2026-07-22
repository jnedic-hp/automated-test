# @file    flasher.py
# @brief   Firmware flashing utility for the Platform Control Board (STM32H745BITx).
# @details Flashes CM7 and CM4 cores in a single OpenOCD session via STLINK-V3SET
#          over SWD. For the Nucleo board see flasher_nucleo.py.

from __future__ import annotations
import shutil
import subprocess
import tempfile
import threading
import time
import logging
from pathlib import Path

log = logging.getLogger(__name__)

PLATFORM_CB_CFG = Path(__file__).parent.parent / "boards" / "cfg" / "platform-control-board.cfg"

# OpenOCD target names produced by stm32h7x.cfg when DUAL_CORE=1.
# Derived from CHIPNAME in platform-control-board.cfg.
_CM7_TARGET = "STM32H745BITx.cpu0"
_CM4_TARGET = "STM32H745BITx.cpu1"

FLASH_TIMEOUT_S = 420


class PlatformCBFlasher:
    """Flash and control the Platform Control Board (STM32H745 CM7 + CM4)."""

    def __init__(self):
        if not PLATFORM_CB_CFG.exists():
            raise FileNotFoundError(f"OpenOCD config not found: {PLATFORM_CB_CFG}")

    def flash(self, cm7_elf: Path, cm4_elf: Path) -> None:
        """Program CM7 then CM4 in one OpenOCD session, then reset both cores.

        Args:
            cm7_elf: ELF built for the Cortex-M7 core.
            cm4_elf: ELF built for the Cortex-M4 core.
        """
        cm7 = Path(cm7_elf)
        cm4 = Path(cm4_elf)
        if not cm7.exists():
            raise FileNotFoundError(f"CM7 ELF not found: {cm7}")
        if not cm4.exists():
            raise FileNotFoundError(f"CM4 ELF not found: {cm4}")

        log.info(f"Flashing Platform CB — CM7={cm7.name}, CM4={cm4.name}")
        t0 = time.monotonic()

        with tempfile.TemporaryDirectory() as tmp:
            cm7 = self._strip_elf(cm7, Path(tmp))
            cm4 = self._strip_elf(cm4, Path(tmp))

            # Both ELFs are flashed using CM7 (cpu0) as the algorithm target.
            #
            # CM7 is programmed via its own target (cpu0).
            # CM4 is programmed via its own target (cpu1).
            #
            # Why CM4 must use cpu1 (not cpu1 via CM7 as we tried):
            #   When the stm32h7x algorithm runs on CM7 to erase sector 14
            #   (bank 2, 0x081C0000-0x081DFFFF), CM7 crashes before the write
            #   phase — leaving CM4's sector erased but never written.  Using
            #   CM4's own algorithm target avoids this: CM4's algorithm runs in
            #   CM4's DTCM (0x10000000) and doesn't contend with bank 2.
            #
            # Expected CM7 crash (unavoidable, harmless):
            #   The CM4 flash algorithm briefly resumes CM4 (cpu1), which
            #   accidentally releases CM7 from debug-halt.  CM7 runs, reaches
            #   its CM4-sync code, finds CM4 busy, and double-faults.
            #   HOWEVER, CM4's "** Programming Finished **" appears BEFORE the
            #   crash — the flash content is safe.
            #
            # Recovery via `reset run`:
            #   SRST hardware-resets both cores (clearing CM7's lockup) and
            #   lets them boot freely — exactly like a power cycle.  This only
            #   works once the option byte BOOT_CM4_ADD0 correctly encodes
            #   CM4's vector-table address (set by sd_partition.cmd / firmware
            #   team).  With correct option bytes both cores boot normally and
            #   the LEDs turn on.
            cmds = (
                f"init; reset halt; "
                f"targets {_CM7_TARGET}; program {cm7}; "
                f"targets {_CM4_TARGET}; program {cm4}; "
                f"reset run; "
                f"shutdown"
            )
            result = self._run_openocd(cmds)

        elapsed = time.monotonic() - t0
        log.info(f"Flash completed in {elapsed:.1f}s (exit code {result.returncode})")
        self._check_result(result, label="CM7+CM4")

    def reset(self) -> None:
        """Hardware reset via SWD SRST."""
        log.info("Resetting Platform CB via SRST...")
        result = self._run_openocd("init; reset run; shutdown", timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"Reset failed (exit {result.returncode}).\nstderr: {result.stderr}")

    def halt(self) -> None:
        """Halt CM7 — used for post-test memory inspection if needed."""
        self._run_openocd("init; halt; shutdown", timeout=10)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _strip_elf(self, elf: Path, tmp_dir: Path) -> Path:
        """Return a debug-stripped copy of *elf* in *tmp_dir*.

        Strips DWARF/debug sections so OpenOCD only transfers the loadable
        flash content (can reduce a 30 MB debug ELF to <1 MB).
        Falls back to the original ELF if arm-none-eabi-objcopy is not found.
        """
        objcopy = shutil.which("arm-none-eabi-objcopy")
        if objcopy is None:
            log.warning("arm-none-eabi-objcopy not found — using original ELF (flash may be slow)")
            return elf
        stripped = tmp_dir / elf.name
        subprocess.run([objcopy, "--strip-debug", str(elf), str(stripped)], check=True)
        orig_kb = elf.stat().st_size // 1024
        stripped_kb = stripped.stat().st_size // 1024
        log.info(f"Stripped {elf.name}: {orig_kb} KB → {stripped_kb} KB")
        return stripped

    def _run_openocd(self, cmds: str, timeout: int = FLASH_TIMEOUT_S) -> subprocess.CompletedProcess:
        proc = subprocess.Popen(
            ["openocd", "-f", str(PLATFORM_CB_CFG), "-c", cmds],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout_chunks: list[str] = []
        stderr_lines: list[str] = []

        def _read(stream, collector: list[str], live: bool = False) -> None:
            for line in stream:
                if live:
                    print(line, end="", flush=True)
                collector.append(line)

        t_out = threading.Thread(target=_read, args=(proc.stdout, stdout_chunks, False), daemon=True)
        t_err = threading.Thread(target=_read, args=(proc.stderr, stderr_lines, True), daemon=True)
        t_out.start()
        t_err.start()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise

        t_out.join()
        t_err.join()

        return subprocess.CompletedProcess(
            args=proc.args,
            returncode=proc.returncode,
            stdout="".join(stdout_chunks),
            stderr="".join(stderr_lines),
        )

    def _check_result(self, result: subprocess.CompletedProcess, label: str) -> None:
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
                f"{label} flash failed (exit {result.returncode}).\n"
                f"OpenOCD stderr:\n{stderr}"
            )

        if "** Programming Finished **" not in result.stderr:
            raise RuntimeError(
                f"'** Programming Finished **' not found for {label} — flash may have been skipped.\n"
                f"stderr: {result.stderr}"
            )


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        description="Flash CM7 + CM4 firmware to the Platform Control Board via OpenOCD."
    )
    parser.add_argument("cm7_elf", type=Path, help="CM7 ELF")
    parser.add_argument("cm4_elf", type=Path, help="CM4 ELF")
    args = parser.parse_args()

    PlatformCBFlasher().flash(args.cm7_elf, args.cm4_elf)
