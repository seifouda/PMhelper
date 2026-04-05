# PMhelper Edu — V1 Implementation Plan

> **Scope:** All ~50 V1 features from `FEATURES_LIST_EDU.md`
> **Approach:** 1 developer + AI agent assistance
> **Estimated Calendar Time:** ~21 weeks (parallelism in Phases 2+3 recovers ~2 weeks; ~1 week buffer in Phase 4; Phase 8 adds ~2 weeks)
> **Date:** March 8, 2026
> **Last Status Update:** April 5, 2026
> **V1 Status:** ✅ CODE-COMPLETE — all development work finished. Remaining items are manual QA (deferred to V2).

---

## Current Implementation Status (as of March 9, 2026)

### ✅ COMPLETED (Phases 0–7)

| Phase     | Description                                                                                                                                                                        | Status     |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Phase 0   | Scaffolding — `EduProjectState`, `AppConfig`, entry point (`edu_main.py`), test stubs                                                                                              | ✅ Done    |
| Phase 1   | EVM Data Model + Input Layer — `EVMTask`, `EVMPeriod`, `EVMProject`, `InputTabEdu`, `evm_io_edu.py`, PV spreading                                                                  | ✅ Done    |
| Phase 2   | EVM Calculation Engine — `evm_calculations_edu.py`, `EVMTabEdu` (KPI cards, RAG, step-by-step, S-Curve), `test_evm_calculations_edu.py`                                            | ✅ Done    |
| Phase 3   | Risk Register & Heat Map — `risk_register_edu.py`, `RiskTabEdu` (register CRUD, 5×5 heat map, contingency integration), `risk_io_edu.py`                                           | ✅ Done    |
| Phase 4   | Monte Carlo Engine — `monte_carlo_edu.py` (threaded, progress bar), `ProbabilityTabEdu` (Monte Carlo + PERT Analysis sub-tabs), Tracking Gantt (baseline bars, % complete shading) | ✅ Done    |
| Phase 5   | Mode Toggle (UG/PG), Chart Export, Demo Data (.pmproj), Dashboard Tab, Save/Load, Unsaved-Changes Warning, PyInstaller spec                                                        | ✅ Done    |
| Phase 6   | Testing & Stabilisation — all test files pass (381 tests)                                                                                                                          | ✅ Done    |
| Phase 7   | CPM/PERT Integration — Analyze button, real Results/Network/PERT/Crashing tabs reused, CPM→EVM sync, `.pmproj` CPM activity persistence                                            | ✅ Done    |
| Phase 8   | Production Hardening — Gantt arrows + today line, RCPS leveling sub-tab, PERT analysis sub-tab, Charter + Charter Mgr wiring, DPCI wiring, full tab refresh                        | ✅ Done    |
| Phase 9   | SWOT & PESTEL Strategic Analysis — `SWOTTabEdu`, `PESTELTabEdu`, auto-extraction engine, models, save/load in `.pmproj`                                                            | ✅ Done    |
| Phase 9C  | WBS Diagram — data model, validator, builder, aggregator, Walker's layout engine, interactive Canvas tab, file export                                                              | ✅ Done    |
| Phase 10  | Polish & Packaging — recent files list, Excel KPI export, PyInstaller `--onedir` spec                                                                                              | ✅ Partial |
| Phase 11  | UG Worked Solutions — `step_generators_edu.py`, `WorkedSolutionWindow` widget, "Show Worked Solution" buttons on EVM/PERT/CPM tabs (UG-only)                                       | ✅ Done    |
| Phase 12  | Schedule Process Stepper — `ScheduleStepperWidget` (5 PMBOK steps, event-driven), embedded in Input Activities tab, both UG + PG modes                                             | ✅ Done    |
| Phase 13  | UG Demo Expansion + Gantt Restyle — 15-task renovation demo with crash data, professional Gantt styling (14×8, bar 0.6h, CSV/Excel export)                                         | ✅ Done    |
| Phase 14  | Network Diagram Smart Layout — Sugiyama layered layout, barycenter Y-ordering, virtual node insertion, polyline edge routing                                                       | ✅ Done    |
| Phase 14A | Shared Sugiyama Layout Engine — `utils/network_layout.py` extracted, applied to NetworkTab + PERT diagram + both Crashing visualization modules                                    | ✅ Done    |
| Phase 15  | Large Project Support — O(V+E) critical-path fix, `ScrollableMatplotlibFrame` widget, batch polyline rendering, adaptive layout sizing for 600-task demos                          | ✅ Done    |
| Phase 16  | Large Demo Predecessor Quality — 19 DAG constraints implemented via `_build_predecessors_map()`, both 600-task demos regenerated and validated                                     | ✅ Done    |
| Phase 17  | Interactive Network Viewer — `pyvis` (vis.js) HTML generation for NetworkTab + PERT tab, browser-based exploration with hover tooltips, zoom/pan, critical path highlighting       | ✅ Done    |

### ✅ COMPLETED — Phase 17: Interactive Network Viewer

> **Goal:** Add an alternative interactive browser-based network visualization using vis.js (via `pyvis`), coexisting alongside the current Matplotlib in-app diagrams.
> **Effort:** ~1 working day
> **Date started:** March 22, 2026
> **Date completed:** March 22, 2026
> **Dependencies:** Phase 14A (shared Sugiyama engine), Phase 15 (large project support)

### ✅ COMPLETED — Phase 8: Production Hardening (P1 + P2 fixes)

> **Goal:** Fix all remaining gaps that prevent the app from being production-ready.
> **Effort:** ~5 working days
> **Date started:** March 9, 2026
> **Date completed:** March 21, 2026

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
| 10.3 | PyInstaller `--onedir` build actually run and tested              | 1 day    | Low      | ➡️ Deferred to V2 (manual QA)       |
| 10.4 | UI smoke test — all 30 checklist items manually verified          | 1 day    | Low      | ➡️ Deferred to V2 (manual QA)       |
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
│   ├── edu_state.py             ✅ Done ← Phase 0  (EduProjectState + AppConfig)
│   ├── evm_models.py            ✅ Done ← Phase 1  (EVMTask, EVMPeriod, EVMProject)
│   ├── evm_calculations.py      ✅ Done ← Phase 2  (pure KPI functions + RAG)
│   ├── risk_register.py         ✅ Done ← Phase 3  (risk_register_edu.py)
│   ├── monte_carlo.py           ✅ Done ← Phase 4  (monte_carlo_edu.py)
│   ├── swot_models_edu.py       ✅ Done ← Phase 9A (SWOTFactor, SWOTAnalysis)
│   ├── pestel_models_edu.py     ✅ Done ← Phase 9B (PESTELFactor, PESTELAnalysis)
│   ├── wbs_models_edu.py        ✅ Done ← Phase 9C (WBSNode, WBSStatus)
│   ├── wbs_validator_edu.py     ✅ Done ← Phase 9C (validation + DFS cycle detection)
│   ├── wbs_builder_edu.py       ✅ Done ← Phase 9C (tree build + BFS levels + WBS codes)
│   ├── wbs_aggregator_edu.py    ✅ Done ← Phase 9C (rollup with caching)
│   ├── wbs_layout_edu.py        ✅ Done ← Phase 9C (Walker's layout + LayoutNode/LayoutEdge)
│   └── step_generators_edu.py   ✅ Done ← Phase 11 (Step dataclass; pert_steps, evm_steps, cpm_steps)
├── gui/
│   ├── main_window.py           ✅ Done (main_window_edu.py — all tabs wired through Phase 16)
│   ├── widgets/
│   │   ├── worked_solution_window.py  ✅ Done ← Phase 11 (scrollable Toplevel, Step cards, export)
│   │   ├── schedule_stepper_edu.py    ✅ Done ← Phase 12 (5-badge PMBOK stepper, event-driven)
│   │   └── scrollable_mpl_frame.py   ✅ Done ← Phase 15 (viewport + scrollbars + toolbar)
│   └── tabs/
│       ├── input_tab_edu.py       ✅ Done (EVM panel + period table + PV spreading + stepper)
│       ├── gantt_tab_edu.py       ✅ Done (professional restyle, scrollable, tracking, EVM overlay)
│       ├── network_tab_edu.py     ✅ Done (Sugiyama layout, scrollable, adaptive sizing)
│       ├── evm_tab_edu.py         ✅ Done ← Phase 2  (KPI cards, RAG, step-by-step, S-curve)
│       ├── risk_tab_edu.py        ✅ Done (register CRUD + 5×5 heat map)
│       ├── pert_tab_edu.py        ✅ Done (Sugiyama layout, scrollable)
│       ├── probability_tab_edu.py ✅ Done (PERT Analysis + Monte Carlo sub-tabs)
│       ├── crashing_tab_edu.py    ✅ Done (reused)
│       ├── rcps_tab_edu.py        ✅ Done (RCPS Schedule + Histograms sub-tabs)
│       ├── rcps_crashing_tab.py   ✅ Done (PG-only)
│       ├── dashboard_tab_edu.py   ✅ Done ← Phase 5  (project health overview)
│       ├── charter_tab.py         ✅ Done (PG-only)
│       ├── charter_manager.py     ✅ Done (PG-only)
│       ├── dpci_tab.py            ✅ Done (PG-only)
│       ├── swot_tab_edu.py        ✅ Done ← Phase 9A (2×2 SWOT matrix UI)
│       ├── pestel_tab_edu.py      ✅ Done ← Phase 9B (6-cell PESTEL heatmap UI)
│       └── wbs_tab_edu.py         ✅ Done ← Phase 9C (interactive WBS Canvas viewer + editor)
└── utils/
    ├── evm_io_edu.py            ✅ Done ← Phase 1
    ├── risk_io_edu.py           ✅ Done ← Phase 3
    ├── swot_extractor_edu.py    ✅ Done ← Phase 9A (auto-extraction from Charter/Risk/EVM)
    ├── wbs_io_edu.py            ✅ Done ← Phase 9C (CSV/JSON import, hierarchical input)
    ├── wbs_export_edu.py        ✅ Done ← Phase 9C (Excel/PDF/JSON/CSV export + renderer)
    ├── project_io_edu.py        ✅ Done ← Phase 5  (SWOT + PESTEL + WBS + CPM keys)
    ├── chart_export_edu.py      ✅ Done ← Phase 5  (SWOT/PESTEL export functions)
    ├── network_layout.py        ✅ Done ← Phase 14A (shared Sugiyama engine)
    └── interactive_network.py   ✅ Done ← Phase 17 (vis.js HTML generator via pyvis)

scripts/
    └── generate_large_demos.py  ✅ Done ← Phase 16 (_build_predecessors_map, 6-step algorithm)
```

**Tab structure inside `MainWindow` after Phases 0–9:**

```
Tab Name               Status                      Notes
──────────────────────────────────────────────────────────────────
Input Activities     ✅ Done                       stepper widget added (Phase 12)
Results              ✅ Done                       no change
Network Diagram      ✅ Done                       Sugiyama layout + scrollable (Phase 14/15)
PERT Diagram         ✅ Done                       Sugiyama layout + scrollable (Phase 14A/15)
Gantt Chart          ✅ Done                       professional restyle + scrollable (Phase 13/15)
EVM Dashboard        ✅ Done                       no change
Risk Analysis        ✅ Done                       no change
Probability          ✅ Done                       PERT Analysis + Monte Carlo sub-tabs
Crashing             ✅ Done                       no change
Resources (RCPS)     ✅ Done                       RCPS Schedule sub-tab added (Phase 8)
RCPS Crashing        ✅ Done (PG-only)             no change
Dashboard            ✅ Done                       no change
Project Charter      ✅ Done (PG-only)             no change
Charter Manager      ✅ Done (PG-only)             no change
DPCI Assessment      ✅ Done (PG-only)             no change
SWOT Analysis        ✅ Done (PG-only)             complete (Phase 9A)
PESTEL Analysis      ✅ Done (PG-only)             complete (Phase 9B)
WBS Diagram          ✅ Done (PG-only)             complete (Phase 9C)
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

4. **Tab overflow on small screens**: With 18 tabs, test on 1366×768 resolution. If tab headers overflow, shorten labels: "Resources" → "RCPS", "Charter Manager" → "Charter Mgr", "RCPS Crashing" → "RCPS Crash".

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
- [ ] `pytest` passes with 0 regressions (797+ tests) after all Phase 8 items

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

| #     | Task                                     | Files Changed                                 | Status  |
| ----- | ---------------------------------------- | --------------------------------------------- | ------- |
| 14A.1 | Extract shared Sugiyama layout module    | `utils/network_layout.py` (NEW)               | ✅ Done |
| 14A.2 | Refactor NetworkTab to use shared module | `gui/tabs/network_tab.py`                     | ✅ Done |
| 14A.3 | Upgrade PERT diagram tab                 | `gui/tabs/pert_diagram_tab.py`                | ✅ Done |
| 14A.4 | Upgrade Crashing viz (gui/tabs)          | `gui/tabs/crashing_visualization.py`          | ✅ Done |
| 14A.5 | Upgrade Crashing viz (core)              | `core/crashing_visualization.py`              | ✅ Done |
| 14A.6 | Tests — shared engine + integration      | `tests/test_phase14a_shared_layout_engine.py` | ✅ Done |

**Tests:** 24 new (10 unit for shared engine, 3 cleanup, 3 draw-edges smoke, 2 PERT integration, 2 gui-crashing integration, 3 core-crashing integration, 1 network-tab delegation). **Total: 797 passing.**

---

### PHASE 15 — Large Project Support (Scrollable Diagrams + Analysis Fix)

> **Goal:** Make 600-task large demo projects fully functional — fix the exponential-time critical-path algorithm, add scrollable network/PERT/Gantt diagrams with adaptive sizing, optimise polyline rendering for thousands of edges, and add runtime timing to the terminal.
> **Dependencies:** Phases 14, 14A complete
> **Priority:** P0 (app crashes on large demo load — blocks feature)
> **Date started:** March 22, 2026

#### Problem Analysis

Loading the 600-task UG Large demo crashes the application. Root causes identified via measurement:

| #   | Problem                        | Root Cause                                                                                                                                                                                | Impact                                  |
| --- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| 1   | **Analysis never completes**   | `identify_critical_path()` calls `nx.all_simple_paths()` — **O(2^n)** on large DAGs. 600 nodes → hangs indefinitely.                                                                      | **P0 crash** — app freezes, OS kills it |
| 2   | **Sugiyama blows up**          | 600 nodes → **220 topological layers**, max 6/layer, **643 long edges** → **8,361 virtual nodes** inserted. At `x_spacing=3.5`, the x-axis spans 770 units crammed into a 12-inch figure. | Diagram unreadable, rendering slow      |
| 3   | **Edge drawing is O(n) calls** | `draw_edges_polyline()` makes one `ax.plot()` per segment → ~8,400 individual matplotlib artist objects.                                                                                  | 10–30 s render time for large graph     |
| 4   | **Gantt is unscrollable**      | 600 bars in a fixed 14×8 figure with no scrollbar or toolbar → bars are 1 px tall                                                                                                         | Gantt unusable for >50 activities       |
| 5   | **No timing visibility**       | `analyze_project()` has no timing output — user sees a frozen window with no feedback                                                                                                     | UX: user thinks app crashed             |

Measured graph statistics for `campus_construction_ug_large.pmproj`:

```
Activities:       600
Topological layers: 220
Max nodes/layer:    6
Long edges (span>1): 643
Virtual nodes:      8,361
Total graph objects: 8,963
```

#### Criticism of Approach (Scrollable Canvas + Toolbar)

| Concern                                                                         | Assessment                                                                                | Mitigation                                                                                                                                                         |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Memory** — large matplotlib figure (e.g. 80×10 inches @ 100 dpi = 3.2 MB)     | Acceptable. RGBA buffer ~32 MB max.                                                       | Cap figure at 120×60 inches; reduce DPI for very large graphs if needed.                                                                                           |
| **Tk.Canvas 32K pixel limit** — some platforms clip widgets >32,767 px          | 120 in × 100 dpi = 12,000 px, within limits.                                              | Cap enforced in code.                                                                                                                                              |
| **Label readability at full zoom-out** — 600 labels in one view                 | Inherent — no layout can make 600 labels readable simultaneously.                         | Adaptive font size + toolbar zoom lets user inspect regions. Plus the toolbar "zoom to rectangle" is ideal for students.                                           |
| **Scrollbar + toolbar confusion** — two navigation mechanisms                   | Scrollbars for coarse movement, toolbar for precise zoom. Complementary, not conflicting. | Scrollbar only appears when figure exceeds viewport (small projects unaffected).                                                                                   |
| **`on_canvas_resize` conflict** — existing handler shrinks figure back to frame | Must be disabled for large projects.                                                      | `ScrollableMatplotlibFrame` widget replaces this with `_auto_fit` flag: True for small projects (resize-to-fill), False for large (fixed size, scrollbars active). |
| **`all_simple_paths` is O(2^n)** — not a rendering issue                        | Must be fixed independently. `dag_longest_path` is O(V+E).                                | Replace in `network_builder.py`.                                                                                                                                   |

#### Solution Design

**Fix 1 — `identify_critical_path` (P0):**
Replace `all_simple_paths(critical_subgraph, start, end)` with `nx.dag_longest_path(critical_subgraph)`. The critical subgraph (zero-float activities only) is a DAG — `dag_longest_path` runs in O(V+E), returning the single longest path directly.

**Fix 2 — `ScrollableMatplotlibFrame` widget:**
New reusable widget `gui/widgets/scrollable_mpl_frame.py` embedding `FigureCanvasTkAgg` inside a `tk.Canvas` viewport with scrollbars. Two modes:

- `_auto_fit = True` (small projects): figure resizes to fill viewport, scrollbars inactive.
- `_auto_fit = False` (large projects): fixed figure size, scrollbars appear when figure exceeds viewport.
  Includes `NavigationToolbar2Tk` at the bottom. Mouse wheel support for vertical/horizontal scroll.

**Fix 3 — Batch polyline rendering:**
Replace per-segment `ax.plot()` calls in `draw_edges_polyline()` with 2 batch `ax.plot()` calls (one for normal edges, one for critical). Insert `None` as line-break markers between edges. Arrowheads remain as individual `ax.annotate()` calls on each edge's final segment. Reduces ~8,400 artist objects to ~650.

**Fix 4 — Adaptive layout + sizing:**

| Parameter      | ≤50 nodes                     | 51–200 nodes              | >200 nodes              |
| -------------- | ----------------------------- | ------------------------- | ----------------------- |
| `x_spacing`    | 3.5 (network) / 5.0 (PERT)    | 2.0 / 3.0                 | 1.0 / 1.5               |
| `y_spacing`    | 4.0                           | 2.5                       | 1.5                     |
| Node radius    | 0.6 (network) / custom (PERT) | 0.4 / scaled              | 0.25 / scaled           |
| Label fontsize | 10                            | 7                         | 5                       |
| Figure size    | Fit-to-frame                  | Computed from layout bbox | Computed, capped 120×60 |

Gantt adaptive height: `fig_h = min(80, max(8, n_activities × 0.25 + 2))` inches.

**Fix 5 — Timing:**
Print `time.time()` timestamps at each major step of `analyze_project()` to terminal.

#### Phase 15 — Tasks

| #    | Task                                           | Files to Create / Change                        | What to Do                                                                                                          | Status  |
| ---- | ---------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------- |
| 15.1 | Fix exponential `identify_critical_path`       | `core/network_builder.py`                       | Replace `all_simple_paths` loop with `nx.dag_longest_path(critical_subgraph)` — O(V+E).                             | ✅ Done |
| 15.2 | Create `ScrollableMatplotlibFrame` widget      | **`gui/widgets/scrollable_mpl_frame.py`** (NEW) | Reusable scrollable matplotlib container with viewport, scrollbars, `NavigationToolbar2Tk`, auto-fit/fixed modes.   | ✅ Done |
| 15.3 | Optimise `draw_edges_polyline` batch rendering | `utils/network_layout.py`                       | Batch intermediate segments into 2 `ax.plot()` calls (normal + critical); keep individual `ax.annotate` arrowheads. | ✅ Done |
| 15.4 | Scrollable + adaptive `NetworkTab`             | `gui/tabs/network_tab.py`                       | Use `ScrollableMatplotlibFrame`; adaptive x/y spacing, node radius, font size, figure size based on activity count. | ✅ Done |
| 15.5 | Scrollable + adaptive `PertDiagramTab`         | `gui/tabs/pert_diagram_tab.py`                  | Same pattern as 15.4 with PERT-specific spacing (x=5.0 baseline) and node shapes.                                   | ✅ Done |
| 15.6 | Scrollable + adaptive `GanttTabEdu`            | `gui/tabs/gantt_tab_edu.py`                     | Use `ScrollableMatplotlibFrame`; dynamic figure height; adaptive bar label size.                                    | ✅ Done |
| 15.7 | Runtime timing in `analyze_project()`          | `gui/main_window_edu.py`                        | Print elapsed-time checkpoints to terminal at each analysis and tab-update step.                                    | ✅ Done |

#### Decisions

| #   | Decision                               | Answer                                                          | Reasoning                                                                                                                   |
| --- | -------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 1   | Scrollable container vs. toolbar only? | **Both** — scrollable canvas (Option A) + toolbar (Option B)    | Scrollbars for coarse navigation, toolbar zoom for precise inspection. Scrollbars only appear when figure exceeds viewport. |
| 2   | Shared widget or inline per tab?       | **Shared `ScrollableMatplotlibFrame`**                          | 3 tabs need identical scroll logic — a shared widget avoids 45 lines of duplication and ensures consistent behavior.        |
| 3   | Figure size cap?                       | **120 × 60 inches** (12,000 × 6,000 px at 100 dpi)              | Stays within Tk.Canvas 32K pixel limit with margin. ~288 MB max RGBA buffer — within typical desktop memory.                |
| 4   | `all_simple_paths` → what replacement? | **`nx.dag_longest_path()`**                                     | O(V+E) for DAGs. The critical subgraph is always a DAG (subset of original DAG). Returns single longest path directly.      |
| 5   | Batch rendering approach?              | **2 batch `ax.plot()` + individual `ax.annotate()` arrowheads** | Reduces ~8,400 artist objects to ~650. `None` values in arrays create line breaks for separate edge polylines.              |

---

### ✅ PHASE 16 — Large Demo Predecessor Network Quality (Complete)

> **Goal:** Ensure both 600-task demo files satisfy all 19 DAG quality constraints, producing structurally sound networks with meaningful critical paths and efficient Sugiyama rendering.
> **Dependencies:** Phase 15 (large project support, `ScrollableMatplotlibFrame`, adaptive rendering)
> **Priority:** P1 — invalid predecessor networks caused thousands of redundant virtual nodes in the Sugiyama layout and produced misleading critical path results in both demos
> **Commit:** `0fa9efd` — March 22, 2026

#### Problem Analysis

The original `scripts/generate_large_demos.py` produced predecessor networks that violated five key constraints:

| Violation                                                                                                           | Constraint # | Impact                                                             |
| ------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------ |
| Transitive redundancy (A→B, B→C, A→C all present)                                                                   | #12          | Thousands of extra virtual nodes; inflated Sugiyama rendering time |
| Up to 7 predecessors per task                                                                                       | #10          | Unrealistic convergence; distorted critical path weights           |
| Fan-out explosion at phase boundaries (all 5 early tasks independently link back to final 2–8 tasks of prior phase) | #13, #15     | Layout explosion at every phase transition                         |
| No chain guarantee — critical path potentially 2–3 tasks only                                                       | #18, #19     | Meaningless CPM/PERT results for a 600-task project                |
| 5% per-task random cross-phase rule fired multiple times per task                                                   | #17          | Uncontrolled connectivity; violated phase structure                |

#### The 19 DAG Quality Constraints

These constraints define what a structurally valid, pedagogically useful project network must satisfy.

**Category 1 — Graph Structure**

| #   | Constraint                                                                                            | Verification                                |
| --- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| 1   | **Valid DAG** — no directed cycles anywhere in the network                                            | `nx.is_directed_acyclic_graph(G) == True`   |
| 2   | **No self-loops** — a task cannot list itself as a predecessor                                        | All edges `(u, v)` have `u ≠ v`             |
| 3   | **No dangling references** — every predecessor ID must exist as a valid task in the project           | Set membership check against all task IDs   |
| 4   | **Full reachability** — all tasks reachable from at least one start task via forward traversal        | `nx.is_weakly_connected(G) == True`         |
| 5   | **Forward connectivity** — all tasks lie on at least one path to an end task (no dead-end sub-graphs) | BFS from all end tasks in reverse direction |

**Category 2 — Start / End Structure**

| #   | Constraint                                                                                    | Verification               |
| --- | --------------------------------------------------------------------------------------------- | -------------------------- |
| 6   | **Minimum start tasks** — at least 1 task with `in_degree = 0`                                | `start_count >= 1`         |
| 7   | **Maximum start tasks** — no more than 5 start tasks (prevents fully flat networks)           | `start_count <= 5`         |
| 8   | **No isolated tasks** — no task with both `in_degree = 0` AND `out_degree = 0` simultaneously | `isolated_node_count == 0` |

**Category 3 — Predecessor Count**

| #   | Constraint                                                                                          | Verification                          |
| --- | --------------------------------------------------------------------------------------------------- | ------------------------------------- |
| 9   | **Minimum predecessors** — every non-start task has at least 1 predecessor (no mid-network orphans) | All non-start `in_degree >= 1`        |
| 10  | **Maximum predecessors** — hard cap of 3 predecessors per task                                      | `max(G.in_degree(n) for n in G) <= 3` |
| 11  | **Typical predecessors** — median in-degree = 1 (most tasks have simple, single dependencies)       | `median(in_degrees) == 1`             |

**Category 4 — Transitive Redundancy**

| #   | Constraint                                                                                                    | Verification                                   |
| --- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 12  | **No transitive redundancy** — if a path A→…→C exists via intermediate nodes, no direct A→C edge is permitted | Ancestor-set traversal: `redundant_edges == 0` |

**Category 5 — Fan-out and Convergence**

| #   | Constraint                                                                                | Verification                           |
| --- | ----------------------------------------------------------------------------------------- | -------------------------------------- |
| 13  | **Fan-out cap** — no single task directly precedes more than 8 successors                 | `max(G.out_degree(n) for n in G) <= 8` |
| 14  | **Convergence cap** — same as constraint #10; no task has more than 3 direct predecessors | `max(G.in_degree(n) for n in G) <= 3`  |

**Category 6 — Phase Topology**

| #   | Constraint                                                                                                                                     | Verification                                     |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| 15  | **Phase boundary single gateway** — exactly ONE task per phase boundary serves as the connection gateway from the previous phase               | Gateway count per transition = 1                 |
| 16  | **Within-phase locality** — intra-phase connections are limited to a sliding window of the preceding 8 tasks; no long-range within-phase jumps | No within-phase edge skips more than 8 positions |
| 17  | **No random cross-phase edges** — cross-phase connections only via the designated gateway mechanism; no opportunistic 5%-rule jumps            | Cross-phase edges from non-gateway tasks = 0     |

**Category 7 — Critical Chain**

| #   | Constraint                                                                                                                                     | Verification                               |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| 18  | **Minimum critical path** — the longest path must span at least 30% of all tasks                                                               | `len(critical_path) / total_tasks >= 0.30` |
| 19  | **Spine requirement** — a sequential chain of every 3rd task (≥ N/3 tasks) forms the backbone, guaranteeing a well-defined project progression | Critical spine coverage ≥ 33% of total     |

#### Implementation — 6-Step Algorithm

The generator uses a shared `_build_predecessors_map()` function (both UG and PG 600-task demos call it):

```
Step 1 — Critical spine      Every 3rd task in project order forms a sequential
                              chain: T₀→T₃→T₆→…→T_{N-3}.
                              Satisfies constraints #18 and #19.
                              Result: critical path ≈ 33–55% of all tasks.

Step 2 — Phase gateways      For each phase boundary, designate exactly ONE
                              gateway task in the new phase that links back to a
                              single task in the previous phase.
                              Satisfies constraints #13, #15.

Step 3 — Within-phase local  For each non-spine, non-gateway task, sample 1–3
                              predecessors from the preceding 8 tasks within the
                              same phase (sliding window).
                              Satisfies constraints #11, #16.

Step 4 — Isolation fallback  Any task still with no predecessors (non-start) is
                              assigned an immediate predecessor.
                              Satisfies constraints #8, #9.

Step 5 — Transitive reduce   Remove any edge A→C where A is already an ancestor
                              of C via another path. O(V+E) via ancestor-set pass.
                              Satisfies constraint #12.

Step 6 — Hard predecessor cap Enforce max 3 predecessors on all tasks, removing
                              the weakest links when over the limit.
                              Satisfies constraint #10.
```

Three helper functions added to `scripts/generate_large_demos.py`:

- `_build_ancestor_sets(pred_map, all_ids)` — O(V+E) ancestor computation in topological order
- `_transitive_reduce(pred_map, all_ids)` — removes A→C edges where A is already an ancestor
- `_build_predecessors_map(phase_codes, phase_task_ids, rng)` — orchestrates all 6 steps

#### Validation Results (March 22, 2026)

Both regenerated demo files passed all constraint checks:

| Metric                     | UG Large (campus_construction) | PG Large (erp_implementation) | Constraint |
| -------------------------- | ------------------------------ | ----------------------------- | ---------- |
| Valid DAG                  | ✅ True                        | ✅ True                       | #1         |
| Start tasks                | ✅ 3                           | ✅ 3                          | #6, #7     |
| Isolated nodes             | ✅ 0                           | ✅ 0                          | #8         |
| Max predecessors           | ✅ 3                           | ✅ 3                          | #10        |
| Transitive-redundant edges | ✅ 0                           | ✅ 0                          | #12        |
| Topological layers         | ✅ 335                         | ✅ 331                        | #4, #18    |
| Critical path length       | ✅ 335 tasks (55%)             | ✅ 331 tasks (55%)            | #18, #19   |
| All 797 tests pass         | ✅                             | ✅                            | —          |

#### Phase 16 — Tasks

| #    | Task                                                   | Files Changed                                                                                   | Status  |
| ---- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------- |
| 16.1 | Implement `_build_ancestor_sets()` helper              | `scripts/generate_large_demos.py`                                                               | ✅ Done |
| 16.2 | Implement `_transitive_reduce()` helper                | `scripts/generate_large_demos.py`                                                               | ✅ Done |
| 16.3 | Implement `_build_predecessors_map()` 6-step algorithm | `scripts/generate_large_demos.py`                                                               | ✅ Done |
| 16.4 | Replace UG generator predecessor-building block        | `scripts/generate_large_demos.py`                                                               | ✅ Done |
| 16.5 | Replace PG generator predecessor-building block        | `scripts/generate_large_demos.py`                                                               | ✅ Done |
| 16.6 | Regenerate both 600-task demo files and validate       | `demos_edu/campus_construction_ug_large.pmproj`, `demos_edu/erp_implementation_pg_large.pmproj` | ✅ Done |

---

### 🔧 PHASE 17 — Interactive Network Viewer (Complete)

> **Goal:** Add a browser-based interactive network visualization using vis.js (via Python `pyvis` wrapper), coexisting with the current Matplotlib in-app diagrams. Solves the 600-task crowding problem by giving users zoom, pan, hover tooltips, and drag in a full browser window.
> **Dependencies:** Phase 14A (shared layout engine), Phase 15 (large project support), Phase 16 (quality predecessor networks)

#### Problem Statement

The Sugiyama + Matplotlib approach works well for ≤50-task projects but produces illegible diagrams for 600-task demos:

- 335 topological layers crammed into viewport width
- ~250 virtual nodes clutter the layout
- No interactive exploration (zoom is toolbar-only, no hover/search)
- `fit_to_viewport()` squashes everything to fit

#### Strategy: Dual Rendering (Matplotlib + vis.js)

| Aspect             | Matplotlib (existing)                  | vis.js / pyvis (new)                     |
| ------------------ | -------------------------------------- | ---------------------------------------- |
| Rendering target   | In-app Tk canvas                       | Self-contained HTML → browser            |
| Best for           | ≤50 tasks, static export (PNG/PDF/SVG) | Any size, especially >50 tasks           |
| Interactivity      | Toolbar zoom/pan only                  | Hover tooltips, drag, search, cluster    |
| Critical path      | Red node fill + bold edges             | Red nodes + red edges + tooltip details  |
| Dependencies       | matplotlib, networkx (already present) | pyvis (~50 KB, pure Python, no binaries) |
| PyInstaller impact | None (already bundled)                 | None (generates HTML, browser renders)   |
| Export             | PNG, PDF, SVG, JPG                     | HTML file (self-contained, shareable)    |

#### Architecture

```
src/pmhelper/utils/interactive_network.py   ← NEW: HTML generator
    generate_interactive_network(results_data, mode) → str (path to HTML file)
    _build_pyvis_graph(activities, critical_activities, mode) → pyvis.Network
    _apply_hierarchical_options(net) → None
```

- **NetworkTab** gets "🌐 Interactive View" button → calls `generate_interactive_network()` → `webbrowser.open()`
- **PertDiagramTab** gets same button → identical call path
- Both buttons always visible (useful even for small projects)
- Matplotlib rendering is untouched — zero regression risk

#### Node Design (vis.js)

Each activity node displays:

- **Label:** Activity ID (e.g., "A101")
- **Title (hover tooltip):** ID, Duration, ES, EF, LS, LF, Float, Critical status
- **Color:** Red (#FF6B6B) for critical, Light Blue (#97C2FC) for non-critical, Green (#7BE141) for START, Orange (#FFA807) for END
- **Shape:** Box (clean, readable at any zoom level)
- **Border:** Bold for critical activities

#### Key Design Decisions

| #   | Decision                            | Choice                                                      | Rationale                                                                |
| --- | ----------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------ |
| 1   | vis.js or Graphviz?                 | **vis.js (via `pyvis`)**                                    | No system binary needed; interactive; zero PyInstaller breakage          |
| 2   | Replace or coexist with Matplotlib? | **Coexist** — both available simultaneously                 | User chooses preferred view; Matplotlib kept for static export           |
| 3   | Threshold gating?                   | **No threshold** — button always available                  | Interactive view is useful even for small projects                       |
| 4   | vis.js layout algorithm?            | **Hierarchical (direction: LR)** with physics disabled      | Matches Sugiyama left-to-right flow; physics off = instant stable layout |
| 5   | HTML output location?               | `tempfile.NamedTemporaryFile(suffix='.html', delete=False)` | OS temp dir; auto-cleaned eventually; no user-visible file management    |
| 6   | Include activity names in labels?   | **ID only in label; full details in hover tooltip**         | Keeps nodes compact; hover reveals everything                            |

#### Phase 17 — Tasks

| #    | Task                                                     | Files Changed                               | Status      |
| ---- | -------------------------------------------------------- | ------------------------------------------- | ----------- |
| 17.1 | Add `pyvis` to `requirements.txt`                        | `requirements.txt`                          | ✅ Done     |
| 17.2 | Create `interactive_network.py` module                   | `src/pmhelper/utils/interactive_network.py` | ✅ Done     |
| 17.3 | Add "Interactive View" button to `NetworkTab`            | `src/pmhelper/gui/tabs/network_tab.py`      | ✅ Done     |
| 17.4 | Add "Interactive View" button to `PertDiagramTab`        | `src/pmhelper/gui/tabs/pert_diagram_tab.py` | ✅ Done     |
| 17.5 | Test with small project (≤15 tasks) — verify layout      | Manual test                                 | ✅ Done     |
| 17.6 | Test with large project (600 tasks) — verify performance | Manual test                                 | ➡️ Deferred to V2 (manual QA) |
| 17.7 | Run full test suite — verify zero regressions            | All test files                              | ✅ Done     |

---

## Definition of Done (V1 Release)

- [ ] All ~50 V1 features listed in `FEATURES_LIST_EDU.md` are reachable and functional in the running app
- [ ] `DECISIONS.md` has answers to all 12 decisions from the Key Decisions Log
- [ ] `pytest` passes with 0 failures across all test files (797+ tests)
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
- [ ] All PG-only tabs (Probability, Resources, RCPS Crashing, Charter, Charter Mgr, DPCI, SWOT, PESTEL, WBS) hidden in UG mode
- [ ] `_PG_ONLY_TABS` and `_pg_only_widgets` updated for all new tabs (Phases 9–16)
- [ ] `_all_tabs_ordered` matches notebook tab indices exactly (18 tabs total)
- [ ] Large demo (`campus_construction_ug_large.pmproj`, `erp_implementation_pg_large.pmproj`) loads without freezing — critical path O(V+E) confirmed
- [ ] Both 600-task demos pass all 19 DAG predecessor constraints (valid DAG, 0 redundant edges, max 3 predecessors, critical path ≥ 30%)
- [ ] `ScrollableMatplotlibFrame` renders network/PERT/Gantt for 600-task project with scrollbars active
- [ ] All scrollable diagrams also render correctly for small (<50 task) projects in auto-fit mode

---

## Phase 18 — Web Application (Angular + FastAPI)

> **Goal:** Re-platform PMHelper Edu as a production-ready Angular web application, wrapping all existing Python computation engines via REST API. The desktop app (Tkinter) remains the current delivery vehicle; this phase builds the web front-end alongside it.
> **Type:** Full-stack web — Angular 17+ frontend + FastAPI backend (existing engines, no rewrite)
> **Product Direction:** Educational only ("PM Scholar")
> **Target Users:** PM students (UG + PG) and instructors
> **Estimated Effort:** ~21 weeks (1 developer + AI assistance)
> **Date Drafted:** March 22, 2026
> **Last Status Update:** March 24, 2026
> **Branch:** `feat/web-v1` (current)
> **Dependencies:** All Python engines from Phases 0–17 are complete and production-ready — this phase exposes them via API only.

---

### 18.0 Product Vision

**PMHelper Edu Web** is an interactive educational platform for learning project management through computation. Students don't just get answers — they understand _why_.

**Core differentiator:** No existing PM educational tool lets students input their own data, run real CPM/PERT/EVM/Risk engines, AND see every intermediate step explained with live formula derivations.

**What it is:**

- A learning tool that wraps a real PM computation engine with step-by-step educational UI
- Learn Mode is the default — walkthroughs, formula explanations, and tooltips are the product
- A secondary "Clean View" hides educational scaffolding for users who already understand the concepts

**What it is NOT:**

- Not a project management tool for managing real projects
- Not a collaboration platform
- Not a Jira / MS Project replacement

---

### 18.1 Why Angular (Not React)

| Reason                                | Detail                                                                                                                                                                                                                                                                                         |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Form-heavy application**            | PMHelper Edu is data-entry + computation + display. Angular Reactive Forms with built-in validation, error states, and dynamic form arrays are purpose-built for the task/period/risk data grids. React requires assembling react-hook-form + zod + custom components to reach the same level. |
| **Structured module architecture**    | Every tab (CPM, PERT, EVM, Risk, Crashing, RCPS, Monte Carlo, WBS, SWOT, PESTEL) is a self-contained feature module with its own components, services, and routes. Angular enforces this separation. In React it relies on convention.                                                         |
| **RxJS for simulation streaming**     | Monte Carlo (5000 trials) and step-by-step animations benefit from observable streams. Angular's native RxJS makes progressive result rendering elegant.                                                                                                                                       |
| **Dependency injection for services** | Each analysis engine maps to an injectable Angular service. Clean, testable, swappable.                                                                                                                                                                                                        |
| **Angular Material + CDK**            | Data tables, dialogs, tabs, steppers out of the box. CDK provides drag-drop (heat map), virtual scrolling (large task lists), and overlay positioning (tooltips).                                                                                                                              |
| **TypeScript-first**                  | Not bolted on — native language from day one.                                                                                                                                                                                                                                                  |

---

### 18.2 Technical Stack

#### Frontend

| Decision     | Choice                                                                                      |
| ------------ | ------------------------------------------------------------------------------------------- |
| Framework    | Angular 17+ (standalone components, signals, new control flow `@if`/`@for`)                 |
| Build        | Angular CLI with esbuild (fast builds, zero config)                                         |
| State        | Angular Signals (local/global) + NgRx ComponentStore (complex view state: EVM, Monte Carlo) |
| Styling      | Angular Material 3 + Tailwind CSS                                                           |
| Charts       | ngx-charts (line/bar/area) + D3.js (network DAG, Gantt, WBS tree, risk heat map)            |
| Data Grid    | Angular Material Table + CDK virtual scroll + inline reactive-form editing                  |
| Math Display | KaTeX via `ngx-katex` (formula rendering in Learn Mode)                                     |
| HTTP         | Built-in `HttpClient` + loading + error interceptors                                        |
| Forms        | Reactive Forms throughout all data entry                                                    |
| Routing      | Angular Router — lazy-loaded feature modules (1 per tab/view)                               |

#### Backend

| Decision       | Choice                                                                    |
| -------------- | ------------------------------------------------------------------------- |
| Framework      | FastAPI (already at `src/pmhelper/server/`) — extend, not replace         |
| Computation    | All existing Python engines — NetworkX, NumPy, Pandas, SciPy — no rewrite |
| Database       | SQLite (dev) / PostgreSQL (prod) — existing SQLAlchemy async models       |
| New API routes | EVM, Risk, Monte Carlo, WBS, SWOT, Steps endpoints (see Section 18.8)     |
| Auth           | None for V1 (single-user educational tool)                                |

---

### 18.3 Application Structure

#### Shell Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  [🎓 PMHelper Edu]            [Learn Mode 🎓 / Clean View ⚡]      │
│                               [Import] [Export] [Save] [UG ↔ PG]   │
├──────────────────────────────────────────────────────────────────────┤
│  Sidebar Navigation           Main Content Area                      │
│  ┌────────────────┐  ┌──────────────────────────────────────────┐   │
│  │ 📊 Dashboard   │  │                                          │   │
│  │ 📝 Input       │  │  Active view renders here.               │   │
│  │ 🔗 Network     │  │                                          │   │
│  │ 📅 Gantt       │  │  Learn Mode: formula + step panels       │   │
│  │ 📈 EVM         │  │  appear beside charts.                   │   │
│  │ ⚡ Crashing    │  │                                          │   │
│  │ 🎲 PERT        │  │  Clean View: charts at full width,       │   │
│  │ ⚠️  Risk        │  │  no educational overlay.                │   │
│  │ 🔄 RCPS   [PG] │  │                                          │   │
│  │ 🎯 Monte  [PG] │  │                                          │   │
│  │ 📋 WBS    [PG] │  │                                          │   │
│  │ 🔍 SWOT   [PG] │  │                                          │   │
│  │ 🌍 PESTEL [PG] │  │                                          │   │
│  └────────────────┘  └──────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────┤
│  Status: [Project: sample.csv]  [Mode: UG]  [Tasks: 9]  [✓ Ready]  │
└──────────────────────────────────────────────────────────────────────┘
```

#### Angular Module Tree

```
src/app/
├── core/
│   ├── services/
│   │   ├── api.service.ts              # HttpClient wrapper, base URL, error handling
│   │   ├── cpm.service.ts              # POST /api/v1/analysis/cpm
│   │   ├── pert.service.ts             # POST /api/v1/analysis/pert
│   │   ├── evm.service.ts              # POST /api/v1/analysis/evm
│   │   ├── risk.service.ts             # POST /api/v1/analysis/risk
│   │   ├── crashing.service.ts         # POST /api/v1/analysis/crashing
│   │   ├── rcps.service.ts             # POST /api/v1/analysis/rcps
│   │   ├── monte-carlo.service.ts      # POST /api/v1/analysis/monte-carlo
│   │   ├── wbs.service.ts              # WBS CRUD + aggregation
│   │   ├── project.service.ts          # Save / load / import / export
│   │   └── sample.service.ts           # GET /api/v1/samples
│   ├── models/
│   │   ├── activity.model.ts
│   │   ├── cpm-result.model.ts
│   │   ├── evm.model.ts
│   │   ├── risk.model.ts
│   │   ├── pert.model.ts
│   │   ├── monte-carlo.model.ts
│   │   ├── wbs.model.ts
│   │   ├── swot.model.ts
│   │   ├── pestel.model.ts
│   │   └── step.model.ts               # CalculationStep for walkthroughs
│   ├── state/
│   │   └── project.store.ts            # Signals-based global state
│   └── interceptors/
│       ├── loading.interceptor.ts
│       └── error.interceptor.ts
│
├── shared/
│   ├── components/
│   │   ├── kpi-card/                   # Value + label + RAG badge + trend + tooltip
│   │   ├── formula-display/            # KaTeX rendering with variable substitution
│   │   ├── explainer-tooltip/          # "?" popover — Learn Mode only
│   │   ├── step-walkthrough/           # Step player (prev / next / play)
│   │   ├── worked-solution/            # Scrollable full worked-solution panel
│   │   ├── file-dropzone/              # Drag-drop CSV / Excel upload
│   │   ├── column-mapper/              # Auto-detect + manual column mapping dialog
│   │   ├── validation-panel/           # Error list with click-to-fix
│   │   ├── mode-toggle/                # Learn 🎓 / Clean ⚡ switch
│   │   ├── level-toggle/               # UG / PG switch
│   │   ├── sample-selector/            # Sample dataset picker dialog
│   │   ├── export-menu/                # PNG / PDF / CSV / Excel dropdown
│   │   └── schedule-stepper/           # 5-badge PMBOK process indicator
│   ├── pipes/
│   │   ├── rag-status.pipe.ts          # KPI value → 'red' | 'amber' | 'green'
│   │   ├── currency.pipe.ts
│   │   └── duration-format.pipe.ts
│   └── directives/
│       └── learn-mode-only.directive.ts  # *appLearnMode structural directive
│
├── features/                           # One lazy-loaded module per tab
│   ├── dashboard/
│   ├── input/
│   │   └── components/
│   │       ├── task-grid/
│   │       ├── evm-period-grid/
│   │       ├── risk-entry/
│   │       └── import-wizard/
│   ├── network/
│   │   └── components/
│   │       ├── cpm-node/
│   │       ├── dependency-edge/
│   │       ├── network-canvas/         # D3 Sugiyama layout + zoom + animation
│   │       ├── forward-pass-stepper/   # Learn Mode animated forward pass
│   │       └── backward-pass-stepper/
│   ├── gantt/
│   │   └── components/
│   │       ├── gantt-bar/
│   │       ├── timeline-axis/
│   │       ├── dependency-arrow/
│   │       ├── float-indicator/        # EF → LF lighter bar extension
│   │       └── gantt-canvas/
│   ├── evm/
│   │   └── components/
│   │       ├── s-curve-chart/
│   │       ├── kpi-panel/
│   │       ├── eac-formula-toggle/
│   │       └── evm-explainer/
│   ├── crashing/
│   │   └── components/
│   │       ├── cost-curve-chart/
│   │       ├── crashing-step-table/
│   │       └── crashing-stepper/
│   ├── pert/
│   │   └── components/
│   │       ├── three-point-table/
│   │       ├── probability-calc/
│   │       ├── distribution-chart/
│   │       └── pert-explainer/
│   ├── risk/
│   │   └── components/
│   │       ├── risk-register/
│   │       ├── heat-map/               # 5×5 D3 matrix
│   │       ├── exposure-chart/
│   │       └── contingency-calc/
│   ├── rcps/                           # PG only
│   │   └── components/
│   │       ├── resource-histogram/
│   │       ├── schedule-comparison/
│   │       └── rcps-stepper/
│   ├── monte-carlo/                    # PG only
│   │   └── components/
│   │       ├── mc-config/
│   │       ├── duration-histogram/
│   │       ├── cost-histogram/
│   │       ├── cp-frequency-table/
│   │       └── convergence-chart/
│   ├── wbs/                            # PG only
│   │   └── components/
│   │       ├── wbs-canvas/             # D3 Walker layout
│   │       ├── wbs-node/
│   │       ├── wbs-editor-dialog/
│   │       └── wbs-rollup-panel/
│   ├── swot/                           # PG only
│   │   └── components/
│   │       ├── swot-matrix/
│   │       └── auto-extract-panel/
│   └── pestel/                         # PG only
│       └── components/
│           ├── pestel-heatmap/
│           └── pestel-factor-table/
│
├── layout/
│   ├── app-shell/
│   ├── sidebar/
│   └── top-bar/
│
└── app.routes.ts                       # Lazy routes for all 13 features
```

---

### 18.4 Global State (Signals)

```typescript
// core/state/project.store.ts

// UI
export const mode = signal<"learn" | "clean">("learn");
export const academicLevel = signal<"ug" | "pg">("ug");
export const isLoading = signal(false);

// Project data
export const activities = signal<Activity[]>([]);
export const cpmResults = signal<CPMResults | null>(null);
export const pertResults = signal<PERTResults | null>(null);
export const evmProject = signal<EVMProject | null>(null);
export const riskRegister = signal<Risk[]>([]);
export const monteCarloResults = signal<MCResults | null>(null);
export const wbsNodes = signal<WBSNode[]>([]);
export const swotAnalysis = signal<SWOTAnalysis | null>(null);
export const pestelAnalysis = signal<PESTELAnalysis | null>(null);

// Derived (computed)
export const criticalPath = computed(
  () => cpmResults()?.critical_paths?.[0] ?? [],
);
export const projectDuration = computed(
  () => cpmResults()?.project_duration ?? 0,
);
export const isAnalyzed = computed(() => cpmResults() !== null);
export const pgVisible = computed(() => academicLevel() === "pg");
```

---

### 18.5 View Specifications

#### 18.5.1 Dashboard

- **Purpose:** At-a-glance project health after analysis
- **Components:** KPI card grid (6 cards: Duration, CP Length, Avg Float, # Tasks, # Critical, Total Cost), mini network diagram, mini Gantt, alerts panel
- **Learn Mode:** Each KPI card has "?" tooltip explaining the metric
- **Interactions:** Click card → navigate to detail view; click mini-chart → expand to full view

#### 18.5.2 Input View

- **Purpose:** Data entry and import
- **Sub-tabs:** Tasks · EVM Periods · Risk Register
- **Task Columns:** ID, Name, Duration, Predecessors, O/M/P, Resource Demand, Cost, Min Duration, Crash Cost
- **Validation:** Real-time red borders, error panel, DAG acyclicity check, non-negative durations, predecessor existence
- **Schedule Stepper:** 5-badge PMBOK indicator (Define → Sequence → Resources → Durations → Analyze)
- **Learn Mode:** Column header tooltips; "What should I enter?" wizard for first-time users

#### 18.5.3 Network Diagram

- **Purpose:** Interactive dependency DAG with CPM scheduling data
- **Node Format (CPM box):**
  ```
  ┌────┬────┐
  │ ES │ EF │
  ├────┴────┤
  │ ID/Name │
  │  Dur    │
  ├────┬────┤
  │ LS │ LF │
  ├────┴────┤
  │  Float  │
  └─────────┘
  ```
- **Layout:** Hierarchical Sugiyama (port from `utils/network_layout.py`)
- **Critical path:** Red nodes + edges where Float = 0
- **Interactions:** Hover → fade non-connected nodes; click → detail panel; "Critical Path Only" filter; zoom/fit
- **Learn Mode:** "Step Through" button animates forward pass (ES/EF fills node-by-node), then backward pass (LS/LF), then float, then critical path reveal. Each step shows formula: `ES(C) = max(EF(A), EF(B)) = max(5, 3) = 5`

#### 18.5.4 Gantt Chart

- **Purpose:** Timeline view with dependencies
- **Standard variant:** Bars with dependency arrows, float extension (lighter EF→LF), today line
- **Tracking variant (PG):** Baseline bars + actual overlay + % complete shading
- **Interactions:** Hover → tooltip (ES/EF/LS/LF/Float); click bar → highlight in Network (cross-view); zoom time axis
- **Learn Mode:** Float bar tooltip: "This task can slip X days without delaying the project"

#### 18.5.5 EVM Dashboard

- **Purpose:** Earned Value performance tracking
- **KPI Cards (11):** CV, SV, CPI, SPI, PC, PS, CR, EAC₁, EAC₂, EAC₃, VAC, TCPI — each with RAG badge
- **RAG thresholds:** CPI/SPI > 1.0 = Green; 0.9–1.0 = Amber; < 0.9 = Red
- **Charts:** S-Curve (PV/EV/AC multi-line with area fills)
- **EAC toggle:** Switch between formulas — see how forecast changes
- **Learn Mode:** "Explain" button per KPI: `CPI = EV / AC = $8,500 / $10,000 = 0.85 → spending $1.18 per $1.00 of value — over budget`. Full worked solution panel for all 11 KPIs.

#### 18.5.6 Crashing / Cost Optimization

- **Purpose:** Time-cost tradeoff analysis
- **Chart:** Direct + indirect + total cost vs. duration curves; optimum duration marker
- **Table:** Step-by-step crashing decisions (activity crashed, cost per step, new duration)
- **Learn Mode:** Animated step narration: "Step 1: Activity F is cheapest on critical path at $200/day. Crash F by 1 day. Project: 28 → 27 days."

#### 18.5.7 PERT / Probability

- **Purpose:** Probabilistic scheduling with 3-point estimates
- **Components:** O/M/P table; expected time + variance display; P(T ≤ X) calculator; normal distribution chart with Z-score marker
- **Learn Mode:** Full formula walkthrough: $t_e = (O + 4M + P) / 6$, $\sigma^2 = ((P - O) / 6)^2$, $Z = (T_{target} - \mu) / \sigma$, $P = \Phi(Z)$

#### 18.5.8 Risk View

- **Purpose:** Risk identification and quantification
- **Risk Register:** CRUD table (ID, Name, Probability, Impact, Category, Exposure)
- **Heat Map:** 5×5 D3 grid (probability Y-axis, impact X-axis); red/amber/green zones; risk dots
- **Exposure chart:** Horizontal bars by exposure (largest first)
- **Contingency:** Total exposure = sum(p × I); displayed as Contingency Reserve
- **Learn Mode:** "Risk Exposure = Probability × Impact. R1: 0.3 × $50,000 = $15,000. Total: $42,500."

#### 18.5.9 RCPS / Resource View (PG only)

- **Purpose:** Resource-constrained scheduling
- **Components:** Resource limit input; algorithm selector (Burgess / Min Moment); stacked histogram (before/after); CPM vs. RCPS schedule comparison
- **Learn Mode:** Heuristic walkthrough: "Period 3: Tasks B and D both need resources. B has less slack → schedule B. D delayed to Period 4."

#### 18.5.10 Monte Carlo (PG only)

- **Purpose:** Statistical project outcome analysis
- **Config:** # trials (default 5000), seed, cost min/max factors
- **Charts:** Duration histogram with P50/P80/P90 markers; cost histogram; CP frequency table; convergence chart
- **Learn Mode:** Progressive histogram build — students watch distribution form. "After 5000 trials: 90% confidence the project finishes by Day 34."

#### 18.5.11 WBS (PG only)

- **Purpose:** Work Breakdown Structure — scope decomposition
- **Canvas:** D3 Walker layout (port from `wbs_layout_edu.py`); rectangle nodes with WBS code, name, cost, duration; color by level
- **Interactions:** Click to select; right-click context menu (Add Child / Edit / Delete / Expand-Collapse); double-click to edit; undo (20-step stack)
- **Rollup panel:** Aggregated cost (sum), duration (max), progress (weighted avg by cost)
- **Learn Mode:** "WBS decomposes scope into work packages. Cost rolls up as sum. Duration = max of children (parallel scheduling assumption)."

#### 18.5.12 SWOT Analysis (PG only)

- **Purpose:** Strategic analysis of project context
- **Components:** 2×2 matrix grid; factor list per quadrant; auto-extract from Charter / Risk Register / EVM KPIs; manual add/edit; export
- **Auto-extract triggers:** CPI < 0.95 → adds "Cost overrun (Weakness)"; high-exposure risks → "Threats"; strategic alignment from Charter → "Opportunities"

#### 18.5.13 PESTEL Analysis (PG only)

- **Purpose:** External factor analysis
- **Components:** 6-cell heatmap (P/E/S/T/En/L); factor detail table with impact × probability scoring; "Create Risk" button → push factor to Risk Register
- **Interactions:** Click category → filter factors; add/edit factors; export

---

### 18.6 Data Visualization Decisions

| Visualization              | Library                                  | Justification                                                                                                                                                                     |
| -------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Network DAG (CPM/PERT)     | D3.js — custom Sugiyama layout           | Port existing Python layout logic. Full control over CPM-box rendering, animation, critical path overlay, step-through. No ready-made library handles educational step animation. |
| Gantt chart                | Custom SVG components                    | Full control over float extensions, dependency arrows, tracking overlay, educational annotations. No Gantt library supports Learn Mode.                                           |
| S-Curve (EVM)              | ngx-charts (AreaChart)                   | Standard multi-line chart, Angular-native, declarative API.                                                                                                                       |
| Resource histogram         | ngx-charts (BarVerticalStackedComponent) | Stacked bars by task per period, built-in legend and color mapping.                                                                                                               |
| Risk heat map              | D3.js — custom grid                      | 5×5 colored grid with draggable risk dots. No ngx-charts equivalent.                                                                                                              |
| Monte Carlo histogram      | D3.js — histogram layout                 | Precise control over percentile marker lines, CDF overlay, progressive animation via RxJS.                                                                                        |
| Cost curves (Crashing)     | ngx-charts (LineChartComponent)          | Three-line chart (direct/indirect/total). Standard line chart suffices.                                                                                                           |
| Normal distribution (PERT) | D3.js — area path                        | Bell curve with shaded region and Z-score marker. Custom SVG required.                                                                                                            |
| WBS tree                   | D3.js — tree layout (Walker port)        | Variable-width rectangles, level coloring, expand/collapse. No off-the-shelf component.                                                                                           |
| SWOT matrix                | Angular Material grid — custom CSS       | 2×2 CSS grid with Material list items per quadrant. Simple enough for CSS; no chart library needed.                                                                               |
| PESTEL heatmap             | D3.js — color-scaled cells               | 6-cell grid with intensity coloring based on exposure score.                                                                                                                      |

**Critical path highlight strategy:** Red applied simultaneously on both Network and Gantt. When user activates "Critical Path Only" filter, non-critical nodes/bars fade to 20% opacity. This dual highlight across views is the single most educationally impactful visual choice — it shows the same information in temporal (Gantt) and structural (Network) contexts simultaneously.

---

### 18.7 Component Breakdown

#### Visualization Components

| Component                      | Responsibility                                               | Key Inputs                                             | Key Outputs                          |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------ | ---------------- | ------- | ----------- | ---------------------------- |
| `CpmNodeComponent`             | SVG CPM box (ES/EF/ID/Dur/LS/LF/Float) with animation state  | `node`, `isCritical`, `animationState: 'hidden'        | 'es-ef'                              | 'ls-lf'          | 'float' | 'complete'` | `(nodeClick)`, `(nodeHover)` |
| `DependencyEdgeComponent`      | SVG directed edge between nodes                              | `from: Point`, `to: Point`, `isCritical`               | —                                    |
| `NetworkCanvasComponent`       | D3 Sugiyama layout, zoom/pan, step animation orchestration   | `graph: GraphData`, `criticalPath`, `animationEnabled` | `(nodeSelected)`                     |
| `ForwardPassStepperComponent`  | Animates ES/EF propagation node by node with formula display | `nodes: CPMNode[]`, `edges`, `speed`                   | `(stepChange)`                       |
| `GanttBarComponent`            | Single task bar SVG + optional float extension               | `task`, `timeScale`, `showFloat`, `variant`            | `(barClick)`, `(barHover)`           |
| `GanttCanvasComponent`         | Full Gantt: task list + bars + arrows + axis + scroll        | `activities`, `variant: 'standard'                     | 'tracking'`                          | `(taskSelected)` |
| `SCurveChartComponent`         | PV/EV/AC multi-line chart                                    | `periods: EVMPeriod[]`, `showForecast`                 | `(periodHover)`                      |
| `ResourceHistogramComponent`   | Stacked bar chart of resource usage per period               | `profile: ResourceProfile`, `limit`                    | `(periodHover)`                      |
| `RiskHeatMapComponent`         | D3 5×5 grid with risk dots and color zones                   | `risks: Risk[]`, `gridSize`                            | `(cellClick)`, `(riskClick)`         |
| `MonteCarloHistogramComponent` | D3 histogram with P50/P80/P90 markers + optional CDF         | `results: MCResults`, `percentiles`                    | `(barHover)`                         |
| `WbsCanvasComponent`           | D3 tree (Walker layout): rectangles, connectors, scroll/zoom | `nodes: WBSNode[]`, `layout: LayoutResult`             | `(nodeSelected)`, `(nodeRightClick)` |
| `CostCurveChartComponent`      | Direct + indirect + total cost vs. duration                  | `costData: CostPoint[]`, `optimumDuration`             | `(pointHover)`                       |
| `DistributionChartComponent`   | Normal bell curve with Z-score / shaded region               | `mean`, `stddev`, `target`                             | —                                    |
| `SwotMatrixComponent`          | 2×2 quadrant grid with editable factor lists                 | `analysis: SWOTAnalysis`                               | `(factorAdd)`, `(factorEdit)`        |
| `PestelHeatmapComponent`       | 6-cell grid with intensity coloring by exposure              | `analysis: PESTELAnalysis`                             | `(categoryClick)`                    |

#### Educational Components (Learn Mode only)

| Component                   | Responsibility                                                                | Key Inputs                                                       | Key Outputs        |
| --------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------ |
| `StepWalkthroughComponent`  | Animated step-by-step player (prev/next/play/pause)                           | `steps: CalculationStep[]`, `autoPlaySpeed`                      | `(stepChange)`     |
| `FormulaDisplayComponent`   | KaTeX rendering with variable substitution + result highlight                 | `formula: string`, `variables: Record<string, number>`, `result` | —                  |
| `ExplainerTooltipComponent` | "?" icon → popover with plain-English explanation                             | `content: string`, `title`                                       | —                  |
| `WorkedSolutionComponent`   | Scrollable full worked-solution panel (all steps with formulas)               | `steps: CalculationStep[]`, `title`                              | `(export)`         |
| `SampleSelectorComponent`   | Dialog grid of sample datasets with UG/PG badges and preview                  | `samples: SampleProject[]`, `level`                              | `(sampleSelected)` |
| `ScheduleStepperComponent`  | 5-badge PMBOK process indicator (Define→Sequence→Resources→Durations→Analyze) | `currentStep`                                                    | `(stepClick)`      |

#### Data Entry Components

| Component                  | Responsibility                                                                             | Key Inputs                  | Key Outputs                           |
| -------------------------- | ------------------------------------------------------------------------------------------ | --------------------------- | ------------------------------------- |
| `TaskGridComponent`        | Editable Angular Material table with inline reactive-form editing and real-time validation | `tasks: Activity[]`         | `(tasksChange)`, `(validationErrors)` |
| `EvmPeriodGridComponent`   | PV/EV/AC period table with cumulative auto-calc                                            | `periods: EVMPeriod[]`      | `(periodsChange)`                     |
| `RiskEntryComponent`       | Risk register CRUD table                                                                   | `risks: Risk[]`             | `(risksChange)`                       |
| `FileDropzoneComponent`    | Drag-drop CSV/Excel upload with format detection                                           | `accept: string[]`          | `(fileLoaded)`                        |
| `ColumnMapperComponent`    | Auto-detect + manual mapping of imported columns to schema                                 | `headers`, `expectedFields` | `(mappingConfirmed)`                  |
| `ValidationPanelComponent` | Error/warning list with click-to-focus-cell navigation                                     | `errors: ValidationError[]` | `(errorClick)`                        |

#### Layout Components

| Component           | Responsibility                                                                          |
| ------------------- | --------------------------------------------------------------------------------------- |
| `AppShellComponent` | Top bar + sidebar + routed content area                                                 |
| `SidebarComponent`  | Nav links with icons; PG-only items show `[PG]` badge and are disabled in UG mode       |
| `TopBarComponent`   | Logo, Learn/Clean mode toggle, UG/PG level toggle, global action buttons                |
| `KpiCardComponent`  | Single metric: value + label + RAG badge + trend arrow + optional "?" explainer tooltip |

---

### 18.8 API Specification

#### Existing Endpoints (Verify + Extend)

```
POST /api/v1/analysis/cpm
  Body:     { activities: Activity[] }
  Response: { project_duration, critical_paths, critical_activities,
              nodes: CPMNode[], edges: Edge[] }

POST /api/v1/analysis/pert
  Body:     { activities: PERTActivity[], target_duration? }
  Response: { expected_duration, variance, std_dev, probability,
              z_score, activities: PERTResult[] }

POST /api/v1/analysis/crashing
  Body:     { activities: Activity[], indirect_cost_rate: number }
  Response: { cost_curve: CostPoint[], optimal_duration,
              crashing_steps: CrashStep[] }

POST /api/v1/analysis/rcps
  Body:     { activities: Activity[], resource_limit: number,
              algorithm: 'burgess' | 'min_moment' }
  Response: { schedule: RCPSSchedule, histogram_before: Profile,
              histogram_after: Profile }
```

#### New Endpoints (Build in Phase 18)

```
POST /api/v1/analysis/evm
  Body:     { project: EVMProject }
  Response: { kpis: AllKPIs, s_curve_data: SCurvePoint[] }

POST /api/v1/analysis/risk
  Body:     { risks: Risk[], bac: number }
  Response: { risks_with_exposure: Risk[], total_exposure,
              contingency_reserve, heat_map_data }

POST /api/v1/analysis/monte-carlo
  Body:     { activities: Activity[], evm_tasks: EVMTask[],
              bac: number, n_trials: number, seed? }
  Response: { durations: number[], costs: number[],
              p50_duration, p80_duration, p90_duration,
              p_cost_within_bac, cp_frequencies: Record<string, number> }

POST /api/v1/analysis/wbs
  Body:     { nodes: WBSNode[] }
  Response: { validated_nodes, layout: LayoutResult, rollup: RollupResult }

POST /api/v1/analysis/swot-extract
  Body:     { charter_data?, risk_register?, evm_kpis? }
  Response: { analysis: SWOTAnalysis }

POST /api/v1/analysis/steps/cpm
  Body:     { activities: Activity[] }
  Response: { forward_steps: Step[], backward_steps: Step[], float_steps: Step[] }

POST /api/v1/analysis/steps/evm
  Body:     { project: EVMProject }
  Response: { steps: Step[] }

POST /api/v1/analysis/steps/pert
  Body:     { activities: PERTActivity[], target: number }
  Response: { steps: Step[] }

GET  /api/v1/samples
  Response: [{ id, name, level: 'ug'|'pg', task_count, description }]

GET  /api/v1/samples/:id
  Response: { activities, evm_project?, risks?, wbs_nodes? }

POST /api/v1/import/csv
  Body:     FormData (file)
  Response: { headers: string[], detected_mapping: ColumnMapping,
              preview_rows: Row[] }

POST /api/v1/import/validate
  Body:     { rows: Row[], mapping: ColumnMapping }
  Response: { activities: Activity[], errors: ValidationError[],
              warnings: Warning[] }

POST /api/v1/export/pdf
  Body:     { project_state: FullProjectState }
  Response: PDF binary

POST /api/v1/export/excel
  Body:     { project_state: FullProjectState }
  Response: XLSX binary
```

---

### 18.9 Data Models (TypeScript)

```typescript
// core/models/activity.model.ts
export interface Activity {
  id: string;
  activity: string;
  duration: number;
  predecessors: string[];
  min_duration?: number;
  crash_cost?: number;
  resource_demand?: number;
  normal_cost?: number;
  optimistic?: number;
  most_likely?: number;
  pessimistic?: number;
}

// core/models/cpm-result.model.ts
export interface CPMNode {
  id: string;
  activity: string;
  duration: number;
  ES: number;
  EF: number;
  LS: number;
  LF: number;
  total_float: number;
  free_float: number;
  is_critical: boolean;
}
export interface CPMResults {
  project_duration: number;
  critical_paths: string[][];
  critical_activities: string[];
  nodes: CPMNode[];
  edges: { from: string; to: string }[];
}

// core/models/evm.model.ts
export interface EVMTask {
  task_id: string;
  name: string;
  budget: number;
  pct_complete: number;
  planned_start: number;
  planned_finish: number;
}
export interface EVMPeriod {
  index: number;
  label: string;
  pv_cumulative: number;
  ev_cumulative: number;
  ac_cumulative: number;
}
export interface EVMProject {
  project_name: string;
  bac: number;
  currency_symbol: string;
  periods: EVMPeriod[];
  tasks: EVMTask[];
}
export interface EVMKPIs {
  ev: number;
  cv: number;
  sv: number;
  cpi: number;
  spi: number;
  pc: number;
  ps: number;
  cr: number;
  eac1: number;
  eac2: number;
  eac3: number;
  vac: number;
  tcpi_bac: number;
}
export type RAGStatus = "red" | "amber" | "green";

// core/models/risk.model.ts
export interface Risk {
  id: string;
  name: string;
  description: string;
  probability: number;
  impact: number;
  category: "Schedule" | "Cost" | "Quality" | "Scope" | "Other";
  exposure: number; // computed: p × I
}

// core/models/monte-carlo.model.ts
export interface MCResults {
  durations: number[];
  costs: number[];
  cp_frequencies: Record<string, number>;
  p50_duration: number;
  p80_duration: number;
  p90_duration: number;
  p_cost_within_bac: number;
  n_trials: number;
}

// core/models/step.model.ts
export interface CalculationStep {
  title: string;
  formula: string; // KaTeX source
  substitution: string; // KaTeX with actual values
  result: string; // KaTeX result expression
  explanation: string; // Plain English
  highlight_nodes?: string[];
}
```

---

### 18.10 Execution Plan

> **Status (March 24, 2026):** Phases 18.1–18.3 are complete. The execution plan below has been re-ordered based on a production-readiness audit. Sprints 0–2 address non-feature gaps that must be fixed before continuing to build new views.

---

#### 18.10.0 — Current Implementation Status

| Phase                         | Description                                                                             | Status         | Notes                                     |
| ----------------------------- | --------------------------------------------------------------------------------------- | -------------- | ----------------------------------------- |
| 18.1 Foundation               | Angular scaffold, AppShell, routes, store, data models, all shared components           | ✅ Done        |                                           |
| 18.2 Data Entry & CPM         | TaskGrid, EvmPeriodGrid, RiskEntry, FileDropzone, SampleSelector, CPM + PERT services   | ✅ Done        |                                           |
| 18.3.1 Network diagram        | D3 Sugiyama layout, CpmNodeComponent, DependencyEdge, zoom/pan                          | ✅ Done        |                                           |
| 18.3.2 Step-through animation | ForwardPassStepper, BackwardPassStepper (animated Learn Mode passes)                    | ✅ Done        |                                           |
| 18.3.3–4 Gantt chart          | GanttCanvasComponent (pure SVG), float bars, dependency arrows, cross-view selection    | ✅ Done        |                                           |
| 18.3.5 Dashboard              | 6 KPI cards, float distribution chart, alerts panel, critical paths display             | ✅ Done        |                                           |
| 18.3.6 PERT view              | 3-point table, bell curve SVG, probability calculator, Z-score, Learn Mode walkthroughs | ✅ Done        |                                           |
| 18.3.7 Cross-view linking     | `selectedTaskId` signal wired across Gantt ↔ Network                                    | ✅ Done        |                                           |
| 18.4 Advanced Analysis        | EVM, Crashing, Risk, RCPS, Monte Carlo                                                  | ⬜ Stubs       | All backend endpoints exist               |
| 18.5 PG-Only Modules          | WBS, SWOT, PESTEL                                                                       | ⬜ Stubs       | All backend endpoints exist               |
| 18.6 Educational Layer        | `*appLearnMode` directive + KaTeX + worked solutions                                    | 🔶 Partial     | Directive done; KaTeX + step data missing |
| 18.7 Polish & Production      | Responsive, a11y, CI/CD, save/export                                                    | ⬜ Not started |                                           |

**Backend:** All 12 `/api/web/` endpoints implemented: CPM, PERT, EVM, Crashing, Risk, Monte Carlo, RCPS, Steps (CPM/PERT/EVM), Samples, CSV Import.

**Known issues to fix in Sprint 0:**

- `_DEMOS_DIR` path bug in `web.py` — one `.parent` too many
- No Angular static file serving from FastAPI (app not publicly deployable)
- `render.yaml` `CORS_ORIGINS` points to nonexistent `pmhelper-frontend.onrender.com`
- No `localStorage` persistence — data lost on browser refresh
- No HTTP interceptors or global `ErrorHandler`
- `effect()` calls in NetworkCanvas, GanttCanvas, steppers lack `DestroyRef` cleanup

---

#### Sprint 0 — Foundation Hardening _(before features, before deploy)_

**Goal:** Make the existing 5 working views production-survivable. No new features — fix infrastructure gaps that compound as more views are added.

| #   | Task                         | File(s)                                                              | What to do                                                                                                                                                                                                                                                                                                                                       |
| --- | ---------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0.1 | **State persistence**        | `core/store/project.store.ts`                                        | Create `persistence.service.ts`. On every store signal change (via `effect()`), debounce 1s and write `activities`, `projectName`, `evmProject`, `riskRegister`, `academicLevel`, `viewMode` to `localStorage`. On app boot (`APP_INITIALIZER`), read from `localStorage` and restore signals. "New Project" clears both store + `localStorage`. |
| 0.2 | **HTTP loading interceptor** | `core/interceptors/loading.interceptor.ts`, `app.config.ts`          | Functional interceptor: `isLoading.set(true)` on request, `isLoading.set(false)` on finalize. Register via `withInterceptors([loadingInterceptor, errorInterceptor])`. Remove manual `isLoading` toggles from individual components.                                                                                                             |
| 0.3 | **HTTP error interceptor**   | `core/interceptors/error.interceptor.ts`                             | Catch all `HttpErrorResponse`, show `MatSnackBar` toast with `error.error?.detail ?? error.error?.message ?? 'HTTP {status}'`. Re-throw so calling code still sees the error if needed.                                                                                                                                                          |
| 0.4 | **Global ErrorHandler**      | `core/global-error-handler.ts`, `app.config.ts`                      | Extend `ErrorHandler`. Override `handleError()`: log to console, show snackbar "Unexpected error — please refresh." Register with `{ provide: ErrorHandler, useClass: GlobalErrorHandler }` in `app.config.ts`.                                                                                                                                  |
| 0.5 | **Effect cleanup**           | `network-canvas.component.ts`, `gantt-canvas.component.ts`, steppers | Inject `DestroyRef` in constructor. Pass `{ injector: this.injector }` to `effect()` calls, or use `takeUntilDestroyed(destroyRef)`. Fill the empty `ngOnDestroy()` in `gantt-canvas`.                                                                                                                                                           |
| 0.6 | **Fix `_DEMOS_DIR`**         | `src/pmhelper/server/api/routes/web.py`                              | Change `Path(__file__).parent.parent.parent.parent.parent` → `Path(__file__).parent.parent.parent.parent` (remove one `.parent`). Fixes `/api/web/samples` and `/api/web/samples/{id}`.                                                                                                                                                          |

**Deliverable:** Data survives browser refresh. Errors surface as toasts. No memory leaks. Demo samples load correctly.

---

#### Sprint 1 — Deploy MVP

**Goal:** App is live at a public URL serving all 5 working views.

| #   | Task                                | File(s)                       | What to do                                                                                                                                                                                                                                                                                |
| --- | ----------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1 | **Multi-stage Dockerfile**          | `Dockerfile`                  | **Stage 1** (node:20-alpine): copy `web/`, run `npm ci`, run `npx ng build --configuration=production`. **Stage 2** (python:3.12-slim): copy built `web/dist/pmhelper-edu-web/browser` → `/app/static/`. Install Python deps. Copy `src/`. Keep existing `CMD`.                           |
| 1.2 | **Serve Angular from FastAPI**      | `src/pmhelper/server/main.py` | After all `include_router()` calls, add: `app.mount("/", StaticFiles(directory="static", html=True), name="static")`. Add SPA fallback: `@app.get("/{full_path:path}")` returning `FileResponse("static/index.html")` for any non-`/api/` path. Remove CORS middleware (same-origin now). |
| 1.3 | **Update `render.yaml`**            | `render.yaml`                 | Single service. Remove `databases` block. Set `dockerfilePath: ./Dockerfile`. Remove `CORS_ORIGINS` env var. Update `branch: feat/web-v1`.                                                                                                                                                |
| 1.4 | **Fix Material Icons font-display** | `web/src/index.html`          | Add `&display=swap` to the Material Icons Google Fonts URL. Prevents FOIT on slow connections.                                                                                                                                                                                            |
| 1.5 | **Smoke test**                      | Render deployment             | Load app → load sample → run CPM → Dashboard, Network, Gantt render → PERT runs → refresh browser → data still present.                                                                                                                                                                   |

**Deliverable:** Public URL. Users can share a link to the working MVP.

---

#### Sprint 2 — CI/CD + Test Scaffolding

**Goal:** Catch regressions before building 8 more views on top of the existing foundation.

| #   | Task                      | File(s)                                 | What to do                                                                                                                                                                                                                                               |
| --- | ------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2.1 | **Angular lint job**      | `.github/workflows/ci-cd.yml`           | Add job `angular-lint`: `cd web && npm ci && npm run lint`. Trigger: all PRs + pushes to `feat/web-v1`, `production`.                                                                                                                                    |
| 2.2 | **Angular build job**     | `.github/workflows/ci-cd.yml`           | Add job `angular-build`: `cd web && npm ci && npx ng build --configuration=production`. Fail pipeline on any TypeScript/build error.                                                                                                                     |
| 2.3 | **Angular unit test job** | `.github/workflows/ci-cd.yml`           | Add job `angular-test`: `cd web && npm ci && npx ng test --watch=false --browsers=ChromeHeadless`. Gate feature deployment on this.                                                                                                                      |
| 2.4 | **Core unit tests**       | `web/src/app/core/**/*.spec.ts`         | `project.store.spec.ts` (resetProject, computed signals). `api.service.spec.ts` (handleError formatting). `cpm.service.spec.ts` (request body mapping). `pg-only.guard.spec.ts` (UG blocked, PG allowed). Use `HttpTestingController`.                   |
| 2.5 | **Rate limiting**         | `src/pmhelper/server/main.py`, `web.py` | Install `slowapi`. `@limiter.limit("30/minute")` on all `/api/web/analysis/*` endpoints. `@limiter.limit("5/minute")` on `/api/web/analysis/monte-carlo`. Cap `num_simulations` server-side: `body.num_simulations = min(body.num_simulations, 50_000)`. |

**Deliverable:** PRs blocked if Angular build/lint/test fails. Core logic has unit tests. Monte Carlo endpoint rate-limited.

---

#### Sprint 3 — Advanced Analysis Views

**Goal:** Implement the 5 remaining analysis views. All backend endpoints already exist — this is frontend work only.

Each view pattern: read store signals → call API → update result signal → render → Learn Mode section.

| #   | Task                             | Backend endpoint                     | Key components / notes                                                                                                                                                                                  |
| --- | -------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3.1 | **EVM view**                     | `POST /api/web/analysis/evm`         | S-curve (PV/EV/AC) as D3 line chart. 11 KPI cards with RAG badges. EAC formula toggle (EAC₁/₂/₃). Full worked solution via `/api/web/analysis/steps/evm`.                                               |
| 3.2 | **Crashing view**                | `POST /api/web/analysis/crashing`    | D3 cost-time tradeoff (direct + indirect + total lines). Step table (activity, ∆cost, new duration). Optimum duration marker. Learn Mode narration per step.                                            |
| 3.3 | **Risk view**                    | `POST /api/web/analysis/risk`        | Reads `riskRegister` signal. D3 5×5 heat map. Horizontal exposure bar chart (sorted descending). Contingency reserve total. EMV formula per risk in Learn Mode.                                         |
| 3.4 | **RCPS view** _(PG only)_        | `POST /api/web/analysis/rcps`        | Resource limit input. Algorithm selector (Burgess / Min Moment). D3 stacked before/after histogram. CPM vs. RCPS Gantt comparison. Heuristic walkthrough in Learn Mode.                                 |
| 3.5 | **Monte Carlo view** _(PG only)_ | `POST /api/web/analysis/monte-carlo` | Config (trials default 5000, seed). D3 duration histogram with P50/P80/P90 markers. Cost histogram. CP frequency table. P(T ≤ X) lookup. Learn Mode: progressive histogram animation via RxJS interval. |

**Deliverable:** All 8 UG+PG analysis tabs functional. Feature parity with desktop app analysis views.

---

#### Sprint 4 — PG-Only Modules + Educational Layer

**Goal:** Complete the 3 remaining PG structural views and enrich Learn Mode with typeset formulas and live walkthroughs.

| #   | Task                            | What to do                                                                                                                                                                                                                                                                                          |
| --- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 4.1 | **WBS view**                    | D3 Walker tree layout (TypeScript port of `wbs_layout_edu.py`). Right-click context menu (Add Child / Edit / Delete / Expand-Collapse). Cost rollup panel (sum cost, max duration, weighted-avg progress). Undo stack (20 steps). Export PNG/JSON. Learn Mode: 100% rule, decomposition principles. |
| 4.2 | **SWOT view**                   | 2×2 Angular Material grid. Auto-extract entries from `riskRegister` signal (high-exposure risks → Threats) and `evmKpis` signal (CPI < 0.95 → Weakness). Manual add/edit via dialog. Export matrix PNG.                                                                                             |
| 4.3 | **PESTEL view**                 | 6-category editor. Factor table with impact × probability scoring. "Create Risk" button pushes factor to `riskRegister` signal. Export CSV.                                                                                                                                                         |
| 4.4 | **KaTeX formulas**              | Install `katex` (npm). Update `FormulaDisplayComponent` to render KaTeX. Apply to: Dashboard KPI tooltips, PERT walkthrough, CPM step formulas, EVM worked solution. Replace all inline HTML formula strings.                                                                                       |
| 4.5 | **Worked solution integration** | Wire `StepWalkthroughComponent` to live data: `/api/web/analysis/steps/cpm`, `/api/web/analysis/steps/pert`, `/api/web/analysis/steps/evm`. Each step maps to `CalculationStep`: `{ title, formula, substitution, result, explanation }`.                                                           |
| 4.6 | **Glossary tooltips**           | `ExplainerTooltipComponent` on all KPI card labels, chart axes, and input column headers. Content from centralized `explanations.const.ts`. Shown only in Learn Mode (`*appLearnMode` wraps them).                                                                                                  |

**Deliverable:** All 13 views functional. Learn Mode has typeset formulas and live walkthroughs for CPM, PERT, and EVM.

---

#### Sprint 5 — Production Hardening

**Goal:** Responsive, accessible, exportable, and robust for classroom use.

| #   | Task                     | What to do                                                                                                                                                                                                                    |
| --- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5.1 | **Responsive design**    | `ResizeObserver` in all SVG chart components (network, gantt, S-curve, histograms, bell curve). Breakpoints: `≤768px` sidebar collapses to icon strip; `≤480px` bottom tab bar (mobile). All data tables scroll horizontally. |
| 5.2 | **Accessibility**        | `role="img"` + `aria-label` on all SVG charts. `aria-live="polite"` on all result regions. Keyboard navigation (Tab/Enter on chart elements). WCAG AA contrast on all text. `aria-valuenow` on KPI cards for screen readers.  |
| 5.3 | **Save / Load / Export** | "Save" → download `.pmproj` JSON (all store state). "Load" → upload `.pmproj` → populate all signals. Chart PNG (html2canvas). PDF report (jsPDF). CSV/Excel table export.                                                    |
| 5.4 | **Error boundaries**     | Wrap each lazy-loaded route: on crash show "Something went wrong" + retry button instead of blank screen. Log to `POST /api/web/telemetry/error` (append-to-file).                                                            |
| 5.5 | **Performance**          | `@defer` blocks for heavy chart components. `trackBy` on all `@for` loops. Self-host Roboto + Material Icons (remove CDN dependency). Lazy-load D3 only in views that use it.                                                 |
| 5.6 | **Cypress E2E**          | Flow 1: Load sample → CPM → Network step-through → Gantt cross-highlight. Flow 2: EVM → verify CPI/SPI values. Flow 3: Monte Carlo → P50/P80/P90 visible. Flow 4: UG → navigate `/rcps` → redirect + toast.                   |
| 5.7 | **CI/CD finalization**   | Auto-deploy to Render on `production` branch push. Add Cypress job to GitHub Actions. README deployment badge.                                                                                                                |

**Deliverable:** Production-ready, accessible, responsive, exportable. Classroom-ready.

---

### 18.11 Sprint Summary

| Sprint   | Focus                                                                                      | Dependencies | Parallelizable within sprint                     |
| -------- | ------------------------------------------------------------------------------------------ | ------------ | ------------------------------------------------ |
| Sprint 0 | Foundation hardening (persistence, interceptors, error handler, effect cleanup, demos fix) | —            | All 6 tasks are independent                      |
| Sprint 1 | Deploy MVP (multi-stage Dockerfile, FastAPI static serving, render.yaml update)            | Sprint 0     | None (sequential deploy steps)                   |
| Sprint 2 | CI/CD + unit tests + rate limiting                                                         | Sprint 1     | All 5 tasks are independent                      |
| Sprint 3 | Advanced analysis views (EVM, Crashing, Risk, RCPS, Monte Carlo)                           | Sprint 2     | All 5 views are mutually independent             |
| Sprint 4 | PG modules + Educational Layer (WBS, SWOT, PESTEL, KaTeX, walkthroughs)                    | Sprint 3     | 4.1/4.2/4.3 independent; 4.4/4.5/4.6 independent |
| Sprint 5 | Production hardening (responsive, a11y, save/export, error bounds, Cypress)                | Sprint 4     | All 7 tasks are independent                      |

**Sprint dependency chain:**

```
Sprint 0 ──→ Sprint 1 ──→ Sprint 2 ──→ Sprint 3 ──→ Sprint 4 ──→ Sprint 5
(harden)     (deploy)     (CI/test)    (features)   (features)   (polish)
```

**Why this order vs. the original 18.1–18.7 phases:**

- **Sprint 0 before Sprint 1:** Without `localStorage`, data is lost on every Render restart. Without the `_DEMOS_DIR` fix, sample loading breaks immediately after deploy.
- **Sprint 1 before Sprint 2:** CI must have a passing build to validate.
- **Sprint 2 before Sprint 3:** Adding 8 views without tests creates regression debt that compounds with every new view.
- **Sprint 3 before Sprint 4:** WBS / SWOT / PESTEL reference analysis results (risks, EVM KPIs) that must exist before they can auto-populate.
- **Sprint 5 last:** Responsive + a11y work touches every chart — more efficient once all views are complete.

**Original phases 18.1–18.3 are complete.** The original 18.4–18.7 have been re-ordered into Sprints 3–5, with new Sprints 0–2 inserted to address gaps found in the production-readiness audit.

---

### 18.12 Key Decisions

| #   | Decision                 | Answer                                        | Reasoning                                                                                                                                                                                                                                                                     |
| --- | ------------------------ | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Framework                | Angular 17+                                   | Form-heavy app, structured modules, RxJS streaming, DI services, Angular Material CDK. See Section 18.1.                                                                                                                                                                      |
| 2   | Product direction        | Educational only                              | All `_edu` modules already built. Market gap. Focus wins over hybrid.                                                                                                                                                                                                         |
| 3   | Default mode             | Learn Mode ON                                 | Education is the product. Clean View is secondary for users who already understand the concepts.                                                                                                                                                                              |
| 4   | State management         | Angular Signals only                          | NgRx ComponentStore was originally planned but actual implementation uses pure signals. All state in `project.store.ts` fits cleanly as flat `signal()` + `computed()`. Simpler, no extra dependency.                                                                         |
| 5   | Chart libraries          | D3.js + pure SVG                              | ngx-charts was originally planned for standard charts, but actual implementation uses pure SVG (Gantt) and D3 (Network). Remaining charts (EVM S-curve, Monte Carlo histograms, cost curves) will also use D3/SVG for consistency and full control. No ngx-charts dependency. |
| 6   | Network layout           | Sugiyama hierarchical                         | TypeScript port of existing `utils/network_layout.py`. Deterministic, readable, consistent with desktop app.                                                                                                                                                                  |
| 7   | Gantt implementation     | Custom SVG                                    | Full control over float extensions, dependency arrows, tracking overlay, educational annotations. No library supports Learn Mode overlays.                                                                                                                                    |
| 8   | Backend                  | Reuse existing FastAPI + Python engines       | All 15 engines are production-ready. No rewrite. API layer is thin wrappers around existing engine calls.                                                                                                                                                                     |
| 9   | Auth                     | None for V1                                   | Single-user educational tool. No login required.                                                                                                                                                                                                                              |
| 10  | Deployment               | Docker Compose (Nginx + FastAPI + PostgreSQL) | Matches existing `docker-compose.yml` and `render.yaml`.                                                                                                                                                                                                                      |
| 11  | UG/PG gating             | Route guard + sidebar badge                   | PG features hidden from UG at nav level. Route guard prevents direct URL access. Toast guides user to toggle level.                                                                                                                                                           |
| 12  | Step-through data source | Backend computes steps, frontend renders      | `step_generators_edu.py` already has logic. Extend to return structured `CalculationStep[]` via new `/analysis/steps/*` endpoints. Single source of truth for calculation logic — no duplication in TypeScript.                                                               |
| 13  | WBS layout               | Walker's algorithm (D3 port)                  | Existing Python implementation in `wbs_layout_edu.py`. Port to D3/TypeScript for consistent rendering. Walker's handles variable-width rectangles correctly.                                                                                                                  |
| 14  | Accessibility standard   | WCAG 2.1 AA                                   | Educational tool used by diverse student populations. Color-blind safe + keyboard nav + screen reader.                                                                                                                                                                        |
| 15  | Save format              | `.pmproj` JSON                                | Consistent with desktop app. All state (activities, EVM, risks, WBS, SWOT, PESTEL) in one file. Desktop app can open web-saved files and vice versa.                                                                                                                          |
| 16  | State persistence        | `localStorage` (auto-save, Sprint 0)          | Auto-save all store signals to `localStorage` on change (debounce 1s), restore on boot. Sprint 5 adds file-based save/load. `localStorage` is the safety net — without it, a browser refresh loses all entered data before file save/load is built.                           |

---

## Phase 19 — Pre-Merge Fixes & Shipping (Post Sprint 5)

> **Goal:** Fix all bugs and gaps discovered during Sprint 5 review, then ship web v1.0.0.
> **Date started:** March 24, 2026
> **Branch:** `feat/web-v1` (current)
> **Dependencies:** All Sprints 0–5 complete (28/28 tests, clean production build)

### 19.0 Critique of Sprint 5 Deliverables

Sprint 5 claimed "production hardening" but review uncovered several real gaps:

1. **Telemetry 404 loop:** `GlobalErrorHandler` POSTs to `/api/web/telemetry/error`, but the backend has no such route. In production, every unhandled error fires a 404, which the `errorInterceptor` catches and shows a _second_ "HTTP 404" snackbar to the user.
2. **No input validation on `.pmproj` load:** `ProjectIOService.load()` does `JSON.parse() as PMProject` — a compile-time cast with zero runtime validation. Any JSON file with a `.pmproj` extension is blindly spread into all 16 global signals. No `version` field check, no type guards.
3. **Persistence asymmetry:** `PersistenceService` (localStorage) saves 9 signals. `ProjectIOService` (file save/load) saves 16 signals (adds all analysis results). A browser refresh after loading a `.pmproj` silently loses all computed analysis results — confusing for users.
4. **CI E2E dependencies missing:** `angular-e2e` job uses `npx http-server` and `npx wait-on` but neither is in `devDependencies`. `npx` downloads them at runtime — nondeterministic, adds latency, may fail behind CI network constraints.
5. **Deploy job swallows failures:** `deploy-render` curl uses `|| true`, making the job always green even if the secret is empty, Render is down, or the hook URL is wrong. No feedback to developer.
6. **Cypress specs are routing-only:** All 4 E2E specs only test navigation and component existence — no actual user flows (add activities, run analysis, verify results). Honestly scoped as "smoke + routing tests", not true E2E.
7. **No security headers:** FastAPI serves the SPA with no `Content-Security-Policy`, `X-Frame-Options`, or `Strict-Transport-Security` headers.
8. **No bundle-size tracking:** No Angular budgets in `angular.json`, no Lighthouse CI gate.
9. **`render.yaml` branch mismatch:** Still points to `feat/web-v1` instead of `production`.
10. **`package.json` version at 0.0.0:** Never bumped for release.

### 19.1 Pre-Merge Fix Tasks

| #    | Task                                          | Files Changed                                     | What to Do                                                                                                                                                                                 | Status  |
| ---- | --------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 19.1 | **Add telemetry sink endpoint**               | `src/pmhelper/server/api/routes/web.py`           | Add `@router.post("/telemetry/error", status_code=204)` that logs the payload and returns no content. Prevents the 404 → snackbar loop.                                                    | ✅ Done |
| 19.2 | **Runtime validation on `.pmproj` load**      | `web/src/app/core/services/project-io.service.ts` | Add `isValidProject()` guard: check `version === 1`, `activities` is array, `viewMode`/`academicLevel` are valid literals. Reject with user-facing "Incompatible file" message on failure. | ✅ Done |
| 19.3 | **Add `http-server` + `wait-on` to devDeps**  | `web/package.json`                                | Add `"http-server": "^14.1.1"` and `"wait-on": "^8.0.0"` to `devDependencies`. Ensures `npm ci` installs them deterministically for CI E2E job.                                            | ✅ Done |
| 19.4 | **Fix `deploy-render` curl failure handling** | `.github/workflows/ci-cd.yml`                     | Remove `\|\| true`. Add `--fail` to curl. Deploy failures now surface as red CI jobs.                                                                                                      | ✅ Done |
| 19.5 | **Bump `web/package.json` to `1.0.0`**        | `web/package.json`                                | Change `"version": "0.0.0"` to `"1.0.0"`.                                                                                                                                                  | ✅ Done |

### 19.2 Ship Tasks (After Fixes)

| #    | Task                                   | What to Do                                                                                                   | Status     |
| ---- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------- |
| 19.6 | `npm install` in `web/`                | Updates `package-lock.json` with Cypress + http-server + wait-on.                                            | ✅ Done    |
| 19.7 | Create PR `feat/web-v1` → `production` | 156+ files. Title: "feat: PMHelper Edu Web v1.0.0". Include summary of Sprints 0–5.                          | ✅ Done (PR #3) |
| 19.8 | Set `RENDER_DEPLOY_HOOK_URL` secret    | GitHub → Settings → Secrets → Actions. Get value from Render dashboard → service → Settings → Deploy Hook.   | ➡️ Deferred to V2 |
| 19.9 | Wait for CI green, merge PR            | All 7 CI jobs must pass (test, lint, angular-lint, angular-build, angular-test, angular-e2e, build-package). | ➡️ Deferred to V2 |

### 19.3 Post-Merge Tasks

| #     | Task                              | What to Do                                                                                                                   | Status     |
| ----- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------- |
| 19.10 | Update `render.yaml` branch       | Commit directly to `production`: change `branch: feat/web-v1` → `branch: production`. OR set the branch in Render dashboard. | ➡️ Deferred to V2 |
| 19.11 | Verify live deploy                | Hit `/health`, navigate core routes, test PG guard redirect, verify sample data loads.                                       | ➡️ Deferred to V2 |
| 19.12 | Document rollback plan            | Add to README: "To roll back, revert the last merge on `production` and push."                                               | ➡️ Deferred to V2 |
| 19.13 | Run 30-item UI smoke test         | Execute checklist from `UI_SMOKE_TEST_CHECKLIST_EDU.md` against live URL.                                                    | ➡️ Deferred to V2 |
| 19.14 | Update CHANGELOG.md               | Add `[1.0.0-web]` entry covering all web app features (Sprints 0–5).                                                         | ➡️ Deferred to V2 |
| 19.15 | Tag `v1.0.0-web` + GitHub Release | Create annotated tag, write release notes, attach any build artifacts.                                                       | ➡️ Deferred to V2 |

### 19.4 Post-Ship Hardening (Track D — Can Be Deferred)

| #     | Task                                       | What to Do                                                                                                                                                                   | Priority |
| ----- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 19.16 | Add CSP `Report-Only` header               | Add middleware to `main.py` that sets `Content-Security-Policy-Report-Only`. Will surface violations without breaking the inline font `onload`. Tighten to enforced in v1.1. | P2       |
| 19.17 | Align `PersistenceService` signal coverage | Either persist all 16 signals (so browser refresh keeps analysis results) or document that refresh only keeps input data.                                                    | P2       |
| 19.18 | Add Angular budgets to `angular.json`      | Set `maximumWarning: 500kb`, `maximumError: 1mb` for initial bundle. Prevents accidental bundle bloat on future PRs.                                                         | P3       |
| 19.19 | True E2E user-flow Cypress spec            | Add spec: type 3 activities → click Analyze → verify Network canvas renders nodes → verify Gantt has bars.                                                                   | P3       |
| 19.20 | Lighthouse CI gate in GitHub Actions       | Add Lighthouse CI job with performance budget assertions.                                                                                                                    | P3       |

### 19.5 Dependency Graph

```
19.1–19.5 (parallel pre-merge fixes on feat/web-v1)
  └──→ 19.6 (npm install)
        └──→ 19.7 (create PR)  +  19.8 (set secret — parallel)
              └──→ 19.9 (CI green + merge)
                    └──→ 19.10 (update render.yaml branch)
                          └──→ 19.11 (verify live) → 19.12 (doc rollback)
                                └──→ 19.13–19.15 (parallel post-ship)
                                      └──→ 19.16–19.20 (deferred hardening)
```

---

## V1 Closeout — April 5, 2026

### Final Metrics

| Metric | Value |
|--------|-------|
| Desktop Python tests | 797+ passing |
| Angular unit tests | 28/28 passing |
| Phases completed (desktop) | 20/20 (code-complete) |
| Web sprints completed | 5/5 + Phase 19 pre-merge fixes |
| Total features delivered | ~50 (per FEATURES_LIST_EDU.md) |
| Lines of Python (src/) | ~25,000 |
| Lines of TypeScript (web/) | ~12,000 |
| Key decisions documented | 12 |
| Calendar time (actual) | March 8 – March 25, 2026 (~2.5 weeks) |

### Items Deferred to V2

| ID | Item | Type | Reason |
|----|------|------|--------|
| 10.3 | PyInstaller `--onedir` test | Manual QA | Requires clean Windows machine without Python |
| 10.4 | 30-item UI smoke test | Manual QA | Manual checklist execution |
| 17.6 | 600-task interactive network test | Manual QA | Manual browser validation |
| 19.8–19.9 | Render deploy secret + PR merge | Ops | Web shipping pipeline |
| 19.10–19.15 | Post-merge deployment tasks | Ops | Blocked on PR merge |
| 19.16–19.20 | Web hardening (CSP, budgets, E2E) | Tech debt | P2/P3 priority |

### Lessons Learned

1. **Event-driven > polling** — Phase 12 stepper proved that calling `refresh()` from 6 mutation points is cleaner than `root.after()` polling.
2. **Shared layout engines pay off** — Phase 14A's extraction saved 3× code duplication across Network, PERT, and Crashing tabs.
3. **O(V+E) matters** — Phase 15's `all_simple_paths` → `dag_longest_path` fix was the difference between "app crashes" and "600 tasks in <1s."
4. **Transitive reduction is essential** — Phase 16 showed that naive predecessor generation creates thousands of redundant edges that explode Sugiyama layout.
5. **Angular signals + standalone components** — The web app's signal-based state proved simpler than NgRx for this scale.
6. **Pre-merge code review catches real bugs** — Phase 19's 10-issue critique found the telemetry 404 loop and missing input validation before users ever saw them.
7. **Manual QA is always the last thing done** — Tasks 10.3, 10.4, 17.6 remain because automated tests covered the critical paths. Schedule manual QA explicitly in V2.

### V1 Declaration

**V1 is CODE-COMPLETE.** All planned features are implemented and tested. The desktop app is fully functional. The web app is built with a PR ready to merge. Remaining work is manual QA and deployment ops, carried forward to V2 Phase 0.

→ **See [EDU_V2_Plan.md](EDU_V2_Plan.md) for the next version.**
