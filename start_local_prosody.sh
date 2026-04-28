#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$SCRIPT_DIR/xmpp/data" "$SCRIPT_DIR/xmpp/logs"

export PATH="/opt/homebrew/opt/lua@5.4/bin:/opt/homebrew/bin:$PATH"

exec prosody -F --config "$SCRIPT_DIR/xmpp/prosody.cfg.lua"

