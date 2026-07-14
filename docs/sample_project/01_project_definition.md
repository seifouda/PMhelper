# Project Definition

## PMHelper_Edu Development Project

| Field            | Value                                     |
| ---------------- | ----------------------------------------- |
| **Document ID**  | PMHE-2025-PD-001                          |
| **Project Code** | PMHE-2025                                 |
| **Version**      | 1.0 — Approved                            |
| **Prepared by**  | Ahmed Samir Khalil, PMP — Project Manager |
| **Approved by**  | Dr. Karim Naguib — Project Sponsor        |
| **Organization** | EduTech Dynamics                          |
| **Date**         | 2025-09-01                                |
| **Status**       | Active                                    |

---

## 1. Project Identification

**Project Name:** PMHelper_Edu — Educational Project Management Software

**Project Code:** PMHE-2025

**Project Manager:** Ahmed Samir Khalil, PMP

**Project Sponsor:** Dr. Karim Naguib, Co-Founder and CTO, EduTech Dynamics

**Project Owner (Product):** Dr. Karim Naguib

**Organization:** EduTech Dynamics — Cairo, Egypt

**Classification:** New Product Development | Software | Educational Technology

---

## 2. Problem Statement

Project management education at university level consistently suffers from a gap between theoretical instruction and practical application. Students learn CPM, PERT, Earned Value Management, risk analysis, and resource leveling through textbook formulas and manual exercises. They have no access to integrated tools that:

- Perform these calculations interactively
- Show step-by-step worked solutions
- Demonstrate how all PM techniques connect within a single project narrative
- Scale from undergraduate basics to postgraduate depth in the same interface

Commercial alternatives (Microsoft Project, Primavera P6, Oracle Fusion) are expensive, licensed per seat, operationally complex, and not designed to teach PM concepts — they assume existing PM knowledge. Free tools are fragmented, cover only one technique each, and provide no educational scaffolding.

This gap reduces the effectiveness of PM education and limits students' ability to apply quantitative techniques after graduation.

---

## 3. Project Purpose and Strategic Justification

EduTech Dynamics will develop **PMHelper_Edu** — a purpose-built educational software application that covers the complete quantitative project management curriculum from undergraduate to postgraduate level.

The product addresses the identified gap by providing:

1. A free-to-use desktop application covering 24 PM topic areas
2. Interactive calculators with step-by-step worked solutions
3. A web application accessible without local installation
4. A distributable Windows executable for lab environments without internet
5. A PyPI Python package for academic institutions with Python infrastructure
6. A comprehensive reference sample project (this document set) demonstrating every application feature

Strategic alignment:

- Positions EduTech Dynamics as an education technology leader in the MENA region
- Generates institutional licensing revenue from universities and training centres
- Establishes the brand within the project management academic community
- Creates a foundation for future premium features and courseware integration

---

## 4. Project Objectives

All objectives are SMART: Specific, Measurable, Achievable, Relevant, Time-bound.

| #   | Objective                                                                           | Measure                                                                       | Target                                     | Deadline   |
| --- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------ | ---------- |
| O1  | Deliver a fully operational desktop application covering all planned PM topic areas | 24 functional tabs, all passing automated tests                               | 100% tab functionality                     | 2026-08-15 |
| O2  | Support undergraduate and postgraduate learning modes with educational scaffolding  | Worked solutions and Try It Yourself mode in all calculation tabs             | All calculation tabs dual-mode             | 2026-08-15 |
| O3  | Deploy a production web application accessible at a stable public URL               | Application reachable at production domain with <3s load time                 | 99%+ uptime over 30-day measurement        | 2026-07-31 |
| O4  | Publish a standalone Windows executable and PyPI package                            | Successful PyPI publication; exe runs on a clean Windows 10 VM without Python | Both distribution channels operational     | 2026-08-31 |
| O5  | Achieve and maintain a comprehensive automated test suite                           | Number of passing tests; zero critical defects in test suite                  | ≥ 800 tests, zero critical failures        | 2026-09-15 |
| O6  | Deliver a complete reference sample project covering all application features       | Reference project loadable in-app and consistent across all 24 tabs           | 100% feature coverage in reference project | 2026-09-30 |

---

## 5. Project Scope

### 5.1 In Scope

**Desktop Application (Primary Deliverable)**

- Complete Python/Tkinter application with 24 educational tabs organised in 5 collapsible groups
- All calculation engines: CPM, PERT, EVM, Risk Analysis, Monte Carlo Simulation, Project Crashing, Resource Leveling, RCPS, Financial Analysis, Cost Estimation, Factor Scoring, Three-Point Estimation, AON/AOA Networks
- Strategic analysis tools: SWOT, PESTEL, WBS, RACI Matrix
- Project initiation tools: Project Charter, DPCI Assessment
- Educational features: Step-by-step worked solutions, Try It Yourself mode, RAG colour-coded KPIs
- UG/PG learning mode toggle with mode-appropriate content visibility
- Project file management: save/load `.pmproj` files, demo projects, chart export
- Interactive visualisations: Gantt chart, network diagram, EV S-Curve, risk matrix, probability distributions, resource histograms, Plotly-embedded interactive charts

**Web Application**

- Angular frontend providing browser-based access to core calculation features
- FastAPI backend with SQLAlchemy database layer
- Production deployment on Render.com cloud platform
- Health endpoint, CORS configuration, API documentation

**Distribution**

- Standalone Windows executable via PyInstaller (`--onedir`, antivirus-safe manifest)
- Python package published to PyPI (`pip install pmhelper`)
- GitHub Actions CI/CD pipeline for automated testing and release

**Educational Content**

- Complete reference sample project: PMHelper_Edu Development Project (this document set)
- All in-application demo datasets (UG Small, UG Medium, UG Large, PG Small, PG Medium, PG Large)
- V2 standalone calculator demonstration datasets for all individual tabs

### 5.2 Out of Scope

- Mobile application (iOS or Android)
- Learning Management System integration (Moodle, Canvas, Blackboard)
- Arabic-language user interface
- Premium subscription or paid feature tiers during initial release
- Dedicated server infrastructure (cloud hosting only)
- macOS or Linux installer packages (source code runs on all platforms)
- Real-time multi-user collaboration
- Database-backed project storage for the desktop edition

---

## 6. Key Deliverables

| #   | Deliverable                | WBS Ref | Acceptance Criteria                                                    |
| --- | -------------------------- | ------- | ---------------------------------------------------------------------- |
| D1  | Desktop application v1.0   | 1.3     | All 24 tabs functional, 800+ tests passing, PyInstaller build verified |
| D2  | Web application v1.0       | 1.4     | Deployed on Render.com, health endpoint returns 200, API tested        |
| D3  | Windows executable package | 1.5.1   | Launches on clean Windows 10 VM, all tabs function, no Python required |
| D4  | PyPI package               | 1.5.2   | Installable via `pip install pmhelper`, GUI launches successfully      |
| D5  | Reference sample project   | 1.6     | Loadable in-app, consistent across all 24 tabs, covers all features    |
| D6  | Test suite                 | 1.3.4   | ≥ 800 passing tests, CI/CD pipeline green on main branch               |
| D7  | User documentation         | 1.6.3   | README, deployment guide, and quick-start guide published              |
| D8  | Educational content        | 1.6.4   | All worked solution generators implemented and tested                  |

---

## 7. Milestones

| #   | Milestone                              | Target Date | Predecessor |
| --- | -------------------------------------- | ----------- | ----------- |
| M1  | Project kickoff complete               | 2025-09-08  | —           |
| M2  | Core architecture established          | 2025-10-15  | M1          |
| M3  | V1 feature-complete (desktop)          | 2026-03-25  | M2          |
| M4  | Web frontend v1 deployed to production | 2026-05-15  | M3          |
| M5  | V2 feature-complete (all 24 tabs)      | 2026-06-30  | M4          |
| M6  | Production build (exe + PyPI) verified | 2026-08-31  | M5          |
| M7  | Reference sample project complete      | 2026-09-30  | M6          |
| M8  | Project closure                        | 2026-09-30  | M7          |

---

## 8. Constraints

| #   | Category     | Constraint                                                                       | Impact                                                    |
| --- | ------------ | -------------------------------------------------------------------------------- | --------------------------------------------------------- |
| C1  | Schedule     | Product must be usable by academic institutions from the 2026–2027 academic year | Fixes the 2026-09-30 deadline                             |
| C2  | Budget       | Total expenditure cannot exceed EGP 1,195,000 (including all reserves)           | Limits team size and tool choices                         |
| C3  | Resources    | Maximum staffing equivalent of 2.0 FTE throughout the project                    | Lead developer is the single critical resource            |
| C4  | Technology   | Desktop application must use Python 3.8+ and Tkinter only (no Electron, no Qt)   | Preserves compatibility with academic Python environments |
| C5  | Platform     | Primary target platform is Windows 10+ (64-bit)                                  | Aligns with university computer lab standard              |
| C6  | Licensing    | Product must be released under MIT License                                       | Required for free academic adoption                       |
| C7  | Connectivity | Desktop application must function fully offline                                  | University lab networks may restrict internet access      |

---

## 9. Assumptions

| #   | Assumption                                                                               | If Wrong — Impact                                                               |
| --- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| A1  | GitHub Copilot AI assistance will remain available and affordable throughout the project | Development velocity decreases significantly; schedule risk                     |
| A2  | Render.com free/starter tier provides sufficient infrastructure for initial deployment   | Additional cloud costs required; budget risk                                    |
| A3  | Python 3.8+ compatibility is sufficient for all target academic environments             | Rework may be needed for older lab environments                                 |
| A4  | Windows 10+ remains the dominant OS in Egyptian and regional university computer labs    | Platform support scope may need to expand                                       |
| A5  | PyPI publication approval is straightforward for an open-source educational package      | Distribution delay if additional review is required                             |
| A6  | A single lead developer can sustain the required development pace with AI assistance     | Schedule risk increases substantially if productivity assumptions are incorrect |
| A7  | The Angular web frontend can reuse core Python calculation logic via the FastAPI backend | Significant rework if direct Python reuse is not feasible                       |
| A8  | Render.com provides adequate response times for academic users in the MENA region        | Web UX may degrade for distant users; CDN or alternative hosting may be needed  |

---

## 10. Dependencies

| #    | Type     | Dependency               | Description                                                                         |
| ---- | -------- | ------------------------ | ----------------------------------------------------------------------------------- |
| DEP1 | External | GitHub                   | Version control, CI/CD, releases, issue tracking                                    |
| DEP2 | External | Render.com               | Web application cloud hosting                                                       |
| DEP3 | External | PyPI                     | Package distribution infrastructure                                                 |
| DEP4 | External | GitHub Copilot           | AI-assisted development tooling                                                     |
| DEP5 | Internal | Core analysis engines    | All GUI tabs depend on the core calculation layer being stable                      |
| DEP6 | Internal | EVM data model           | All EVM KPIs, charts, and Monte Carlo depend on the EVMProject data model           |
| DEP7 | Internal | `.pmproj` schema         | All save/load, demo loading, and cross-tab data sharing depend on this format       |
| DEP8 | Internal | Reference sample project | Educational completeness depends on the reference sample being ready before release |

---

## 11. Success Criteria

The project is considered successfully completed when ALL of the following are verified:

1. All 24 application tabs function correctly in both UG and PG modes
2. All EVM KPIs produce verified correct results matching manual calculations
3. The reference sample project loads without errors and populates all tabs
4. The Windows executable launches and runs fully on a clean Windows 10 machine
5. The PyPI package installs and launches without errors
6. The web application returns a 200 response on its health endpoint
7. The automated test suite reports ≥ 800 passing tests with zero critical failures
8. All worked solution generators produce educationally correct step-by-step outputs
9. The project is formally closed with lessons learned captured and approved

---

## 12. Project Team (Summary)

| Role              | Name                         | Type     | Allocation       |
| ----------------- | ---------------------------- | -------- | ---------------- |
| Project Sponsor   | Dr. Karim Naguib             | Internal | Part-time (10%)  |
| Project Manager   | Ahmed Samir Khalil, PMP      | Internal | Part-time (30%)  |
| Lead Developer    | Omar Hassan El-Rashidy       | Internal | Full-time (100%) |
| Junior Developer  | Nour Ahmed Fawzy             | Internal | Part-time (50%)  |
| QA Engineer       | Sara Mostafa Abdel-Fattah    | Internal | Part-time (25%)  |
| Technical Advisor | Prof. Youssef Ibrahim Tawfik | External | Part-time (15%)  |

_Detailed resource plan is provided in the Resource Management Plan (PMHE-2025-RM-001)._

---

## Document Control

| Version      | Date       | Author             | Change Description               |
| ------------ | ---------- | ------------------ | -------------------------------- |
| 0.1 Draft    | 2025-08-25 | Ahmed Samir Khalil | Initial draft for sponsor review |
| 1.0 Approved | 2025-09-01 | Dr. Karim Naguib   | Approved at project kickoff      |
