# -*- mode: python ; coding: utf-8 -*-
"""
PMhelper Edu — PyInstaller spec file.
Build with: pyinstaller pmhelper_edu.spec
Or use: .\build_edu.ps1
"""

import os
import sys

block_cipher = None

# Paths — anchored to the repo root. This spec lives in packaging/, and PyInstaller
# resolves spec-relative paths against the spec's directory (SPECPATH), so derive the
# repo root from it rather than relying on the current working directory.
ROOT = os.path.dirname(os.path.abspath(SPECPATH))
SRC_DIR = os.path.join(ROOT, 'src', 'pmhelper')
DEMOS_DIR = os.path.join(SRC_DIR, 'demos_edu')

a = Analysis(
    [os.path.join(SRC_DIR, 'edu_main.py')],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=[],
    datas=[
        (DEMOS_DIR, os.path.join('pmhelper', 'demos_edu')),
        # Z-table used by the PERT/probability features (loader looks for it
        # next to the pmhelper package)
        (os.path.join(SRC_DIR, 'ztable.csv'), 'pmhelper'),
    ],
    hiddenimports=[
        'pmhelper',
        'pmhelper.core',
        'pmhelper.core.evm_models_edu',
        'pmhelper.core.evm_calculations_edu',
        'pmhelper.core.risk_register_edu',
        'pmhelper.core.cpm_sampler_edu',
        'pmhelper.core.monte_carlo_edu',
        'pmhelper.gui',
        'pmhelper.gui.edu_state',
        'pmhelper.gui.main_window_edu',
        'pmhelper.gui.tabs',
        'pmhelper.gui.tabs.input_tab_edu',
        'pmhelper.gui.tabs.gantt_tab_edu',
        'pmhelper.gui.tabs.network_tab_edu',
        'pmhelper.gui.tabs.evm_tab_edu',
        'pmhelper.gui.tabs.risk_tab_edu',
        'pmhelper.gui.tabs.probability_tab_edu',
        'pmhelper.gui.tabs.pert_tab_edu',
        'pmhelper.gui.tabs.crashing_tab_edu',
        'pmhelper.gui.tabs.rcps_tab_edu',
        'pmhelper.gui.tabs.dashboard_tab_edu',
        'pmhelper.utils',
        'pmhelper.utils.evm_io_edu',
        'pmhelper.utils.risk_io_edu',
        'pmhelper.utils.project_io_edu',
        'pmhelper.utils.chart_export_edu',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PMhelper_Edu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # UPX off to reduce AV false positives
    console=False,        # Windowed app (no console)
    icon=None,            # TODO: Add icon in Phase 6
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PMhelper_Edu',
)
