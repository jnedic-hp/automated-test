#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p results
python3 -m pytest offtarget/ -v --junitxml=results/offtarget-results.xml --html=results/offtarget-report.html --self-contained-html --css=assets/report.css "$@"
