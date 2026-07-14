# WBS Dictionary

## PMHelper_Edu Development Project

| Field             | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| **Document ID**   | PMHE-2025-WD-001                                          |
| **Project Code**  | PMHE-2025                                                 |
| **Version**       | 1.1 — Active                                              |
| **Prepared by**   | Ahmed Samir Khalil, PMP                                   |
| **Approved by**   | Dr. Karim Naguib                                          |
| **Organization**  | EduTech Dynamics                                          |
| **Baseline Date** | 2025-10-15                                                |
| **Last Updated**  | 2026-07-09                                                |
| **Companion WBS** | PMHE-2025-SS-001; data/demos/v2/pmhelper_edu_ref_wbs.json |

---

## Purpose

The WBS Dictionary provides the management definition for each work package in the WBS.
It defines scope boundaries, resource assignments, dependencies, assumptions, and
acceptance criteria at the work package level. It is the contract between the Project
Manager and the work package owner.

**Entry format per work package:**

| Field                | Content                                       |
| -------------------- | --------------------------------------------- |
| WBS Code + Name      | From WBS                                      |
| BAC / Duration       | Budget and estimated effort                   |
| Responsible Party    | Who delivers this work package                |
| Resources            | Specific people and percentage allocation     |
| Predecessor WPs      | WBS codes that must finish before this starts |
| Scope Description    | What is included and excluded                 |
| Acceptance Criteria  | How we know this WP is complete               |
| Assumptions          | What must be true for the estimate to hold    |
| Output / Deliverable | The tangible output of this work package      |

---

## 1.1 — Project Management

### WBS 1.1.1 — Project Initiation Documents

| Field                   | Detail                                                                                                                                                                                                                        |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 5,000                                                                                                                                                                                                                     | **Duration** | 10 WD |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                                                       |
| **Resources**           | PM (80%), Sponsor (20% review)                                                                                                                                                                                                |
| **Predecessor WPs**     | None (first WP)                                                                                                                                                                                                               |
| **Scope**               | Produce signed Project Charter (PMHE-2025-PC-001), Stakeholder Register v1.0 (PMHE-2025-SR-001), Benefits Management Plan v1.0 (PMHE-2025-BMP-001). Excludes: full planning documents (in 1.1.2), team onboarding (in 1.1.4). |
| **Acceptance Criteria** | Sponsor signature on charter; all three documents in version-controlled repository; charter date stamped 2025-09-01                                                                                                           |
| **Assumptions**         | Sponsor available for review during week 1; charter template available                                                                                                                                                        |
| **Output**              | PMHE-2025-PC-001 (signed), PMHE-2025-SR-001 v1.0, PMHE-2025-BMP-001 v1.0                                                                                                                                                      |

---

### WBS 1.1.2 — Project Planning Documents

| Field                   | Detail                                                                                                                                                                                                                                                                                  |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 20,000                                                                                                                                                                                                                                                                              | **Duration** | 20 WD |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                                                                                                                 |
| **Resources**           | PM (70%), Lead Dev (20% input), Technical Advisor (10% educational review)                                                                                                                                                                                                              |
| **Predecessor WPs**     | 1.1.1 (charter authorises planning), 1.2.1 (requirements needed before planning)                                                                                                                                                                                                        |
| **Scope**               | Requirements Traceability Matrix (PMHE-2025-RTM-001), WBS and Schedule Baseline (PMHE-2025-SS-001), Cost Baseline (PMHE-2025-CB-001), Risk Management Plan (part of PMHE-2025-RR-001), Communications Plan (PMHE-2025-CP-001). Excludes: reference sample project documents (in 1.7.6). |
| **Acceptance Criteria** | RTM covers all charter requirements; WBS sums to BAC; schedule has critical path identified; risk plan approved by sponsor                                                                                                                                                              |
| **Assumptions**         | Architecture milestone (M2) must complete before schedule can be baselined                                                                                                                                                                                                              |
| **Output**              | PMHE-2025-RTM-001 v1.0, PMHE-2025-SS-001 v1.0, PMHE-2025-CB-001 v1.0                                                                                                                                                                                                                    |

---

### WBS 1.1.3 — Project Management Plan (Integrated)

| Field                   | Detail                                                                                                                                                                                                                                        |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 15,000                                                                                                                                                                                                                                    | **Duration** | 15 WD |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                                                                       |
| **Resources**           | PM (100%)                                                                                                                                                                                                                                     |
| **Predecessor WPs**     | 1.1.2 (subsidiary plans must exist)                                                                                                                                                                                                           |
| **Scope**               | Single integrated project management plan combining all subsidiary plans. Includes: scope baseline, schedule baseline, cost baseline, quality plan, communications plan, risk management plan, procurement plan, stakeholder engagement plan. |
| **Acceptance Criteria** | All subsidiary plans referenced; sponsor approval signature; no conflicts between plans                                                                                                                                                       |
| **Assumptions**         | Subsidiary plans are stable before integration                                                                                                                                                                                                |
| **Output**              | Integrated Project Management Plan (internal document; not a separate public file)                                                                                                                                                            |

---

### WBS 1.1.4 — Team and Stakeholder Management

| Field                   | Detail                                                                                                                                                                                               |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ---------------- |
| **BAC**                 | EGP 30,000                                                                                                                                                                                           | **Duration** | 200 WD (ongoing) |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                              |
| **Resources**           | PM (30% allocation × 13 months)                                                                                                                                                                      |
| **Predecessor WPs**     | 1.1.1 (stakeholder register identifies who to manage)                                                                                                                                                |
| **Scope**               | Daily standups, sprint reviews (bi-weekly), monthly technical advisor sessions, faculty partner engagement meetings, stakeholder engagement assessment updates. Excludes: status reports (in 1.1.5). |
| **Acceptance Criteria** | Sprint reviews held bi-weekly throughout project; Technical Advisor session held monthly; stakeholder engagement assessment updated at each milestone                                                |
| **Assumptions**         | Team members remain available at committed allocations; faculty partners respond to engagement requests within 5 business days                                                                       |
| **Output**              | Meeting minutes (GitHub wiki); stakeholder engagement assessment updates (PMHE-2025-SR-001 revision history)                                                                                         |

---

### WBS 1.1.5 — Status Reporting and Communications

| Field                   | Detail                                                                                                                                                                |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ---------------- |
| **BAC**                 | EGP 20,000                                                                                                                                                            | **Duration** | 200 WD (ongoing) |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                               |
| **Resources**           | PM (15% of working time)                                                                                                                                              |
| **Predecessor WPs**     | 1.1.3 (communications plan defines reporting requirements)                                                                                                            |
| **Scope**               | Weekly financial status email to sponsor; monthly formal status report; milestone completion reports (8 total). EVM dashboard screenshot included in monthly reports. |
| **Acceptance Criteria** | 13 monthly status reports delivered; 8 milestone reports issued; no report more than 3 business days late                                                             |
| **Assumptions**         | EVM data available monthly for report preparation                                                                                                                     |
| **Output**              | 13 monthly status reports; 8 milestone reports                                                                                                                        |

---

### WBS 1.1.6 — Schedule and Cost Monitoring

| Field                   | Detail                                                                                                                                                                                                |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ---------------- |
| **BAC**                 | EGP 20,000                                                                                                                                                                                            | **Duration** | 200 WD (ongoing) |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                               |
| **Resources**           | PM (10% of working time)                                                                                                                                                                              |
| **Predecessor WPs**     | 1.1.3 (baselines must be established)                                                                                                                                                                 |
| **Scope**               | Monthly EVM calculations (EV, AC, PV, CPI, SPI, EAC, TCPI), schedule variance analysis, cost trend reporting, management reserve request preparation if needed. Excludes: risk monitoring (in 1.1.7). |
| **Acceptance Criteria** | EVM computed monthly against approved baselines; CPI and SPI trends documented; EAC forecast updated monthly                                                                                          |
| **Assumptions**         | Team reports actual hours/costs weekly; percent complete assessed honestly per work package                                                                                                           |
| **Output**              | Monthly EVM report section (embedded in status reports); cost forecast updates                                                                                                                        |

---

### WBS 1.1.7 — Risk and Change Monitoring

| Field                   | Detail                                                                                                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ---------------- |
| **BAC**                 | EGP 10,000                                                                                                                                                                                        | **Duration** | 200 WD (ongoing) |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                           |
| **Resources**           | PM (5% of working time); Lead Dev (review input)                                                                                                                                                  |
| **Predecessor WPs**     | 1.1.2 (risk register established)                                                                                                                                                                 |
| **Scope**               | Bi-weekly risk register review, probability/impact reassessment, new risk identification, change request processing and impact assessment. Excludes: day-to-day team issue resolution (informal). |
| **Acceptance Criteria** | Risk register reviewed bi-weekly (record in revision history); all change requests processed within 5 business days; change log maintained                                                        |
| **Assumptions**         | Team members surface risks proactively through daily standups                                                                                                                                     |
| **Output**              | Risk register revision history; change control log (PMHE-2025-CCL-001)                                                                                                                            |

---

### WBS 1.1.8 — Project Closure and Archive

| Field                   | Detail                                                                                                                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 10,000                                                                                                                                                                                                          | **Duration** | 30 WD |
| **Responsible**         | Ahmed Samir Khalil, PMP                                                                                                                                                                                             |
| **Resources**           | PM (60%), Sponsor (20% approval), Lead Dev (20% archive)                                                                                                                                                            |
| **Predecessor WPs**     | ALL other WPs (closure cannot start until all deliverables accepted)                                                                                                                                                |
| **Scope**               | Final financial reconciliation (actual vs. budget); lessons learned register; project archive (GitHub tag v1.1.0-final); benefits baseline report (B4, B6, B8 measurements); formal sponsor sign-off; team release. |
| **Acceptance Criteria** | Sponsor sign-off on closure report; GitHub repository tagged; benefits baseline report delivered; team officially released                                                                                          |
| **Assumptions**         | All deliverables (D1–D8) accepted before closure begins                                                                                                                                                             |
| **Output**              | Closure Report (PMHE-2025-CR-001); Lessons Learned (PMHE-2025-LL-001); Benefits Baseline Report                                                                                                                     |

---

## 1.2 — Architecture and Infrastructure

### WBS 1.2.1 — Requirements Analysis and Documentation

| Field                   | Detail                                                                                                                                                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 15,000                                                                                                                                                                                                                      | **Duration** | 15 WD |
| **Responsible**         | Ahmed Samir Khalil (lead) + Omar Hassan (technical)                                                                                                                                                                             |
| **Resources**           | PM (50%), Lead Dev (40%), Technical Advisor (10%)                                                                                                                                                                               |
| **Predecessor WPs**     | 1.1.1 (charter defines scope boundary)                                                                                                                                                                                          |
| **Scope**               | Functional requirements (FR-001–FR-051), non-functional requirements (NFR-001–NFR-010), educational requirements (EDU-001–EDU-008), technical requirements (TR-001–TR-008). Review with Prof. Youssef for curriculum alignment. |
| **Acceptance Criteria** | All charter objectives mapped to at least one FR; all FRs reviewed by Technical Advisor; RTM v1.0 produced                                                                                                                      |
| **Assumptions**         | Charter approved before requirements analysis begins                                                                                                                                                                            |
| **Output**              | RTM v1.0 (PMHE-2025-RTM-001)                                                                                                                                                                                                    |

---

### WBS 1.2.2 — Module Architecture Design

| Field                   | Detail                                                                                                                                                                             |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 15,000                                                                                                                                                                         | **Duration** | 10 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                             |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                    |
| **Predecessor WPs**     | 1.2.1 (requirements must exist to design architecture)                                                                                                                             |
| **Scope**               | src/pmhelper/ directory structure, core/ vs gui/tabs/ separation, EduProjectState shared-state pattern, step generator pattern, module dependency map. Documented in DECISIONS.md. |
| **Acceptance Criteria** | Architecture diagram produced; all planned modules listed; no circular imports; existing code loads cleanly with new structure                                                     |
| **Assumptions**         | Python Tkinter confirmed as GUI framework (C4 constraint); no major changes to architecture once development begins                                                                |
| **Output**              | DECISIONS.md architecture section; module dependency diagram                                                                                                                       |

---

### WBS 1.2.3 — Data Model Design (.pmproj Schema)

| Field                   | Detail                                                                                                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ---- |
| **BAC**                 | EGP 12,000                                                                                                                                                                                        | **Duration** | 8 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                            |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                                   |
| **Predecessor WPs**     | 1.2.2 (architecture defines which data models are needed)                                                                                                                                         |
| **Scope**               | EVMTask, EVMPeriod, EVMProject, RiskRegister, Risk dataclasses with @dataclass + manual validation. .pmproj JSON schema v1 with schema version field. EduProjectState as central state container. |
| **Acceptance Criteria** | All dataclasses have to_dict()/from_dict() round-trip tests; schema version field present; manual validation raises meaningful errors                                                             |
| **Assumptions**         | Decisions #1–#7 (DECISIONS.md) are finalised before data model implementation                                                                                                                     |
| **Output**              | core/evm_models_edu.py, core/risk_register_edu.py, gui/edu_state.py                                                                                                                               |

---

### WBS 1.2.4 — GUI Architecture and Component Design

| Field                   | Detail                                                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- |
| **BAC**                 | EGP 8,000                                                                                                                                        | **Duration** | 5 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                           |
| **Resources**           | Lead Dev (100%)                                                                                                                                  |
| **Predecessor WPs**     | 1.2.2                                                                                                                                            |
| **Scope**               | Main window structure (MainWindowEdu), tab creation pattern, worked solution window design, scrollable Matplotlib frame, chart export framework. |
| **Acceptance Criteria** | Main window creates without error; tab stub pattern works; worked solution window opens and closes correctly                                     |
| **Output**              | gui/main_window_edu.py (skeleton); gui/widgets/ directory structure                                                                              |

---

### WBS 1.2.5 — Repository Setup

| Field                   | Detail                                                                                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---- |
| **BAC**                 | EGP 5,000                                                                                                                                                    | **Duration** | 3 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                       |
| **Resources**           | Lead Dev (100%)                                                                                                                                              |
| **Predecessor WPs**     | 1.1.1 (project code and naming confirmed)                                                                                                                    |
| **Scope**               | GitHub repository seifouda/PMhelper creation, initial commit, .gitignore, branching strategy (production/EDU_PROD/feat/\* pattern), contributor permissions. |
| **Acceptance Criteria** | Repository accessible; initial commit present; branching policy documented in README                                                                         |
| **Output**              | GitHub repository with initial structure                                                                                                                     |

---

### WBS 1.2.6 — CI/CD Pipeline Configuration

| Field                   | Detail                                                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ---- |
| **BAC**                 | EGP 5,000                                                                                                                                         | **Duration** | 5 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                            |
| **Resources**           | Lead Dev (100%)                                                                                                                                   |
| **Predecessor WPs**     | 1.2.5 (repository must exist); 1.8.1 (test plan defines what to run)                                                                              |
| **Scope**               | .github/workflows/ci-cd.yml: automated test run on push to production, build step, badge generation. GitHub Actions configuration for Python 3.8. |
| **Acceptance Criteria** | CI badge shows on README; pipeline runs tests successfully; failed test blocks merge                                                              |
| **Output**              | .github/workflows/ci-cd.yml; CI/CD badge on README.md                                                                                             |

---

## 1.3 — Desktop Application V1 (Selected Key Entries)

_All 1.3.x WPs are 100% complete. Key dictionary entries provided for educational value._

### WBS 1.3.2 — EVM Engine and 16-KPI Module

| Field                   | Detail                                                                                                                                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 30,000                                                                                                                                                                                                              | **Duration** | 20 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                                                  |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                                                         |
| **Predecessor WPs**     | 1.2.3 (EVMProject data model), 1.3.1 (CPM engine for cpm_task_id linking)                                                                                                                                               |
| **Scope**               | evm_calculations_edu.py: all 16 KPI pure functions (CV, SV, CPI, SPI, PC, PS, CR, EAC₁, EAC₂, EAC₃, VAC, TCPI), RAG threshold logic, step generator for EVM walkthrough. Excludes: Earned Schedule (FR-052 — deferred). |
| **Acceptance Criteria** | All 16 KPIs produce correct results per test suite; RAG codes match configured thresholds; TCPI edge case (BAC=AC) handled with clear error message                                                                     |
| **Assumptions**         | EVM formulas per PMBOK 6th Edition as reviewed by Prof. Youssef                                                                                                                                                         |
| **Output**              | core/evm_calculations_edu.py; test_evm.py (unit tests)                                                                                                                                                                  |

---

### WBS 1.3.3 — Risk Register and Monte Carlo Engine

| Field                   | Detail                                                                                                                                                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 25,000                                                                                                                                                                                                             | **Duration** | 18 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                                                 |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                                                        |
| **Predecessor WPs**     | 1.2.3 (Risk data model); 1.3.1 (CPM activities used by MC)                                                                                                                                                             |
| **Scope**               | risk_register_edu.py (CRUD, zone logic, response strategies V2), monte_carlo_edu.py (PERT-Beta sampling, threading.Thread + queue.Queue per Decision #4). N-trial configurable; P50/P80/P90 outputs; CP frequency map. |
| **Acceptance Criteria** | Monte Carlo with seed produces identical results on repeated runs; P50/P80/P90 values statistically valid for N=5000; threading does not block GUI event loop                                                          |
| **Assumptions**         | threading.Thread + queue.Queue model (Decision #4) is acceptable — no asyncio dependency                                                                                                                               |
| **Output**              | core/risk_register_edu.py; core/monte_carlo_edu.py; tests/test_risk.py                                                                                                                                                 |

---

## 1.4 — Desktop Application V2 (Selected Key Entries)

### WBS 1.4.1 — Tab Group Refactor and Infrastructure

| Field                   | Detail                                                                                                                                                                                                                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 25,000                                                                                                                                                                                                                                                                                          | **Duration** | 15 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                                                                                                                              |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                                                                                                                                     |
| **Predecessor WPs**     | 1.3.10 (V1 complete and tested — no regressions before refactor)                                                                                                                                                                                                                                    |
| **Scope**               | TabGroupNotebook widget (gui/widgets/tab_group_notebook.py), EducationalCalculatorTab abstract base (gui/widgets/educational_calculator_tab.py), DemoLoader utility (utils/demo_loader.py), main_window_edu.py refactored to use TabGroupNotebook. ALL 797 V1 tests must still pass after refactor. |
| **Acceptance Criteria** | 797 tests pass after refactor; all 18 V1 tabs accessible through new widget; PG-only tab show/hide still works; no regressions                                                                                                                                                                      |
| **Assumptions**         | The flat 18-tab ttk.Notebook can be replaced without changing any tab's internal code                                                                                                                                                                                                               |
| **Output**              | gui/widgets/tab_group_notebook.py; gui/widgets/educational_calculator_tab.py; utils/demo_loader.py; refactored main_window_edu.py                                                                                                                                                                   |

---

### WBS 1.4.6 — Risk Response Planning and AON/AOA Dual Network

| Field                   | Detail                                                                                                                                                                                                                                                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 30,000                                                                                                                                                                                                                                                                                                                                        | **Duration** | 18 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                                                                                                                                                                            |
| **Resources**           | Lead Dev (80%), Technical Advisor (20% review of risk response methodology)                                                                                                                                                                                                                                                                       |
| **Predecessor WPs**     | 1.4.1 (V2 infrastructure), 1.3.7 (existing risk tab as base)                                                                                                                                                                                                                                                                                      |
| **Scope**               | Extended risk_tab_edu.py with 4th sub-tab (Response Planning), aoa_network_builder.py (AOA algorithm with dummy activity detection), AON/AOA toggle in network_tab_edu.py. aoa_demo.json with ground-truth solutions. risk_assessment_demo.json (12 risks, all zones). Response strategies: Avoid/Transfer/Mitigate/Accept/Exploit/Share/Enhance. |
| **Acceptance Criteria** | AOA demo project produces correct critical path (duration 13); response strategies saved to .pmproj; residual probability/impact fields computable from inputs                                                                                                                                                                                    |
| **Assumptions**         | AOA algorithm uses event-based representation internally (not AON DiGraph); conversion handled in aoa_network_builder.py                                                                                                                                                                                                                          |
| **Output**              | core/aoa_network_builder.py; extended risk_register_edu.py; aoa_demo.json; risk_assessment_demo.json                                                                                                                                                                                                                                              |

---

## 1.5 — Web Application (Selected Key Entry)

### WBS 1.5.1 — FastAPI Backend and SQLAlchemy Database

| Field                   | Detail                                                                                                                                                                                                                                                                                                                |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 30,000                                                                                                                                                                                                                                                                                                            | **Duration** | 20 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                                                                                                                                                |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                                                                                                                                                       |
| **Predecessor WPs**     | 1.2.3 (data models), 1.3.1 (CPM engine — backend reuses core)                                                                                                                                                                                                                                                         |
| **Scope**               | server/ directory: FastAPI application, SQLAlchemy ORM with asyncpg (PostgreSQL production) and aiosqlite (SQLite development), API endpoints for CPM/PERT analysis, slowapi rate limiting (NFR-006 data protection), CORS configuration for Angular frontend. Docker configuration (Dockerfile, docker-compose.yml). |
| **Acceptance Criteria** | /health endpoint returns 200; CPM analysis endpoint returns correct results; SQLite works locally without PostgreSQL; CORS allows Angular dev server origin                                                                                                                                                           |
| **Assumptions**         | Render.com provides PostgreSQL on free/starter tier; no authentication required for MVP                                                                                                                                                                                                                               |
| **Output**              | server/ directory; Dockerfile; docker-compose.yml; render.yaml                                                                                                                                                                                                                                                        |

---

## 1.6 — Distribution and Packaging

### WBS 1.6.1 — PyInstaller Build and AV-Safe Manifest

| Field                   | Detail                                                                                                                                                                                                                                                                            |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 15,000                                                                                                                                                                                                                                                                        | **Duration** | 10 WD |
| **Responsible**         | Omar Hassan El-Rashidy                                                                                                                                                                                                                                                            |
| **Resources**           | Lead Dev (100%)                                                                                                                                                                                                                                                                   |
| **Predecessor WPs**     | 1.3.10, 1.4.8 (all desktop features complete before building)                                                                                                                                                                                                                     |
| **Scope**               | pmhelper_edu_production.spec (--onedir, AV-resistant), pmhelper_edu.manifest (requestedExecutionLevel=asInvoker), patch_scipy.py (scipy.stats.\_distn_infrastructure.py NameError fix — see repo memory), build_production.ps1 (8-step pipeline). Testing on clean Windows 10 VM. |
| **Acceptance Criteria** | Exe launches on clean Windows 10 VM without Python; all 24 tabs function; no admin rights required; passes Windows Defender scan without quarantine                                                                                                                               |
| **Assumptions**         | scipy patch resolves the known PyInstaller/scipy NameError (v2 patch: try/except NameError); no new library incompatibilities in final build                                                                                                                                      |
| **Output**              | dist/PMHelper_Edu/ directory; pmhelper_edu_production.spec; pmhelper_edu.manifest; patch_scipy.py; build_production.ps1                                                                                                                                                           |

---

## 1.7 — Educational Content

### WBS 1.7.6 — Reference Sample Project Document Set

| Field                   | Detail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 40,000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | **Duration** | 30 WD |
| **Responsible**         | Ahmed Samir Khalil (PM); Prof. Youssef Ibrahim Tawfik (review)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **Resources**           | PM (60%), Technical Advisor (30%), Jr Dev (10% JSON file creation)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Predecessor WPs**     | 1.3.10, 1.4.8 (all features must be known before documenting them); 1.8.1 (test plan establishes acceptance criteria)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Scope**               | 32 document pairs (Professional + Annotated Educational versions): Project Definition, Business Case, Benefits Plan, Charter (+ JSON), Stakeholder Register, RTM, Scope/WBS (+ JSON), WBS Dictionary, Schedule (CPM activities + O/M/P), Calendars, Resources, Cost Baseline (EVM data), Quality Plan, Communications Plan, Risk Register (.pmproj format), Procurement Register, RACI Matrix (.pmproj format), SWOT (.pmproj format), PESTEL (.pmproj format), Change Log, EVM Execution Snapshot, Monte Carlo Inputs, DPCI Assessment, Factor Scoring Scenario, Financial Analysis, EVM Dashboard Walkthrough, Lessons Learned, Closure Report, .pmproj master file, V2 demo supplements, Future Recommendations. |
| **Acceptance Criteria** | All 32 documents internally consistent (project code, BAC, team names, dates); EVM data produces CPI≈0.92, SPI≈1.02 when loaded; .pmproj file loads all 24 tabs correctly; Prof. Youssef signs off on educational content accuracy                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Assumptions**         | Reference project documents the PMHelper_Edu project itself (recursive); all application features stable before documentation begins                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **Output**              | docs/sample_project/ (32 pairs); data/demos/v2/ JSON supplements; complete .pmproj master file                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

---

### WBS 1.7.7 — User Documentation

| Field                   | Detail                                                                                                                                                                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----- |
| **BAC**                 | EGP 15,000                                                                                                                                                                                                                                             | **Duration** | 12 WD |
| **Responsible**         | Omar Hassan El-Rashidy (technical content); Ahmed Samir Khalil (PM sections)                                                                                                                                                                           |
| **Resources**           | Lead Dev (60%), PM (40%)                                                                                                                                                                                                                               |
| **Predecessor WPs**     | 1.6.1 (exe build — docs must cover actual distribution); 1.7.6 (reference project — quick-start references it)                                                                                                                                         |
| **Scope**               | README.md (PyPI + GitHub top-level, updated for v1.1.0 with full feature list), README_DEPLOYMENT.md (Render deployment instructions), Quick-Start Guide (2-page faculty onboarding), UI_SMOKE_TEST_CHECKLIST_EDU.md (30-item verification checklist). |
| **Acceptance Criteria** | README covers all installation methods; Quick-Start allows a new faculty user to load a demo project within 5 minutes; deployment guide tested against fresh Render account                                                                            |
| **Assumptions**         | All features stable before final documentation pass                                                                                                                                                                                                    |
| **Output**              | Updated README.md; README_DEPLOYMENT.md; QUICK_START_GUIDE.md; UI_SMOKE_TEST_CHECKLIST_EDU.md                                                                                                                                                          |

---

## 1.8 — Testing and QA

### WBS 1.8.2 — Unit Tests — Core Calculation Engines

| Field                   | Detail                                                                                                                                                                                                                                                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------- |
| **BAC**                 | EGP 50,000                                                                                                                                                                                                                                                                                                     | **Duration** | 30 WD (distributed across Phases 3–5) |
| **Responsible**         | Omar Hassan El-Rashidy (primary); Sara Mostafa (review)                                                                                                                                                                                                                                                        |
| **Resources**           | Lead Dev (70%), QA (30%)                                                                                                                                                                                                                                                                                       |
| **Predecessor WPs**     | 1.3.1–1.3.4 (engines must exist to test); 1.8.1 (test plan defines coverage)                                                                                                                                                                                                                                   |
| **Scope**               | Unit tests for all core/ calculation engines: CPM, PERT, EVM (16 KPIs), Risk, Monte Carlo, Crashing, Resource Leveling, Financial Analysis, Cost Estimation, Factor Scoring, Three-Point, AOA. Pure function tests with edge cases (zero values, negative floats, single-activity networks). pytest framework. |
| **Acceptance Criteria** | Every public function in core/ covered by at least one test; all edge cases from NFR-008 verified (±0.01 tolerance); no test failures on CI                                                                                                                                                                    |
| **Assumptions**         | Pure function architecture (TR-002) makes unit testing straightforward without mocking                                                                                                                                                                                                                         |
| **Output**              | tests/ directory: test_sprint1.py, test_evm.py, test_risk_register.py, test_three_point.py, test_optimization_fixes.py, and others                                                                                                                                                                             |

---

### WBS 1.8.5 — User Acceptance Testing — Faculty Partner Beta

| Field                   | Detail                                                                                                                                                                                                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| **BAC**                 | EGP 25,000                                                                                                                                                                                                                                                     | **Duration** | 15 WD |
| **Responsible**         | Ahmed Samir Khalil (coordination); Sara Mostafa (defect tracking)                                                                                                                                                                                              |
| **Resources**           | PM (50%), QA (30%), 2 Faculty Beta Partners (external, unpaid — SR-007)                                                                                                                                                                                        |
| **Predecessor WPs**     | 1.4.8 (all tabs must be functional), 1.7.4 (demo datasets needed for UAT)                                                                                                                                                                                      |
| **Scope**               | Execute UI_SMOKE_TEST_CHECKLIST_EDU.md with 2 faculty beta partners. Collect feedback via structured survey (SUS usability scale + PM-specific questions). Track defects in GitHub Issues. Verify O2 acceptance criterion (worked solutions in all calc tabs). |
| **Acceptance Criteria** | Both faculty partners complete smoke test without critical blockers; SUS score ≥ 68 (industry average); all critical defects resolved before QA sign-off                                                                                                       |
| **Assumptions**         | Faculty partners available for a 2-hour beta test session; they have Windows 10 computers available                                                                                                                                                            |
| **Output**              | UAT feedback report; GitHub Issues (defects from beta); revised smoke test checklist                                                                                                                                                                           |

---

## Summary: Work Package Cost Distribution

| WBS Area                | # WPs  | Total BAC         | Avg. WP Cost   |
| ----------------------- | ------ | ----------------- | -------------- |
| 1.1 Project Management  | 8      | EGP 130,000       | EGP 16,250     |
| 1.2 Architecture        | 6      | EGP 60,000        | EGP 10,000     |
| 1.3 Desktop V1          | 10     | EGP 280,000       | EGP 28,000     |
| 1.4 Desktop V2          | 8      | EGP 200,000       | EGP 25,000     |
| 1.5 Web Application     | 6      | EGP 120,000       | EGP 20,000     |
| 1.6 Distribution        | 4      | EGP 40,000        | EGP 10,000     |
| 1.7 Educational Content | 7      | EGP 140,000       | EGP 20,000     |
| 1.8 Testing and QA      | 6      | EGP 180,000       | EGP 30,000     |
| **TOTAL**               | **55** | **EGP 1,150,000** | **EGP 20,909** |

---

## Document Control

| Version | Date       | Author             | Change                                                                      |
| ------- | ---------- | ------------------ | --------------------------------------------------------------------------- |
| 1.0     | 2025-10-15 | Ahmed Samir Khalil | Baseline version                                                            |
| 1.1     | 2026-07-09 | Ahmed Samir Khalil | Updated scope descriptions to reflect V2 deliverables; 1.7.6 scope expanded |
