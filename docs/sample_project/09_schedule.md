# Project Schedule — CPM Activity List

## PMHelper_Edu Development Project

| Field                | Value                                           |
| -------------------- | ----------------------------------------------- |
| **Document ID**      | PMHE-2025-SCH-001                               |
| **Project Code**     | PMHE-2025                                       |
| **Version**          | 1.1 — Baseline Active                           |
| **Prepared by**      | Ahmed Samir Khalil, PMP                         |
| **Approved by**      | Dr. Karim Naguib                                |
| **Organization**     | EduTech Dynamics                                |
| **Baseline Date**    | 2025-10-15                                      |
| **Last Updated**     | 2026-07-09                                      |
| **Project Start**    | 2025-09-01                                      |
| **Planned Finish**   | 2026-09-30                                      |
| **Total Activities** | 84                                              |
| **App Import File**  | `data/sample_project/pmhelper_edu_schedule.csv` |

---

## 1. Calendar and Schedule Assumptions

**Working calendar:** Monday to Friday, 5 days per week.

**Non-working days excluded from schedule:**

| Holiday                      | Date(s)                                                         |
| ---------------------------- | --------------------------------------------------------------- |
| Egyptian Armed Forces Day    | 2025-10-06                                                      |
| Eid al-Adha (estimated)      | 2025-06-06 to 2025-06-09 → affects 2026 schedule from Q2        |
| Revolution Day               | 2026-07-23                                                      |
| Eid al-Fitr (estimated)      | 2026-03-29 to 2026-04-02                                        |
| Sinai Liberation Day         | 2026-04-25                                                      |
| Labour Day                   | 2026-05-01                                                      |
| Eid al-Adha (estimated)      | 2026-05-27 to 2026-05-30                                        |
| Islamic New Year (estimated) | 2026-06-17                                                      |
| Revolution Day               | 2026-07-23                                                      |
| Ramadan reduced productivity | 2026-02-17 to 2026-03-17 (20% velocity reduction, not excluded) |

**Total working days available:** ~258 WD over 13 months.

**Scheduling method:** Finish-to-Start (FS) unless otherwise noted.
Durations are in **working days (WD)**.

---

## 2. Critical Path Summary

The CPM calculation (performed by PMHelper_Edu) identifies the following critical path:

**Critical Path:** A01 → A04 → A05 → A06 → A11 → A22 → A30 → A33 → A43 → A53 → A57 → A59 → A68 → A72 → A73 → A74

**Critical Path Duration:** ~243 WD  
**Project Float Available:** ~15 WD (built-in buffer for Ramadan and unexpected delays)  
**Identified Critical Activities:** 16 (starred ★ in the activity table)

---

## 3. Project Milestones

| Milestone                         | Activity               | Target Date |
| --------------------------------- | ---------------------- | ----------- |
| M1 — Project Kickoff              | A01 complete           | 2025-09-08  |
| M2 — Architecture Established     | A05, A06, A07 complete | 2025-10-15  |
| M3 — V1 Desktop Feature-Complete  | A33 complete           | 2026-03-25  |
| M4 — Web Frontend Deployed        | A41 complete           | 2026-05-15  |
| M5 — V2 All Tabs Feature-Complete | A59 complete           | 2026-06-30  |
| M6 — Distribution Verified        | A63, A64 complete      | 2026-08-31  |
| M7 — Reference Project Complete   | A68 complete           | 2026-09-30  |
| M8 — Project Closure              | A74 complete           | 2026-09-30  |

---

## 4. Complete Activity List

### Phase 1 — Initiation

| ID   | Activity Name                                | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | -------------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| ★A01 | Project Charter Development                  | 1.1.1 | 10       | —            | PM       | 7   | 10  | 16  | 7       | 800            |
| A02  | Stakeholder Register and Benefits Plan       | 1.1.1 | 10       | A01          | PM       | 8   | 10  | 14  | 7       | 600            |
| A03  | Development Environment and Repository Setup | 1.2.5 | 5        | A01          | Lead Dev | 3   | 5   | 8   | 3       | 1500           |

### Phase 2 — Planning and Architecture

| ID   | Activity Name                           | WBS   | Duration | Predecessors | Resource     | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | --------------------------------------- | ----- | -------- | ------------ | ------------ | --- | --- | --- | ------- | -------------- |
| ★A04 | Requirements Analysis and Documentation | 1.2.1 | 15       | A01          | PM; Lead Dev | 11  | 15  | 22  | 10      | 1800           |
| ★A05 | Module Architecture Design              | 1.2.2 | 10       | A04          | Lead Dev     | 7   | 10  | 15  | 7       | 2000           |
| ★A06 | Data Model and .pmproj Schema Design    | 1.2.3 | 8        | A05          | Lead Dev     | 6   | 8   | 12  | 5       | 2000           |
| A07  | GUI Architecture and Component Design   | 1.2.4 | 5        | A05          | Lead Dev     | 4   | 5   | 8   | 3       | 2000           |
| A08  | CI/CD Pipeline Configuration            | 1.2.6 | 5        | A03          | Lead Dev     | 3   | 5   | 9   | 3       | 1500           |
| A09  | Project Management Baseline Planning    | 1.1.2 | 15       | A05          | PM           | 11  | 15  | 22  | 10      | 800            |

### Phase 3 — V1 Core Calculation Engines

| ID   | Activity Name                                  | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | ---------------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| A10  | CPM and PERT Calculation Engines               | 1.3.1 | 25       | A06;A07      | Lead Dev | 18  | 25  | 38  | 17      | 2000           |
| ★A11 | EVM Engine and 16-KPI Module                   | 1.3.2 | 20       | A06          | Lead Dev | 15  | 20  | 30  | 14      | 2000           |
| A12  | Risk Register Engine                           | 1.3.3 | 15       | A06          | Lead Dev | 11  | 15  | 22  | 10      | 2000           |
| A13  | Monte Carlo Simulation Engine                  | 1.3.3 | 15       | A12          | Lead Dev | 11  | 15  | 24  | 10      | 2000           |
| A14  | Project Crashing Engine                        | 1.3.4 | 12       | A10          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A15  | Resource Leveling Engine (MinMoment + Burgess) | 1.3.4 | 18       | A10          | Lead Dev | 13  | 18  | 27  | 12      | 2000           |

### Phase 4 — V1 GUI Tabs: Schedule Group

| ID  | Activity Name                              | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| --- | ------------------------------------------ | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| A16 | Input Activities Tab                       | 1.3.5 | 10       | A10;A07      | Lead Dev | 7   | 10  | 15  | 7       | 2000           |
| A17 | Results and Analysis Tab                   | 1.3.5 | 8        | A16          | Lead Dev | 6   | 8   | 12  | 5       | 2000           |
| A18 | Network Diagram Tab (AON, Sugiyama Layout) | 1.3.5 | 12       | A10;A07      | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A19 | PERT Diagram Tab                           | 1.3.5 | 8        | A10;A07      | Lead Dev | 6   | 8   | 12  | 5       | 2000           |
| A20 | Gantt Chart Tab with Tracking Gantt        | 1.3.5 | 12       | A10;A07      | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A21 | Project Crashing Tab                       | 1.3.5 | 12       | A14          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |

### Phase 5 — V1 GUI Tabs: Cost and Risk Groups

| ID   | Activity Name                           | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | --------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| ★A22 | EVM Dashboard Tab (KPI Cards + S-Curve) | 1.3.6 | 20       | A11;A07      | Lead Dev | 15  | 20  | 30  | 14      | 2000           |
| A23  | Risk Analysis Tab (4 sub-tabs)          | 1.3.7 | 15       | A12;A07      | Lead Dev | 11  | 15  | 22  | 10      | 2000           |
| A24  | Probability and Monte Carlo Tab         | 1.3.7 | 15       | A13;A07      | Lead Dev | 11  | 15  | 23  | 10      | 2000           |
| A25  | RCPS and Resource Management Tab        | 1.3.7 | 18       | A15;A07      | Lead Dev | 13  | 18  | 27  | 12      | 2000           |

### Phase 6 — V1 Data Management, Interactive Viz, and Demos

| ID   | Activity Name                                   | WBS   | Duration | Predecessors | Resource         | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | ----------------------------------------------- | ----- | -------- | ------------ | ---------------- | --- | --- | --- | ------- | -------------- |
| A26  | Project File Management (.pmproj save/load)     | 1.3.8 | 12       | A06          | Lead Dev         | 9   | 12  | 18  | 8       | 2000           |
| A27  | CSV and Excel Import Handlers                   | 1.3.8 | 8        | A06          | Lead Dev         | 6   | 8   | 12  | 5       | 1500           |
| A28  | Small Demo Datasets (UG/PG Small)               | 1.3.9 | 10       | A26;A22;A23  | Lead Dev; Jr Dev | 7   | 10  | 15  | 7       | 1200           |
| A29  | Interactive Network Viewer (vis.js/pyvis)       | 1.3.5 | 12       | A10;A18      | Lead Dev         | 9   | 12  | 20  | 8       | 2000           |
| ★A30 | Interactive Gantt and S-Curve (Plotly/WebView2) | 1.3.6 | 10       | A22;A20      | Lead Dev         | 7   | 10  | 16  | 7       | 2000           |

### Phase 7 — V1 Testing, Integration, and Phase Complete

| ID   | Activity Name                                 | WBS    | Duration | Predecessors                | Resource         | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | --------------------------------------------- | ------ | -------- | --------------------------- | ---------------- | --- | --- | --- | ------- | -------------- |
| A31  | Unit Tests — Core Calculation Engines         | 1.8.2  | 20       | A10;A11;A12;A13;A14;A15     | Lead Dev; QA     | 15  | 20  | 30  | 14      | 1800           |
| A32  | Unit Tests — GUI Binding and Data Models      | 1.8.3  | 15       | A16;A22;A23;A24;A25;A26;A27 | Jr Dev; QA       | 11  | 15  | 22  | 10      | 1400           |
| ★A33 | V1 Integration Testing and Phase Completion   | 1.3.10 | 15       | A31;A32;A28;A29;A30         | Lead Dev; QA     | 11  | 15  | 23  | 10      | 2000           |
| A34  | Large-Scale Demo Support and Performance Test | 1.4.6  | 10       | A33                         | Lead Dev; Jr Dev | 7   | 10  | 16  | 7       | 1500           |

### Phase 8 — Web Application Development

| ID  | Activity Name                           | WBS   | Duration | Predecessors | Resource         | O   | M   | P   | Min Dur | Crash Cost/Day |
| --- | --------------------------------------- | ----- | -------- | ------------ | ---------------- | --- | --- | --- | ------- | -------------- |
| A35 | FastAPI Backend and SQLAlchemy Database | 1.5.1 | 20       | A06;A03      | Lead Dev         | 15  | 20  | 30  | 14      | 2000           |
| A36 | API Endpoints for CPM/EVM Analysis      | 1.5.1 | 15       | A35;A10;A11  | Lead Dev         | 11  | 15  | 22  | 10      | 2000           |
| A37 | Angular Frontend UI Development         | 1.5.2 | 25       | A35          | Lead Dev; Jr Dev | 18  | 25  | 38  | 17      | 2500           |
| A38 | Web API Integration and Testing         | 1.5.3 | 12       | A36;A37      | Lead Dev; QA     | 9   | 12  | 18  | 8       | 1800           |

### Phase 9 — Cloud Deployment and Distribution Infrastructure

| ID  | Activity Name                                 | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| --- | --------------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| A39 | Render.com Configuration and Deployment       | 1.5.4 | 8        | A38          | Lead Dev | 6   | 8   | 13  | 5       | 2000           |
| A40 | Domain Registration and SSL Certificate       | 1.5.5 | 2        | A39          | Lead Dev | 1   | 2   | 4   | 1       | 1000           |
| A41 | Production Verification and Health Monitoring | 1.5.6 | 5        | A40          | Lead Dev | 3   | 5   | 9   | 3       | 1500           |
| A42 | CI/CD Build and Release Automation            | 1.6.4 | 8        | A08;A33      | Lead Dev | 6   | 8   | 13  | 5       | 1500           |

### Phase 10 — V2 Infrastructure

| ID   | Activity Name                                                        | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | -------------------------------------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| ★A43 | Tab Group Refactor (TabGroupNotebook)                                | 1.4.1 | 15       | A33          | Lead Dev | 11  | 15  | 23  | 10      | 2000           |
| A44  | V2 Educational Infrastructure (DemoLoader, EducationalCalculatorTab) | 1.4.1 | 8        | A43          | Lead Dev | 6   | 8   | 13  | 5       | 2000           |

### Phase 11 — V2 New Calculation and Planning Tabs

| ID   | Activity Name                                   | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | ----------------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| A45  | Three-Point Estimation Tab                      | 1.4.2 | 12       | A44          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A46  | Financial Analysis Tab (NPV/IRR/Payback/ROI/PI) | 1.4.3 | 14       | A44          | Lead Dev | 10  | 14  | 21  | 9       | 2000           |
| A47  | Factor Scoring Tab (0-1/Factor/Weighted)        | 1.4.3 | 8        | A44          | Lead Dev | 6   | 8   | 12  | 5       | 2000           |
| A48  | RACI Matrix Tab                                 | 1.4.4 | 12       | A44          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A49  | Cost Estimation Tab (7 Techniques)              | 1.4.5 | 12       | A44          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A50  | AON/AOA Dual Network Mode                       | 1.4.6 | 10       | A44;A18      | Lead Dev | 7   | 10  | 16  | 7       | 2000           |
| A51  | Risk Response Planning Sub-tab                  | 1.4.6 | 10       | A44;A23      | Lead Dev | 7   | 10  | 15  | 7       | 2000           |
| A52  | Resource Leveling Educational Walkthrough       | 1.4.7 | 12       | A44;A25      | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| ★A53 | Charter and Charter Manager Tabs                | 1.4.8 | 15       | A44          | Lead Dev | 11  | 15  | 23  | 10      | 2000           |

### Phase 12 — V2 Strategic Analysis Tabs

| ID   | Activity Name                          | WBS   | Duration | Predecessors | Resource | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | -------------------------------------- | ----- | -------- | ------------ | -------- | --- | --- | --- | ------- | -------------- |
| A54  | SWOT Analysis Tab                      | 1.4.8 | 12       | A44          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| A55  | PESTEL Analysis Tab                    | 1.4.8 | 10       | A44          | Lead Dev | 7   | 10  | 16  | 7       | 2000           |
| A56  | WBS Tab                                | 1.4.8 | 12       | A44          | Lead Dev | 9   | 12  | 18  | 8       | 2000           |
| ★A57 | Dashboard Health Summary Tab           | 1.4.8 | 15       | A53;A30;A22  | Lead Dev | 11  | 15  | 23  | 10      | 2000           |
| A58  | Foundations and PM Role Reference Tabs | 1.4.8 | 8        | A44          | Lead Dev | 6   | 8   | 12  | 5       | 1500           |
| A70  | DPCI Assessment Tab                    | 1.4.8 | 10       | A44          | Lead Dev | 7   | 10  | 16  | 7       | 2000           |

### Phase 13 — V2 Testing and Large Demos

| ID   | Activity Name                               | WBS         | Duration | Predecessors                                                | Resource         | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | ------------------------------------------- | ----------- | -------- | ----------------------------------------------------------- | ---------------- | --- | --- | --- | ------- | -------------- |
| ★A59 | V2 Integration Testing and Regression Suite | 1.8.3;1.8.4 | 25       | A45;A46;A47;A48;A49;A50;A51;A52;A53;A54;A55;A56;A57;A58;A70 | Lead Dev; QA     | 18  | 25  | 38  | 17      | 2000           |
| A60  | V2 Calculator Demo Datasets (11 JSON Files) | 1.7.4       | 10       | A45;A46;A47;A48;A49;A52                                     | Jr Dev; Lead Dev | 7   | 10  | 15  | 7       | 1200           |
| A61  | Large-Scale Demo Projects (UG/PG 600-task)  | 1.7.5       | 10       | A34                                                         | Jr Dev           | 7   | 10  | 15  | 7       | 1000           |

### Phase 14 — Distribution and Packaging

| ID  | Activity Name                             | WBS   | Duration | Predecessors | Resource     | O   | M   | P   | Min Dur | Crash Cost/Day |
| --- | ----------------------------------------- | ----- | -------- | ------------ | ------------ | --- | --- | --- | ------- | -------------- |
| A62 | PyInstaller Build and AV-Safe Manifest    | 1.6.1 | 10       | A59          | Lead Dev     | 7   | 10  | 16  | 7       | 2000           |
| A63 | Build Testing on Clean Windows 10 VM      | 1.6.1 | 5        | A62          | Lead Dev; QA | 4   | 5   | 8   | 3       | 1800           |
| A64 | PyPI Package Configuration and Submission | 1.6.3 | 5        | A62          | Lead Dev     | 4   | 5   | 8   | 3       | 1500           |
| A65 | GitHub Release Package Preparation        | 1.6.2 | 5        | A63;A64      | Lead Dev     | 4   | 5   | 8   | 3       | 1500           |

### Phase 15 — Educational Content and Documentation

| ID   | Activity Name                                      | WBS               | Duration | Predecessors                | Resource                  | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | -------------------------------------------------- | ----------------- | -------- | --------------------------- | ------------------------- | --- | --- | --- | ------- | -------------- |
| A66  | All Worked Solution Generators                     | 1.7.1;1.7.2;1.7.3 | 20       | A10;A11;A45;A46;A47;A48;A49 | Lead Dev                  | 15  | 20  | 30  | 14      | 2000           |
| A67  | V2 Demo Datasets Validation and Correction         | 1.7.4             | 8        | A60                         | Jr Dev; Technical Advisor | 6   | 8   | 12  | 5       | 1000           |
| ★A68 | Reference Sample Project Document Set              | 1.7.6             | 30       | A59;A67;A61                 | PM; Technical Advisor     | 22  | 30  | 46  | 20      | 1500           |
| A69  | User Documentation (README/Deployment/Quick-Start) | 1.7.7             | 12       | A62;A68                     | Lead Dev; PM              | 9   | 12  | 18  | 8       | 1200           |

### Phase 16 — UAT, Final QA, and Closure

| ID   | Activity Name                                 | WBS   | Duration | Predecessors    | Resource     | O   | M   | P   | Min Dur | Crash Cost/Day |
| ---- | --------------------------------------------- | ----- | -------- | --------------- | ------------ | --- | --- | --- | ------- | -------------- |
| A71  | Faculty Partner Beta Testing (UAT)            | 1.8.5 | 15       | A57;A60;A66     | PM; QA       | 10  | 15  | 24  | 10      | 1500           |
| ★A72 | UAT Defect Resolution                         | 1.8.5 | 10       | A71             | Lead Dev; QA | 7   | 10  | 16  | 7       | 2000           |
| ★A73 | Final Regression Testing and QA Sign-off      | 1.8.6 | 15       | A68;A69;A72;A65 | QA           | 10  | 15  | 23  | 10      | 1800           |
| ★A74 | Project Closure, Lessons Learned, and Archive | 1.1.8 | 30       | A73             | PM; Sponsor  | 22  | 30  | 46  | 20      | 1000           |

---

## 5. Activity Count and Network Summary

| Phase                    | Activities      | Duration Range | % of Total Effort |
| ------------------------ | --------------- | -------------- | ----------------- |
| Initiation               | 3 (A01–A03)     | 5–10 WD        | 2%                |
| Planning/Architecture    | 6 (A04–A09)     | 5–15 WD        | 7%                |
| V1 Engines               | 6 (A10–A15)     | 12–25 WD       | 14%               |
| V1 Schedule Tabs         | 6 (A16–A21)     | 8–12 WD        | 8%                |
| V1 Cost/Risk Tabs        | 4 (A22–A25)     | 15–20 WD       | 8%                |
| V1 Data Mgmt + Viz       | 5 (A26–A30)     | 8–12 WD        | 6%                |
| V1 Testing + Integration | 4 (A31–A34)     | 10–20 WD       | 7%                |
| Web Application          | 4 (A35–A38)     | 12–25 WD       | 8%                |
| Cloud + CI/CD            | 4 (A39–A42)     | 2–8 WD         | 3%                |
| V2 Infrastructure        | 2 (A43–A44)     | 8–15 WD        | 3%                |
| V2 New Tabs              | 9 (A45–A53)     | 8–15 WD        | 14%               |
| V2 Strategic Tabs        | 6 (A54–A58,A70) | 8–15 WD        | 7%                |
| V2 Testing + Demos       | 3 (A59–A61)     | 10–25 WD       | 5%                |
| Distribution             | 4 (A62–A65)     | 5–10 WD        | 3%                |
| Educational Content      | 4 (A66–A69)     | 8–30 WD        | 8%                |
| UAT + Closure            | 4 (A71–A74)     | 10–30 WD       | 8%                |
| **TOTAL**                | **84**          | —              | **100%**          |

**Critical path activities (★):** A01, A04, A05, A06, A11, A22, A30, A33, A43, A53, A57, A59, A68, A72, A73, A74

---

## 6. Import Instructions

To load this schedule into PMHelper_Edu:

**Option A — Direct CSV Import:**

1. Navigate to Schedule → Input Activities
2. Click "Import CSV" or "Import Excel"
3. Select: `data/sample_project/pmhelper_edu_schedule.csv`
4. Verify 84 activities appear in the grid
5. Run CPM Analysis → verify project duration ≈ 258 WD

**Option B — Load Reference Demo (after .pmproj file complete):**

1. File → Load Demo → PMHelper_Edu Reference Project
2. The full project loads including this schedule, EVM data, risks, RACI, WBS, SWOT, PESTEL

**PERT Analysis:**
Switch analysis mode to "Probabilistic (PERT)" in the Input tab dropdown to use
the O/M/P columns. The schedule provides three-point estimates for all 84 activities.

**Crashing Analysis:**
Navigate to Schedule → Crashing Tab to perform sequential least-cost crashing.
The critical path (16 activities) will be eligible for crashing. Activities with
the lowest crash_cost/day will be crashed first.

**Note on TCPI and EVM:** The EVM data for this project (document 21) shows
CPI ≈ 0.92 at the status date. The crashing tab can demonstrate the cost of
schedule compression — educational contrast: the project is already over budget
(CPI < 1) while crashing would add further cost. This teaches the cost-time
trade-off within a real project context.

---

## 7. Document Control

| Version | Date       | Author             | Change                                                                        |
| ------- | ---------- | ------------------ | ----------------------------------------------------------------------------- |
| 1.0     | 2025-10-15 | Ahmed Samir Khalil | Baseline schedule (84 activities)                                             |
| 1.1     | 2026-07-09 | Ahmed Samir Khalil | Actual durations verified; O/M/P confirmed by Prof. Youssef for PERT analysis |
