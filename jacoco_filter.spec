from pathlib import Path
import os
import sys
import lxml

block_cipher = None

# Detect platform
platform = sys.platform
output_name = "jacoco-filter"

if platform.startswith("win"):
    lxml_files = ["etree.pyd", "objectify.pyd"]
elif platform.startswith("darwin"):
    lxml_files = ["etree.cpython-312-darwin.so", "objectify.cpython-312-darwin.so"]
else:
    # Linux
    lxml_files = ["etree.cpython-312-x86_64-linux-gnu.so", "objectify.cpython-312-x86_64-linux-gnu.so"]

# Locate lxml module path dynamically
lxml_path = Path(lxml.__file__).parent
lxml_binaries = [(str(lxml_path / f), "lxml") for f in lxml_files]

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
