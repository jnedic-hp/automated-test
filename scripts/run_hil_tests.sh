#!/usr/bin/env bash
# run_hil_tests.sh — run the HIL test suite on the Raspberry Pi.
#
# Usage:
#   ./scripts/run_hil_tests.sh              # run all HIL tests
#   ./scripts/run_hil_tests.sh -k version   # run tests matching a keyword
#
# Run from the repo root on the Raspberry Pi.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p results
python -m pytest hil/tests/ -v --junitxml=results/hil-results.xml --html=results/hil-report.html --self-contained-html --css=assets/report.css "$@"
