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
| A CLI | `python -m pmhelper.cli.cpm_cli analyze project.csv -o results.json` | also `pert_cli`, `risk_cli`, `selection_cli`, `optimization_cli` |

Each CLI takes a **subcommand** first (`cpm_cli`: `analyze`/`crash`/`sample`;
`pert_cli`: `analyze`/`probability`/`sample`). The input file is **positional**
for these two — there is no `--input` flag. `optimization_cli` is the exception:
it *requires* `--input`. When in doubt run `--help` on the subcommand; don't
guess the flags.

## How to read a Python error
Read the traceback **bottom-up**: the last line is *what* broke; the lines above
are *where*. The first frame that points at a `src/pmhelper/...` file is usually
the real culprit.

## Common failures and fixes
- **`ModuleNotFoundError: No module named 'pmhelper...'`** → you didn't run
  `pip install -e .`, or the venv isn't activated. Re-run it.
- **`database is locked` (server)** → the SQLite connect timeout lives in
  `src/pmhelper/server/database/connection.py` (`connect_args={"timeout": 30}`),
  **not** in `server/config.py`. Don't run two servers on the same `data/*.db`.
- **Blank/!broken Plotly panel in the Edu app** → the app pre-initializes COM STA
  for the embedded WebView2 renderer (`ensure_com_sta`, defined in
  `gui/widgets/plotly_chart_frame.py` and called from `edu_main.py`); launch via
  `python -m pmhelper.edu_main`, not by importing a tab directly.
- **CLI shows boxes instead of ✓/⚠ on Windows** → expected; the CLIs use ASCII
  markers `[OK]`/`[!]`/`[!!]` on Windows consoles.
- **`pmhelper` console command errors** → check the subcommand and flags first
  (see the CLI note above); `pmhelper`, `pmhelper-cpm`, and `pmhelper-pert` all
  resolve correctly. A bare `pmhelper project.csv` fails because the subcommand
  is missing, not because the entry point is broken.

## Debugging technique
Add a temporary `print(...)` or use `python -m pdb yourscript.py` (`n` next,
`s` step in, `p var` print, `c` continue). Remove prints before committing — in
production mode `launch_app.py` filters `[DEBUG_*]`-prefixed prints.

## Related skills
[[run-tests]] to confirm a fix. [[understand-this-codebase]] for the layout.
