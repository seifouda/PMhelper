# PMhelper Edu — V2 Implementation Plan

> **Scope:** 12 feature areas (Three-Point Chart, Financial Calcs, Factor Scoring, RACI, Risk Assessment/Response, AON/AOA, Cost Estimation, Resource Leveling enhancements, Strategic Visualizations, Z-Score Table & Probability, Cross-Tab Polish), tab group refactor, web porting
> **Approach:** 1 developer + AI agent assistance
> **Date:** April 5, 2026
> **Last Status Update:** April 20, 2026
> **Predecessor:** [EDU_V1_Plan.md](EDU_V1_Plan.md) — code-complete as of March 25, 2026
> **Branch:** `feat/web-v1` (continue until PR #3 merges, then branch from `production`)

---

## V2 Vision

V1 delivered a complete desktop PM teaching tool (20 phases, 797+ tests, 18 tabs) and an Angular web front-end (28/28 tests, production build ready). V2 adds **9 major feature areas** requested from the PM curriculum, extends the educational scaffolding model (worked solutions + "Try It Yourself"), and restructures the tab layout into **collapsible groups**.

### Design Principles

1. **Desktop-First** — All new features target the Tkinter desktop app first; web (Angular) porting follows later in V2
2. **Dual-Mode Calculators** — Every calculator works as a **standalone** tool (students type textbook problems) AND offers a **"Load from Project"** button to pull data from the active `.pmproj` file
3. **Educational Depth** — Every new feature gets full **worked solutions** (step-by-step with formulas) plus a **"Try It Yourself"** mode where students solve before the answer is revealed
4. **New Demo Files** — V2 features use **new separate demo files** (V1 demos remain untouched)
5. **Collapsible Tab Groups** — The 18+ tabs are organized into categories: Schedule, Cost, Risk, Strategic, Dashboard

---

## Existing Code Inventory (Reuse Map)

| Area                 | What Exists                                | Where                         | Reuse Plan                                               |
| -------------------- | ------------------------------------------ | ----------------------------- | -------------------------------------------------------- |
| PERT / Three-Point   | `calculate_pert_estimates()` — Te, σ²      | `core/calculations.py:32`     | Reuse calc; add chart + table tab                        |
| NPV                  | `NPVOptimizer.calculate_npv()`             | `core/npv_optimization.py`    | Reuse for NPV calc; add 5 more financial metrics         |
| AHP / Linear Scoring | `AHPAnalyzer`, `LinearScoringRule`         | `core/selection.py`           | Keep; add 3 new factor scoring models alongside          |
| Selection Tab        | Empty stub — "Coming Soon"                 | `gui/tabs/selection_tab.py`   | **Replace entirely** with Financial + Factor Scoring tab |
| Risk Register        | `Risk` dataclass, `RiskRegister`           | `core/risk_register_edu.py`   | **Extend** with response fields                          |
| Risk Tab             | 2 sub-tabs (Register, Matrix)              | `gui/tabs/risk_tab_edu.py`    | **Add** 2 more sub-tabs                                  |
| AON Network          | `NetworkBuilder` DiGraph                   | `core/network_builder.py`     | Keep; build parallel AOA builder                         |
| Network Tab          | AON vis.js viewer                          | `gui/tabs/network_tab.py`     | Add AOA mode + toggle                                    |
| Resource Leveling    | `MinimumMomentLeveling`, `BurgessLeveling` | `core/resource_leveling.py`   | Reuse; add educational walkthrough                       |
| RCPS Tab             | 2 sub-tabs (Schedule, Histograms)          | `gui/tabs/rcps_tab_edu.py`    | Add walkthrough sub-tab                                  |
| PERT Tab             | Empty stub                                 | `gui/tabs/pert_tab_edu.py`    | **Replace** with Three-Point Estimate tab                |
| Step Generators      | `CrashingStepGenerator`, EVM steps         | `core/step_generators_edu.py` | Extend pattern for new features                          |

---

## Tab Group Structure (Post-Refactor)

After Phase 1, tabs will be organized into collapsible groups:

```
📁 Schedule
   ├── Input Activities
   ├── Results
   ├── Network Diagram
   ├── PERT Diagram
   ├── Gantt Chart
   ├── Three-Point Estimates          ← NEW (Phase 2)
   └── Crashing

📁 Cost
   ├── EVM Dashboard
   ├── Financial Analysis             ← NEW (Phase 3, replaces Selection stub)
   ├── Cost Estimation                ← NEW (Phase 5)
   └── Resources (RCPS)

📁 Risk
   ├── Risk Analysis (4 sub-tabs)     ← EXTENDED (Phase 6)
   ├── Probability / Monte Carlo
   └── RCPS Crash

📁 Strategic
   ├── Responsibility Matrix (RACI)   ← NEW (Phase 4)
   ├── Charter
   ├── Charter Mgr
   ├── DPCI
   ├── SWOT
   ├── PESTEL
   └── WBS

📁 Dashboard
   └── Dashboard
```

---

## ~~Phase 0 — V1 Carry-Forward & QA~~ — OBSOLETE (superseded)

> **⚠️ This phase is obsolete. Task text below is preserved as a record of intent —
> do not work it.** Superseded by the repo reorganization onto `EDU_PROD`:
>
> - **0.1–0.3** reference PR #3 and branch `feat/web-v1`. That branch is 10+ commits
>   behind and pre-dates the reorg; work continues on `EDU_PROD`. The same stale
>   `feat/web-v1` pin was found and fixed in `render.yaml` (Render was serving code
>   older than the "fix broken imports" commit while deploys looked green).
> - **0.8–0.9** (`v1.0.0-web` tag + release) never happened — `v1.0.0` remains the
>   only tag. Rather than cut a retroactive V1 web release, these fold into
>   Phase 13's `v2.0.0`.
> - **0.4–0.7, 0.10** (deploy verification, smoke test, PyInstaller, rollback doc)
>   remain valid work but belong to Phase 13, not as a V2 blocker.
>
> **Original goal:** Complete all deferred V1 items before starting new work.
> **Original priority:** P0 — nothing else starts until this is done.

| #    | Task                                        | What to Do                                          | Effort   | Status |
| ---- | ------------------------------------------- | --------------------------------------------------- | -------- | ------ |
| 0.1  | Merge PR #3 (`feat/web-v1` → `production`)  | Resolve any conflicts, ensure CI green, merge       | 0.5 day  | ⬜     |
| 0.2  | Set `RENDER_DEPLOY_HOOK_URL` GitHub secret  | Render dashboard → Deploy Hook URL → GitHub Secrets | 15 min   | ⬜     |
| 0.3  | Update `render.yaml` branch to `production` | Commit to production after merge                    | 15 min   | ⬜     |
| 0.4  | Verify live deploy on Render                | Hit `/health`, test PG guard, load sample data      | 0.5 day  | ⬜     |
| 0.5  | Run 30-item UI smoke test (desktop)         | Execute `UI_SMOKE_TEST_CHECKLIST_EDU.md`            | 0.5 day  | ⬜     |
| 0.6  | PyInstaller `--onedir` build + test         | Build on clean machine, test launch without Python  | 0.5 day  | ⬜     |
| 0.7  | Test interactive network viewer (600 tasks) | Load large demo, open in browser, verify zoom/pan   | 0.25 day | ⬜     |
| 0.8  | Update CHANGELOG.md                         | Add `[1.0.0-web]` entry for web features            | 0.25 day | ⬜     |
| 0.9  | Tag `v1.0.0-web` + GitHub Release           | Annotated tag, release notes                        | 0.25 day | ⬜     |
| 0.10 | Document rollback plan in README            | "To roll back: revert merge on production"          | 15 min   | ⬜     |

---

## ✅ Phase 1 — Tab Group Refactor & Infrastructure — COMPLETE

> **Goal:** Refactor the flat 18-tab `ttk.Notebook` into collapsible tab groups so new tabs can be organized logically.
> **Why first:** All subsequent phases add new tabs — they need the group structure in place.

| #   | Task                                   | What to Do                                                                                                                                                    | Files                                                  | Status |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------ |
| 1.1 | Design collapsible group widget        | Create a `TabGroupNotebook` widget that uses nested `ttk.Notebook` or `ttk.LabelFrame` with collapsible sections (Schedule, Cost, Risk, Strategic, Dashboard) | `gui/widgets/tab_group_notebook.py` (NEW)              | ✅     |
| 1.2 | Refactor `_build_tabs()`               | Replace flat `ttk.Notebook` with `TabGroupNotebook`; assign all 18 existing tabs to their groups per the structure above                                      | `gui/main_window_edu.py` — `_build_tabs()` at line 189 | ✅     |
| 1.3 | Update `_all_tabs_ordered`             | Adapt ordered list + PG-only show/hide logic to work with nested groups                                                                                       | `gui/main_window_edu.py` — lines 303–343               | ✅     |
| 1.4 | Update tab selection / navigation      | Ensure `on_tab_selected()`, keyboard navigation, and programmatic tab switching work with groups                                                              | `gui/main_window_edu.py`                               | ✅     |
| 1.5 | Regression test all 18 existing tabs   | Verify every tab still renders, loads data, and responds to mode toggle (UG/PG)                                                                               | Tests: existing 797+ tests must pass                   | ✅     |
| 1.6 | Create V2 demo data infrastructure     | Add `data/demos/v2/` folder structure; create `DemoLoader` utility that reads demo JSON files and populates the appropriate calculator                        | `data/demos/v2/` (NEW), `utils/demo_loader.py` (NEW)   | ✅     |
| 1.7 | Create base `EducationalCalculatorTab` | Abstract base class with: standalone input panel, "Load from Project" button, "Worked Solution" expandable frame, "Try It Yourself" toggle                    | `gui/widgets/educational_calculator_tab.py` (NEW)      | ✅     |

---

## ✅ Phase 2 — Three-Point Estimate Tab — COMPLETE

> **Goal:** Add a dedicated "Three-Point Estimates" tab showing O/P/M/Expected values per activity as a line chart and summary table.
> **Existing code:** `calculate_pert_estimates()` in `core/calculations.py` computes Te = (O+4M+P)/6 and σ².
> **Decision:** Standalone calculator + Load from Project.

| #   | Task                      | What to Do                                                                                                                                                                                                                                              | Files                                                                     | Status |
| --- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------ |
| 2.1 | Create Three-Point engine | Extract/extend PERT calculation into a dedicated module: given O, M, P per activity → compute Expected (Te), Variance (σ²), Std Dev (σ), project-level σ for critical path. Support both PERT-weighted `(O+4M+P)/6` and Triangular `(O+M+P)/3` formulas | `core/three_point_engine.py` (NEW)                                        | ✅     |
| 2.2 | Build Three-Point tab UI  | Create tab with: (1) Standalone input grid (Activity, O, M, P — editable rows), (2) "Load from Project" button pulling from Input Activities PERT data, (3) Formula selector (PERT vs Triangular), (4) "Calculate" button                               | `gui/tabs/three_point_tab_edu.py` (NEW) — replaces `pert_tab_edu.py` stub | ✅     |
| 2.3 | Results table             | Treeview table with columns: Activity, O, M, P, Expected (Te), Variance (σ²), Std Dev (σ). Footer row with project totals for critical path. Color-code critical path activities                                                                        | Same file — sub-frame                                                     | ✅     |
| 2.4 | Line chart visualization  | Matplotlib chart with 4 lines per activity (O, M, P, Expected) — X-axis = Activity ID, Y-axis = Duration. Legend, gridlines, highlight critical path activities                                                                                         | Same file — chart sub-frame using `FigureCanvasTkAgg`                     | ✅     |
| 2.5 | Worked solution panel     | Step-by-step panel: show formula → substitute values → compute Te → compute σ² → interpret. Use existing `step_generators_edu.py` pattern                                                                                                               | `core/three_point_step_generator.py` (NEW)                                | ✅     |
| 2.6 | "Try It Yourself" mode    | Hide the results; student enters their answer for Te per activity; "Check" button compares; reveal on completion                                                                                                                                        | `gui/tabs/three_point_tab_edu.py` — practice frame                        | ✅     |
| 2.7 | Demo file                 | Create `data/demos/v2/three_point_demo.json` with 8–10 activities with O/M/P values and known solutions                                                                                                                                                 | `data/demos/v2/three_point_demo.json` (NEW)                               | ✅     |
| 2.8 | Register tab in group     | Add to Schedule group in `TabGroupNotebook`; update `_all_tabs_ordered` and `tabs` dict                                                                                                                                                                 | `gui/main_window_edu.py`                                                  | ✅     |
| 2.9 | Unit tests                | Test engine calculations (known PERT values), test Load from Project, test Try It Yourself scoring                                                                                                                                                      | `tests/test_three_point.py` (NEW)                                         | ✅     |

---

## ✅ Phase 3 — Financial Analysis Tab (Project Selection Calculators) — COMPLETE

> **Goal:** Replace the empty `selection_tab.py` stub with a full Financial Analysis tab containing 6 financial calculators and 3 factor scoring models.
> **Existing code:** `NPVOptimizer` (CLI only), `AHPAnalyzer`, `LinearScoringRule` in `core/selection.py`.
> **Decision:** Standalone + Load from Project. Full worked solutions + Try It Yourself.

### Phase 3A — Financial Calculators

| #    | Task                               | What to Do                                                                                                                                                                                                                                                                                                                                                                         | Files                                                               | Status |
| ---- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------ |
| 3A.1 | Financial calculation engine       | Module with functions for: **Payback Period** (cumulative CF until break-even), **Discounted Payback Period** (discounted CF until break-even), **ROI** ((Gain−Cost)/Cost × 100), **NPV** (Σ CFₜ/(1+r)ᵗ — reuse from `npv_optimization.py`), **IRR** (rate where NPV=0 — use `scipy.optimize.brentq` or bisection), **Profitability Index** (PV of future CF / Initial Investment) | `core/financial_calcs.py` (NEW)                                     | ✅     |
| 3A.2 | Financial Analysis tab — structure | Create tabbed sub-notebook within the Financial Analysis tab: sub-tabs for (1) Financial Calculators, (2) Factor Scoring Models (Phase 3B). Place in Cost group.                                                                                                                                                                                                                   | `gui/tabs/financial_tab_edu.py` (NEW) — replaces `selection_tab.py` | ✅     |
| 3A.3 | Financial Calculators sub-tab UI   | Standalone input panel: Initial Investment, Discount Rate, table of (Year, Cash Flow) rows. "Load from Project" pulls costs/durations. 6 checkboxes to select which metrics to compute. "Calculate" button.                                                                                                                                                                        | Same file — financial sub-tab                                       | ✅     |
| 3A.4 | Financial results display          | Results panel: table with Metric / Value / Interpretation columns. E.g., "Payback Period = 3.4 years — Investment recovered within project horizon". NPV positive = green, negative = red                                                                                                                                                                                          | Same file                                                           | ✅     |
| 3A.5 | Financial worked solutions         | Step-by-step for each selected metric: formula → substitution → intermediate steps → final value → interpretation. E.g., Payback: show cumulative table row by row until break-even; IRR: show bisection iterations                                                                                                                                                                | `core/financial_step_generator.py` (NEW)                            | ✅     |
| 3A.6 | Financial "Try It Yourself"        | Hide all results; student enters their answers for each selected metric; "Check" button validates (tolerance ±0.01 for rates, ±0.1 for currency)                                                                                                                                                                                                                                   | `gui/tabs/financial_tab_edu.py` — practice frame                    | ✅     |
| 3A.7 | Payback chart                      | Matplotlib: cumulative cash flow bar chart with break-even line for Payback; discounted CF overlay for Discounted Payback                                                                                                                                                                                                                                                          | Same file — chart                                                   | ✅     |
| 3A.8 | Financial demo file                | `data/demos/v2/financial_demo.json` — 2 project scenarios with cash flows, known Payback/NPV/IRR/PI values                                                                                                                                                                                                                                                                         | `data/demos/v2/financial_demo.json` (NEW)                           | ✅     |
| 3A.9 | Unit tests — financial             | Test all 6 calculations against hand-computed values; edge cases (negative CF, zero discount rate, no payback possible)                                                                                                                                                                                                                                                            | `tests/test_financial_calcs.py` (NEW)                               | ✅     |

### Phase 3B — Factor Scoring Models

| #    | Task                             | What to Do                                                                                                                                                                                                                                                                                                                                                                              | Files                                                    | Status |
| ---- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------ | ---------- | ----------- | -------------------------------------------------------------------------------------------- | --------- | --- |
| 3B.1 | Factor scoring engine            | Module with 3 models: (1) **Unweighted 0-1 Scoring** — each criterion yes/no (0 or 1), sum scores per project, (2) **Unweighted Factor Scoring** — each criterion scored 1–5 (or custom scale), sum per project, (3) **Weighted Factor Scoring** — criteria have weights (must sum to 1.0 or 100%), score × weight, sum per project. All models rank N projects and identify the winner | `core/factor_scoring.py` (NEW)                           | ✅     |
| 3B.2 | Factor Scoring sub-tab UI        | Standalone input: (1) Define criteria list (add/remove/reorder), (2) Define projects list, (3) Select model type (radio buttons), (4) If weighted: enter weights per criterion, (5) Score matrix grid (projects × criteria), (6) "Load from Project" loads criteria from project metadata                                                                                               | `gui/tabs/financial_tab_edu.py` — factor scoring sub-tab | ✅     |
| 3B.3 | Factor scoring results           | Results table: Project                                                                                                                                                                                                                                                                                                                                                                  | Criterion1                                               | ...    | CriterionN | Total Score | Rank. Color-code winner. Side-by-side comparison bar chart (projects on X, total score on Y) | Same file | ✅  |
| 3B.4 | Factor scoring worked solutions  | For weighted model: show weight × score per cell → row sum → rank; for 0-1: show binary mapping logic                                                                                                                                                                                                                                                                                   | `core/factor_scoring_step_generator.py` (NEW)            | ✅     |
| 3B.5 | Factor scoring "Try It Yourself" | Give criteria, weights, scores; student computes weighted totals and ranking; validate answers                                                                                                                                                                                                                                                                                          | Same tab — practice frame                                | ✅     |
| 3B.6 | Factor scoring demo file         | `data/demos/v2/factor_scoring_demo.json` — 4 projects, 5 criteria, known rankings for each model                                                                                                                                                                                                                                                                                        | `data/demos/v2/factor_scoring_demo.json` (NEW)           | ✅     |
| 3B.7 | Unit tests — factor scoring      | All 3 models with known solutions; edge cases (tied scores, single project, zero weights)                                                                                                                                                                                                                                                                                               | `tests/test_factor_scoring.py` (NEW)                     | ✅     |

---

## ✅ Phase 4 — Responsibility Matrix (RACI) — COMPLETE

> **Goal:** New tab for RACI matrix (Responsible/Accountable/Consulted/Informed) + Deliverables vs Department matrix.
> **Existing code:** Nothing — completely new.
> **Decision:** Both auto-populate from project activities AND free-form grid. Goes in Strategic group.

| #    | Task                              | What to Do                                                                                                                                                                                                                                                                                                                           | Files                                              | Status |
| ---- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------- | ------ |
| 4.1  | RACI data model                   | Dataclass: `RACIMatrix` with activities (rows), roles/people (columns), cell values ∈ {R, A, C, I, ""}. Validation: exactly 1 A per activity (warn if missing), at least 1 R per activity. Support export to dict/JSON for persistence in `.pmproj`                                                                                  | `core/raci_model.py` (NEW)                         | ✅     |
| 4.2  | RACI tab — main structure         | New tab with 2 sub-tabs: (1) **Task × Role RACI** (activities vs team members), (2) **Deliverables × Department** (project deliverables vs organizational departments)                                                                                                                                                               | `gui/tabs/raci_tab_edu.py` (NEW)                   | ✅     |
| 4.3  | Task × Role sub-tab               | Editable grid: rows = activities (auto-populated from Input Activities OR free-form add/remove), columns = roles (free-form add/remove: "Project Manager", "Developer", "QA", etc.). Cell = dropdown {R, A, C, I, ""}. Color-coded cells (R=blue, A=red, C=yellow, I=green). "Load from Project" fills activity names from `.pmproj` | Same file — sub-tab 1                              | ✅     |
| 4.4  | Deliverables × Department sub-tab | Same grid concept but rows = deliverables (WBS work packages if available, else free-form), columns = departments (free-form). Cell = dropdown {R, A, C, I, ""}                                                                                                                                                                      | Same file — sub-tab 2                              | ✅     |
| 4.5  | RACI validation panel             | Real-time validation warnings: "Activity X has no Accountable (A)", "Activity Y has multiple A assignments", "Role Z has no assignments". Summary stats: total assignments by type                                                                                                                                                   | Same file — bottom panel                           | ✅     |
| 4.6  | RACI worked solution              | Educational panel explaining: what each letter means, how to construct a RACI, common mistakes (no A, multiple A's). Worked example with 5 activities × 4 roles                                                                                                                                                                      | `core/raci_step_generator.py` (NEW)                | ✅     |
| 4.7  | RACI "Try It Yourself"            | Give a scenario description; student fills the RACI grid; "Check" validates against expected answer                                                                                                                                                                                                                                  | Same tab — practice frame                          | ✅     |
| 4.8  | RACI persistence                  | Save/load RACI matrices in `.pmproj` file format (add `raci_data` section to project state)                                                                                                                                                                                                                                          | `gui/tabs/raci_tab_edu.py` + `utils/project_io.py` | ✅     |
| 4.9  | RACI demo file                    | `data/demos/v2/raci_demo.json` — software project scenario with 10 activities, 5 roles, pre-filled RACI with known correct answers                                                                                                                                                                                                   | `data/demos/v2/raci_demo.json` (NEW)               | ✅     |
| 4.10 | Register in Strategic group       | Add to `TabGroupNotebook` Strategic category; update `_all_tabs_ordered` and `tabs` dict                                                                                                                                                                                                                                             | `gui/main_window_edu.py`                           | ✅     |
| 4.11 | Unit tests — RACI                 | Model validation (single A enforcement), grid population from activities, persistence round-trip                                                                                                                                                                                                                                     | `tests/test_raci.py` (NEW)                         | ✅     |

---

## ✅ Phase 5 — Cost Estimation Techniques — COMPLETE

> **Goal:** New "Cost Estimation" tab with 7 estimation methods as a standalone educational calculator.
> **Existing code:** Nothing — completely new.
> **Decision:** Standalone + Load from Project. Goes in Cost group.

### 7 Estimation Techniques

1. **Top-Down (Analogous)** — Estimate from similar past projects + adjustment factor
2. **Bottom-Up** — Sum of WBS work-package estimates (can load from WBS if available)
3. **Work Element (Template)** — Cost = Labour + Materials + Equipment, per work element
4. **Cost-Capacity Index (Power Sizing)** — Cost₂ = Cost₁ × (Capacity₂/Capacity₁)^X
5. **Unit/Factor Method** — Cost = Unit_Cost × Quantity × Factor
6. **Power Sizing Model** — C_new = C_ref × (S_new/S_ref)^x, where x = sizing exponent
7. **Learning Curves** — T_N = T₁ × N^b, where b = ln(learning_rate)/ln(2)

| #    | Task                                      | What to Do                                                                                                                                                                                                                                            | Files                                           | Status |
| ---- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------ |
| 5.1  | Cost estimation engine                    | Module with a class per technique: `AnalogousEstimator`, `BottomUpEstimator`, `WorkElementEstimator`, `PowerSizingEstimator`, `UnitFactorEstimator`, `CostCapacityEstimator`, `LearningCurveEstimator`. Each has `estimate()` → cost + breakdown dict | `core/cost_estimation.py` (NEW)                 | ✅     |
| 5.2  | Cost Estimation tab — structure           | New tab with a method selector (7 radio buttons or dropdown). Selecting a method shows the corresponding input form below. "Load from Project" fills relevant data (e.g., WBS costs for bottom-up)                                                    | `gui/tabs/cost_estimation_tab_edu.py` (NEW)     | ✅     |
| 5.3  | Top-Down input/output                     | Inputs: Reference project cost, Adjustment factors (complexity, size, risk %). Output: Estimated cost with adjustment breakdown                                                                                                                       | Same file — top-down panel                      | ✅     |
| 5.4  | Bottom-Up input/output                    | Inputs: Table of work packages (Name, Labour Cost, Material Cost, Equipment Cost, Overhead %). "Load from Project" pulls WBS work packages. Output: Total cost with breakdown tree                                                                    | Same file — bottom-up panel                     | ✅     |
| 5.5  | Work Element input/output                 | Inputs: Work elements table (Element, Hours, Rate, Material $, Equip $). Output: Element costs + total                                                                                                                                                | Same file — work element panel                  | ✅     |
| 5.6  | Power Sizing / Cost-Capacity input/output | Inputs: Reference cost, Reference capacity, Target capacity, Sizing exponent (x). Output: Estimated cost with formula                                                                                                                                 | Same file — power sizing panel                  | ✅     |
| 5.7  | Unit/Factor input/output                  | Inputs: Table of items (Item, Unit Cost, Quantity, Factor). Output: Extended cost per item + total                                                                                                                                                    | Same file — unit/factor panel                   | ✅     |
| 5.8  | Learning Curves input/output              | Inputs: First unit time/cost (T₁), Learning rate (%), Target unit number (N). Output: T_N, cumulative average, total cost. Plot: learning curve chart (unit # vs time)                                                                                | Same file — learning curve panel                | ✅     |
| 5.9  | Cost estimation worked solutions          | Step generator for each technique: show formula → substitute → compute → interpret. Learning curves: show the log transformation steps                                                                                                                | `core/cost_estimation_step_generator.py` (NEW)  | ✅     |
| 5.10 | Cost estimation "Try It Yourself"         | Per technique: give inputs, student computes cost; validate against known answer                                                                                                                                                                      | Same tab — practice frame                       | ✅     |
| 5.11 | Comparison view                           | After computing 2+ techniques, show a side-by-side comparison table + bar chart of estimated costs from different methods                                                                                                                             | Same file — comparison panel                    | ✅     |
| 5.12 | Cost estimation demo files                | `data/demos/v2/cost_estimation_demo.json` — scenarios for each technique with known solutions                                                                                                                                                         | `data/demos/v2/cost_estimation_demo.json` (NEW) | ✅     |
| 5.13 | Register in Cost group                    | Add to `TabGroupNotebook` Cost category                                                                                                                                                                                                               | `gui/main_window_edu.py`                        | ✅     |
| 5.14 | Unit tests — cost estimation              | All 7 techniques with hand-verified results; edge cases (zero quantities, learning rate = 100%)                                                                                                                                                       | `tests/test_cost_estimation.py` (NEW)           | ✅     |

---

## ✅ Phase 6 — Risk Assessment Matrix & Risk Response Planning — COMPLETE

> **Goal:** Extend the existing Risk Analysis tab (2 sub-tabs) with 2 new sub-tabs: Risk Assessment Matrix and Risk Response Planning. Also extend the `Risk` dataclass with response fields.
> **Existing code:** `Risk` dataclass + `RiskRegister` in `core/risk_register_edu.py`; Risk tab with Register + Heat Map in `gui/tabs/risk_tab_edu.py`.
> **Decision:** Both — extend Risk Register columns AND add separate detailed sub-tabs.

| #    | Task                                 | What to Do                                                                                                                                                                                                                                                                                                                                                                                                         | Files                                           | Status |
| ---- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | ------ |
| 6.1  | Extend `Risk` dataclass              | Add fields: `risk_score` (P × I, auto-computed), `risk_rank` (ordinal within register), `response_strategy` (enum: Avoid/Transfer/Mitigate/Accept/Exploit/Share/Enhance), `response_description` (str), `response_owner` (str), `response_cost` (float), `residual_probability` (float 1–5), `residual_impact` (float 1–5), `residual_score` (auto-computed), `trigger_conditions` (str), `contingency_plan` (str) | `core/risk_register_edu.py`                     | ✅     |
| 6.2  | Update Risk Register sub-tab columns | Add visible columns to the Treeview: Risk Score (auto-computed, sortable), Rank, Response Strategy (dropdown). Sorting by Risk Score ranks risks automatically                                                                                                                                                                                                                                                     | `gui/tabs/risk_tab_edu.py` — sub-tab 1          | ✅     |
| 6.3  | Risk Assessment Matrix sub-tab (NEW) | **Sub-tab 3:** 5×5 matrix grid (Probability 1–5 on Y-axis, Impact 1–5 on X-axis). Each cell shows count of risks + risk IDs. Color zones: Green (1–4 low), Yellow (5–9 medium), Orange (10–15 high), Red (16–25 critical). Click a cell to list risks in that position. Summary panel: total risks per zone, top-5 risks by score                                                                                  | `gui/tabs/risk_tab_edu.py` — new sub-tab        | ✅     |
| 6.4  | Risk ranking view                    | Sortable table of all risks ordered by Risk Score (desc). Columns: Rank, ID, Name, P, I, Score, Category, Response Strategy. Bar chart: horizontal bars per risk colored by zone                                                                                                                                                                                                                                   | Same sub-tab — ranking panel                    | ✅     |
| 6.5  | Risk Response Planning sub-tab (NEW) | **Sub-tab 4:** Detailed response planning form per selected risk. Fields: Response Strategy (dropdown with PM-standard options per threat/opportunity), Description, Owner, Estimated Response Cost, Residual P, Residual I, Residual Score (auto), Trigger Conditions, Contingency Plan. "Apply to All Unplanned" button sets Accept as default                                                                   | `gui/tabs/risk_tab_edu.py` — new sub-tab        | ✅     |
| 6.6  | Response effectiveness summary       | Table: Risk ID, Original Score, Response, Residual Score, Score Reduction (%). Total: Original Total Exposure vs Residual Total Exposure. "Response Effectiveness" metric = (Original − Residual) / Original × 100%                                                                                                                                                                                                | Same sub-tab — summary panel                    | ✅     |
| 6.7  | Risk worked solutions                | Step-by-step panel: (1) How to assess P and I, (2) Computing Risk Score, (3) Plotting on the matrix, (4) Selecting response strategies (when to Avoid vs Mitigate vs Accept), (5) Computing residual risk                                                                                                                                                                                                          | `core/risk_step_generator.py` (NEW)             | ✅     |
| 6.8  | Risk "Try It Yourself"               | Give a scenario with risk descriptions; student assigns P, I, computes scores, selects strategies; validate against expected answers                                                                                                                                                                                                                                                                               | `gui/tabs/risk_tab_edu.py` — practice frame     | ✅     |
| 6.9  | Risk demo file                       | `data/demos/v2/risk_assessment_demo.json` — 12 risks with pre-assigned P/I, known scores, recommended strategies, and residual values                                                                                                                                                                                                                                                                              | `data/demos/v2/risk_assessment_demo.json` (NEW) | ✅     |
| 6.10 | Unit tests — risk extensions         | Test Risk Score auto-computation, ranking, response effectiveness calc, residual score. Test backward compatibility (old `.pmproj` files without response fields load cleanly)                                                                                                                                                                                                                                     | `tests/test_risk_assessment.py` (NEW)           | ✅     |

---

## ✅ Phase 7 — AON / AOA Dual Network Mode — COMPLETE

> **Goal:** Add Activity-on-Arrow (AOA) representation alongside the existing Activity-on-Node (AON). Support both input modes with conversion between them.
> **Existing code:** `NetworkBuilder` (AON DiGraph) in `core/network_builder.py`; Network tab with vis.js in `gui/tabs/network_tab.py`.
> **Decision:** Both input modes — full AON and AOA entry with bidirectional conversion.

| #    | Task                        | What to Do                                                                                                                                                                                                                                                                                    | Files                                     | Status |
| ---- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ------ |
| 7.1  | AOA data model              | `AOANetwork` class: events (numbered nodes), arrows (activities on edges), dummy activities (zero duration, dashed). Event = `{id: int, label: str, earliest_time: float, latest_time: float}`. Arrow = `{from_event: int, to_event: int, activity_id: str, duration: float, is_dummy: bool}` | `core/aoa_network_builder.py` (NEW)       | ✅     |
| 7.2  | AOA CPM engine              | Forward pass (earliest event times), backward pass (latest event times), float calculation per arrow/activity, critical path identification on AOA graph. Must produce identical critical path to AON for same project                                                                        | Same file — CPM methods                   | ✅     |
| 7.3  | Dummy activity insertion    | Algorithm to insert dummy activities where needed: (1) when two activities share same start AND end event, (2) to enforce dependency logic that can't be represented without dummies. Follow the merge/burst node rules from PM textbooks                                                     | Same file — `insert_dummies()`            | ✅     |
| 7.4  | AON → AOA converter         | Given an AON network (activity list with predecessors), generate the equivalent AOA network with proper event numbering and dummy insertion. Validate: same critical path, same floats                                                                                                        | `core/network_converter.py` (NEW)         | ✅     |
| 7.5  | AOA → AON converter         | Reverse conversion: given AOA events + arrows, extract activity list with predecessors. Strip dummy activities                                                                                                                                                                                | Same file — reverse method                | ✅     |
| 7.6  | AOA input mode in Input tab | Toggle in Input Activities tab: "Network Type: AON / AOA". In AOA mode, input changes to: Event-based entry (From Event, To Event, Activity, Duration) instead of predecessor-based. Both modes maintained simultaneously; switching converts automatically                                   | `gui/tabs/input_tab_edu.py` — mode toggle | ✅     |
| 7.7  | AOA visualization           | vis.js network diagram in AOA style: numbered circles (events) connected by labeled arrows (activities). Dummies shown as dashed arrows. Event nodes show ET/LT. Critical path arrows highlighted in red                                                                                      | `gui/tabs/network_tab.py` — AOA renderer  | ✅     |
| 7.8  | Network tab mode toggle     | Add "View: AON / AOA" toggle in Network Diagram tab. Switching re-renders the same project in the other representation. Both views coexist                                                                                                                                                    | `gui/tabs/network_tab.py` — toggle button | ✅     |
| 7.9  | AOA PERT diagram            | If PERT data available, show AOA with 4-compartment event nodes (Event#, ET, LT, Slack)                                                                                                                                                                                                       | `gui/tabs/pert_diagram_tab.py` — AOA mode | ✅     |
| 7.10 | AOA worked solutions        | Step-by-step: (1) How to number events, (2) When dummies are needed (rules), (3) Forward pass on AOA, (4) Backward pass, (5) Identifying critical path on arrows. Side-by-side AON vs AOA comparison                                                                                          | `core/aoa_step_generator.py` (NEW)        | ✅     |
| 7.11 | AOA "Try It Yourself"       | Give an activity list; student draws AOA (assigns events, identifies dummies); validate event numbering and critical path                                                                                                                                                                     | Network tab — practice mode               | ✅     |
| 7.12 | AOA demo file               | `data/demos/v2/aoa_demo.json` — project with known AOA representation, including required dummy activities                                                                                                                                                                                    | `data/demos/v2/aoa_demo.json` (NEW)       | ✅     |
| 7.13 | Unit tests — AOA            | AOA CPM correctness (vs AON), dummy insertion correctness, converter round-trip (AON→AOA→AON = original), edge cases (parallel activities, complex dependencies)                                                                                                                              | `tests/test_aoa_network.py` (NEW)         | ✅     |

---

## ✅ Phase 8 — Resource Leveling Educational Enhancements — COMPLETE

> **Goal:** Enhance the existing RCPS tab with educational walkthrough showing smoothing vs constrained leveling, step-by-step algorithm visualization, and before/after comparison.
> **Existing code:** `MinimumMomentLeveling`, `BurgessLeveling` in `core/resource_leveling.py`; RCPS tab with schedule + histogram in `gui/tabs/rcps_tab_edu.py`.
> **Decision:** Add educational sub-tab to existing RCPS tab.

| #   | Task                                 | What to Do                                                                                                                                                                                                                                                                                                               | Files                                             | Status |
| --- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- | ------ |
| 8.1 | Smoothing vs Constrained distinction | Add clear mode selector: **Resource Smoothing** (minimize peak within float, don't extend project) vs **Resource Constrained** (enforce limits, may extend project). Document the difference in tooltips and educational panel                                                                                           | `gui/tabs/rcps_tab_edu.py` — mode selector        | ✅     |
| 8.2 | Step-by-step walkthrough sub-tab     | **New sub-tab 3:** Animated/stepped walkthrough of the leveling algorithm. Show: (1) Initial resource histogram (before), (2) Each scheduling decision with explanation ("Activity X delayed by 2 periods because resource R exceeds limit"), (3) Final histogram (after). Slider or "Next Step"/"Previous Step" buttons | `gui/tabs/rcps_tab_edu.py` — new sub-tab          | ✅     |
| 8.3 | Leveling step recorder               | Modify `MinimumMomentLeveling` and `BurgessLeveling` to emit step-by-step events: which activity was considered, what decision was made, what the resource profile looks like after each step. Store as list of `LevelingStep` dataclasses                                                                               | `core/resource_leveling.py` — add step recording  | ✅     |
| 8.4 | Before/after comparison              | Side-by-side histograms: left = original schedule resources, right = leveled schedule. Metrics comparison: RMS deviation, peak usage, project duration (delta if constrained extended it)                                                                                                                                | `gui/tabs/rcps_tab_edu.py` — comparison panel     | ✅     |
| 8.5 | Leveling metrics panel               | Display: Minimum Moment value (before/after), Burgess metric, Resource utilization %, Peak-to-average ratio. Explain what each metric means                                                                                                                                                                              | Same sub-tab — metrics section                    | ✅     |
| 8.6 | Resource leveling worked solutions   | Step-by-step educational content: (1) What is resource leveling, (2) Smoothing vs Constrained, (3) Minimum Moment algorithm explanation, (4) Burgess algorithm explanation, (5) When to use which                                                                                                                        | `core/leveling_step_generator.py` (NEW)           | ✅     |
| 8.7 | Resource leveling "Try It Yourself"  | Small project (5 activities, 1 resource); student manually adjusts start times to reduce peak; app validates total moment reduction                                                                                                                                                                                      | `gui/tabs/rcps_tab_edu.py` — practice frame       | ✅     |
| 8.8 | Resource leveling demo file          | `data/demos/v2/resource_leveling_demo.json` — project designed to show clear leveling benefit (high initial peak, ample float)                                                                                                                                                                                           | `data/demos/v2/resource_leveling_demo.json` (NEW) | ✅     |
| 8.9 | Unit tests — leveling education      | Test step recorder output, before/after metrics computation, smoothing-only mode (verify project not extended)                                                                                                                                                                                                           | `tests/test_leveling_education.py` (NEW)          | ✅     |

---

## ✅ Phase 9 — Strategic Visualizations (SWOT Bubble Chart + PESTEL Radar Upgrade) — COMPLETE

> **Goal:** Enhance the SWOT and PESTEL tabs with richer visualizations. SWOT gets a 4D bubble chart on a 2×2 grid; PESTEL's existing radar gets hover + bubble overlay. No rebuilds — extends existing tabs.
> **Existing code:** `SWOTFactor` with `weight` field in `core/swot_models_edu.py`; SWOT 2×2 treeview grid in `gui/tabs/swot_tab_edu.py`; PESTEL radar chart + category filter in `gui/tabs/pestel_tab_edu.py`; `PESTELFactor` with `impact_score`/`probability` in `core/pestel_models_edu.py`.
> **Constraint:** No rebuilds — enhance existing code only.

| #   | Task                                    | What to Do                                                                                                                                                                                                                                                                                                                            | Files                                                                | Status |
| --- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------ |
| 9.1 | Extend `SWOTFactor` model               | Add `impact_score: float` (1–5, drives bubble size) and `likelihood: float` (0–1, drives color intensity) fields. Update `to_dict()`/`from_dict()`, `validate()`. Backward-compatible defaults for existing data                                                                                                                      | `core/swot_models_edu.py`                                            | ✅     |
| 9.2 | SWOT bubble chart — 2×2 grid            | Matplotlib scatter in existing tab. 4 quadrants: **Strengths** (upper-left), **Weaknesses** (upper-right), **Opportunities** (lower-left), **Threats** (lower-right). Each factor = 1 bubble. Bubble size ∝ `impact_score`. Color = green→red gradient (`matplotlib.colors.LinearSegmentedColormap`). Quadrant labels + divider lines | `gui/tabs/swot_tab_edu.py` — add chart panel below existing 2×2 grid | ✅     |
| 9.3 | SWOT dropdown filter                    | `ttk.Combobox` to switch between 3 visualization modes: (1) **Impact vs Weight** (default — X=weight, Y=impact, size=likelihood), (2) **Strategic Fit** (X=impact, Y=likelihood, size=weight), (3) **Priority Matrix** (X=likelihood, Y=impact, size=weight). Chart redraws on selection                                              | `gui/tabs/swot_tab_edu.py` — filter in chart toolbar                 | ✅     |
| 9.4 | SWOT bubble hover tooltips              | `mpl_connect('motion_notify_event')`: hover over bubble → annotation with factor text, category, weight, impact, likelihood. Annotation follows cursor, hides on mouse-out                                                                                                                                                            | `gui/tabs/swot_tab_edu.py` — event handler                           | ✅     |
| 9.5 | SWOT chart export                       | "Export PNG" / "Export SVG" buttons for the bubble chart (extend existing export toolbar row)                                                                                                                                                                                                                                         | `gui/tabs/swot_tab_edu.py` — export buttons                          | ✅     |
| 9.6 | PESTEL radar interactivity              | Upgrade existing radar: (1) Add hover tooltip showing factor count + avg exposure per axis, (2) Click-to-filter — clicking a radar axis sets the category filter in the table below                                                                                                                                                   | `gui/tabs/pestel_tab_edu.py` — radar event handlers                  | ✅     |
| 9.7 | PESTEL bubble overlay                   | Toggle button "Show Bubbles" — overlays scatter points on the radar chart. Each bubble = 1 factor, size ∝ exposure, positioned along the category axis at distance = impact_score. Allows seeing individual factors vs aggregated radar                                                                                               | `gui/tabs/pestel_tab_edu.py` — bubble overlay toggle                 | ✅     |
| 9.8 | SWOT demo file with scored factors      | `data/demos/v2/swot_scored_demo.json` — 16 factors (4 per quadrant) with impact_score + likelihood values, designed to show clear clustering patterns in the bubble chart                                                                                                                                                             | `data/demos/v2/swot_scored_demo.json` (NEW)                          | ✅     |
| 9.9 | Unit tests — SWOT bubble + PESTEL radar | Test model extensions (backward compat, validation), chart data generation (correct quadrant placement, color mapping), filter mode switching, demo file loading                                                                                                                                                                      | `tests/test_strategic_viz.py` (NEW)                                  | ✅     |

---

## ✅ Phase 9B — UX Bug Fixes & Demo Loaders — COMPLETE

> **Goal:** Fix 5 reported UX issues: Plotly Gantt readability, matplotlib canvas positioning, crashing iteration limits, financial demo loader paths, and WBS sample data. All fixes are non-breaking and improve existing tabs.
> **Priority order:** Crashing iterations (trivial) → Financial demo (unblocks tab) → Canvas centering (fixes 3 tabs) → Plotly Gantt (UX) → WBS sample (new content).

| #    | Task                                         | What to Do                                                                                                                                                                                                                                                                                                                                                                                                                                               | Files                                                                                                                            | Status |
| ---- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 9B.1 | Crashing max iterations 300 → 1500           | Change hardcoded `max_iterations = 300` to `1500` in **all** crashing-related files. Two changes in `crashing_tab_gui.py` (line 81 runtime value + line 1032 UI default). Four default-parameter changes in `project_crashing_core.py` (lines 80, 99, 468, 751). Two changes in `rcps_crashing_tab_gui.py` (line 632 default param + line 891 hardcoded call). One in `cpm_analyzer.py` (line 401 default param). **9 occurrences total across 5 files** | `gui/tabs/crashing_tab_gui.py`, `gui/tabs/project_crashing_core.py`, `gui/tabs/rcps_crashing_tab_gui.py`, `core/cpm_analyzer.py` | ✅     |
| 9B.2 | Financial demo — fix path resolution         | Both `_load_demo()` methods in `financial_tab_edu.py` use `os.path.dirname(__file__)` + relative `../../..` which fails when installed as a package. Add robust path resolution: try `__file__`-relative first, fall back to `importlib.resources` or CWD-relative search. Also add `try/except` with traceback logging to surface silent errors. Verify `factor_scoring_demo.json` exists and structure matches code                                    | `gui/tabs/financial_tab_edu.py`                                                                                                  | ✅     |
| 9B.3 | Canvas centering — fix "higher and right"    | In `ScrollableMatplotlibFrame`: when `_auto_fit` is True, center the chart in the viewport instead of anchoring at `(0,0)` NW. Add `self.after_idle(self._resize_to_viewport)` inside `fit_to_viewport()` to handle Tk idle timing on first render. Ensure all 3 diagram tabs (network, PERT, Gantt) show the full diagram centered on initial load, with zoom/pan available via toolbar                                                                 | `gui/widgets/scrollable_mpl_frame.py`, `gui/tabs/network_tab.py`, `gui/tabs/pert_diagram_tab.py`, `gui/tabs/gantt_tab_edu.py`    | ✅     |
| 9B.4 | Plotly Gantt — improve Y-axis & initial view | Cap figure height at `min(900, ...)` so chart fits in browser viewport. Use `"ID – Name"` labels (truncated to 30 chars) on Y-axis instead of bare IDs. Set initial X-axis range to `[0, max_EF]` so full chart is visible. Add `config={'scrollZoom': True}` to `write_html()`. Increase left margin for longer labels                                                                                                                                  | `utils/interactive_network.py`                                                                                                   | ✅     |
| 9B.5 | WBS bigger sample + Load Demo button         | Create `data/demos/v2/wbs_demo.json` with 30–40 nodes: 1 project root, 5 Level-1 phases (Initiation, Planning, Execution, Testing, Deployment), 3–4 work packages per phase (Level 2), 2–3 tasks per package (Level 3 leaves). Mix of statuses, realistic durations/costs, named responsibles. Add `to_dict()`/`from_dict()` to `WBSTree` if missing. Add "📂 Load Demo" button + `_load_demo()` to `wbs_tab_edu.py`                                     | `data/demos/v2/wbs_demo.json` (NEW), `gui/tabs/wbs_tab_edu.py`, `core/wbs_models_edu.py`                                         | ✅     |
| 9B.6 | Unit tests — UX fixes                        | Test: crashing accepts 1500 iterations without error, financial demo files load & parse correctly (both sub-tabs), WBS demo file loads into `WBSTree`, interactive Gantt generates valid HTML with capped height. Canvas centering is visual — manual smoke test only                                                                                                                                                                                    | `tests/test_ux_fixes.py` (NEW)                                                                                                   | ✅     |

---

## ✅ Phase 9C — UX Polish Wave 2 (10 Reported Issues) — COMPLETE

> **Goal:** Fix 10 UX issues reported during QA testing. Covers chart display problems (Y-stretch, clipped titles/legends, whitespace), data pipeline gaps (histogram not wired to RCPS data, resource usage placeholder), missing interactivity (probability chart not reactive, PESTEL bubbles ignore filter, no WBS interactive view), missing info panels (RCPS crashing durations), UI layout bugs (Refresh button misplaced), and demo data gaps (financial demos too simple, Factor Scoring missing 0-1/Factor model demos).
> **Existing code:** All chart tabs use `ScrollableMatplotlibFrame` with `subplots_adjust(top=0.95, bottom=0.02)` and `set_title(pad=20)`. Probability tab uses button-driven calculation with no `trace_add`. RCPS histograms read EVM data only. PESTEL bubbles iterate all 6 categories unconditionally. WBS has Tkinter Canvas only — no Plotly export.
> **Priority order:** Trivial (PESTEL filter, Results CP) → Small (RCPS info, Probability reactive, Gantt layout) → Medium (Network, PERT, WBS interactive, Financial demos) → Large (Resources 3 sub-fixes).
> **Constraint:** Non-breaking. No architecture changes. Reuse existing patterns (`interactive_network.py` Plotly → browser for WBS).

### Issue Inventory & Root Causes

| #     | Tab                | Symptom                                                                                                                                      | Root Cause (verified line #)                                                                                                                                                                                                                                               | Effort  | Status  |
| ----- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 9C.1  | Results            | Critical path shown twice — in Project Summary AND in separate Critical Path section below                                                   | `self.critical_path_label` at L68 in `create_summary_frame()` duplicates the dedicated `create_critical_path_frame()` at L113                                                                                                                                              | Trivial | ✅ Done |
| 9C.2  | Network Diagram    | Y-stretched, title invisible, END node hidden behind white bar, legend barely visible                                                        | `subplots_adjust(top=0.95, bottom=0.02)` at L394 leaves only 5% for title with `pad=20` at L389; legend `loc='lower right'` at L503 clipped by `bottom=0.02`; `y_spacing=4.0` at L406 distorts small projects                                                              | Medium  | ✅ Done |
| 9C.3  | PERT Diagram       | Y-stretched, title invisible, task name overflows semicircle cell                                                                            | `subplots_adjust(top=0.95, bottom=0.02)` at L417; `pad=20` at L250; `y_spacing=4.0` at L430; node ID text centered in `semicircle_width = width/3` at L543 — long IDs overflow; `wrap_activity_name()` at L656 has `max_chars_per_line=12` parameter but **never uses it** | Medium  | ✅ Done |
| 9C.4  | Gantt Chart        | Y-stretched, title/x-axis invisible, large whitespace left, Refresh button on separate row from Save Chart                                   | `subplots_adjust(top=0.95, bottom=0.06)` at L193; `pad=20` at L314; `left_margin=0.22` hardcoded for ≤50 activities at L192; Refresh on `toolbar2` (L118) but Save Chart on `button_frame` (L107) — different parent widgets                                               | Small   | ✅ Done |
| 9C.5  | Financial Analysis | Demo samples too simple (only 2 short scenarios); Factor Scoring has only Weighted model demo, missing 0-1 and Factor model demos            | `financial_demo.json` has 2 basic scenarios; `factor_scoring_demo.json` only contains `"model": "Weighted"` entries                                                                                                                                                        | Medium  | ✅ Done |
| 9C.6  | Resources (RCPS)   | Histogram Refresh reads EVM data not RCPS; Resource Usage chart always shows placeholder; Resource Leveling content overflows without scroll | `_draw_histograms()` at L368 reads `self.state.evm_project.periods`; resource usage at L416 is hardcoded placeholder text; `_build_leveling_tab()` uses plain `ttk.Frame` with no scroll mechanism                                                                         | Large   | ✅ Done |
| 9C.7  | Probability PERT   | Chart only updates on button click — dashed line does not move when user types new target duration                                           | `_target_dur_var` (L94) and `_target_prob_var` (L105) have **zero** `trace_add()` calls; `_draw_distribution()` already reads the var at L303 but is never triggered on change                                                                                             | Small   | ✅ Done |
| 9C.8  | RCPS Crashing      | No info showing original CPM and RCPS durations before crashing run                                                                          | `RCPSCrashingTabGUIManager` has no `on_tab_selected()` and no duration info panel; `_update_interface_for_rcps()` at L170 only renames LabelFrame titles                                                                                                                   | Small   | ✅ Done |
| 9C.9  | PESTEL             | Bubble overlay shows ALL 6 category bubbles regardless of category filter selection                                                          | Bubble loop at L203 iterates `for i, c in enumerate(categories)` unconditionally; `_cat_filter` (L64) is checked only for the factor table, not the radar/bubble overlay                                                                                                   | Trivial | ✅ Done |
| 9C.10 | WBS                | No interactive browser-based view — canvas diagram is Tkinter-only                                                                           | No `plotly` import; toolbar has no "Interactive View" button; existing `interactive_network.py` pattern (Plotly → `write_html()` → `webbrowser.open()`) is proven but not applied to WBS                                                                                   | Medium  | ✅ Done |

### Detailed Fix Specifications

---

#### 9C.1 — Results Tab: Remove Duplicate Critical Path (Trivial)

**File:** `gui/tabs/results_tab.py`

**Problem:** `create_summary_frame()` creates a `critical_path_label` at L68 inside Project Summary. Below that, `create_critical_path_frame()` at L113 creates a full scrollable `tk.Text` widget for the critical path. Both display the same data — the label is redundant and clips long paths (no wrapping).

**Fix:**

1. Delete L68–69: `self.critical_path_label = ttk.Label(...)` and its `.pack()`
2. Delete L212: `self.critical_path_label.config(text=f"Critical Path: {cp_text}")` in `update_summary()`
3. Delete L338: `self.critical_path_label.config(text="Critical Path: --")` in `clear_results()`
4. Keep `create_critical_path_frame()` and its `self.critical_path_text` widget unchanged

**Risk:** None — the dedicated section already shows the data with better formatting.

---

#### 9C.2 — Network Diagram: Y-Stretch, Title, Legend, END Node (Medium)

**File:** `gui/tabs/network_tab.py`

**Sub-fixes:**

| #   | What                         | Current                  | New                                  | Lines              |
| --- | ---------------------------- | ------------------------ | ------------------------------------ | ------------------ |
| a   | Title padding                | `pad=20`                 | `pad=5`                              | L389 (`set_title`) |
| b   | AON `subplots_adjust` top    | `top=0.95`               | `top=0.88`                           | L394               |
| c   | AON `subplots_adjust` bottom | `bottom=0.02`            | `bottom=0.10`                        | L394               |
| d   | AOA `subplots_adjust` bottom | `bottom=0.02`            | `bottom=0.10`                        | L857               |
| e   | AON legend location          | `loc='lower right'`      | `loc='upper right'`                  | L503               |
| f   | AOA legend location          | `loc="lower right"`      | `loc="upper right"`                  | L842               |
| g   | Y-spacing (≤50 nodes)        | `y_sp = 4.0`             | `y_sp = 2.5`                         | L406               |
| h   | Y-axis padding               | `set_ylim(y_min, y_max)` | `set_ylim(y_min - 1.5, y_max + 1.5)` | L392, L855         |

**Why each change:**

- (a–c): `top=0.95` + `pad=20` pushes the title above the figure area; `bottom=0.02` eliminates room for the legend
- (d): AOA suffers the same bottom clipping
- (e–f): Legend moves to upper-right where there's always white space (the start node is at the left)
- (g): `y_spacing=4.0` makes the diagram 4 units tall per level — with auto-fit, this stretches vertically; 2.5 keeps levels distinct without distortion
- (h): If END node is exactly at `y_max`, the node circle radius (typically ~1.0) extends below the limit, clipping it

---

#### 9C.3 — PERT Diagram: Y-Stretch, Title, Name Overflow (Medium)

**File:** `gui/tabs/pert_diagram_tab.py`

**Sub-fixes:**

| #   | What                     | Current                                                                                                     | New                                                                   | Lines    |
| --- | ------------------------ | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------- |
| a   | Title padding            | `pad=20`                                                                                                    | `pad=5`                                                               | L250     |
| b   | `subplots_adjust` top    | `top=0.95`                                                                                                  | `top=0.88`                                                            | L417     |
| c   | `subplots_adjust` bottom | `bottom=0.02`                                                                                               | `bottom=0.10`                                                         | L417     |
| d   | Y-spacing (≤50 nodes)    | `y_sp = 4.0`                                                                                                | `y_sp = 2.5`                                                          | L430     |
| e   | Node ID text overflow    | Full ID drawn at center of `semicircle_width = width/3`                                                     | Truncate: `node_display = node[:8] + "…" if len(node) > 8 else node`  | L618     |
| f   | Activity name wrapping   | `wrap_activity_name()` at L656 has `max_chars_per_line=12` but never enforces it — each word becomes a line | Implement actual char-limit wrapping: `textwrap.fill(name, width=12)` | L656–659 |

**Why (e–f):** The semicircle cell is ~33% of node width. For a `width` of ~3.0 (typical), `semicircle_width ≈ 1.0` — only ~8 chars fit at `fontsize=8`. The `wrap_activity_name()` method splits words but doesn't enforce the 12-char limit, so "Implementation" becomes one unbroken line.

---

#### 9C.4 — Gantt Chart: Y-Stretch, Title, Whitespace, Refresh Button (Small)

**File:** `gui/tabs/gantt_tab_edu.py`

**Sub-fixes:**

| #   | What                       | Current                         | New                                                                                                            | Lines    |
| --- | -------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------- |
| a   | Title padding              | `pad=20`                        | `pad=5`                                                                                                        | L314     |
| b   | `subplots_adjust` top      | `top=0.95`                      | `top=0.90`                                                                                                     | L193     |
| c   | `left_margin` for ≤50 acts | hardcoded `0.22`                | Dynamic: `min(0.30, max(0.08, max_label_chars * 0.009 + 0.02))` where `max_label_chars` = longest y-tick label | L192     |
| d   | Move Refresh button        | `toolbar2` (L118, separate row) | `button_frame` (L107, same row as Save Chart)                                                                  | L116–119 |

**Why (c):** `left_margin=0.22` reserves 22% of figure width for labels. With 6-char IDs like "A", "B", "C" this wastes space. With 20-char names it may be too little. Dynamic computation based on actual max label length is more robust.

**Why (d):** Users expect Refresh near Save Chart. The current 2-row layout puts Refresh in a different visual group, making it hard to find.

---

#### 9C.5 — Financial Analysis: Richer Demos + Factor Scoring Models (Medium)

**Files:** `data/demos/v2/financial_demo.json`, `data/demos/v2/factor_scoring_demo.json`

**Sub-fixes:**

**5a — `financial_demo.json`:** Replace current 2-scenario file with 3 more complex scenarios:

1. **Capital Investment** — 10-period cash flow with initial outlay, ramp-up, peak, and decline. Mixed positive/negative interim flows → interesting NPV/IRR
2. **Lease vs Buy** — Two mutually exclusive alternatives with different cost structures, designed so NPV comparison shows non-obvious winner
3. **Digital Product** — High initial cost, low recurring, exponential revenue growth → high IRR scenario

**5b — `factor_scoring_demo.json`:** Add 2 additional demo entries:

1. `"model": "01"` — Binary (0-1) scoring: 5 criteria × 4 alternatives, each cell is 0 or 1, weights sum to 1.0
2. `"model": "Factor"` — Unweighted factor model: 6 criteria × 3 alternatives, scores 1–10, no weights (equal weight implied)

Keep existing `"model": "Weighted"` entry unchanged.

---

#### 9C.6 — Resources: Histogram Data, Resource Usage, Leveling Scroll (Large)

**File:** `gui/tabs/rcps_tab_edu.py`

Three sub-fixes:

**6a — Wire RCPS data to `_draw_histograms()`:**

- In `_run_rcps()` (after L193 where `self._rcps_table_data = rcps_table`), compute per-period resource totals:
  ```python
  profile = {}
  for _, row in rcps_table.iterrows():
      aid = row.get('id', '')
      if not aid or aid in ('RA', 'RS'):
          continue
      es = row.get('actual_start', row.get('early_start', 0))
      dur = row.get('duration', 0)
      res = row.get('resource_demand', row.get('resource', 0))
      for t in range(int(es), int(es + dur)):
          profile[t] = profile.get(t, 0) + res
  self._rcps_resource_profile = profile
  ```
- Call `self._draw_histograms()` at the end of `_run_rcps()`

**6b — Fix `_draw_histograms()` Resource Usage section (L416–422):**

- Replace the hardcoded placeholder text block with:
  ```python
  if hasattr(self, '_rcps_resource_profile') and self._rcps_resource_profile:
      periods_r = sorted(self._rcps_resource_profile.keys())
      usage_vals = [self._rcps_resource_profile[t] for t in periods_r]
      ax2.bar(periods_r, usage_vals, color="#3498db", alpha=0.8, label="Resource Usage")
      ax2.axhline(self._resource_limit, color='#e74c3c', linestyle='--',
                  linewidth=1.5, label=f"Limit = {self._resource_limit}")
      ax2.set_xlabel("Period")
      ax2.set_ylabel("Resource Units")
      ax2.legend(fontsize=8)
  else:
      ax2.text(0.5, 0.5, "Resource usage data requires RCPS analysis.\nRun RCPS analysis first.",
               ha="center", va="center", fontsize=11, color="grey", transform=ax2.transAxes)
  ```

**6c — Leveling Tab Vertical Scroll:**

- In `_build_leveling_tab()`, wrap the outer `ttk.Frame` in a scrollable `tk.Canvas` + `ttk.Scrollbar`:
  ```python
  scroll_canvas = tk.Canvas(self._leveling_frame)
  vsb = ttk.Scrollbar(self._leveling_frame, orient=tk.VERTICAL, command=scroll_canvas.yview)
  outer = ttk.Frame(scroll_canvas)
  scroll_canvas.create_window((0, 0), window=outer, anchor="nw")
  outer.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
  scroll_canvas.configure(yscrollcommand=vsb.set)
  vsb.pack(side=tk.RIGHT, fill=tk.Y)
  scroll_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
  ```
- Add mouse-wheel binding for smooth scrolling

---

#### 9C.7 — Probability PERT: Live-Reactive Chart (Small)

**File:** `gui/tabs/probability_tab_edu.py`

**Problem:** `_target_dur_var` (L94) and `_target_prob_var` (L105) have no `trace_add` calls. Chart only updates on button click. `_draw_distribution()` already reads `self._target_dur_var.get()` at L303 — it just needs to be triggered.

**Fix:**

1. After var creation (near L106), add:
   ```python
   self._target_dur_var.trace_add('write', lambda *_: self._safe_redraw_pert())
   self._target_prob_var.trace_add('write', lambda *_: self._safe_redraw_pert())
   ```
2. Add guard method:
   ```python
   def _safe_redraw_pert(self):
       if not hasattr(self, '_pert_fig') or self._pert_fig is None:
           return
       try:
           self._draw_pert_chart()
       except Exception:
           pass  # Ignore non-numeric intermediate states
   ```
3. In `_draw_cumulative()` (L318), add target-duration vertical line:
   ```python
   target = self._target_dur_var.get()
   if target > 0:
       ax.axvline(target, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
       ax.annotate(f'd={target:.1f}', xy=(target, 0.5), fontsize=8, color='red')
   ```

---

#### 9C.8 — RCPS Crashing: Show Durations Before Running (Small)

**File:** `gui/tabs/rcps_crashing_tab_gui.py`

**Problem:** No `on_tab_selected()` exists. No info panel shows CPM/RCPS durations.

**Fix:**

1. In `__init__` (after L40), create an info banner using `tk.StringVar` + `ttk.Label` at the top of the tab:
   ```python
   self._duration_info_var = tk.StringVar(value="CPM Duration: — | RCPS Duration: — | Run RCPS analysis first")
   # Insert banner label into the tab's controls area
   ```
2. Add `on_tab_selected()` method:
   ```python
   def on_tab_selected(self):
       cpm_dur = "—"
       rcps_dur = "—"
       analyzer = getattr(self.app, 'cpm_analyzer', None)
       if analyzer:
           cpm_dur = f"{analyzer.project_duration:.0f}"
       if self.rcps_tab and hasattr(self.rcps_tab, '_rcps_table_data') and self.rcps_tab._rcps_table_data is not None:
           table = self.rcps_tab._rcps_table_data
           ef_vals = [r.get('actual_start', 0) + r.get('duration', 0)
                      for _, r in table.iterrows()
                      if r.get('id', '') not in ('RA', 'RS', '')]
           rcps_dur = f"{max(ef_vals):.0f}" if ef_vals else "—"
       self._duration_info_var.set(
           f"Original CPM Duration: {cpm_dur} periods  |  "
           f"RCPS Duration: {rcps_dur} periods")
   ```

---

#### 9C.9 — PESTEL: Filter Bubbles by Selected Category (Trivial)

**File:** `gui/tabs/pestel_tab_edu.py`

**Problem:** Bubble overlay loop at L203 iterates `for i, c in enumerate(categories)` over all 6 categories. The `_cat_filter` var (L64) is only checked for the table.

**Fix:** Add filter guard inside the bubble loop (L204):

```python
if self._show_bubbles_var.get():
    cat_filter = self._cat_filter.get()          # ← NEW
    for i, c in enumerate(categories):
        if cat_filter != "All" and c.value != cat_filter:   # ← NEW
            continue                                         # ← NEW
        factors = analysis.by_category(c)
        ...
```

`_refresh_all()` already calls `_draw_radar()` when filter changes (confirmed: radio buttons have `command=self._refresh_all`), so no additional wiring needed.

---

#### 9C.10 — WBS: Interactive Plotly Sunburst View (Medium)

**File:** `gui/tabs/wbs_tab_edu.py`

**Problem:** WBS uses Tkinter Canvas only. No browser-based interactive view. The `interactive_network.py` pattern (Plotly → `write_html()` → `webbrowser.open()`) is established in the project but not applied to WBS.

**Fix:**

1. Add imports: `import webbrowser, tempfile`
2. Add "🌐 Interactive View" button to toolbar (next to Export CSV):
   ```python
   ttk.Button(toolbar, text="🌐 Interactive View",
              command=self._open_interactive_view).pack(side=tk.LEFT, padx=2)
   ```
3. Add `_open_interactive_view()` method:
   - Check `self.state.wbs_tree.node_count() > 0`; if empty show `messagebox.showinfo`
   - Build `plotly.graph_objects.Sunburst` from WBS tree: `ids`, `labels`, `parents`, `values` (costs or durations), `customdata` (WBS codes)
   - Set `branchvalues="total"`, colorscale based on `WBS_STATUS_COLOURS`
   - `fig.write_html(tmpfile)` → `webbrowser.open(tmpfile)`
   - Wrap Plotly import in `try/except ImportError` with user-friendly message

### Files To Modify

| File                                     | Issues |
| ---------------------------------------- | ------ |
| `gui/tabs/results_tab.py`                | 9C.1   |
| `gui/tabs/network_tab.py`                | 9C.2   |
| `gui/tabs/pert_diagram_tab.py`           | 9C.3   |
| `gui/tabs/gantt_tab_edu.py`              | 9C.4   |
| `data/demos/v2/financial_demo.json`      | 9C.5   |
| `data/demos/v2/factor_scoring_demo.json` | 9C.5   |
| `gui/tabs/rcps_tab_edu.py`               | 9C.6   |
| `gui/tabs/probability_tab_edu.py`        | 9C.7   |
| `gui/tabs/rcps_crashing_tab_gui.py`      | 9C.8   |
| `gui/tabs/pestel_tab_edu.py`             | 9C.9   |
| `gui/tabs/wbs_tab_edu.py`                | 9C.10  |

---

## ✅ Phase 10 — Z-Score Table & Probability Enhancements — COMPLETE

> **Goal:** Add a Z-score lookup table (from `ztable_stats.csv`) to **both** the Probability tab and Three-Point Estimates tab. Student enters Z → table highlights the path (row + column header → intersection cell) to the probability. Enter probability → reverse-highlights the Z value. Data-linked to calculator inputs so changes update the highlight in real time. "📊 Show All Calculations" button (UG mode) added to both tabs.
> **Existing code:** `ProbabilityTabEdu` with PERT Analysis + Monte Carlo sub-tabs, `scipy.stats.norm`, P50/P80/P90/P95 calculator in `gui/tabs/probability_tab_edu.py`. `pert_steps()` in `core/step_generators_edu.py`. `WorkedSolutionWindow` reusable widget in `gui/widgets/worked_solution_window.py`. `ztable_stats.csv` with Z from −3.9 to +3.9 (tenths as rows, hundredths as columns, semicolon-delimited).
> **Constraint:** Z-table from CSV (not computed), path highlighting is the core UX. In both tabs. UG mode only for calculations button.

| #    | Task                                 | What to Do                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Files                                                                                         | Status |
| ---- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------ |
| 10.1 | Z-table data loader                  | Utility function `load_ztable(csv_path) → dict` that parses `ztable_stats.csv` (semicolon-delimited). Returns lookup structure: `{(row_z_str, col_hundredth_str): probability}` plus a reverse index: sorted list of `(probability, z_row, z_col)` for nearest-match inverse lookup. Ship CSV as package data                                                                                                                                                                                     | `core/ztable_loader.py` (NEW) + `ztable_stats.csv` (EXISTS — ship as data)                    | ✅     |
| 10.2 | `ZScoreTableWidget` — reusable       | Reusable Tkinter widget (`ttk.Frame`): renders the full Z-table as a scrollable grid of `tk.Label` cells. **Forward lookup:** student enters Z (e.g., 1.96) → widget highlights row Z=1.9 header in blue, column .06 header in blue, and the intersection cell (0.97500) in green. **Reverse lookup:** student enters probability (e.g., 0.975) → widget finds nearest cell, highlights it in green, traces path back to row/column headers in blue. Clear previous highlights on each new lookup | `gui/widgets/ztable_widget.py` (NEW)                                                          | ✅     |
| 10.3 | Z-table in Probability tab           | Add sub-tab 3 "Z-Score Table" to `ProbabilityTabEdu` notebook. Embeds `ZScoreTableWidget`. Input panel above: (1) "Z → Probability" entry + "Highlight" button, (2) "Probability → Z" entry + "Highlight" button. Below table: interpretation text (e.g., "Z = 1.96 → P(Z ≤ 1.96) = 0.9750 → 97.5% of values fall below this point")                                                                                                                                                              | `gui/tabs/probability_tab_edu.py` — new sub-tab                                               | ✅     |
| 10.4 | Z-table in Three-Point tab           | Add a "Z-Score Table" expandable section (or sub-tab) to the Three-Point Estimates tab. Same `ZScoreTableWidget` reuse. Purpose: when students compute project completion probability, they look up Z → probability directly in the same tab without switching                                                                                                                                                                                                                                    | `gui/tabs/three_point_tab_edu.py` — Z-table section                                           | ✅     |
| 10.5 | Data-linked reactive highlighting    | Wire Probability tab calculator inputs to the Z-table: when student changes "Target Duration" → compute Z = (d − μ) / σ automatically → Z-table widget highlights the path in real time. Uses `trace_add('write', ...)` on `DoubleVar`. Same linkage for Three-Point tab if project-level Z is computed                                                                                                                                                                                           | `gui/tabs/probability_tab_edu.py` + `gui/tabs/three_point_tab_edu.py` — trace bindings        | ✅     |
| 10.6 | Formula step display                 | Below the Z-table in Probability tab: formula panel showing Z = (d − μ_T) / σ_T with substituted values in bold. Step: "Z = (42 − 38) / 2.5 = 1.60 → P(T ≤ 42) = 0.9452 = 94.52%". Updates live as target duration changes                                                                                                                                                                                                                                                                        | `gui/tabs/probability_tab_edu.py` — formula label panel                                       | ✅     |
| 10.7 | "📊 Show All Calculations" (UG mode) | Add to Probability PERT sub-tab + Three-Point tab. Opens existing `WorkedSolutionWindow` (no new widget) pre-populated with: all activity Te/σ² values, critical path identification, project μ and σ, Z computation, table lookup result, and interpretation. UG-only visibility (hidden in PG mode via `set_mode()`)                                                                                                                                                                            | `gui/tabs/probability_tab_edu.py` + `gui/tabs/three_point_tab_edu.py` — extend `pert_steps()` | ✅     |
| 10.8 | Unit tests — Z-table                 | Test CSV parsing (known values: Z=0.00→0.5000, Z=1.96→0.9750, Z=−1.645→~0.05), widget highlight logic (correct row/col selection), reverse lookup accuracy, formula output string generation                                                                                                                                                                                                                                                                                                      | `tests/test_ztable.py` (NEW)                                                                  | ✅     |

---

## ✅ Phase 11 — Cross-Tab Polish (Interactive Charts + Calculations Button + WBS Cost View) — COMPLETE

> **⚠️ Notes from implementation — the tasks below were not as-described:**
>
> - **11.5** targets `gui/tabs/crashing_tab_edu.py`. That file is a dead 16-line
>   "Coming Soon" stub that `main_window_edu.py` does not import. The live tab is
>   `crashing_tab.py` → `crashing_tab_gui.py`; the button went there.
> - **11.6** was not "add the button" — it already existed on **8 of 9** tabs under
>   **four different labels**, and the UG-only gating existed on only 2 (EVM,
>   Probability). The work was standardizing to `📊 Show All Calculations` and
>   wiring `set_mode` on the other 7. `tests/test_cross_tab_polish.py` now pins the
>   label so it can't drift again.
>   - Found + fixed: `crashing_steps()` derived cost slope as `(CC − NC)/(ND − CD)`,
>     which assumes costs are **totals**. This codebase stores **rates**
>     (`cost = crash_cost * crash_amount`; field `crash_cost_per_unit`), so the
>     worked solution would have taught wrong arithmetic. It now accepts a
>     `cost_slope` passthrough. It had **zero callers and zero tests** before.
>   - Found + fixed: the Crashing tab was absent from `main_window_edu.py`'s `tabs`
>     dict in **both** build paths, so it had never received a `set_mode` call.
> - **11.9** was half-built and **had never worked**: `_load_costs_from_estimation`
>   read `self.main_window` (a param `WBSTabEdu.__init__` did not accept), then
>   `mw._tabs` (the attribute is `mw.tabs`), then `result.items` / `.line_items`
>   (the real field is `breakdown`). Three independent faults; it always bailed on
>   the first. All fixed, plus the "Estimate from WBS" direction added.
> - **11.8** shipped as a render-mode toggle on the **existing** Treeview rather
>   than a new "secondary panel" — that widget already had the exact columns the
>   task lists, plus sorting. Same outcome, less surface.
>
> **Goal:** (1) Implement hybrid visualization upgrade (Option D: matplotlib static + Plotly interactive) across all chart tabs, (2) Add "📊 Show All Calculations" button (UG mode) to every remaining calculator tab, (3) Extend WBS with cost display mode + flat table view (UG educational requirement).
> **Existing code:** `ScrollableMatplotlibFrame` with `NavigationToolbar2Tk` in `gui/widgets/scrollable_mpl_frame.py`. Plotly already used for Gantt "Open Interactive" via `utils/interactive_network.py` (`generate_interactive_gantt()` → HTML → browser). `WBSNode.cost` field + `WBSAggregator` in `core/wbs_models_edu.py`. `WorkedSolutionWindow` in `gui/widgets/worked_solution_window.py`. All `*_step_generator.py` files produce step trees.
> **Decision:** **Option D — Hybrid** (matplotlib embedded for static quick-view + "🔍 Open Interactive" Plotly button that generates HTML and opens in browser). This extends the proven Gantt chart pattern to all tabs.
>
> **Viz Library Analysis:**
> | Approach | Where Currently Used | Interactivity | Embedded? |
> |---|---|---|---|
> | **Matplotlib** `FigureCanvasTkAgg` | All 15+ charts (EVM, RCPS, probability, risk, etc.) | Limited (zoom/pan via toolbar, no hover) | Yes — in Tkinter |
> | **Plotly** `fig.write_html()` | Gantt chart only | Full (hover, zoom, toggle, export) | No — opens in browser |
> | **PyVis** `net.show()` | Network diagram only | Full (drag, zoom, physics) | No — opens in browser |
>
> Option D keeps matplotlib for the embedded quick-view and adds a "🔍 Open Interactive" button that generates a Plotly HTML with full hover/zoom/toggle/export. One new utility function, zero architecture change. Already proven with `generate_interactive_gantt()`.

| #     | Task                                                 | What to Do                                                                                                                                                                                                                                                                                                                                                                                   | Files                                                             | Status |
| ----- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------ |
| 11.1  | `generate_interactive_chart()` utility               | Generic Plotly chart generator function: `generate_interactive_chart(chart_type, data, title, **kwargs) → html_path`. Supports chart types: `bar`, `scatter`, `histogram`, `heatmap`, `line`, `bubble`. Generates self-contained HTML with hover tooltips, zoom/pan, toggle series, PNG/SVG download button. Opens in default browser. Extends the existing `interactive_network.py` pattern | `utils/interactive_charts.py` (NEW)                               | ✅     |
| 11.2  | "🔍 Open Interactive" — RCPS & Resource Leveling     | Add "🔍 Open Interactive" button to RCPS histograms and Resource Leveling before/after charts. Button calls `generate_interactive_chart('histogram', ...)` → opens Plotly histogram in browser with full hover/zoom/toggle                                                                                                                                                                   | `gui/tabs/rcps_tab_edu.py` — interactive buttons                  | ✅     |
| 11.3  | "🔍 Open Interactive" — EVM & Financial charts       | Add to EVM dashboard S-curves and Financial cumulative cash flow chart. Plotly line/bar charts with hover showing period-by-period values                                                                                                                                                                                                                                                    | `gui/tabs/evm_tab_edu.py` + `gui/tabs/financial_tab_edu.py`       | ✅     |
| 11.4  | "🔍 Open Interactive" — Probability & Risk charts    | Add to Probability distribution/cumulative charts and Risk heat map. Plotly heatmap for risk matrix with cell hover showing risk IDs. Plotly distribution chart with shaded area + crosshair                                                                                                                                                                                                 | `gui/tabs/probability_tab_edu.py` + `gui/tabs/risk_tab_edu.py`    | ✅     |
| 11.5  | "🔍 Open Interactive" — SWOT bubble & Crashing       | Add to SWOT bubble chart (Plotly scatter with quadrant annotations) and Crashing cost trade-off chart (Plotly line with dual Y-axis)                                                                                                                                                                                                                                                         | `gui/tabs/swot_tab_edu.py` + `gui/tabs/crashing_tab_edu.py`       | ✅     |
| 11.6  | "📊 Show All Calculations" — all remaining tabs (UG) | For each calculator tab that has a `*_step_generator.py` and does NOT yet have the button (from Phase 10): add "📊 Show All Calculations" button visible in UG mode only. Opens `WorkedSolutionWindow` with the full step tree. Tabs: Financial, Factor Scoring, Cost Estimation, RACI validation, Resource Leveling, Crashing, EVM, Risk Assessment. No new widget — reuse existing         | Multiple `gui/tabs/*.py` + `core/*_step_generator.py`             | ✅     |
| 11.7  | WBS cost column display mode (UG)                    | Add "💰 Show Costs" toggle to WBS toolbar (UG-only via `set_mode()`). When active: tree list shows cost column prominently, canvas nodes display cost below name, summary nodes show rolled-up total (already computed by `WBSAggregator`), color-code nodes by cost magnitude (white→blue gradient)                                                                                         | `gui/tabs/wbs_tab_edu.py` — cost display toggle                   | ✅     |
| 11.8  | WBS flat table view (UG)                             | Add "📋 Table View" button to WBS toolbar (UG-only). Opens secondary panel with flat `Treeview` table: WBS Code, Name, Duration, Cost, Progress, Status, Responsible. Sortable columns. Complements the tree diagram for data-heavy analysis                                                                                                                                                 | `gui/tabs/wbs_tab_edu.py` — flat table panel                      | ✅     |
| 11.9  | WBS ↔ Cost Estimation link                           | "Estimate from WBS" button on WBS tab: collects all leaf-node costs → opens Cost Estimation tab pre-populated with bottom-up data. Reverse: "Load WBS Costs" button on Cost Estimation bottom-up method pulls from WBS tree                                                                                                                                                                  | `gui/tabs/wbs_tab_edu.py` + `gui/tabs/cost_estimation_tab_edu.py` | ✅     |
| 11.10 | WBS top-down allocation                              | In cost display mode: right-click summary node → "Allocate Budget" → enter total → distributes proportionally to children (by existing cost ratios, or equally if no costs set). Enables top-down estimation workflow                                                                                                                                                                        | `gui/tabs/wbs_tab_edu.py` — context menu action                   | ✅     |
| 11.11 | Unit tests — cross-tab polish                        | Test `generate_interactive_chart()` output (valid HTML, correct chart type), WBS cost toggle, flat table population, WBS↔Cost Estimation data transfer, top-down allocation math, "Show All Calculations" button presence in UG mode / hidden in PG mode                                                                                                                                     | `tests/test_cross_tab_polish.py` (NEW)                            | ✅     |

---

## Phase 12 — Web Porting (Angular)

> **Goal:** Port all new desktop features to the Angular web app.
> **Decision:** Desktop first; web porting follows after all desktop features are stable.
> **Scope:** Port Phases 2–11 features to Angular standalone components with D3.js charts.

| #     | Task                                     | What to Do                                                                                                              | Files                                         | Status |
| ----- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------ |
| 12.1  | Three-Point Estimates component          | Angular standalone component with reactive forms for O/M/P input, D3.js line chart, worked solution accordion           | `web/src/app/features/three-point/` (NEW)     | ⬜     |
| 12.2  | Financial Analysis component             | Sub-routed component with Financial Calculators + Factor Scoring child components. Reactive forms, D3.js bar charts     | `web/src/app/features/financial/` (NEW)       | ⬜     |
| 12.3  | RACI Matrix component                    | Editable grid component (virtual scroll for large matrices), color-coded cells, validation messages                     | `web/src/app/features/raci/` (NEW)            | ⬜     |
| 12.4  | Cost Estimation component                | 7-method tabbed component with dynamic forms per technique, D3.js comparison chart                                      | `web/src/app/features/cost-estimation/` (NEW) | ⬜     |
| 12.5  | Risk Assessment & Response components    | Extend existing risk feature: add assessment matrix (D3.js heat map), response planning form, effectiveness dashboard   | `web/src/app/features/risk/` (extend)         | ⬜     |
| 12.6  | AOA Network component                    | vis.js AOA renderer, mode toggle, converter integration                                                                 | `web/src/app/features/network/` (extend)      | ⬜     |
| 12.7  | Resource Leveling walkthrough component  | Step-by-step animation with D3.js histograms, before/after comparison                                                   | `web/src/app/features/resources/` (extend)    | ⬜     |
| 12.8  | Strategic viz components (SWOT + PESTEL) | SWOT bubble chart (D3.js scatter with quadrants), PESTEL interactive radar. Port Phase 9 desktop features               | `web/src/app/features/strategic/` (NEW)       | ⬜     |
| 12.9  | Z-Score table component                  | Reusable Angular Z-table with path highlighting, used in Probability and Three-Point components. Port Phase 10 features | `web/src/app/shared/ztable/` (NEW)            | ⬜     |
| 12.10 | Interactive Plotly charts (web native)   | Replace desktop Plotly-in-browser pattern with embedded Plotly.js components. Port Phase 11 interactive chart features  | Multiple feature components                   | ⬜     |
| 12.11 | Navigation refactor for tab groups       | Angular router restructure: `/schedule/*`, `/cost/*`, `/risk/*`, `/strategic/*` with collapsible sidebar navigation     | `web/src/app/app.routes.ts`                   | ⬜     |
| 12.12 | Web E2E tests                            | Cypress tests for all new features (Phases 2–11)                                                                        | `web/cypress/e2e/v2/` (NEW)                   | ⬜     |
| 12.13 | Web deployment update                    | Update Render config, test production build with new features                                                           | `render.yaml`, `Dockerfile`                   | ⬜     |

---

## Phase 13 — Integration, QA & Release

> **Goal:** Final integration testing, documentation, and release.

| #    | Task                            | What to Do                                                                                                                               | Files                                 | Status |
| ---- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------ |
| 13.1 | Cross-feature integration tests | Test workflows that span multiple features: e.g., create project → load into financial calcs → load into RACI → risk analysis → leveling | `tests/test_v2_integration.py` (NEW)  | ⬜     |
| 13.2 | Backward compatibility test     | Verify all V1 `.pmproj` files load correctly with new Risk fields defaulting gracefully; V1 demos still work                             | `tests/test_backward_compat.py` (NEW) | ⬜     |
| 13.3 | UI smoke test (desktop) — V2    | Extended checklist covering all new tabs, sub-tabs, and modes                                                                            | `UI_SMOKE_TEST_CHECKLIST_V2.md` (NEW) | ⬜     |
| 13.4 | PyInstaller build + test        | Rebuild `.exe` with all new modules; verify launch and feature access                                                                    | Build scripts                         | ⬜     |
| 13.5 | Update README.md                | Document all new features with screenshots                                                                                               | `README.md`                           | ⬜     |
| 13.6 | Update CHANGELOG.md             | Add `[2.0.0]` entry with all new features                                                                                                | `CHANGELOG.md`                        | ⬜     |
| 13.7 | Tag `v2.0.0` + GitHub Release   | Annotated tag, release notes, attach `.exe`                                                                                              | Git                                   | ⬜     |
| 13.8 | Deploy web V2 to Render         | Production deploy with all web-ported features                                                                                           | Render                                | ⬜     |

---

## Key Decisions Log (V2)

| #   | Decision                                  | Answer                                                                                          | Reasoning                                                                             |
| --- | ----------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 1   | Standalone vs Integrated calculators?     | **Both** — standalone + "Load from Project" button                                              | Students need to practice textbook problems AND apply to real projects                |
| 2   | RACI matrix scope?                        | **Both** — auto-populate from activities + free-form grid                                       | Covers both real-project use and textbook exercises                                   |
| 3   | AON/AOA depth?                            | **Both modes** — full AON and AOA input with bidirectional conversion                           | PM curriculum requires understanding both representations                             |
| 4   | Web app scope for V2?                     | **Desktop first, web later in V2**                                                              | Get features right on desktop, then port to Angular                                   |
| 5   | Educational depth?                        | **Full + practice mode** — worked solutions + "Try It Yourself"                                 | Maximizes learning value; consistent with V1's educational model                      |
| 6   | Risk Response integration?                | **Both** — extend register columns + separate detailed sub-tab                                  | Quick view in register; deep planning in dedicated sub-tab                            |
| 7   | Tab overflow strategy?                    | **Collapsible tab groups** (Schedule, Cost, Risk, Strategic)                                    | Organizes 25+ tabs into navigable categories                                          |
| 8   | Demo data approach?                       | **New separate demo files** for V2 features                                                     | Don't break V1 demos; each feature gets purpose-built examples                        |
| 9   | Start from `feat/web-v1` or `production`? | Continue on `feat/web-v1` until PR #3 merges                                                    | Branch from production after merge                                                    |
| 10  | Web auth for V2?                          | No                                                                                              | Single-user educational tool; defer auth to V2.1+                                     |
| 11  | Visualization library strategy?           | **Option D — Hybrid** (matplotlib static + Plotly interactive)                                  | Extends proven Gantt pattern; zero architecture change; full interactivity in browser |
| 12  | Z-score table source?                     | **CSV file** (`ztable_stats.csv`), not computed                                                 | Matches textbook reference; students see the exact table from their course material   |
| 13  | "Show All Calculations" scope?            | **UG mode only**, every calculator tab, reuses `WorkedSolutionWindow`                           | Educational requirement; avoids creating a parallel widget pattern                    |
| 14  | SWOT bubble chart layout?                 | **2×2 grid** (S upper-left, W upper-right, O lower-left, T lower-right) with green→red gradient | Preserves familiar SWOT structure while adding quantitative depth                     |

---

## New Files Summary

### Core Engines (11 new files)

| File                                     | Phase | Purpose                                            |
| ---------------------------------------- | ----- | -------------------------------------------------- |
| `core/three_point_engine.py`             | 2     | PERT + Triangular three-point calculations         |
| `core/financial_calcs.py`                | 3A    | Payback, Disc. Payback, ROI, NPV, IRR, PI          |
| `core/factor_scoring.py`                 | 3B    | Unweighted 0-1, Unweighted Factor, Weighted Factor |
| `core/raci_model.py`                     | 4     | RACI matrix dataclass + validation                 |
| `core/cost_estimation.py`                | 5     | 7 cost estimation technique classes                |
| `core/aoa_network_builder.py`            | 7     | AOA network + CPM + dummy insertion                |
| `core/network_converter.py`              | 7     | AON ↔ AOA bidirectional converter                  |
| `core/ztable_loader.py`                  | 10    | Z-table CSV parser + forward/reverse lookup        |
| `core/three_point_step_generator.py`     | 2     | Three-point worked solutions                       |
| `core/financial_step_generator.py`       | 3A    | Financial calc worked solutions                    |
| `core/factor_scoring_step_generator.py`  | 3B    | Factor scoring worked solutions                    |
| `core/raci_step_generator.py`            | 4     | RACI worked solutions                              |
| `core/cost_estimation_step_generator.py` | 5     | Cost estimation worked solutions                   |
| `core/risk_step_generator.py`            | 6     | Risk assessment worked solutions                   |
| `core/aoa_step_generator.py`             | 7     | AOA network worked solutions                       |
| `core/leveling_step_generator.py`        | 8     | Resource leveling worked solutions                 |

### GUI Tabs (6 new files, 10+ modified)

| File                                        | Phase  | Action                                         |
| ------------------------------------------- | ------ | ---------------------------------------------- |
| `gui/widgets/tab_group_notebook.py`         | 1      | NEW — collapsible tab group widget             |
| `gui/widgets/educational_calculator_tab.py` | 1      | NEW — base class for educational calculators   |
| `gui/widgets/ztable_widget.py`              | 10     | NEW — reusable Z-score table with highlighting |
| `gui/tabs/three_point_tab_edu.py`           | 2      | NEW (replaces empty stub `pert_tab_edu.py`)    |
| `gui/tabs/financial_tab_edu.py`             | 3      | NEW (replaces empty stub `selection_tab.py`)   |
| `gui/tabs/raci_tab_edu.py`                  | 4      | NEW                                            |
| `gui/tabs/cost_estimation_tab_edu.py`       | 5      | NEW                                            |
| `gui/tabs/risk_tab_edu.py`                  | 6      | MODIFY — add 2 sub-tabs                        |
| `gui/tabs/rcps_tab_edu.py`                  | 8      | MODIFY — add educational sub-tab               |
| `gui/tabs/network_tab.py`                   | 7      | MODIFY — add AOA mode                          |
| `gui/tabs/input_tab_edu.py`                 | 7      | MODIFY — add AON/AOA toggle                    |
| `gui/tabs/swot_tab_edu.py`                  | 9      | MODIFY — add bubble chart + dropdown filter    |
| `gui/tabs/pestel_tab_edu.py`                | 9      | MODIFY — add radar interactivity + bubbles     |
| `gui/tabs/probability_tab_edu.py`           | 10, 11 | MODIFY — add Z-table sub-tab + interactive     |
| `gui/tabs/wbs_tab_edu.py`                   | 11     | MODIFY — add cost display + flat table         |
| Multiple chart tabs                         | 11     | MODIFY — add "🔍 Open Interactive" buttons     |

### Demo Data (9 new files)

| File                                        | Phase |
| ------------------------------------------- | ----- |
| `data/demos/v2/three_point_demo.json`       | 2     |
| `data/demos/v2/financial_demo.json`         | 3A    |
| `data/demos/v2/factor_scoring_demo.json`    | 3B    |
| `data/demos/v2/raci_demo.json`              | 4     |
| `data/demos/v2/cost_estimation_demo.json`   | 5     |
| `data/demos/v2/risk_assessment_demo.json`   | 6     |
| `data/demos/v2/aoa_demo.json`               | 7     |
| `data/demos/v2/resource_leveling_demo.json` | 8     |
| `data/demos/v2/swot_scored_demo.json`       | 9     |

### Tests (12 new files)

| File                               | Phase |
| ---------------------------------- | ----- |
| `tests/test_three_point.py`        | 2     |
| `tests/test_financial_calcs.py`    | 3A    |
| `tests/test_factor_scoring.py`     | 3B    |
| `tests/test_raci.py`               | 4     |
| `tests/test_cost_estimation.py`    | 5     |
| `tests/test_risk_assessment.py`    | 6     |
| `tests/test_aoa_network.py`        | 7     |
| `tests/test_leveling_education.py` | 8     |
| `tests/test_strategic_viz.py`      | 9     |
| `tests/test_ztable.py`             | 10    |
| `tests/test_cross_tab_polish.py`   | 11    |
| `tests/test_v2_integration.py`     | 13    |
| `tests/test_backward_compat.py`    | 13    |

### Utilities (3 new files)

| File                          | Phase |
| ----------------------------- | ----- |
| `utils/demo_loader.py`        | 1     |
| `utils/interactive_charts.py` | 11    |
| `data/demos/v2/` (directory)  | 1     |

---

## Phase 12 — Plotly Embedded Renderer (Complete) ✅

> **Goal:** Add an interactive Plotly chart renderer toggle (Classic / 📊 Plotly) to every chart tab, using Edge WebView2 embedded in Tkinter frames.

---

## Phase 12B — Web App: Interactive Tutorial System ✅

> **Goal:** Add an in-app guided tutorial to the Angular web app that highlights UI elements step-by-step and describes each feature. The tutorial button sits in the top bar; pressing it starts an overlay-based walkthrough.
> **Status:** Implemented — builds successfully.

### Architecture

```
web/src/app/
├── core/models/tutorial.model.ts         ← TutorialStep interface
├── shared/
│   ├── constants/tutorial-steps.ts       ← Global step definitions (single-file update)
│   ├── services/tutorial.service.ts      ← Central state, step registry, navigation
│   └── components/tutorial/
│       ├── tutorial-overlay.component.ts  ← Overlay highlight + tooltip UI
│       └── tutorial-overlay.component.scss
├── layout/
│   ├── app-shell/                        ← Hosts <app-tutorial-overlay>
│   └── top-bar/                          ← Tutorial button + step registration
```

### Design Decisions

| Decision                 | Choice                                                                      | Reasoning                                                 |
| ------------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------- |
| Element targeting        | CSS selectors (`.pm-topbar__hamburger`, `a[routerLink="/input"]`)           | Stable with BEM classes; no manual `id` attributes needed |
| Route awareness          | Steps have optional `route` field — auto-navigates before highlighting      | Elements on lazy-loaded pages become reachable            |
| Academic level filtering | PG-only steps (`group: 'pg'`) hidden in UG mode                             | UG students don't see features they can't access          |
| Extensibility            | `TutorialService.registerSteps()` — callable from any component             | Feature components can add their own contextual steps     |
| Persistence              | `localStorage` tracks "tutorial seen" state                                 | Supports first-visit auto-trigger if desired              |
| Accessibility            | Keyboard nav (Esc, Arrow keys), `role="dialog"`, `aria-modal`, `aria-label` | Screen reader and keyboard-only users supported           |
| Missing elements         | Auto-skips to next step if selector not found in DOM                        | Graceful handling of conditional/hidden elements          |

### Files

| File                                                                     | Action                                    |
| ------------------------------------------------------------------------ | ----------------------------------------- |
| `web/src/app/core/models/tutorial.model.ts`                              | NEW — `TutorialStep` interface            |
| `web/src/app/shared/constants/tutorial-steps.ts`                         | NEW — 18 global tutorial steps            |
| `web/src/app/shared/services/tutorial.service.ts`                        | NEW — service with start/next/back/close  |
| `web/src/app/shared/components/tutorial/tutorial-overlay.component.ts`   | NEW — overlay + tooltip component         |
| `web/src/app/shared/components/tutorial/tutorial-overlay.component.scss` | NEW — overlay styles                      |
| `web/src/app/layout/app-shell/app-shell.component.ts`                    | MODIFIED — import + declare overlay       |
| `web/src/app/layout/app-shell/app-shell.component.html`                  | MODIFIED — add `<app-tutorial-overlay>`   |
| `web/src/app/layout/top-bar/top-bar.component.ts`                        | MODIFIED — inject service, register steps |
| `web/src/app/layout/top-bar/top-bar.component.html`                      | MODIFIED — add help_outline button        |
| `web/src/app/layout/top-bar/top-bar.component.scss`                      | MODIFIED — tutorial button style          |

### How to Add New Tutorial Steps

**Global steps:** Edit `web/src/app/shared/constants/tutorial-steps.ts` — append to the array.

**Feature-specific steps:** In any feature component, inject `TutorialService` and call `registerSteps()`:

```typescript
constructor() {
  inject(TutorialService).registerSteps([
    { selector: '.evm-baseline-btn', title: 'Set Baseline', description: '...', group: 'evm' },
  ]);
}
```

> **Status:** **Complete** — all 13 chart tabs wired.
> **Branch:** `feat/web-v1`
> **Tests:** 1182 passed (no regressions from baseline)

### Architecture

- **Embed engine:** `tkwebview2` v3.5.0 + `pywebview==4.4.1` (Edge WebView2 in Tkinter)
- **Critical prerequisite:** `ensure_com_sta()` must call `CoInitializeEx(None, 0x2)` (STA) before `Tk()` creation
- **pywebview pin:** Must be 4.4.1 — pywebview 6.x breaks `tkwebview2`'s `EdgeChrome.web_view` attribute
- **Plotly loading:** CDN via `include_plotlyjs="cdn"` in generated HTML
- **Widget:** `PlotlyChartFrame(ttk.Frame)` — writes HTML to temp file → WebView2 navigates to `file://` path

### New Files

| File                                             | Purpose                                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------ |
| `src/pmhelper/gui/widgets/plotly_chart_frame.py` | `PlotlyChartFrame` widget, `ensure_com_sta()`, `WEBVIEW2_AVAILABLE` flag |
| `src/pmhelper/utils/plotly_charts.py`            | 18 Plotly generator functions for all chart types                        |
| `src/pmhelper/utils/plotly_network.py`           | Interactive network diagram generator (sugiyama layout)                  |

### Wiring Pattern (applied to every tab)

1. Import `PlotlyChartFrame`, `WEBVIEW2_AVAILABLE`, relevant generator; set `_PLOTLY_EMBED` flag
2. Add `self._render_mode_var = tk.StringVar(value="matplotlib")` in `__init__`
3. Add renderer toggle radio buttons ("Classic" / "📊 Plotly") calling `self._switch_renderer`
4. Wrap existing matplotlib canvas in `self._mpl_*_frame = ttk.Frame(parent)` container
5. Create `self._plotly_frame = PlotlyChartFrame(parent)` (hidden by default)
6. Add guard at top of existing draw method: if plotly mode → call `_update_plotly_*()` → return
7. Add `_switch_renderer()` — pack_forget/pack swap between matplotlib and Plotly frames
8. Add `_update_plotly_*()` — calls generator function → `_plotly_frame.update_chart(fig)`

### Tabs Wired

| #   | Tab File                     | Chart(s)                                            | Generator(s)                                                                                    |
| --- | ---------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1   | `gantt_tab_edu.py`           | Gantt/CPM                                           | `plotly_gantt_cpm`                                                                              |
| 2   | `network_tab.py`             | AON Network                                         | `generate_plotly_network`                                                                       |
| 3   | `pert_diagram_tab.py`        | PERT Network                                        | `plotly_pert_network`                                                                           |
| 4   | `evm_tab_edu.py`             | S-Curve                                             | `plotly_scurve`                                                                                 |
| 5   | `three_point_tab_edu.py`     | Three-Point Chart                                   | `plotly_three_point`                                                                            |
| 6   | `financial_tab_edu.py`       | CF Chart + Factor Scoring                           | `plotly_financial_cf`, `plotly_factor_scoring`                                                  |
| 7   | `risk_tab_edu.py`            | Risk Matrix                                         | `plotly_risk_matrix`                                                                            |
| 8   | `probability_tab_edu.py`     | PERT Dist/CDF/Sensitivity + MC Results              | `plotly_pert_distribution`, `plotly_pert_cumulative`, `plotly_sensitivity`, `plotly_mc_results` |
| 9   | `rcps_tab_edu.py`            | RCPS Gantt                                          | `plotly_rcps_gantt`                                                                             |
| 10  | `cost_estimation_tab_edu.py` | Learning Curve                                      | `plotly_learning_curve`                                                                         |
| 11  | `optimization_tab.py`        | Time-Cost Curve, Resource Profiles, Pareto Frontier | `plotly_time_cost_curve`, `plotly_resource_profiles`, `plotly_pareto_frontier`                  |
| 12  | `crashing_tab_gui.py`        | Step-by-step Network                                | `plotly_crashing_network`                                                                       |
| 13  | `dashboard_tab_edu.py`       | Mini S-Curve                                        | `plotly_scurve(compact=True)`                                                                   |

### Dependencies Added

```
pywebview==4.4.1
tkwebview2>=3.5.0
plotly>=5.18.0
```

---

## V2+ Roadmap (Future)

| Feature                                          | Target | Status      |
| ------------------------------------------------ | ------ | ----------- |
| Portfolio Management (multi-project dashboard)   | V2.1+  | ⬜ Planning |
| Collaborative Features (multi-user editing)      | V2.2+  | ⬜ Planning |
| Predictive ML (duration estimation from history) | V3     | ⬜ Research |
| Mobile Applications (iOS/Android)                | V3     | ⬜ Research |

---

## Definition of Done (V2 Release)

> Boxes are ticked only where verified against the code, not inferred from a
> phase being "done". Unticked items below are genuinely outstanding.

- [x] ~~All V1 deferred items completed (Phase 0)~~ — **N/A, phase obsolete** (see Phase 0)
- [x] Tab group refactor working with all 25+ tabs (Phase 1)
- [x] Three-Point Estimates tab with chart, worked solution, Try It Yourself (Phase 2)
- [x] Financial Analysis: 6 calculators + 3 factor scoring models + worked solutions (Phase 3)
- [x] RACI matrix with auto-populate + free-form + validation (Phase 4)
- [x] Cost Estimation: 7 techniques with worked solutions (Phase 5)
- [x] Risk Assessment Matrix + Risk Response Planning sub-tabs (Phase 6)
- [x] AON/AOA dual mode with conversion + AOA visualization (Phase 7)
- [x] Resource Leveling: smoothing/constrained modes + step walkthrough (Phase 8)
- [x] SWOT 4D bubble chart with dropdown filter + green→red gradient (Phase 9)
- [x] PESTEL radar interactivity + bubble overlay (Phase 9)
- [x] Z-score table from `ztable_stats.csv` in BOTH Probability AND Three-Point tabs (Phase 10)
- [x] Z-table path highlighting — forward Z→P and reverse P→Z with real-time data linking (Phase 10)
- [x] "📊 Show All Calculations" button on every calculator tab, UG mode (Phases 10 + 11)
- [x] Hybrid interactive charts (matplotlib static + Plotly "🔍 Open Interactive") on all chart tabs (Phase 11)
- [x] Plotly embedded renderer toggle on all 13 chart tabs via WebView2 (Phase 12) ✅
- [x] WBS cost display mode + flat table view, UG mode (Phase 11)
- [x] WBS ↔ Cost Estimation bidirectional link + top-down allocation (Phase 11)
- [x] All new features have dedicated demo files — 9 files present in `data/demos/v2/`
- [ ] All new features have "Try It Yourself" practice mode — **not audited**; present on Three-Point, Financial, Factor Scoring, Cost Estimation, RACI. Not confirmed across the rest.
- [ ] All new features have unit tests — per-feature test files all exist; **coverage depth not audited**. Note `crashing_steps()` shipped untested and was wrong (Phase 11 notes), so file-exists ≠ covered.
- [ ] All V1 tests (797+) still pass — **NO.** Measured at `ef3fec9`: **32 failures / 1279 passing** (`--ignore=tests/server`; `tests/server` currently fails to collect). All pre-date V2 Phase 11 and are test/env debt, not product bugs — but the claim as written is false today.
- [ ] Backward compatibility with V1 `.pmproj` files verified — `tests/test_backward_compat.py` (Phase 13.2) does not exist
- [ ] PyInstaller bundle builds and runs on clean machine — note the specs hidden-import `pert_tab_edu` / `crashing_tab_edu`, both dead modules
- [ ] CHANGELOG.md updated with `[2.0.0]` entry — still tops out at `[1.0.0]` (2025-09-27)
- [ ] GitHub Release tagged `v2.0.0` — only `v1.0.0` exists
- [ ] **Phase 12 (Web Porting) — not started.** `web/src/app/features/` holds only the V1 set; no Three-Point / Financial / RACI / Cost Estimation / Strategic / Z-table components, and `app.routes.ts` is still flat.
- [ ] **Phase 13 (Integration, QA & Release) — not started.**
