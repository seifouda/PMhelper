---
name: add-a-feature
description: Use when adding a new capability to PMHelper — a new Edu GUI tab, a calculation, a CLI subcommand, or an API endpoint — so it follows the established pattern (pure calc in core, a Step generator, a tab, persistence, and tests). Follow this to avoid breaking the shared package.
---

# Add a feature the PMHelper way

The golden rule: **calculation logic is pure and lives in `core/`; the UI only
displays it.** Never put math in a tab or a route.

## Adding a new Edu domain (calc + tab) — end to end
1. **Pure calculation** — create `src/pmhelper/core/<x>_edu.py`. Only functions,
   dataclasses, and math. No `tkinter`, no file I/O, no globals. Copy the header
   style from `core/evm_calculations_edu.py` ("All functions are PURE").
2. **Step generator** — create `src/pmhelper/core/<x>_step_generator.py` returning
   a `List[Step]` (see `core/step_generators_edu.py` for the `Step` dataclass:
   `title, formula, substitution, result, interpretation, rag, children`). This is
   what makes the feature *teachable*.
3. **The tab** — create `src/pmhelper/gui/tabs/<x>_tab_edu.py`. A tab is a class
   taking `(parent_notebook, state, main_window=...)`, exposing a `.frame`. Read
   inputs from and write results to the shared `state` (`EduProjectState`).
4. **Register it** — in `src/pmhelper/gui/main_window_edu.py`, import the tab and
   add it inside `_build_tabs_ug` / `_build_tabs_pg` via `<lecture>_nb.add(tab.frame,
   text="...")`. If it's advanced/PG-only, add its key to `_PG_ONLY_TABS`.
5. **Persistence** — add a field in `src/pmhelper/gui/edu_state.py` and save/load it
   in `src/pmhelper/utils/project_io_edu.py` (mirror how `swot`, `pestel`, `wbs`,
   `raci`, `risk_register` are handled).
6. **Tests** — add `tests/test_<x>_edu.py` covering the pure functions and the step
   output. See [[run-tests]].
7. **(Optional) web parity** — add `web/src/app/features/<x>/` + a service in
   `web/src/app/core/services/`, and an endpoint if it needs the server.

## Adding a CLI subcommand
Edit the relevant `src/pmhelper/cli/<x>_cli.py`; keep it a thin wrapper that parses
args and calls `core/`. Support `--output` for text/JSON/CSV like the others.

## Adding an API endpoint
Add a router module under `src/pmhelper/server/api/routes/` and a schema in
`server/api/models/schemas.py`, then mount it in `server/main.py` (the single
FastAPI app). Call into `core/` directly — `api/routes/web.py` is the model to
copy. **Don't route it through `src/pmhelper/calculations.py`**: that is a
placeholder stub, not the calc engine (see [[understand-this-codebase]]).

CPU-bound calc should run in a thread-pool executor rather than blocking the event
loop (`run_in_executor`).

Two traps in `server/main.py`:
- The SPA catch-all `@app.get("/{full_path:path}")` matches in registration order
  and **swallows anything mounted after it** — your `include_router` must go
  above it, or the route silently returns `index.html` instead of 404ing.
- `web.py`'s endpoints are rate-limited via `app.state.limiter`. Tests that hit
  them repeatedly get 429; set `limiter.enabled = False` in the test.

## Before you finish
- Run [[run-tests]] — the suite must still collect and your new tests pass.
- Follow [[git-workflow]] — branch, small commits, push.
- If you invented a reusable pattern, capture it: [[capture-patterns]].

## Suggest improvements as you go
While building the feature, look one step beyond the request: a nearby function that
could be reused, a missing edge case, a test gap, a clearer name, duplicated logic
worth extracting. Raise it — small safe wins, just do them and mention it; bigger or
uncertain ones, propose with trade-offs and let the user choose. Leaving the code a
little better than you found it is part of the job.

## Check your assumptions
If anything about where a piece should live is unclear, **ask** rather than guess —
a misplaced calculation breaks the pure-core contract that the server and web rely on.
