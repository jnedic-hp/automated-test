#!/usr/bin/env bash
# flash_firmware_nucleo.sh — flash firmware to the Nucleo-G071RB board
#                            via OpenOCD + on-board STLINK.
#
# Usage:
#   ./scripts/flash_firmware_nucleo.sh <path/to/firmware.elf>
#
# Run from the repo root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path/to/firmware.elf>"
    exit 1
fi

echo "Flashing Nucleo-G071RB — $1 ..."
python3 -m hil.flasher_nucleo "$1"
