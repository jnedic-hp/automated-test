#!/usr/bin/env bash
# run_offtarget_tests.sh — run the off-target test suite. No hardware required.
#
# Usage:
#   ./scripts/run_offtarget_tests.sh              # run all off-target tests
#   ./scripts/run_offtarget_tests.sh -k version   # run tests matching a keyword
#
# Run from the repo root on any machine.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p results
python -m pytest offtarget/tests/ -v --junitxml=results/offtarget-results.xml --html=results/offtarget-report.html --self-contained-html --css=assets/report.css "$@"
