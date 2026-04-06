# PMhelper Edu — V2 Implementation Plan

> **Scope:** 9 new desktop feature areas (Three-Point Chart, Financial Calcs, Factor Scoring, RACI, Risk Assessment/Response, AON/AOA, Cost Estimation, Resource Leveling enhancements), tab group refactor, web porting
> **Approach:** 1 developer + AI agent assistance
> **Date:** April 5, 2026
> **Last Status Update:** April 6, 2026
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

| Area | What Exists | Where | Reuse Plan |
| ---- | ----------- | ----- | ---------- |
| PERT / Three-Point | `calculate_pert_estimates()` — Te, σ² | `core/calculations.py:32` | Reuse calc; add chart + table tab |
| NPV | `NPVOptimizer.calculate_npv()` | `core/npv_optimization.py` | Reuse for NPV calc; add 5 more financial metrics |
| AHP / Linear Scoring | `AHPAnalyzer`, `LinearScoringRule` | `core/selection.py` | Keep; add 3 new factor scoring models alongside |
| Selection Tab | Empty stub — "Coming Soon" | `gui/tabs/selection_tab.py` | **Replace entirely** with Financial + Factor Scoring tab |
| Risk Register | `Risk` dataclass, `RiskRegister` | `core/risk_register_edu.py` | **Extend** with response fields |
| Risk Tab | 2 sub-tabs (Register, Matrix) | `gui/tabs/risk_tab_edu.py` | **Add** 2 more sub-tabs |
| AON Network | `NetworkBuilder` DiGraph | `core/network_builder.py` | Keep; build parallel AOA builder |
| Network Tab | AON vis.js viewer | `gui/tabs/network_tab.py` | Add AOA mode + toggle |
| Resource Leveling | `MinimumMomentLeveling`, `BurgessLeveling` | `core/resource_leveling.py` | Reuse; add educational walkthrough |
| RCPS Tab | 2 sub-tabs (Schedule, Histograms) | `gui/tabs/rcps_tab_edu.py` | Add walkthrough sub-tab |
| PERT Tab | Empty stub | `gui/tabs/pert_tab_edu.py` | **Replace** with Three-Point Estimate tab |
| Step Generators | `CrashingStepGenerator`, EVM steps | `core/step_generators_edu.py` | Extend pattern for new features |

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

## Phase 0 — V1 Carry-Forward & QA

> **Goal:** Complete all deferred V1 items before starting new work.
> **Priority:** P0 — nothing else starts until this is done.

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

## Phase 1 — Tab Group Refactor & Infrastructure

> **Goal:** Refactor the flat 18-tab `ttk.Notebook` into collapsible tab groups so new tabs can be organized logically.
> **Why first:** All subsequent phases add new tabs — they need the group structure in place.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 1.1 | Design collapsible group widget | Create a `TabGroupNotebook` widget that uses nested `ttk.Notebook` or `ttk.LabelFrame` with collapsible sections (Schedule, Cost, Risk, Strategic, Dashboard) | `gui/widgets/tab_group_notebook.py` (NEW) | ⬜ |
| 1.2 | Refactor `_build_tabs()` | Replace flat `ttk.Notebook` with `TabGroupNotebook`; assign all 18 existing tabs to their groups per the structure above | `gui/main_window_edu.py` — `_build_tabs()` at line 189 | ⬜ |
| 1.3 | Update `_all_tabs_ordered` | Adapt ordered list + PG-only show/hide logic to work with nested groups | `gui/main_window_edu.py` — lines 303–343 | ⬜ |
| 1.4 | Update tab selection / navigation | Ensure `on_tab_selected()`, keyboard navigation, and programmatic tab switching work with groups | `gui/main_window_edu.py` | ⬜ |
| 1.5 | Regression test all 18 existing tabs | Verify every tab still renders, loads data, and responds to mode toggle (UG/PG) | Tests: existing 797+ tests must pass | ⬜ |
| 1.6 | Create V2 demo data infrastructure | Add `data/demos/v2/` folder structure; create `DemoLoader` utility that reads demo JSON files and populates the appropriate calculator | `data/demos/v2/` (NEW), `utils/demo_loader.py` (NEW) | ⬜ |
| 1.7 | Create base `EducationalCalculatorTab` | Abstract base class with: standalone input panel, "Load from Project" button, "Worked Solution" expandable frame, "Try It Yourself" toggle | `gui/widgets/educational_calculator_tab.py` (NEW) | ⬜ |

---

## Phase 2 — Three-Point Estimate Tab

> **Goal:** Add a dedicated "Three-Point Estimates" tab showing O/P/M/Expected values per activity as a line chart and summary table.
> **Existing code:** `calculate_pert_estimates()` in `core/calculations.py` computes Te = (O+4M+P)/6 and σ².
> **Decision:** Standalone calculator + Load from Project.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 2.1 | Create Three-Point engine | Extract/extend PERT calculation into a dedicated module: given O, M, P per activity → compute Expected (Te), Variance (σ²), Std Dev (σ), project-level σ for critical path. Support both PERT-weighted `(O+4M+P)/6` and Triangular `(O+M+P)/3` formulas | `core/three_point_engine.py` (NEW) | ⬜ |
| 2.2 | Build Three-Point tab UI | Create tab with: (1) Standalone input grid (Activity, O, M, P — editable rows), (2) "Load from Project" button pulling from Input Activities PERT data, (3) Formula selector (PERT vs Triangular), (4) "Calculate" button | `gui/tabs/three_point_tab_edu.py` (NEW) — replaces `pert_tab_edu.py` stub | ⬜ |
| 2.3 | Results table | Treeview table with columns: Activity, O, M, P, Expected (Te), Variance (σ²), Std Dev (σ). Footer row with project totals for critical path. Color-code critical path activities | Same file — sub-frame | ⬜ |
| 2.4 | Line chart visualization | Matplotlib chart with 4 lines per activity (O, M, P, Expected) — X-axis = Activity ID, Y-axis = Duration. Legend, gridlines, highlight critical path activities | Same file — chart sub-frame using `FigureCanvasTkAgg` | ⬜ |
| 2.5 | Worked solution panel | Step-by-step panel: show formula → substitute values → compute Te → compute σ² → interpret. Use existing `step_generators_edu.py` pattern | `core/three_point_step_generator.py` (NEW) | ⬜ |
| 2.6 | "Try It Yourself" mode | Hide the results; student enters their answer for Te per activity; "Check" button compares; reveal on completion | `gui/tabs/three_point_tab_edu.py` — practice frame | ⬜ |
| 2.7 | Demo file | Create `data/demos/v2/three_point_demo.json` with 8–10 activities with O/M/P values and known solutions | `data/demos/v2/three_point_demo.json` (NEW) | ⬜ |
| 2.8 | Register tab in group | Add to Schedule group in `TabGroupNotebook`; update `_all_tabs_ordered` and `tabs` dict | `gui/main_window_edu.py` | ⬜ |
| 2.9 | Unit tests | Test engine calculations (known PERT values), test Load from Project, test Try It Yourself scoring | `tests/test_three_point.py` (NEW) | ⬜ |

---

## Phase 3 — Financial Analysis Tab (Project Selection Calculators)

> **Goal:** Replace the empty `selection_tab.py` stub with a full Financial Analysis tab containing 6 financial calculators and 3 factor scoring models.
> **Existing code:** `NPVOptimizer` (CLI only), `AHPAnalyzer`, `LinearScoringRule` in `core/selection.py`.
> **Decision:** Standalone + Load from Project. Full worked solutions + Try It Yourself.

### Phase 3A — Financial Calculators

| #    | Task | What to Do | Files | Status |
| ---- | ---- | ---------- | ----- | ------ |
| 3A.1 | Financial calculation engine | Module with functions for: **Payback Period** (cumulative CF until break-even), **Discounted Payback Period** (discounted CF until break-even), **ROI** ((Gain−Cost)/Cost × 100), **NPV** (Σ CFₜ/(1+r)ᵗ — reuse from `npv_optimization.py`), **IRR** (rate where NPV=0 — use `scipy.optimize.brentq` or bisection), **Profitability Index** (PV of future CF / Initial Investment) | `core/financial_calcs.py` (NEW) | ⬜ |
| 3A.2 | Financial Analysis tab — structure | Create tabbed sub-notebook within the Financial Analysis tab: sub-tabs for (1) Financial Calculators, (2) Factor Scoring Models (Phase 3B). Place in Cost group. | `gui/tabs/financial_tab_edu.py` (NEW) — replaces `selection_tab.py` | ⬜ |
| 3A.3 | Financial Calculators sub-tab UI | Standalone input panel: Initial Investment, Discount Rate, table of (Year, Cash Flow) rows. "Load from Project" pulls costs/durations. 6 checkboxes to select which metrics to compute. "Calculate" button. | Same file — financial sub-tab | ⬜ |
| 3A.4 | Financial results display | Results panel: table with Metric / Value / Interpretation columns. E.g., "Payback Period = 3.4 years — Investment recovered within project horizon". NPV positive = green, negative = red | Same file | ⬜ |
| 3A.5 | Financial worked solutions | Step-by-step for each selected metric: formula → substitution → intermediate steps → final value → interpretation. E.g., Payback: show cumulative table row by row until break-even; IRR: show bisection iterations | `core/financial_step_generator.py` (NEW) | ⬜ |
| 3A.6 | Financial "Try It Yourself" | Hide all results; student enters their answers for each selected metric; "Check" button validates (tolerance ±0.01 for rates, ±0.1 for currency) | `gui/tabs/financial_tab_edu.py` — practice frame | ⬜ |
| 3A.7 | Payback chart | Matplotlib: cumulative cash flow bar chart with break-even line for Payback; discounted CF overlay for Discounted Payback | Same file — chart | ⬜ |
| 3A.8 | Financial demo file | `data/demos/v2/financial_demo.json` — 2 project scenarios with cash flows, known Payback/NPV/IRR/PI values | `data/demos/v2/financial_demo.json` (NEW) | ⬜ |
| 3A.9 | Unit tests — financial | Test all 6 calculations against hand-computed values; edge cases (negative CF, zero discount rate, no payback possible) | `tests/test_financial_calcs.py` (NEW) | ⬜ |

### Phase 3B — Factor Scoring Models

| #    | Task | What to Do | Files | Status |
| ---- | ---- | ---------- | ----- | ------ |
| 3B.1 | Factor scoring engine | Module with 3 models: (1) **Unweighted 0-1 Scoring** — each criterion yes/no (0 or 1), sum scores per project, (2) **Unweighted Factor Scoring** — each criterion scored 1–5 (or custom scale), sum per project, (3) **Weighted Factor Scoring** — criteria have weights (must sum to 1.0 or 100%), score × weight, sum per project. All models rank N projects and identify the winner | `core/factor_scoring.py` (NEW) | ⬜ |
| 3B.2 | Factor Scoring sub-tab UI | Standalone input: (1) Define criteria list (add/remove/reorder), (2) Define projects list, (3) Select model type (radio buttons), (4) If weighted: enter weights per criterion, (5) Score matrix grid (projects × criteria), (6) "Load from Project" loads criteria from project metadata | `gui/tabs/financial_tab_edu.py` — factor scoring sub-tab | ⬜ |
| 3B.3 | Factor scoring results | Results table: Project | Criterion1 | ... | CriterionN | Total Score | Rank. Color-code winner. Side-by-side comparison bar chart (projects on X, total score on Y) | Same file | ⬜ |
| 3B.4 | Factor scoring worked solutions | For weighted model: show weight × score per cell → row sum → rank; for 0-1: show binary mapping logic | `core/factor_scoring_step_generator.py` (NEW) | ⬜ |
| 3B.5 | Factor scoring "Try It Yourself" | Give criteria, weights, scores; student computes weighted totals and ranking; validate answers | Same tab — practice frame | ⬜ |
| 3B.6 | Factor scoring demo file | `data/demos/v2/factor_scoring_demo.json` — 4 projects, 5 criteria, known rankings for each model | `data/demos/v2/factor_scoring_demo.json` (NEW) | ⬜ |
| 3B.7 | Unit tests — factor scoring | All 3 models with known solutions; edge cases (tied scores, single project, zero weights) | `tests/test_factor_scoring.py` (NEW) | ⬜ |

---

## Phase 4 — Responsibility Matrix (RACI)

> **Goal:** New tab for RACI matrix (Responsible/Accountable/Consulted/Informed) + Deliverables vs Department matrix.
> **Existing code:** Nothing — completely new.
> **Decision:** Both auto-populate from project activities AND free-form grid. Goes in Strategic group.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 4.1 | RACI data model | Dataclass: `RACIMatrix` with activities (rows), roles/people (columns), cell values ∈ {R, A, C, I, ""}. Validation: exactly 1 A per activity (warn if missing), at least 1 R per activity. Support export to dict/JSON for persistence in `.pmproj` | `core/raci_model.py` (NEW) | ⬜ |
| 4.2 | RACI tab — main structure | New tab with 2 sub-tabs: (1) **Task × Role RACI** (activities vs team members), (2) **Deliverables × Department** (project deliverables vs organizational departments) | `gui/tabs/raci_tab_edu.py` (NEW) | ⬜ |
| 4.3 | Task × Role sub-tab | Editable grid: rows = activities (auto-populated from Input Activities OR free-form add/remove), columns = roles (free-form add/remove: "Project Manager", "Developer", "QA", etc.). Cell = dropdown {R, A, C, I, ""}. Color-coded cells (R=blue, A=red, C=yellow, I=green). "Load from Project" fills activity names from `.pmproj` | Same file — sub-tab 1 | ⬜ |
| 4.4 | Deliverables × Department sub-tab | Same grid concept but rows = deliverables (WBS work packages if available, else free-form), columns = departments (free-form). Cell = dropdown {R, A, C, I, ""} | Same file — sub-tab 2 | ⬜ |
| 4.5 | RACI validation panel | Real-time validation warnings: "Activity X has no Accountable (A)", "Activity Y has multiple A assignments", "Role Z has no assignments". Summary stats: total assignments by type | Same file — bottom panel | ⬜ |
| 4.6 | RACI worked solution | Educational panel explaining: what each letter means, how to construct a RACI, common mistakes (no A, multiple A's). Worked example with 5 activities × 4 roles | `core/raci_step_generator.py` (NEW) | ⬜ |
| 4.7 | RACI "Try It Yourself" | Give a scenario description; student fills the RACI grid; "Check" validates against expected answer | Same tab — practice frame | ⬜ |
| 4.8 | RACI persistence | Save/load RACI matrices in `.pmproj` file format (add `raci_data` section to project state) | `gui/tabs/raci_tab_edu.py` + `utils/project_io.py` | ⬜ |
| 4.9 | RACI demo file | `data/demos/v2/raci_demo.json` — software project scenario with 10 activities, 5 roles, pre-filled RACI with known correct answers | `data/demos/v2/raci_demo.json` (NEW) | ⬜ |
| 4.10 | Register in Strategic group | Add to `TabGroupNotebook` Strategic category; update `_all_tabs_ordered` and `tabs` dict | `gui/main_window_edu.py` | ⬜ |
| 4.11 | Unit tests — RACI | Model validation (single A enforcement), grid population from activities, persistence round-trip | `tests/test_raci.py` (NEW) | ⬜ |

---

## Phase 5 — Cost Estimation Techniques

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

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 5.1 | Cost estimation engine | Module with a class per technique: `AnalogousEstimator`, `BottomUpEstimator`, `WorkElementEstimator`, `PowerSizingEstimator`, `UnitFactorEstimator`, `CostCapacityEstimator`, `LearningCurveEstimator`. Each has `estimate()` → cost + breakdown dict | `core/cost_estimation.py` (NEW) | ⬜ |
| 5.2 | Cost Estimation tab — structure | New tab with a method selector (7 radio buttons or dropdown). Selecting a method shows the corresponding input form below. "Load from Project" fills relevant data (e.g., WBS costs for bottom-up) | `gui/tabs/cost_estimation_tab_edu.py` (NEW) | ⬜ |
| 5.3 | Top-Down input/output | Inputs: Reference project cost, Adjustment factors (complexity, size, risk %). Output: Estimated cost with adjustment breakdown | Same file — top-down panel | ⬜ |
| 5.4 | Bottom-Up input/output | Inputs: Table of work packages (Name, Labour Cost, Material Cost, Equipment Cost, Overhead %). "Load from Project" pulls WBS work packages. Output: Total cost with breakdown tree | Same file — bottom-up panel | ⬜ |
| 5.5 | Work Element input/output | Inputs: Work elements table (Element, Hours, Rate, Material $, Equip $). Output: Element costs + total | Same file — work element panel | ⬜ |
| 5.6 | Power Sizing / Cost-Capacity input/output | Inputs: Reference cost, Reference capacity, Target capacity, Sizing exponent (x). Output: Estimated cost with formula | Same file — power sizing panel | ⬜ |
| 5.7 | Unit/Factor input/output | Inputs: Table of items (Item, Unit Cost, Quantity, Factor). Output: Extended cost per item + total | Same file — unit/factor panel | ⬜ |
| 5.8 | Learning Curves input/output | Inputs: First unit time/cost (T₁), Learning rate (%), Target unit number (N). Output: T_N, cumulative average, total cost. Plot: learning curve chart (unit # vs time) | Same file — learning curve panel | ⬜ |
| 5.9 | Cost estimation worked solutions | Step generator for each technique: show formula → substitute → compute → interpret. Learning curves: show the log transformation steps | `core/cost_estimation_step_generator.py` (NEW) | ⬜ |
| 5.10 | Cost estimation "Try It Yourself" | Per technique: give inputs, student computes cost; validate against known answer | Same tab — practice frame | ⬜ |
| 5.11 | Comparison view | After computing 2+ techniques, show a side-by-side comparison table + bar chart of estimated costs from different methods | Same file — comparison panel | ⬜ |
| 5.12 | Cost estimation demo files | `data/demos/v2/cost_estimation_demo.json` — scenarios for each technique with known solutions | `data/demos/v2/cost_estimation_demo.json` (NEW) | ⬜ |
| 5.13 | Register in Cost group | Add to `TabGroupNotebook` Cost category | `gui/main_window_edu.py` | ⬜ |
| 5.14 | Unit tests — cost estimation | All 7 techniques with hand-verified results; edge cases (zero quantities, learning rate = 100%) | `tests/test_cost_estimation.py` (NEW) | ⬜ |

---

## Phase 6 — Risk Assessment Matrix & Risk Response Planning

> **Goal:** Extend the existing Risk Analysis tab (2 sub-tabs) with 2 new sub-tabs: Risk Assessment Matrix and Risk Response Planning. Also extend the `Risk` dataclass with response fields.
> **Existing code:** `Risk` dataclass + `RiskRegister` in `core/risk_register_edu.py`; Risk tab with Register + Heat Map in `gui/tabs/risk_tab_edu.py`.
> **Decision:** Both — extend Risk Register columns AND add separate detailed sub-tabs.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 6.1 | Extend `Risk` dataclass | Add fields: `risk_score` (P × I, auto-computed), `risk_rank` (ordinal within register), `response_strategy` (enum: Avoid/Transfer/Mitigate/Accept/Exploit/Share/Enhance), `response_description` (str), `response_owner` (str), `response_cost` (float), `residual_probability` (float 1–5), `residual_impact` (float 1–5), `residual_score` (auto-computed), `trigger_conditions` (str), `contingency_plan` (str) | `core/risk_register_edu.py` | ⬜ |
| 6.2 | Update Risk Register sub-tab columns | Add visible columns to the Treeview: Risk Score (auto-computed, sortable), Rank, Response Strategy (dropdown). Sorting by Risk Score ranks risks automatically | `gui/tabs/risk_tab_edu.py` — sub-tab 1 | ⬜ |
| 6.3 | Risk Assessment Matrix sub-tab (NEW) | **Sub-tab 3:** 5×5 matrix grid (Probability 1–5 on Y-axis, Impact 1–5 on X-axis). Each cell shows count of risks + risk IDs. Color zones: Green (1–4 low), Yellow (5–9 medium), Orange (10–15 high), Red (16–25 critical). Click a cell to list risks in that position. Summary panel: total risks per zone, top-5 risks by score | `gui/tabs/risk_tab_edu.py` — new sub-tab | ⬜ |
| 6.4 | Risk ranking view | Sortable table of all risks ordered by Risk Score (desc). Columns: Rank, ID, Name, P, I, Score, Category, Response Strategy. Bar chart: horizontal bars per risk colored by zone | Same sub-tab — ranking panel | ⬜ |
| 6.5 | Risk Response Planning sub-tab (NEW) | **Sub-tab 4:** Detailed response planning form per selected risk. Fields: Response Strategy (dropdown with PM-standard options per threat/opportunity), Description, Owner, Estimated Response Cost, Residual P, Residual I, Residual Score (auto), Trigger Conditions, Contingency Plan. "Apply to All Unplanned" button sets Accept as default | `gui/tabs/risk_tab_edu.py` — new sub-tab | ⬜ |
| 6.6 | Response effectiveness summary | Table: Risk ID, Original Score, Response, Residual Score, Score Reduction (%). Total: Original Total Exposure vs Residual Total Exposure. "Response Effectiveness" metric = (Original − Residual) / Original × 100% | Same sub-tab — summary panel | ⬜ |
| 6.7 | Risk worked solutions | Step-by-step panel: (1) How to assess P and I, (2) Computing Risk Score, (3) Plotting on the matrix, (4) Selecting response strategies (when to Avoid vs Mitigate vs Accept), (5) Computing residual risk | `core/risk_step_generator.py` (NEW) | ⬜ |
| 6.8 | Risk "Try It Yourself" | Give a scenario with risk descriptions; student assigns P, I, computes scores, selects strategies; validate against expected answers | `gui/tabs/risk_tab_edu.py` — practice frame | ⬜ |
| 6.9 | Risk demo file | `data/demos/v2/risk_assessment_demo.json` — 12 risks with pre-assigned P/I, known scores, recommended strategies, and residual values | `data/demos/v2/risk_assessment_demo.json` (NEW) | ⬜ |
| 6.10 | Unit tests — risk extensions | Test Risk Score auto-computation, ranking, response effectiveness calc, residual score. Test backward compatibility (old `.pmproj` files without response fields load cleanly) | `tests/test_risk_assessment.py` (NEW) | ⬜ |

---

## Phase 7 — AON / AOA Dual Network Mode

> **Goal:** Add Activity-on-Arrow (AOA) representation alongside the existing Activity-on-Node (AON). Support both input modes with conversion between them.
> **Existing code:** `NetworkBuilder` (AON DiGraph) in `core/network_builder.py`; Network tab with vis.js in `gui/tabs/network_tab.py`.
> **Decision:** Both input modes — full AON and AOA entry with bidirectional conversion.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 7.1 | AOA data model | `AOANetwork` class: events (numbered nodes), arrows (activities on edges), dummy activities (zero duration, dashed). Event = `{id: int, label: str, earliest_time: float, latest_time: float}`. Arrow = `{from_event: int, to_event: int, activity_id: str, duration: float, is_dummy: bool}` | `core/aoa_network_builder.py` (NEW) | ⬜ |
| 7.2 | AOA CPM engine | Forward pass (earliest event times), backward pass (latest event times), float calculation per arrow/activity, critical path identification on AOA graph. Must produce identical critical path to AON for same project | Same file — CPM methods | ⬜ |
| 7.3 | Dummy activity insertion | Algorithm to insert dummy activities where needed: (1) when two activities share same start AND end event, (2) to enforce dependency logic that can't be represented without dummies. Follow the merge/burst node rules from PM textbooks | Same file — `insert_dummies()` | ⬜ |
| 7.4 | AON → AOA converter | Given an AON network (activity list with predecessors), generate the equivalent AOA network with proper event numbering and dummy insertion. Validate: same critical path, same floats | `core/network_converter.py` (NEW) | ⬜ |
| 7.5 | AOA → AON converter | Reverse conversion: given AOA events + arrows, extract activity list with predecessors. Strip dummy activities | Same file — reverse method | ⬜ |
| 7.6 | AOA input mode in Input tab | Toggle in Input Activities tab: "Network Type: AON / AOA". In AOA mode, input changes to: Event-based entry (From Event, To Event, Activity, Duration) instead of predecessor-based. Both modes maintained simultaneously; switching converts automatically | `gui/tabs/input_tab_edu.py` — mode toggle | ⬜ |
| 7.7 | AOA visualization | vis.js network diagram in AOA style: numbered circles (events) connected by labeled arrows (activities). Dummies shown as dashed arrows. Event nodes show ET/LT. Critical path arrows highlighted in red | `gui/tabs/network_tab.py` — AOA renderer | ⬜ |
| 7.8 | Network tab mode toggle | Add "View: AON / AOA" toggle in Network Diagram tab. Switching re-renders the same project in the other representation. Both views coexist | `gui/tabs/network_tab.py` — toggle button | ⬜ |
| 7.9 | AOA PERT diagram | If PERT data available, show AOA with 4-compartment event nodes (Event#, ET, LT, Slack) | `gui/tabs/pert_diagram_tab.py` — AOA mode | ⬜ |
| 7.10 | AOA worked solutions | Step-by-step: (1) How to number events, (2) When dummies are needed (rules), (3) Forward pass on AOA, (4) Backward pass, (5) Identifying critical path on arrows. Side-by-side AON vs AOA comparison | `core/aoa_step_generator.py` (NEW) | ⬜ |
| 7.11 | AOA "Try It Yourself" | Give an activity list; student draws AOA (assigns events, identifies dummies); validate event numbering and critical path | Network tab — practice mode | ⬜ |
| 7.12 | AOA demo file | `data/demos/v2/aoa_demo.json` — project with known AOA representation, including required dummy activities | `data/demos/v2/aoa_demo.json` (NEW) | ⬜ |
| 7.13 | Unit tests — AOA | AOA CPM correctness (vs AON), dummy insertion correctness, converter round-trip (AON→AOA→AON = original), edge cases (parallel activities, complex dependencies) | `tests/test_aoa_network.py` (NEW) | ⬜ |

---

## Phase 8 — Resource Leveling Educational Enhancements

> **Goal:** Enhance the existing RCPS tab with educational walkthrough showing smoothing vs constrained leveling, step-by-step algorithm visualization, and before/after comparison.
> **Existing code:** `MinimumMomentLeveling`, `BurgessLeveling` in `core/resource_leveling.py`; RCPS tab with schedule + histogram in `gui/tabs/rcps_tab_edu.py`.
> **Decision:** Add educational sub-tab to existing RCPS tab.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 8.1 | Smoothing vs Constrained distinction | Add clear mode selector: **Resource Smoothing** (minimize peak within float, don't extend project) vs **Resource Constrained** (enforce limits, may extend project). Document the difference in tooltips and educational panel | `gui/tabs/rcps_tab_edu.py` — mode selector | ⬜ |
| 8.2 | Step-by-step walkthrough sub-tab | **New sub-tab 3:** Animated/stepped walkthrough of the leveling algorithm. Show: (1) Initial resource histogram (before), (2) Each scheduling decision with explanation ("Activity X delayed by 2 periods because resource R exceeds limit"), (3) Final histogram (after). Slider or "Next Step"/"Previous Step" buttons | `gui/tabs/rcps_tab_edu.py` — new sub-tab | ⬜ |
| 8.3 | Leveling step recorder | Modify `MinimumMomentLeveling` and `BurgessLeveling` to emit step-by-step events: which activity was considered, what decision was made, what the resource profile looks like after each step. Store as list of `LevelingStep` dataclasses | `core/resource_leveling.py` — add step recording | ⬜ |
| 8.4 | Before/after comparison | Side-by-side histograms: left = original schedule resources, right = leveled schedule. Metrics comparison: RMS deviation, peak usage, project duration (delta if constrained extended it) | `gui/tabs/rcps_tab_edu.py` — comparison panel | ⬜ |
| 8.5 | Leveling metrics panel | Display: Minimum Moment value (before/after), Burgess metric, Resource utilization %, Peak-to-average ratio. Explain what each metric means | Same sub-tab — metrics section | ⬜ |
| 8.6 | Resource leveling worked solutions | Step-by-step educational content: (1) What is resource leveling, (2) Smoothing vs Constrained, (3) Minimum Moment algorithm explanation, (4) Burgess algorithm explanation, (5) When to use which | `core/leveling_step_generator.py` (NEW) | ⬜ |
| 8.7 | Resource leveling "Try It Yourself" | Small project (5 activities, 1 resource); student manually adjusts start times to reduce peak; app validates total moment reduction | `gui/tabs/rcps_tab_edu.py` — practice frame | ⬜ |
| 8.8 | Resource leveling demo file | `data/demos/v2/resource_leveling_demo.json` — project designed to show clear leveling benefit (high initial peak, ample float) | `data/demos/v2/resource_leveling_demo.json` (NEW) | ⬜ |
| 8.9 | Unit tests — leveling education | Test step recorder output, before/after metrics computation, smoothing-only mode (verify project not extended) | `tests/test_leveling_education.py` (NEW) | ⬜ |

---

## Phase 9 — Web Porting (Angular)

> **Goal:** Port all new desktop features to the Angular web app.
> **Decision:** Desktop first; web porting follows after all desktop features are stable.
> **Scope:** Port Phases 2–8 features to Angular standalone components with D3.js charts.

| #   | Task | What to Do | Files | Status |
| --- | ---- | ---------- | ----- | ------ |
| 9.1 | Three-Point Estimates component | Angular standalone component with reactive forms for O/M/P input, D3.js line chart, worked solution accordion | `web/src/app/features/three-point/` (NEW) | ⬜ |
| 9.2 | Financial Analysis component | Sub-routed component with Financial Calculators + Factor Scoring child components. Reactive forms, D3.js bar charts | `web/src/app/features/financial/` (NEW) | ⬜ |
| 9.3 | RACI Matrix component | Editable grid component (virtual scroll for large matrices), color-coded cells, validation messages | `web/src/app/features/raci/` (NEW) | ⬜ |
| 9.4 | Cost Estimation component | 7-method tabbed component with dynamic forms per technique, D3.js comparison chart | `web/src/app/features/cost-estimation/` (NEW) | ⬜ |
| 9.5 | Risk Assessment & Response components | Extend existing risk feature: add assessment matrix (D3.js heat map), response planning form, effectiveness dashboard | `web/src/app/features/risk/` (extend) | ⬜ |
| 9.6 | AOA Network component | vis.js AOA renderer, mode toggle, converter integration | `web/src/app/features/network/` (extend) | ⬜ |
| 9.7 | Resource Leveling walkthrough component | Step-by-step animation with D3.js histograms, before/after comparison | `web/src/app/features/resources/` (extend) | ⬜ |
| 9.8 | Navigation refactor for tab groups | Angular router restructure: `/schedule/*`, `/cost/*`, `/risk/*`, `/strategic/*` with collapsible sidebar navigation | `web/src/app/app.routes.ts` | ⬜ |
| 9.9 | Web E2E tests | Cypress tests for all new features | `web/cypress/e2e/v2/` (NEW) | ⬜ |
| 9.10 | Web deployment update | Update Render config, test production build with new features | `render.yaml`, `Dockerfile` | ⬜ |

---

## Phase 10 — Integration, QA & Release

> **Goal:** Final integration testing, documentation, and release.

| #    | Task | What to Do | Files | Status |
| ---- | ---- | ---------- | ----- | ------ |
| 10.1 | Cross-feature integration tests | Test workflows that span multiple features: e.g., create project → load into financial calcs → load into RACI → risk analysis → leveling | `tests/test_v2_integration.py` (NEW) | ⬜ |
| 10.2 | Backward compatibility test | Verify all V1 `.pmproj` files load correctly with new Risk fields defaulting gracefully; V1 demos still work | `tests/test_backward_compat.py` (NEW) | ⬜ |
| 10.3 | UI smoke test (desktop) — V2 | Extended checklist covering all new tabs, sub-tabs, and modes | `UI_SMOKE_TEST_CHECKLIST_V2.md` (NEW) | ⬜ |
| 10.4 | PyInstaller build + test | Rebuild `.exe` with all new modules; verify launch and feature access | Build scripts | ⬜ |
| 10.5 | Update README.md | Document all new features with screenshots | `README.md` | ⬜ |
| 10.6 | Update CHANGELOG.md | Add `[2.0.0]` entry with all new features | `CHANGELOG.md` | ⬜ |
| 10.7 | Tag `v2.0.0` + GitHub Release | Annotated tag, release notes, attach `.exe` | Git | ⬜ |
| 10.8 | Deploy web V2 to Render | Production deploy with all web-ported features | Render | ⬜ |

---

## Key Decisions Log (V2)

| #  | Decision | Answer | Reasoning |
| -- | -------- | ------ | --------- |
| 1  | Standalone vs Integrated calculators? | **Both** — standalone + "Load from Project" button | Students need to practice textbook problems AND apply to real projects |
| 2  | RACI matrix scope? | **Both** — auto-populate from activities + free-form grid | Covers both real-project use and textbook exercises |
| 3  | AON/AOA depth? | **Both modes** — full AON and AOA input with bidirectional conversion | PM curriculum requires understanding both representations |
| 4  | Web app scope for V2? | **Desktop first, web later in V2** | Get features right on desktop, then port to Angular |
| 5  | Educational depth? | **Full + practice mode** — worked solutions + "Try It Yourself" | Maximizes learning value; consistent with V1's educational model |
| 6  | Risk Response integration? | **Both** — extend register columns + separate detailed sub-tab | Quick view in register; deep planning in dedicated sub-tab |
| 7  | Tab overflow strategy? | **Collapsible tab groups** (Schedule, Cost, Risk, Strategic) | Organizes 25+ tabs into navigable categories |
| 8  | Demo data approach? | **New separate demo files** for V2 features | Don't break V1 demos; each feature gets purpose-built examples |
| 9  | Start from `feat/web-v1` or `production`? | Continue on `feat/web-v1` until PR #3 merges | Branch from production after merge |
| 10 | Web auth for V2? | No | Single-user educational tool; defer auth to V2.1+ |

---

## New Files Summary

### Core Engines (10 new files)
| File | Phase | Purpose |
| ---- | ----- | ------- |
| `core/three_point_engine.py` | 2 | PERT + Triangular three-point calculations |
| `core/financial_calcs.py` | 3A | Payback, Disc. Payback, ROI, NPV, IRR, PI |
| `core/factor_scoring.py` | 3B | Unweighted 0-1, Unweighted Factor, Weighted Factor |
| `core/raci_model.py` | 4 | RACI matrix dataclass + validation |
| `core/cost_estimation.py` | 5 | 7 cost estimation technique classes |
| `core/aoa_network_builder.py` | 7 | AOA network + CPM + dummy insertion |
| `core/network_converter.py` | 7 | AON ↔ AOA bidirectional converter |
| `core/three_point_step_generator.py` | 2 | Three-point worked solutions |
| `core/financial_step_generator.py` | 3A | Financial calc worked solutions |
| `core/factor_scoring_step_generator.py` | 3B | Factor scoring worked solutions |
| `core/raci_step_generator.py` | 4 | RACI worked solutions |
| `core/cost_estimation_step_generator.py` | 5 | Cost estimation worked solutions |
| `core/risk_step_generator.py` | 6 | Risk assessment worked solutions |
| `core/aoa_step_generator.py` | 7 | AOA network worked solutions |
| `core/leveling_step_generator.py` | 8 | Resource leveling worked solutions |

### GUI Tabs (5 new files, 4 modified)
| File | Phase | Action |
| ---- | ----- | ------ |
| `gui/widgets/tab_group_notebook.py` | 1 | NEW — collapsible tab group widget |
| `gui/widgets/educational_calculator_tab.py` | 1 | NEW — base class for educational calculators |
| `gui/tabs/three_point_tab_edu.py` | 2 | NEW (replaces empty stub `pert_tab_edu.py`) |
| `gui/tabs/financial_tab_edu.py` | 3 | NEW (replaces empty stub `selection_tab.py`) |
| `gui/tabs/raci_tab_edu.py` | 4 | NEW |
| `gui/tabs/cost_estimation_tab_edu.py` | 5 | NEW |
| `gui/tabs/risk_tab_edu.py` | 6 | MODIFY — add 2 sub-tabs |
| `gui/tabs/rcps_tab_edu.py` | 8 | MODIFY — add educational sub-tab |
| `gui/tabs/network_tab.py` | 7 | MODIFY — add AOA mode |
| `gui/tabs/input_tab_edu.py` | 7 | MODIFY — add AON/AOA toggle |

### Demo Data (7 new files)
| File | Phase |
| ---- | ----- |
| `data/demos/v2/three_point_demo.json` | 2 |
| `data/demos/v2/financial_demo.json` | 3A |
| `data/demos/v2/factor_scoring_demo.json` | 3B |
| `data/demos/v2/raci_demo.json` | 4 |
| `data/demos/v2/cost_estimation_demo.json` | 5 |
| `data/demos/v2/risk_assessment_demo.json` | 6 |
| `data/demos/v2/aoa_demo.json` | 7 |
| `data/demos/v2/resource_leveling_demo.json` | 8 |

### Tests (9 new files)
| File | Phase |
| ---- | ----- |
| `tests/test_three_point.py` | 2 |
| `tests/test_financial_calcs.py` | 3A |
| `tests/test_factor_scoring.py` | 3B |
| `tests/test_raci.py` | 4 |
| `tests/test_cost_estimation.py` | 5 |
| `tests/test_risk_assessment.py` | 6 |
| `tests/test_aoa_network.py` | 7 |
| `tests/test_leveling_education.py` | 8 |
| `tests/test_v2_integration.py` | 10 |
| `tests/test_backward_compat.py` | 10 |

### Utilities (2 new files)
| File | Phase |
| ---- | ----- |
| `utils/demo_loader.py` | 1 |
| `data/demos/v2/` (directory) | 1 |

---

## V2+ Roadmap (Future)

| Feature | Target | Status |
| ------- | ------ | ------ |
| Portfolio Management (multi-project dashboard) | V2.1+ | ⬜ Planning |
| Collaborative Features (multi-user editing) | V2.2+ | ⬜ Planning |
| Predictive ML (duration estimation from history) | V3 | ⬜ Research |
| Mobile Applications (iOS/Android) | V3 | ⬜ Research |

---

## Definition of Done (V2 Release)

- [ ] All V1 deferred items completed (Phase 0)
- [ ] Tab group refactor working with all 25+ tabs (Phase 1)
- [ ] Three-Point Estimates tab with chart, worked solution, Try It Yourself (Phase 2)
- [ ] Financial Analysis: 6 calculators + 3 factor scoring models + worked solutions (Phase 3)
- [ ] RACI matrix with auto-populate + free-form + validation (Phase 4)
- [ ] Cost Estimation: 7 techniques with worked solutions (Phase 5)
- [ ] Risk Assessment Matrix + Risk Response Planning sub-tabs (Phase 6)
- [ ] AON/AOA dual mode with conversion + AOA visualization (Phase 7)
- [ ] Resource Leveling: smoothing/constrained modes + step walkthrough (Phase 8)
- [ ] All new features have "Try It Yourself" practice mode
- [ ] All new features have dedicated demo files
- [ ] All new features have unit tests
- [ ] All V1 tests (797+) still pass
- [ ] Backward compatibility with V1 `.pmproj` files verified
- [ ] PyInstaller bundle builds and runs on clean machine
- [ ] CHANGELOG.md updated with `[2.0.0]` entry
- [ ] GitHub Release tagged `v2.0.0`
