from pathlib import Path
import sys
import lxml

block_cipher = None

# Detect platform
platform = sys.platform
output_name = "jacoco-filter"

# Locate lxml module path dynamically
lxml_path = Path(lxml.__file__).parent
lxml_binaries = []

# Search dynamically for etree and objectify binaries
for name in ["etree", "objectify"]:
    matches = list(lxml_path.glob(f"{name}.*"))
    if not matches:
        print(f"Warning: no match found for '{name}.*' in {lxml_path}")
    for match in matches:
        lxml_binaries.append((str(match), "lxml"))

if not lxml_binaries:
    raise RuntimeError("❌ No lxml binary extensions found — cannot package.")

a = Analysis(
    ['run_filter.py'],
    pathex=[],
    binaries=lxml_binaries,
    datas=[],
    hiddenimports=["lxml._elementpath"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=output_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=output_name
)
