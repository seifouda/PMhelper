---
name: run-and-debug
description: Use to launch any part of PMHelper (desktop GUI, FastAPI server, Angular web, or a CLI) and to diagnose common startup/runtime errors like import errors, "database locked", or a blank Plotly panel. Reach for this when something won't start or throws a traceback.
---

# Run & debug PMHelper

## First-time setup (once)
```bash
python -m venv .venv && .venv\Scripts\activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .            # installs pmhelper as an editable package
pip install -e .[dev]       # adds pytest, coverage, etc.
```
Editable install means `import pmhelper` works from anywhere — you should **not**
need `sys.path` hacks.

## Launch each surface
| What | Command | Notes |
|---|---|---|
| Edu desktop app | `python -m pmhelper.edu_main` | the main educational GUI |
| Legacy desktop app | `python launch_app.py` | older v1 |
| API server | `uvicorn pmhelper.server.main:app --reload` | app defined in `src/pmhelper/server/main.py`; health at `GET /health` |
| Web frontend | `cd web && npm install && npm start` | Angular dev server on `:4200`, talks to the API |
| A CLI | `python -m pmhelper.cli.cpm_cli --input project.csv --output results.json` | also `pert_cli`, `risk_cli`, `selection_cli`, `optimization_cli` |

## How to read a Python error
Read the traceback **bottom-up**: the last line is *what* broke; the lines above
are *where*. The first frame that points at a `src/pmhelper/...` file is usually
the real culprit.

## Common failures and fixes
- **`ModuleNotFoundError: No module named 'pmhelper...'`** → you didn't run
  `pip install -e .`, or the venv isn't activated. Re-run it.
- **`ModuleNotFoundError: pmhelper.core.models`** → that module was removed long
  ago; the importing file is stale/legacy (e.g. some tests in `manual_tests/`).
  Fix the import to the current module or leave the legacy file alone.
- **`database is locked` (server)** → SQLite is tuned for slow disks; increase the
  connection timeout in `src/pmhelper/server/config.py`. Don't run two servers on
  the same `data/*.db`.
- **Blank/!broken Plotly panel in the Edu app** → the app pre-initializes COM STA
  (`ensure_com_sta` in `edu_main.py`) for the embedded WebView2 renderer; launch
  via `python -m pmhelper.edu_main`, not by importing a tab directly.
- **CLI shows boxes instead of ✓/⚠ on Windows** → expected; the CLIs use ASCII
  markers `[OK]`/`[!]`/`[!!]` on Windows consoles.
- **`pmhelper` console command errors** → `pyproject.toml` has a known typo
  (`cmp_cli` should be `cpm_cli`); use `python -m pmhelper.cli.cpm_cli` instead.

## Debugging technique
Add a temporary `print(...)` or use `python -m pdb yourscript.py` (`n` next,
`s` step in, `p var` print, `c` continue). Remove prints before committing — in
production mode `launch_app.py` filters `[DEBUG_*]`-prefixed prints.

## Related skills
[[run-tests]] to confirm a fix. [[understand-this-codebase]] for the layout.
