# Business Case — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> This is the annotated (Version B) companion to the professional Business Case
> (`02_business_case.md`). Teaching notes appear after each major section. For best
> learning, read the professional version first, then return to this version to understand
> the _why_ behind each choice.

---

| Field                              | Value                                                             |
| ---------------------------------- | ----------------------------------------------------------------- |
| **Document ID**                    | PMHE-2025-BC-001-EDU                                              |
| **Companion to**                   | PMHE-2025-BC-001 (Professional Version)                           |
| **PMBOK Alignment**                | Initiating Process Group — Input to Develop Project Charter (4.1) |
| **Knowledge Area**                 | Integration Management + Financial Analysis                       |
| **Supported Application Features** | Financial Analysis tab (NPV, IRR, Payback, ROI, PI)               |

---

## Section 1 — Executive Summary

> **📚 Teaching Note — Why the Executive Summary Comes First**
>
> Senior stakeholders and project sponsors often read _only_ the Executive Summary.
> It must therefore stand alone as a complete mini-document:
>
> - **What is the problem?** (one sentence)
> - **What is the recommendation?** (one sentence)
> - **What does it cost?** (one number)
> - **What is the financial return?** (key metrics)
>
> The financial summary table serves a specific purpose: a busy decision-maker can
> approve or reject the project from this table alone, without reading the full analysis.
> This is called **management-by-exception** — if the numbers look acceptable, they
> approve; if something looks wrong, they read deeper.
>
> **PMP exam tip:** The Business Case is an _input_ to the Develop Project Charter process.
> The charter is the _output_. The Business Case justifies _why_ the project exists;
> the Charter formally authorises it to proceed.

---

## Section 2 — Problem Statement

> **📚 Teaching Note — Structure of a Strong Problem Statement**
>
> Notice the problem statement is divided into three parts:
>
> **2.1 The Education Gap** — This describes the _current state_ (what is happening now)
> and the _desired state_ (what should be happening). The gap between these two states
> defines the problem.
>
> **2.2 Evidence of the Gap** — A Business Case must be evidence-based. Simply stating
> "there is a gap" is insufficient. Good PMs quantify:
>
> - How many hours are being wasted? (4–8 hours per course)
> - What does the alternative cost? (USD 600–3,000 per seat)
>
> **2.3 Cost of Inaction** — This is the most overlooked section. The PM must answer:
> "What happens if we do nothing?" If inaction has no cost, there is no urgency to
> approve the project.
>
> **Student exercise:** For your own university's PM course, estimate the cost of inaction.
> How many hours does your lecturer spend creating exercise solutions manually each semester?
> What is that time worth? This is the "doing nothing" cost.

---

## Section 3 — Strategic Context

> **📚 Teaching Note — Strategic Alignment and Portfolio Management**
>
> The Business Case must connect the project to the **organisational strategy**. This is
> the foundation of **Portfolio Management** — organisations should only fund projects
> that advance their strategic goals.
>
> PMI's Standard for Portfolio Management states that portfolio components (projects and
> programs) must be ranked by their strategic alignment. Projects with higher alignment
> scores receive funding priority.
>
> In this case, PMHelper_Edu scores highly on:
>
> - Market positioning (educational tech in MENA — direct alignment)
> - Revenue diversification (institutional licensing — new revenue stream)
> - Capability building (internal technical skills — indirect alignment)
>
> **Real-world application:** When you present a project proposal to leadership, always
> open with "This project advances Strategy X because..." before discussing costs or
> features. Leaders approve projects for strategic reasons, not technical ones.

---

## Section 4 — Options Analysis

> **📚 Teaching Note — Why You Must Always Analyse Multiple Options**
>
> The **Options Analysis** section is one of the most important tests of a PM's
> analytical rigour. A Business Case that presents only one option (the one the PM
> already wants to do) is not a Business Case — it is a justification.
>
> A rigorous Business Case always includes:
>
> - **Option 0 — Do Nothing:** The baseline. Establishes the cost of inaction.
> - **At least two alternative approaches:** Different strategies, not just different vendors.
> - **A recommended option with justification.**
>
> Notice the three dimensions evaluated for each option:
>
> 1. **Cost** — total cost of ownership over a comparable period
> 2. **Benefits** — what value it delivers
> 3. **Limitations** — why it might not be the best choice
>
> **PMP exam tip:** The Options Analysis is the most common reason a Business Case is
> rejected and sent back for revision. Sponsors who see only one option immediately
> ask "Did you consider alternatives?" Having a well-documented Options Analysis
> prevents this conversation.

### Option Comparison Summary

| Criterion           | Option 0 (Do Nothing) | Option 1 (License) | Option 2 (Commission) | Option 3 (Build) |
| ------------------- | --------------------- | ------------------ | --------------------- | ---------------- |
| 5-Year Cost (EGP)   | 0                     | ~1,405,000         | ~1,420,000–1,820,000  | 1,195,000        |
| Internal IP created | None                  | None               | Partial               | Full             |
| Revenue potential   | None                  | None               | Limited               | High             |
| Educational value   | Low (status quo)      | Low (wrong tool)   | High                  | High             |
| Strategic alignment | None                  | Low                | Medium                | High             |
| **Recommended?**    | ❌                    | ❌                 | ❌                    | ✅               |

> **📚 Note on Option 1 (Licensing) Total Cost**
>
> The 5-year licensing cost (EGP ~1,405,000) actually _exceeds_ the cost of building
> the product internally (EGP 1,195,000). This is a common and counter-intuitive finding
> in Buy vs. Build analyses for software products.
>
> The reason: Software licenses are **recurring costs**. A one-time build cost amortises
> over years; licensing costs compound.
>
> This is a direct teaching point for the **Financial Analysis** tab. Load these numbers
> into the application and observe how NPV, payback period, and ROI compare between
> options.

---

## Section 5 — Financial Analysis

> **📚 Teaching Note — This is the Application's Financial Analysis Tab in Action**
>
> The numbers in this section are specifically designed to be loaded into the
> **Financial Analysis tab** of PMHelper_Edu. The input data matches the
> `FinancialInputs` data model:
>
> ```
> initial_investment = 1,195,000
> cash_flows = [180,000, 290,000, 380,000, 430,000, 480,000]
> discount_rate = 0.10
> ```
>
> The application will compute and verify: Payback Period, Discounted Payback,
> NPV, IRR, ROI, and Profitability Index — all shown in this document with
> manual calculations so students can verify the application output.

### 5.1 Net Present Value — Step-by-Step Explanation

**What NPV measures:** The total value created by an investment in today's money.
A positive NPV means the investment creates more value than it costs (accounting for
the time value of money).

**The Time Value of Money principle:** EGP 1,000 received today is worth _more_ than
EGP 1,000 received in one year, because today's EGP 1,000 can be invested to earn
interest. The **discount rate** represents this opportunity cost.

**Discount factor formula:**

$$\text{Discount Factor}_t = \frac{1}{(1 + r)^t}$$

For r = 10%, Year 3:

$$\text{DF}_3 = \frac{1}{(1.10)^3} = \frac{1}{1.331} = 0.7513$$

**Present Value of Year 3 cash flow (EGP 380,000):**

$$\text{PV}_3 = 380{,}000 \times 0.7513 = 285{,}500 \text{ EGP}$$

This means EGP 380,000 received in Year 3 is equivalent to only EGP 285,500 today.

**Complete NPV calculation:**

| Year    | Cash Flow  | Discount Factor (10%) | Present Value |
| ------- | ---------- | --------------------- | ------------- |
| 0       | −1,195,000 | 1.0000                | −1,195,000    |
| 1       | +180,000   | 0.9091                | +163,636      |
| 2       | +290,000   | 0.8264                | +239,669      |
| 3       | +380,000   | 0.7513                | +285,500      |
| 4       | +430,000   | 0.6830                | +293,691      |
| 5       | +480,000   | 0.6209                | +297,984      |
| **NPV** |            |                       | **+85,480**   |

$$\text{NPV} = -1{,}195{,}000 + 163{,}636 + 239{,}669 + 285{,}500 + 293{,}691 + 297{,}984 = +\mathbf{85{,}480 \text{ EGP}}$$

> **📚 Interpretation:** NPV = +EGP 85,480 means this investment creates EGP 85,480 of
> value above and beyond the 10% required return. The investment is accepted.
>
> **Decision rule:** NPV > 0 → Accept | NPV < 0 → Reject | NPV = 0 → Indifferent

### 5.2 Sensitivity Analysis — Understanding the Hurdle Rate

> **📚 Teaching Note — Why NPV Sensitivity Matters**
>
> The NPV changes sign between 12% (marginal) and 15% (negative). This means the
> project's financial viability is **highly sensitive to the discount rate assumption**.
>
> This is a teaching opportunity about risk:
>
> - If the organisation uses 10% as its hurdle rate → proceed (NPV > 0)
> - If the organisation uses 15% → reject on financial grounds alone
> - The non-financial benefits (brand, IP, capability) may justify proceeding anyway
>
> **This is exactly why financial analysis alone is insufficient.** The sensitivity
> table demonstrates that a 5% change in the discount rate (from 10% to 15%) swings
> the NPV by over EGP 170,000. Decision-makers must understand this.
>
> **Exercise:** Load this project into the Financial Analysis tab. Change the discount
> rate from 10% to 15% and observe the NPV change. What is the NPV at 12%?
> (Answer: approximately −EGP 6,500)

### 5.3 Internal Rate of Return — Concept Explained

> **📚 Teaching Note — What IRR Actually Means**
>
> The IRR is the discount rate that makes NPV = 0. In this project, IRR ≈ 12.4%.
>
> **Interpretation:** If EduTech Dynamics can invest money elsewhere and earn _more_
> than 12.4%, it should do that instead of this project. If it cannot earn more than
> 12.4% on alternative investments, this project is the better choice.
>
> **Why IRR is useful:** It is a single percentage that can be compared directly to
> a bank interest rate, bond yield, or hurdle rate — no assumptions about the discount
> rate are needed.
>
> **Why IRR has limitations:** For non-conventional cash flows (alternating positive
> and negative over multiple periods), IRR can give multiple solutions or be undefined.
> NPV is always more reliable for final decisions.
>
> **The application calculates IRR using bisection search.** You can verify the result
> by substituting 12.4% into the NPV formula — it should give approximately EGP 0.

### 5.4 Payback Period — The Simplest Metric

> **📚 Teaching Note — When to Use Payback Period**
>
> The **Payback Period** answers one question: "How long until I get my money back?"
>
> It is the simplest capital budgeting metric and the most widely understood by
> non-finance stakeholders. A sponsor who has never heard of NPV will immediately
> understand "You will recover your investment in 3.8 years."
>
> **Limitation:** Payback period ignores everything after the payback point. A project
> that returns EGP 1 million in Year 5 but nothing in Years 1–4 looks worse than one
> that returns nothing in Year 5 but recovers the investment in Year 2. This is why
> NPV is a more complete metric.
>
> **The application also computes Discounted Payback Period**, which accounts for the
> time value of money. The discounted payback will always be _longer_ than the simple
> payback period because discounted cash flows are smaller.

**Payback calculation walkthrough:**

$$\text{Remaining to recover after Year 3} = 1{,}195{,}000 - (180{,}000 + 290{,}000 + 380{,}000) = 345{,}000 \text{ EGP}$$

$$\text{Payback Period} = 3 + \frac{345{,}000}{430{,}000} = 3 + 0.802 = \mathbf{3.80 \text{ years}}$$

### 5.5 ROI Calculation Walkthrough

$$\text{Total Benefits (5 years)} = 180{,}000 + 290{,}000 + 380{,}000 + 430{,}000 + 480{,}000 = 1{,}760{,}000 \text{ EGP}$$

$$\text{Net Profit} = 1{,}760{,}000 - 1{,}195{,}000 = 565{,}000 \text{ EGP}$$

$$\text{ROI} = \frac{565{,}000}{1{,}195{,}000} \times 100\% = \mathbf{47.3\%}$$

> **📚 Note:** ROI does not account for the time value of money. It treats EGP 480,000
> received in Year 5 the same as EGP 180,000 received in Year 1. This is why ROI and
> NPV can tell different stories about the same investment.

### 5.6 Profitability Index

$$\text{PI} = \frac{\text{NPV} + \text{Initial Investment}}{\text{Initial Investment}} = \frac{85{,}480 + 1{,}195{,}000}{1{,}195{,}000} = \frac{1{,}280{,}480}{1{,}195{,}000} = \mathbf{1.07}$$

> **📚 When PI is Most Useful**
>
> The Profitability Index is most valuable when **comparing projects competing for the
> same limited budget**. A portfolio of 5 projects may all have positive NPVs, but if
> only 3 can be funded, PI ranks them by value created per EGP invested.
>
> PI > 1.0 → Create value (accept)
> PI = 1.0 → Break even
> PI < 1.0 → Destroy value (reject)
>
> In this case PI = 1.07 means that for every EGP 1.00 invested, EGP 1.07 is returned
> in present value terms (a 7-cent profit per pound invested). This is modest but positive.

---

## Section 6 — Non-Financial Benefits

> **📚 Teaching Note — When Financial Analysis Is Not Enough**
>
> At a 10% discount rate, NPV = +EGP 85,480 — positive but not dramatically so.
> At a 12% hurdle rate, NPV is essentially zero. At 15%, it is negative.
>
> This is a classic situation where **non-financial benefits tip the decision**.
>
> The PMBOK Guide explicitly recognises that Business Cases must include qualitative
> benefits. Some of the most important project benefits cannot be expressed in EGP:
>
> - Brand value and market positioning
> - Capability building within the organisation
> - Strategic optionality (future projects enabled by this one)
> - Social impact (student outcomes, educational quality)
>
> **PMP exam focus:** Questions about Benefits Management Plans often test whether
> students understand that some benefits are intangible and require non-financial
> measurement approaches (surveys, adoption metrics, academic citation counts, etc.).
> The Benefits Management Plan (next document) will define how each benefit will be
> tracked.

---

## Section 7 — Risks to the Business Case

> **📚 Teaching Note — Business Case Risks vs. Project Risks**
>
> Business Case risks are different from project execution risks:
>
> - **Business Case risk:** "What if adoption is lower than projected?" — this threatens
>   the _financial return_, not the project schedule
> - **Project execution risk:** "What if the lead developer leaves?" — this threatens
>   the _project delivery_, not the financial model
>
> Both types appear in the Risk Register (document 15). Business Case risks appear as
> risks at the _benefits realisation_ level — they matter even after the project closes.
>
> This distinction is tested on the PMP exam. The **Benefits Management Plan** (next
> document) addresses how post-project risks will be monitored.

---

## Section 8 — Recommendation

> **📚 Teaching Note — The Recommendation Must Be Definitive**
>
> A Business Case that says "it depends" or "you should consider..." is a poor Business
> Case. The PM's job is to conduct the analysis and make a clear recommendation.
>
> The sponsor's job is to accept, modify, or reject that recommendation — but the PM
> must be willing to commit to a position. Presenting a neutral summary and asking the
> sponsor to decide without a recommendation wastes the sponsor's time and signals low
> confidence.
>
> Notice how the recommendation here:
>
> 1. States the selected option explicitly
> 2. Summarises the key financial metrics
> 3. Acknowledges the marginal financial case
> 4. Provides the non-financial reason to proceed anyway
> 5. Closes with sponsor signature and date (formal authorisation)

---

## 📋 Review Questions (Self-Assessment)

1. The NPV at 10% is +EGP 85,480. At 15% it is −EGP 84,740. What is the approximate
   IRR, and how did you estimate it without a calculator?

2. Why must a Business Case always include a "Do Nothing" option? What purpose does
   it serve in the options analysis?

3. The Options Analysis shows that licensing Microsoft Project for 5 years costs
   _more_ than building the product internally. Why might an organisation choose to
   license anyway? What factors beyond cost might influence the decision?

4. The benefit projections assume 8 institutions and 700 students by Year 2. If actual
   adoption is only 4 institutions and 350 students, what happens to the NPV? Calculate
   the revised NPV and state whether the project would still be financially justified.
   _(Hint: reduce all revenue streams by ~50% while keeping time savings constant.)_

5. The document states IRR ≈ 12.4%. Using the discount factor table, verify this by
   calculating the NPV at 12% and at 13% and confirming that 12.4% falls between them.

6. The Profitability Index is 1.07 for this project. A competing project at EduTech
   Dynamics has PI = 1.21 but requires EGP 3,000,000 investment. The budget allows
   only one project. Using PI logic, which should be selected? Is PI always the right
   criterion for this decision?

---

> **📋 Application Exercise**
>
> Load the Business Case financial data into the **Financial Analysis tab** of PMHelper_Edu:
>
> - Initial Investment: EGP 1,195,000
> - Cash Flows (Years 1–5): [180,000 | 290,000 | 380,000 | 430,000 | 480,000]
> - Discount Rate: 10%
>
> Verify that the application computes:
>
> - Payback Period = 3.80 years
> - NPV = +85,480 EGP (approximately)
> - IRR ≈ 12.4%
> - ROI = 47.3%
> - PI = 1.07
>
> Then change the discount rate to 15% and observe the NPV sign change.

---

_Document ends. Proceed to:_ [03_benefits_management_plan.md](03_benefits_management_plan.md)
