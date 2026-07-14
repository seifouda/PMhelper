# Business Case

## PMHelper_Edu Development Project

| Field              | Value                                     |
| ------------------ | ----------------------------------------- |
| **Document ID**    | PMHE-2025-BC-001                          |
| **Project Code**   | PMHE-2025                                 |
| **Version**        | 1.0 — Approved                            |
| **Prepared by**    | Ahmed Samir Khalil, PMP — Project Manager |
| **Reviewed by**    | Omar Hassan El-Rashidy — Lead Developer   |
| **Approved by**    | Dr. Karim Naguib — Project Sponsor        |
| **Organization**   | EduTech Dynamics                          |
| **Date**           | 2025-09-01                                |
| **Classification** | Internal — Confidential                   |

---

## 1. Executive Summary

EduTech Dynamics proposes to develop **PMHelper_Edu**, a purpose-built educational
project management software application targeting university students, postgraduate
candidates, CAPM/PMP exam candidates, and engineering management students.

The problem being solved is well-defined: existing commercial PM tools are too complex
and expensive for educational use, while freely available tools are fragmented and
provide no pedagogical scaffolding. No single tool teaches the complete quantitative
PM curriculum interactively.

The recommended option is to build the product internally with AI-assisted development.
This approach delivers the highest net present value and the strongest strategic position
for EduTech Dynamics.

**Financial Summary (10% discount rate, 5-year horizon):**

| Metric              | Value         |
| ------------------- | ------------- |
| Total Investment    | EGP 1,195,000 |
| 5-Year NPV          | EGP 85,480    |
| IRR                 | ~12.5%        |
| Payback Period      | 3.8 years     |
| ROI (5-year)        | 47.3%         |
| Profitability Index | 1.07          |

The business case is financially marginal at a 15% hurdle rate (NPV = −EGP 84,740) but
positive at 10%. The non-financial strategic benefits — brand establishment, academic
adoption, future revenue potential — are expected to tip the decision to proceed.

**Recommendation:** Proceed with Option 3 (Build Internally with AI Assistance).

---

## 2. Problem Statement

### 2.1 The Education Gap

Project management is a required course in most engineering, business, and construction
management programmes in Egypt and the broader MENA region. The typical curriculum covers:

- Work Breakdown Structures and project scope
- Critical Path Method (CPM) and network scheduling
- PERT and probabilistic scheduling
- Earned Value Management (EVM) and cost control
- Risk analysis and Monte Carlo simulation
- Resource leveling and optimisation

Students are taught these methods through:

- Textbooks with static examples
- Spreadsheet exercises prepared by faculty
- Manual calculation practice in examinations

**The gap:** None of these approaches provide:

- Interactive calculation with immediate feedback
- Step-by-step worked solutions linking formula to result
- Visualisations that update dynamically as inputs change
- A single integrated environment where students see how CPM feeds EVM, which feeds
  risk analysis, which feeds Monte Carlo, all within one project context

### 2.2 Evidence of the Gap

- University teaching assistants routinely spend 4–8 hours per course creating manual
  exercise solutions that could be automated
- Students report confusion about which formula applies to which scenario when formulas
  are learned in isolation
- Commercial software (Microsoft Project, Oracle Primavera P6) costs USD 600–3,000
  per seat per year — prohibitive for academic lab deployment
- No open-source alternative covers the full curriculum taught at Egyptian universities

### 2.3 Cost of Inaction

Each semester without an integrated PM teaching tool:

- Faculty spend an estimated 40–60 hours recreating exercise materials
- Students receive lower-quality feedback on problem-solving approaches
- EduTech Dynamics misses an early-mover advantage in educational PM software

---

## 3. Strategic Context

### 3.1 Organisational Strategy Alignment

EduTech Dynamics' 3-year strategy (2025–2028) is centred on becoming the leading
education technology provider for engineering and project management curricula in Egypt
and the MENA region. PMHelper_Edu directly advances this strategy by:

- Creating a tangible, deployable product in the target market
- Building credibility with academic institutions through a free, open-source offering
- Establishing a foundation for premium institutional licensing

### 3.2 Market Context

- Egypt has 27 accredited engineering universities with PM-related courses
- The MENA region has over 150 universities with engineering programmes
- CAPM and PMP examination registrations in Egypt have grown ~18% year-over-year
  since 2022
- No Egyptian EdTech company currently occupies the PM education software space

---

## 4. Options Analysis

### Option 0 — Do Nothing (Baseline)

Continue without a dedicated PM educational tool. Faculty continue using manual
spreadsheet exercises. Students continue without interactive software support.

**Costs:** No direct development cost.
**Benefits:** None.
**NPV:** EGP 0 (baseline reference).
**Risks:** Continued competitive disadvantage; missed market opportunity.
**Recommendation:** Rejected. Delivers no value.

---

### Option 1 — License an Existing Commercial PM Tool for Education

License Microsoft Project for Education or a comparable tool for university lab use.

**Costs (estimated over 5 years):**

- Microsoft Project Academic licensing: ~USD 150/seat/year
- 30 seats for a typical computer lab × 5 years = USD 22,500 (~EGP 1,125,000 at EGP 50/USD)
- Setup, training, and IT administration: ~EGP 80,000
- Annual support and renewals: ~EGP 40,000/year
- **Total 5-year cost: ~EGP 1,405,000**

**Benefits:**

- Well-known, industry-standard tool
- No development effort

**Limitations:**

- Does not cover PERT, EVM, risk analysis, or Monte Carlo in an educational context
- No worked solutions or step-by-step explanations
- Requires ongoing annual licensing payments
- Does not generate institutional IP or revenue for EduTech Dynamics
- Completely dependent on Microsoft pricing and product decisions

**NPV:** Negative (pure ongoing cost, no revenue stream).
**Recommendation:** Rejected. Higher long-term cost, lower educational value, no IP.

---

### Option 2 — Commission External Development

Hire an external software development agency to build PMHelper_Edu to specification.

**Costs (estimated):**

- External agency quote: EGP 800,000–1,200,000 for initial build
- Ongoing maintenance contract: EGP 120,000/year
- Project management overhead: EGP 60,000
- **Total 3-year cost: ~EGP 1,220,000–1,620,000**

**Benefits:**

- Lower internal resource commitment

**Limitations:**

- No ownership of technical knowledge; dependency on external vendor
- Higher cost without AI-assisted development efficiency
- Quality risk: external teams have no stake in educational correctness
- Maintenance dependency prevents future evolution without additional cost
- No internal capability building for EduTech Dynamics

**NPV:** Negative to marginally positive depending on revenue; higher risk.
**Recommendation:** Rejected. Higher cost, dependency risk, no internal capability.

---

### Option 3 — Build Internally with AI-Assisted Development (Recommended)

Develop PMHelper_Edu with an internal team of 1 full-time lead developer and part-time
support roles, leveraging GitHub Copilot AI assistance throughout.

**Key advantages over Options 1 and 2:**

- Internal ownership of all code, data, and intellectual property
- AI assistance (GitHub Copilot) reduces development time by an estimated 30–40%
  compared to un-assisted development, making a single-developer project viable
- Full flexibility to evolve the product based on curriculum feedback
- Revenue potential from institutional licensing once established
- Positions EduTech Dynamics with a unique, proprietary product asset

**Total investment:** EGP 1,195,000 (including all reserves)
**Development timeline:** 13 months (2025-09-01 to 2026-09-30)

**Recommendation:** Proceed. Highest long-term value, lowest total cost, builds
organisational capability.

---

## 5. Financial Analysis (Option 3)

### 5.1 Investment Summary

| Category                                                 | Amount (EGP)  |
| -------------------------------------------------------- | ------------- |
| Personnel costs (all roles, 13 months)                   | 885,500       |
| Software subscriptions (Copilot, hosting, domain, tools) | 41,600        |
| Hardware (development + testing equipment)               | 73,000        |
| Training and materials                                   | 22,000        |
| **Subtotal (direct costs)**                              | **1,022,100** |
| **Contingency Reserve (12%)**                            | **122,652**   |
| **Budget at Completion (BAC)**                           | **1,144,752** |
| **Management Reserve (5% of BAC, held separately)**      | **50,248**    |
| **Total Authorised Budget**                              | **1,195,000** |

_Note: BAC rounded to EGP 1,150,000 for EVM calculation purposes._

### 5.2 Benefit Stream Projections

Benefit projections are based on conservative institutional adoption scenarios.

**Revenue Sources:**

- Institutional licensing: EGP 200 per student per year (optional; product is free for
  direct download but institutions seeking support, customisation, or branded deployments
  pay licensing fee)
- Consulting and customisation: EGP 50,000–80,000/year from Year 2 onward (estimated)
- Faculty time savings (quantified as avoided cost): ~EGP 100,000/year (40 institutions ×
  5 courses × 10 hrs × EGP 500/hr equivalent)

**Year-by-Year Benefit Projection:**

| Year        | Institutions | Students | Licensing Rev. | Consulting Rev. | Time Savings | Total Benefits |
| ----------- | ------------ | -------- | -------------- | --------------- | ------------ | -------------- |
| 1 (2026-27) | 3            | 300      | 60,000         | 20,000          | 100,000      | 180,000        |
| 2 (2027-28) | 8            | 700      | 140,000        | 50,000          | 100,000      | 290,000        |
| 3 (2028-29) | 14           | 1,200    | 240,000        | 80,000          | 100,000      | 420,000 ¹      |
| 4 (2029-30) | 18           | 1,500    | 300,000        | 80,000          | 100,000      | 480,000        |
| 5 (2030-31) | 22           | 1,800    | 360,000        | 80,000          | 100,000      | 540,000        |

¹ _Note: Year 3 benefits used at EGP 380,000 in NPV calculation (conservative scenario)._

### 5.3 Net Present Value Analysis

**Discount rate: 10%** (baseline scenario — moderate-risk EdTech startup in Egypt)

| Year           | Cash Flow (EGP) | Discount Factor (10%) | Present Value (EGP) |
| -------------- | --------------- | --------------------- | ------------------- |
| 0 (Investment) | −1,195,000      | 1.0000                | −1,195,000          |
| 1              | +180,000        | 0.9091                | +163,636            |
| 2              | +290,000        | 0.8264                | +239,669            |
| 3              | +380,000        | 0.7513                | +285,500            |
| 4              | +430,000        | 0.6830                | +293,691            |
| 5              | +480,000        | 0.6209                | +297,984            |
| **NPV @ 10%**  |                 |                       | **+85,480**         |

**Sensitivity Analysis (NPV at varying discount rates):**

| Discount Rate | NPV (EGP) | Decision      |
| ------------- | --------- | ------------- |
| 8%            | +189,000  | Strong Accept |
| 10%           | +85,480   | Accept        |
| 12%           | −6,500    | Marginal      |
| 15%           | −84,740   | Reject        |

### 5.4 Internal Rate of Return

The IRR is approximately **12.4%** — the discount rate at which NPV = 0.

Decision rule: If EduTech Dynamics' required rate of return (hurdle rate) is below
12.4%, this investment creates value. If the hurdle rate is above 12.4%, the project
destroys value on a purely financial basis.

### 5.5 Payback Period

Cumulative cash flows:

| Year | Annual CF  | Cumulative CF |
| ---- | ---------- | ------------- |
| 0    | −1,195,000 | −1,195,000    |
| 1    | +180,000   | −1,015,000    |
| 2    | +290,000   | −725,000      |
| 3    | +380,000   | −345,000      |
| 4    | +430,000   | +85,000       |

Payback occurs during Year 4:

$$\text{Payback Period} = 3 + \frac{345{,}000}{430{,}000} = 3.80 \text{ years}$$

### 5.6 Return on Investment

$$\text{ROI} = \frac{\text{Total Benefits} - \text{Total Investment}}{\text{Total Investment}} \times 100\%$$

$$\text{ROI} = \frac{(180{,}000 + 290{,}000 + 380{,}000 + 430{,}000 + 480{,}000) - 1{,}195{,}000}{1{,}195{,}000} \times 100\%$$

$$\text{ROI} = \frac{1{,}760{,}000 - 1{,}195{,}000}{1{,}195{,}000} \times 100\% = \mathbf{47.3\%}$$

### 5.7 Profitability Index

$$\text{PI} = \frac{\text{PV of Future Cash Inflows}}{\text{Initial Investment}} = \frac{1{,}195{,}000 + 85{,}480}{1{,}195{,}000} = 1.07$$

PI > 1.0 confirms the investment creates value at a 10% discount rate.

---

## 6. Non-Financial Benefits

The following benefits are expected but are not fully quantifiable in financial terms:

| Benefit                                      | Expected Impact                                                                          |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Brand establishment in academic PM education | Positions EduTech Dynamics for longer-term market leadership                             |
| Academic publication potential               | One or more conference/journal papers from the educational methodology                   |
| Student career outcomes                      | Graduates who used PMHelper_Edu carry the brand into industry                            |
| Open-source community engagement             | GitHub contributors may extend functionality at no additional cost                       |
| Foundation for future products               | Codebase, data models, and methodology can be reused for premium courses and LMS modules |
| Technical capability building                | Internal team gains expertise in full-stack Python + Angular + cloud development         |

---

## 7. Risks to the Business Case

| #    | Risk                                                                | Probability | Impact   | Mitigation                                                                                                               |
| ---- | ------------------------------------------------------------------- | ----------- | -------- | ------------------------------------------------------------------------------------------------------------------------ |
| BR-1 | Adoption lower than projected (fewer institutions than forecast)    | Medium      | High     | Start with free access to build user base; track adoption metrics from Month 6                                           |
| BR-2 | Competing product enters the market during development              | Low         | High     | Open-source MIT licence provides first-mover protection — copying is permitted; being first with adoption is the barrier |
| BR-3 | Exchange rate changes affect USD-denominated costs (GitHub, Render) | Medium      | Medium   | EGP-denominated costs dominate; USD-portion is <5% of BAC                                                                |
| BR-4 | Lead developer attrition                                            | Low         | Critical | Documented architecture, AI-assisted codebase, complete test suite reduce key-person risk                                |
| BR-5 | Actual benefits materialize later than projected                    | Medium      | Medium   | Break-even at Year 4 provides buffer; Year 3+ adoption drives financial viability                                        |

---

## 8. Recommendation

**Proceed with Option 3: Build Internally with AI-Assisted Development.**

The business case is financially positive at a 10% discount rate (NPV = +EGP 85,480,
IRR = 12.4%, Payback = 3.8 years). Non-financial benefits — particularly brand
establishment and academic adoption — provide additional justification that tilts the
decision to proceed even if the hurdle rate approaches 12%.

The project has a clearly defined scope, a fixed deadline aligned with the academic year,
a competent team, and a validated problem statement. The primary risk is the dependency
on the lead developer, which is partially mitigated by AI-assisted development and
comprehensive documentation practices.

**Approved for execution by:** Dr. Karim Naguib, Project Sponsor
**Date:** 2025-09-01

---

## 9. Document Control

| Version      | Date       | Author             | Change                        |
| ------------ | ---------- | ------------------ | ----------------------------- |
| 0.1 Draft    | 2025-08-18 | Ahmed Samir Khalil | Initial draft                 |
| 0.2 Review   | 2025-08-25 | Dr. Karim Naguib   | Financial assumptions revised |
| 1.0 Approved | 2025-09-01 | Dr. Karim Naguib   | Approved at project kickoff   |
