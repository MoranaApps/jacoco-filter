#!/usr/bin/env bash
set -e

PLATFORM="${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
echo "🛠 Building for: $PLATFORM"

pyinstaller --clean jacoco_filter.spec

echo "✅ Output placed in ./dist/jacoco-filter/"
