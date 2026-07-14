# Project Charter — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> This is the annotated (Version B) companion to the professional Project Charter
> (`04_project_charter.md`). An importable JSON version (`04_project_charter.json`)
> can be loaded directly into the **Charter tab** of PMHelper_Edu via _File → Open_.

---

| Field               | Value                                                                  |
| ------------------- | ---------------------------------------------------------------------- |
| **Document ID**     | PMHE-2025-PC-001-EDU                                                   |
| **Companion to**    | PMHE-2025-PC-001 (Professional) + 04_project_charter.json (App Import) |
| **PMBOK Alignment** | Initiating Process Group — Process 4.1: Develop Project Charter        |
| **Knowledge Area**  | Integration Management                                                 |
| **Key Output**      | Formal project authorisation; PM authority granted                     |

---

## What Is the Project Charter and Why Does It Matter?

> **📚 Core Concept — The Charter Is the Most Important Document**
>
> The **Project Charter** is the _only_ document in the PMBOK process framework that
> formally authorises a project to exist. Without a signed charter:
>
> - The project manager has no authority to commit resources
> - The team has no formal basis to do the work
> - The organisation has no documented basis for the investment decision
>
> The charter is created during the **Initiating Process Group** and is one of the
> primary outputs of Process 4.1 (Develop Project Charter).
>
> **Inputs to the charter** (per PMBOK):
>
> 1. Business Case (PMHE-2025-BC-001) ← already written
> 2. Benefits Management Plan (PMHE-2025-BMP-001) ← already written
> 3. Agreements (contracts — if external; not applicable here)
> 4. Enterprise environmental factors (organisation's culture, HR policies, etc.)
> 5. Organisational process assets (templates, historical information)
>
> **Who writes the charter?** Technically the _sponsor_ or the _PMO_ initiates the
> charter. In practice, the PM usually drafts it and the sponsor approves it. This is
> an important nuance: the PM helps create their own authorisation document.
>
> **PMP exam tip:** Questions about "when the project is formally authorised" always
> refer to the signing of the Project Charter — not the Business Case, not the kickoff
> meeting, not the first status report.

---

## Section 1 — Project Identification

> **📚 Teaching Note — The Project Code**
>
> `PMHE-2025` is the project code used across _every_ subsequent document, file, and
> financial record. Consistent project codes are a basic project governance practice.
>
> Why does this matter?
>
> - Every invoice, purchase order, and contract references the project code
> - Every document has a Document ID that starts with the project code
> - When problems arise years later, the project code links everything together
>
> **Common mistake:** Projects that don't establish a project code from Day 1 find
> themselves with scattered records, inconsistent naming, and difficulty reconstructing
> history. This is a real audit risk.

---

## Section 2 — Business Case and Need

> **📚 Teaching Note — Charter vs. Business Case: What Gets Summarised**
>
> The charter does NOT reproduce the full Business Case. It summarises the _essential
> justification_ in 3–5 sentences that a new stakeholder can read in under 30 seconds.
>
> The charter says: "The investment of EGP 1,195,000 delivers an estimated 5-year NPV
> of +EGP 85,480 at a 10% discount rate."
>
> What the charter does NOT do:
>
> - Reproduce the full options analysis
> - Show the discount factor table
> - Justify every financial assumption
>
> Those details belong in the Business Case. The charter references it by document ID.
> This **referencing rather than duplicating** is a critical document management practice.
> It prevents inconsistency (if the Business Case is updated, only one document needs
> changing) and keeps the charter readable.
>
> **Exercise:** Look at the Charter's NPV statement: "+EGP 85,480 at a 10% discount
> rate." If you had not read the Business Case, would you have any doubt that this
> number is correct? What question would you ask the PM to verify it?

---

## Section 3 — Objectives

> **📚 Teaching Note — Objectives Must Be Measurable in the Charter**
>
> Notice that objectives in the charter include specific, observable targets:
>
> - "24 functional tabs" — not "many tabs"
> - "≥ 800 passing tests" — not "comprehensive testing"
> - "< 3s load time" — not "fast performance"
>
> This is a common failure point in real charters: objectives are written as aspirations
> ("deliver a high-quality product") rather than commitments ("deliver a product with
> < 2% defect rate at first release").
>
> **Why this matters at project close:** The charter is the baseline against which
> project success is judged. If objectives are vague, the sponsor can always claim
> "this isn't what I wanted" and the PM has no documented standard to point to.
>
> **PMP exam question type:** Given a charter objective, identify whether it is SMART
> or not, and explain which component is missing.

---

## Section 6 — Budget Summary

> **📚 Teaching Note — Three Layers of Budget Authority**
>
> The budget section introduces a three-level budget structure that is critical for
> understanding how PM authority works:
>
> **Level 1: Direct Cost Budget** (EGP 1,022,100)
> The actual cost of doing the work, based on resource rates and quantities.
>
> **Level 2: Budget at Completion — BAC** (EGP 1,144,752 ≈ EGP 1,150,000)
> = Direct costs + Contingency Reserve (12%)
> The PM controls this amount. They use the contingency reserve to respond to
> _identified_ risks that materialise.
>
> **Level 3: Total Authorised Budget** (EGP 1,195,000)
> = BAC + Management Reserve (EGP 50,248)
> The sponsor controls the Management Reserve. It is released only for completely
> _unexpected_ events that couldn't have been planned for.
>
> **The key distinction:**
>
> - Contingency Reserve → PM authority → planned risk response
> - Management Reserve → Sponsor authority → unknown unknowns (UFOs)
>
> **EVM implication:** The BAC used in all Earned Value calculations is
> EGP 1,150,000 (rounded). Management Reserve is NOT included in the BAC because
> it is not part of the project's planned scope.
>
> You will see this number throughout the EVM calculations in the project. When you
> load the reference project in PMHelper_Edu, the BAC field will show EGP 1,150,000.

---

## Section 7 — Budget Breakdown: Subscription Costs

> **📚 Teaching Note — Software Subscriptions as a Project Cost**
>
> Notice the software subscription line: EGP 41,600 (EGP 3,200/month × 13 months).
>
> This includes:
>
> - **GitHub Copilot**: AI coding assistant (~USD 19/month ≈ EGP 950/month)
> - **Render.com hosting**: Cloud deployment (~USD 25/month ≈ EGP 1,250/month)
> - **Domain name + SSL**: ~USD 15/year ≈ EGP 63/month
> - **Other tools**: Remaining ~EGP 937/month (documentation tools, CI minutes, etc.)
>
> The inclusion of GitHub Copilot as a project cost is educationally important. AI
> assistance is now a standard professional tool with a real cost. Projects that ignore
> this underestimate their actual cost structure.
>
> **Teaching point:** In EVM, these recurring monthly costs are part of the Actual Cost
> (AC) stream. They distribute uniformly across the project timeline, not as a lump sum.
> This means the cost baseline (time-phased PV) includes these costs spread evenly
> across periods.

---

## Section 9 — Stakeholder Table

> **📚 Teaching Note — Interest vs. Influence**
>
> The stakeholder table uses two dimensions: **Interest** and **Influence**.
>
> - **Interest**: How much does this person _care_ about the project outcome?
> - **Influence**: How much _power_ do they have to affect the project?
>
> The 2×2 Interest/Influence matrix produces four stakeholder management strategies:
>
> |                   | Low Influence | High Influence |
> | ----------------- | ------------- | -------------- |
> | **High Interest** | Keep Informed | Manage Closely |
> | **Low Interest**  | Monitor       | Keep Satisfied |
>
> Students (high interest, low influence) → **Keep Informed**: they care deeply about
> the product but have no authority over project decisions.
>
> Sponsor (high interest, high influence) → **Manage Closely**: weekly updates, early
> escalation of risks, formal milestone reviews.
>
> Prof. Youssef (medium interest, high influence) → **Keep Satisfied**: his advisory
> role can block educational content publication; engage proactively on curriculum matters.
>
> **Full stakeholder analysis is in:** PMHE-2025-SR-001 (Stakeholder Register, document 5)

---

## Section 13 — Project Manager Authority

> **📚 Teaching Note — Why PM Authority Must Be Explicit**
>
> A surprisingly common cause of project failure is the PM not knowing what they are
> and are not authorised to do. The authority section prevents this by being explicit.
>
> Notice the specific thresholds:
>
> - "Up to EGP 15,000 per line item without sponsor approval" — below this, the PM
>   can sign a purchase order. Above this, they need the sponsor.
> - "Minor scope changes < 5% effort impact" — this prevents every tiny change
>   requiring a formal meeting, while still escalating significant changes.
>
> The things that **require sponsor approval** are listed explicitly too:
>
> - Changing the end date (2026-09-30 is a hard constraint)
> - Using Management Reserve
> - Changing deliverables D1–D8
>
> **Real-world relevance:** In many projects, the PM's authority is vague or assumed.
> When an unexpected cost arises, the PM and sponsor argue about whether approval was
> needed. An explicit authority matrix prevents this argument.
>
> **RACI connection:** This authority structure will reappear in the RACI matrix
> (document 17), where the PM and sponsor are shown as A (Accountable) for different
> activities — the charter defines who is A for what.

---

## Section 14 — Approval Signatures

> **📚 Teaching Note — Why Signatures Matter**
>
> In a digital project, you might wonder why signature lines matter. In practice,
> signatures serve three functions:
>
> 1. **Commitment**: The sponsor commits to providing the budget and support described
>    in the charter. The PM commits to managing within those parameters.
> 2. **Authority transfer**: The moment the charter is signed, the PM has formal
>    authority to direct team members, commit resources, and make decisions.
> 3. **Legal and audit protection**: If disputes arise, the signed charter is the
>    documented agreement. Courts and auditors accept signed charters as evidence of
>    the agreed scope and budget.
>
> The Technical Advisor's signature is also notable — it indicates they reviewed and
> accept the educational content scope. This protects against later claims that the
> curriculum validation was not agreed.
>
> **PMP exam tip:** A common distractor question: "Who signs the project charter?"
> The correct answer is always the **Project Sponsor** (and sometimes additional
> stakeholders, but the sponsor is mandatory). The PM does not approve their own charter
> — they prepare it; the sponsor approves it.

---

## 📋 Review Questions (Self-Assessment)

1. What is the primary purpose of the Project Charter? What formal right does it grant
   that no other document grants?

2. The charter references the Business Case by document ID (PMHE-2025-BC-001) rather
   than repeating its content. Why is this referencing approach better than duplicating?
   What risk does duplication create?

3. The BAC is EGP 1,150,000 but the Management Reserve adds EGP 50,248 more. Why is
   the Management Reserve NOT included in the BAC for EVM calculations?

4. Look at the PM Authority section. The PM can approve expenditure up to EGP 15,000
   per line item. A new software tool costs EGP 18,000. What must the PM do? Draft
   a one-paragraph change request justification for this purchase.

5. Three people sign the charter: the Sponsor, the PM, and the Technical Advisor.
   In a different project, the lead developer also signs. What does this additional
   signature signify? Would you recommend it for this project? Why or why not?

6. Risk R-001 (lead developer unavailability) is listed as Low probability but Critical
   impact. Given that this is the highest-impact risk, why is its probability rated
   "Low"? Is this realistic? What evidence from the repository supports or contradicts
   this rating?

---

> **📋 Application Exercise — Load the Charter**
>
> 1. Launch PMHelper_Edu
> 2. Navigate to **Strategic → Charter**
> 3. Click **Open** and select `04_project_charter.json`
> 4. Verify that all fields are populated correctly:
>    - Project name, code, PM, sponsor, dates
>    - Business case text
>    - Budget breakdown (10 line items)
>    - 8 milestones
>    - 6 team members
>    - 7 stakeholders
>    - 5 risks
>    - 3 approval signatures
> 5. Export the charter as PDF and compare the output to `04_project_charter.md`

---

_Document ends. Proceed to:_ [05_stakeholder_register.md](05_stakeholder_register.md)
