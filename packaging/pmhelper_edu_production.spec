# -*- mode: python ; coding: utf-8 -*-
"""
PMhelper Edu — Production PyInstaller Spec File
================================================
Build with:  pyinstaller pmhelper_edu_production.spec --noconfirm
Or use:      .\\build_production.ps1

AV-Resistance Features:
  1. Embedded Windows manifest (asInvoker, DPI-aware, OS compatibility)
  2. Embedded version info (ProductName, CompanyName in file properties)
  3. UPX disabled (packed binaries trigger heuristic AV scanners)
  4. --onedir mode (directory bundles get far fewer AV flags than --onefile)
  5. No cipher/encryption on bytecode (encrypted payloads look malicious)
  6. Icon resource embedded (legitimate apps have icons)
  7. Console disabled (windowed app = no suspicious console pop-up)
"""

import os
import sys

block_cipher = None  # No bytecode encryption — encrypted .pyc triggers AV heuristics

# ─── Paths ───────────────────────────────────────────────────────────────────
# Anchored to the repo root. This spec lives in packaging/, and PyInstaller resolves
# spec-relative paths against the spec's directory (SPECPATH), so derive the repo root
# from it rather than relying on the current working directory.
ROOT = os.path.dirname(os.path.abspath(SPECPATH))
SRC_DIR = os.path.join(ROOT, 'src', 'pmhelper')
DEMOS_DIR = os.path.join(SRC_DIR, 'demos_edu')
ASSETS_DIR = os.path.join(ROOT, 'assets')

# Icon: use generated .ico if it exists, else None (build script creates it)
ICON_PATH = os.path.join(ASSETS_DIR, 'pmhelper_edu.ico')
if not os.path.isfile(ICON_PATH):
    ICON_PATH = None

# Manifest: embedded into .exe for Windows compatibility + DPI + no-elevation.
# This spec lives in packaging/; SPECPATH is its directory, so find sibling build
# inputs there regardless of the current working directory.
MANIFEST_PATH = os.path.join(SPECPATH, 'pmhelper_edu.manifest')
if not os.path.isfile(MANIFEST_PATH):
    MANIFEST_PATH = None

# Version info: embeds metadata into .exe Properties -> Details tab
VERSION_FILE = os.path.join(SPECPATH, 'version_info.rc')
if not os.path.isfile(VERSION_FILE):
    VERSION_FILE = None

# ---- Collect all scipy submodules (fixes scipy.stats runtime codegen) ----
from PyInstaller.utils.hooks import collect_all
scipy_datas, scipy_binaries, scipy_hiddenimports = collect_all('scipy')

# ---- Data files to bundle ----
datas_list = [
    (DEMOS_DIR, os.path.join('pmhelper', 'demos_edu')),
    # Z-table used by the PERT/probability features (loader looks for it next to
    # the pmhelper package)
    (os.path.join(SRC_DIR, 'ztable.csv'), 'pmhelper'),
]
datas_list.extend(scipy_datas)
# Bundle assets directory (CSV examples, templates) if it exists
if os.path.isdir(ASSETS_DIR):
    datas_list.append((ASSETS_DIR, 'assets'))

# ─── Analysis ────────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(SRC_DIR, 'edu_main.py')],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=scipy_binaries,
    datas=datas_list,
    hiddenimports=[
        # -- pmhelper package --
        'pmhelper',
        'pmhelper.core',
        'pmhelper.core.evm_models_edu',
        'pmhelper.core.evm_calculations_edu',
        'pmhelper.core.risk_register_edu',
        'pmhelper.core.cpm_sampler_edu',
        'pmhelper.core.monte_carlo_edu',
        'pmhelper.core.swot_models_edu',
        'pmhelper.core.pestel_models_edu',
        'pmhelper.core.wbs_models_edu',
        'pmhelper.core.wbs_validator_edu',
        'pmhelper.core.step_generators_edu',
        'pmhelper.core.cpm_analyzer',
        'pmhelper.core.pert_analyzer',
        'pmhelper.core.network_builder',
        'pmhelper.core.rcps_analyzer',
        'pmhelper.core.risk_analysis',
        'pmhelper.core.resource_leveling',

        # ── GUI ──
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
        'pmhelper.gui.tabs.swot_tab_edu',
        'pmhelper.gui.tabs.pestel_tab_edu',
        'pmhelper.gui.tabs.wbs_tab_edu',

        # ── Utilities ──
        'pmhelper.utils',
        'pmhelper.utils.evm_io_edu',
        'pmhelper.utils.risk_io_edu',
        'pmhelper.utils.project_io_edu',
        'pmhelper.utils.chart_export_edu',
        'pmhelper.utils.app_config_edu',
        'pmhelper.utils.swot_extractor_edu',
        'pmhelper.utils.wbs_builder_edu',
        'pmhelper.utils.wbs_export_edu',
        'pmhelper.utils.wbs_layout_edu',
        'pmhelper.utils.interactive_network',
        'pmhelper.utils.network_layout',

        # ── Third-party deps (ensure PyInstaller finds them) ──
        'numpy',
        'pandas',
        'scipy',
        'scipy.optimize',
        'scipy.stats',        'scipy.stats._distn_infrastructure',
        'scipy.stats.distributions',
        'scipy.stats._stats_py',
        'scipy.stats._continuous_distns',
        'scipy.stats._discrete_distns',
        'scipy.special',
        'scipy.special._cdflib',
        'scipy._lib',
        'scipy._lib.array_api_compat',
        'scipy._lib.array_api_compat.numpy',        'networkx',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'openpyxl',
        'tabulate',
        'tksheet',
        'pyvis',
        'pyvis.network',

        # ── Tkinter submodules (sometimes missed on some Python builds) ──
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
    ] + scipy_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary heavy modules to slim the bundle
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'docutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ─── PYZ (compiled Python archive) ───────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ─── EXE ─────────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # --onedir: binaries go in COLLECT, not the .exe
    name='PMhelper_Edu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,             # Don't strip — stripped binaries look suspicious to AV
    upx=False,               # AV FIX: UPX packing triggers heuristic scanners
    console=False,           # Windowed app — no suspicious console pop-up
    disable_windowed_traceback=False,
    icon=ICON_PATH,          # Embedded icon (None if not yet generated)
    manifest=MANIFEST_PATH,  # AV FIX: Embedded manifest = legitimate Windows app
    version=VERSION_FILE,    # AV FIX: Version info in Properties → Details
)

# ─── COLLECT (onedir bundle) ─────────────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,               # AV FIX: No UPX on bundled DLLs either
    upx_exclude=[],
    name='PMhelper_Edu',
)
