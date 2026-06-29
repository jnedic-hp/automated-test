#!/usr/bin/env bash
# flash_firmware.sh — flash CM7 + CM4 firmware to the Platform Control Board
#                     (STM32H745BITx) via OpenOCD + STLINK-V3SET.
#
# Usage:
#   ./scripts/flash_firmware.sh <path/to/cm7.elf> <path/to/cm4.elf>
#
# Run from the repo root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ $# -ne 2 ]; then
    echo "Usage: $0 <cm7.elf> <cm4.elf>"
    exit 1
fi

echo "Flashing Platform Control Board — CM7=$1  CM4=$2 ..."
python3 -m hil.flasher "$1" "$2"
