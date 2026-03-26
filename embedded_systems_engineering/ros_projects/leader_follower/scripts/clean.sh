#!/usr/bin/env bash
# ============================================================
# clean.sh — Clean build artifacts
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Cleaning build artifacts ==="
cd "$WS_DIR"

rm -rf build/ install/ log/
echo "Removed: build/ install/ log/"
echo "Done. Run ./scripts/build.sh to rebuild."
