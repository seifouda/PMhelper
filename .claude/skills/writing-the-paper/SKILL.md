---
name: writing-the-paper
description: Use when writing the academic paper / thesis about PMHelper — turning the repo's algorithms, validation reports, and educational design into paper sections (methodology, implementation, results, discussion). Points at exactly which files feed each section.
---

# Writing the academic paper from this repo

PMHelper is an *educational* tool, so the defensible research contribution is the
**learning-tool design** plus rigorous PM algorithm implementation. Here's how the
repo maps to a standard paper structure.

## Suggested section → source material

### 1. Introduction / Problem
PM students struggle to connect formulas to worked examples. Frame the tool as a
"show-your-work" tutor. Background material: `docs/reference/` (the KPIs & metrics
PDF and `PM_CHARTS_KPI_COMPARISON.md`), `FEATURES_LIST_EDU.md`.

### 2. Methodology / Algorithms (the meat)
Cite the implemented methods with their complexity and formulas — pull directly
from the pure modules (see [[pm-concepts-explained]] for the full map):
- CPM forward/backward pass — `core/cpm_analyzer.py` (≈ O(V+E)).
- PERT beta estimates + z-table probability — `core/pert_analyzer.py`.
- EVM KPI definitions — docstrings in `core/evm_calculations_edu.py`.
- AHP with consistency ratio and the published Random-Index table —
  `core/selection.py` (directly citable methodology).
- Crashing (cost-slope heuristic), RCPS, resource leveling, multi-objective/NPV
  optimization — respective `core/*` modules.

The **`core/*_step_generator.py`** files encode formula + substitution +
interpretation — ready-made **worked-example appendices**.

### 3. System design / Implementation
- Architecture: `docs/guides/SERVER_ARCHITECTURE.md` (FastAPI + SQLite monolith,
  pure `core` separated from UI, cloud-migration staging) — a citable decision log.
- Architecture Decision Record: `DECISIONS.md` (dated design choices with rationale).
- Layers: pure `core/` engine, Tkinter GUI, FastAPI server, Angular web, CLIs
  (see [[understand-this-codebase]]).

### 4. Pedagogical design (your novel angle)
- UG/PG dual mode and the **L1–L10 lecture-sequenced** curriculum mapping in
  `gui/main_window_edu.py`.
- "Show-your-work" `Step` trees, RAG indicators, and the *same* steps rendered in
  both desktop and web — a genuine design contribution.

### 5. Validation / Results
`docs/reports/` is your evidence base: `COMPREHENSIVE_TESTING_REPORT.md`,
`FINAL_TEST_SUMMARY.md`, `TECHNICAL_REPORT_v1.0.0.md`, `VALIDATION_ENHANCEMENT.md`,
per-feature implementation summaries, and phase completion reports. Reproducibility:
~1,350 automated tests in `tests/` with coverage; smoke checklist in
`docs/reports/UI_SMOKE_TEST_CHECKLIST_EDU.md`.

> **Re-count before you publish** — the suite grows:
> `pytest --collect-only -q --no-cov | tail -1`. Never cite a test count you
> haven't just measured; a stale number in a reproducibility section is exactly
> the kind of claim a reviewer will check.

### 6. Discussion / Limitations / Future work
Be honest, and verify each limitation against the code before you write it — this
section is where unverified repo folklore tends to get laundered into citable
claims. Real, verified ones as of this writing:
- Some docs are aspirational vs. the code (`CALCULATIONS_MIGRATION.md` is still a
  plan; `src/pmhelper/calculations.py` is a stub, not the facade its name implies).
- The legacy vs. Edu split, and that the `pmhelper-gui` console script still
  launches the **legacy** window while the Edu app is the shipped product.
- `tests/server/` was written against an older server API and largely does not run,
  so the headline test count is not uniformly load-bearing.

Future work: web feature parity, cloud deployment (already staged in the
architecture doc).

## Writing hygiene
- **Verify every claim against the code before citing it** — don't repeat README
  marketing (coverage %, PyPI availability) without checking.
- Quote formulas from the actual module, not from memory.
- Keep a table mapping each claim → source file for your own traceability.

## Related skills
[[pm-concepts-explained]] · [[understand-this-codebase]] · [[run-tests]] (to
regenerate results/coverage evidence).
