# Benefits Management Plan — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> This is the annotated (Version B) companion to the professional Benefits Management
> Plan (`03_benefits_management_plan.md`). Read the professional version first to
> understand the structure, then use this version to understand the reasoning behind
> each section.

---

| Field                      | Value                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------ |
| **Document ID**            | PMHE-2025-BMP-001-EDU                                                                            |
| **Companion to**           | PMHE-2025-BMP-001 (Professional Version)                                                         |
| **PMBOK Alignment**        | Initiating Process Group; extends into Closing and post-project operations                       |
| **Knowledge Area**         | Integration Management — Benefits Realisation Management                                         |
| **Supported App Features** | Financial Analysis tab (track B1–B3); no direct tab for BMP, but supports Dashboard KPI thinking |

---

## What Is a Benefits Management Plan?

> **📚 Core Concept**
>
> The **Business Case** asks: "Should we do this project?"
> The **Project Charter** asks: "Are we authorised to start?"
> The **Benefits Management Plan** asks: "How will we know the project was worth doing?"
>
> These are three _different_ questions. A project can deliver everything on time and on
> budget yet still fail to deliver business value. The Benefits Management Plan is the
> document that closes this loop — it defines _what will be measured, when, and by whom,
> long after the project team has disbanded._
>
> **PMBOK 6th Edition** introduced explicit guidance on Benefits Management as part of
> the Project Integration Management knowledge area. PMBOK 7th Edition reinforces this
> under the principle of "Demonstrating Value."
>
> **PMP exam focus:** Questions about benefits management often test whether students
> understand that benefit realisation is a **post-project responsibility**. The project
> team delivers; the organisation measures and harvests.

---

## Section 1 — Purpose

> **📚 Teaching Note — Why the Plan Must Extend Beyond Project Close**
>
> Notice that this plan includes a monitoring schedule extending to Q3 2031 — five
> years after project completion. This is intentional.
>
> Most project benefits in software products do **not** materialise during the project.
> They materialise during the _operations_ period that follows. A project that builds an
> educational tool realises its value when students use it and institutions pay for it —
> not when the code is deployed.
>
> This creates an important distinction:
>
> - **Project success** = delivered on time, on budget, to scope
> - **Benefit realisation** = the organisation achieves the value that justified the investment
>
> A project can be a project success but a benefits failure (if no one adopts the product).
> A project can also be a delivery failure (over budget, late) but still a benefits success
> (if the product was good enough and the market adopted it anyway).
>
> **Real-world example:** The Sydney Opera House was massively over budget and late —
> a project delivery failure. But it is arguably one of Australia's most successful
> investments in brand, tourism, and culture — a benefits success.

---

## Section 2 — Benefits Summary

> **📚 Teaching Note — Financial vs. Non-Financial Benefits**
>
> The benefits summary table separates:
>
> - **Financial benefits** (B1, B2, B3): Can be expressed in EGP with a target value
> - **Non-financial benefits** (B4–B8): Strategic, reputational, or capability benefits
>   that are real but cannot be directly expressed as EGP
>
> This distinction matters because:
>
> 1. Financial benefits justify the investment (they feed the NPV calculation)
> 2. Non-financial benefits often matter _more_ to decision-makers but are harder to
>    prove — which is why they must still be measured, even if qualitatively
>
> **Student exercise:** Look at B7 ("Foundation for future products"). This benefit is
> listed as "Not quantified" in the 5-year target column. How would you attempt to
> quantify it? One approach: estimate the cost EduTech Dynamics would save by reusing
> PMHelper_Edu components in a future product (reduced development time × developer rate).
>
> **PMP exam tip:** The Benefits Register (Section 3 below) is the detailed companion
> to the Benefits Summary table. Examiners often ask which document contains specific
> benefit measurements, owners, or measurement methods — that is the Benefits Register.

---

## Section 3 — Benefits Register

> **📚 Teaching Note — Anatomy of a Benefit Register Entry**
>
> Each benefit register entry answers six questions:
>
> 1. **What** is the benefit? (Description)
> 2. **How much** is it worth? (Measurement unit + targets)
> 3. **When** will it appear? (Realisation start + timeline)
> 4. **Who** is responsible? (Benefit Owner)
> 5. **How** will it be measured? (Measurement method)
> 6. **What could stop it?** (Risk/dependencies)
>
> Notice that **Benefit Owners** are named individuals with clear accountability. Vague
> ownership ("the organisation will track this") is a common weakness in real-world
> benefits plans that leads to benefits never being measured.

### Deep Dive: B2 — Faculty Time Savings

> **📚 Why "Avoided Cost" Is a Real Financial Benefit**
>
> B2 (Faculty Time Savings) is classified as "Financial — Avoided Cost." This requires
> explanation because no money actually flows to EduTech Dynamics. The benefit accrues
> to adopting institutions.
>
> **Why it still belongs in the Business Case:**
>
> - The total value created by the project includes value for all stakeholders
> - Faculty time savings justify _institutional adoption_ — which drives B1 (licensing revenue)
> - Quantifying avoided cost makes the argument to faculty buyers: "By adopting this tool,
>   your department saves EGP X per year"
>
> **The measurement approach (faculty survey) is important.** Rather than claiming
> EGP 100,000/year as a definite number, the plan commits to _measuring_ actual time saved
> through faculty feedback surveys. This is intellectual honesty — the Business Case
> used an estimate; the Benefits Plan converts it to a measured outcome.

### Deep Dive: B4 — Brand Establishment

> **📚 Measuring Brand Through Proxy Indicators**
>
> B4 cannot be directly valued in EGP, but it can be tracked through **proxy indicators**:
>
> - GitHub stars (a publicly visible signal of developer awareness)
> - Mentions in university syllabi (adoption signal)
> - Academic papers (recognition by the research community)
>
> These are called **leading indicators** — they predict future financial value
> (institutional adoption) before the revenue actually arrives.
>
> This concept maps directly to the **Earned Value** framework: GitHub stars are a
> leading indicator, just as SPI is a leading indicator of schedule performance.
> Both tell you early whether you're on track, before the final outcome is confirmed.
>
> **PMP exam link:** Benefits with non-financial measures often require a **measurement
> methodology** to be defined upfront. The plan defines this methodology per benefit,
> which is a required practice in benefits management frameworks.

---

## Section 4 — Benefits Realisation Timeline

> **📚 Teaching Note — The J-Curve of Investment Returns**
>
> The benefits timeline shows a pattern common to all investment projects:
>
> ```
> Value
>   │
>   │                              ╭─────── cumulative benefits
>   │                        ╭────╯
>   │                   ╭────╯
>   0 ─────────────────────────────────── time
>   │  ─────project─────│← post-project →
>   │                   payback at 3.8 years
>   │──────investment
> ```
>
> This is called the **J-Curve** (or Investment Return Curve) in project finance.
> The initial period shows negative cash flow (the investment); positive returns
> accumulate later.
>
> **Key insight for students:** When a project manager reports "we delivered on time and
> on budget," the J-curve reminds us this is only the first part of the story. The project
> was a cost centre for 13 months. The organisation will not recover that investment until
> approximately mid-2029.
>
> This timeline appears nowhere in the Gantt chart or CPM schedule. It is a separate
> planning artefact that extends beyond project close — which is why a Benefits
> Management Plan is a distinct document from the project schedule.

---

## Section 5 — Roles and Responsibilities

> **📚 Teaching Note — The Benefits Owner Is Not the Project Manager**
>
> In many small organisations, the Project Manager is incorrectly made responsible for
> benefits realisation after the project ends. This is a governance error.
>
> The **Benefits Owner** is a business stakeholder (typically the sponsor) who:
>
> - Has authority to allocate operational budget to maintain the product
> - Is accountable to the organisation for delivering the promised return
> - Continues after the project team has moved on
>
> The **PM's role in benefits management ends at project closure.** The PM transfers
> the benefits monitoring plan and baseline measurements to the Benefits Owner as part
> of the closure process.
>
> In this project:
>
> - **Ahmed (PM)** is responsible for _creating_ the plan and tracking during the project
> - **Dr. Karim (Sponsor/Benefits Owner)** is responsible for _measuring and reporting_
>   benefits for 5 years after project close
>
> This separation is a PMBOK best practice that prevents benefits measurement from being
> quietly abandoned when the PM moves to their next project.

---

## Section 6 — Benefits Monitoring Schedule

> **📚 Teaching Note — Post-Project Reviews Are Contractual Obligations**
>
> Notice the monitoring schedule has a formal review at Q3 2029 ("Year 3 — payback
> verification"). This review has a specific purpose: to confirm whether the payback
> period projection of 3.8 years was accurate, or to update the forecast.
>
> If actual adoption has been slower than projected, this review triggers a decision:
>
> - Continue current approach (if on-track)
> - Increase marketing/outreach investment (if behind)
> - Revise the financial model downward (if the market has not responded)
>
> This is analogous to a **Forecast EAC** in Earned Value Management — it is a
> mid-project (in this case, mid-operations) check on whether the original estimate
> is still valid.
>
> **PMP exam link:** Project governance frameworks (including Prince2, which influenced
> PMBOK 7) require formal **benefit reviews at defined intervals** post-project.
> These are sometimes called "Post-Implementation Reviews" or "Post-Project Reviews."

---

## Section 7 — Benefits Assumptions and Constraints

> **📚 Teaching Note — Assumption BA5 Is the Most Critical**
>
> BA5 states: _"EduTech Dynamics invests ≥ EGP 60,000/year in product maintenance
> post-release."_ This is a constraint, not just an assumption. Without ongoing
> maintenance:
>
> - Python version compatibility breaks over time
> - Security vulnerabilities accumulate
> - New PM curriculum requirements go unmet
> - The product becomes abandonware within 2–3 years
>
> This is called **Total Cost of Ownership (TCO)** — the lifecycle cost of an asset
> includes not just the initial investment but the ongoing maintenance cost.
>
> The Business Case's NPV analysis did NOT include post-project maintenance costs.
> A more rigorous NPV would subtract EGP 60,000/year from the benefit stream for
> Years 1–5, reducing the NPV to approximately:
>
> NPV_revised ≈ 85,480 − (60,000 × PV annuity factor @ 10%, 5 yrs)
> NPV_revised ≈ 85,480 − (60,000 × 3.791) ≈ 85,480 − 227,460 = **−EGP 141,980**
>
> This would make the investment financially marginal at best. The project sponsor is
> aware of this and has committed to the maintenance investment in the Benefits Plan.
>
> **This is a deliberate educational choice:** The slightly optimistic Business Case
> (which didn't include maintenance costs) vs. the more cautious Benefits Plan (which
> does) teaches students that financial models are always simplified, and that
> assumptions deserve scrutiny.

---

## Section 8 — Transition to Benefits Realisation

> **📚 Teaching Note — Closing the Loop on Benefits**
>
> The transition section formalises the handover from the project to operations.
> Without this formal handover:
>
> - The PM's final report says "done" and moves on
> - The sponsor forgets what was measured and what wasn't
> - Benefits measurement never starts
>
> The "Benefits Baseline Report" at project closure is especially important.
> It captures the _starting point_ for each non-financial benefit:
>
> - How many GitHub stars does the project have on release day? (B4 baseline)
> - What is the skills matrix score at project close? (B6 baseline)
> - How many external contributors exist on release day? (B8 baseline)
>
> Without a baseline, you cannot measure improvement. This is the same principle
> as EVM's **Baseline** in the schedule: without a planned baseline, you cannot
> compute Schedule Variance.

---

## 📋 Review Questions (Self-Assessment)

1. What is the difference between the Business Case and the Benefits Management Plan?
   At what point in the project lifecycle is each document primarily used?

2. The project has a payback period of 3.8 years. However, if EGP 60,000/year in
   maintenance costs are included, the NPV becomes negative. Does this mean the project
   should not have been approved? What factors might still justify it?

3. B4 (Brand Establishment) is measured through "GitHub stars" as a proxy indicator.
   What are the limitations of using GitHub stars as a measure of academic adoption?
   Propose one alternative or complementary indicator.

4. Who is responsible for benefits realisation after the project closes — the PM
   or the sponsor? What happens in practice when there is no formal Benefits Owner
   designated? Why is this a governance failure?

5. The benefits timeline shows that B7 (Foundation for Future Products) does not
   realise until Q1 2027. Why does this benefit appear later than B4 (Brand) and B8
   (Community), even though all three are non-financial? What must happen first?

6. Critically evaluate assumption BA4: "Open-source MIT license does not attract a
   competing fork that diverts adoption." Is this a realistic concern? Research one
   real-world example of an open-source project that was forked by a competitor.
   What happened to the original project's market position?

---

_Document ends. Proceed to:_ [04_project_charter.md](04_project_charter.md)
