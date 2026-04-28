#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"
source .venv/bin/activate
SPADE_GUI=true DEMO_CASE=success python main.py

