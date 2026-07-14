# Procurement Register, Change Control Log, and Lessons Learned

## PMHelper_Edu Development Project — Sections 16, 20, 27

| Field            | Value                                                     |
| ---------------- | --------------------------------------------------------- |
| **Document ID**  | PMHE-2025-PROC-001 / PMHE-2025-CCL-001 / PMHE-2025-LL-001 |
| **Project Code** | PMHE-2025                                                 |
| **Version**      | 1.1 — Active                                              |
| **Organization** | EduTech Dynamics                                          |
| **Last Updated** | 2026-07-09                                                |

---

## Section 16 — Procurement Register

| ID    | Item                                                 | Type                  | Vendor                       | Contract              | Monthly Cost | Annual Cost | Period              | Status           |
| ----- | ---------------------------------------------------- | --------------------- | ---------------------------- | --------------------- | ------------ | ----------- | ------------------- | ---------------- |
| P-001 | GitHub Copilot (AI coding assistant)                 | Software Subscription | GitHub / Microsoft           | Monthly SaaS          | EGP 950      | EGP 11,400  | Sep 2025 – Sep 2026 | ✅ Active        |
| P-002 | Render.com Starter Web Hosting                       | Cloud Hosting         | Render Inc.                  | Monthly PaaS          | EGP 1,250    | EGP 15,000  | Apr 2026 – ongoing  | ✅ Active        |
| P-003 | Domain Name Registration (1 year)                    | Domain                | Namecheap                    | Annual renewal        | —            | EGP 750     | Apr 2026            | ✅ Paid          |
| P-004 | SSL Certificate (Let's Encrypt via Render)           | Security Certificate  | Render / Let's Encrypt       | Included with hosting | —            | EGP 0       | Apr 2026 – ongoing  | ✅ Active (free) |
| P-005 | Development Laptop — Lead Developer                  | Hardware              | Local vendor                 | One-time purchase     | —            | EGP 35,000  | Sep 2025            | ✅ Delivered     |
| P-006 | Development Monitor (27") — Lead Developer           | Hardware              | Local vendor                 | One-time purchase     | —            | EGP 8,000   | Sep 2025            | ✅ Delivered     |
| P-007 | Test Device — Windows 10 Clean VM                    | Hardware / Software   | Oracle VirtualBox (free)     | Free                  | —            | EGP 0       | Oct 2025            | ✅ Active        |
| P-008 | Test Device — Secondary Windows Laptop               | Hardware              | Local vendor                 | One-time purchase     | —            | EGP 22,000  | Oct 2025            | ✅ Delivered     |
| P-009 | Microsoft Office 365 (documentation)                 | Software Subscription | Microsoft                    | Monthly               | EGP 200      | EGP 2,400   | Sep 2025 – Sep 2026 | ✅ Active        |
| P-010 | GitHub Pro (private repositories)                    | Software Subscription | GitHub                       | Monthly               | EGP 100      | EGP 1,200   | Sep 2025 – Sep 2026 | ✅ Active        |
| P-011 | PyPI Package Registry (free)                         | Platform              | Python Software Foundation   | Free                  | —            | EGP 0       | Aug 2026            | ✅ Registered    |
| P-012 | Prof. Youssef Technical Advisory Retainer            | Professional Services | Prof. Youssef Ibrahim Tawfik | Monthly retainer      | EGP 2,500    | EGP 32,500  | Sep 2025 – Sep 2026 | ✅ Active        |
| P-013 | PMP Study Materials (PMBOK 6th Ed. + guides)         | Training Materials    | PMI / Amazon                 | One-time              | —            | EGP 6,000   | Sep 2025            | ✅ Delivered     |
| P-014 | Online PM Certification Reference (PMP Prep)         | Training Materials    | PM PrepCast / Udemy          | One-time              | —            | EGP 3,000   | Sep 2025            | ✅ Delivered     |
| P-015 | GitHub Copilot Chat (upgrade to enterprise features) | Software              | GitHub                       | One-time add-on       | —            | EGP 2,500   | Jan 2026            | ✅ Active        |

**Total Procurement Spend:** EGP 140,750 _(actual vs. budget EGP 136,600 — 3.1% over)_

**Procurement Notes:**

- All software tools are SaaS/PaaS — no long-term vendor lock-in
- Domain registered at EGP 750 (budgeted EGP 1,000 — EGP 250 under budget)
- Hardware procured locally at competitive pricing; all within budget
- No external development contractors required (contingency reserve untouched for procurement)

---

## Section 20 — Change Control Log

| CR #   | Date       | Title                                                          | Requested by         | Impact                                                                     | Decision     | Approved by        | Date Closed |
| ------ | ---------- | -------------------------------------------------------------- | -------------------- | -------------------------------------------------------------------------- | ------------ | ------------------ | ----------- |
| CR-001 | 2026-01-15 | Expand V2 demo datasets from 6 to 11 calculator-specific files | Omar Hassan          | Schedule: +5 days; Cost: +EGP 8,000; Scope: +5 JSON files in 1.7.4         | Approved     | Ahmed Samir Khalil | 2026-04-10  |
| CR-002 | 2026-02-08 | Add RACI Deliverable×Department matrix (second RACI type)      | Prof. Youssef        | Schedule: +3 days; Cost: +EGP 5,000; Scope: raci_deliv added to .pmproj    | Approved     | Ahmed Samir Khalil | 2026-03-01  |
| CR-003 | 2026-03-20 | Add AOA (Activity-on-Arrow) network mode alongside AON         | Dr. Karim Naguib     | Schedule: +10 days; Cost: +EGP 15,000; Scope: aoa_network_builder.py added | Approved     | Dr. Karim Naguib   | 2026-06-01  |
| CR-004 | 2026-04-05 | Include DPCI Assessment Tab in V2 (originally planned for V3)  | Prof. Youssef        | Schedule: +8 days; Cost: +EGP 12,000; Scope: dpci_tab.py added             | Approved     | Dr. Karim Naguib   | 2026-06-15  |
| CR-005 | 2026-04-20 | Add medium-scale demo datasets (UG/PG 150-task)                | Ahmed Samir Khalil   | Schedule: +8 days; Cost: +EGP 10,000; Scope: 2 new demo files              | Approved     | Ahmed Samir Khalil | 2026-05-20  |
| CR-006 | 2026-05-10 | Request mobile application (iOS) for V2                        | Faculty Beta Partner | Schedule: +60 days; Cost: +EGP 200,000; Out of scope per E1                | **Rejected** | Ahmed Samir Khalil | 2026-05-12  |
| CR-007 | 2026-06-01 | Add Foundations (L1) and PM Role (L3) reference tabs           | Dr. Karim Naguib     | Schedule: +10 days; Cost: +EGP 8,000; Scope: 2 educational reference cards | Approved     | Dr. Karim Naguib   | 2026-06-25  |

**Approved changes total impact:** Schedule: +44 days absorbed through schedule buffer; Cost: +EGP 58,000 (absorbed in contingency reserve)

**Rejected changes:** CR-006 (mobile app) — deferred to V3 roadmap per exclusion E1

**Change control lessons:**

- CR-003 (AOA network) significantly improved educational value; the 10-day investment was well justified
- CR-006 rejection illustrates scope control: a technically feasible request correctly deferred because it was explicitly excluded from scope
- Total approved change cost (EGP 58,000) is the primary contributor to the CPI=0.92 overrun alongside underestimated educational content complexity

---

## Section 27 — Lessons Learned Register

| LL #   | Phase        | Category     | Lesson                                                                                                                                                                                                                                                       | Recommendation for Future Projects                                                                                                                                                                                                            |
| ------ | ------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LL-001 | Planning     | Estimation   | Educational content (worked solutions, annotations, review questions) was severely underestimated at approximately 60% of budgeted time. The reference project alone required 30+ working days vs. 20 days estimated.                                        | For educational software projects: apply a 1.5× multiplier to any estimate involving curriculum-aligned content creation. Technical implementation is predictable; educational quality is not.                                                |
| LL-002 | Monitoring   | EVM          | The CPI trend was visible at Month 4 (CPI=0.95) but not acted upon. By Month 10, CPI had deteriorated to 0.92. TCPI=1.53 at Month 10 makes budget recovery impossible.                                                                                       | Establish a CPI alarm threshold at 0.95. If CPI falls below 0.95 for two consecutive months, mandatory corrective action meeting with sponsor.                                                                                                |
| LL-003 | Planning     | Risk         | Risk R-003 (PyInstaller/scipy) was identified as Medium probability but the specific failure mode (scipy.stats.\_distn_infrastructure.py NameError) was not documented. Resolution required significant debugging time.                                      | For Python packaging projects: create a PyInstaller compatibility test in the CI/CD pipeline from Day 1. Do not wait until the distribution phase to discover build issues.                                                                   |
| LL-004 | Architecture | Technical    | The single EduProjectState shared-state pattern (Decision #6) enabled all tabs to use the same data model. This architectural decision was correct and saved significant integration effort in V1 and V2.                                                    | Document and enforce the shared-state pattern from project initiation. Tabs that bypass the shared state create integration defects that are expensive to debug.                                                                              |
| LL-005 | Execution    | Scope        | Approved change CR-003 (AOA network) added the most educational value of all changes but also required 18 days of development. The educational value justified the cost.                                                                                     | When evaluating change requests, include an "Educational Value Score" alongside schedule and cost impact. For educational software, high educational value may justify overrun that financial analysis alone would reject.                    |
| LL-006 | Execution    | Resources    | The 30% PM allocation was insufficient during Phase 7 (V2 development) when stakeholder management intensity peaked with faculty partner engagement, CR processing, and Prof. Youssef review cycles simultaneously.                                          | For phases where multiple change requests and stakeholder reviews coincide, increase PM allocation to 50% for those specific months. Budget the capacity surge in the original resource plan.                                                 |
| LL-007 | Planning     | Stakeholders | SR-013 (University IT Departments) was identified as a stakeholder but no direct engagement was planned. The AV-safe manifest and no-admin-rights requirement addressed their concerns through product design rather than relationship management.           | For every stakeholder in the "Keep Satisfied" quadrant: determine whether engagement is through relationship or through product design. Product design is more scalable than individual relationship management for large stakeholder groups. |
| LL-008 | Execution    | Technology   | GitHub Copilot's contribution to development velocity was greater than the 30-40% estimate used in planning. The actual multiplier appears closer to 2x for well-structured, documented codebases.                                                           | Update AI-assistance velocity assumptions for future projects. The quality of the codebase documentation (DECISIONS.md, pure function architecture, comprehensive tests) is what enables AI tools to be effective — not the AI tool alone.    |
| LL-009 | Architecture | Data         | The decision to use 0-based period indices (not calendar dates) in the EVM data model simplified calculations but made data entry non-intuitive for non-technical users. Faculty beta testers struggled to understand "Period 6" vs. "Month 7 (March 2026)". | In the next version, consider adding a `start_date` field to the EVMProject model and auto-computing period labels as calendar months. The calculation layer can remain index-based; only the display layer needs dates.                      |
| LL-010 | Closure      | Benefits     | The Benefits Management Plan identified B2 (Faculty Time Savings) as a key benefit but measurement requires faculty survey data that cannot be collected until product is in use. The plan correctly specified semi-annual surveys starting Q3 2026.         | Always include a benefits baseline measurement at project closure, even for non-financial benefits. At minimum, record B4 (GitHub stars), B6 (skills matrix), and B8 (contributors) on the day of release to enable future comparison.        |

---

## Document Control

| Document                  | Version | Date       | Author | Status                                |
| ------------------------- | ------- | ---------- | ------ | ------------------------------------- |
| Procurement Register (16) | 1.1     | 2026-07-09 | PM     | Active                                |
| Change Control Log (20)   | 1.0     | 2026-07-09 | PM     | Active (3 months remaining)           |
| Lessons Learned (27)      | 1.0     | 2026-07-09 | PM     | Active — will be finalized at closure |
