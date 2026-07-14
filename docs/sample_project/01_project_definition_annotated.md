# Project Definition — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> This is the annotated (Version B) companion to the professional Project Definition
> (`01_project_definition.md`). Every section is followed by a teaching note explaining
> _why_ it is structured this way, _which PMBOK process_ it supports, and _what a student
> should learn_ from it. Yellow-highlighted passages in an exam context would be prime
> locations for CAPM/PMP questions.

---

| Field                      | Value                                   |
| -------------------------- | --------------------------------------- |
| **Document ID**            | PMHE-2025-PD-001-EDU                    |
| **Companion to**           | PMHE-2025-PD-001 (Professional Version) |
| **Educational Level**      | UG + PG                                 |
| **PMBOK Alignment**        | Initiating Process Group                |
| **Primary Knowledge Area** | Integration Management                  |

---

## Section 1 — Project Identification

| Field               | Value                                                         |
| ------------------- | ------------------------------------------------------------- |
| **Project Name**    | PMHelper_Edu — Educational Project Management Software        |
| **Project Code**    | PMHE-2025                                                     |
| **Project Manager** | Ahmed Samir Khalil, PMP                                       |
| **Project Sponsor** | Dr. Karim Naguib, Co-Founder and CTO, EduTech Dynamics        |
| **Organization**    | EduTech Dynamics — Cairo, Egypt                               |
| **Classification**  | New Product Development \| Software \| Educational Technology |

> **📚 Teaching Note — Project Identification**
>
> Every project must have a **unique code** for referencing across documents, reports, and
> financial systems. In this case `PMHE-2025` follows the convention:
>
> - `PM` = PMHelper
> - `HE` = Edu (Edu edition identifier)
> - `2025` = start year
>
> **PMBOK alignment:** This section feeds directly into the **Project Charter** (Section 4.1
> of PMBOK 6th / Section 2.1 of PMBOK 7th), which is the formal authorisation document.
>
> **PMP exam tip:** The Project Manager is identified here _before_ the charter is issued.
> This is intentional — in practice, the PM is often involved in drafting the very charter
> that authorises their own appointment. The sponsor formally authorises the project.

---

## Section 2 — Problem Statement

> **📚 Teaching Note — Why a Problem Statement Comes First**
>
> The **Problem Statement** is the single most important entry in the Project Definition.
> It justifies the existence of the project. A project without a clear problem being solved
> is a project at risk of scope creep and sponsor withdrawal.
>
> A well-written problem statement follows the structure:
>
> 1. **Context** — What is the current situation?
> 2. **Problem** — What is wrong or missing?
> 3. **Impact** — Why does it matter?
>
> Notice that the problem statement in the professional version does NOT yet propose a
> solution. Solutions are proposed in the Business Case (next document).
>
> **Common student mistake:** Writing a problem statement that already assumes the solution
> ("We need to build software to..."). The problem statement must describe the problem in
> isolation first.
>
> **PMBOK alignment:** The Problem Statement is the foundation of the **Business Case**
> (Process 4.1 — Develop Project Charter inputs).

Project management education at university level consistently suffers from a gap between
theoretical instruction and practical application. Students learn CPM, PERT, Earned Value
Management, risk analysis, and resource leveling through textbook formulas and manual
exercises. They have no access to integrated tools that:

- Perform these calculations interactively
- Show step-by-step worked solutions
- Demonstrate how all PM techniques connect within a single project narrative
- Scale from undergraduate basics to postgraduate depth in the same interface

Commercial alternatives (Microsoft Project, Primavera P6, Oracle Fusion) are expensive,
licensed per seat, operationally complex, and not designed to teach PM concepts — they
assume existing PM knowledge. Free tools are fragmented, cover only one technique each,
and provide no educational scaffolding.

> **📚 Competitive Context Note**
>
> The problem statement identifies _existing alternatives_ and explains _why they are
> insufficient_. This is a critical component of the Business Case options analysis that
> follows. A PM must be able to answer the question: "Why not just buy an existing product?"
>
> For CAPM/PMP candidates: This approach aligns with the **needs assessment** described in
> the PMBOK Guide as a precursor to the Business Case.

---

## Section 3 — Project Purpose and Strategic Justification

> **📚 Teaching Note — Linking Project to Organisational Strategy**
>
> The PMBOK Guide emphasises that projects must be tied to **organisational strategy**.
> A project that cannot demonstrate strategic alignment is a candidate for cancellation
> during portfolio review.
>
> This section answers the question: "Why is _this organisation_ the right one to do
> _this project_ at _this time_?"
>
> Note the three-part structure:
>
> 1. **What the product does** (scope summary)
> 2. **How it addresses the problem** (value proposition)
> 3. **How it aligns with business strategy** (strategic justification)
>
> **PMP exam focus:** Strategic alignment is tested frequently. Questions may describe a
> project and ask whether it should proceed based on its strategic fit.

EduTech Dynamics will develop **PMHelper_Edu** — a purpose-built educational software
application that covers the complete quantitative project management curriculum from
undergraduate to postgraduate level.

Strategic alignment:

- Positions EduTech Dynamics as an education technology leader in the MENA region
- Generates institutional licensing revenue from universities and training centres
- Establishes the brand within the project management academic community
- Creates a foundation for future premium features and courseware integration

---

## Section 4 — Project Objectives

> **📚 Teaching Note — SMART Objectives**
>
> Project objectives must be **SMART**:
>
> - **S**pecific — clearly defined, no ambiguity
> - **M**easurable — a number or observable condition that can be verified
> - **A**chievable — realistic given resources and time
> - **R**elevant — aligned with the project purpose
> - **T**ime-bound — a specific deadline
>
> Study the table below and notice:
>
> - Each objective has a _specific_ measure (e.g. "24 functional tabs" not "many tabs")
> - Each objective has a _target_ that is binary or numeric (pass/fail or a number)
> - Each objective has a _deadline_ that falls before the project end date
>
> **Common student mistake:** Writing vague objectives like "Build a good application."
> This is not SMART. A good test: Can the sponsor look at this objective on the end date
> and say "Yes, we achieved it" or "No, we did not"?
>
> **PMP exam tip:** Objectives flow directly into the _Scope Statement_ (what we produce)
> and into _Acceptance Criteria_ (how we verify). You will see these links in later documents.

| #   | Objective                                                                           | Measure                                                           | Target                          | Deadline   |
| --- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------- | ---------- |
| O1  | Deliver a fully operational desktop application covering all planned PM topic areas | 24 functional tabs, all passing automated tests                   | 100% tab functionality          | 2026-08-15 |
| O2  | Support UG and PG learning modes with educational scaffolding                       | Worked solutions and Try It Yourself mode in all calculation tabs | All calculation tabs dual-mode  | 2026-08-15 |
| O3  | Deploy a production web application at a stable public URL                          | Application reachable at production domain with <3s load time     | 99%+ uptime over 30-day period  | 2026-07-31 |
| O4  | Publish a standalone Windows exe and PyPI package                                   | PyPI published; exe verified on clean Windows 10 VM               | Both distribution channels live | 2026-08-31 |
| O5  | Achieve and maintain a comprehensive automated test suite                           | Passing tests count; zero critical defects                        | ≥ 800 tests passing             | 2026-09-15 |
| O6  | Deliver a complete reference sample project                                         | Reference project loadable in-app, consistent across all 24 tabs  | 100% feature coverage           | 2026-09-30 |

> **📚 Note on Objective Sequencing**
>
> Notice that O3 (web deployment) has a deadline of 2026-07-31 — earlier than O1 and O2
> (desktop completion: 2026-08-15). This is intentional and reflects the actual project
> history: the web version was deployed as a milestone in its own right, while desktop
> development continued in parallel.
>
> This teaches an important scheduling concept: **parallel streams**. In a real project,
> the web team and desktop team can work concurrently after shared architecture is
> established, shortening the overall project duration.

---

## Section 5 — Project Scope

> **📚 Teaching Note — Scope Definition**
>
> The scope section answers two questions:
>
> 1. **What IS included?** (In Scope)
> 2. **What is explicitly NOT included?** (Out of Scope)
>
> Both are equally important. The Out of Scope list prevents **scope creep** — the tendency
> for stakeholders to add requirements incrementally. When a stakeholder asks "Can we also
> have a mobile app?", the PM points to the Out of Scope list.
>
> **Key principle:** Anything not explicitly listed as In Scope should be treated as Out of
> Scope by default. But the best practice is to explicitly list the most likely omissions
> to prevent misunderstandings.
>
> **PMBOK alignment:** This section is the high-level input to the **Scope Statement**
> (Process 5.3 — Define Scope) and to the **WBS** (Process 5.4 — Create WBS). You will
> see these expand in the WBS document.

### 5.1 In Scope (Summary)

- Desktop application with 24 tabs: calculation engines, strategic tools, visualisations
- Web application (Angular + FastAPI + database)
- Production cloud deployment (Render.com)
- Windows executable (PyInstaller) and PyPI package
- Automated test suite (800+ tests)
- Complete reference sample project
- All educational content: worked solutions, Try It Yourself, demo datasets

### 5.2 Out of Scope

- Mobile application (iOS or Android)
- LMS integration (Moodle, Canvas, Blackboard)
- Arabic-language user interface
- Premium subscription features during initial release
- Dedicated server infrastructure
- macOS / Linux installer packages
- Real-time multi-user collaboration

> **📚 Note on the "Arabic UI" Out of Scope Decision**
>
> It might seem natural that an Egyptian educational software company would offer an
> Arabic interface. The decision to exclude it was a deliberate **scope constraint** —
> not a permanent product decision.
>
> This is an example of a **deferred scope item**: it belongs in the product backlog for
> a future version, not this project. The Project Definition does not prevent a future
> project from adding it.
>
> Teaching point: Scope decisions are always made within a **triple constraint trade-off**.
> Adding Arabic UI would require more time (translators, testing), more budget, and
> potentially more complexity. At the current budget and timeline, it was deferred.

---

## Section 6 — Key Deliverables

> **📚 Teaching Note — Deliverables vs. Objectives**
>
> Students often confuse **objectives** (what we want to achieve) with **deliverables**
> (what we physically produce).
>
> - Objective O1: "Deliver a fully operational desktop application" — this is a _goal_
> - Deliverable D1: "Desktop application v1.0" — this is the _tangible product_
>
> The acceptance criteria column is critical. It must be specific enough that a QA
> engineer can verify it without asking for interpretation.
>
> **PMBOK alignment:** The deliverables table is the direct input to the **WBS Dictionary**
> (a WBS work package becomes a deliverable when it reaches the lowest meaningful level
> of decomposition with clear acceptance criteria).

| #   | Deliverable                | WBS Ref | Acceptance Criteria                                                    |
| --- | -------------------------- | ------- | ---------------------------------------------------------------------- |
| D1  | Desktop application v1.0   | 1.3     | All 24 tabs functional; 800+ tests passing; PyInstaller build verified |
| D2  | Web application v1.0       | 1.4     | Deployed on Render.com; health endpoint 200; API tested                |
| D3  | Windows executable package | 1.5.1   | Launches on clean Windows 10 VM; no Python required                    |
| D4  | PyPI package               | 1.5.2   | Installable via `pip install pmhelper`; GUI launches                   |
| D5  | Reference sample project   | 1.6     | Loadable in-app; consistent across all 24 tabs                         |
| D6  | Test suite                 | 1.3.4   | ≥ 800 passing tests; CI/CD pipeline green                              |
| D7  | User documentation         | 1.6.3   | README, deployment guide, quick-start guide published                  |
| D8  | Educational content        | 1.6.4   | All worked solution generators implemented and tested                  |

---

## Section 7 — Milestones

> **📚 Teaching Note — Milestones**
>
> A **milestone** is a significant event in the project schedule — it has zero duration
> and marks the completion of a phase or a decision point.
>
> Notice that milestones are listed with **target dates** and **predecessors**. In the
> CPM/Gantt chart, these become zero-duration tasks at the end of each phase.
>
> **Key distinction:** A milestone is NOT a deliverable. M3 ("V1 feature-complete") is
> the _event_ of completing V1. D1 ("Desktop application v1.0") is the _product_ produced.
>
> **PMP exam tip:** Milestones are used in **stakeholder communications** — they appear in
> status reports and dashboards. They are the checkpoints that the sponsor monitors most
> closely. A slipping milestone is an early warning of schedule risk.

| #   | Milestone                              | Target Date | Key Predecessor |
| --- | -------------------------------------- | ----------- | --------------- |
| M1  | Project kickoff complete               | 2025-09-08  | —               |
| M2  | Core architecture established          | 2025-10-15  | M1              |
| M3  | V1 feature-complete (desktop)          | 2026-03-25  | M2              |
| M4  | Web frontend v1 deployed to production | 2026-05-15  | M3              |
| M5  | V2 feature-complete (all 24 tabs)      | 2026-06-30  | M4              |
| M6  | Production build (exe + PyPI) verified | 2026-08-31  | M5              |
| M7  | Reference sample project complete      | 2026-09-30  | M6              |
| M8  | Project closure                        | 2026-09-30  | M7              |

---

## Section 8 — Constraints

> **📚 Teaching Note — Constraints vs. Assumptions**
>
> These two concepts are frequently tested on PMP and CAPM exams. The distinction is:
>
> - A **constraint** is a _known, confirmed limitation_ that the project cannot change.
>   It is a fact, not a guess.
> - An **assumption** is something _believed to be true_ for planning purposes, which has
>   not yet been confirmed. Assumptions carry risk — if they turn out to be wrong,
>   the project is affected.
>
> In the table below, notice that constraints often come with an **impact** column —
> this is best practice because it documents _why_ the constraint matters for planning.
>
> **Real-world tip:** Constraints are negotiated _before_ the project starts. If a PM
> later claims "I couldn't deliver because of budget constraints", but those constraints
> were known at kickoff, the PM should have raised a change request when the constraint
> became binding — not after the fact.

| #   | Category     | Constraint                                               | Planning Impact                                                         |
| --- | ------------ | -------------------------------------------------------- | ----------------------------------------------------------------------- |
| C1  | Schedule     | Product usable by the 2026–2027 academic year            | Fixes 2026-09-30 as a hard deadline                                     |
| C2  | Budget       | Total expenditure ≤ EGP 1,195,000 including all reserves | Limits team size and tool choices                                       |
| C3  | Resources    | Maximum 2.0 FTE equivalent                               | Lead developer is the single critical resource — no slack in resourcing |
| C4  | Technology   | Desktop must use Python 3.8+ and Tkinter                 | Preserves compatibility with academic Python environments               |
| C5  | Platform     | Primary target: Windows 10+ 64-bit                       | Aligns with university lab standard; other platforms are best-effort    |
| C6  | Licensing    | Must be released under MIT License                       | Required for free academic adoption; prevents proprietary forks         |
| C7  | Connectivity | Desktop must function fully offline                      | University networks may restrict internet access                        |

---

## Section 9 — Assumptions

> **📚 Teaching Note — Assumption Risk**
>
> Each assumption should be linked to a **risk**. If the assumption turns out to be false,
> what happens? This is why the "If Wrong — Impact" column exists.
>
> When you build the risk register, you will often find that most risks originate from
> assumptions that may not hold. This is one of the most important practical skills a PM
> develops: converting vague assumptions into explicit risks with probability and impact
> estimates.
>
> **Exercise for students:** Look at assumption A6 ("A single lead developer can sustain
> the required development pace with AI assistance"). What is the probability that this
> assumption is wrong? What would happen if the lead developer became unavailable for
> 4 weeks? This analysis will appear in the Risk Register (document 15).

| #   | Assumption                                              | If Wrong — Impact                                              |
| --- | ------------------------------------------------------- | -------------------------------------------------------------- |
| A1  | GitHub Copilot license available throughout             | Development velocity decreases ≈ 40%; schedule risk HIGH       |
| A2  | Render.com starter tier sufficient                      | Additional cloud costs: +EGP 15,000–25,000/year; budget risk   |
| A3  | Python 3.8+ compatibility sufficient                    | Rework for older lab Python versions; scope risk               |
| A4  | Windows 10+ dominates in target university labs         | Platform support scope expands; cost and schedule risk         |
| A5  | PyPI publication straightforward for open-source        | Distribution delay of 2–4 weeks; minor schedule risk           |
| A6  | Single lead developer can sustain pace with AI assist   | Most critical assumption — if wrong, entire schedule collapses |
| A7  | Angular frontend can reuse Python logic via FastAPI API | Significant rework if backend bridging is not feasible         |
| A8  | Render.com response times acceptable for MENA users     | UX degradation; may require CDN layer; cost risk               |

---

## Section 10 — Dependencies

> **📚 Teaching Note — External Dependencies as Schedule Risk**
>
> Dependencies on _external parties_ are among the highest-risk schedule items because
> the project team cannot directly control them. Notice that all high-criticality external
> dependencies (GitHub, Render.com, PyPI) are for infrastructure the project depends on
> but does not own.
>
> **Best practice:** For each external dependency, a PM should ask:
>
> 1. What happens if this dependency is unavailable?
> 2. Is there a fallback?
> 3. Should we include this in the risk register?
>
> DEP1 (GitHub) — fallback: GitLab self-hosted
> DEP2 (Render.com) — fallback: Heroku, Railway, Fly.io
> DEP3 (PyPI) — fallback: GitHub Releases for direct download

---

## Section 11 — Success Criteria

> **📚 Teaching Note — Success Criteria vs. Acceptance Criteria**
>
> - **Acceptance Criteria** (per deliverable) — what the customer checks before accepting
>   a specific output (e.g., "the exe launches on Windows 10")
> - **Success Criteria** (project level) — what defines overall project success across
>   all objectives and deliverables
>
> The success criteria in this document are deliberately binary: each can be answered
> "Yes" or "No" at project close. This is how a **Project Closure Report** validates
> whether the project succeeded.
>
> **PMP exam tip:** In the Closing process group, the PM compares the final product/service
> against the success criteria established at project initiation. If an objective was
> not met, it must be documented in the lessons learned register.

---

## Section 12 — Project Team

> **📚 Teaching Note — Team Composition in a Small Startup**
>
> Notice the allocation percentages. The Lead Developer (Omar Hassan El-Rashidy) is the
> only full-time resource at 100%. Everyone else is part-time. This is typical of a small
> software startup where:
>
> - The PM wears multiple hats (PM + BA + stakeholder manager)
> - The sponsor is also technically involved (CTO role)
> - QA is part-time because testing follows development peaks
>
> **Resource planning implication:** The Lead Developer is a **critical resource** with
> **zero resource float**. If Omar is unavailable for even 2 weeks, the project schedule
> shifts by 2 weeks. This appears in the Risk Register as risk R-002.
>
> **Organisational structure:** EduTech Dynamics operates as a **projectised organisation**
> — the project team reports directly to the Project Sponsor/CTO. There are no functional
> managers to negotiate resource allocation with. This gives the PM high authority but
> means there is no backup pool to draw from.

---

## 📋 Review Questions (Self-Assessment)

> Use these questions to test your understanding of this document before proceeding to
> the Business Case.

1. What is the difference between a project constraint and a project assumption? Give one example of each from this document.
2. List three ways the project objectives are SMART. Which objective do you think is the most difficult to measure, and why?
3. Why is the Lead Developer identified as a critical resource risk? What would you recommend to mitigate this?
4. The Out of Scope list includes "Arabic-language UI." Write a 2-sentence justification for why this was deferred, referencing the triple constraint.
5. Milestone M4 (web frontend deployed) has a deadline of 2026-07-31, which is before the desktop completion milestone M3 (2026-08-15). Wait — M4 comes _after_ M3. Explain the scheduling logic: why did the web deployment come before the final desktop version was locked?

---

_Document ends. Proceed to:_ [02_business_case.md](02_business_case.md)
