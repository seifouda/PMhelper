# Requirements Traceability Matrix

## PMHelper_Edu Development Project

| Field            | Value                                                   |
| ---------------- | ------------------------------------------------------- |
| **Document ID**  | PMHE-2025-RTM-001                                       |
| **Project Code** | PMHE-2025                                               |
| **Version**      | 1.2 — Active                                            |
| **Prepared by**  | Ahmed Samir Khalil, PMP                                 |
| **Reviewed by**  | Prof. Youssef Ibrahim Tawfik (Educational Requirements) |
| **Reviewed by**  | Omar Hassan El-Rashidy (Technical Requirements)         |
| **Approved by**  | Dr. Karim Naguib                                        |
| **Organization** | EduTech Dynamics                                        |
| **Date**         | 2025-10-15 (architecture milestone)                     |
| **Last Updated** | 2026-07-09                                              |

---

## 1. Purpose and Scope

This Requirements Traceability Matrix (RTM) provides complete forward and backward
traceability from business needs through to application features, deliverables, and
test cases. It ensures:

- Every feature implemented can be traced back to a stated requirement
- Every requirement can be traced forward to a deliverable and test case
- No requirements are missed (completeness)
- No features are built without a requirement (scope discipline)
- Change requests can assess which requirements are affected before approval

**Requirement hierarchy:**

```
Business Requirements (BR)
  └─ Stakeholder Requirements (SHR)
       └─ Functional Requirements (FR)
            ├─ Educational Requirements (EDU) ← cross-cutting
            ├─ Non-Functional Requirements (NFR)
            └─ Technical Requirements (TR)
                  └─ Acceptance Criteria (AC)
                        └─ Test Cases (TC) ← in test plan
                              └─ Deliverables (D1–D8)
                                    └─ Application Features (TAB-xx)
```

---

## 2. Requirement ID Conventions

| Prefix | Type                       | Example |
| ------ | -------------------------- | ------- |
| BR     | Business Requirement       | BR-001  |
| SHR    | Stakeholder Requirement    | SHR-001 |
| FR     | Functional Requirement     | FR-001  |
| EDU    | Educational Requirement    | EDU-001 |
| NFR    | Non-Functional Requirement | NFR-001 |
| TR     | Technical Requirement      | TR-001  |
| AC     | Acceptance Criterion       | AC-001  |

---

## 3. Business Requirements

Business requirements define _why_ the organisation is investing in the project.
They are stated from the perspective of the business problem to be solved.

| ID     | Business Requirement                                                                                            | Source                                                       | Priority     | Status               |
| ------ | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------ | -------------------- |
| BR-001 | Provide an integrated educational tool covering the complete quantitative PM curriculum in a single application | Business Case PMHE-2025-BC-001; SR-001 (Sponsor)             | Must Have    | ✅ Met               |
| BR-002 | Deliver the tool free of charge for individual users to maximise adoption without barrier                       | Business Case (open-source first-mover strategy); SR-001     | Must Have    | ✅ Met               |
| BR-003 | Generate institutional licensing revenue to achieve business case NPV targets                                   | Business Case PMHE-2025-BC-001; SR-001                       | Should Have  | ⚠️ Post-project (B1) |
| BR-004 | Establish EduTech Dynamics brand in MENA academic PM education within 12 months of release                      | Benefits Plan PMHE-2025-BMP-001 (B4); SR-001                 | Should Have  | ⚠️ Post-project      |
| BR-005 | Support both undergraduate (UG) and postgraduate (PG) learning levels within the same application               | SR-009 (UG Students); SR-010 (PG Students); SR-006 (Advisor) | Must Have    | ✅ Met               |
| BR-006 | Enable deployment in university computer labs without internet access                                           | SR-013 (IT Departments); C7 (Constraint)                     | Must Have    | ✅ Met               |
| BR-007 | Distribute via PyPI to integrate with academic Python environments                                              | SR-018 (PyPI); SR-009 (Students)                             | Should Have  | ✅ Met               |
| BR-008 | Build an internal technical capability that enables future EduTech Dynamics products                            | Benefits Plan (B6, B7); SR-001                               | Nice to Have | ✅ Met               |

---

## 4. Stakeholder Requirements

Stakeholder requirements capture the specific needs of each stakeholder group.
They elaborate the business requirements with the stakeholder's perspective.

| ID      | Stakeholder Requirement                                                                                              | Source Stakeholder                                  | Linked BR      | Priority     |
| ------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | -------------- | ------------ |
| SHR-001 | The application must teach CPM (forward/backward pass, float, critical path) with step-by-step worked solutions      | SR-009 (UG), SR-010 (PG), SR-006 (Advisor)          | BR-001, BR-005 | Must Have    |
| SHR-002 | The application must teach PERT three-point estimates with probability calculations                                  | SR-010 (PG), SR-011 (CAPM/PMP), SR-006              | BR-001, BR-005 | Must Have    |
| SHR-003 | The application must teach all 16 EVM KPIs with RAG colour coding and formula walkthroughs                           | SR-009, SR-010, SR-011, SR-006                      | BR-001, BR-005 | Must Have    |
| SHR-004 | The application must include risk analysis with probability-impact matrix and response planning                      | SR-010, SR-011, SR-006                              | BR-001, BR-005 | Must Have    |
| SHR-005 | The application must support Monte Carlo simulation with configurable trials and probability outputs                 | SR-010, SR-006                                      | BR-001, BR-005 | Must Have    |
| SHR-006 | The application must demonstrate project crashing (cost-time trade-off) with sequential algorithm                    | SR-009, SR-010, SR-006                              | BR-001         | Must Have    |
| SHR-007 | The application must demonstrate resource leveling with visual before/after histograms                               | SR-009, SR-010, SR-006                              | BR-001         | Must Have    |
| SHR-008 | The application must provide financial analysis (NPV, IRR, Payback, ROI, PI) as standalone calculator                | SR-010, SR-011, SR-006                              | BR-001         | Must Have    |
| SHR-009 | The application must support at least 5 cost estimation techniques with worked solutions                             | SR-010, SR-006                                      | BR-001         | Must Have    |
| SHR-010 | The application must include WBS creation and validation with rollup calculations                                    | SR-009, SR-010, SR-006                              | BR-001, BR-005 | Must Have    |
| SHR-011 | The application must include a RACI matrix editor with PM validation rules (one A per row, at least one R)           | SR-009, SR-010, SR-006                              | BR-001         | Must Have    |
| SHR-012 | The application must include SWOT and PESTEL analysis with weighted scoring                                          | SR-010, SR-006                                      | BR-001, BR-005 | Should Have  |
| SHR-013 | The application must include a Project Charter form with PDF export capability                                       | SR-007 (Faculty), SR-006                            | BR-001         | Should Have  |
| SHR-014 | Faculty must be able to load the application with a pre-built sample project to use as classroom demonstration       | SR-007 (Faculty), SR-008 (TAs)                      | BR-001, BR-003 | Must Have    |
| SHR-015 | Students must be able to try all calculations themselves before revealing the worked answer ("Try It Yourself" mode) | SR-009, SR-010                                      | BR-001, BR-005 | Must Have    |
| SHR-016 | The application must run completely offline — no internet connection required for any core feature                   | SR-013 (IT Depts), SR-009, C7                       | BR-006         | Must Have    |
| SHR-017 | The Windows executable must not require administrator rights to install or run                                       | SR-013 (IT Depts)                                   | BR-006         | Must Have    |
| SHR-018 | The application must allow UG/PG mode toggling at runtime to show or hide advanced features                          | SR-007 (Faculty), SR-009, SR-010                    | BR-005         | Must Have    |
| SHR-019 | All formulas must align with PMBOK 6th Edition terminology and CAPM/PMP exam standards                               | SR-011 (Candidates), SR-006 (Advisor), SR-017 (PMI) | BR-001         | Must Have    |
| SHR-020 | The web application must be accessible from a public URL without any installation                                    | SR-009, SR-010                                      | BR-001         | Should Have  |
| SHR-021 | Users must be able to save and reload their project data in a portable format                                        | SR-007 (Faculty), SR-009                            | BR-001         | Must Have    |
| SHR-022 | Faculty must be able to export charts as images for use in lecture slides                                            | SR-007 (Faculty)                                    | BR-001         | Should Have  |
| SHR-023 | The DPCI (Design Complexity Project Index) assessment must be available for advanced PM evaluation                   | SR-010, SR-006                                      | BR-001         | Nice to Have |
| SHR-024 | The application must provide a comprehensive reference sample project demonstrating all features                     | SR-007 (Faculty), SR-008 (TAs), SR-009, SR-010      | BR-001, BR-003 | Must Have    |

---

## 5. Functional Requirements

Functional requirements describe specific capabilities the system must have.

### 5.1 Schedule Analysis

| ID     | Functional Requirement                                                                    | Linked SHR | Deliverable | App Feature                     | Status         |
| ------ | ----------------------------------------------------------------------------------------- | ---------- | ----------- | ------------------------------- | -------------- |
| FR-001 | CPM forward pass: compute ES and EF for all activities                                    | SHR-001    | D1          | TAB-Network, TAB-Results        | ✅ Implemented |
| FR-002 | CPM backward pass: compute LS, LF, and Total Float                                        | SHR-001    | D1          | TAB-Network, TAB-Results        | ✅ Implemented |
| FR-003 | Identify all critical paths (zero-float paths) including multiple equal-length paths      | SHR-001    | D1          | TAB-Network                     | ✅ Implemented |
| FR-004 | PERT three-point estimates: compute Te, σ², σ per activity using PERT-Beta and Triangular | SHR-002    | D1          | TAB-ThreePoint                  | ✅ Implemented |
| FR-005 | PERT critical path: sum Te and σ² along critical path; compute path probability           | SHR-002    | D1          | TAB-ThreePoint, TAB-Probability | ✅ Implemented |
| FR-006 | Project crashing: sequential least-cost crashing with cost-time trade-off curve           | SHR-006    | D1          | TAB-Crashing                    | ✅ Implemented |
| FR-007 | AON and AOA network diagram rendering with critical path highlighting                     | SHR-001    | D1          | TAB-Network                     | ✅ Implemented |
| FR-008 | Interactive network viewer (vis.js) with zoom, pan, and hover tooltips                    | SHR-001    | D1          | TAB-Network                     | ✅ Implemented |
| FR-009 | Gantt chart with baseline vs. actual tracking (Tracking Gantt mode)                       | SHR-001    | D1          | TAB-Gantt                       | ✅ Implemented |

### 5.2 Earned Value Management

| ID     | Functional Requirement                                                                       | Linked SHR | Deliverable | App Feature            | Status         |
| ------ | -------------------------------------------------------------------------------------------- | ---------- | ----------- | ---------------------- | -------------- |
| FR-010 | Compute EV = Σ(budget × % complete) per task                                                 | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-011 | Compute CV = EV − AC and SV = EV − PV                                                        | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-012 | Compute CPI = EV/AC and SPI = EV/PV with zero-denominator guard                              | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-013 | Compute PC = EV/BAC × 100% and PS = AC/BAC × 100%                                            | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-014 | Compute Critical Ratio = CPI × SPI                                                           | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-015 | Compute three EAC variants: EAC₁ = AC+(BAC−EV), EAC₂ = BAC/CPI, EAC₃ = AC+(BAC−EV)/(CPI×SPI) | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-016 | Compute VAC = BAC − EAC and TCPI (toward BAC) = (BAC−EV)/(BAC−AC)                            | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-017 | Apply RAG thresholds to all KPI cards (configurable in AppConfig)                            | SHR-003    | D1          | TAB-EVM, TAB-Dashboard | ✅ Implemented |
| FR-018 | Render EV S-Curve (Matplotlib + Plotly/WebView2 toggle) from period data                     | SHR-003    | D1          | TAB-EVM                | ✅ Implemented |
| FR-019 | Project health dashboard: headline KPI strip + expandable mini-charts                        | SHR-003    | D1          | TAB-Dashboard          | ✅ Implemented |

### 5.3 Risk Analysis

| ID     | Functional Requirement                                                                                                | Linked SHR | Deliverable | App Feature | Status         |
| ------ | --------------------------------------------------------------------------------------------------------------------- | ---------- | ----------- | ----------- | -------------- |
| FR-020 | Risk register: CRUD for risks with id, name, probability, impact, category fields                                     | SHR-004    | D1          | TAB-Risk    | ✅ Implemented |
| FR-021 | Risk exposure: RE = p × I per risk; total exposure = sum                                                              | SHR-004    | D1          | TAB-Risk    | ✅ Implemented |
| FR-022 | 5×5 risk matrix heat-map with zone classification (Critical/High/Medium/Low)                                          | SHR-004    | D1          | TAB-Risk    | ✅ Implemented |
| FR-023 | Risk response planning: strategy (Avoid/Transfer/Mitigate/Accept/Exploit/Share/Enhance), owner, cost, residual scores | SHR-004    | D1          | TAB-Risk    | ✅ Implemented |
| FR-024 | Contingency reserve calculation: Σ(p×I) + management reserve                                                          | SHR-004    | D1          | TAB-Risk    | ✅ Implemented |

### 5.4 Simulation

| ID     | Functional Requirement                                                     | Linked SHR | Deliverable | App Feature     | Status         |
| ------ | -------------------------------------------------------------------------- | ---------- | ----------- | --------------- | -------------- |
| FR-025 | Monte Carlo simulation: N-trial (configurable) PERT-Beta duration sampling | SHR-005    | D1          | TAB-Probability | ✅ Implemented |
| FR-026 | Monte Carlo: output P50, P80, P90 project duration percentiles             | SHR-005    | D1          | TAB-Probability | ✅ Implemented |
| FR-027 | Monte Carlo: compute P(cost ≤ BAC) from simulated cost distribution        | SHR-005    | D1          | TAB-Probability | ✅ Implemented |
| FR-028 | Monte Carlo: identify probabilistic critical path frequencies per activity | SHR-005    | D1          | TAB-Probability | ✅ Implemented |

### 5.5 Resource Management

| ID     | Functional Requirement                                                                | Linked SHR | Deliverable | App Feature | Status         |
| ------ | ------------------------------------------------------------------------------------- | ---------- | ----------- | ----------- | -------------- |
| FR-029 | Resource leveling: Minimum Moment and Burgess algorithms with before/after histograms | SHR-007    | D1          | TAB-RCPS    | ✅ Implemented |
| FR-030 | RCPS: schedule activities under resource constraints, compute revised dates           | SHR-007    | D1          | TAB-RCPS    | ✅ Implemented |
| FR-031 | Resource leveling educational walkthrough: step-by-step explanation                   | SHR-007    | D1, D8      | TAB-RCPS    | ✅ Implemented |

### 5.6 Financial and Cost Analysis

| ID     | Functional Requirement                                                                                        | Linked SHR | Deliverable | App Feature   | Status         |
| ------ | ------------------------------------------------------------------------------------------------------------- | ---------- | ----------- | ------------- | -------------- |
| FR-032 | Financial analysis: Payback Period (simple and discounted), NPV, IRR, ROI, PI                                 | SHR-008    | D1          | TAB-Financial | ✅ Implemented |
| FR-033 | Cost estimation: Analogous, Bottom-Up, Work Element, Power Sizing, Unit Factor, Cost Capacity, Learning Curve | SHR-009    | D1          | TAB-CostEst   | ✅ Implemented |
| FR-034 | Factor scoring: 0-1 model, Unweighted Factor, Weighted Factor with normalised weights                         | SHR-008    | D1          | TAB-Financial | ✅ Implemented |

### 5.7 Project Planning Tools

| ID     | Functional Requirement                                                            | Linked SHR | Deliverable | App Feature | Status         |
| ------ | --------------------------------------------------------------------------------- | ---------- | ----------- | ----------- | -------------- |
| FR-035 | WBS tree editor: add/edit/delete nodes with rollup of duration, cost, progress    | SHR-010    | D1          | TAB-WBS     | ✅ Implemented |
| FR-036 | WBS validator: warn on missing names, negative values, out-of-range progress      | SHR-010    | D1          | TAB-WBS     | ✅ Implemented |
| FR-037 | RACI matrix editor: Task×Role and Deliverables×Department views                   | SHR-011    | D1          | TAB-RACI    | ✅ Implemented |
| FR-038 | RACI validation: flag rows missing A, rows missing R, columns with no assignments | SHR-011    | D1          | TAB-RACI    | ✅ Implemented |
| FR-039 | SWOT analysis: weighted factors with source linking, bubble chart visualisation   | SHR-012    | D1          | TAB-SWOT    | ✅ Implemented |
| FR-040 | PESTEL analysis: factors with impact score (−5 to +5), probability, timeframe     | SHR-012    | D1          | TAB-PESTEL  | ✅ Implemented |
| FR-041 | Project Charter form: all PMBOK-standard charter fields with PDF export           | SHR-013    | D1          | TAB-Charter | ✅ Implemented |
| FR-042 | DPCI (Design Complexity Project Index) assessment with scoring calculator         | SHR-023    | D1          | TAB-DPCI    | ✅ Implemented |

### 5.8 Data Management

| ID     | Functional Requirement                                                                   | Linked SHR       | Deliverable | App Feature   | Status         |
| ------ | ---------------------------------------------------------------------------------------- | ---------------- | ----------- | ------------- | -------------- |
| FR-043 | Save full project state to `.pmproj` JSON file (EVM, Risk, CPM, SWOT, PESTEL, WBS, RACI) | SHR-021          | D1          | Project I/O   | ✅ Implemented |
| FR-044 | Load `.pmproj` file and restore all tabs to saved state                                  | SHR-021          | D1          | Project I/O   | ✅ Implemented |
| FR-045 | Import CPM activities from CSV and Excel (.xlsx)                                         | SHR-021          | D1          | File Handlers | ✅ Implemented |
| FR-046 | Load pre-built demo projects: UG Small/Medium/Large, PG Small/Medium/Large               | SHR-014          | D1, D5      | Demo Loader   | ✅ Implemented |
| FR-047 | Load reference sample project as a selectable demo option ("PMHelper_Edu Reference")     | SHR-014, SHR-024 | D1, D5      | Demo Loader   | ⚠️ In Progress |
| FR-048 | Export all charts as PNG/PDF via batch export dialog                                     | SHR-022          | D1          | Chart Export  | ✅ Implemented |

### 5.9 Distribution

| ID     | Functional Requirement                                               | Linked SHR             | Deliverable | App Feature | Status         |
| ------ | -------------------------------------------------------------------- | ---------------------- | ----------- | ----------- | -------------- |
| FR-049 | Web application: Angular frontend with FastAPI backend on Render.com | SHR-020                | D2          | Web app     | ✅ Implemented |
| FR-050 | Windows standalone executable via PyInstaller (--onedir, AV-safe)    | SHR-016, SHR-017       | D3          | Executable  | ✅ Implemented |
| FR-051 | PyPI package: `pip install pmhelper` launches GUI                    | SHR-007 (PyPI), BR-007 | D4          | Package     | ✅ Implemented |

---

## 6. Educational Requirements

Educational requirements are cross-cutting — they apply to every calculation feature.

| ID      | Educational Requirement                                                                                | Linked FR        | Deliverable | Status                                                          |
| ------- | ------------------------------------------------------------------------------------------------------ | ---------------- | ----------- | --------------------------------------------------------------- |
| EDU-001 | Every calculation tab must provide a worked solution showing formula → substitution → result           | FR-001 to FR-034 | D8          | ✅ Implemented (step_generators_edu.py)                         |
| EDU-002 | "Try It Yourself" mode must allow students to attempt calculation before revealing the answer          | FR-001 to FR-034 | D8          | ✅ Implemented (worked_solution_window.py)                      |
| EDU-003 | UG mode must hide advanced features (PESTEL, DPCI, Monte Carlo P50/P90 EAC, Earned Schedule)           | SHR-018          | D1          | ✅ Implemented (\_PG_ONLY_TABS in main_window_edu.py)           |
| EDU-004 | All KPI formulas must match PMBOK 6th Edition notation and definitions                                 | SHR-019          | D1, D8      | ✅ Verified by Prof. Youssef                                    |
| EDU-005 | The reference sample project must link all calculations to a single coherent project narrative         | SHR-024          | D5          | ⚠️ In Progress (this document set)                              |
| EDU-006 | Foundations and PM Role reference tabs must provide curriculum-aligned lecture content                 | SHR-019          | D8          | ✅ Implemented                                                  |
| EDU-007 | All demo datasets must contain pre-computed "known solutions" for verification against student work    | SHR-014, SHR-015 | D5          | ✅ Implemented (data/demos/v2/)                                 |
| EDU-008 | The application must support PMBOK process group navigation: Initiating→Planning→Executing→M&C→Closing | SHR-019          | D1          | ⚠️ Partial (individual tabs; no integrated lifecycle navigator) |

---

## 7. Non-Functional Requirements

| ID      | Non-Functional Requirement                                                                                     | Category         | Linked SHR    | Deliverable | Status                        |
| ------- | -------------------------------------------------------------------------------------------------------------- | ---------------- | ------------- | ----------- | ----------------------------- |
| NFR-001 | Desktop application must load to ready state within 5 seconds on minimum spec hardware (4GB RAM, i5)           | Performance      | SHR-016       | D1          | ✅ Met                        |
| NFR-002 | CPM analysis on 600 activities must complete within 10 seconds                                                 | Performance      | FR-001–FR-003 | D1          | ✅ Met (large demo verified)  |
| NFR-003 | Monte Carlo with 5,000 trials must complete within 30 seconds on minimum spec                                  | Performance      | FR-025        | D1          | ✅ Met                        |
| NFR-004 | Application must operate with no internet connection for all features except web tab                           | Availability     | SHR-016, C7   | D1, D3      | ✅ Met                        |
| NFR-005 | Windows executable must not require administrator privileges to install or run                                 | Security         | SHR-017       | D3          | ✅ Met (--onedir, manifest)   |
| NFR-006 | Application must not transmit any user project data to external servers                                        | Security/Privacy | BR-002        | D1, D3      | ✅ Met (desktop = local only) |
| NFR-007 | Automated test suite must achieve ≥ 800 passing tests at delivery                                              | Quality          | All FR        | D6          | ✅ Met (845+ per commit msg)  |
| NFR-008 | All calculation results must match manually computed reference values within floating-point tolerance (± 0.01) | Accuracy         | All FR        | D1, D6      | ✅ Met (test suite validates) |
| NFR-009 | Application must be compatible with Python 3.8+ on Windows, macOS, and Linux                                   | Compatibility    | C4            | D1, D4      | ✅ Met                        |
| NFR-010 | Web application must achieve <3s Time-to-Interactive on 50Mbps connection                                      | Performance      | FR-049        | D2          | ✅ Met (Render deployment)    |

---

## 8. Technical Requirements

| ID     | Technical Requirement                                                                                                                                | Rationale                                                | Linked FR              | Status                                 |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------- | -------------------------------------- |
| TR-001 | GUI must be implemented in Python Tkinter (no Electron, no Qt, no web browser embedding except Plotly)                                               | C4 (constraint) + academic Python compatibility          | All FR                 | ✅ Implemented                         |
| TR-002 | Core calculation engines must be pure functions (no GUI, state, or I/O dependencies)                                                                 | Testability; reusability by FastAPI backend              | All FR                 | ✅ Implemented (core/ directory)       |
| TR-003 | Project state must be serialised to/from JSON only (no binary formats, no database)                                                                  | Portability; offline operation; version control friendly | FR-043, FR-044         | ✅ Implemented (.pmproj format)        |
| TR-004 | CI/CD pipeline must run all tests on every push to production branch via GitHub Actions                                                              | Quality gate; release safety                             | D6                     | ✅ Implemented (.github/workflows/)    |
| TR-005 | PyInstaller build must use --onedir mode with code signing manifest to reduce antivirus false positives                                              | SHR-017; SR-013 concern                                  | FR-050                 | ✅ Implemented (pmhelper_edu.manifest) |
| TR-006 | Interactive charts (S-Curve, Gantt, Network) must support both Matplotlib (offline) and Plotly/WebView2 (enhanced) rendering, with graceful fallback | NFR-004; UX enhancement                                  | FR-008, FR-009, FR-018 | ✅ Implemented                         |
| TR-007 | All EVM period data must use 0-based integer period indices (not calendar dates) with user-defined period labels                                     | Schema simplicity; PERT compatibility                    | FR-010–FR-018          | ✅ Implemented (evm_models_edu.py)     |
| TR-008 | The `.pmproj` schema version must be included in every saved file for future migration compatibility                                                 | Maintainability                                          | FR-043, FR-044         | ✅ Implemented (version: 1)            |

---

## 9. Acceptance Criteria (Summary)

Acceptance criteria are defined per deliverable. Full test cases are in the Test Plan.

| ID     | Acceptance Criterion                                                                                         | Linked Requirements     | Deliverable | Verified                             |
| ------ | ------------------------------------------------------------------------------------------------------------ | ----------------------- | ----------- | ------------------------------------ |
| AC-001 | CPM forward/backward pass produces correct ES, EF, LS, LF, Float for all activities in the reference project | FR-001, FR-002, NFR-008 | D1          | ✅                                   |
| AC-002 | All 16 EVM KPIs compute correctly for the reference project EVM snapshot                                     | FR-010–FR-016, NFR-008  | D1          | ✅                                   |
| AC-003 | RAG colour codes apply correctly for CPI=0.92, SPI=1.02 (expected: amber/green)                              | FR-017                  | D1          | ✅                                   |
| AC-004 | Monte Carlo P50/P80/P90 outputs are stable across 10 repeated runs with the same seed                        | FR-025–FR-028, NFR-003  | D1          | ✅                                   |
| AC-005 | Risk matrix correctly places all 12+ risks in the reference project register                                 | FR-020–FR-022           | D1          | ✅                                   |
| AC-006 | Financial Analysis tab computes NPV=+85,480, IRR≈12.4%, Payback=3.80 for reference project inputs            | FR-032                  | D1          | ✅                                   |
| AC-007 | Reference project loads without error and populates all 24 tabs consistently                                 | FR-046, FR-047          | D1, D5      | ⚠️ In Progress                       |
| AC-008 | Windows executable launches on a clean Windows 10 VM with no Python installation                             | FR-050, NFR-005         | D3          | ✅                                   |
| AC-009 | `pip install pmhelper && pmhelper-gui` launches the desktop application                                      | FR-051                  | D4          | ✅                                   |
| AC-010 | Web health endpoint returns HTTP 200; API processes CPM request within 5 seconds                             | FR-049, NFR-010         | D2          | ✅                                   |
| AC-011 | RACI validator correctly identifies: missing A, missing R, and empty columns                                 | FR-037, FR-038          | D1          | ✅                                   |
| AC-012 | Worked solution for CPM forward pass matches manual computation for reference project                        | EDU-001, NFR-008        | D1, D8      | ✅                                   |
| AC-013 | UG/PG mode toggle correctly shows/hides PG-only tabs (PESTEL, DPCI, Charter Mgr, RACI, SWOT)                 | EDU-003, FR-018 (UG/PG) | D1          | ✅                                   |
| AC-014 | Charter JSON export from reference project matches the structure of `04_project_charter.json`                | FR-041                  | D1, D5      | ⚠️ Pending sample project completion |
| AC-015 | All 800+ automated tests pass on a clean Python 3.8 environment                                              | NFR-007, TR-004         | D6          | ✅                                   |

---

## 10. Traceability Summary Matrix

The following matrix traces key Business Requirements forward to deliverables and
identifies the coverage status.

| BR     | SHR                | FR Range         | EDU/NFR            | Deliverable | Coverage       |
| ------ | ------------------ | ---------------- | ------------------ | ----------- | -------------- |
| BR-001 | SHR-001 to SHR-013 | FR-001 to FR-042 | EDU-001 to EDU-008 | D1, D8      | ✅ Full        |
| BR-002 | SHR-016, SHR-017   | FR-049 to FR-051 | NFR-005, NFR-006   | D2, D3, D4  | ✅ Full        |
| BR-003 | SHR-014, SHR-024   | FR-046, FR-047   | EDU-005            | D5          | ⚠️ In Progress |
| BR-004 | SHR-024            | —                | EDU-005            | D5, D7      | ⚠️ In Progress |
| BR-005 | SHR-018            | —                | EDU-003            | D1          | ✅ Full        |
| BR-006 | SHR-016            | FR-050           | NFR-004, NFR-005   | D3          | ✅ Full        |
| BR-007 | —                  | FR-051           | —                  | D4          | ✅ Full        |
| BR-008 | —                  | TR-001 to TR-008 | —                  | All         | ✅ Full        |

---

## 11. Gap Analysis — Requirements Not Yet Fully Met

The following requirements are identified but not yet fully implemented. They become
inputs to the project schedule (Phases 6–7) and to the future development roadmap.

| ID      | Gap                                                  | Impact                               | Plan                            |
| ------- | ---------------------------------------------------- | ------------------------------------ | ------------------------------- |
| FR-047  | Reference project not yet loadable as an in-app demo | D5 acceptance criterion AC-007 unmet | Phase 7 (this document set)     |
| EDU-005 | Reference project narrative not yet linking all tabs | D5 not complete                      | Phase 7 (this document set)     |
| EDU-008 | No integrated PMBOK lifecycle navigator              | Missing cross-tab educational flow   | Future development (V3 roadmap) |
| SHR-024 | Reference project document set incomplete            | Multiple AC items pending            | Phase 7 (in progress)           |

**Future development items identified (not in scope for PMHE-2025):**

| ID     | Requirement                                         | Priority |
| ------ | --------------------------------------------------- | -------- |
| FR-052 | Earned Schedule (ES) and SV(t) calculation          | High     |
| FR-053 | TCPI toward EAC (in addition to toward BAC)         | Medium   |
| FR-054 | Cumulative SPI/CPI trend chart                      | Medium   |
| FR-055 | Risk-Adjusted EAC                                   | Medium   |
| FR-056 | Requirements Traceability module in the application | Low      |
| FR-057 | Communications management tab                       | Low      |
| FR-058 | Change control log tab                              | Medium   |

---

## 12. Document Control

| Version | Date       | Author                 | Change                                                                 |
| ------- | ---------- | ---------------------- | ---------------------------------------------------------------------- |
| 0.1     | 2025-09-08 | Ahmed Samir Khalil     | Initial requirements from charter and project definition               |
| 1.0     | 2025-10-15 | Ahmed Samir Khalil     | Architecture milestone: full functional requirements added             |
| 1.1     | 2026-03-25 | Omar Hassan El-Rashidy | V1 feature-complete: updated status to ✅ for all FR-001–FR-031        |
| 1.2     | 2026-07-09 | Ahmed Samir Khalil     | Status update: FR-047, EDU-005 still in progress; gap analysis updated |
