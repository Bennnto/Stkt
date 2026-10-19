#!/usr/bin/env bash
set -e

echo "=========================================="
echo "=== Stkt Self-Hosted Compiler Installer ==="
echo "=========================================="

PREFIX="${PREFIX:-$HOME/.local}"
BINDIR="$PREFIX/bin"

mkdir -p "$BINDIR"

if command -v clang >/dev/null 2>&1; then
    CC=clang
elif command -v gcc >/dev/null 2>&1; then
    CC=gcc
elif command -v cc >/dev/null 2>&1; then
    CC=cc
else
    echo "Error: No C compiler found (clang or gcc required)." >&2
    exit 1
fi

echo "===> Compiling native Stkt compiler using $CC..."
$CC -O3 bootstrap/stkt.c -o "$BINDIR/stkt"
codesign -s - -f "$BINDIR/stkt" 2>/dev/null || true

echo "✅ Stkt installed successfully to $BINDIR/stkt"
echo ""
echo "Verify installation with:"
echo "  $BINDIR/stkt"
echo ""
echo "Ensure $BINDIR is in your PATH (e.g., in ~/.zshrc or ~/.bashrc):"
echo "  export PATH=\"$BINDIR:\$PATH\""
