# PMhelper Edu — V1 Implementation Plan

> **Scope:** All 39 V1 features from `FEATURES_LIST_EDU.md`
> **Approach:** 1 developer + AI agent assistance
> **Estimated Calendar Time:** ~19 weeks (parallelism in Phases 2+3 recovers ~2 weeks; ~1 week buffer in Phase 4)
> **Date:** March 8, 2026

---

## Key Decisions Log

All 7 decisions are resolved here. Record any changes to these in `DECISIONS.md`.

| #   | Decision                                             | Answer                                                                                                                                                | Reasoning                                                                                                                                                                                                                           |
| --- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | CPM tasks vs. EVM tasks — same class or separate?    | **Separate classes. `EVMTask` has an optional `cpm_task_id` link.**                                                                                   | The existing CPM task model is tightly coupled to `cpm_analyzer.py` and `network_builder.py`. Extending it would drag those dependencies into EVM code. A separate `EVMTask` also allows EVM-only projects with no network.         |
| 2   | Monte Carlo — extend `pert_analyzer.py` or new file? | **New `core/monte_carlo.py`.**                                                                                                                        | `pert_analyzer.py` is already 759 lines with its own I/O contracts and point-estimate outputs. Monte Carlo needs distributions, threading, and progress callbacks — a completely different interface.                               |
| 3   | Data model base class — Pydantic or `@dataclass`?    | **Keep whatever the developer is comfortable with; plain Python `@dataclass` is fine.**                                                               | The existing Pydantic models are in `core/models.py` for the selection module only. EVM and Risk models are new and self-contained — no need to force Pydantic. Use `@dataclass` with manual validation methods; simpler to debug.  |
| 4   | Monte Carlo threading model?                         | **`threading.Thread` + `queue.Queue`.**                                                                                                               | Standard Tkinter threading pattern. Worker thread puts progress floats and the final result into a `Queue`; the main thread polls via `root.after(100, poll_queue)`. Do not call any Tkinter widget methods from the worker thread. |
| 5   | PV spreading rule for "Compute from Tasks"?          | **Uniform only** — budget divided evenly across all periods the task spans.                                                                           | Sufficient for undergraduate teaching; avoids introducing a confusing setting. Front/back-loaded spreading is out of scope for V1.                                                                                                  |
| 6   | Shared state between tabs?                           | **Single `EduProjectState` object owned by `MainWindow`, passed to each tab constructor.**                                                            | Avoids global variables and avoids N×N inter-tab references. The existing app already passes `main_window` to every tab — `EduProjectState` lives on `main_window.edu_state`.                                                       |
| 7   | Which EAC formula feeds VAC and TCPI?                | **All three EAC values are computed and stored. VAC and TCPI each have a dropdown to select which EAC to use. Default: EAC₁ for TCPI; EAC₂ for VAC.** | Keeps the tool pedagogically honest — students can see how the choice of EAC changes forecasts.                                                                                                                                     |

---

## First Day Checklist

Do these in order on Day 1 before writing any feature code.

1. Run `pytest` on the current `production` branch — record the baseline pass count. This is your regression baseline.
2. Create and switch to branch `feat/edu-v1` off `production`.
3. Open `DECISIONS.md` (create it if it doesn't exist) and confirm all 7 decisions above are written down.
4. Add `edu_state: EduProjectState` to `MainWindow.__init__()` in `main_window.py`. Create the `EduProjectState` class (stub only) in a new file `src/pmhelper/core/edu_state.py`. Confirm the app still launches.
5. Create all new module stubs (see Architecture section below). Each stub: module docstring + empty class with a `pass` body. Run `python -m pmhelper` — confirm no new import errors.
6. Create all new test files as empty suites. Run `pytest` — 0 new failures required.
7. Pick the simplest new tab to add first (EVM Input panel in `input_tab.py`) and write its empty `_create_evm_panel()` method. This proves the extension pattern works before real work starts.

---

## Architecture Map

The Edu features are added **to the existing `MainWindow` and existing tabs** — not to a separate app entry point. New modules are added to the existing `src/pmhelper/` package.

```
src/pmhelper/
├── core/
│   ├── cpm_analyzer.py          ✅ reuse unchanged
│   ├── pert_analyzer.py         ✅ reuse unchanged
│   ├── cost_optimization.py     ✅ reuse unchanged (crashing)
│   ├── edu_state.py             ❌ NEW  ← Phase 0  (EduProjectState + AppConfig)
│   ├── evm_models.py            ❌ NEW  ← Phase 1  (EVMTask, EVMPeriod, EVMProject)
│   ├── evm_calculations.py      ❌ NEW  ← Phase 2  (pure KPI functions + RAG)
│   ├── risk_register.py         ❌ NEW  ← Phase 3  (Risk, RiskRegister)
│   └── monte_carlo.py           ❌ NEW  ← Phase 4  (MCInputs, MCResults, runner)
├── gui/
│   ├── main_window.py           ⚠️ extend (add edu_state; add new tabs; add mode toggle)
│   └── tabs/
│       ├── input_tab.py         ⚠️ extend (add EVM panel + period table as new sub-section)
│       ├── gantt_tab.py         ⚠️ extend (baseline snapshot + % complete overlay)
│       ├── network_tab.py       ✅ reuse unchanged
│       ├── evm_tab.py           ❌ NEW  ← Phase 2
│       ├── risk_tab.py          ⚠️ extend (add Risk Register sub-tab + Heat Map sub-tab)
│       ├── pert_tab.py          ✅ reuse unchanged
│       ├── probability_tab.py   ⚠️ extend (add Monte Carlo sub-tab)
│       ├── crashing_tab.py      ✅ reuse unchanged
│       ├── rcps_tab.py          ⚠️ extend (add Cost/Resource Histogram sub-tab)
│       └── dashboard_tab.py     ❌ NEW  ← Phase 5  (project health summary)
└── utils/
    ├── evm_io.py                ❌ NEW  ← Phase 1
    ├── risk_io.py               ❌ NEW  ← Phase 3
    ├── project_io.py            ❌ NEW  ← Phase 5  (combined .pmproj save/load)
    └── chart_export.py          ❌ NEW  ← Phase 5  (reusable ExportButton)
```

**Tab structure inside `MainWindow` after V1:**

```
Input Activities   — extended with EVM data entry panel
Results            — unchanged
Network Diagram    — unchanged
PERT Diagram       — unchanged
Gantt Chart        — extended with Tracking Gantt mode
EVM Dashboard      — NEW (Phase 2)
Risk Analysis      — extended with Register + Heat Map sub-tabs
Probability        — extended with Monte Carlo sub-tab
Crashing           — unchanged
RCPS               — extended with Histogram sub-tab
RCPS Crashing      — unchanged
Dashboard          — NEW (Phase 5)
...existing tabs unchanged...
```

---

## Data Model Specification

Full specification so a developer can start Phase 1 immediately with no open architectural questions.

```python
# src/pmhelper/core/evm_models.py

from dataclasses import dataclass, field
from typing import List, Optional, Literal

@dataclass
class EVMTask:
    task_id:          str                          # unique within project
    name:             str
    budget:           float                        # this task's share of BAC (>= 0)
    pct_complete:     float = 0.0                  # 0.0 – 100.0
    planned_start:    int   = 0                    # 0-based period index
    planned_finish:   int   = 0                    # >= planned_start
    actual_start:     Optional[int] = None
    actual_finish:    Optional[int] = None
    baseline_start:   Optional[int] = None         # set by "Set Baseline" button
    baseline_finish:  Optional[int] = None
    cpm_task_id:      Optional[str] = None         # optional link to CPM network task

    @property
    def ev(self) -> float:
        return self.budget * self.pct_complete / 100.0

    def validate(self):
        """Call before saving. Raises ValueError on invalid data."""
        if self.budget < 0:
            raise ValueError(f"Task '{self.name}': budget must be >= 0")
        if not 0.0 <= self.pct_complete <= 100.0:
            raise ValueError(f"Task '{self.name}': pct_complete must be 0–100")
        if self.planned_finish < self.planned_start:
            raise ValueError(
                f"Task '{self.name}': planned_finish must be >= planned_start")

@dataclass
class EVMPeriod:
    index:          int                            # 0-based sort key
    label:          str                            # e.g. "Week 1", "Month 3"
    pv_cumulative:  float = 0.0                    # planned value to this period (>= 0)
    ev_cumulative:  float = 0.0                    # earned value to this period (>= 0)
    ac_cumulative:  float = 0.0                    # actual cost to this period (>= 0)
    ev_source:      Literal["manual", "computed"] = "manual"
    # "computed" means EV was auto-generated from task % complete;
    # "manual" means the user typed it in directly.

@dataclass
class EVMProject:
    project_name:    str          = "New Project"
    bac:             float        = 0.0            # Budget at Completion
    currency_symbol: str          = "$"
    periods:         List[EVMPeriod]  = field(default_factory=list)
    tasks:           List[EVMTask]    = field(default_factory=list)

    # --- Convenience accessors ---

    def current_pv(self) -> float:
        return self.periods[-1].pv_cumulative if self.periods else 0.0

    def current_ev(self) -> float:
        return self.periods[-1].ev_cumulative if self.periods else 0.0

    def current_ac(self) -> float:
        return self.periods[-1].ac_cumulative if self.periods else 0.0

    def task_ev(self) -> float:
        """EV computed bottom-up from task % complete × budget."""
        return sum(t.ev for t in self.tasks)

    def ev_discrepancy(self) -> float:
        """Non-zero means period-level EV and task-level EV disagree."""
        return abs(self.task_ev() - self.current_ev())

    def compute_pv_schedule(self) -> List[float]:
        """
        Uniform PV spreading: each task's budget is split evenly across
        the periods it spans (planned_start to planned_finish inclusive).
        Returns a list of per-period cumulative PV values (same length as
        self.periods).
        """
        n = len(self.periods)
        if n == 0:
            return []
        pv_per_period = [0.0] * n
        for task in self.tasks:
            start  = max(0, task.planned_start)
            finish = min(n - 1, task.planned_finish)
            span   = finish - start + 1
            if span <= 0:
                continue
            share  = task.budget / span
            for p in range(start, finish + 1):
                pv_per_period[p] += share
        # Cumulate
        cumulative = []
        running = 0.0
        for pv in pv_per_period:
            running += pv
            cumulative.append(running)
        return cumulative
```

```python
# src/pmhelper/core/edu_state.py

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Callable, Literal
from .evm_models import EVMProject

def _config_dir() -> Path:
    """Return OS-appropriate config directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home()
    return base / ".pmhelper_edu"

@dataclass
class AppConfig:
    mode:              Literal["ug", "pg"] = "ug"
    currency_symbol:   str                 = "$"
    last_project_path: Optional[str]       = None

    CONFIG_PATH = _config_dir() / "config.json"

    def save(self):
        import json
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.CONFIG_PATH.write_text(
            json.dumps({"mode": self.mode,
                        "currency_symbol": self.currency_symbol,
                        "last_project_path": self.last_project_path},
                       indent=2))

    @classmethod
    def load(cls) -> "AppConfig":
        import json
        if cls.CONFIG_PATH.exists():
            data = json.loads(cls.CONFIG_PATH.read_text())
            return cls(**data)
        return cls()   # defaults


class EduProjectState:
    """Single shared state object. Lives on MainWindow.edu_state."""

    def __init__(self):
        self.evm_project:   EVMProject      = EVMProject(bac=0.0)
        self.risk_register                  = None   # set in Phase 3
        self.mc_results                     = None   # set in Phase 4
        self.config:        AppConfig       = AppConfig.load()
        self._dirty:        bool            = False
        self._callbacks:    List[Callable]  = []

    def subscribe(self, callback: Callable):
        """Tabs call this in __init__ to be notified of state changes."""
        self._callbacks.append(callback)

    def mark_dirty(self):
        self._dirty = True
        for cb in self._callbacks:
            cb()

    def is_dirty(self) -> bool:
        return self._dirty

    def mark_clean(self):
        self._dirty = False
```

---

## Phase 0 — Setup & Scaffolding

**Duration: 0.5 weeks**
**Depends on: nothing**
**Blocks: all phases**
**Goal: Runnable app with all new files importable, baseline tests green, and Day 1 checklist complete.**

| Task                                                        | Detail                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Create branch `feat/edu-v1` off `production`                | —                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Add `edu_state: EduProjectState` to `MainWindow.__init__()` | One line + import; app must still launch cleanly                                                                                                                                                                                                                                                                                                                                                                                                       |
| Create `core/edu_state.py`                                  | `EduProjectState` + `AppConfig` as specified above                                                                                                                                                                                                                                                                                                                                                                                                     |
| Create all new module stubs                                 | `evm_models.py`, `evm_calculations.py`, `risk_register.py`, `monte_carlo.py`, `evm_tab.py`, `dashboard_tab.py`, `evm_io.py`, `risk_io.py`, `project_io.py`, `chart_export.py` — docstring + empty class only. **Import order matters:** `evm_models.py` must contain at minimum `class EVMProject: pass` and `class EVMTask: pass` before `edu_state.py` can be imported (it does `from .evm_models import EVMProject`). Create `evm_models.py` first. |
| Create empty test files                                     | `tests/test_evm_models.py`, `tests/test_evm_calculations.py`, `tests/test_risk_register.py`, `tests/test_monte_carlo.py`, `tests/test_evm_io.py`, `tests/test_rag.py`, `tests/test_app_config.py`                                                                                                                                                                                                                                                      |
| Baseline `pytest` run                                       | 0 new failures after scaffold                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Address `.exe` false-positive strategy (see note below)     | Document plan in `DECISIONS.md`                                                                                                                                                                                                                                                                                                                                                                                                                        |

**Note on `.exe` false-positive flagging:**
This is a known PyInstaller problem — unsigned executables from unknown publishers are flagged by Windows Defender and some AV products regardless of content. Mitigation options in priority order:

1. **Code signing certificate** — a cheap OV (organization validation) code-signing cert (~$70/year from Sectigo or DigiCert) eliminates the false-positive for most AV products. This is the correct long-term solution.
2. **Inno Setup / NSIS installer** — wrap the `.exe` in a signed installer (VirtusTotal score improves dramatically).
3. **Submit for AV vendor whitelisting** — Microsoft Defender has a free submission portal (`microsoft.com/en-us/wdsi/filesubmission`); most vendors do too. Takes 1–3 days.
4. **PyInstaller `--onedir` instead of `--onefile`** — a directory bundle gets flagged far less often than a single-file UPX-packed `.exe` because it looks less like malware packing.
5. **Short-term workaround for development** — distribute as a `.zip` of the `--onedir` output with a `README` explaining the AV issue and how to add an exception. Acceptable for beta/testing.

Add a task in Phase 5 to implement option 4 and document options 1–3 for the end user.

**Deliverable:** App launches, all stubs importable, tests green, `.exe` strategy documented.

---

## Phase 1 — EVM Data Model + Input Layer

**Duration: 3 weeks**
**Depends on: Phase 0**
**Blocks: Phase 2 (all KPI calculations), Phase 4.3 (Tracking Gantt needs task date fields)**

> **Why 3 weeks instead of 2:** The "Compute from Tasks" PV spreading algorithm, the period table UI with inline editing, and the EVM file I/O with round-trip tests are each larger than they first appear. Do not start Phase 2 until the data model is fully tested.

### 1.1 — EVMTask / EVMPeriod / EVMProject (`core/evm_models.py`)

Implement the exact data model specified in the Data Model section above. The `compute_pv_schedule()` method is mandatory and must have its own unit tests before the UI button is built.

Key validation rules:

- `budget >= 0`
- `pct_complete` in [0.0, 100.0]
- `planned_finish >= planned_start`
- All period `*_cumulative` values must be non-decreasing (warn, don't crash)

### 1.2 — Extend `InputTab` with EVM Data Entry

The existing `InputTab` already has a `ttk.Treeview` for CPM/PERT task data. Add a **new collapsible panel below the existing task table** — separate visually and functionally — for EVM data. This way:

- The existing CPM/PERT workflow is completely untouched
- EVM data is entered in the same tab (consistent with the existing app's single-input-tab design)
- Both datasets are visible at once on larger screens

The EVM panel contains **two sub-sections**, each a labelled `ttk.LabelFrame`:

**BAC Input:** A single `ttk.Entry` field labelled "Budget at Completion (BAC)" at the top of the EVM panel, writing directly to `evm_project.bac`. When the user presses Enter or the field loses focus, validate that `bac >= 0` and show a warning if `bac != sum(task.budget)` (see reconciliation rule below). This is the user-facing input for BAC — `EVMProject.bac` must not rely solely on task budgets.

**BAC ↔ Task Budget Reconciliation Rule:** If `abs(bac - sum(task.budget)) > 0.01`, show a yellow warning label: `"⚠ BAC ($X) ≠ sum of task budgets ($Y). Adjust task budgets or BAC."` This is a warning only — it does not block saving or calculations. `EVMProject.bac` is always used as the authoritative BAC for all KPI formulas.

**Sub-section A: Task Budgets & Progress**

A second `ttk.Treeview` (separate from the CPM tree, same tab):

| Column                  | Type             | Notes                                                                                                   |
| ----------------------- | ---------------- | ------------------------------------------------------------------------------------------------------- |
| Task ID                 | read-only        | auto-populated from the CPM task table above if a CPM analysis has been run; otherwise manually entered |
| Task Name               | read-only mirror | mirrors the activity name from the CPM table                                                            |
| Budget ($)              | editable         | double-click to edit; non-negative                                                                      |
| % Complete              | editable         | Spinbox 0–100                                                                                           |
| Planned Start (period)  | editable         | integer >= 0                                                                                            |
| Planned Finish (period) | editable         | integer >= planned start                                                                                |

A "Sync from CPM Tasks" button copies task IDs and names from the CPM table into this EVM table. If no CPM data is loaded, the user enters them manually.

**Re-sync behaviour when CPM data changes:** If the user edits tasks in the CPM table above (add, delete, rename), the EVM table does **not** auto-update — this avoids unexpected data loss. Instead, clicking "Sync from CPM Tasks" again merges changes: new CPM tasks are appended to the EVM table with budget=0; deleted CPM tasks are flagged with a `⚠ (CPM task deleted)` suffix in the Name column but preserved in the EVM table; renamed tasks update the mirror name. A confirmation dialog is shown: `"Sync will update N tasks. Budgets and % Complete are preserved. Continue?"`

**Sub-section B: Period PV / EV / AC Table**

A `ttk.Treeview` for period data:

| Column        | Type     | Notes                        |
| ------------- | -------- | ---------------------------- |
| #             | auto     | 0-based index                |
| Label         | editable | e.g. "Week 1"                |
| Cumul. PV ($) | editable | must be non-decreasing       |
| Cumul. EV ($) | editable | must be non-decreasing       |
| Cumul. AC ($) | editable | must be non-decreasing       |
| EV Source     | display  | "manual" or "computed" badge |

Buttons: **Add Period**, **Remove Period**, **Compute PV from Tasks** (calls `compute_pv_schedule()` and fills the PV column).

Warning label shown at the bottom when `evm_project.ev_discrepancy() > 0.01`: `"⚠ Period EV ($X) differs from task-level EV ($Y). Check % completes or edit period EV manually."`

### 1.3 — EVM File I/O (`utils/evm_io.py`)

```python
import json, csv
from pathlib import Path
from pmhelper.core.evm_models import EVMProject, EVMTask, EVMPeriod

def save_evm_project(project: EVMProject, filepath: str) -> None:
    """Serialise to JSON using dataclasses.asdict()."""

def load_evm_project(filepath: str) -> EVMProject:
    """Deserialise from JSON; reconstruct nested dataclass objects."""

def export_periods_to_csv(project: EVMProject, filepath: str) -> None:
    """Write one row per period: index, label, pv, ev, ac."""

def import_periods_from_csv(filepath: str) -> list:
    """Return list of EVMPeriod; skip rows with non-numeric values."""
```

Unit tests required before moving to Phase 2:

- Round-trip save/load: loaded project equals saved project
- CSV export then import: same period values
- Load with missing optional fields: no crash, uses defaults
- Load from non-existent file: raises `FileNotFoundError` with clear message

**Deliverable:** `InputTab` extended with EVM task + period tables. "Compute PV from Tasks" working. Save/load round-trip tested. No calculations yet.

---

## Phase 2 — EVM Calculation Engine & KPI Dashboard

**Duration: 3.5 weeks**
**Depends on: Phase 1**
**Blocks: Phase 4.3 (Tracking Gantt uses `pct_complete`)**

### 2.1 — Pure KPI Functions (`core/evm_calculations.py`)

All functions are **pure** — no imports of GUI, state, or I/O modules. All input comes from the `EVMProject` object or individual numeric parameters. This makes them trivial to unit-test.

| Function                              | Formula                              | Zero-denominator behaviour                            |
| ------------------------------------- | ------------------------------------ | ----------------------------------------------------- |
| `compute_ev(tasks)`                   | $\sum B_i \times pc_i / 100$         | returns 0.0 for empty list                            |
| `compute_cv(ev, ac)`                  | $EV - AC$                            | always defined                                        |
| `compute_sv(ev, pv)`                  | $EV - PV$                            | always defined                                        |
| `compute_cpi(ev, ac)`                 | $EV / AC$                            | raises `ValueError("AC is zero — CPI undefined")`     |
| `compute_spi(ev, pv)`                 | $EV / PV$                            | raises `ValueError("PV is zero — SPI undefined")`     |
| `compute_pc(ev, bac)`                 | $EV / BAC \times 100$                | raises `ValueError("BAC is zero")`                    |
| `compute_ps(ac, bac)`                 | $AC / BAC \times 100$                | raises `ValueError("BAC is zero")`                    |
| `compute_cr(cpi, spi)`                | $CPI \times SPI$                     | always defined                                        |
| `compute_eac1(ac, bac, ev)`           | $AC + (BAC - EV)$                    | always defined                                        |
| `compute_eac2(bac, cpi)`              | $BAC / CPI$                          | raises `ValueError("CPI is zero")`                    |
| `compute_eac3(ac, bac, ev, cpi, spi)` | $AC + (BAC - EV) / (CPI \times SPI)$ | raises `ValueError("CPI × SPI is zero")`              |
| `compute_vac(bac, eac)`               | $BAC - EAC$                          | always defined                                        |
| `compute_tcpi_bac(bac, ev, ac)`       | $(BAC - EV) / (BAC - AC)$            | raises `ValueError("BAC equals AC — TCPI undefined")` |

**`compute_all_kpis(project: EVMProject, primary_eac: int = 1) -> dict`**

Returns a flat dict with keys: `ev`, `pv`, `ac`, `bac`, `cv`, `sv`, `cpi`, `spi`, `pc`, `ps`, `cr`, `eac1`, `eac2`, `eac3`, `vac`, `tcpi_bac`, `primary_eac_value`. Any `ValueError` is caught per KPI; the value in the dict is `None` for that KPI and a second `errors` key maps KPI name → error message string. The UI reads this dict — the UI never calls individual compute functions directly.

### 2.2 — RAG Engine (`core/evm_calculations.py`)

```python
# RAG thresholds — define as module-level constants; user can override via AppConfig later
RAG_DEFAULTS = {
    "cpi":  {"amber_lower": 0.95, "green_lower": 1.0},
    "spi":  {"amber_lower": 0.95, "green_lower": 1.0},
    "cr":   {"amber_lower": 0.80, "green_lower": 0.90},
    "tcpi": {"amber_upper": 1.10, "red_upper": 1.20},
    # For CV, SV, VAC: thresholds are expressed as % of BAC
    "cv":   {"amber_pct": 0.05},   # CV in [-5% BAC, 0) = amber; < -5% BAC = red
    "sv":   {"amber_pct": 0.05},
    "vac":  {"amber_pct": 0.10},
    "eac":  {"amber_pct": 0.10},   # EAC in (BAC, 1.1×BAC] = amber; > 1.1×BAC = red
}

def get_rag(kpi: str, value: float, bac: float,
            thresholds: dict = None) -> str:
    """Returns 'green', 'amber', or 'red'. Returns 'grey' if value is None."""
```

**Critical boundary rule:** the boundary value itself goes to the _better_ band. `CPI = 0.95` → amber (not red). `CPI = 1.0` → green (not amber). Test every boundary in `tests/test_rag.py`.

### 2.3 — EVM Tab (`gui/tabs/evm_tab.py`)

New tab added to `MainWindow` in `create_main_interface()` after the Gantt tab.

The tab has two sub-tabs (inner `ttk.Notebook`):

**Sub-tab A: KPI Cards**

- 4-column grid of `ttk.LabelFrame` cards
- Each card contains: KPI name (bold), formula in small grey text, current value (large), RAG badge (`tk.Label` with background colour), one-line interpretation text
- EAC section: three cards side by side (EAC₁, EAC₂, EAC₃). A radio-button row below the three cards selects which EAC is "primary" — this selection feeds VAC and TCPI
- "Recalculate" button at the top calls `compute_all_kpis()`, reads results dict, updates all card widgets
- **Stale-data warning:** When the user switches to the EVM tab and the underlying `EVMProject` has changed since the last recalculation (tracked via a `_last_calc_hash` on the tab), show a yellow info bar at the top: `"⚠ Input data has changed since last calculation. Click Recalculate to update."` The bar disappears after recalculation. Alternatively, auto-recalculate on tab switch if the computation is fast (< 100 ms for typical projects).
- If a KPI is `None` in the results dict: card shows `N/A` with grey badge. Tooltip (or small label beneath the badge) shows the error message
- "Step-by-Step" panel: a `ttk.LabelFrame` at the bottom that populates when any KPI card is clicked. Shows:
  - Formula line (static text)
  - Substitution line: `"= $40,000 ÷ $44,000"`
  - Result line: `"= 0.909"`
  - Interpretation: `"⚠ You are spending $1.10 for every $1.00 of work earned."`

**Sub-tab B: EV S-Curve**

- `FigureCanvasTkAgg` embedding a Matplotlib figure
- Three cumulative line series: PV (green dashed), EV (blue solid), AC (red solid)
- Data markers on each series
- Shaded region between EV and AC: red shade when AC > EV (cost overrun), green shade when EV > AC
- X-axis: period labels from `EVMProject.periods`; Y-axis: currency values with `currency_symbol` prefix
- Updates automatically when "Recalculate" is pressed
- "Export PNG" and "Export PDF" buttons (see Phase 5 for reusable `ExportButton`)
- Empty state: if no periods in the project, show a `ttk.Label` "No period data — add periods in the Input tab" instead of the chart

**Deliverable:** All 13 KPI functions implemented and tested. EVM tab with KPI cards (RAG coloured), step-by-step panel, and EV S-curve chart. All functions unit-tested with known-value assertions and boundary conditions.

---

## Phase 3 — Risk Register & Heat Map

**Duration: 2 weeks**
**Depends on: Phase 0 — can run in parallel with Phase 2**
**Blocks: Phase 4 (Monte Carlo cost distributions use Risk data)**

### 3.1 — Risk Register Data Model (`core/risk_register.py`)

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class RiskCategory(str, Enum):
    SCHEDULE = "Schedule"
    COST     = "Cost"
    QUALITY  = "Quality"
    SCOPE    = "Scope"
    OTHER    = "Other"

@dataclass
class Risk:
    id:          str
    name:        str
    description: str = ""
    probability: float = 0.0   # 0.0 – 1.0
    impact:      float = 0.0   # monetary value (>= 0)
    category:    RiskCategory = RiskCategory.OTHER
    exposure:    float = 0.0   # computed: probability × impact; always call recompute_exposures() before reading

    def validate(self):
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"Risk '{self.name}': probability must be 0–1")
        if self.impact < 0:
            raise ValueError(f"Risk '{self.name}': impact must be >= 0")

@dataclass
class RiskRegister:
    risks:                       List[Risk] = field(default_factory=list)
    bac:                         float = 0.0        # synced from EVMProject.bac
    high_exposure_threshold_pct: float = 0.05       # flag if RE > 5% of BAC

    def recompute_exposures(self):
        for r in self.risks:
            r.exposure = r.probability * r.impact

    def total_exposure(self) -> float:
        return sum(r.exposure for r in self.risks)

    def contingency_reserve(self) -> float:
        return self.total_exposure()

    def risks_by_exposure(self) -> List[Risk]:
        return sorted(self.risks, key=lambda r: r.exposure, reverse=True)

    def flag_high_exposure(self) -> List[Risk]:
        threshold = self.bac * self.high_exposure_threshold_pct
        return [r for r in self.risks if r.exposure > threshold]
```

`RiskRegister` is stored in `EduProjectState.risk_register`. When `EduProjectState.mark_dirty()` is called and `bac` changes, the register's `bac` field is updated: `self.risk_register.bac = self.evm_project.bac`.

### 3.2 — Risk I/O (`utils/risk_io.py`)

Same pattern as `evm_io.py`:

```python
def save_register(register: RiskRegister, filepath: str) -> None: ...
def load_register(filepath: str) -> RiskRegister: ...
def export_to_csv(register: RiskRegister, filepath: str) -> None: ...
def import_from_csv(filepath: str) -> RiskRegister: ...
```

The combined project save (Phase 5) will write both `evm_project` and `risk_register` into a single JSON with two top-level keys.

### 3.3 — Extend `RiskAnalysisTab` with Risk Register Sub-Tab

The existing `RiskAnalysisTab` in `risk_tab.py` already has an inner `ttk.Notebook` with four sub-tabs (Delay Risk, Contingency Planning, Variance Reduction, Activity Risk Prioritization). Add two more sub-tabs at the end:

**Sub-tab: Risk Register**

> **Note on sub-tab count:** After adding Risk Register and Risk Matrix, the Risk Analysis tab will have **6 sub-tabs** total (Delay Risk, Contingency, Strategies, Activity Risks, Risk Register, Risk Matrix). On small screens (< 1366px wide), the tab headers may overflow. Mitigation: use `ttk.Notebook` with `tabposition='nw'` (default) and ensure tab labels are short (≤ 12 chars each). If overflow is still an issue, consider grouping the 4 existing sub-tabs into a "Schedule Risk" parent and the 2 new sub-tabs into a "Project Risk" parent — but defer this refactor to V1.1 unless testing reveals a real usability problem.

- `ttk.Treeview` with columns: ID | Name | Category | Probability | Impact ($) | Exposure ($) | ⚠
- "⚠" column: red `▲` badge if risk is in `flag_high_exposure()` result list
- Rows sorted by exposure descending (highest first by default)
- Buttons: **Add Risk**, **Edit Risk**, **Delete Risk** — each opens a `Toplevel` dialog with form fields
- On dialog "Save": call `register.recompute_exposures()` → refresh tree
- Footer bar below the tree: `"Total Exposure: $X,XXX  |  Contingency Reserve: $X,XXX  |  Flagged risks: N"`
- Import/Export CSV buttons

**Sub-tab: Risk Matrix**

- `FigureCanvasTkAgg` embedding a 5×5 Matplotlib heat map
- Rendered with `plt.pcolormesh` on a grid of 5 probability bands × 5 impact bands
- Cell colour: score = probability_band_midpoint × impact_band_midpoint → mapped to green / yellow / orange / red
- Impact bands auto-scaled to `[0, max(risk.impact) × 1.1]` across all risks in the register; recalculated on every refresh
- Each risk plotted as a numbered circle at `(impact, probability)` coordinates
- Clicking a circle: populates a small detail panel to the right (name, category, exposure, flag status)
- "Export PNG/PDF" button
- Empty state: text label "Add risks in the Risk Register tab to populate this matrix"

### 3.4 — Connect to Existing Contingency Planner

The existing `contingency_tab` (sub-tab inside `RiskAnalysisTab`) already shows schedule-delay contingency from the PERT/Monte Carlo delay model. Extend its footer to also show:

- `"p×I Register Contingency: $X,XXX"` (from `RiskRegister.contingency_reserve()`)
- `"Combined Reserve: $X,XXX"` (sum of both)

**Deliverable:** Risk Register CRUD with auto-computed RE = p×I, ranked table, `▲` flagging, 5×5 heat map, contingency integration.

---

## Phase 4 — Monte Carlo Engine, Tracking Gantt & Resource Histograms

**Duration: 5 weeks** (includes ~0.5 week buffer for `run_cpm_on_sample()` and coordinate translation work)
**Depends on: Phase 1 (EVMTask date fields), Phase 3 (Risk data for cost distributions)**
**Blocks: Phase 5**

> **Revised up from 4.5 weeks.** Monte Carlo threading + progress bar + result caching + the Probabilistic CP table are larger than they appear. Tracking Gantt baseline state management and the coordinate system translation (period indices ↔ CPM ES/EF) are also non-trivial. The `run_cpm_on_sample()` helper function does not exist yet and must be written + tested. Do not compress this phase.

### 4.1 — Monte Carlo Engine (`core/monte_carlo.py`)

#### Data contracts

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import numpy as np

@dataclass
class MCInputs:
    cpm_activities: list  # List[dict] — from InputTab.get_activities_data()
                          # Provides task IDs, predecessors, and durations.
                          # For PERT mode: dicts also have 'optimistic'/'most_likely'/'pessimistic' keys.
                          # MC builds the dependency graph from this — NOT from EVMTask
                          # (EVMTask has no predecessors field by design).
    evm_tasks:  list      # List[EVMTask] — used only for budget data (cost sampling)
    risks:      list      # List[Risk] — optional; used for cost sampling
    bac:        float
    n_trials:   int = 5000

@dataclass
class MCResults:
    durations:          np.ndarray           # shape (n_trials,)
    costs:              np.ndarray           # shape (n_trials,)
    cp_frequencies:     Dict[str, float]     # task_id → fraction of trials on critical path
    p50_duration:       float
    p80_duration:       float
    p90_duration:       float
    p_cost_within_bac:  float
    n_trials:           int
    seed_used:          int

    def to_serializable(self) -> dict:
        """Convert to JSON-safe dict (np.ndarray → list)."""
        return {
            "durations": self.durations.tolist(),
            "costs": self.costs.tolist(),
            "cp_frequencies": self.cp_frequencies,
            "p50_duration": self.p50_duration,
            "p80_duration": self.p80_duration,
            "p90_duration": self.p90_duration,
            "p_cost_within_bac": self.p_cost_within_bac,
            "n_trials": self.n_trials,
            "seed_used": self.seed_used,
        }

    @classmethod
    def from_serializable(cls, data: dict) -> "MCResults":
        """Reconstruct from JSON-loaded dict."""
        return cls(
            durations=np.array(data["durations"]),
            costs=np.array(data["costs"]),
            **{k: data[k] for k in [
                "cp_frequencies", "p50_duration", "p80_duration",
                "p90_duration", "p_cost_within_bac", "n_trials", "seed_used"]}
        )
```

#### Simulation algorithm

```
ALGORITHM: run_simulation(inputs, progress_callback) → MCResults
rng = numpy.random.default_rng(seed)

FOR trial in range(N):
    sampled_durations = {}
    sampled_costs = 0.0

    FOR each task:
        # Duration sampling — PERT-Beta distribution
        # If task has O, M, P (PERT mode):
        #     mean  = (O + 4M + P) / 6
        #     sigma = (P - O) / 6
        #     alpha = ((mean-O)/(P-O)) * (6-2) + 1   # Beta shape params
        #     beta  = (1 - (mean-O)/(P-O)) * (6-2) + 1
        #     sample = O + (P - O) * rng.beta(alpha, beta)
        # If task has only planned_start/planned_finish (CPM mode):
        #     deterministic — use planned_finish - planned_start as duration

        # Cost sampling — Triangular distribution
        # min_cost   = 0.8 × task.budget
        # likely     = 1.0 × task.budget
        # max_cost   = 1.3 × task.budget     (adjustable)
        # If risks available: add sampled p×I contributions

        sampled_durations[task.task_id] = sampled_dur
        sampled_costs += sampled_task_cost

    # Run CPM on sampled_durations → get project_duration + critical path set
    project_duration, cp_set = run_cpm_on_sample(sampled_durations, task_graph)
```

> **⚠ `run_cpm_on_sample()` does not exist yet.** The existing `CPMAnalyzer.analyze()` takes a list of activity dicts (from `InputTab.get_activities_data()`), not a dict of sampled durations. You must write a new helper function — either a method on `CPMAnalyzer` or a standalone function in `monte_carlo.py` — that:
>
> 1. Takes the original `cpm_activities` list + a `sampled_durations: dict[str, float]` map.
> 2. Substitutes each activity's duration with the sampled value.
> 3. Runs forward/backward pass to compute the critical path.
> 4. Returns `(project_duration: float, critical_path_set: set[str])`.
>
> **Estimate: 1–2 days** including unit tests. This is already accounted for in the Phase 4 duration.

```

    record(project_duration, sampled_costs, cp_set)

    IF trial % (N // 100) == 0:
        progress_callback(trial / N)           # float 0.0–1.0

COMPUTE:
    p50, p80, p90 = numpy.percentile(durations, [50, 80, 90])
    p_cost_within_bac = count(cost <= bac) / N
    cp_freq[task] = count(task in cp_set) / N

RETURN MCResults(...)
```

#### Threading wrapper (mandatory — do not skip)

```python
class MonteCarloRunner:
    """Thread-safe wrapper. All public methods are safe to call from the Tkinter main thread."""

    def run_async(
        self,
        inputs: MCInputs,
        on_progress: Callable[[float], None],   # called from worker thread via queue
        on_complete: Callable[[MCResults], None],
        on_error:    Callable[[Exception], None]
    ) -> None:
        import threading, queue
        q = queue.Queue()

        def worker():
            try:
                def progress_cb(pct):
                    q.put(("progress", pct))
                result = run_simulation(inputs, progress_cb)
                q.put(("done", result))
            except Exception as e:
                q.put(("error", e))

        def poll():
            try:
                while True:
                    msg_type, payload = q.get_nowait()
                    if msg_type == "progress":
                        on_progress(payload)
                    elif msg_type == "done":
                        on_complete(payload)
                        return
                    elif msg_type == "error":
                        on_error(payload)
                        return
            except:
                pass
            # Schedule next poll
            self._root.after(100, poll)

        threading.Thread(target=worker, daemon=True).start()
        self._root.after(100, poll)
```

`MonteCarloRunner` receives `root: tk.Tk` in its constructor to use `root.after()`. The UI passes this in.

**Result caching:** Store the last `MCResults` in `EduProjectState.mc_results`. The "Run Simulation" button is disabled (greyed) if `mc_results` exists and the inputs have not changed since the last run. Add a `mc_inputs_hash: str` field to `EduProjectState` — recompute as `hash(str(inputs))` and compare before enabling the button.

### 4.2 — Monte Carlo UI (extend `gui/tabs/probability_tab.py`)

> **Layout note:** The existing `ProbabilityTab` uses a `ttk.PanedWindow` (NOT an inner `ttk.Notebook`). To add the Monte Carlo UI, **refactor the tab** to use a `ttk.Notebook` with two sub-tabs: (1) the existing PERT probability content moved into a "PERT Analysis" sub-tab, and (2) a new "Monte Carlo" sub-tab. This is a one-time refactor — wrap the existing content in a frame, create the Notebook, and add both frames as tabs. Ensure all existing widget references still work after the move.

The new "Monte Carlo" sub-tab contains:

- N input field (Spinbox, 500–50,000, default 5,000)
- "Run Simulation" button; disabled while running; disabled if inputs unchanged since last run
- `ttk.Progressbar` (determinate, 0–100) that advances during simulation
- After completion — three sections in a vertical scroll frame:
  1. **Duration histogram**: Matplotlib figure with P50/P80/P90 vertical lines labelled with values; PERT normal curve overlaid as dashed line (for comparison)
  2. **Cost histogram**: bar histogram with a vertical BAC line; annotation `"P(cost ≤ BAC) = XX%"`
  3. **Probabilistic Critical Path table**: `ttk.Treeview` with columns Task Name | Frequency on CP (%) | a proportional bar drawn as a wide `tk.Canvas` widget or as a spark-bar using emoji-free Unicode block characters

### 4.3 — Tracking Gantt (extend `gui/tabs/gantt_tab.py`)

Extension of the existing `GanttTab`. All new elements are hidden in UG mode (Phase 5.1 wires the mode toggle).

**"Set Baseline" button:**

- Copies `planned_start` / `planned_finish` → `baseline_start` / `baseline_finish` for every `EVMTask` in `edu_state.evm_project.tasks`
- Shows a confirmation dialog: `"Baseline set for N tasks. Use 'Reset Baseline' to undo."`
- Button becomes "Reset Baseline" after setting; reset requires a confirmation dialog

**Tracking Gantt mode toggle (`ttk.Checkbutton`):**
When enabled, the Gantt renderer:

> **Coordinate system note:** The existing `gantt_tab.py` renders bars using CPM `ES`/`EF` values (float days), while `EVMTask` uses 0-based period indices (`planned_start`/`planned_finish`). These are different coordinate systems. The Tracking Gantt must translate between them:
>
> - If `EVMTask.cpm_task_id` is set, use the linked CPM task's `ES`/`EF` for bar positioning (consistent with the existing Gantt renderer).
> - The `baseline_start`/`baseline_finish` and `pct_complete` overlay are drawn relative to the same CPM coordinate space.
> - If no CPM link exists (EVM-only project), fall back to period indices as x-coordinates with a separate axis scale.
> - Add a helper `_evm_to_gantt_coords(evm_task, cpm_results)` in `gantt_tab.py` to centralise this translation.

1. Draws the normal task bar at the **current** `planned_start` / `planned_finish` position
2. Draws a lighter/hatched bar at `baseline_start` / `baseline_finish` behind the current bar
3. Overlays a solid fill from `planned_start` to `planned_start + (planned_finish - planned_start) × pct_complete/100`
4. Colours the bar green if ahead/on-schedule, amber if slightly delayed, red if significantly delayed (thresholds based on float remaining)

Task table adds columns visible only in Tracking Gantt mode: Baseline Start | Baseline Finish | % Complete | Status badge.

### 4.4 — Resource & Cost Histograms (extend `gui/tabs/rcps_tab.py`)

Add a "Histograms" sub-tab to the existing RCPS tab (`rcps_tab.py` / `rcps_tab_clean.py`):

- **"Cost per Period" chart**: computes period-by-period AC delta from `EVMPeriod.ac_cumulative` values; draws as a bar chart; overlays a PV-per-period bar for comparison
- **"Resource Usage" chart**: reads the existing resource leveling output if available; shows placeholder `"Run RCPS analysis first"` if not
- Before/After leveling toggle — enabled only if RCPS has been run
- Both charts use `FigureCanvasTkAgg` with "Export" buttons

This tab is PG-only (hidden in UG mode per Phase 5.1).

### 4.5 — Risk Probability Distribution Chart (extend `probability_tab.py`)

In the existing PERT probability sub-tab:

- When Monte Carlo results exist in `edu_state.mc_results`, replace the PERT normal curve with a histogram of MC durations with the PERT curve overlaid as dashed
- A toggle "Show PERT overlay" shows/hides the dashed PERT curve
- P50/P80/P90 vertical markers with date labels derived from the period labels in `EVMProject.periods`

**Deliverable:** Threaded Monte Carlo engine with progress bar; Tracking Gantt with baseline bars + % complete shading; cost/resource histograms in RCPS tab; enriched probability chart.

---

## Phase 5 — Mode Toggle, Export, Demo Data, Dashboard & Packaging

**Duration: 3 weeks** (increased from 2.5 weeks to accommodate Dashboard tab, combined save/load, and unsaved-changes warning)
**Depends on: Phases 2, 3, 4**

### 5.1 — UG / PG Mode Toggle

Mode is stored in `AppConfig.mode` and persists via `AppConfig.save()`.

In `MainWindow`, add a mode toggle button to the toolbar (or a `Tools → Toggle Mode` menu item). Clicking it calls `apply_mode(new_mode)`:

```python
def apply_mode(self, mode: str):
    self.edu_state.config.mode = mode
    self.edu_state.config.save()
    self.root.title(f"PMHelper [{mode.upper()}]")
    for tab in self._edu_tabs:        # list of tabs that implement set_mode()
        tab.set_mode(mode)
```

Every tab that has PG-only content implements `set_mode(mode: str)`. Hiding is done by calling `.pack_forget()` / `.pack()` (or `.grid_remove()` / `.grid()`) on the relevant frames. Tab visibility (entire tabs hidden) is handled by `self.notebook.hide(tab_index)` / `self.notebook.add(...)`.

| Feature                                                                        | UG  | PG  |
| ------------------------------------------------------------------------------ | --- | --- |
| Gantt, Network, CPM, EVM S-Curve, Risk Matrix, All 11 UG KPIs, EAC₁, EAC₂, VAC | ✅  | ✅  |
| Step-by-step walkthrough                                                       | ✅  | ✅  |
| PERT Three-Point Estimation                                                    | ❌  | ✅  |
| Monte Carlo (duration + cost)                                                  | ❌  | ✅  |
| Tracking Gantt / Baseline                                                      | ❌  | ✅  |
| Probabilistic Critical Path table                                              | ❌  | ✅  |
| Advanced EAC₃ (CPI × SPI)                                                      | ❌  | ✅  |
| TCPI toward BAC                                                                | ❌  | ✅  |
| Aggregate Risk Exposure                                                        | ❌  | ✅  |
| Resource / Cost Histograms (RCPS tab)                                          | ❌  | ✅  |

Mode label shown in window title: `PMHelper [UG]` or `PMHelper [PG]`.

### 5.2 — Chart Export (PNG / PDF)

Reusable `ExportButton` class in a new `utils/chart_export.py`:

```python
class ExportButton(ttk.Button):
    def __init__(self, parent, figure_getter, **kw):
        super().__init__(parent, text="Export Chart", command=self._export, **kw)
        self._get_fig = figure_getter

    def _export(self):
        from tkinter import filedialog, messagebox
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("PDF Document", "*.pdf")])
        if path:
            self._get_fig().savefig(path, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {path}")
```

Use this widget in every chart sub-tab (EVM S-Curve, Risk Matrix, Monte Carlo charts, Gantt, probability chart).

**"Export All Charts" in `File` menu:**

- Calls `tab.get_figures() -> list` on every tab that implements it
- Opens a folder-chooser dialog
- Saves each figure as `<tab_name>_<chart_name>.png` in the chosen folder
- Shows a summary dialog: `"Exported N charts to <folder>"`

### 5.3 — Sample Demo Datasets

Two complete JSON files in `src/pmhelper/data/demos/`:

**`office_renovation_ug.json`** (Undergraduate Demo)

Design constraints:

- 8 tasks, 3 predecessor links, 10 periods
- `CPI ≈ 0.87` (cost overrun), `SPI ≈ 0.92` (schedule delay)
- 2 risks with `exposure > 5% BAC` → flagged
- Pre-filled PV/EV/AC with visible S-curve divergence

**`software_development_pg.json`** (Postgraduate Demo)

Design constraints:

- 12 tasks with O/M/P values, 3 resource types, 16 periods
- Monte Carlo P90 > planned finish by 2 periods
- Two tasks share CP with > 30% frequency each
- `CPI > 1.1` (healthy cost — contrast with UG demo)
- 8 risks with varied categories

"Load Demo" button on a startup splash screen (simple `Toplevel` dialog shown once on first launch) and `File → Load Demo Project → [Office Renovation (UG)] / [Software Dev (PG)]` menu items.

### 5.4 — Extended Import/Export

- `export_evm_periods_csv()`, `import_evm_periods_csv()` — extend `evm_io.py`
- `export_risks_csv()`, `import_risks_csv()` — extend `risk_io.py`
- `export_full_project_xlsx(state, filepath)` — multi-sheet `.xlsx` via `openpyxl`:
  - Sheet 1: Tasks (task_id, name, budget, pct_complete, planned_start, planned_finish)
  - Sheet 2: EVM Periods (index, label, pv, ev, ac)
  - Sheet 3: Risk Register (id, name, category, probability, impact, exposure)
  - Sheet 4: KPI Results (kpi name, value, rag status)
- Add `openpyxl` to `requirements.txt`

**Combined Project Save/Load (`utils/project_io.py`):**

The plan references combined save/load in Phase 3.2 but it needs an explicit task. Create a unified `save_project()` / `load_project()` that writes **all** state to a single `.pmproj` JSON file with top-level keys:

```json
{
  "version": "1.0",
  "evm_project": { ... },
  "risk_register": { ... },
  "mc_results": { ... },         // via MCResults.to_serializable(); null if no MC run
  "cpm_activities": [ ... ],     // raw activity dicts from InputTab
  "app_config": { "mode": "ug" }
}
```

This file is what `File → Save Project` / `File → Open Project` uses. The existing CPM-only `save_results()` / `load_cpm_data()` in `main_window.py` remains for backward compatibility. Wire both save paths into `EduProjectState.mark_clean()` after successful write.

### 5.5 — Dashboard Tab (`gui/tabs/dashboard_tab.py`)

`dashboard_tab.py` is listed in the Architecture Map but needs a concrete description. This is a summary/overview tab that gives a project-health-at-a-glance view. Contents:

- **Project header:** project name, BAC, currency, current period label
- **KPI summary strip:** 6 key KPIs (CPI, SPI, CV, SV, EAC₁, VAC) displayed as coloured cards with RAG badges — a condensed version of the EVM tab's KPI cards
- **Mini S-curve:** a small (300×200 px) embedded Matplotlib chart showing PV/EV/AC (no interactivity needed)
- **Risk summary:** total exposure, flagged risk count, top 3 risks by exposure
- **Monte Carlo summary** (PG only): P50/P80/P90 values, P(cost ≤ BAC)
- **Mode badge:** shows current UG/PG mode

This tab reads from `edu_state` and calls `compute_all_kpis()` on load/refresh. No new data model needed. Empty state: show `"Load or create a project to see the dashboard."`

### 5.6 — PyInstaller Packaging

- Use `--onedir` (not `--onefile`) — directory bundles get far fewer AV false positives
- Create `pmhelper_edu.spec` with:
  - `datas`: demo JSON files, Matplotlib data files, any icon/image assets
  - `hiddenimports`: numpy, scipy (conditional), matplotlib backends
- Add `build_edu.ps1` convenience script: calls PyInstaller with the spec; zips the output directory
- Test: the zipped bundle unpacks and launches on a machine with no Python installed
- Document the AV false-positive mitigation steps from Phase 0 in a `INSTALL_NOTES.md`

**Deliverable:** Mode toggle working and persisting; all charts have export buttons; demo datasets load from menu; full `.xlsx` export; combined `.pmproj` save/load; Dashboard tab; `--onedir` bundle tested.

### 5.7 — Unsaved-Changes Warning

Intercept `WM_DELETE_WINDOW` on the root window and check `edu_state.is_dirty()`. If dirty, show a confirmation dialog: `"You have unsaved changes. Save before closing?"` with three buttons: **Save & Close** (calls combined save, then destroys), **Discard** (destroys without saving), **Cancel** (returns to app). Wire this in `MainWindow.__init__()` via `self.root.protocol("WM_DELETE_WINDOW", self._on_close)`.

---

## Phase 6 — Testing & Stabilization

**Duration: 3 weeks** (increased from 2.5 weeks for additional integration tests)
**Depends on: all phases**

### 6.1 — Unit Tests

| File                       | What to cover                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_evm_models.py`       | `EVMTask.validate()` for each bad field; `compute_pv_schedule()` with 1, 3, and 8 tasks; uniform spreading correctness; `ev_discrepancy()` detection; period ordering; **edge case: task spans more periods than exist** (e.g. `planned_finish=10` but only 5 periods — must clamp, not crash)                                                                                                                                                                                                                      |
| `test_evm_calculations.py` | All 13 functions with known values (e.g. EV=$40k, AC=$44k → CPI=0.909); `ValueError` raised at every zero-denominator case; `compute_all_kpis()` with all zeros and with valid data; `None` values in results dict when errors occur                                                                                                                                                                                                                                                                                |
| `test_rag.py`              | Every KPI, every boundary value; `CPI=0.95` → "amber"; `CPI=1.0` → "green"; `CPI=0.949` → "red"; `bac=0` edge case → returns "grey"                                                                                                                                                                                                                                                                                                                                                                                 |
| `test_risk_register.py`    | CRUD operations; `recompute_exposures()` correctness; `flag_high_exposure()` with threshold exactly at boundary; `contingency_reserve()` sum; `bac` sync from project                                                                                                                                                                                                                                                                                                                                               |
| `test_monte_carlo.py`      | Deterministic seed: identical results on two runs; output arrays shape `(N,)`; `P50 ≤ P80 ≤ P90` always true; convergence: seed=42, N=10000, mean within 5% of PERT expected; wall-time: N=5000 completes in < 30 seconds; **MC with deterministic tasks (no O/M/P)**: tasks with only `planned_start`/`planned_finish` use fixed duration — verify MC still runs and produces zero-variance durations for those tasks; **`MCResults.to_serializable()` round-trip**: serialize → deserialize → assert arrays equal |
| `test_evm_io.py`           | Round-trip JSON save/load equality; CSV round-trip; empty project; non-ASCII project name; missing fields use defaults; **combined `.pmproj` save/load round-trip** (EVM + risk + MC results in one file)                                                                                                                                                                                                                                                                                                           |
| `test_app_config.py`       | Load from non-existent path → defaults; save → read back → assert equality; mode field persists; **Windows `%APPDATA%` vs Unix `~` path resolution**                                                                                                                                                                                                                                                                                                                                                                |

All tests must be written by the developer (with AI assistance), not post-hoc. Write test stubs in Phase 0; fill them in as each phase completes.

### 6.2 — Integration Tests

- Load UG demo → `compute_all_kpis()` → assert `CPI ≈ 0.87`, `SPI ≈ 0.92`, 2 risks flagged
- Load PG demo → `run_simulation(inputs, N=500, seed=42)` → assert `p90 > planned_finish`
- UG mode: assert PG-only panels/tabs are not visible (access widget's `.winfo_viewable()`)
- PG mode: assert they are visible
- Full EVM workflow: populate programmatically → `save_evm_project()` → `load_evm_project()` → assert equality
- **Sync from CPM round-trip:** load CPM data → click "Sync from CPM Tasks" → verify EVM table matches → edit CPM tasks → re-sync → verify merge behaviour (new tasks added, deleted tasks flagged, budgets preserved)
- Risk workflow: add 3 risks → `export_to_csv()` → `import_from_csv()` → assert same risks and exposures
- Mode persistence: set mode → call `AppConfig.load()` in a fresh instance → assert same mode

### 6.3 — Edge Cases (all must produce graceful UI messages, never unhandled exceptions)

| Scenario                          | Expected behaviour                                                  |
| --------------------------------- | ------------------------------------------------------------------- |
| `AC = 0`                          | CPI card: `"N/A — AC is zero"`                                      |
| `BAC = 0`                         | All BAC-dependent KPIs: `"N/A — BAC is zero"`                       |
| All tasks at 0% complete          | EV = 0; CPI/SPI show `"N/A"`; PV S-curve still renders              |
| No risks in register              | Heat map shows empty-state label; contingency = $0                  |
| Single-task network               | CPM trivial critical path; Monte Carlo runs normally                |
| Monte Carlo N=1                   | Returns `MCResults` with `n_trials=1`; no crash                     |
| Period table empty                | S-curve shows `"No period data — add periods in the Input tab"`     |
| `planned_finish < planned_start`  | Caught in `EVMTask.validate()`; shown as inline error in task table |
| Non-monotonic cumulative PV/EV/AC | Warning label shown; does not block save                            |

### 6.4 — UI Smoke Test Checklist

- [ ] App launches (`python src/main.py`) with no errors in console
- [ ] Load UG demo → all KPI cards populate with correct values
- [ ] Click CPI card → step-by-step panel shows correct substitution
- [ ] EV S-curve renders with three lines; shaded cost-variance region visible
- [ ] Risk Register: add, edit, delete risk → table updates; heat map updates
- [ ] Risk Matrix: risk dot appears at correct position; clicking shows detail panel
- [ ] Load PG demo → Monte Carlo runs with progress bar; completes; histogram renders
- [ ] Tracking Gantt: Set Baseline → enable tracking mode → baseline bars visible
- [ ] Switch UG → PG: Monte Carlo tab becomes visible
- [ ] Switch PG → UG: Monte Carlo tab hidden; mode persists after restart
- [ ] Export EVM S-curve as PNG → file non-zero, opens correctly
- [ ] Export EVM S-curve as PDF → file non-zero, opens correctly
- [ ] Export All Charts → folder created with all chart files
- [ ] Save project → close app → reopen → load → all data intact; no discrepancy warning
- [ ] Export full project as `.xlsx` → opens in Excel with 4 sheets populated
- [ ] `--onedir` bundle launches on a machine with no Python installed
- [ ] Unsaved-changes warning appears on close when dirty; "Save & Close" saves correctly
- [ ] Dashboard tab shows correct KPI summary, mini S-curve, risk summary
- [ ] Combined `.pmproj` save/load round-trip: all data (EVM + risk + MC) intact

---

## Timeline Summary

```
Week 0–0.5   │ Phase 0: Scaffolding, Decisions, Entry Point, AppConfig
Week 1–3.5   │ Phase 1: EVM Data Model, Input UI, PV Spreading, File I/O
Week 4–7.5   │ Phase 2: EVM Calculations, RAG, KPI Cards, S-Curve
Week 4–6     │ Phase 3: Risk Register + Heat Map  ← parallel with Phase 2
Week 7.5–13  │ Phase 4: Monte Carlo (threaded), Tracking Gantt, Histograms (5 wks incl. buffer)
Week 13–16   │ Phase 5: Mode Toggle, Export, Demo Data, Dashboard, Save/Load, Packaging (3 wks)
Week 16–19   │ Phase 6: Testing & Stabilization (3 wks)
─────────────────────────────────────────────────────────────────────────
TOTAL        │ ~19 calendar weeks  (~22 weeks of actual work;
             │  Phase 2 ∥ Phase 3 recovers ~2 weeks;
             │  ~1 week buffer distributed in Phases 4–6)
```

### Critical Path

```
Phase 0 → Phase 1 → Phase 2 ──────────────────────────→ Phase 5 → Phase 6
                   ↘                                   ↗
                    Phase 3 → (feeds Phase 4 MC cost) ↗
                              ↑
                    Phase 4.3 also needs Phase 1 task date fields
```

**Phase 1 is the irreducible blocker.** The `EVMTask` date fields (`planned_start`, `planned_finish`, `baseline_start`, `baseline_finish`) must be in place before Phase 4.3 (Tracking Gantt) can begin, even though Phase 4 officially starts after Phase 2.

---

## Definition of Done (V1 Release)

- [ ] All 39 V1 features listed in `FEATURES_LIST_EDU.md` are reachable and functional in the running app
- [ ] `DECISIONS.md` has answers to all 7 decisions from the Key Decisions Log
- [ ] `pytest` passes with 0 failures across all test files
- [ ] All 6.3 edge cases produce graceful UI messages — no unhandled exceptions
- [ ] All 6.4 smoke-test checklist items are checked
- [ ] UG demo loads and produces: `CPI < 1`, `SPI < 1`, 2 flagged risks (verified by integration test)
- [ ] PG demo loads and produces: Monte Carlo `P90 > planned_finish` (verified by integration test)
- [ ] `AppConfig` mode persists across simulated restarts (test in `test_app_config.py`)
- [ ] All chart exports produce non-zero PNG and PDF files
- [ ] "Export All Charts" creates a complete folder of all chart files
- [ ] Full `save → close → load` cycle produces byte-identical data (round-trip integration test)
- [ ] Combined `.pmproj` save → load round-trip preserves all state (EVM + risk + MC results)
- [ ] `.xlsx` export produces a valid 4-sheet file openable in Excel/LibreOffice
- [ ] `--onedir` PyInstaller bundle launches on a machine with no Python installed
- [ ] AV false-positive mitigation steps documented in `INSTALL_NOTES.md`
- [ ] Unsaved-changes dialog shown on close when project is dirty
- [ ] Dashboard tab renders correctly in both UG and PG modes
- [ ] No known data-loss bugs identified during Phase 6 integration testing
