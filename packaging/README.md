# packaging/

Build and deployment scripts for PMHelper. **Run them from anywhere** — each script
locates the repo root itself (PowerShell scripts `Set-Location` to the parent of this
folder; `build_setup.py` `chdir`s to the repo root). Build outputs go to the repo-root
`build/` and `dist/` directories.

## Windows executable — PyInstaller (the shipped Edu app)
| Script | Purpose |
|---|---|
| `build_production.ps1` | Full production build (icon + manifest + version info, no UPX, onedir), zips + hashes the result. Uses `pmhelper_edu_production.spec`. |
| `build_production_no_zip.ps1` | Same, without the zip/hash step. |
| `build_edu.ps1` | Quick dev build. Uses `pmhelper_edu.spec`. |

Build inputs consumed by the specs / scripts:
- `pmhelper_edu.spec`, `pmhelper_edu_production.spec` — PyInstaller specs (entry:
  `src/pmhelper/edu_main.py`). The production spec embeds the manifest + version info,
  found next to the spec via `SPECPATH`.
- `pmhelper_edu.manifest` — Windows app manifest (DPI-aware, asInvoker).
- `version_info.rc` — version metadata embedded in the .exe properties.
- `create_icon.py` — generates `assets/pmhelper_edu.ico` (written to the repo-root
  `assets/`).
- `patch_scipy.py` — post-processing helper for SciPy DLLs.

```powershell
.\packaging\build_production.ps1     # from the repo root
```

## Windows executable — cx_Freeze (alternative, used by CI)
- `build_setup.py` — cx_Freeze setup (entry: `launch_app.py`). CI runs
  `python packaging/build_setup.py build`.

## Deployment
- `deploy_production.ps1` — production deploy helper (branch/clean checks, DB backup).

## Notes
- Two packaging systems (PyInstaller and cx_Freeze) coexist for historical reasons;
  PyInstaller is the primary path for the Edu app. Consolidating to one is a sensible
  future cleanup.
- The specs/manifest are intentionally tracked (see the negations in `.gitignore`) so a
  fresh clone can build.
