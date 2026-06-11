#!/usr/bin/env bash
# flash_firmware.sh — flash a firmware ELF to the connected board via OpenOCD.
#
# Usage:
#   ./scripts/flash_firmware.sh <path/to/firmware.elf>
#
# Run from the repo root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path/to/firmware.elf>"
    exit 1
fi

ELF="$1"

if [ ! -f "$ELF" ]; then
    echo "Error: ELF file not found: $ELF"
    exit 1
fi

echo "Flashing $ELF ..."
python3 -m hil.flasher "$ELF"
