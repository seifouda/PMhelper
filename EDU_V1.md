# PMhelper Edu — Version 1 Implementation Plan

> **Scope:** All features marked 🎯 V1 in `FEATURES_LIST_EDU.md`
> **Approach:** 1 developer with AI agent assistance
> **Total Estimated Time:** ~17 weeks
> **Date Drafted:** March 7, 2026

---

## Quick Reference: V1 Feature List

| #   | Feature                                           | Current Status | Phase      |
| --- | ------------------------------------------------- | -------------- | ---------- |
| 1   | Gantt Chart                                       | ✅ Ready       | — (adapt)  |
| 2   | Critical Path Network Diagram                     | ✅ Ready       | — (adapt)  |
| 3   | Earned Value S-Curve Chart                        | ❌ Not built   | Phase 2    |
| 4   | Risk Impact-Probability Matrix                    | ❌ Not built   | Phase 3    |
| 5   | Advanced Gantt / Tracking Gantt                   | ⚠️ Semi-ready  | Phase 4    |
| 6   | Risk Probability Distribution Chart               | ⚠️ Semi-ready  | Phase 4    |
| 7   | Resource & Cost Histograms                        | ⚠️ Semi-ready  | Phase 4    |
| 8   | All 11 Undergraduate EVM KPIs                     | ❌ Not built   | Phase 2    |
| 9   | TCPI toward BAC (Postgrad)                        | ❌ Not built   | Phase 2    |
| 10  | Schedule Probability of Success                   | ✅ Ready       | — (adapt)  |
| 11  | Aggregate Risk Exposure                           | ❌ Not built   | Phase 3    |
| 12  | Monte Carlo P50/P90 Finish Date                   | ⚠️ Semi-ready  | Phase 4    |
| 13  | Probability of Meeting Budget                     | ❌ Not built   | Phase 4    |
| 14  | CPM Calculation                                   | ✅ Ready       | — (adapt)  |
| 15  | Float / Slack                                     | ✅ Ready       | — (adapt)  |
| 16  | EV Computation                                    | ❌ Not built   | Phase 2    |
| 17  | Schedule & Cost Variances (SV, CV, SPI, CPI)      | ❌ Not built   | Phase 2    |
| 18  | EAC (2 formulas)                                  | ❌ Not built   | Phase 2    |
| 19  | VAC                                               | ❌ Not built   | Phase 2    |
| 20  | TCPI (undergraduate)                              | ❌ Not built   | Phase 2    |
| 21  | Risk Exposure (RE = p×I)                          | ❌ Not built   | Phase 3    |
| 22  | PERT Three-Point Estimation                       | ✅ Ready       | — (adapt)  |
| 23  | Advanced EAC (3rd formula: CPI×SPI)               | ❌ Not built   | Phase 2    |
| 24  | Cost of Risk / Contingency Reserve                | ⚠️ Semi-ready  | Phase 3    |
| 25  | Schedule Compression / Crashing                   | ✅ Ready       | — (adapt)  |
| 26  | Monte Carlo Simulation (full N-trial)             | ⚠️ Semi-ready  | Phase 4    |
| 27  | Probabilistic Critical Path                       | ⚠️ Semi-ready  | Phase 4    |
| 28  | Aggregate Risk Exposure (postgrad)                | ❌ Not built   | Phase 3    |
| 29  | WBS task entry                                    | ⚠️ Semi-ready  | Phase 1    |
| 30  | Period-by-period PV/EV/AC data entry              | ❌ Not built   | Phase 1    |
| 31  | Risk register entry (p, I, description)           | ❌ Not built   | Phase 3    |
| 32  | CSV / Excel import-export                         | ✅ Ready       | — (extend) |
| 33  | Project save / load (JSON)                        | ✅ Ready       | — (extend) |
| 34  | Sample / demo datasets (UG + PG)                  | ⚠️ Semi-ready  | Phase 5    |
| 35  | UG / PG mode toggle                               | ❌ Not built   | Phase 5    |
| 36  | Step-by-step calculation walkthrough              | ❌ Not built   | Phase 5    |
| 37  | RAG color coding on all KPIs                      | ❌ Not built   | Phase 2    |
| 38  | Tabbed layout (Input/CPM/EVM/Risk/PERT/Dashboard) | ✅ Ready       | — (extend) |
| 39  | Export charts as PNG/PDF                          | ⚠️ Semi-ready  | Phase 5    |

---

## Architecture Overview

The new app is built as a standalone Python desktop app (Tkinter), reusing the existing PMhelper codebase with new modules added alongside.

```
src/pmhelper/
├── core/
│   ├── cpm_analyzer.py         ✅ reuse
│   ├── pert_analyzer.py        ✅ reuse
│   ├── cost_optimization.py    ✅ reuse (crashing)
│   ├── evm_engine.py           ❌ NEW  ← Phase 1 core blocker
│   ├── risk_register.py        ❌ NEW  ← Phase 3
│   └── monte_carlo.py          ⚠️ extend ← Phase 4
├── gui/tabs/
│   ├── input_tab.py            ⚠️ extend (add EVM data entry)
│   ├── gantt_tab.py            ⚠️ extend (baseline + % complete)
│   ├── network_tab.py          ✅ reuse
│   ├── evm_tab.py              ❌ NEW  ← Phase 2
│   ├── risk_tab.py             ⚠️ extend (add register + heat map)
│   ├── pert_tab.py             ✅ reuse
│   ├── probability_tab.py      ✅ reuse
│   ├── crashing_tab.py         ✅ reuse
│   ├── resource_tab.py         ⚠️ extend (adapt histograms)
│   └── dashboard_tab.py        ❌ NEW  ← Phase 5
└── utils/
    ├── evm_io.py               ❌ NEW  ← Phase 1
    └── risk_io.py              ❌ NEW  ← Phase 3
```

---

## Phase 0 — Project Setup & Repo Branch

**Duration: 0.5 weeks**
**Depends on: nothing**

### Tasks

| Task                                  | Details                                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Create new branch `feat/edu-v1`       | Branch off `production`; this is the dedicated V1 development branch                                                            |
| Scaffold new files (empty stubs)      | Create `evm_engine.py`, `risk_register.py`, `evm_tab.py`, `dashboard_tab.py`, `evm_io.py`, `risk_io.py` with blank class shells |
| Confirm existing modules load cleanly | Run existing tests; fix any import issues from new empty files                                                                  |
| Set up V1 test file                   | Create `tests/test_evm.py`, `tests/test_risk_register.py` as empty test suites                                                  |

### Deliverable

Clean project structure with all new files in place and existing tests still passing.

---

## Phase 1 — EVM Data Model & Input Layer

**Duration: 2 weeks**
**Depends on: Phase 0**
**Blocks: Phase 2 (all EVM calculations depend on this data model)**

This is the single most critical phase. Every EVM KPI, chart, and calculation depends on having a well-designed data model for time-phased project data.

### Tasks

#### 1.1 — EVM Data Model (`core/evm_engine.py`)

Design and implement the data structures:

```python
class EVMProject:
    bac: float                        # Budget at Completion
    periods: List[str]                # e.g. ["Week 1", "Week 2", ...]
    tasks: List[EVMTask]

class EVMTask:
    name: str
    budget: float                     # task budget (for EV calc)
    pct_complete: float               # reported % complete (0–100)
    ev: float                         # computed: budget × pct_complete / 100

class EVMPeriod:
    label: str
    pv_cumulative: float              # planned value to date
    ev_cumulative: float              # earned value to date
    ac_cumulative: float              # actual cost to date
```

- Validate: PV and AC must be non-negative; % complete 0–100
- Compute period-by-period deltas from cumulative inputs
- Serialize to / from JSON (for save/load)

#### 1.2 — WBS Task Input UI (extend `gui/tabs/input_tab.py`)

- Add "Budget ($)" column to the existing task table
- Add "% Complete" column (editable spinner 0–100)
- Validate % complete on entry
- Wire budget and % complete fields to `EVMTask` model

#### 1.3 — Period Data Entry UI (new panel in `input_tab.py`)

- Period table: columns are Period Label | Cumulative PV | Cumulative EV | Cumulative AC
- Add / remove periods with buttons
- Weekly / monthly label toggle
- Inline cell editing
- "Compute from Tasks" button: auto-generates PV from the task baseline schedule

#### 1.4 — EVM File I/O (`utils/evm_io.py`)

- `save_evm_project(project, filepath)` → JSON
- `load_evm_project(filepath)` → `EVMProject`
- `export_periods_to_csv(project, filepath)`
- `import_periods_from_csv(filepath)` → list of `EVMPeriod`
- Unit tests for round-trip save/load and CSV import

### Deliverable

A fully functional data entry screen for EVM project data (tasks with budgets + % complete, and a period table for PV/EV/AC). Data persists on save/load. No calculations yet.

---

## Phase 2 — EVM Calculation Engine & KPI Dashboard

**Duration: 3 weeks**
**Depends on: Phase 1**
**Blocks: Phase 4 (advanced Gantt uses % complete from EVM model)**

### Tasks

#### 2.1 — Core EVM Engine (`core/evm_engine.py`)

Implement all V1 EVM calculations as pure functions (no UI dependencies):

| Function                                      | Formula                                        |
| --------------------------------------------- | ---------------------------------------------- |
| `compute_ev(tasks)`                           | $EV = \sum Budget_i \times \%complete_i / 100$ |
| `compute_cv(ev, ac)`                          | $CV = EV - AC$                                 |
| `compute_sv(ev, pv)`                          | $SV = EV - PV$                                 |
| `compute_cpi(ev, ac)`                         | $CPI = EV / AC$                                |
| `compute_spi(ev, pv)`                         | $SPI = EV / PV$                                |
| `compute_pc(ev, bac)`                         | $PC = EV / BAC \times 100\%$                   |
| `compute_ps(ac, bac)`                         | $PS = AC / BAC \times 100\%$                   |
| `compute_cr(cpi, spi)`                        | $CR = CPI \times SPI$                          |
| `compute_eac_formula1(ac, bac, ev)`           | $EAC = AC + (BAC - EV)$                        |
| `compute_eac_formula2(bac, cpi)`              | $EAC = BAC / CPI$                              |
| `compute_eac_formula3(ac, bac, ev, cpi, spi)` | $EAC = AC + (BAC - EV) / (CPI \times SPI)$     |
| `compute_vac(bac, eac)`                       | $VAC = BAC - EAC$                              |
| `compute_tcpi_bac(bac, ev, ac)`               | $TCPI = (BAC - EV) / (BAC - AC)$               |

- All functions raise `ZeroDivisionError` with descriptive message when denominator is 0
- All functions return `None` when inputs are missing
- Full unit test coverage in `tests/test_evm.py` with known-value assertions

#### 2.2 — RAG Thresholds

Define configurable RAG thresholds for each KPI:

| KPI  | Green | Amber            | Red           |
| ---- | ----- | ---------------- | ------------- |
| CV   | ≥ 0   | −5% of BAC to 0  | < −5% of BAC  |
| SV   | ≥ 0   | −5% of BAC to 0  | < −5% of BAC  |
| CPI  | ≥ 1.0 | 0.95–1.0         | < 0.95        |
| SPI  | ≥ 1.0 | 0.95–1.0         | < 0.95        |
| CR   | ≥ 0.9 | 0.8–0.9          | < 0.8         |
| TCPI | ≤ 1.1 | 1.1–1.2          | > 1.2         |
| EAC  | ≤ BAC | BAC to 1.1×BAC   | > 1.1×BAC     |
| VAC  | ≥ 0   | −10% of BAC to 0 | < −10% of BAC |

- Store thresholds in a config dict (user-editable in settings)
- `get_rag(kpi_name, value, bac) → "green" | "amber" | "red"`

#### 2.3 — EVM Tab (`gui/tabs/evm_tab.py`)

New tab with two sub-sections:

**Sub-section A: KPI Cards Panel**

- One card per KPI: name, formula hint, current value, RAG color badge, interpretation text
- Cards laid out in a 4-column grid
- Cards for: CV, SV, CPI, SPI, PC, PS, CR, EAC (×3 formulas side-by-side), VAC, TCPI
- "Recalculate" button triggers recompute from current period data

**Sub-section B: EV S-Curve Chart**

- Matplotlib figure embedded in the tab
- Three cumulative lines: PV (green), EV (blue), AC (red)
- X-axis: period labels; Y-axis: currency ($)
- Data point markers; legend
- Chart updates automatically when "Recalculate" is pressed
- Export button (PNG/PDF)

#### 2.4 — Step-by-Step Walkthrough Panel

A collapsible panel (shown in EVM tab) that, for any selected KPI:

- Displays the formula
- Shows the substitution with current values
- Shows the result with interpretation text

Example for CPI: `CPI = EV / AC = $40,000 / $44,000 = 0.91 → ⚠️ Cost overrun — spending $1.10 for every $1.00 of work done`

### Deliverable

Fully functional EVM KPI dashboard with all 11 undergrad KPIs + advanced EAC, RAG colour coding, EV S-Curve chart, and step-by-step walkthrough. All calculations unit-tested.

---

## Phase 3 — Risk Register & Heat Map

**Duration: 2 weeks**
**Depends on: Phase 0 (can be built in parallel with Phase 2)**
**No hard blockers**

### Tasks

#### 3.1 — Risk Register Data Model (`core/risk_register.py`)

```python
class Risk:
    id: str
    name: str
    description: str
    probability: float        # 0.0 – 1.0
    impact: float             # $ value
    exposure: float           # computed: probability × impact
    category: str             # optional: Schedule / Cost / Quality / etc.

class RiskRegister:
    risks: List[Risk]
    bac: float                # reference budget for threshold %

    def total_exposure(self) -> float
    def risks_by_exposure(self) -> List[Risk]          # sorted descending
    def flag_high_exposure(self, threshold_pct=0.05)   # flag if RE > 5% of BAC
    def contingency_reserve(self) -> float             # sum of all p×I
```

- Validate: probability 0–1; impact ≥ 0
- Unit tests in `tests/test_risk_register.py`

#### 3.2 — Risk Register File I/O (`utils/risk_io.py`)

- `save_register(register, filepath)` → JSON
- `load_register(filepath)` → `RiskRegister`
- `export_to_csv(register, filepath)`
- `import_from_csv(filepath)` → `RiskRegister`

#### 3.3 — Risk Register UI (extend `gui/tabs/risk_tab.py`)

Add a new sub-tab "Risk Register" alongside the existing delay-probability tabs:

- Table: ID | Name | Category | Probability | Impact ($) | Exposure (p×I) | Flag
- Add / Edit / Delete rows via dialogs
- "Exposure" column auto-computed on entry; highlighted red if > threshold
- "Total Exposure" and "Contingency Reserve" shown at bottom of table
- Ranked list: risks sorted by exposure (highest first)

#### 3.4 — Risk Impact-Probability Heat Map

A new sub-tab "Risk Matrix" in the risk tab:

- 5×5 grid rendered with Matplotlib `imshow` or `pcolor`
- Each cell color: green (low), yellow (medium), orange (high), red (very high)
- Probability on Y-axis (0.0–1.0 in 5 bands); Impact on X-axis ($ in 5 bands — auto-scaled)
- Each risk plotted as a labeled dot in its cell
- Clicking a dot shows risk details in a tooltip / side panel
- Export button (PNG/PDF)

#### 3.5 — Extend Contingency Reserve (extend existing `risk_analysis.py`)

- Connect new risk register's `contingency_reserve()` to the existing `ContingencyPlanner`
- Show both: schedule-delay contingency (existing) and p×I register contingency (new) side by side

### Deliverable

Fully functional risk register with CRUD, auto-computed RE = p×I, ranked exposure list, RAG flagging, and an interactive 5×5 heat map chart.

---

## Phase 4 — Monte Carlo, Advanced Gantt & Resource Histograms

**Duration: 3.5 weeks**
**Depends on: Phase 1 (EVM data model for % complete in Gantt), Phase 3 (risk register for cost distributions)**

### Tasks

#### 4.1 — Full Monte Carlo Engine (extend `core/pert_analyzer.py` or new `core/monte_carlo.py`)

The existing PERT analysis uses a normal approximation. Replace/extend with a true N-trial simulation:

```
ALGORITHM: Monte Carlo Simulation
INPUT: tasks with (O, M, P) estimates; N trials; BAC
OUTPUT: distribution of project duration and total cost

FOR trial = 1 to N:
    FOR each task:
        sample duration from PERT-beta distribution using O, M, P
        sample cost from triangular distribution using (min_cost, likely_cost, max_cost)
    run CPM on sampled durations → record project_duration, critical_path, total_cost
COLLECT: array of project_durations, array of total_costs, frequency of each task on CP
COMPUTE:
    P50_duration = 50th percentile of durations
    P90_duration = 90th percentile of durations
    P(T ≤ T_target) = count(duration ≤ T_target) / N
    P(cost ≤ BAC) = count(total_cost ≤ BAC) / N
    CP_frequency[task] = count(task on critical path) / N
```

- Default N = 5,000; user-configurable (500 – 50,000)
- Uses `numpy.random` for performance; falls back to `random` if numpy unavailable
- Progress bar during simulation (Tkinter `ttk.Progressbar`)
- Results cached; re-run only when inputs change

#### 4.2 — Monte Carlo Results UI (extend `gui/tabs/probability_tab.py`)

Add a new "Monte Carlo" section:

- Histogram of project durations with P50/P80/P90 markers
- Histogram of total costs with BAC line; P(cost ≤ BAC) annotation
- Probabilistic Critical Path table: task name | frequency on CP (%) | bar chart
- "Run Simulation" button with N input field

#### 4.3 — Advanced Gantt / Tracking Gantt (extend `gui/tabs/gantt_tab.py`)

Extension of the existing Gantt tab:

- **Baseline snapshot**: "Set Baseline" button records current planned start/end dates per task
- **Actual bars**: when % complete > 0, draw a coloured overlay on the task bar proportional to completion
- **Side-by-side columns**: add Baseline Start | Baseline End | Actual % columns to the task table
- **Tracking Gantt mode toggle**: switch between plain Gantt and Tracking Gantt views
- Existing critical path highlighting retained

#### 4.4 — Resource & Cost Histograms (adapt `gui/tabs/` resource views)

The existing resource leveling module generates histograms in a different context. Wire them into the new app's flow:

- "Resource Usage" chart: bar chart of resource-hours per period, derived from task assignments
- "Cost per Period" chart: bar chart of AC per period from EVM period data
- Both charts in a new "Resources" sub-tab within the existing Resource / Leveling tab
- Before/after leveling comparison toggle

#### 4.5 — Risk Probability Distribution Chart (extend `gui/tabs/probability_tab.py`)

Extend the existing PERT probability chart:

- Add a "Duration Distribution" histogram from Monte Carlo output (replaces or supplements the PERT normal curve)
- Overlay the PERT normal approximation curve for comparison (educational value)
- Add P50/P80/P90 vertical markers with labels

### Deliverable

Full Monte Carlo engine with N-trial sampling for both duration and cost; advanced tracking Gantt with baseline comparison and % complete shading; resource/cost histograms; enriched probability distribution chart.

---

## Phase 5 — UI Polish, Mode Toggle & Demo Data

**Duration: 2 weeks**
**Depends on: Phases 2, 3, 4 complete**

### Tasks

#### 5.1 — Undergraduate / Postgraduate Mode Toggle

A mode switcher in the main window toolbar or settings panel:

- **Undergraduate mode**: hides tabs/panels marked as postgraduate-only (Monte Carlo, Advanced EAC F3, TCPI toward BAC, Aggregate Risk, Probabilistic CP)
- **Postgraduate mode**: shows everything
- Mode persists across sessions (stored in app config JSON)
- Mode label shown in window title bar

Features visible in each mode:

| Feature             | UG Mode | PG Mode |
| ------------------- | ------- | ------- |
| Gantt Chart         | ✅      | ✅      |
| Network Diagram     | ✅      | ✅      |
| EV S-Curve          | ✅      | ✅      |
| Risk Matrix         | ✅      | ✅      |
| All 11 UG KPIs      | ✅      | ✅      |
| PERT Estimation     | ❌      | ✅      |
| Monte Carlo         | ❌      | ✅      |
| Advanced Gantt      | ❌      | ✅      |
| Probabilistic CP    | ❌      | ✅      |
| Advanced EAC F3     | ❌      | ✅      |
| TCPI toward BAC     | ❌      | ✅      |
| Aggregate Risk      | ❌      | ✅      |
| Resource Histograms | ❌      | ✅      |

#### 5.2 — Chart Export (PNG / PDF)

Extend the existing partial export to cover all charts:

- Each chart tab has an "Export" button
- Opens a `SaveAs` dialog defaulting to PNG; user can switch to PDF
- All Matplotlib figures use `fig.savefig(path, dpi=150, bbox_inches='tight')`
- Batch export: "Export All Charts" button in main menu → saves all current charts to a chosen folder

#### 5.3 — Sample / Demo Datasets

Create two complete sample projects that exercise every V1 feature:

**Undergraduate Demo: "Office Renovation Project"**

- 8 tasks, 3 dependencies, 10 periods
- Pre-filled: task budgets, % complete, cumulative PV/EV/AC, 5 risks with p and I
- Designed to produce: CPI < 1 (cost overrun), SPI < 1 (schedule delay), 2 critical risks

**Postgraduate Demo: "Software Development Project"**

- 12 tasks with O/M/P estimates, multiple resource types, 16 periods
- Pre-filled: full EVM data, 8 risks, three-point duration estimates
- Designed to produce: Monte Carlo P90 > planned duration, probabilistic CP shows 2 competing paths

Include "Load Demo" button on startup screen and in File menu.

#### 5.4 — Extend CSV/Excel Import-Export for New Data Types

Extend the existing import-export to cover EVM and risk data:

- EVM period data: `export_evm_periods_csv()`, `import_evm_periods_csv()`
- Risk register: `export_risks_csv()`, `import_risks_csv()`
- Combined project export: one Excel file with multiple sheets (Tasks | EVM Periods | Risk Register | Results)

### Deliverable

UG/PG mode toggle working; all charts exportable; two complete demo projects loadable from the app; CSV/Excel extended to cover all new data types.

---

## Phase 6 — Testing & Stabilization

**Duration: 2 weeks**
**Depends on: all phases**

### Tasks

#### 6.1 — Unit Tests

| Test File                     | Coverage Target                                                                       |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| `tests/test_evm.py`           | All 13 EVM functions; edge cases (ZeroDivision, missing data, BAC=0)                  |
| `tests/test_risk_register.py` | Risk CRUD, RE computation, ranking, flagging, contingency sum                         |
| `tests/test_monte_carlo.py`   | Deterministic seed runs, output shape, percentile correctness, convergence at N=10000 |
| `tests/test_evm_io.py`        | Round-trip JSON save/load; CSV import edge cases (empty, bad data)                    |
| `tests/test_rag.py`           | RAG threshold logic for all KPIs; boundary values                                     |

#### 6.2 — Integration Tests

- Load demo datasets → run all calculations → verify no exceptions
- UG/PG mode toggle → verify correct tabs shown/hidden
- Full EVM workflow: enter data → calculate → export chart → reload from JSON → values unchanged
- Risk register workflow: add risks → view heat map → export CSV → reimport → compare

#### 6.3 — Edge Case Handling

Verify graceful failures for:

- AC = 0 (divide-by-zero in CPI)
- BAC = 0
- All tasks at 0% complete
- No risks in register
- Single-task project (CPM trivial case)
- Monte Carlo with N = 1

#### 6.4 — UI Smoke Testing Checklist

Manual walkthrough against a printed checklist:

- [ ] App launches from cold start with no errors
- [ ] Load UG demo → all KPI cards populate correctly
- [ ] Load PG demo → Monte Carlo runs in < 30 seconds at N=5000
- [ ] Switch UG↔PG mode → correct features visible/hidden
- [ ] Export all charts to PNG → all files created and non-zero size
- [ ] Save project → close app → reopen → load project → all data present
- [ ] Risk heat map renders correctly with 8 risks

### Deliverable

All tests passing; known edge cases handled gracefully; smoke test checklist fully checked.

---

## Timeline Summary

```
Week 1–0.5  │ Phase 0: Setup & Scaffolding
Week 1–2.5  │ Phase 1: EVM Data Model & Input
Week 3–5    │ Phase 2: EVM Engine & KPI Dashboard
Week 3–5    │ Phase 3: Risk Register & Heat Map  ← parallel with Phase 2
Week 6–9.5  │ Phase 4: Monte Carlo, Advanced Gantt, Histograms
Week 10–12  │ Phase 5: UI Polish, Mode Toggle, Demo Data
Week 13–14  │ Phase 6: Testing & Stabilization
────────────────────────────────────────────────
TOTAL       │ ~17 weeks (1 developer + AI agents)
```

### Critical Path

```
Phase 0 → Phase 1 → Phase 2 → Phase 5 → Phase 6
                  ↗
          Phase 3
                  ↘
           Phase 4 ↗
```

Phase 1 is the hardest blocker — no EVM calculations can be built without it.
Phase 3 can run in parallel with Phase 2.
Phase 4 can start when Phase 1 is done and Phase 3 is in progress.

---

## Agent-Assisted Work Notes

Tasks where agent output can be used near-directly (high confidence):

- All pure formula functions in `evm_engine.py` (Phase 2.1)
- All data model classes and validators (Phase 1.1, 3.1)
- All file I/O (Phase 1.4, 3.2, 5.4)
- Unit test generation from function docstrings (Phase 6.1)
- RAG threshold logic (Phase 2.2)
- CSV import/export extensions (Phase 5.4)

Tasks requiring careful human review regardless of agent help:

- Monte Carlo engine correctness and convergence (Phase 4.1)
- Heat map cell boundary mapping (Phase 3.4)
- Tracking Gantt baseline snapshot logic (Phase 4.3)
- UG/PG mode tab show/hide wiring (Phase 5.1)
- Integration between EVM data model and chart rendering (Phase 2.3)

---

## Definition of Done (V1 Release)

- [ ] All 39 V1 features implemented and manually verified
- [ ] All unit and integration tests passing (`pytest` with 0 failures)
- [ ] Both demo datasets load without errors in UG and PG modes
- [ ] App launches from `pip install` and from standalone `.exe`
- [ ] All charts export correctly to PNG and PDF
- [ ] No known data-loss bugs on save/load cycle
- [ ] UG/PG mode toggle persists across sessions
