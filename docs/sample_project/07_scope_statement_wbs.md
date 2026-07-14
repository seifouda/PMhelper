# Scope Statement and Work Breakdown Structure

## PMHelper_Edu Development Project

| Field             | Value                                  |
| ----------------- | -------------------------------------- |
| **Document ID**   | PMHE-2025-SS-001                       |
| **Project Code**  | PMHE-2025                              |
| **Version**       | 1.1 — Active                           |
| **Prepared by**   | Ahmed Samir Khalil, PMP                |
| **Approved by**   | Dr. Karim Naguib                       |
| **Organization**  | EduTech Dynamics                       |
| **Baseline Date** | 2025-10-15 (architecture milestone M2) |
| **Last Updated**  | 2026-07-09 (status date)               |

---

## 1. Project Scope Description

PMHelper_Edu is a purpose-built educational software platform that teaches the
complete quantitative project management curriculum through interactive calculations,
dynamic visualisations, and guided worked solutions.

The project scope covers the full lifecycle of the product from initial concept through
production deployment across four distribution channels:

1. **Desktop Application** — Python/Tkinter standalone app with 24 educational tabs
   organised in five collapsible groups: Schedule, Cost, Risk, Strategic, and Dashboard
2. **Web Application** — Angular frontend with FastAPI/SQLAlchemy backend deployed on
   Render.com at a stable public URL
3. **Windows Executable** — Self-contained PyInstaller build requiring no Python
   installation, suitable for university computer labs
4. **PyPI Package** — `pip install pmhelper` for academic environments with Python

The product supports two educational levels selectable at runtime:

- **UG Mode** — undergraduate fundamentals: CPM, EVM, Gantt, basic risk analysis
- **PG Mode** — all UG content plus: PERT, Monte Carlo, PESTEL, SWOT, DPCI,
  Advanced EAC, RACI, and financial analysis tools

---

## 2. Project Deliverables

| ID  | Deliverable              | Description                               | Acceptance Criteria                                |
| --- | ------------------------ | ----------------------------------------- | -------------------------------------------------- |
| D1  | Desktop Application v1.0 | Complete Tkinter application, all 24 tabs | 24 tabs functional; 800+ tests; UG/PG mode working |
| D2  | Web Application v1.0     | Angular + FastAPI + Render.com deployment | Health endpoint 200; API tested; <3s load          |
| D3  | Windows Executable       | PyInstaller --onedir build with manifest  | Launches on clean Windows 10; no Python required   |
| D4  | PyPI Package             | `pip install pmhelper` distribution       | Installs cleanly; GUI launches; correct version    |
| D5  | Reference Sample Project | 32-document set covering all 24 tabs      | Loadable in-app; consistent across all sections    |
| D6  | Test Suite ≥ 800 Tests   | Automated test suite in CI/CD pipeline    | All tests pass; zero critical failures; CI green   |
| D7  | User Documentation       | README, deployment guide, quick-start     | Published on GitHub; accurate; complete            |
| D8  | Educational Content      | All worked solution generators            | All calc tabs have worked solutions; EDU-001 met   |

---

## 3. Scope Exclusions

The following are explicitly outside the scope of PMHE-2025:

| #   | Exclusion                              | Reason                                                 |
| --- | -------------------------------------- | ------------------------------------------------------ |
| E1  | Mobile application (iOS/Android)       | Schedule and budget constraint; future V3              |
| E2  | LMS integration (Moodle, Canvas)       | Out of capability scope; separate future project       |
| E3  | Arabic-language user interface         | Deferred; require translation specialist not in team   |
| E4  | Premium subscription/paid feature tier | Business model decision deferred to post-launch        |
| E5  | Dedicated server infrastructure        | Cloud-only approach sufficient at this scale           |
| E6  | macOS/Linux installers                 | Source code runs on all platforms; installers deferred |
| E7  | Real-time multi-user collaboration     | Significant architectural change; not required for V1  |
| E8  | Earned Schedule (ES) calculations      | Not yet implemented; scheduled for V3 roadmap          |

---

## 4. Project Constraints and Assumptions

_(Established in Charter PMHE-2025-PC-001 — reproduced here for scope context)_

**Binding Constraints:**

- Hard deadline: 2026-09-30 (academic year alignment)
- Budget ceiling: EGP 1,195,000 total (BAC EGP 1,150,000 + Management Reserve)
- Technology stack: Python 3.8+ and Tkinter for desktop GUI
- Distribution: MIT Licence required

**Key Assumptions:**

- GitHub Copilot available throughout
- Render.com starter tier sufficient
- Lead developer maintains projected pace with AI assistance

---

## 5. Work Breakdown Structure

The WBS is structured by project **deliverable area** (not by phase), aligned with PMBOK
knowledge area categories. This enables cost and schedule performance to be tracked per
product area rather than per phase.

**WBS Structure:** 3 levels (Root → Area → Work Package)
**Total nodes:** 64 (1 root + 8 area summaries + 55 work packages)
**Total BAC allocated:** EGP 1,150,000

---

### 1.0 PMHelper_Edu Development Project _(Root)_

**BAC: EGP 1,150,000 | Duration: 290 WD | Progress: 80% (weighted)**

---

#### 1.1 Project Management

**BAC: EGP 130,000 | Duration: 290 WD (span) | Progress: 75%**

| WBS Code | Work Package                         | Duration | Cost (EGP) | Responsible | Progress | Status      |
| -------- | ------------------------------------ | -------- | ---------- | ----------- | -------- | ----------- |
| 1.1.1    | Project Initiation Documents         | 10 WD    | 5,000      | PM          | 100%     | Completed   |
| 1.1.2    | Project Planning Documents           | 20 WD    | 20,000     | PM          | 95%      | In Progress |
| 1.1.3    | Project Management Plan (integrated) | 15 WD    | 15,000     | PM          | 100%     | Completed   |
| 1.1.4    | Team and Stakeholder Management      | 200 WD   | 30,000     | PM          | 75%      | In Progress |
| 1.1.5    | Status Reporting and Communications  | 200 WD   | 20,000     | PM          | 78%      | In Progress |
| 1.1.6    | Schedule and Cost Monitoring         | 200 WD   | 20,000     | PM          | 78%      | In Progress |
| 1.1.7    | Risk and Change Monitoring           | 200 WD   | 10,000     | PM          | 76%      | In Progress |
| 1.1.8    | Project Closure and Archive          | 30 WD    | 10,000     | PM          | 0%       | Not Started |

---

#### 1.2 Architecture and Infrastructure

**BAC: EGP 60,000 | Duration: 30 WD | Progress: 100%**

| WBS Code | Work Package                            | Duration | Cost (EGP) | Responsible   | Progress | Status    |
| -------- | --------------------------------------- | -------- | ---------- | ------------- | -------- | --------- |
| 1.2.1    | Requirements Analysis and Documentation | 15 WD    | 15,000     | PM + Lead Dev | 100%     | Completed |
| 1.2.2    | Module Architecture Design              | 10 WD    | 15,000     | Lead Dev      | 100%     | Completed |
| 1.2.3    | Data Model Design (.pmproj schema)      | 8 WD     | 12,000     | Lead Dev      | 100%     | Completed |
| 1.2.4    | GUI Architecture and Component Design   | 5 WD     | 8,000      | Lead Dev      | 100%     | Completed |
| 1.2.5    | Repository Setup (GitHub, branching)    | 3 WD     | 5,000      | Lead Dev      | 100%     | Completed |
| 1.2.6    | CI/CD Pipeline Configuration            | 5 WD     | 5,000      | Lead Dev      | 100%     | Completed |

---

#### 1.3 Desktop Application — V1 Features

**BAC: EGP 280,000 | Duration: 130 WD | Progress: 100%**

| WBS Code | Work Package                                                  | Duration | Cost (EGP) | Responsible       | Progress | Status    |
| -------- | ------------------------------------------------------------- | -------- | ---------- | ----------------- | -------- | --------- |
| 1.3.1    | CPM and PERT Calculation Engines                              | 25 WD    | 35,000     | Lead Dev          | 100%     | Completed |
| 1.3.2    | EVM Engine and 16-KPI Module                                  | 20 WD    | 30,000     | Lead Dev          | 100%     | Completed |
| 1.3.3    | Risk Register and Monte Carlo Engine                          | 18 WD    | 25,000     | Lead Dev          | 100%     | Completed |
| 1.3.4    | Crashing and Resource Leveling Engines                        | 18 WD    | 25,000     | Lead Dev          | 100%     | Completed |
| 1.3.5    | Schedule GUI Tabs (Input/Results/Network/Gantt/PERT/Crashing) | 35 WD    | 55,000     | Lead Dev          | 100%     | Completed |
| 1.3.6    | EVM Dashboard Tab                                             | 20 WD    | 30,000     | Lead Dev          | 100%     | Completed |
| 1.3.7    | Risk Analysis and Probability/Monte Carlo Tabs                | 18 WD    | 25,000     | Lead Dev          | 100%     | Completed |
| 1.3.8    | Project File Management (.pmproj format)                      | 12 WD    | 20,000     | Lead Dev          | 100%     | Completed |
| 1.3.9    | Small Demo Datasets (UG/PG Small)                             | 10 WD    | 15,000     | Lead Dev + Jr Dev | 100%     | Completed |
| 1.3.10   | V1 Module Integration and Regression Testing                  | 15 WD    | 20,000     | Lead Dev + QA     | 100%     | Completed |

---

#### 1.4 Desktop Application — V2 Features

**BAC: EGP 200,000 | Duration: 90 WD | Progress: 90%**

| WBS Code | Work Package                                                                       | Duration | Cost (EGP) | Responsible       | Progress | Status      |
| -------- | ---------------------------------------------------------------------------------- | -------- | ---------- | ----------------- | -------- | ----------- |
| 1.4.1    | Tab Group Refactor and Infrastructure (TabGroupNotebook, EducationalCalculatorTab) | 15 WD    | 25,000     | Lead Dev          | 100%     | Completed   |
| 1.4.2    | Three-Point Estimation Tab                                                         | 12 WD    | 20,000     | Lead Dev          | 100%     | Completed   |
| 1.4.3    | Financial Analysis and Factor Scoring Tabs                                         | 14 WD    | 22,000     | Lead Dev          | 100%     | Completed   |
| 1.4.4    | RACI Matrix Tab                                                                    | 12 WD    | 20,000     | Lead Dev          | 100%     | Completed   |
| 1.4.5    | Cost Estimation Tab (7 techniques)                                                 | 12 WD    | 20,000     | Lead Dev          | 100%     | Completed   |
| 1.4.6    | Risk Response Planning and AON/AOA Dual Network                                    | 18 WD    | 30,000     | Lead Dev          | 100%     | Completed   |
| 1.4.7    | Resource Leveling Educational Walkthrough                                          | 12 WD    | 20,000     | Lead Dev          | 100%     | Completed   |
| 1.4.8    | Strategic Tabs (SWOT/PESTEL/WBS/Dashboard) and Foundations                         | 25 WD    | 43,000     | Lead Dev + Jr Dev | 70%      | In Progress |

---

#### 1.5 Web Application

**BAC: EGP 120,000 | Duration: 50 WD | Progress: 90%**

| WBS Code | Work Package                                  | Duration | Cost (EGP) | Responsible       | Progress | Status      |
| -------- | --------------------------------------------- | -------- | ---------- | ----------------- | -------- | ----------- |
| 1.5.1    | FastAPI Backend and SQLAlchemy Database Layer | 20 WD    | 30,000     | Lead Dev          | 100%     | Completed   |
| 1.5.2    | Angular Frontend UI Components                | 25 WD    | 40,000     | Lead Dev + Jr Dev | 100%     | Completed   |
| 1.5.3    | API Integration and Web Testing               | 12 WD    | 20,000     | Lead Dev + QA     | 100%     | Completed   |
| 1.5.4    | Render.com Configuration and Deployment       | 8 WD     | 15,000     | Lead Dev          | 100%     | Completed   |
| 1.5.5    | Domain Registration and SSL Certificate       | 2 WD     | 5,000      | Lead Dev          | 100%     | Completed   |
| 1.5.6    | Production Verification and Health Monitoring | 5 WD     | 10,000     | Lead Dev          | 50%      | In Progress |

---

#### 1.6 Distribution and Packaging

**BAC: EGP 40,000 | Duration: 25 WD | Progress: 60%**

| WBS Code | Work Package                              | Duration | Cost (EGP) | Responsible | Progress | Status      |
| -------- | ----------------------------------------- | -------- | ---------- | ----------- | -------- | ----------- |
| 1.6.1    | PyInstaller Build and AV-Safe Manifest    | 10 WD    | 15,000     | Lead Dev    | 100%     | Completed   |
| 1.6.2    | GitHub Release Package and Notes          | 5 WD     | 8,000      | Lead Dev    | 30%      | In Progress |
| 1.6.3    | PyPI Package Configuration and Submission | 5 WD     | 10,000     | Lead Dev    | 100%     | Completed   |
| 1.6.4    | CI/CD Build and Release Automation        | 8 WD     | 7,000      | Lead Dev    | 100%     | Completed   |

---

#### 1.7 Educational Content

**BAC: EGP 140,000 | Duration: 180 WD (rolling) | Progress: 25%**

| WBS Code | Work Package                                         | Duration | Cost (EGP) | Responsible            | Progress | Status      |
| -------- | ---------------------------------------------------- | -------- | ---------- | ---------------------- | -------- | ----------- |
| 1.7.1    | CPM and EVM Worked Solution Generators               | 15 WD    | 20,000     | Lead Dev               | 100%     | Completed   |
| 1.7.2    | Risk, PERT, and Monte Carlo Worked Solutions         | 12 WD    | 15,000     | Lead Dev               | 100%     | Completed   |
| 1.7.3    | Financial, Cost, and Factor Scoring Worked Solutions | 15 WD    | 20,000     | Lead Dev               | 100%     | Completed   |
| 1.7.4    | V2 Calculator Demo Datasets (11 JSON files)          | 10 WD    | 15,000     | Lead Dev + Jr Dev      | 100%     | Completed   |
| 1.7.5    | Large-Scale Demo Projects (UG/PG 600-task)           | 10 WD    | 15,000     | Jr Dev + Lead Dev      | 100%     | Completed   |
| 1.7.6    | Reference Sample Project Document Set (32 docs)      | 30 WD    | 40,000     | PM + Technical Advisor | 25%      | In Progress |
| 1.7.7    | User Documentation (README/Deployment/Quick-Start)   | 12 WD    | 15,000     | Lead Dev + PM          | 20%      | In Progress |

---

#### 1.8 Testing and Quality Assurance

**BAC: EGP 180,000 | Duration: 45 WD (focused) | Progress: 75%**

| WBS Code | Work Package                                   | Duration | Cost (EGP) | Responsible            | Progress | Status      |
| -------- | ---------------------------------------------- | -------- | ---------- | ---------------------- | -------- | ----------- |
| 1.8.1    | Test Plan and Test Case Design                 | 10 WD    | 15,000     | QA                     | 100%     | Completed   |
| 1.8.2    | Unit Tests — Core Calculation Engines          | 30 WD    | 50,000     | Lead Dev + QA          | 100%     | Completed   |
| 1.8.3    | Unit Tests — GUI Binding and Data Models       | 25 WD    | 40,000     | Lead Dev + Jr Dev + QA | 100%     | Completed   |
| 1.8.4    | Integration Tests — Tab, File, and Save/Load   | 20 WD    | 30,000     | QA + Lead Dev          | 100%     | Completed   |
| 1.8.5    | User Acceptance Testing — Faculty Partner Beta | 15 WD    | 25,000     | PM + QA                | 60%      | In Progress |
| 1.8.6    | Regression Testing and Final QA Sign-off       | 15 WD    | 20,000     | QA                     | 0%       | Not Started |

---

## 6. WBS Summary — Cost and Schedule Status at 2026-07-09

| WBS     | Area                | BAC (EGP)     | % Complete | EV (EGP)    | Remaining Work |
| ------- | ------------------- | ------------- | ---------- | ----------- | -------------- |
| 1.1     | Project Management  | 130,000       | 75%        | 97,500      | 32,500         |
| 1.2     | Architecture        | 60,000        | 100%       | 60,000      | 0              |
| 1.3     | Desktop V1          | 280,000       | 100%       | 280,000     | 0              |
| 1.4     | Desktop V2          | 200,000       | 90%        | 180,000     | 20,000         |
| 1.5     | Web Application     | 120,000       | 90%        | 108,000     | 12,000         |
| 1.6     | Distribution        | 40,000        | 60%        | 24,000      | 16,000         |
| 1.7     | Educational Content | 140,000       | 25%        | 35,000      | 105,000        |
| 1.8     | Testing and QA      | 180,000       | 75%        | 135,000     | 45,000         |
| **1.0** | **TOTAL**           | **1,150,000** | **80.4%**  | **919,500** | **230,500**    |

> **EVM Preview (computed from WBS):**
> EV = EGP 919,500 | Planned Value at status date ≈ EGP 901,500 | Actual Cost ≈ EGP 999,500
> CPI ≈ 0.92 | SPI ≈ 1.02
> _Full EVM snapshot and period-by-period data: document 21 (EVM Data)_

---

## 7. WBS Dictionary Summary (Level 2)

| WBS | Area                | Key Scope Boundary                                                                     |
| --- | ------------------- | -------------------------------------------------------------------------------------- |
| 1.1 | Project Management  | All PM processes from initiation through closure; does NOT include development work    |
| 1.2 | Architecture        | Design and infrastructure setup only; does NOT include implementation                  |
| 1.3 | Desktop V1          | V1 features as defined in EDU_V1_Plan.md; does NOT include V2 features                 |
| 1.4 | Desktop V2          | V2 features as defined in EDU_V2_Plan.md; does NOT include V3 planned items            |
| 1.5 | Web Application     | All web components; the FastAPI backend is specifically for web — not a shared backend |
| 1.6 | Distribution        | Build, packaging, and release artefacts only; source code is in 1.3 and 1.4            |
| 1.7 | Educational Content | Worked solutions, demos, and documentation; does NOT include feature development       |
| 1.8 | Testing and QA      | Test design, execution, and sign-off; unit tests written alongside code are in 1.3/1.4 |

_Full WBS Dictionary (per work package): document 08 (WBS Dictionary)_

---

## 8. Document Control

| Version | Date       | Author             | Change                                                             |
| ------- | ---------- | ------------------ | ------------------------------------------------------------------ |
| 0.1     | 2025-09-08 | Ahmed Samir Khalil | Initial scope statement from charter                               |
| 1.0     | 2025-10-15 | Ahmed Samir Khalil | WBS established at architecture milestone                          |
| 1.1     | 2026-07-09 | Ahmed Samir Khalil | Progress updated at status date; 1.4.8 and 1.5.6 still in progress |
