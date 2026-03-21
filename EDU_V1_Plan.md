# PMhelper Edu — V1 Implementation Plan

> **Scope:** All ~50 V1 features from `FEATURES_LIST_EDU.md`
> **Approach:** 1 developer + AI agent assistance
> **Estimated Calendar Time:** ~21 weeks (parallelism in Phases 2+3 recovers ~2 weeks; ~1 week buffer in Phase 4; Phase 8 adds ~2 weeks)
> **Date:** March 8, 2026
> **Last Status Update:** March 21, 2026

---

## Current Implementation Status (as of March 9, 2026)

### ✅ COMPLETED (Phases 0–7)

| Phase   | Description                                                                                                                                                                        | Status  |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Phase 0 | Scaffolding — `EduProjectState`, `AppConfig`, entry point (`edu_main.py`), test stubs                                                                                              | ✅ Done |
| Phase 1 | EVM Data Model + Input Layer — `EVMTask`, `EVMPeriod`, `EVMProject`, `InputTabEdu`, `evm_io_edu.py`, PV spreading                                                                  | ✅ Done |
| Phase 2 | EVM Calculation Engine — `evm_calculations_edu.py`, `EVMTabEdu` (KPI cards, RAG, step-by-step, S-Curve), `test_evm_calculations_edu.py`                                            | ✅ Done |
| Phase 3 | Risk Register & Heat Map — `risk_register_edu.py`, `RiskTabEdu` (register CRUD, 5×5 heat map, contingency integration), `risk_io_edu.py`                                           | ✅ Done |
| Phase 4 | Monte Carlo Engine — `monte_carlo_edu.py` (threaded, progress bar), `ProbabilityTabEdu` (Monte Carlo + PERT Analysis sub-tabs), Tracking Gantt (baseline bars, % complete shading) | ✅ Done |
| Phase 5 | Mode Toggle (UG/PG), Chart Export, Demo Data (.pmproj), Dashboard Tab, Save/Load, Unsaved-Changes Warning, PyInstaller spec                                                        | ✅ Done |
| Phase 6 | Testing & Stabilisation — all test files pass (381 tests)                                                                                                                          | ✅ Done |
| Phase 7 | CPM/PERT Integration — Analyze button, real Results/Network/PERT/Crashing tabs reused, CPM→EVM sync, `.pmproj` CPM activity persistence                                            | ✅ Done |

### 🔧 IN PROGRESS — Phase 8: Production Hardening (P1 + P2 fixes)

> **Goal:** Fix all remaining gaps that prevent the app from being production-ready.
> **Estimated effort:** ~5 working days
> **Date started:** March 9, 2026

#### Phase 8 — Priority 1 (Must Fix)

These are wiring/refresh gaps. The underlying logic already works in unit tests — the issue is that tabs don't always update on screen when they should.

| #   | Task                                             | Files to Change                           | What to Do                                                                                                                                                                                  | Effort  | Status  |
| --- | ------------------------------------------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 8.1 | Analyze → full tab distribution                  | `main_window_edu.py`                      | After `analyze_project()`, call `on_tab_selected()` on EVM tab + Dashboard tab + Probability tab (PERT mode). Already partially done — verify all 4 real tabs + 3 edu tabs receive results. | 0.5 day | ✅ Done |
| 8.2 | **New Project → full reset ALL tabs**            | `main_window_edu.py`, tab files           | `_new_project()` now: clears CPM tree, clears Gantt analysis data, calls `_refresh_all_edu_tabs()` to reset all UI panels.                                                                  | 0.5 day | ✅ Done |
| 8.3 | **`.pmproj` load → re-populate CPM Input table** | `project_io_edu.py`, `main_window_edu.py` | Save: persist `cpm_activities` + `cpm_mode` in `.pmproj`. Load: call `InputTabEdu.load_activities()`. Already done.                                                                         | —       | ✅ Done |
| 8.4 | **`.pmproj` load → refresh ALL edu tabs**        | `main_window_edu.py`                      | `_open_project()` and `_load_demo()` now call `_refresh_all_edu_tabs()` instead of only refreshing the currently-visible tab.                                                               | 0.5 day | ✅ Done |

#### Phase 8 — Priority 2 (Should Fix)

These are missing functionality or incomplete features that a user would notice immediately.

| #    | Task                                             | Files to Change                                                                     | What to Do                                                                                                                                              | Effort  | Status  |
| ---- | ------------------------------------------------ | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 8.5  | **UG/PG mode toggle verification**               | `main_window_edu.py`                                                                | Verified — `_apply_mode()` correctly hides/shows PG-only tabs and propagates `set_mode()`. All tab `set_mode()` methods audited.                        | 0.5 day | ✅ Done |
| 8.6  | **Demo datasets load → produce meaningful KPIs** | `demos_edu/office_renovation_ug.pmproj`, `demos_edu/software_development_pg.pmproj` | Added `cpm_activities` + `cpm_mode` to both demo files (UG=8 det. activities, PG=12 PERT activities). Load → Analyze flow works.                        | 1 day   | ✅ Done |
| 8.7  | **Gantt — predecessor arrows + today line**      | `gantt_tab_edu.py`                                                                  | Already implemented: arrows, today line toggle, project start date, export. Fixed crash bug (stray `ax.legend` in `_draw_predecessor_arrows`).          | 1 day   | ✅ Done |
| 8.8  | **Probability tab — PERT Analysis sub-tab**      | `probability_tab_edu.py`                                                            | Verified — `update_from_analysis()`, stats, charts all handle empty state gracefully. Added defensive guard on `evm_project.bac`.                       | 0.5 day | ✅ Done |
| 8.9  | **RCPS tab — resource-constrained scheduling**   | `rcps_tab_edu.py`                                                                   | Verified — schedule + histogram sub-tabs work. Added None guard in `_draw_histograms()` to prevent crash on empty project.                              | 0.5 day | ✅ Done |
| 8.10 | **Wire PG-only tabs into main window**           | `main_window_edu.py`                                                                | Wired DPCI tab (PG-only) into `_build_tabs()`, `_all_tabs_ordered`, `tabs`, `_pg_only_widgets`. RCPS Crashing, Charter, Charter Mgr were already wired. | 0.5 day | ✅ Done |

#### Phase 8 — Task Dependency Order

```
8.2 (New Project reset) ──────────────────────────┐
8.4 (Load → refresh all tabs) ────────────────────┤
8.5 (UG/PG mode toggle) ─────────────────────────┼──→ 8.6 (Demo data verification)
8.7 (Gantt arrows + today line) ──────────────────┤
8.8 (PERT sub-tab) ──────────────────────────────┤
8.9 (RCPS schedule sub-tab) ─────→ 8.10 (Wire PG tabs) ──→ 8.6 (Demo data)
```

Tasks 8.2, 8.4, 8.5, 8.7, 8.8, 8.9 are independent and can be done in any order.
Task 8.10 depends on 8.9 (RCPS must work before wiring RCPS Crashing).
Task 8.6 (demo verification) should be done last — it's the integration smoke test.

---

## 🆕 What's New — Phase 9: SWOT & PESTEL Strategic Analysis

**Phase 9 adds two new strategic analysis modules** (PG-only) that teach students how executives validate project charters and assess external risks. These are NOT in the original Phase 0–8 scope.

| Feature                    | What It Does                                                                                                                                                         | Value                                                                                                                           |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **SWOT Analysis**          | 2×2 matrix (Strengths, Weaknesses, Opportunities, Threats) with auto-extraction from Charter, Risk Register, and EVM KPIs. Students can also enter factors manually. | Teaches cause-effect thinking: "A weak CPI means cost overrun risk (Weakness)"; "High stakeholder influence = project strength" |
| **PESTEL Analysis**        | 6-cell heatmap (Political, Economic, Social, Technological, Environmental, Legal) with impact scoring and probability. Factors include contextual mitigation notes.  | Teaches external factor analysis: "New regulations (Legal) threaten timeline"; "Inflation (Economic) erodes budget"             |
| **Auto-Extract from Data** | Both analyses can auto-populate from existing project data: Charter descriptions, Risk Register exposures, EVM KPIs (CPI/SPI). User validates + edits.               | Reduces manual data entry; teaches traceability; leverages info already in the project                                          |
| **Manual Entry + Editing** | Users can add custom factors, edit auto-extracted factors, or clear and start fresh. All factors have "source" tracking (Charter, Risk, EVM, Manual).                | Flexibility for edge cases + audit trail for educational accountability                                                         |
| **Export to PNG/PDF/CSV**  | Export the SWOT matrix or PESTEL heatmap as visuals (PNG/PDF) or as data (CSV) for reports and presentations.                                                        | Students can include analysis in project reports; lecturers can collect data for grading                                        |
| **Save/Load in `.pmproj`** | SWOT and PESTEL analyses are persisted in the `.pmproj` file (`swot_analysis` and `pestel_analysis` keys). Load a project → see your prior analysis.                 | Zero data loss; students can iterate on analysis as the project evolves                                                         |

**Effort breakdown:**

- Phase 9A (SWOT): 5 days (models + extraction + UI + tests)
- Phase 9B (PESTEL): 2.5 days (models + UI + tests)
- **Total Phase 9: 1.5 weeks (7.5 days)**

**Timeline impact:** Phase 9 extends V1 by 1.5 weeks, but is independent of MVP (Phases 0–8). Can ship Phase 7 MVP without it, then add Phase 9 for v1.0-final.

---

### ✅ PHASE 9: SWOT & PESTEL Strategic Analysis (Complete)

> **Goal:** Add strategic analysis tools that extract insights from Project Charter, Risk Register, and EVM data.
> **Dependencies:** Requires Phases 0–8 complete (Charter tab, Risk register, EVM KPIs)
> **Priority:** P2 (should have for PG mode; educational value for teaching strategic thinking)
> **PG-Only:** Yes

#### Phase 9A: SWOT Analysis Module (5 days)

| #   | Task                                      | Files to Change / Create                                                                | What to Do                                                                                                         | Effort  | Status  |
| --- | ----------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------- | ------- |
| 9.1 | SWOT data model + extraction logic        | **`core/swot_models_edu.py`** (NEW), **`utils/swot_extractor_edu.py`** (NEW)            | Implement `SWOTFactor`, `SWOTAnalysis` dataclasses + `SWOTExtractor` static methods to auto-populate from Charter  | 2 days  | ✅ Done |
| 9.2 | SWOT I/O (save/load to `.pmproj`)         | `utils/project_io_edu.py` (extend)                                                      | Add `swot_analysis` key to `.pmproj` JSON schema; round-trip tests                                                 | 0.5 day | ✅ Done |
| 9.3 | SWOT Tab UI (2×2 matrix + CRUD + buttons) | **`gui/tabs/swot_tab_edu.py`** (NEW), `main_window_edu.py` (wire tab)                   | 2×2 grid Treeviews for each quadrant; double-click to edit; auto-extract buttons; manual entry; export PNG/PDF/CSV | 2 days  | ✅ Done |
| 9.4 | SWOT Tests                                | **`tests/test_swot_models_edu.py`** (NEW), **`tests/test_swot_extractor_edu.py`** (NEW) | Unit tests for dataclasses, extraction logic (from Charter, Risk, EVM), I/O round-trip                             | 0.5 day | ✅ Done |

**Extraction sources for SWOT (auto-populate):**

- **Strengths:** Project team capability (from Charter), achievable scope, high-value deliverables
- **Weaknesses:** Resource constraints (Budget/Schedule limits in Charter), team skill gaps, scope uncertainty
- **Opportunities:** Strategic alignment (from Charter), market need (business_case field), risk mitigation results
- **Threats:** High-impact risks (Exposure > 5% BAC from Risk Register), external dependencies, cost/schedule pressure (CPI/SPI from EVM)

#### Phase 9B: PESTEL Analysis Module (2.5 days)

| #   | Task                                          | Files to Change / Create                                                | What to Do                                                                                                           | Effort  | Status  |
| --- | --------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 9.5 | PESTEL data model + scoring                   | **`core/pestel_models_edu.py`** (NEW)                                   | Implement `PESTELFactor`, `PESTELAnalysis` dataclasses + exposure scoring (impact × probability)                     | 1 day   | ✅ Done |
| 9.6 | PESTEL I/O (save/load to `.pmproj`)           | `utils/project_io_edu.py` (extend)                                      | Add `pestel_analysis` key to `.pmproj` JSON schema; round-trip tests                                                 | 0.5 day | ✅ Done |
| 9.7 | PESTEL Tab UI (6-cell heatmap + detail table) | **`gui/tabs/pestel_tab_edu.py`** (NEW), `main_window_edu.py` (wire tab) | 6 coloured buttons (P/E/S/T/En/L) with heatmap intensity; click to filter factors; detail table; add/edit UI; export | 1 day   | ✅ Done |

**PESTEL factors in scope:**

- **Political:** Tax laws, regulations, government incentives
- **Economic:** Inflation, interest rates, budget cycles
- **Social:** Workforce trends, stakeholder expectations, cultural factors
- **Technological:** New tools, automation, IT landscape
- **Environmental:** Climate impact, sustainability requirements
- **Legal:** Compliance, contracts, IP protection

#### Phase 9 Integration Points

**Data flow diagram:**

```
Charter Tab                  EVM Tab                  Risk Tab
     ↓                           ↓                        ↓
 charter_data ────────────→ SWOTExtractor ←────── risk_register
                                 ↓
                          SWOTAnalysis (auto-populated)
                                 ↓
                              SWOT Tab
                         (2×2 matrix UI)
                                 ↓
                          (manual editing)
                                 ↓
                      .pmproj save/load
```

**`.pmproj` schema additions (Phase 9.2 + 9.6):**

```json
{
  "version": "1.0",
  "evm_project": { ... },
  "risk_register": { ... },
  "charter_data": { ... },
  "swot_analysis": {
    "strengths": [
      {
        "text": "Strong project team with 5+ years PM experience",
        "source": "Charter",
        "weight": 1.0,
        "linked_to": "team_experience"
      }
    ],
    "weaknesses": [
      {
        "text": "Budget constraint: only $250K allocated",
        "source": "Charter",
        "weight": 0.8,
        "linked_to": "budget_constraint"
      }
    ],
    "opportunities": [...],
    "threats": [
      {
        "text": "Risk: Market shift to competitor (Exposure $45K)",
        "source": "Risk Register",
        "weight": 0.6,
        "linked_to": "risk_id_42"
      }
    ]
  },
  "pestel_analysis": {
    "factors": [
      {
        "category": "Political",
        "description": "New tax incentives for tech projects",
        "impact_score": 2.5,
        "probability": 0.7,
        "mitigation": "Engage tax consultants",
        "exposure": 1.75
      }
    ]
  }
}
```

**PG-only tabs in `main_window_edu.py`:**

```python
# Add to _build_tabs() after DPCI tab:

from pmhelper.gui.tabs.swot_tab_edu import SWOTTabEdu
from pmhelper.gui.tabs.pestel_tab_edu import PESTELTabEdu

self._swot_tab = SWOTTabEdu(self.notebook, state=self.edu_state, main_window=self)
self.notebook.add(self._swot_tab, text="SWOT")

self._pestel_tab = PESTELTabEdu(self.notebook, state=self.edu_state, main_window=self)
self.notebook.add(self._pestel_tab, text="PESTEL")

# Mark as PG-only
self._pg_only_widgets.extend([self._swot_tab, self._pestel_tab])
self._all_tabs_ordered.extend(["swot", "pestel"])
```

**Tab refresh wiring (in `_refresh_all_edu_tabs()`):**

```python
def _refresh_all_edu_tabs(self):
    """Call on_tab_selected() or update() on all edu tabs when state changes."""
    # ...existing tabs...
    if hasattr(self, '_swot_tab'):
        self._swot_tab.update_from_analysis(self.edu_state)
    if hasattr(self, '_pestel_tab'):
        self._pestel_tab.update_from_analysis(self.edu_state)
```

**Export button wiring (Phase 9.3 + 9.7):**

Both SWOT and PESTEL tabs have:

- `[Auto-populate from Charter]` button → calls `SWOTExtractor.from_charter()`
- `[Auto-populate from Risks]` button (SWOT only) → calls `SWOTExtractor.from_risk_register()`
- `[Auto-populate from EVM]` button (SWOT only) → calls `SWOTExtractor.from_evm()`
- `[Add Factor]` button → dialog for manual entry
- `[Export as PNG]` button → calls `chart_export_edu.export_swot_png()`
- `[Export as PDF]` button → calls `chart_export_edu.export_swot_pdf()`
- `[Export as CSV]` button → calls `utils.export_to_csv()`
- `[Clear All]` button → confirmation dialog

---

### ✅ DONE — Phase 10: Polish & Packaging

| #    | Feature                                                           | Effort   | Priority | Status                               |
| ---- | ----------------------------------------------------------------- | -------- | -------- | ------------------------------------ |
| 10.1 | Recent files list in File menu                                    | 0.5 days | Low      | ✅ Done                              |
| 10.2 | Step-by-step walkthrough panel visible by default (not collapsed) | 0.5 days | Low      | ✅ Superseded by Phase 11 Worked Sol |
| 10.3 | PyInstaller `--onedir` build actually run and tested              | 1 day    | Low      | ⏳ Manual testing required           |
| 10.4 | UI smoke test — all 30 checklist items manually verified          | 1 day    | Low      | ⏳ Manual testing required           |
| 10.5 | Excel export for KPI table                                        | 1 day    | Low      | ✅ Done (EVM tab Export Excel btn)   |

---

### ✅ PHASE 9C: Work Breakdown Structure (WBS) Diagram (Complete)

> **Goal:** Interactive hierarchical WBS editor with tree visualization, validation, aggregation, and export.
> **Dependencies:** Requires Phases 0–8 complete (InputTabEdu for optional CPM task linking)
> **Priority:** P2 (must be in V1; educational value for teaching scope decomposition)
> **PG-Only:** Yes
> **Performance Target:** 3000 tasks, <2 sec full rebuild

#### Phase 9C — Data Model & Logic (4.5 days)

| #    | Task                                        | Files to Change / Create                                            | What to Do                                                                                                                                                                                              | Effort  | Status  |
| ---- | ------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 9.8  | WBS data model                              | **`core/wbs_models_edu.py`** (NEW)                                  | `WBSNode` dataclass (node_id, parent_id, name, description, owner, estimated_duration, estimated_cost, status, level, wbs_code, linked_task_id); `WBSStatus` enum (5 states); `to_dict()`/`from_dict()` | 1 day   | ✅ Done |
| 9.9  | WBS validator                               | **`core/wbs_validator_edu.py`** (NEW)                               | Validate: unique IDs, parent existence, single root, no cycles (DFS with recursion stack)                                                                                                               | 0.5 day | ✅ Done |
| 9.10 | WBS tree builder + level assignment + codes | **`core/wbs_builder_edu.py`** (NEW)                                 | Build tree from flat list (O(N) dict lookup); BFS level assignment (root=0); WBS code generation (1 → 1.1 → 1.1.1); work package identification (leaf = is_work_package)                                | 1 day   | ✅ Done |
| 9.11 | WBS aggregator (rollup)                     | **`core/wbs_aggregator_edu.py`** (NEW)                              | Cost: sum(children); Duration: max(children); Progress: weighted by cost. Post-order traversal with subtree caching. Invalidate cache on mutation.                                                      | 1 day   | ✅ Done |
| 9.12 | WBS I/O (save/load + CSV/JSON import)       | `utils/project_io_edu.py` (extend), **`utils/wbs_io_edu.py`** (NEW) | `.pmproj` `wbs_data` key; CSV import (`ID,ParentID,Name,Duration,Cost`); JSON import; hierarchical input support. Missing columns default: owner="Unassigned", status="not_started"                     | 1 day   | ✅ Done |

**Duration aggregation rule (corrected from naive sum):**

- **Cost:** Parent = sum(children) — always additive
- **Duration:** Parent = max(children) — assumes parallel unless told otherwise
- **Progress (weighted):** Parent = Σ(child_progress × child_cost) / Σ(child_cost)

**WBS Status enum (5 states with colours):**

```python
class WBSStatus(str, Enum):
    NOT_STARTED = "not_started"   # Light grey
    IN_PROGRESS = "in_progress"   # Yellow/Amber
    COMPLETED   = "completed"     # Green
    DELAYED     = "delayed"       # Red
    ON_HOLD     = "on_hold"       # Blue/Grey
```

#### Phase 9C — Layout & Visualization (3 days)

| #    | Task                                  | Files to Change / Create                | What to Do                                                                                                                                                                                   | Effort  | Status  |
| ---- | ------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 9.13 | Layout engine (Walker's algorithm)    | **`core/wbs_layout_edu.py`** (NEW)      | Walker's algorithm for variable-width rectangle nodes; top-down layout; y = level × vertical_spacing; children centered under parents; handles nodes up to 3000                              | 2 days  | ✅ Done |
| 9.14 | Visualization data model (graph repr) | In `core/wbs_layout_edu.py` (same file) | `LayoutNode` (id, x, y, width, height, label, wbs_code, level, cost, duration, progress, status) + `LayoutEdge` (source, target)                                                             | 0.5 day | ✅ Done |
| 9.15 | Matplotlib export renderer            | **`utils/wbs_export_edu.py`** (NEW)     | Render WBS tree to Matplotlib figure for PNG/PDF export; rectangles with WBS code + name + cost + duration; colour by level (dark→medium→light) + optional status colours (green/yellow/red) | 0.5 day | ✅ Done |

#### Phase 9C — Tab UI & Interactions (4 days)

| #    | Task                                   | Files to Change / Create                                         | What to Do                                                                                                                                                                       | Effort   | Status  |
| ---- | -------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------- |
| 9.16 | WBS Tab UI (Canvas renderer)           | **`gui/tabs/wbs_tab_edu.py`** (NEW), `main_window_edu.py` (wire) | Tkinter Canvas with rectangle nodes, connector lines, scroll, zoom (Ctrl+wheel); node rendering: WBS code + name + cost + duration; colour by level + status                     | 2 days   | ✅ Done |
| 9.17 | Interactions (expand/collapse/add/del) | In `gui/tabs/wbs_tab_edu.py`                                     | Click node → select; right-click → context menu (Add Child, Edit, Delete Subtree, Delete & Promote, Expand/Collapse); double-click → edit dialog; drag-reparent with visual cues | 1.5 days | ✅ Done |
| 9.18 | Export dialog (Excel/PDF/JSON + all)   | In `gui/tabs/wbs_tab_edu.py` + `utils/wbs_export_edu.py`         | Export button → dropdown: Excel (openpyxl), PDF (matplotlib), JSON, CSV, "All Formats"; table format: WBS Code / Level / Task / Cost / Duration / Progress                       | 0.5 day  | ✅ Done |

**Node rendering rules:**

- Shape: rounded rectangle
- Display: WBS Code (bold), Task Name, Cost, Duration
- Colour by level: Level 0 (root) → dark blue; Level 1 → medium blue; Level 2+ → progressively lighter
- Optional status overlay: Green border (completed), Yellow (in progress), Red (delayed), Grey (not started), Blue-grey (on hold)

**Delete semantics (resolved):**

- **Delete Subtree:** Removes node + all descendants. Parent's remaining children codes regenerated.
- **Delete & Promote:** Removes node only. Children move to deleted node's parent. WBS codes regenerated for affected subtree.
- Both operations trigger full WBS code re-generation on the affected parent's subtree.

**Undo mechanism:**

- 20-deep command stack: each Add/Delete/Edit/Reparent operation stores before-snapshot
- Ctrl+Z to undo; implemented as simple list of `(action, node_snapshots)` tuples

#### Phase 9C — Tests (1.5 days)

| #    | Task                           | Files to Change / Create                                                                | What to Do                                                                                                                         | Effort  | Status  |
| ---- | ------------------------------ | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 9.19 | WBS model + validator tests    | **`tests/test_wbs_models_edu.py`** (NEW), **`tests/test_wbs_validator_edu.py`** (NEW)   | Dataclass round-trip, validation rules, cycle detection (DFS), single root, unique IDs, parent existence                           | 0.5 day | ✅ Done |
| 9.20 | WBS builder + aggregator tests | **`tests/test_wbs_builder_edu.py`** (NEW), **`tests/test_wbs_aggregator_edu.py`** (NEW) | Tree construction, BFS levels, WBS code generation, work package identification, cost/duration/progress rollup, cache invalidation | 0.5 day | ✅ Done |
| 9.21 | WBS layout + export tests      | **`tests/test_wbs_layout_edu.py`** (NEW), **`tests/test_wbs_export_edu.py`** (NEW)      | Layout positions non-overlapping, children centered, export produces valid files, I/O round-trip (CSV/JSON/Excel)                  | 0.5 day | ✅ Done |

**Performance test:** Build + layout + render 3000-node tree in <2 sec (timed test).

#### Phase 9C — `.pmproj` Schema Addition

```json
{
  "wbs_data": {
    "nodes": [
      {
        "node_id": "1",
        "parent_id": null,
        "name": "PMhelper Edu V1",
        "description": "Complete project scope",
        "owner": "Project Lead",
        "estimated_duration": 0,
        "estimated_cost": 0,
        "status": "in_progress",
        "linked_task_id": null
      },
      {
        "node_id": "1.1",
        "parent_id": "1",
        "name": "EVM Module",
        "description": "Earned Value Management features",
        "owner": "Dev",
        "estimated_duration": 15,
        "estimated_cost": 12000,
        "status": "completed",
        "linked_task_id": null
      }
    ]
  }
}
```

---

## Key Decisions Log

All 12 decisions are resolved here. Record any changes to these in `DECISIONS.md`.

| #   | Decision                                             | Answer                                                                                                                                                | Reasoning                                                                                                                                                                                                                               |
| --- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | CPM tasks vs. EVM tasks — same class or separate?    | **Separate classes. `EVMTask` has an optional `cpm_task_id` link.**                                                                                   | The existing CPM task model is tightly coupled to `cpm_analyzer.py` and `network_builder.py`. Extending it would drag those dependencies into EVM code. A separate `EVMTask` also allows EVM-only projects with no network.             |
| 2   | Monte Carlo — extend `pert_analyzer.py` or new file? | **New `core/monte_carlo.py`.**                                                                                                                        | `pert_analyzer.py` is already 759 lines with its own I/O contracts and point-estimate outputs. Monte Carlo needs distributions, threading, and progress callbacks — a completely different interface.                                   |
| 3   | Data model base class — Pydantic or `@dataclass`?    | **Keep whatever the developer is comfortable with; plain Python `@dataclass` is fine.**                                                               | The existing Pydantic models are in `core/models.py` for the selection module only. EVM and Risk models are new and self-contained — no need to force Pydantic. Use `@dataclass` with manual validation methods; simpler to debug.      |
| 4   | Monte Carlo threading model?                         | **`threading.Thread` + `queue.Queue`.**                                                                                                               | Standard Tkinter threading pattern. Worker thread puts progress floats and the final result into a `Queue`; the main thread polls via `root.after(100, poll_queue)`. Do not call any Tkinter widget methods from the worker thread.     |
| 5   | PV spreading rule for "Compute from Tasks"?          | **Uniform only** — budget divided evenly across all periods the task spans.                                                                           | Sufficient for undergraduate teaching; avoids introducing a confusing setting. Front/back-loaded spreading is out of scope for V1.                                                                                                      |
| 6   | Shared state between tabs?                           | **Single `EduProjectState` object owned by `MainWindow`, passed to each tab constructor.**                                                            | Avoids global variables and avoids N×N inter-tab references. The existing app already passes `main_window` to every tab — `EduProjectState` lives on `main_window.edu_state`.                                                           |
| 7   | Which EAC formula feeds VAC and TCPI?                | **All three EAC values are computed and stored. VAC and TCPI each have a dropdown to select which EAC to use. Default: EAC₁ for TCPI; EAC₂ for VAC.** | Keeps the tool pedagogically honest — students can see how the choice of EAC changes forecasts.                                                                                                                                         |
| 8   | SWOT: auto-extract or manual-entry only?             | **Both auto-extract AND manual entry.** Extract from Charter, Risk Register, EVM KPIs; user can add/edit factors manually in the SWOT Tab UI.         | Auto-extract teaches cause-effect (Charter → SWOT, Risks → Threats, CPI < 0.95 → Weakness); manual editing allows users to add contextual factors and validate the extraction. Reduces data-entry burden while maintaining flexibility. |
| 9   | PESTEL: standalone or feed into Risk Register?       | **Both. PESTEL is a standalone analysis tool. High-impact PESTEL threats can optionally be added to Risk Register via "Create Risk" button.**         | Standalone PESTEL teaches external factor analysis separately from project-specific risks. Optional link to Risk Register preserves audit trail and allows qualitative factors to influence quantitative risk exposure.                 |
| 10  | WBS duration aggregation rule?                       | **max(children)** — assumes parallel execution by default. Cost is always sum(children). Progress is weighted by cost.                                | Naive sum is incorrect for PM (parallel tasks). Max is the safer default. Students learn that WBS = scope, not schedule.                                                                                                                |
| 11  | WBS layout algorithm?                                | **Walker's algorithm** for variable-width rectangle nodes. Falls back to simple layered (BFS + centering) for <50 nodes.                              | Reingold–Tilford designed for circles/binary trees; Walker's handles wide rectangles and variable fan-out correctly. Simple fallback avoids over-engineering small WBS trees.                                                           |
| 12  | WBS `Children_List` in data model?                   | **Not stored.** Computed from `parent_id` at tree-build time. Only `parent_id` is persisted.                                                          | Storing both `parent_id` and `children` creates sync risk. Single source of truth via `parent_id`; children computed dynamically in O(N).                                                                                               |

---

## First Day Checklist

Do these in order on Day 1 before writing any feature code.

1. Run `pytest` on the current `production` branch — record the baseline pass count. This is your regression baseline.
2. Create and switch to branch `feat/edu-v1` off `production`.
3. Open `DECISIONS.md` (create it if it doesn't exist) and confirm all 9 decisions above are written down.
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
│   ├── risk_register.py         ✅ DONE  ← Phase 3  (risk_register_edu.py)
│   ├── monte_carlo.py           ✅ DONE  ← Phase 4  (monte_carlo_edu.py)
│   ├── swot_models_edu.py       ❌ NEW  ← Phase 9A (SWOTFactor, SWOTAnalysis)
│   ├── pestel_models_edu.py     ❌ NEW  ← Phase 9B (PESTELFactor, PESTELAnalysis)
│   ├── wbs_models_edu.py        ❌ NEW  ← Phase 9C (WBSNode, WBSStatus)
│   ├── wbs_validator_edu.py     ❌ NEW  ← Phase 9C (validation + DFS cycle detection)
│   ├── wbs_builder_edu.py       ❌ NEW  ← Phase 9C (tree build + BFS levels + WBS codes)
│   ├── wbs_aggregator_edu.py    ❌ NEW  ← Phase 9C (rollup with caching)
│   └── wbs_layout_edu.py        ❌ NEW  ← Phase 9C (Walker's layout + LayoutNode/LayoutEdge)
├── gui/
│   ├── main_window.py           ✅ DONE  (main_window_edu.py — edu edition; Phase 9: wire SWOT + PESTEL tabs)
│   └── tabs/
│       ├── input_tab_edu.py     ✅ DONE  (EVM panel + period table + PV spreading)
│       ├── gantt_tab_edu.py     ✅ DONE  (baseline + tracking + arrows + today line)
│       ├── network_tab_edu.py   ✅ DONE  reused with edu wiring
│       ├── evm_tab_edu.py       ✅ DONE  ← Phase 2
│       ├── risk_tab_edu.py      ✅ DONE  (register CRUD + 5×5 heat map)
│       ├── pert_tab_edu.py      ✅ DONE  reused with edu wiring
│       ├── probability_tab_edu.py ✅ DONE (Monte Carlo + PERT Analysis sub-tabs)
│       ├── crashing_tab_edu.py  ✅ DONE  reused
│       ├── rcps_tab_edu.py      ✅ DONE  (schedule + histograms)
│       ├── rcps_crashing_tab.py ✅ DONE  (PG-only)
│       ├── dashboard_tab_edu.py ✅ DONE  ← Phase 5
│       ├── charter_tab.py       ✅ DONE  wired (PG-only)
│       ├── charter_manager.py   ✅ DONE  wired (PG-only)
│       ├── dpci_tab.py          ✅ DONE  wired (PG-only)
│       ├── swot_tab_edu.py      ❌ NEW  ← Phase 9A (2×2 SWOT matrix UI)
│       ├── pestel_tab_edu.py    ❌ NEW  ← Phase 9B (6-cell PESTEL heatmap UI)
│       └── wbs_tab_edu.py       ❌ NEW  ← Phase 9C (interactive WBS Canvas viewer + editor)
└── utils/
    ├── evm_io_edu.py            ✅ DONE  ← Phase 1
    ├── risk_io_edu.py           ✅ DONE  ← Phase 3
    ├── swot_extractor_edu.py    ❌ NEW  ← Phase 9A (auto-extraction from Charter/Risk/EVM)
    ├── wbs_io_edu.py             ❌ NEW  ← Phase 9C (CSV/JSON import, hierarchical input)
    ├── wbs_export_edu.py         ❌ NEW  ← Phase 9C (Excel/PDF/JSON/CSV export + Matplotlib renderer)
    ├── project_io_edu.py        ✅ DONE  ← Phase 5  (Phase 9: add SWOT+PESTEL+WBS keys)
    └── chart_export_edu.py      ✅ DONE  ← Phase 5  (Phase 9: add SWOT/PESTEL export functions)
```

**Tab structure inside `MainWindow` after Phases 0–9:**

```
Tab Name             Phase 8 Status              Phase 9 Target
──────────────────────────────────────────────────────────────────
Input Activities   ✅ done                       no change
Results            ✅ done                       no change
Network Diagram    ✅ done                       no change
PERT Diagram       ✅ done                       no change
Gantt Chart        ✅ done (arrows + today)      no change
EVM Dashboard      ✅ done                       no change
Risk Analysis      ✅ done                       no change
Probability        ✅ done (MC + PERT)           no change
Crashing           ✅ done                       no change
Resources (RCPS)   ✅ done (schedule)            no change
RCPS Crashing      ✅ done (PG-only)             no change
Dashboard          ✅ done                       no change
Project Charter    ✅ done (PG-only)             no change
Charter Manager    ✅ done (PG-only)             no change
DPCI Assessment    ✅ done (PG-only)             no change
SWOT Analysis      ❌ missing                    9A: 2×2 matrix (PG-only)
PESTEL Analysis    ❌ missing                    9B: 6-cell heatmap (PG-only)
WBS Diagram        ❌ missing                    9C: interactive tree (PG-only)
```

> **Tab overflow risk resolved:** 18 tabs total. Mitigation: short labels (≤ 12 chars). Test on 1366×768 screen. If overflow occurs, upgrade to collapsible tab groups in v1.1.

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

## Phase 8 — Remaining V1 Features (Added March 9, 2026; Revised March 10, 2026)

**Status:** ❌ Not started  
**Depends on:** Phases 0–7 (all complete)  
**Estimated effort:** ~10 working days (~2 calendar weeks)  
**All source code exists on the current branch.** No cherry-picking from `feat--sel-risk-da-co` is required — git diff confirms the relevant files are already identical or present.

These items complete the gap between the working app and the full V1 feature set. They are grouped into 7 independent workstreams that can be tackled in any order.

### Critique Log (March 10, 2026)

Issues found and corrected in this revision:

1. **`RCPSAnalyzer` has no `schedule()` method.** The original plan said "call `analyzer.schedule()`" but `RCPSAnalyzer`'s public API is: `forward_pass`, `backward_pass`, `calculate_float`, `get_critical_path`, `validate_resource_constraints`. Actual scheduling is done by the CPM/PERT analyzer's `build_cpm_schedule_table()` and `rcps_heuristic_schedule_table()` methods, which are called from `rcps_tab.py:run_rcps()`. Fixed in 8.2.
2. **`rcps_tab_clean.py` line count was wrong.** Plan said "1 745 lines" — that's `rcps_tab.py`. `rcps_tab_clean.py` is 414 lines on both branches (git diff is empty). The reference implementation for the RCPS Schedule sub-tab is `rcps_tab.py` (1 791 lines). Fixed in 8.2.
3. **RCPS Crashing files already exist on current branch.** Plan said "create `rcps_crashing_tab_edu.py`" and port from `feat--sel-risk-da-co`, but `rcps_crashing_tab.py` (49 lines), `rcps_crashing_tab_gui.py` (1 205 lines), and `project_crashing_core.py` (2 132 lines) all exist and import successfully. The task is **wiring**, not creation. Fixed in 8.3.
4. **DPCI tab was completely missing.** `dpci_tab.py` (400 lines) + `dpci_model.py` + `dpci_service.py` + `dpci_pdf_generator.py` exist on the current branch but were never in the plan. Added as 8.7.
5. **Feature count wrong.** Plan header said "39 V1 features" but `FEATURES_LIST_EDU.md` has ~50 V1 references. Fixed to "~50".
6. **`ProbabilityTabEdu` constructor is `(parent, state)`, not `(parent, state, main_window)`.** Plan 8.4 assumed a `self._main_window` reference that doesn't exist. Constructor must be updated to accept `main_window` or use `state` for analysis results. Fixed in 8.4.
7. **`CharterTab` calls `self.main_window.charter_manager.refresh()`.** Plan 8.5 didn't mention that `main_window_edu.py` must expose `self.charter_manager` as a public attribute (not just `self._charter_manager`). Fixed in 8.5.
8. **Missing help method stubs.** `MainWindowEdu` has `show_network_tab_help`, `show_results_tab_help`, `show_gantt_tab_help`, `show_crashing_tab_help` but NOT `show_probability_tab_help` or `show_charter_tab_help`. Stubs must be added. Noted in 8.4 and 8.5.
9. **Phase 8 had no effort estimates.** All other phases had duration estimates. Added per sub-task and in the status table.
10. **Gantt 8.1 and 8.2 were separate items in the status table but one section in the body.** Merged into a single item 8.1 throughout.
11. **Work Order referenced wrong sub-task numbers.** Fixed to use consistent numbering: 8.1 (Gantt), 8.2 (RCPS Schedule), 8.3 (RCPS Crashing wire), 8.4 (PERT Probability), 8.5 (Charter wire), 8.6 (Charter Manager wire), 8.7 (DPCI wire).

---

### 8.1 — Gantt Chart: Predecessor Arrows, Project Start Date, Today Line & Viz Fixes (~2 days)

**File to edit:** `src/pmhelper/gui/tabs/gantt_tab_edu.py` (322 lines)  
**Reference implementation:** `src/pmhelper/gui/tabs/gantt_tab.py` (951 lines, already on current branch — verified by import)

**What to add:**

1. **"Show Predecessor Arrows" checkbox** (`BooleanVar`, default `True`)
   - Draw annotated arrows from the EF of each predecessor to the ES of its successor on the CPM Gantt.
   - Use `ax.annotate()` with `arrowprops=dict(arrowstyle='->', color='#555')` pointing from `(EF_pred, y_pred)` to `(ES_succ, y_succ)`.
   - Predecessors come from `results_data['activities'][i]['predecessors']` (list of predecessor IDs).
   - Wire checkbox command to `self._draw_gantt()`.

2. **"Show Today Line" checkbox** (`BooleanVar`, default `False`)
   - Compute offset: `(datetime.today() - project_start_date).days` (1 period = 1 day default).
   - Draw `ax.axvline(x=today_offset, color='red', linestyle='--', linewidth=1.5, label='Today')`.
   - Wire checkbox command to `self._draw_gantt()`.

3. **"Project Start Date" entry** (`StringVar`, default = today as `YYYY-MM-DD`)
   - `ttk.LabelFrame("Project Dates")` with label + entry + update button.
   - Parse with `datetime.strptime(val, "%Y-%m-%d")`; store as `self._project_start: datetime`.
   - Convert CPM period units to dates: `start_date + timedelta(days=period_value)`.

4. **Chart visualisation fixes:**
   - `self._fig.subplots_adjust(left=0.25)` or `tight_layout(pad=1.2)` — prevent y-axis label clipping.
   - Grid lines: `ax.set_axisbelow(True); ax.xaxis.grid(True, linestyle='--', alpha=0.4)`.
   - Truncate y-axis labels at 25 characters.
   - Thin horizontal rules: `ax.hlines(y - 0.5, xmin, xmax, colors='#eee', linewidth=0.5)`.
   - Background: white figure, `#fafafa` axes face.

**Acceptance test:**  
Load any CPM project → Gantt renders without clipping → enable predecessor arrows → arrows appear → enable today line → red dashed line appears → change project start date → x-axis date labels update.

---

### 8.2 — RCPS Tab: Full Resource-Constrained Scheduling Sub-Tab (~3 days)

**File to edit:** `src/pmhelper/gui/tabs/rcps_tab_edu.py` (132 lines)  
**Reference implementation:** `src/pmhelper/gui/tabs/rcps_tab.py` (1 791 lines, already on current branch)  
**Core algorithm:** `src/pmhelper/core/rcps_analyzer.py` (215 lines, already on current branch)

**Current state:** `RCPSTabEdu.__init__(parent, state)` — has only a "Histograms" sub-tab. No `main_window` reference.

**Constructor change required:** Add `main_window=None` parameter:

```python
def __init__(self, parent, state, main_window=None):
    self._main_window = main_window
```

Also update `main_window_edu.py` call site to pass `main_window=self`.

**What to add — new "RCPS Schedule" sub-tab** (insert as the first sub-tab, before "Histograms"):

1. **Control panel (top strip):**
   - `ttk.Label("Resource Limit:") + ttk.Spinbox(width=5)` — integer, default 5
   - `ttk.Label("Priority Rule:") + ttk.Combobox` — values: `['minimum_slack', 'shortest_duration', 'earliest_start']`
   - `ttk.Button("Run RCPS")` → `self._run_rcps()`

2. **`_run_rcps()` method — CORRECTED API:**
   - **Do NOT call `RCPSAnalyzer.schedule()` — that method does not exist.**
   - Instead, follow the pattern in `rcps_tab.py:run_rcps()` (line 399):
     1. Get the active analyzer from `self._main_window` (CPM or PERT analyzer depending on mode).
     2. Get the dataframe via `self._main_window.current_data`.
     3. Call `analyzer.build_cpm_schedule_table(df, resource_limit)` → CPM table.
     4. Call `analyzer.rcps_heuristic_schedule_table(df, resource_limit, priority_rule=rule)` → RCPS table.
     5. Build a NetworkX graph from the RCPS table and create `RCPSAnalyzer(G, resource_limit, analyzer)` for downstream use.
   - Guard: if `self._main_window.last_analysis_results is None`, show `messagebox.showwarning("No CPM data", "Run CPM analysis first.")` and return.
   - Catch exceptions → `messagebox.showerror()`.

3. **Results display (two panes):**
   - **Left — Comparison table** (`ttk.Treeview`):
     Columns: Task | CPM Start | CPM Finish | RCPS Start | RCPS Finish | Delay.
     Colour-coded rows: green (no delay), amber (delay ≤ 2), red (delay > 2).
     Footer: `"CPM duration: X  |  RCPS duration: Y  |  Total delay: Z"`
   - **Right — Comparison Gantt** (`FigureCanvasTkAgg`):
     Two ribbons per task: CPM bar (blue) and RCPS bar (orange).
     Export PNG/PDF buttons.

4. **`update_from_analysis(results_data, analysis_mode)` public method** — cache latest results for the Run RCPS button.

**Acceptance test:**  
Load CPM project → run CPM analysis → Resources tab → "RCPS Schedule" sub-tab → set resource limit → Run RCPS → comparison table + Gantt render → "Histograms" sub-tab still accessible.

---

### 8.3 — RCPS Crashing Tab: Wire Existing Code Into Edu Main Window (~1 day)

**Files already on current branch (verified — all import successfully):**

- `src/pmhelper/gui/tabs/rcps_crashing_tab.py` — 49 lines, thin wrapper, `RCPSCrashingTab(ttk.Frame)`, constructor: `(master, main_window)`
- `src/pmhelper/gui/tabs/rcps_crashing_tab_gui.py` — 1 205 lines, `RCPSCrashingTabGUIManager`
- `src/pmhelper/gui/tabs/project_crashing_core.py` — 2 132 lines, `RCPSProjectCrashing` + helpers

**There is NO need to create an `rcps_crashing_tab_edu.py` wrapper.** The existing `RCPSCrashingTab` already extends `ttk.Frame` and takes `(master, main_window)` — compatible with `notebook.add()`.

**What to do in `main_window_edu.py`:**

1. Import:

   ```python
   from pmhelper.gui.tabs.rcps_crashing_tab import RCPSCrashingTab
   ```

2. In `_build_tabs()`, after the Resources tab:

   ```python
   # 11. RCPS Crashing (PG-only) — wire existing tab
   self._rcps_crashing_tab = RCPSCrashingTab(self.notebook, main_window=self)
   self.notebook.add(self._rcps_crashing_tab, text="RCPS Crashing")
   ```

3. Wire the bidirectional link after both tabs exist:

   ```python
   self._rcps_crashing_tab.set_rcps_tab_reference(self._rcps_tab)
   ```

   **Note:** `set_rcps_tab_reference()` calls `self.rcps_tab.set_rcps_crashing_tab(self)` internally — but `RCPSTabEdu` currently lacks a `set_rcps_crashing_tab()` method. Add a stub:

   ```python
   # In RCPSTabEdu:
   def set_rcps_crashing_tab(self, tab):
       self._rcps_crashing_tab = tab
   ```

   Also add `get_rcps_analyzer()`, `get_resource_limit()`, `get_rcps_table_data()` methods to `RCPSTabEdu` matching the interface `RCPSCrashingTab` expects from its RCPS tab reference.

4. Add to `self._all_tabs_ordered` and `self.tabs["rcps_crashing"]`.

5. Add `self._rcps_crashing_tab` to `self._pg_only_widgets` — PG-only.

**Acceptance test:**  
App launches → PG mode → "RCPS Crashing" tab visible → run RCPS first → switch to RCPS Crashing → select activity → crash step table renders → crashing cost curve renders → UG mode → tab hidden.

---

### 8.4 — Probability Tab: PERT Analysis Sub-Tab (~2 days)

**File to edit:** `src/pmhelper/gui/tabs/probability_tab_edu.py` (247 lines)  
**Reference implementation:** `src/pmhelper/gui/tabs/probability_tab.py` (1 055 lines, on current branch)  
**Core dependency:** `pmhelper.utils.calculations.ProbabilityCalculations` (on current branch)

**Current state:** `ProbabilityTabEdu.__init__(parent, state)` — only Monte Carlo sub-tab.

**Constructor change required:** Add `main_window=None` parameter:

```python
def __init__(self, parent, state, main_window=None):
    self._main_window = main_window
```

Update `main_window_edu.py` call site to pass `main_window=self`.

**Missing help stub:** Add to `MainWindowEdu`:

```python
def show_probability_tab_help(self):
    from tkinter import messagebox
    messagebox.showinfo("Probability Help",
        "PERT Analysis: View project duration statistics and calculate completion probabilities.\n"
        "Monte Carlo: Run N-trial simulations for duration and cost distributions.")
```

**What to add — new "PERT Analysis" sub-tab** (insert as first sub-tab, before "Monte Carlo"):

Guard: only meaningful after PERT analysis. Check `self._main_window.last_analysis_results` and `self._main_window.analysis_mode == 'probabilistic'`. If unavailable, show placeholder: `"Run PERT analysis to populate this tab."`.

Layout (horizontal `ttk.PanedWindow`):

**Left pane — Controls & Statistics:**

1. **Project Duration Statistics** (`ttk.LabelFrame`): Expected Duration, Variance, Std Dev, 95% CI — from `ProbabilityCalculations.calculate_project_statistics(results_data)`.

2. **Completion Probability Calculator** (`ttk.LabelFrame`):
   - Target Duration → Calculate Probability
   - Target Percentage → Calculate Duration
   - Results labels + Clear button

3. **Common Scenarios** (`ttk.LabelFrame`): `Expected`, `+1σ`, `-1σ`, `+2σ`, `-2σ` quick-fill buttons.

4. **Risk Analysis** (`ttk.LabelFrame`): Risk level + high-risk activities list from `ProbabilityCalculations.identify_high_risk_activities()`.

5. **Export buttons**: Export Analysis (JSON), Generate Report (text).

**Right pane — Chart:**

1. Chart type selector: `distribution` | `cumulative` | `sensitivity`
2. `FigureCanvasTkAgg` with `figsize=(8, 5)`
3. Export PNG/PDF buttons

**`update_from_analysis(results_data, analysis_mode)` public method** — auto-populate statistics on PERT mode; show info label on CPM mode.

**Acceptance test:**  
PERT project → run PERT → Probability tab → "PERT Analysis" is first → stats populated → enter target duration → correct probability → all 3 chart types render → Monte Carlo sub-tab still works.

---

### 8.5 — Project Charter & Manager: Wire Into Edu Main Window (~1 day, PG-only)

**All files exist and import cleanly (verified):**

- `charter_tab.py` (627 lines) — `CharterTab(ttk.Frame)`, constructor: `(parent, main_window)`
- `charter_manager.py` (414 lines) — `CharterManager(ttk.Frame)`, constructor: `(parent, on_open_callback=None, on_duplicate_callback=None)`
- `charter_form.py`, models, services, dialogs — all present

**What to do in `main_window_edu.py`:**

1. Import:

   ```python
   from pmhelper.gui.tabs.charter_tab import CharterTab
   from pmhelper.gui.tabs.charter_manager import CharterManager
   ```

2. In `_build_tabs()`:

   ```python
   # 12. Project Charter (PG-only)
   self._charter_tab = CharterTab(self.notebook, main_window=self)
   self.notebook.add(self._charter_tab, text="Charter")

   # 13. Charter Manager (PG-only)
   self.charter_manager = CharterManager(   # ← PUBLIC attribute, NOT self._charter_manager
       self.notebook,
       on_open_callback=self._charter_tab.open_charter_file,
       on_duplicate_callback=self._charter_tab.duplicate_charter_file,
   )
   self.notebook.add(self.charter_manager, text="Charter Mgr")
   ```

   **Critical:** `CharterTab._refresh_charter_manager()` accesses `self.main_window.charter_manager.refresh()` via `hasattr`. The attribute **must** be `self.charter_manager` (public), not `self._charter_manager`.

3. Add both to `self._all_tabs_ordered` and `self.tabs`.

4. Add both to `self._pg_only_widgets` — PG-only.

5. **Add help stub** to `MainWindowEdu`:
   ```python
   def show_charter_tab_help(self):
       from tkinter import messagebox
       messagebox.showinfo("Project Charter Help",
           "Create, edit, and manage project charters.\n"
           "Use templates for quick starts. Export to PDF.")
   ```

**Acceptance test:**  
PG mode → "Charter" and "Charter Mgr" tabs visible → create charter from template → fill fields → save → Charter Mgr shows entry → UG mode → both tabs hidden.

---

### 8.6 — (Merged into 8.5 — Charter Manager is wired together with Charter Tab)

_(Charter Manager wiring is included in 8.5 above since the two tabs share callbacks and must be created together.)_

---

### 8.7 — DPCI Assessment Tab: Wire Into Edu Main Window (~0.5 days, PG-only)

**Files already on current branch (verified):**

- `src/pmhelper/gui/tabs/dpci_tab.py` (400 lines) — `DPCITab(ttk.Frame)`, constructor: `(parent)` — takes only `parent`, no `state` or `main_window`
- `src/pmhelper/gui/models/dpci_model.py` — `DPCIAssessment`, `DPCICalculator`, `RiskLevel`
- `src/pmhelper/gui/services/dpci_service.py` — `DPCIService`
- `src/pmhelper/gui/utils/dpci_pdf_generator.py` — `DPCIPDFGenerator`

**What to do in `main_window_edu.py`:**

1. Import:

   ```python
   from pmhelper.gui.tabs.dpci_tab import DPCITab
   ```

2. In `_build_tabs()`:

   ```python
   # 14. DPCI Assessment (PG-only)
   self._dpci_tab = DPCITab(self.notebook)
   self.notebook.add(self._dpci_tab, text="DPCI")
   ```

3. Add to `self._all_tabs_ordered` and `self.tabs["dpci"]`.

4. Add `self._dpci_tab` to `self._pg_only_widgets` — PG-only.

**Acceptance test:**  
PG mode → "DPCI" tab visible → create new assessment → fill categories → calculate index → result renders → UG mode → tab hidden.

---

### Phase 8 — Work Order & Dependencies

All sub-tasks are **independent** and can be done in any order. Suggested sequence for lowest risk:

```
8.5  (Charter + Manager wire-up)       ← simplest; code already exists, just wire + expose attribute (0.5–1 day)
8.7  (DPCI wire-up)                    ← trivial; DPCITab takes only parent (0.5 day)
8.3  (RCPS Crashing wire-up)           ← wire existing tab + add compat stubs on RCPSTabEdu (1 day)
8.1  (Gantt arrows, today, dates, viz) ← self-contained, port from gantt_tab.py (2 days)
8.4  (PERT Probability sub-tab)        ← most new code; port from probability_tab.py (2 days)
8.2  (RCPS Schedule sub-tab)           ← most complex; follow rcps_tab.py:run_rcps() pattern (3 days)
```

### Phase 8 — Cross-Cutting Concerns

These items affect multiple sub-tasks and must be addressed during implementation:

1. **`_PG_ONLY_TABS` constant** (line 27 of `main_window_edu.py`): Currently `{"probability", "rcps"}`. Must be updated to include `"rcps_crashing"`, `"charter"`, `"charter_manager"`, `"dpci"`.

2. **`_all_tabs_ordered` list** must match the notebook tab indices exactly after adding 4 new tabs. The index-based `_on_tab_changed()` logic depends on this being correct.

3. **Help method stubs**: `MainWindowEdu` must have stubs for `show_probability_tab_help()` and `show_charter_tab_help()` — called by the respective tab modules.

4. **Tab overflow on small screens**: With 15 tabs, test on 1366×768 resolution. If tab headers overflow, shorten labels: "Resources" → "RCPS", "Charter Manager" → "Charter Mgr", "RCPS Crashing" → "RCPS Crash".

5. **341 existing tests must remain green** after all Phase 8 changes. Run `pytest` after each sub-task.

### Phase 8 — Acceptance Checklist

- [ ] 8.1: Gantt renders predecessor arrows when checkbox is on
- [ ] 8.1: Today line appears as a dashed red vertical line
- [ ] 8.1: Project start date entry changes x-axis date labels
- [ ] 8.1: Task names never clipped on y-axis; grid lines visible
- [ ] 8.2: "RCPS Schedule" sub-tab present in Resources tab
- [ ] 8.2: Run RCPS shows comparison table (CPM vs RCPS) and Gantt
- [ ] 8.2: RCPS uses `analyzer.rcps_heuristic_schedule_table()`, NOT `RCPSAnalyzer.schedule()`
- [ ] 8.3: "RCPS Crashing" tab visible in PG mode, hidden in UG mode
- [ ] 8.3: Crashing cost curve renders for a simple network
- [ ] 8.3: `RCPSTabEdu` exposes `get_rcps_analyzer()`, `get_resource_limit()`, `get_rcps_table_data()`
- [ ] 8.4: "PERT Analysis" sub-tab is the first sub-tab in Probability tab
- [ ] 8.4: Statistics labels populate after PERT analysis run
- [ ] 8.4: "Calculate Probability" gives correct value for a known PERT network
- [ ] 8.4: Distribution / Cumulative / Sensitivity charts all render
- [ ] 8.4: `show_probability_tab_help()` stub exists on `MainWindowEdu`
- [ ] 8.5: "Charter" and "Charter Mgr" tabs visible in PG mode, hidden in UG mode
- [ ] 8.5: Charter can be created, saved, and listed in Charter Manager
- [ ] 8.5: `self.charter_manager` is a public attribute on `MainWindowEdu`
- [ ] 8.5: `show_charter_tab_help()` stub exists on `MainWindowEdu`
- [ ] 8.7: "DPCI" tab visible in PG mode, hidden in UG mode
- [ ] 8.7: DPCI assessment can be created and calculated
- [ ] `pytest` passes with 0 regressions (341+ tests) after all Phase 8 items

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
Week 19–21   │ Phase 8: Remaining V1 Features (~2 wks — see sub-task estimates)
─────────────────────────────────────────────────────────────────────────
TOTAL        │ ~21 calendar weeks  (~24 weeks of actual work;
             │  Phase 2 ∥ Phase 3 recovers ~2 weeks;
             │  ~1 week buffer distributed in Phases 4–6;
             │  Phase 8 parallel sub-tasks recover ~0.5 weeks)
```

### Critical Path

```
Phase 0 → Phase 1 → Phase 2 ──────────────────────────→ Phase 5 → Phase 6 → Phase 8
                   ↘                                   ↗
                    Phase 3 → (feeds Phase 4 MC cost) ↗
                              ↑
                    Phase 4.3 also needs Phase 1 task date fields
```

**Phase 1 is the irreducible blocker.** The `EVMTask` date fields (`planned_start`, `planned_finish`, `baseline_start`, `baseline_finish`) must be in place before Phase 4.3 (Tracking Gantt) can begin, even though Phase 4 officially starts after Phase 2.

**Phase 8 is parallelisable.** All 7 sub-tasks are independent. With 2 parallel workstreams, ~10 working days compress to ~1.5 calendar weeks.

---

### ✅ PHASE 11 — UG Worked Solutions (Complete)

> **Status:** Planned — not started
> **Goal:** Make UG mode genuinely educational by turning every numeric result into a readable, multi-step worked solution using the project's actual data. Students see exactly how each answer was derived — formula → substitution → result — without having to leave the app.
> **UG-Only:** Yes (PG students are assumed to already know the mechanics; UG students are learning them)
> **Deferred:** Practice Calculator (student enters own numbers) — Phase 11B

#### What's wrong with the current step-by-step

The existing EVM "Step-by-Step Walkthrough" is **3 static labels** embedded inline (formula / substitution / result). It only covers single-formula KPIs, is not scrollable, has no multi-step chaining, and cannot represent PERT's 6-step pipeline or CPM's forward/backward pass. This phase replaces and extends it with a proper worked-solution system.

#### Design: "Worked Solution" Window

A **modal Toplevel window** opened by a **"Show Worked Solution"** button on each relevant tab/panel. Renders a scrollable, multi-step breakdown using the project's real numbers.

**Key design principles:**

1. **Multi-step chain** — each step feeds the next, with visual separators
2. **Three-column layout per step:** symbolic formula | substitution with numbers | numerical result
3. **Colour-coded results:** green = favourable, red = unfavourable, blue = neutral
4. **Collapsible sub-steps** — e.g. per-activity breakdown inside "Step 1: Expected Durations"
5. **Copy-friendly** — "Copy as Text" button produces clean text for pasting into reports/assignments
6. **Export** — "Export PDF" renders the solution to a Matplotlib figure (same export pattern as charts)

**Example — PERT Z-score for target = 30 days:**

```
┌────────────────────────────────────────────────────────────────┐
│ Step 1: Activity Expected Durations                  [▼ Show] │
│   SD1: tₑ = (2 + 4×5 + 14) / 6 = 36/6               = 6.00  │
│   SD3: tₑ = (3 + 4×7 + 12) / 6 = 43/6               = 7.17  │
│   ...                                                          │
├────────────────────────────────────────────────────────────────┤
│ Step 2: Activity Variances (critical path activities only)     │
│   SD1: σ² = ((14−2)/6)² = (12/6)² = 2²              = 4.00  │
│   SD3: σ² = ((12−3)/6)² = (9/6)²  = 1.5²            = 2.25  │
├────────────────────────────────────────────────────────────────┤
│ Step 3: Project Variance                                       │
│   σ²_proj = 4.00 + 2.25 + 1.00                      = 7.25  │
├────────────────────────────────────────────────────────────────┤
│ Step 4: Project Standard Deviation                             │
│   σ = √7.25                                          = 2.69  │
├────────────────────────────────────────────────────────────────┤
│ Step 5: Z-Score  (target = 30 days)                            │
│   Z = (30 − 27.5) / 2.69 = 2.5 / 2.69              = 0.93  │
├────────────────────────────────────────────────────────────────┤
│ Step 6: Probability from Z-table                               │
│   P(T ≤ 30) = Φ(0.93)                              = 82.4%  │
│   ✅ Good chance of on-time completion                         │
└────────────────────────────────────────────────────────────────┘
                                     [Copy as Text]  [Export PDF]
```

#### Architecture

```
core/step_generators_edu.py          ← Pure logic, zero UI dependency
  @dataclass Step:
      title: str
      formula: str           # symbolic: "σ² = ((p − o) / 6)²"
      substitution: str      # with numbers: "σ² = ((14 − 2) / 6)²"
      result: str            # "= 4.00"
      interpretation: str    # "Low variance — estimate is tight"
      rag: str               # "green" | "red" | "amber" | "neutral"
      children: List[Step]   # sub-steps (e.g., per-activity rows)

  pert_steps(activities, critical_path, target_duration) → List[Step]
  evm_steps(project, period, primary_eac) → List[Step]
  cpm_forward_steps(tasks) → List[Step]
  cpm_backward_steps(tasks) → List[Step]

gui/widgets/worked_solution_window.py  ← Reusable Tk Toplevel
  WorkedSolutionWindow(parent, title, steps: List[Step])
    - ttk.Frame with scrollbar
    - Each Step rendered as a card (LabelFrame) with expand/collapse
    - Sub-steps indented inside parent card
    - "Copy as Text" button → clipboard
    - "Export PDF" button → Matplotlib figure → filedialog save
```

#### Phase 11A — Tasks (7 days, UG-only)

| #    | Task                                    | Files to Create / Change                                       | What to Do                                                                                                                                | Effort   | Status  |
| ---- | --------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------- |
| 11.1 | `Step` data model + PERT step generator | **`core/step_generators_edu.py`** (NEW)                        | `Step` dataclass; `pert_steps()` producing 6 steps: tₑ per activity, σ² per activity, path variance, σ, Z, P(Z)                           | 2 days   | ✅ Done |
| 11.2 | EVM step generator                      | `core/step_generators_edu.py` (extend)                         | `evm_steps()` producing full KPI chain: PV→EV→AC→CV/SV→CPI/SPI→EAC→VAC→TCPI, each building on prior                                       | 1.5 days | ✅ Done |
| 11.3 | CPM forward + backward step generators  | `core/step_generators_edu.py` (extend)                         | `cpm_forward_steps()` (ES/EF per node in topological order, showing max-predecessor logic); `cpm_backward_steps()` (LF/LS, Float = LS−ES) | 1.5 days | ✅ Done |
| 11.4 | `WorkedSolutionWindow` widget           | **`gui/widgets/worked_solution_window.py`** (NEW)              | Scrollable Toplevel; Step cards with expand/collapse; colour coding by RAG; Copy + Export PDF buttons                                     | 2 days   | ✅ Done |
| 11.5 | Wire buttons into tabs (UG mode only)   | `probability_tab_edu.py`, `evm_tab_edu.py`, `gantt_tab_edu.py` | "Show Worked Solution" buttons; hidden in PG mode via `set_mode()`; opens `WorkedSolutionWindow`                                          | 0.5 day  | ✅ Done |
| 11.6 | Tests for step generators               | **`tests/test_step_generators_edu.py`** (NEW)                  | 36 known-value assertions for all three generators; verify step count, formula strings, result values, RAG classification                 | 1 day    | ✅ Done |

**Total Phase 11A: 8.5 days**

#### Phase 11B — Practice Calculator (Deferred)

Separate dialog where students input their **own** numbers (not from the project) and the app solves step-by-step in real time. Useful for exam prep. Deferred because it requires a full input form + live recalculation loop, and Phase 11A already covers the highest-value use case (project data).

#### Decisions

| #   | Decision                                   | Answer                                                                                                 |
| --- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| 1   | Inline panel or Toplevel window?           | **Toplevel** — inline panel is too cramped for 6-step PERT chain; modal window gives full space        |
| 2   | Replace or extend current EVM walkthrough? | **Replace** — current 3-label widget becomes the "Show Worked Solution" button; Toplevel supersedes it |
| 3   | UG-only or both modes?                     | **UG-only** — PG students already know derivations; showing steps in PG mode clutters the workflow     |
| 4   | Practice Calculator in Phase 11A?          | **Deferred to Phase 11B** — separate input form + live recalculation is a distinct scope increment     |

---

### ✅ PHASE 12 — Schedule Process Stepper (Complete)

> **Goal:** Turn the 5 PMBOK scheduling process steps into a visible, interactive progress bar inside the Input Activities tab so that students understand _where they are_ in the schedule development workflow — not just _what buttons to press_.
> **Dependencies:** Phases 0–8 complete, Phase 11 (Step dataclass reuse)
> **Priority:** P1 — this is the main pedagogical gap remaining: data entry tabs exist, but students get no signal about the overall scheduling process
> **Scope:** UG + PG (both modes — detection logic adapts per mode)

#### Why This Matters

The app already covers all 5 PMBOK scheduling steps across various tabs:

| PMBOK Scheduling Step   | Tab / Control That Covers It                              |
| ----------------------- | --------------------------------------------------------- |
| 1. Define Activities    | Input Activities (activity rows) + WBS (PG)               |
| 2. Sequence Activities  | Input Activities → Predecessors column → Network Diagram  |
| 3. Estimate Resources   | Input Activities → Resource Demand column + Resources tab |
| 4. Estimate Durations   | Input Activities → Duration (CPM) or o/m/p (PERT) columns |
| 5. Develop the Schedule | ▶ Analyze → Gantt / Results / Network / Critical Path     |

**The problem:** Nothing tells the student "here are 5 steps — you've done 2 of them." The tabs are a flat list. Students skip ahead, forget predecessors, and get confused when analysis produces a trivial network. A visible stepper widget fixes this with zero changes to the underlying logic.

#### Critique of Initial Design & Corrections

The original Phase 12 plan had these flaws — all addressed in this revised version:

| #   | Original Flaw                                                                                                                                                                                                                                                                                                           | Correction                                                                                                                                                                                                  |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **12A "Schedule Guide" as a worked-solution popup was too passive.** It's just a tutorial in a modal — students won't read static text about "what is Step 1" with no connection to their data. The `WorkedSolutionWindow` is designed for _calculations_ (formula→substitution→result), not for conceptual checklists. | **Removed 12A entirely.** The step descriptions become tooltip/popover text _inside_ the stepper badges. Context where you need it, not in a separate window.                                               |
| 2   | **`root.after(1500)` polling is wasteful and fragile.** Polling every 1.5s to detect tree changes creates unnecessary CPU load, and `root.after` callbacks need careful teardown when the tab is destroyed or the window is closed.                                                                                     | **Event-driven refresh.** Call `stepper.refresh()` from the 6 methods that already mutate data: `add_row()`, `delete_row()`, `clear_all()`, `load_file()`, `_save_edit()`, `_run_analysis()`. Zero polling. |
| 3   | **Step 3 (Estimate Resources) was required — but Resource Demand is optional.** Many UG projects work perfectly without resource data. Showing a red badge for a step the student doesn't need creates confusion.                                                                                                       | **Step 3 is marked "optional"** — badge shows "○ optional" in grey by default, turns green only if any activity has Resource Demand > 0. Never red.                                                         |
| 4   | **Step 2 detection was naive** — "≥1 activity has Predecessors" fails because the first activity legitimately has no predecessors.                                                                                                                                                                                      | **Smarter detection:** Step 2 = complete when activity_count ≤ 1 OR at least one non-first activity has a non-empty Predecessors field. A single-activity project has no sequencing to do.                  |
| 5   | **12C contextual hints were redundant with the stepper.** Both the stepper badge and a separate hint banner saying "No predecessors set" deliver the same information. This clutters the UI.                                                                                                                            | **Merged into stepper tooltips.** Each incomplete badge shows a one-line hint on hover explaining what to do next. No separate banner widget.                                                               |
| 6   | **UG-only was wrong.** PG students also need workflow guidance. The only detection difference is Step 1 in PG mode (WBS exists OR activities entered vs. just activities). That's one `if` statement, not a reason to hide the whole widget.                                                                            | **Both modes.** Step 1 detection adapts: UG checks activity rows; PG also accepts WBS tree with ≥ 1 child node as "defined".                                                                                |
| 7   | **Three sub-phases (12A/12B/12C) for one feature over-fragmented the work.** This is a single widget with a single purpose.                                                                                                                                                                                             | **One phase, 4 tasks.** Widget + wiring + tests + plan update.                                                                                                                                              |

#### Step Completion Detection Logic

All reads are from existing data — no new state needed.

| Step | Badge Label         | Complete When                                                   | Source                                                  |
| ---- | ------------------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| 1    | Define Activities   | ≥ 1 activity with non-empty ID in tree                          | `input_tab.get_activities_data()`                       |
| 2    | Sequence Activities | `activity_count ≤ 1` OR ≥ 1 activity has non-empty Predecessors | `get_activities_data()` → check `predecessors` field    |
| 3    | Estimate Resources  | _(Optional)_ Any activity has Resource Demand > 0               | `get_activities_data()` → check `resource_demand` field |
| 4    | Estimate Durations  | All activities have Duration > 0 (CPM) or Optimistic > 0 (PERT) | `get_activities_data()` → check by `current_mode`       |
| 5    | Develop Schedule    | `main_window.results_data is not None`                          | Direct attribute check                                  |

**PG-mode Step 1 override:** Also complete if `state.wbs_tree` has ≥ 1 child node (i.e., student defined scope via WBS).

#### Badge State Machine

Each badge has exactly 3 visual states:

```
┌──────────────────────────────────────────┐
│  ● complete  (green bg, ✓ icon)          │
│  ○ pending   (grey outline, step number) │
│  ○ optional  (grey dashed, "optional")   │  ← Step 3 only
└──────────────────────────────────────────┘
```

No "red/failed" state — the stepper is encouraging, not punitive. Incomplete badges show the step number and a subtle grey background. Hovering shows a one-line tooltip explaining what to do.

#### Badge Click → Tab Navigation

| Badge Clicked           | Action                                                            |
| ----------------------- | ----------------------------------------------------------------- |
| 1 — Define Activities   | Switch to Input Activities tab (already there — no-op)            |
| 2 — Sequence Activities | Switch to Input Activities tab, flash Predecessors column header  |
| 3 — Estimate Resources  | Switch to Resources tab (PG) or flash Resource Demand column (UG) |
| 4 — Estimate Durations  | Switch to Input Activities tab, flash Duration column header      |
| 5 — Develop Schedule    | Click ▶ Analyze if data exists, else flash Analyze button         |

"Flash" = 3× blink the column header background between yellow and default over 500ms — draws the eye without being jarring.

#### Architecture

```
gui/widgets/schedule_stepper_edu.py     ← New widget, zero business logic
  class ScheduleStepperWidget(ttk.Frame):
    __init__(parent, main_window)
    refresh()                          ← Called by InputTabEdu after mutations
    _detect_steps() → dict[int, str]   ← Returns {1: "complete", 2: "pending", ...}
    _on_badge_click(step_num)          ← Tab navigation + column flash
    _build_badges()                    ← 5 LabelFrames in a horizontal row

gui/tabs/input_tab_edu.py              ← Embed stepper, add refresh() calls
  - Insert stepper below button_frame (before mode_label)
  - Add self._stepper.refresh() to: add_row, delete_row,
    clear_all_without_confirmation, load_file, _save_edit

gui/main_window_edu.py                 ← Post-analysis refresh
  - After analyze_project() succeeds, call
    self._input_tab_edu._stepper.refresh()

tests/test_schedule_stepper_edu.py     ← Detection logic tests
```

#### Visual Layout (in Input Activities tab)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Load CPM] [Load PERT] [Auto-Detect] [Add Row] [Del Row] [Clear] [▶]  │  ← button_frame
├─────────────────────────────────────────────────────────────────────────┤
│ [1 Define ✓]──►[2 Sequence ✓]──►[3 Resources ○]──►[4 Durations ✓]──►[5 Analyse ○]  │  ← stepper
├─────────────────────────────────────────────────────────────────────────┤
│ Mode: Deterministic (CPM)                                               │  ← mode_label
├─────────────────────────────────────────────────────────────────────────┤
│ ID  │ Activity │ Duration │ Predecessors │ Min Dur │ Crash │ Resource │  │  ← tree
│ ... │ ...      │ ...      │ ...          │ ...     │ ...   │ ...      │  │
├─────────────────────────────────────────────────────────────────────────┤
│ EVM Data Entry Panel                                                    │  ← bottom pane
└─────────────────────────────────────────────────────────────────────────┘
```

#### Tooltip Content (appears on hover over incomplete badges)

| Step | Tooltip Text                                                                                                      |
| ---- | ----------------------------------------------------------------------------------------------------------------- |
| 1    | "Enter your project activities in the table below, or load data from a CSV file."                                 |
| 2    | "Set the Predecessors column to define task dependencies (e.g., 'A, B'). The first activity has no predecessors." |
| 3    | "Optional: Set Resource Demand per activity to enable resource-constrained scheduling."                           |
| 4    | "Enter a Duration for each activity (CPM) or Optimistic/Most-Likely/Pessimistic estimates (PERT)."                |
| 5    | "Click ▶ Analyze to calculate the critical path, float values, and project duration."                             |

#### Phase 12 — Tasks

| #    | Task                              | Files to Create / Change                        | What to Do                                                                                                                                                                                   | Effort   | Status  |
| ---- | --------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------- |
| 12.1 | Schedule Stepper widget           | **`gui/widgets/schedule_stepper_edu.py`** (NEW) | `ScheduleStepperWidget(ttk.Frame)` — 5 badges in a row; `refresh()` reads activities data + results_data; `_detect_steps()` returns completion dict; tooltips on hover; click→tab navigation | 1 day    | ✅ Done |
| 12.2 | Embed stepper in Input Activities | `gui/tabs/input_tab_edu.py` (modify)            | Insert stepper between `button_frame` and `mode_label`. Add `self._stepper.refresh()` calls to `add_row`, `delete_row`, `clear_all_without_confirmation`, `load_file`, `_save_edit`          | 0.5 day  | ✅ Done |
| 12.3 | Post-analysis stepper refresh     | `gui/main_window_edu.py` (modify)               | After successful `analyze_project()`, call `self._input_tab_edu._stepper.refresh()` to turn Step 5 green. After `_new_project()`, call refresh to reset all badges.                          | 0.25 day | ✅ Done |
| 12.4 | Tests for detection logic         | **`tests/test_schedule_stepper_edu.py`** (NEW)  | 22 tests: empty project→all pending; 1 activity→step 1 green; predecessors set→step 2 green; optional step 3 logic; all durations set→step 4; results_data present→step 5; PG WBS override   | 0.5 day  | ✅ Done |

**Total Phase 12: 2.25 days**

#### Decisions

| #   | Decision                         | Answer                                                             | Reasoning                                                                                                                                                                                                   |
| --- | -------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Polling or event-driven refresh? | **Event-driven** — call `refresh()` from 6 existing methods        | Polling (`root.after`) wastes cycles and requires teardown logic on destroy. The 6 mutation points are already known.                                                                                       |
| 2   | UG-only or both modes?           | **Both modes** — Step 1 detection adapts for PG (accepts WBS tree) | The detection difference is one `if` statement. Hiding the stepper in PG mode means PG students miss the workflow guidance.                                                                                 |
| 3   | Step 3 required or optional?     | **Optional** — grey "optional" badge, never red                    | Resource Demand is an optional column. Making it required contradicts current behavior where analysis works without resources.                                                                              |
| 4   | Red badge for incomplete steps?  | **No** — only green (complete) and grey (pending)                  | The stepper should encourage, not shame. A student in the middle of data entry sees grey badges as "things to do", not "things done wrong."                                                                 |
| 5   | Separate guide popup (12A)?      | **Removed** — tooltip text inside badges is sufficient             | A `WorkedSolutionWindow` with static PMBOK text and no calculations is just a help page in a modal. It misuses the worked-solution infrastructure, which is designed for formula→substitution→result flows. |

---

### ✅ PHASE 13 — UG Demo Expansion + Gantt Chart Professional Restyle (Complete)

> **Goal:** (1) Expand UG demo to a realistic 15-task project with full crash data, (2) restyle `GanttTabEdu` to match the original `GanttTab` professional look while keeping edu-only enhancements.
> **Dependencies:** Phases 0–12 complete
> **Priority:** P1 (users immediately notice thin demo + different-looking Gantt)
> **Date started:** March 21, 2026

#### Problem Analysis

**UG Demo (`office_renovation_ug.pmproj`):**

| Issue                   | Current                           | Target                                              |
| ----------------------- | --------------------------------- | --------------------------------------------------- |
| Task count              | 8 activities                      | 15 activities                                       |
| Duration range          | 1–3 periods                       | 2–10 periods                                        |
| `min_duration`          | All empty (`""`)                  | Every task has `min_duration` < `duration` (50–75%) |
| `crash_cost`            | All empty (`""`)                  | Every task has `crash_cost` > `normal_cost`         |
| EVM data                | 7 periods, BAC=120k               | ~16 periods, BAC=250k (to match expanded scope)     |
| Crashing tab usefulness | Completely broken (no crash data) | Fully functional on demo load                       |

**Gantt Tab (`gantt_tab_edu.py` vs. original `gantt_tab.py`):**

| Aspect            | Original                                         | Edu (current)                                                                                        | Fix                      |
| ----------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | ------------------------ |
| Figure size       | `14×8`                                           | `8×5`                                                                                                | → `14×8`                 |
| Bar height        | `0.6`                                            | `0.4`                                                                                                | → `0.6`                  |
| Bar colours       | `red` α=0.7 / `lightblue` α=0.7                  | `#e74c3c` / `#3498db`                                                                                | → match original         |
| Bar edges         | `black`, `lw=0.8`                                | `white`, `lw=0.5`                                                                                    | → `black`, `lw=0.8`      |
| Label on bar      | **Activity ID** (bold, fs=10)                    | Duration number (fs=7)                                                                               | → Activity ID            |
| Y-axis labels     | Activity IDs (fs=12, bold)                       | Names truncated (fs=8)                                                                               | → Activity IDs           |
| Slack bars        | Dashed edge, full height                         | Solid, 60% height                                                                                    | → dashed, full height    |
| Arrows            | `#2F4F4F`, `lw=2`, α=0.7, `rad=0.1`              | `#7f8c8d`, `lw=1`, α=0.6, `rad=0.15`                                                                 | → match original         |
| Axis labels       | fs=12 bold `darkgreen`, both axes                | fs=10 X only                                                                                         | → match original         |
| Title             | fs=14, bold, pad=20                              | fs=11, bold                                                                                          | → match original         |
| Controls          | `LabelFrame("Professional Gantt Chart Options")` | Bare `ttk.Frame`                                                                                     | → `LabelFrame`           |
| X-axis limits     | `set_xlim(-0.5, max_lf+0.5)`                     | Auto                                                                                                 | → explicit limits        |
| Legend position   | `lower left`                                     | `lower right`                                                                                        | → `lower left`           |
| Data export       | CSV + Excel (from graph)                         | None                                                                                                 | → Add CSV + Excel export |
| **KEEP** edu-only | —                                                | Alternating row bg, row grid lines, tracking Gantt, EVM overlay, today line, worked-solution buttons | ✅ Keep all              |

#### Phase 13 — Tasks

| #    | Task                                             | Files to Change                          | What to Do                                                                                                                                                                                  | Effort  | Status  |
| ---- | ------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 13.1 | Expand UG demo to 15 tasks + crash data          | `demos_edu/office_renovation_ug.pmproj`  | 15 realistic renovation activities (durations 2–10), all with `min_duration` + `crash_cost`. Update EVM tasks/periods/BAC to match. Update risk register.                                   | 0.5 day | ✅ Done |
| 13.2 | Restyle Gantt Edu to match original professional | `gui/tabs/gantt_tab_edu.py`              | Figure 14×8, bar 0.6, red/lightblue α=0.7, black edges, activity ID on bar, ID y-labels, dashed slack, thick arrows, darkgreen axis labels, LabelFrame controls, x-limits                   | 1 day   | ✅ Done |
| 13.3 | Add CSV/Excel schedule data export to Gantt Edu  | `gui/tabs/gantt_tab_edu.py`              | Add "Export Data" button → CSV/Excel via graph node extraction (port logic from original `_export_csv` / `_export_excel`)                                                                   | 0.5 day | ✅ Done |
| 13.4 | Tests — demo loads, crash data present, Gantt ok | `tests/test_phase13_demo_gantt.py` (NEW) | 21 tests: 15+ activities, unique IDs, duration range, min_duration/crash_cost populated, predecessor refs valid, EVM 15 tasks + 16 periods, BAC ≥ 200k, risk register, Gantt module methods | 0.5 day | ✅ Done |

**Total Phase 13: 2.5 days**

#### Decisions

| #   | Decision                       | Answer                                                                        | Reasoning                                                                                                       |
| --- | ------------------------------ | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 1   | Keep edu-only Gantt features?  | **Yes** — tracking Gantt, EVM overlay, alternating rows, worked-solution btns | These are pedagogically valuable. The restyle only changes the visual appearance to match the professional look |
| 2   | Activity ID or name on Y-axis? | **Activity ID** (matching original)                                           | Original uses IDs; students need to cross-reference with the input table. IDs are shorter and fit better.       |
| 3   | Update PG demo too?            | **No** (out of scope)                                                         | PG demo uses PERT mode with different columns. Keep this phase focused on UG.                                   |

---

### ✅ PHASE 14 — Network Diagram Smart Layout (Strategy 5: Barycenter + Virtual Nodes) (Complete)

> **Goal:** Eliminate arrows passing through intermediate nodes by implementing a Sugiyama-style layered layout with barycenter ordering and virtual node edge routing.
> **Dependencies:** Phases 0–8 complete (NetworkTab, CPM Analyzer)
> **Priority:** P1 (usability — arrows through nodes makes the diagram hard to read)
> **Applies to:** Both UG and PG modes (original NetworkTab used by edu app)
> **Strategy:** #5 — Barycenter Y-ordering + Virtual Nodes + Polyline edges

#### Problem Analysis

The current `create_hierarchical_layout()` in `network_tab.py` uses `nx.topological_generations(G)` with alphabetical sorting within each column and fixed `y = (j - len/2 + 0.5) * 4` spacing. This produces:

1. **Arrows through nodes:** When edge (A→D) passes through the column containing B/C, the straight-line arrow goes right through those nodes
2. **No crossing minimization:** Alphabetical sort within columns ignores graph connectivity, creating unnecessary edge crossings
3. **No long-edge routing:** Edges spanning multiple columns are drawn as single straight lines through all intermediate columns

#### Solution: Sugiyama-style Layered Layout (Strategy 5)

**Phase 1 — Barycenter Y-ordering:** Instead of alphabetical sort within each topological column, order nodes by the average Y position of their predecessors (barycenter heuristic). This minimizes edge crossings.

**Phase 2 — Virtual node insertion:** For any edge (u→v) that spans more than one column, insert virtual (invisible) nodes at each intermediate column. This creates a path: u → virt₁ → virt₂ → ... → v.

**Phase 3 — Polyline edge routing:** Draw edges as polylines through virtual node positions. Virtual nodes are positioned by the same barycenter ordering, so the edge bends to avoid real nodes.

**Phase 4 — Iterative refinement:** Run 2–4 passes of barycenter ordering (alternating forward/backward) to further reduce crossings.

#### Phase 14 — Tasks

| #    | Task                                    | Files to Change                              | What to Do                                                                                                                                                                                                                        | Effort   | Status  |
| ---- | --------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------- |
| 14.1 | Implement Sugiyama layout engine        | `gui/tabs/network_tab.py`                    | Replace `create_hierarchical_layout()` with: (a) topological generation layering, (b) virtual node insertion for long edges, (c) barycenter Y-ordering with 4 iterative passes, (d) final coordinate assignment with even spacing | 1 day    | ✅ Done |
| 14.2 | Implement polyline edge routing         | `gui/tabs/network_tab.py`                    | Replace `draw_network_edges()` with polyline routing through virtual node waypoints. Straight segments between consecutive waypoints, arrowhead only on final segment. Critical path edges in red, lw=2                           | 0.5 day  | ✅ Done |
| 14.3 | Adjust node spacing and margins         | `gui/tabs/network_tab.py`                    | Tune `x_spacing` and `y_spacing` to prevent node overlap in the new layout. Add padding for float labels when "Show Float" is enabled. Ensure START/END nodes positioned correctly                                                | 0.25 day | ✅ Done |
| 14.4 | Tests — layout correctness + no overlap | `tests/test_phase14_network_layout.py` (NEW) | Test: no two real nodes overlap, all edges avoid node interiors, barycenter reduces crossings vs alphabetical, virtual nodes created for long edges, polyline waypoints correct, START/END positioned at extremes                 | 0.5 day  | ✅ Done |

**Total Phase 14: 2.25 days**

#### Technical Design

**Barycenter heuristic:**

```python
def barycenter_y(node, G, pos, direction='forward'):
    """Compute barycenter = avg Y of connected nodes in previous layer."""
    if direction == 'forward':
        neighbors = list(G.predecessors(node))
    else:
        neighbors = list(G.successors(node))
    if not neighbors:
        return pos.get(node, (0, 0))[1]  # Keep current Y
    return sum(pos[n][1] for n in neighbors if n in pos) / len([n for n in neighbors if n in pos])
```

**Virtual node insertion:**

```python
# For edge (u, v) spanning columns col_u → col_v where col_v - col_u > 1:
# Insert virtual nodes virt_u_v_1, virt_u_v_2, ... at each intermediate column
# Replace edge (u, v) with path: u → virt_1 → virt_2 → ... → v
# Virtual nodes participate in barycenter ordering but are not rendered
```

**Polyline edge drawing:**

```python
# For each original edge (u, v):
#   Collect waypoints: [pos[u], pos[virt_1], pos[virt_2], ..., pos[v]]
#   Draw line segments between consecutive waypoints
#   Arrowhead only on the last segment (virt_n → v)
```

**Iterative refinement (4 passes):**

1. Forward pass (left→right): order each column by barycenter of predecessors
2. Backward pass (right→left): order each column by barycenter of successors
3. Forward pass (refinement)
4. Backward pass (refinement)

#### Decisions

| #   | Decision                            | Answer                                                                                        | Reasoning                                                                                                                             |
| --- | ----------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Modify original NetworkTab or copy? | **Modify original** — the edu app already uses `NetworkTab` directly                          | Creating a copy would duplicate 600+ lines. The layout improvement benefits both modes.                                               |
| 2   | How many barycenter iterations?     | **4 passes** (2 forward + 2 backward)                                                         | Empirically 2–4 passes gives most of the crossing reduction benefit. More passes have diminishing returns.                            |
| 3   | Virtual node rendering?             | **Invisible** — virtual nodes are layout-only; only the polyline segments through them render | Virtual nodes are an implementation detail of the routing algorithm. Users should see clean curved/bent edges, not intermediate dots. |
| 4   | Critical path edge styling?         | **Red, lw=2** for critical edges; **black, lw=1.5** for normal                                | Matches the existing node coloring convention (red = critical). Thicker lines make the critical path visually prominent in the path.  |

---

### ✅ PHASE 14A — Shared Sugiyama Layout Engine for All Network-Based Tabs (Complete)

> **Goal:** Extract the Phase 14 Sugiyama layout into a shared module and apply it to PERT diagram and both Crashing visualization modules, so every network-based diagram benefits from crossing minimisation and arrow-avoids-node routing.
> **Dependencies:** Phase 14 complete
> **Priority:** P1 (consistency — all network diagrams should look equally good)
> **Applies to:** Both UG and PG modes

#### What Changed

1. **Shared layout engine** — `src/pmhelper/utils/network_layout.py` (NEW): extracted `sugiyama_layout()`, `cleanup_virtual_nodes()`, and `draw_edges_polyline()` from `network_tab.py` so every consumer uses a single implementation.
2. **`network_tab.py`** — refactored to delegate to the shared engine (no behaviour change).
3. **`pert_diagram_tab.py`** — Sugiyama layout + polyline edges; PERT-specific rectangle-semicircle node shapes preserved with custom `_edge_start` / `_edge_end` helpers; virtual nodes skipped in node & float-label drawing.
4. **`gui/tabs/crashing_visualization.py`** — both `draw_network_diagram_on_ax` and `draw_network_diagram_on_ax_small` use shared engine.
5. **`core/crashing_visualization.py`** — same upgrade; `initial=True` deep-copy safety preserved.

#### Phase 14A — Tasks

| #     | Task                                    | Files Changed                                    | Status  |
| ----- | --------------------------------------- | ------------------------------------------------ | ------- |
| 14A.1 | Extract shared Sugiyama layout module   | `utils/network_layout.py` (NEW)                  | ✅ Done |
| 14A.2 | Refactor NetworkTab to use shared module| `gui/tabs/network_tab.py`                        | ✅ Done |
| 14A.3 | Upgrade PERT diagram tab                | `gui/tabs/pert_diagram_tab.py`                   | ✅ Done |
| 14A.4 | Upgrade Crashing viz (gui/tabs)         | `gui/tabs/crashing_visualization.py`             | ✅ Done |
| 14A.5 | Upgrade Crashing viz (core)             | `core/crashing_visualization.py`                 | ✅ Done |
| 14A.6 | Tests — shared engine + integration     | `tests/test_phase14a_shared_layout_engine.py`    | ✅ Done |

**Tests:** 24 new (10 unit for shared engine, 3 cleanup, 3 draw-edges smoke, 2 PERT integration, 2 gui-crashing integration, 3 core-crashing integration, 1 network-tab delegation). **Total: 797 passing.**

---

## Definition of Done (V1 Release)

- [ ] All ~50 V1 features listed in `FEATURES_LIST_EDU.md` are reachable and functional in the running app
- [ ] `DECISIONS.md` has answers to all 7 decisions from the Key Decisions Log
- [ ] `pytest` passes with 0 failures across all test files (341+ tests)
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
- [ ] Phase 8 Acceptance Checklist (22 items) — all checked
- [ ] All PG-only tabs (Probability, Resources, RCPS Crashing, Charter, Charter Mgr, DPCI) hidden in UG mode
- [ ] `_PG_ONLY_TABS` and `_pg_only_widgets` updated for all new tabs
- [ ] `_all_tabs_ordered` matches notebook tab indices exactly (15 tabs total)
