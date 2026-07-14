# Project Charter

## PMHelper_Edu Development Project

| Field             | Value                   |
| ----------------- | ----------------------- |
| **Document ID**   | PMHE-2025-PC-001        |
| **Project Code**  | PMHE-2025               |
| **Version**       | 1.0 — Approved          |
| **Status**        | Approved and Active     |
| **Prepared by**   | Ahmed Samir Khalil, PMP |
| **Approved by**   | Dr. Karim Naguib        |
| **Organization**  | EduTech Dynamics        |
| **Approval Date** | 2025-09-01              |

> This charter formally authorises the PMHelper_Edu Development Project and assigns
> Ahmed Samir Khalil as Project Manager with authority to apply organisational resources
> to project activities.

---

## 1. Project Identification

| Field                       | Value                                                  |
| --------------------------- | ------------------------------------------------------ |
| **Project Name**            | PMHelper_Edu — Educational Project Management Software |
| **Project Code**            | PMHE-2025                                              |
| **Project Manager**         | Ahmed Samir Khalil, PMP                                |
| **Project Sponsor**         | Dr. Karim Naguib, Co-Founder & CTO, EduTech Dynamics   |
| **Start Date**              | 2025-09-01                                             |
| **Planned End Date**        | 2026-09-30                                             |
| **Organisation**            | EduTech Dynamics — Cairo, Egypt                        |
| **Business Case Reference** | PMHE-2025-BC-001                                       |

---

## 2. Business Case and Need

EduTech Dynamics has identified a market gap in project management education.
University students, postgraduate candidates, and CAPM/PMP exam candidates lack access
to an integrated, interactive tool that covers the full quantitative PM curriculum with
step-by-step educational scaffolding.

Commercial alternatives (Microsoft Project, Oracle Primavera) are prohibitively expensive
and operationally complex for educational settings. Free tools are fragmented and cover
single techniques only.

This project will produce **PMHelper_Edu** — a purpose-built educational application
covering 24 PM topic areas, distributed as:

- A Python/Tkinter desktop application (free, open-source, MIT licence)
- An Angular web application deployed on Render.com
- A standalone Windows executable (no Python required)
- A PyPI package (`pip install pmhelper`)

The investment of EGP 1,195,000 delivers an estimated 5-year NPV of +EGP 85,480 at
a 10% discount rate (IRR ≈ 12.4%, Payback ≈ 3.8 years). Strategic benefits include
brand establishment in the MENA academic market and internal capability building.

_Full financial analysis:_ PMHE-2025-BC-001

---

## 3. Project Objectives

| ID  | Objective                               | Measure                                               | Target    | Deadline   |
| --- | --------------------------------------- | ----------------------------------------------------- | --------- | ---------- |
| O1  | Deliver operational desktop application | 24 functional tabs; all tests passing                 | 100%      | 2026-08-15 |
| O2  | Dual-mode educational scaffolding       | Worked solutions and Try It Yourself in all calc tabs | All tabs  | 2026-08-15 |
| O3  | Production web deployment               | Public URL; <3s load; 99%+ uptime                     | Live      | 2026-07-31 |
| O4  | Desktop exe and PyPI distribution       | Clean Windows 10 launch; pip install works            | Both live | 2026-08-31 |
| O5  | Comprehensive test suite                | ≥ 800 passing; zero critical defects                  | Verified  | 2026-09-15 |
| O6  | Reference sample project                | Loads in-app; covers all 24 tabs                      | Complete  | 2026-09-30 |

---

## 4. Project Scope

### In Scope

- Desktop application: 24 educational tabs (CPM, PERT, EVM, Risk, Monte Carlo, Crashing,
  Resource Leveling, RCPS, Financial Analysis, Cost Estimation, Factor Scoring, Three-Point
  Estimation, AON/AOA Networks, SWOT, PESTEL, WBS, RACI, Charter, DPCI, Dashboard)
- Angular web frontend and FastAPI/SQLAlchemy backend
- Cloud deployment (Render.com), Windows executable (PyInstaller), PyPI package
- GitHub Actions CI/CD pipeline (automated testing and release)
- Comprehensive test suite (≥ 800 tests)
- Complete reference sample project and all in-app demo datasets
- Educational worked solutions for all calculation features

### Out of Scope

- Mobile application (iOS/Android)
- LMS integration (Moodle, Canvas)
- Arabic-language UI
- Paid subscription features in initial release
- Dedicated server infrastructure
- macOS/Linux installers

---

## 5. Deliverables

| ID  | Deliverable              | Planned Date | Acceptance Criteria                                      |
| --- | ------------------------ | ------------ | -------------------------------------------------------- |
| D1  | Desktop application v1.0 | 2026-08-15   | All 24 tabs functional; 800+ tests; PyInstaller verified |
| D2  | Web application v1.0     | 2026-07-31   | Deployed on Render.com; health endpoint OK; API tested   |
| D3  | Windows executable       | 2026-08-31   | Runs on clean Windows 10 without Python                  |
| D4  | PyPI package             | 2026-08-31   | `pip install pmhelper` installs and GUI launches         |
| D5  | Reference sample project | 2026-09-30   | Loadable; consistent across all 24 tabs                  |
| D6  | Test suite ≥ 800 tests   | 2026-09-15   | CI/CD pipeline green; zero critical failures             |
| D7  | User documentation       | 2026-09-30   | README, deployment guide, quick-start published          |
| D8  | Educational content      | 2026-08-15   | All worked solution generators implemented and tested    |

---

## 6. Milestones

| #   | Milestone                                     | Target Date |
| --- | --------------------------------------------- | ----------- |
| M1  | Project kickoff complete                      | 2025-09-08  |
| M2  | Core architecture established                 | 2025-10-15  |
| M3  | V1 desktop feature-complete                   | 2026-03-25  |
| M4  | Web frontend v1 deployed to production        | 2026-05-15  |
| M5  | V2 desktop feature-complete (all 24 tabs)     | 2026-06-30  |
| M6  | Production distribution (exe + PyPI) verified | 2026-08-31  |
| M7  | Reference sample project complete             | 2026-09-30  |
| M8  | Project closure                               | 2026-09-30  |

---

## 7. Budget Summary

| Category                                                     | Amount (EGP)  |
| ------------------------------------------------------------ | ------------- |
| Personnel — Lead Developer (full-time, 13 months)            | 494,000       |
| Personnel — Junior Developer (50%, 8 months)                 | 144,000       |
| Personnel — Project Manager / BA (30%, 13 months)            | 130,000       |
| Personnel — QA Engineer (25%, 7 months)                      | 52,500        |
| Personnel — Technical Advisor (15%, 13 months)               | 65,000        |
| Software subscriptions (Copilot, Render, domain, SSL, tools) | 41,600        |
| Hardware (development + testing equipment)                   | 73,000        |
| Training and certification materials                         | 22,000        |
| **Subtotal (direct costs)**                                  | **1,022,100** |
| **Contingency Reserve (12%)**                                | **122,652**   |
| **Budget at Completion (BAC)**                               | **1,144,752** |
| **Management Reserve (held by Sponsor)**                     | **50,248**    |
| **Total Authorised Budget**                                  | **1,195,000** |

_The Project Manager controls the BAC (EGP 1,144,752 rounded to EGP 1,150,000 for EVM).
The Sponsor controls the Management Reserve (EGP 50,248)._

---

## 8. Project Team

| Role              | Name                         | Allocation | Responsibilities                                                        |
| ----------------- | ---------------------------- | ---------- | ----------------------------------------------------------------------- |
| Project Sponsor   | Dr. Karim Naguib             | 10%        | Strategic direction; sponsor decisions; Management Reserve approval     |
| Project Manager   | Ahmed Samir Khalil, PMP      | 30%        | Schedule, cost, scope, risk, stakeholder, communications management     |
| Lead Developer    | Omar Hassan El-Rashidy       | 100%       | Full-stack development; architecture; CI/CD; technical decisions        |
| Junior Developer  | Nour Ahmed Fawzy             | 50%        | Feature development support; testing; documentation                     |
| QA Engineer       | Sara Mostafa Abdel-Fattah    | 25%        | Test design, execution, defect tracking, test suite maintenance         |
| Technical Advisor | Prof. Youssef Ibrahim Tawfik | 15%        | PM curriculum validation; educational content review; academic guidance |

---

## 9. Key Stakeholders

| Stakeholder                  | Organisation        | Role                  | Interest                                      | Influence       |
| ---------------------------- | ------------------- | --------------------- | --------------------------------------------- | --------------- |
| Dr. Karim Naguib             | EduTech Dynamics    | Sponsor / CTO         | Product success and revenue                   | High / High     |
| Ahmed Samir Khalil           | EduTech Dynamics    | Project Manager       | Delivery on time/cost                         | High / High     |
| Omar Hassan El-Rashidy       | EduTech Dynamics    | Lead Developer        | Technical quality; manageable scope           | High / High     |
| Nour Ahmed Fawzy             | EduTech Dynamics    | Junior Developer      | Learning; clear tasks                         | Medium / Low    |
| Sara Mostafa Abdel-Fattah    | EduTech Dynamics    | QA Engineer           | Quality standards; testable deliverables      | Medium / Medium |
| Prof. Youssef Ibrahim Tawfik | Partner University  | Technical Advisor     | Educational correctness; academic credibility | Medium / High   |
| University Faculty           | Target institutions | End users (primary)   | Time saving; curriculum alignment             | Low / High      |
| Undergraduate Students       | Target institutions | End users (secondary) | Ease of use; correct results                  | High / Low      |
| Postgraduate Students        | Target institutions | End users (secondary) | Advanced features; exam relevance             | High / Low      |
| CAPM/PMP Candidates          | General market      | End users (tertiary)  | Exam preparation value                        | Medium / Low    |

_Full Stakeholder Register: PMHE-2025-SR-001_

---

## 10. Constraints

| #   | Constraint                                                                        |
| --- | --------------------------------------------------------------------------------- |
| C1  | Product must be usable by the 2026–2027 academic year (hard deadline: 2026-09-30) |
| C2  | Total expenditure cannot exceed EGP 1,195,000 (all reserves included)             |
| C3  | Maximum 2.0 FTE equivalent — no additional full-time hires                        |
| C4  | Desktop must use Python 3.8+ and Tkinter only                                     |
| C5  | Primary platform: Windows 10+ 64-bit                                              |
| C6  | Must be released under MIT Licence                                                |
| C7  | Desktop application must function fully offline                                   |

---

## 11. Assumptions

| #   | Assumption                                                              |
| --- | ----------------------------------------------------------------------- |
| A1  | GitHub Copilot licence available throughout the project                 |
| A2  | Render.com starter tier sufficient for initial deployment               |
| A3  | Python 3.8+ compatibility sufficient for target academic environments   |
| A4  | Windows 10+ remains the dominant OS in university computer labs         |
| A5  | PyPI publication approval is straightforward for an open-source package |
| A6  | Lead developer can sustain required pace with AI assistance             |
| A7  | Angular frontend can reuse Python logic via FastAPI backend             |

---

## 12. Key Risks

| ID    | Risk                                                   | Probability | Impact   | Response                                                                                  |
| ----- | ------------------------------------------------------ | ----------- | -------- | ----------------------------------------------------------------------------------------- |
| R-001 | Lead developer becomes unavailable for extended period | Low         | Critical | Cross-training; comprehensive documentation; GitHub history as knowledge base             |
| R-002 | Scope creep from new PM curriculum requirements        | Medium      | High     | Formal change control process; PM has authority to defer new requirements to next version |
| R-003 | Adoption lower than projected                          | Medium      | High     | Free open-source model reduces adoption barrier; monitor from Month 6                     |
| R-004 | GitHub Copilot becomes unavailable                     | Low         | High     | Document alternative AI tools; fallback to traditional development                        |
| R-005 | PyPI publication rejected                              | Very Low    | Medium   | GitHub Releases as fallback distribution channel                                          |

_Full Risk Register: PMHE-2025-RR-001_

---

## 13. Project Manager Authority

The Project Manager (Ahmed Samir Khalil) is authorised to:

- Approve expenditure up to EGP 15,000 per line item without sponsor approval
- Approve minor scope changes (< 5% effort impact) without a formal change request
- Negotiate directly with external vendors for services within the approved budget
- Add team members at part-time capacity without sponsor approval, within budget
- Approve schedule changes of up to 2 weeks without escalation

The following require sponsor approval:

- Any change to the project end date (2026-09-30)
- Any expenditure from the Management Reserve
- Any change to the core project scope (deliverables D1–D8)
- Team composition changes affecting FTE allocation

---

## 14. Approval Signatures

By signing below, the Project Sponsor formally authorises this project and grants the
Project Manager the authority described in Section 13.

| Role              | Name                         | Signature  | Date       |
| ----------------- | ---------------------------- | ---------- | ---------- |
| Project Sponsor   | Dr. Karim Naguib             | _[signed]_ | 2025-09-01 |
| Project Manager   | Ahmed Samir Khalil, PMP      | _[signed]_ | 2025-09-01 |
| Technical Advisor | Prof. Youssef Ibrahim Tawfik | _[signed]_ | 2025-09-01 |

---

## 15. Document Control

| Version      | Date       | Author             | Change                                 |
| ------------ | ---------- | ------------------ | -------------------------------------- |
| 0.1 Draft    | 2025-08-22 | Ahmed Samir Khalil | Initial draft                          |
| 0.2 Review   | 2025-08-28 | Dr. Karim Naguib   | Budget and authority sections revised  |
| 1.0 Approved | 2025-09-01 | Dr. Karim Naguib   | Signed and approved at kickoff meeting |

---

_Supporting documents:_
_Business Case: PMHE-2025-BC-001 | Benefits Plan: PMHE-2025-BMP-001_
_Stakeholder Register: PMHE-2025-SR-001 | Risk Register: PMHE-2025-RR-001_
