#!/bin/bash
# build.sh

set -e

# Ensure we're in the project root
cd "$(dirname "$0")"

echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "🔨 Building jacoco-filter using PyInstaller..."
pyinstaller jacoco_filter.spec

echo "✅ Done. Binary located at: dist/jacoco-filter"
