# Requirements Traceability Matrix — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> Annotated companion to `06_requirements_traceability_matrix.md`. This document
> explains the methodology of requirements management, traceability, and gap analysis
> rather than repeating all requirement entries.

---

| Field               | Value                                                                              |
| ------------------- | ---------------------------------------------------------------------------------- |
| **Document ID**     | PMHE-2025-RTM-001-EDU                                                              |
| **Companion to**    | PMHE-2025-RTM-001 (Professional)                                                   |
| **PMBOK Alignment** | Planning: Process 5.2 (Collect Requirements); 5.3 (Define Scope); 5.4 (Create WBS) |
| **Knowledge Area**  | Scope Management                                                                   |

---

## What Is a Requirements Traceability Matrix?

> **📚 Core Concept**
>
> A **Requirements Traceability Matrix (RTM)** is a document that maps every
> requirement in a project to its origin (the business need) and its destination
> (the deliverable, test case, and application feature that satisfies it).
>
> The word "traceability" is key. It means you can trace a requirement:
>
> - **Forward**: from business need → stakeholder need → functional requirement
>   → deliverable → test case (proves requirement was met)
> - **Backward**: from a feature → requirement → business need (proves the feature
>   was justified)
>
> **Why this matters:**
>
> Without an RTM, projects commonly experience:
>
> - **Gold plating**: developers build features no stakeholder asked for
> - **Missed requirements**: a stakeholder need was never implemented
> - **Untested requirements**: a requirement was implemented but never tested
> - **Uncontrolled scope**: a change request is approved without knowing which
>   requirements it affects
>
> **PMP exam focus:** The RTM is the primary tool for _Scope Verification_ (now called
> "Validate Scope" in PMBOK 6) — the process of formally accepting deliverables.
> A deliverable is accepted when all its linked acceptance criteria are verified.

---

## Section 3 — Understanding the Requirement Hierarchy

> **📚 Teaching Note — Why Five Levels of Requirements?**
>
> The RTM uses five levels:
>
> 1. Business Requirements (BR) — the _why_
> 2. Stakeholder Requirements (SHR) — the _who wants what_
> 3. Functional Requirements (FR) — the _what the system does_
> 4. Non-Functional Requirements (NFR) — the _how well it does it_
> 5. Educational Requirements (EDU) — the _how it teaches_ (unique to this project)
>
> Each level is more specific than the previous. The connection between levels
> is where requirements management earns its value.
>
> **Example trace — CPM feature:**
>
> | Level   | Content                                                            |
> | ------- | ------------------------------------------------------------------ |
> | BR-001  | "Provide an integrated educational PM tool"                        |
> | SHR-001 | "Teach CPM with step-by-step worked solutions"                     |
> | FR-001  | "CPM forward pass: compute ES and EF for all activities"           |
> | FR-002  | "CPM backward pass: compute LS, LF, Total Float"                   |
> | EDU-001 | "Every calculation must show formula → substitution → result"      |
> | NFR-008 | "Results must match manual computation within ±0.01"               |
> | AC-001  | "Forward/backward pass correct for reference project"              |
> | AC-012  | "Worked solution matches manual computation for reference project" |
>
> Notice: BR-001 alone could justify building almost anything. SHR-001 constrains
> it to CPM specifically. FR-001/002 define _exactly_ which calculation is needed.
> EDU-001 ensures it teaches, not just computes. NFR-008 sets the accuracy bar.
> AC-001/012 are the _proof_ that the requirements were met.

---

## Section 5 — Reading the Status Column

> **📚 Teaching Note — Status as a Project Progress Tool**
>
> The status column (✅ / ⚠️ / ❌) in the functional requirements tables is more
> than documentation — it is a **real-time project progress indicator**.
>
> At version 1.2 of this document (2026-07-09 — the project status date), most
> requirements show ✅. Only FR-047 and EDU-005 remain ⚠️.
>
> **Why is this useful?**
>
> - The PM can report to the Sponsor: "58 of 60 functional requirements are met"
> - The QA engineer can report: "13 of 15 acceptance criteria are verified"
> - The team can focus on the two remaining gaps without distraction
>
> This is the RTM functioning as a **Scope Performance Measurement** tool.
> Compare this to EVM: just as EV measures completed work value, the RTM measures
> completed requirement coverage.
>
> **The gap between planned (60 requirements) and completed (58) is measurable.**
> This gap is the basis for FR-047 and EDU-005 appearing in the project schedule's
> remaining work (Phase 7 tasks).

---

## Section 6 — Educational Requirements as Cross-Cutting Concerns

> **📚 Teaching Note — What Makes EDU Requirements Special**
>
> Notice that EDU-001 applies to "FR-001 to FR-034" — every single calculation feature.
> This is called a **cross-cutting concern** in software engineering: a requirement
> that is not specific to one feature but must be satisfied by all of them.
>
> Other examples of cross-cutting concerns:
>
> - Security (every function must validate inputs — not just the login page)
> - Logging (every action should be logged — not just errors)
> - Accessibility (every UI element must be keyboard-navigable)
>
> EDU-001 (worked solutions) and EDU-002 (Try It Yourself) are the educational
> versions of security and logging — they must be present in every calculation,
> not just added to a few prominent ones.
>
> **PMBOK alignment:** Cross-cutting requirements are often called **quality
> requirements** in PM terminology. They appear in the Quality Management Plan
> (document 13) as quality standards that all deliverables must meet.

---

## Section 7 — Non-Functional Requirements (NFRs)

> **📚 Teaching Note — NFRs vs. FRs: The "How Well" vs. "What"**
>
> Students frequently confuse NFRs with FRs. The test is:
>
> **FR**: "The system computes CPM forward pass." (What it does)
> **NFR**: "The computation completes in under 10 seconds for 600 activities." (How well)
>
> NFRs are often called **quality attributes** or **"-ility" requirements**:
>
> - **Perform**ance (NFR-001, NFR-002, NFR-003, NFR-010)
> - **Availab**ility (NFR-004)
> - **Secur**ity (NFR-005, NFR-006)
> - **Reliab**ility / Accuracy (NFR-008)
> - **Compat**ibility (NFR-009)
>
> NFRs are notoriously hard to test because they require infrastructure and measurement
> tools, not just functional verification. NFR-002 ("600 activities within 10 seconds")
> requires a large test project and a timer — it cannot be verified by unit testing alone.
>
> **This is why NFR-002 has its own acceptance test** (the 600-activity demo projects
> committed in the repository are specifically sized to test this requirement).

---

## Section 8 — Technical Requirements vs. Design Decisions

> **📚 Teaching Note — When Does a Design Decision Become a Requirement?**
>
> TR-001 says: "GUI must be implemented in Python Tkinter." This looks like a
> design decision — but it has been elevated to a Technical Requirement because:
>
> 1. It is enforced by a formal constraint (C4 in the charter)
> 2. It has specific traceability to academic environment compatibility (BR-001)
> 3. Changing it would require a formal change request and scope change
>
> Technical requirements are design choices that have been **formally approved**
> and **cannot be changed without a change request**.
>
> Compare to an ordinary design decision: "We use NetworkX for graph algorithms."
> This is an implementation detail the developer chose. It is not a requirement.
> It could be changed without affecting any stakeholder's needs.
>
> **The distinction matters for change control.** A change to TR-001 (switch to Qt)
> would require sponsor approval because it affects constraint C4. A change to the
> internal graph library is a developer decision.

---

## Section 9 — Acceptance Criteria Are Testable Commitments

> **📚 Teaching Note — Why AC Must Be Binary**
>
> Every acceptance criterion must be answerable with "Pass" or "Fail" — never
> "Mostly" or "Almost."
>
> Compare:
>
> - **Bad AC**: "Application should be reasonably fast" — not testable
> - **Good AC**: "CPM analysis on 600 activities completes in <10 seconds" — testable
>
> Look at AC-003: "RAG colour codes apply correctly for CPI=0.92, SPI=1.02
> (expected: amber/green)." This specifies exact input values and expected output.
> The tester runs the reference project at the status date, reads the KPI cards,
> and verifies amber on CPI and green on SPI.
>
> **Why specify exact values?** Because "CPI ≈ 0.92" in the EVM snapshot is a
> **designed scenario** — the reference project data was constructed so that CPI
> would be approximately 0.92 at the 2026-07-09 status date. This means the
> acceptance criterion can be validated against both the application output AND
> the manually computed expected value.
>
> This is a key educational design principle: the reference project's EVM data is
> not arbitrary — it was designed to produce specific, verifiable KPI values.

---

## Section 10 — Reading the Traceability Summary Matrix

> **📚 Teaching Note — Coverage Analysis**
>
> The summary matrix in Section 10 shows 6 out of 8 Business Requirements with
> "Full" coverage and 2 with "In Progress." This is called **Requirements Coverage**.
>
> A mature PM practice uses this matrix for three types of analysis:
>
> **1. Completeness Analysis** (forward from BRs):
> "Is every business requirement satisfied by at least one deliverable?"
> BR-003 and BR-004 are "In Progress" → their deliverable D5 is not yet complete.
>
> **2. Necessity Analysis** (backward from deliverables):
> "Is every deliverable justified by at least one business requirement?"
> This prevents gold plating. If a feature can't be traced to a BR, it shouldn't exist.
>
> **3. Test Coverage Analysis** (forward from FRs):
> "Is every functional requirement tested by at least one test case?"
> The 800+ test cases in the test suite are the evidence for this analysis.
> The CI/CD pipeline enforces this every time code changes.

---

## Section 11 — Gap Analysis as a Living Tool

> **📚 Teaching Note — The RTM Is Not a One-Time Document**
>
> Notice the version history (Section 12): the RTM has been updated 4 times during
> the project. Each update reflects the project's state at that point:
>
> - v0.1 (Sept 8): Kickoff — requirements from charter only
> - v1.0 (Oct 15): Architecture milestone — full FRs added
> - v1.1 (Mar 25): V1 feature-complete — 31 FRs marked ✅
> - v1.2 (Jul 9): Status date — 2 FRs still in progress
>
> **This versioning is not administrative overhead.** Each version captures the
> requirements state at a specific moment, enabling two important practices:
>
> 1. **Change impact assessment**: When a change request arrives, the PM can look up
>    which requirements are affected before approving
> 2. **Lessons learned**: At project close, the final RTM shows exactly which
>    requirements were delivered, which were deferred, and which were discovered
>    mid-project (indicating requirements definition was incomplete at start)
>
> **The "Future Development" items in Section 11** are also significant: they represent
> requirements that were identified during the project but deferred to V3. These become
> the starting point for the next project's RTM.

---

## 📋 Review Questions (Self-Assessment)

1. FR-047 ("Load reference project as in-app demo") is marked ⚠️ In Progress at the
   status date. Using the RTM, identify: which Business Requirement does this unmet
   FR affect? Which Acceptance Criteria cannot be verified until FR-047 is complete?

2. What is the difference between a Functional Requirement and a Non-Functional
   Requirement? Using one example from this RTM, explain how both types can apply
   to the same application feature.

3. EDU-003 states: "UG mode must hide advanced features (PESTEL, DPCI, Charter Mgr,
   RACI, SWOT)." Looking at the repository source code, where is this implemented?
   _(Hint: search for `_PG_ONLY_TABS` in `main_window_edu.py`.)_ Does the implementation
   match the requirement exactly, or does it differ? Explain the discrepancy.

4. The RTM records NFR-008: "All calculation results must match manually computed
   reference values within ±0.01." Propose a test case that would verify this NFR
   for the EVM module. Specify: test inputs, expected outputs, and pass/fail criterion.

5. Section 11 lists FR-052 (Earned Schedule) as a future development item with
   "High" priority. Write a complete Functional Requirement entry for FR-052 in the
   same format as the existing FR entries, including: the linked SHR, the linked BR,
   the targeted deliverable, and the acceptance criterion.

6. The RTM has 58 requirements marked ✅ and 2 marked ⚠️. As PM, what do you report
   to the sponsor this week regarding requirements completion? Write a 3-sentence
   status report that is accurate, concise, and decision-enabling.

---

_Document ends. Proceed to:_ [07_scope_statement.md](07_scope_statement.md)
