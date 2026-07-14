# Scope Statement and WBS — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> Annotated companion to `07_scope_statement_wbs.md`.
> The WBS JSON (`data/demos/v2/pmhelper_edu_ref_wbs.json`) loads directly in the
> **Strategic → WBS** tab of PMHelper_Edu.

---

| Field               | Value                                                       |
| ------------------- | ----------------------------------------------------------- |
| **Document ID**     | PMHE-2025-SS-001-EDU                                        |
| **Companion to**    | PMHE-2025-SS-001 + pmhelper_edu_ref_wbs.json                |
| **PMBOK Alignment** | Planning: Processes 5.3 (Define Scope) and 5.4 (Create WBS) |
| **Knowledge Area**  | Scope Management                                            |

---

## What Is the Difference Between the Charter Scope and the Scope Statement?

> **📚 Core Concept**
>
> | Document                       | Purpose                                       | Detail Level                             |
> | ------------------------------ | --------------------------------------------- | ---------------------------------------- |
> | **Charter (Section 4)**        | Authorise the project; define PM authority    | High-level; fits in one page             |
> | **Scope Statement (This doc)** | Define exactly what will and won't be built   | Detailed; PM's working reference         |
> | **WBS (This doc)**             | Decompose scope into measurable work packages | Deliverable-oriented; cost/schedule base |
>
> The Charter says: "We will build PMHelper_Edu — a desktop app, web app, exe, and
> PyPI package."
>
> The Scope Statement says: "The desktop app has 24 tabs in 5 groups. It supports UG
> and PG modes. The exe runs without Python. The web app is deployed on Render.com..."
>
> The WBS says: "1.3.5 Schedule GUI Tabs costs EGP 55,000, takes 35 days, is owned by
> Lead Developer, and is currently 100% complete."
>
> Each level adds specificity without contradicting the previous.

---

## Section 3 — Scope Exclusions: Why They Matter

> **📚 Teaching Note — "Out of Scope" Is a Contractual Statement**
>
> The exclusion list does two things:
>
> 1. **Prevents scope creep**: When a faculty user asks "Can we have a mobile app?"
>    the PM can point to Exclusion E1 and say "This was explicitly excluded at
>    project initiation. A change request is required."
> 2. **Protects the PM**: If the product launches without Arabic language support,
>    and a stakeholder complains, the PM shows Exclusion E3 — signed off in the
>    charter. The PM cannot be held accountable for excluded scope.
>
> **Notice E8 (Earned Schedule calculations)**: This exclusion was added after the
> requirements analysis. It was not in the original charter scope exclusions —
> it was discovered during planning when the team found no implementation existed.
> Adding it to the Scope Statement formally captures the gap identified in the RTM.
>
> This is the feedback loop working: RTM gap analysis → Scope Statement exclusion.

---

## Section 5 — Understanding the WBS Structure

> **📚 Teaching Note — Why Organise by Deliverable Area, Not by Phase?**
>
> There are two common WBS structures:
>
> **Phase-based WBS:**
>
> ```
> 1.1 Initiation → 1.2 Planning → 1.3 Development → 1.4 Testing → 1.5 Deployment
> ```
>
> **Deliverable-based WBS (used here):**
>
> ```
> 1.1 PM → 1.2 Architecture → 1.3 V1 Features → 1.4 V2 Features → 1.5 Web → ...
> ```
>
> PMBOK recommends deliverable-based WBS because:
>
> - **Cost tracking**: You can see how much is spent on V1 vs. V2 vs. Web — not just
>   on "Phase 3" which means nothing after the project ends
> - **Scope boundary**: Each area has clear boundaries (1.3 is V1 features only;
>   1.4 is V2 features only — no ambiguity about which cost centre bears an expense)
> - **EVM compatibility**: Earned Value is computed per work package, which maps
>   directly to deliverable areas
>
> **The 100% Rule**: The WBS must cover 100% of the project scope — no more, no less.
> Sum the BACs: 130+60+280+200+120+40+140+180 = EGP 1,150,000 = BAC ✓
> Every EGP of the budget is assigned to exactly one WBS work package.

---

## Understanding the WBS Progress → EVM Connection

> **📚 Teaching Note — How WBS Progress Drives EVM**
>
> The WBS summary table in Section 6 shows:
>
> | WBS | Area      | BAC     | % Complete | EV      |
> | --- | --------- | ------- | ---------- | ------- |
> | 1.3 | V1        | 280,000 | 100%       | 280,000 |
> | 1.7 | Education | 140,000 | 25%        | 35,000  |
>
> EV = BAC × % Complete. This is the fundamental EVM formula.
>
> The WBS % complete fields (set by the responsible party) are the **inputs** to
> the EVM calculation. They are not computed by the app automatically — the PM
> must assess physical completion per work package.
>
> **This is the most common EVM mistake:** Using time elapsed as % complete.
> "We're 79% through the time budget, so we're 79% complete."
> **WRONG.** The % complete must be assessed against physical work done, not time spent.
>
> In this project:
>
> - 1.3 (V1) is 100% complete — ALL V1 features are coded, tested, and working
> - 1.7 (Education) is only 25% complete — documents are being written right now
>
> Time elapsed (79%) doesn't tell you this. The WBS assessment does.
>
> **Application exercise:** Load `pmhelper_edu_ref_wbs.json` in the WBS tab.
> Verify the progress rollup: the root node shows ~80% weighted progress.
> Change 1.7 (Educational Content) from 25% to 80% and observe how the root
> progress changes. This demonstrates the weighted average computation.

---

## The "Two Phases of Development" WBS Design

> **📚 Teaching Note — Why V1 and V2 Are Separate WBS Nodes**
>
> Notice that V1 features (1.3) and V2 features (1.4) are separate Level-2 WBS nodes.
> This is a deliberate design choice reflecting how the project evolved.
>
> V1 was planned first (EDU_V1_Plan.md, drafted March 7, 2026) and delivered at M3.
> V2 was planned after V1 was nearly complete (EDU_V2_Plan.md, April 5, 2026).
>
> By keeping them separate in the WBS:
>
> - The V1 cost (EGP 280,000) is a completed, auditable figure
> - The V2 cost (EGP 200,000) is the cost of the expansion
> - Stakeholders can evaluate the ROI of V1 vs. V2 independently
>
> **This is how real software projects work**: MVP (V1) is delivered and
> evaluated; feature expansion (V2) is then approved based on V1 outcomes.
> Treating the whole project as one flat development block would hide this.

---

## The WBS JSON File: Bridge Between Documentation and Application

> **📚 Teaching Note — The Reference Project as a Living Demo**
>
> The file `data/demos/v2/pmhelper_edu_ref_wbs.json` placed in the demo directory
> means it is immediately loadable in the **WBS tab** of the application.
>
> When a student loads this demo, they see:
>
> - A real project's WBS with accurate costs, durations, and progress
> - The description fields link to actual source code files they can inspect
> - The linked_task_id fields connect WBS work packages to CPM activities
>   (which will be populated in the Schedule document — document 9)
>
> **This is the cross-tab narrative in action**: the WBS tab, EVM tab, and schedule
> tab all refer to the same underlying project data. The reference project makes
> every tab "talk about" the same project.
>
> **Notice the linked_task_id values** (e.g., "A10", "A28"): these are placeholder
> IDs for the CPM activities that will be defined in document 9 (Schedule). Once
> the schedule is built, each WBS work package maps to one or more CPM activities,
> enabling the link from WBS deliverable → schedule task → EVM budget.

---

## WBS Status as a Project Health Indicator

> **📚 Teaching Note — Reading the Traffic Light Pattern**
>
> Looking at the WBS summary at status date (Section 6):
>
> | Status    | WBS Areas                                    | Meaning                         |
> | --------- | -------------------------------------------- | ------------------------------- |
> | ✅ 100%   | 1.2 (Arch), 1.3 (V1)                         | Closed; no more cost expected   |
> | 🟡 75-90% | 1.1 (PM), 1.4 (V2), 1.5 (Web), 1.8 (Testing) | Nearly done; small tail of work |
> | 🔴 60%    | 1.6 (Distribution)                           | Release packaging stalled       |
> | 🔴 25%    | 1.7 (Education)                              | Largest remaining work item     |
>
> A PM reading this table immediately focuses on 1.6 and 1.7.
> They don't need to review all 55 work packages individually.
>
> This is called **management by exception** — attention goes where it's needed most.
>
> Notice that 1.7 (Educational Content) at 25% represents EGP 105,000 of remaining
> work (140,000 × 75%). This is the LARGEST remaining cost item. The cost overrun
> (CPI=0.92) likely traces partly to underestimating the complexity of educational
> content creation — a lesson for future projects.

---

## 📋 Review Questions (Self-Assessment)

1. The WBS uses a deliverable-based structure (1.1 PM, 1.2 Architecture, etc.) rather
   than a phase-based structure. What are the **two** main advantages of this approach
   for EVM tracking? Can you think of a scenario where a phase-based WBS would be better?

2. The BAC values sum to EGP 1,150,000 across all 8 Level-2 areas. Verify this using
   the WBS table. This is called the **100% Rule**. Why would a WBS that sums to only
   EGP 1,050,000 be a problem for the project?

3. WBS node 1.7.6 (Reference Sample Project) has a cost of EGP 40,000 and is 25%
   complete at the status date. This means EV = EGP 10,000 and remaining work = EGP 30,000.
   At the current CPI of 0.92, what will the actual cost of completing this work package be?
   _(Formula: Estimate to Complete = Remaining Work / CPI)_

4. Why are V1 (1.3) and V2 (1.4) separate WBS nodes rather than one combined
   "Desktop Application" node? What stakeholder reporting benefit does this provide?

5. The `linked_task_id` field in the WBS JSON contains values like "A10" and "A28".
   These currently map to CPM activity IDs that will be defined in the Schedule (document 9).
   Why is this link important? What would happen to the EVM calculation if WBS work packages
   were NOT linked to CPM activities?

6. WBS node 1.8.6 (Final QA Sign-off) is 0% complete and "Not Started." Yet the
   overall Testing and QA area (1.8) is shown as 75% complete. Calculate the weighted
   progress for the 1.8 node manually using the 6 work packages and verify that it
   equals approximately 75%.

---

> **📋 Application Exercise — Load and Explore the WBS**
>
> 1. Launch PMHelper_Edu in PG mode (WBS tab is PG-only)
> 2. Navigate to **Strategic → WBS**
> 3. Click **Load Demo** and select `pmhelper_edu_ref_wbs.json`
> 4. Explore the tree structure — expand all nodes
> 5. Verify: root node shows ~80% progress; all 1.3 children show 100%
> 6. Edit WBS node 1.7 (Educational Content): change progress from 25% to 80%
> 7. Observe how the parent node and root node progress values update
> 8. What does this tell you about how the WBS rollup calculation works?

---

_Document ends. Proceed to:_ [08_wbs_dictionary.md](08_wbs_dictionary.md)
