# Feature Comparison: PMhelper vs. Target PM Charts, KPIs & Metrics Product

This document compares the features of the current **PMhelper** application against the target product scope described in the _"Project Management Charts, KPIs, and Metrics (Undergraduate & Postgraduate)"_ reference document.

The target product is a focused educational/professional tool covering:

- Charts & Visualizations (Gantt, EV S-Curve, Critical Path Network, Risk Matrix)
- KPIs & Metrics (EVM indicators, risk exposure)
- Core Calculations (CPM, float, EV, EAC, VAC, TCPI, risk exposure)

at both **undergraduate** and **postgraduate** levels.

---

## Legend

| Symbol | Meaning                                 |
| ------ | --------------------------------------- |
| ✅     | Fully implemented in PMhelper           |
| ⚠️     | Partially implemented / different scope |
| ❌     | Not implemented in PMhelper             |

---

## 1. Charts & Visualizations

### 1.1 Undergraduate Level

| Feature                            | Target Product                                                                                                                         | PMhelper Status | Notes                                                                                                                                                                                                                                                                                                  |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Gantt Chart**                    | Task timeline with start/end dates, durations, and dependencies on a bar chart                                                         | ✅              | Gantt chart implemented in `gantt_tab.py`. Shows tasks vs. time. Supports dependencies and critical path highlighting.                                                                                                                                                                                 |
| **Critical Path Network Diagram**  | Dependency network showing all tasks/links; forward & backward pass; critical path highlighted                                         | ✅              | Fully implemented in `network_tab.py` and `cpm_analyzer.py`. ES, EF, LS, LF computed; critical path highlighted in the diagram.                                                                                                                                                                        |
| **Earned Value S-Curve Chart**     | Cumulative line chart of PV, EV, and AC over time; S-shaped curves; tracks schedule and cost performance                               | ❌              | No Earned Value Management (EVM) tracking module exists. PMhelper does not model PV, EV, or AC over time at all. This is a major gap for the target product.                                                                                                                                           |
| **Risk Impact-Probability Matrix** | 2D heat-map grid categorizing risks by probability vs. impact; color-coded (red/yellow/green); optional Risk Exposure = p × I per risk | ⚠️              | A `risk_heatmap_tab` was referenced in tests but the quality_tools module is empty (not implemented). The existing `risk_tab.py` focuses on project **delay probability** (truncated normal distribution) — a different concept from a p×I risk register heat map. The p×I formula is not implemented. |

### 1.2 Postgraduate Level

| Feature                                 | Target Product                                                                                                                  | PMhelper Status | Notes                                                                                                                                                                                                                                                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Advanced Gantt / Timeline Views**     | Gantt with baseline bars, percent-complete shading, resource allocation overlay, actual vs. planned comparison (Tracking Gantt) | ⚠️              | Basic Gantt exists. No baseline comparison, no percent-complete shading on bars, no resource allocation overlay on the Gantt.                                                                                                                                                                                  |
| **Integrated Earned Value Dashboard**   | Multi-series chart showing PV/EV/AC plus ETC and BAC projections; forecast trend lines extending beyond current date            | ❌              | No EVM module. Not implemented.                                                                                                                                                                                                                                                                                |
| **Risk Probability Distribution Chart** | Histogram or S-curve of possible finish dates / costs from Monte Carlo simulation; derived from PERT three-point estimates      | ⚠️              | PERT probability analysis exists (`probability_tab.py`, `pert_analyzer.py`): computes probability of completing by a target date and plots probability/distribution charts. However, it is schedule-duration only — no cost distribution, and no full Monte Carlo engine (random sampling across many trials). |
| **Resource & Cost Histograms**          | Bar/line charts of resource use or cost per period (man-hours per week); useful for resource leveling analysis                  | ✅              | Resource leveling module (`resource_leveling.py`, `resource_visualizations.py`) generates resource profiles / histograms — before and after leveling. Burgess and Minimum Moment methods.                                                                                                                      |
| **Earned Schedule (ES) Chart**          | Chart comparing EV timeline to actual time; "Earned Schedule" vs. planned; highlights schedule performance in time units        | ❌              | Earned Schedule concept is not implemented. No EVM module exists.                                                                                                                                                                                                                                              |

---

## 2. KPIs & Metrics

### 2.1 Undergraduate Level

| KPI / Metric                             | Formula                                            | Target Product                                         | PMhelper Status | Notes                                                                                                                                               |
| ---------------------------------------- | -------------------------------------------------- | ------------------------------------------------------ | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cost Variance (CV)**                   | $CV = EV - AC$                                     | Positive = under budget (green); negative = over (red) | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Schedule Variance (SV)**               | $SV = EV - PV$                                     | Positive = ahead of schedule; negative = behind        | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Cost Performance Index (CPI)**         | $CPI = EV / AC$                                    | >1 = cost efficient; <1 = overrun                      | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Schedule Performance Index (SPI)**     | $SPI = EV / PV$                                    | >1 = ahead; <1 = behind                                | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Percent Complete (PC)**                | $PC = EV / BAC \times 100\%$                       | Progress % by budget; lagging status measure           | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Percent Budget Spent (PS)**            | $PS = AC / BAC \times 100\%$                       | Compare with PC; PS > PC = overspending                | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Critical Ratio (CR)**                  | $CR = CPI \times SPI$                              | Combined index; ~1 = healthy; <1 = at risk             | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Estimate at Completion (EAC)**         | $EAC = AC + (BAC - EV)$ or $EAC = BAC / CPI$       | Forecast total cost; EAC > BAC = projected overrun     | ❌              | Not implemented. No EVM module (note: PMhelper has a cost _optimization_ module for crashing, which is unrelated).                                  |
| **Variance at Completion (VAC)**         | $VAC = BAC - EAC$                                  | Positive = underrun; negative = overrun                | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **To-Complete Performance Index (TCPI)** | $TCPI = (BAC - EV) / (BAC - AC)$                   | >1 = must improve efficiency; leading metric           | ❌              | Not implemented. No EVM module.                                                                                                                     |
| **Project Risk Exposure (RE)**           | $RE = p \times I$ (per risk; sum = total exposure) | Leading indicator; identifies highest-risk items       | ❌              | Not implemented in this form. PMhelper's risk analysis uses a probabilistic delay model (truncated normal distribution), not a simple p×I register. |

### 2.2 Postgraduate Level

| KPI / Metric                                              | Target Product                                                                        | PMhelper Status | Notes                                                                                                                                                                                         |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cumulative SPI/CPI Trend**                              | Track CPI and SPI week by week; chart trends; sustained decline below 1.0 = warning   | ❌              | Not implemented. Requires EVM module.                                                                                                                                                         |
| **Cost & Schedule Risk Indices (Risk-Adjusted EAC)**      | $EAC_{risk} = EAC + k \times RE_{total}$; incorporate contingency from aggregate risk | ❌              | Not implemented in this form. PMhelper has a contingency planning module based on schedule delay probability, but not a risk-adjusted EAC combining EVM + risk exposure.                      |
| **Quality & Scope Metrics**                               | Defect Density, Change Request Rate; leading/lagging scope stability indicators       | ❌              | Not implemented. Outside current PMhelper scope.                                                                                                                                              |
| **Risk Exposure (Aggregate / Probabilistic)**             | Sum all $p_i I_i$; use probabilistic models / EMV; set risk tolerance thresholds      | ❌              | Not implemented. PMhelper risk analysis focuses on schedule delay, not an aggregate p×I risk register.                                                                                        |
| **Schedule Probability of Success**                       | PERT-based probability of finishing on time; P(finish ≤ target date) using z-scores   | ✅              | Implemented in `pert_analyzer.py` (`calculate_completion_probability`) and `probability_tab.py`. Computes P(T ≤ target) with z-scores from PERT mean and variance.                            |
| **Earned Schedule (ES) & Schedule Variance in Time**      | ES = time at which PV = EV; SV(t) = ES − actual time; measured in days not $          | ❌              | Not implemented.                                                                                                                                                                              |
| **TCPI (Advanced — BAC & EAC variants)**                  | Two formulas: toward BAC and toward EAC; advanced threshold interpretation            | ❌              | Not implemented.                                                                                                                                                                              |
| **Monte Carlo-Based KPIs**                                | 50% & 90% confidence EAC and finish time; P(cost ≤ budget)                            | ⚠️              | PERT-based probability of schedule completion is available. Cost Monte Carlo (P(cost ≤ budget)) and confidence intervals for EAC are not implemented.                                         |
| **Stakeholder Satisfaction / Benefit Metrics (NPV, ROI)** | NPV or ROI of project; Earned Business Value; financial link to business case         | ⚠️              | NPV optimization (`npv_optimization.py`) exists in the context of project selection and multi-objective optimization. ROI is not explicitly computed as a standalone project performance KPI. |

---

## 3. Core Calculations

### 3.1 Undergraduate Level

| Calculation                                                | Target Product                                                                                                   | PMhelper Status | Notes                                                                                                                   |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Critical Path (CP) Calculation**                         | Forward pass (ES/EF) + backward pass (LS/LF); identify tasks with zero float; handle multiple equal-length paths | ✅              | Fully implemented in `cpm_analyzer.py` and `network_builder.py`. Handles multiple critical paths, computes ES/EF/LS/LF. |
| **Float / Slack Calculation**                              | Total Float = LF − EF (or LS − ES); identifies flexible vs. critical tasks                                       | ✅              | Fully implemented. Total float calculated for all activities; zero-float activities identified as critical.             |
| **Earned Value (EV) Computation**                          | $EV = \sum Budget_i \times \%complete_i$; task-level EV summed across WBS                                        | ❌              | Not implemented. No EVM or WBS percent-complete tracking module.                                                        |
| **Schedule & Cost Variances & Indices (SV, CV, SPI, CPI)** | Compute PV from schedule; EV from above; AC from accounting; derive SV = EV−PV, CV = EV−AC, SPI, CPI             | ❌              | Not implemented. No EVM module.                                                                                         |
| **EAC Calculation**                                        | $EAC = AC + (BAC - EV)$ or $EAC = BAC / CPI$; choose formula based on context                                    | ❌              | Not implemented. Note: PMhelper's crashing module produces cost trade-off curves (different concept).                   |
| **VAC Calculation**                                        | $VAC = BAC - EAC$; interpret positive as underrun                                                                | ❌              | Not implemented. No EVM module.                                                                                         |
| **TCPI Calculation**                                       | $(BAC - EV) / (BAC - AC)$; flag TCPI > 1 as red; edge: denominator ≤ 0                                           | ❌              | Not implemented. No EVM module.                                                                                         |
| **Risk Exposure (Expected Loss)**                          | $RE = p \times I$ per risk; sum across all risks                                                                 | ❌              | Not implemented in this form.                                                                                           |

### 3.2 Postgraduate Level

| Calculation                                          | Target Product                                                                                                            | PMhelper Status | Notes                                                                                                                                                                                                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Extended Critical Path (with risk / Monte Carlo)** | Treat task durations as random variables; run simulations; derive confidence interval for project end date                | ⚠️              | PERT probability analysis covers critical path duration uncertainty via normal approximation (mean ± σ of critical path). Full Monte Carlo (random sampling over many trials) is described in README but not evidenced in implementation files.   |
| **PERT Expected Time & Variance**                    | $T_E = (O + 4M + P) / 6$; $\sigma = (P - O) / 6$; sum for critical path                                                   | ✅              | Fully implemented in `pert_analyzer.py`. TE, σ², project mean, project σ all computed.                                                                                                                                                            |
| **EAC (Advanced, multiple formulas)**                | $EAC = AC + (BAC - EV) / (CPI \times SPI)$; scenario weighting; choice of formula by context                              | ❌              | Not implemented. No EVM module.                                                                                                                                                                                                                   |
| **Cost of Risk (Contingency Reserve)**               | Total Contingency = $\sum p_i I_i$ + management reserve; compare worst-case vs. expected-case                             | ⚠️              | `ContingencyPlanner` in `risk_analysis.py` computes contingency based on schedule delay probability at a confidence level (truncated normal). This is schedule-delay contingency only — not a general p×I risk register sum.                      |
| **TCPI Scenarios (BAC vs. EAC goals)**               | Derive TCPI for "on budget" vs. "on current forecast"; interpret threshold changes                                        | ❌              | Not implemented.                                                                                                                                                                                                                                  |
| **Schedule Compression (Crashing / Fast-Tracking)**  | Extra cost per day saved; crash cost per unit time; decision on when to crash                                             | ✅              | Fully implemented via the crashing module (`crashing_tab.py`, `cost_optimization.py`). Crash cost per day, sequential crashing, cost-time trade-off curve.                                                                                        |
| **Monte Carlo Simulation Steps**                     | Identify variables, assign distributions, random-sample N trials, record outcomes, derive mean/percentile; plot histogram | ⚠️              | PERT-based probability analysis (`pert_analyzer.py`) approximates Monte Carlo via normal distribution. A true iterative Monte Carlo engine (random sampling loop with N trials) is described in the README but no implementation found in `src/`. |
| **Scaling & Complex Dependencies**                   | Normalized KPIs for large projects; SPI/CPI control charts; Earned Value at program level                                 | ❌              | Not implemented. Sensitivity analysis exists for duration/cost variations but not EVM-based control charts.                                                                                                                                       |

---

## 4. Summary: Feature Gap Analysis

### 4.1 Features in PMhelper NOT in Target Product

The following PMhelper features are **out of scope** for the target product:

| PMhelper Feature                                                                 | Notes                                                                     |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Project Screening & Selection** (AHP, Linear Scoring, B/C, Portfolio ILP)      | Advanced decision-making tool; not covered in the target scope            |
| **Decision Analysis** (Maximin, Bayes, Decision Trees, EVPI, EVE)                | Out of scope for the target product                                       |
| **Multi-objective Optimization** (Pareto frontier, NPV/resource/cost trade-offs) | Out of scope                                                              |
| **Resource-Constrained Project Scheduling (RCPS)** heuristics                    | Out of scope                                                              |
| **Resource Leveling** (Burgess, Minimum Moment)                                  | Out of scope (though resource histograms are mentioned at postgrad level) |
| **Project Charter Management**                                                   | Out of scope                                                              |
| **DPCI (Detailed Project Control Interface)** tab                                | Out of scope                                                              |

### 4.2 Features in Target Product NOT in PMhelper

These are the **implementation gaps** that would need to be built for the target product:

| Missing Feature                                                           | Priority Level | Complexity Estimate                                      |
| ------------------------------------------------------------------------- | -------------- | -------------------------------------------------------- |
| **EV Tracking Module** (PV, EV, AC per period, WBS % complete input)      | 🔴 Critical    | High — new data model required                           |
| **Earned Value S-Curve Chart** (PV / EV / AC cumulative lines over time)  | 🔴 Critical    | Medium — charting once data model exists                 |
| **All EVM KPIs** (CV, SV, CPI, SPI, PC, PS, CR, EAC, VAC, TCPI)           | 🔴 Critical    | Medium — straightforward formulas once data model exists |
| **Risk Impact-Probability Matrix (Heat Map)** (p×I grid, color coding)    | 🔴 Critical    | Medium — new risk register data model + heat-map chart   |
| **Risk Exposure (RE = p × I)** per risk and total                         | 🔴 Critical    | Low — simple formula, needs new risk register UI         |
| **Integrated EV Dashboard** (ETC/BAC projections, forecast trend lines)   | 🟡 High        | High — requires EVM module + forecasting                 |
| **Earned Schedule (ES) Metric & Chart**                                   | 🟡 High        | Medium — requires EVM module                             |
| **Cumulative SPI/CPI Trend Chart**                                        | 🟡 High        | Low — requires EVM time-series data                      |
| **Risk-Adjusted EAC** ($EAC_{risk} = EAC + k \times RE$)                  | 🟡 High        | Medium — requires EVM + risk register                    |
| **Advanced Gantt** (baseline bars, % complete shading, tracking Gantt)    | 🟡 High        | Medium — extensions to existing Gantt                    |
| **Monte Carlo-Based KPIs** (confidence EAC, P(cost ≤ budget))             | 🟠 Medium      | High — needs cost distribution modeling                  |
| **Quality & Scope Metrics** (Change Request Rate, Defect Density)         | 🟠 Medium      | Medium — new data model                                  |
| **TCPI Scenarios** (toward BAC vs. toward EAC)                            | 🟠 Medium      | Low — formula extension of TCPI                          |
| **Full Monte Carlo Engine** (N-trial random sampling for duration & cost) | 🟠 Medium      | High — new simulation engine                             |
| **NPV / ROI as standalone project KPI**                                   | 🟢 Low         | Low — formula exists; needs new UI context               |

### 4.3 Overlap: Features Shared (Fully or Partially)

| Feature                                    | Alignment                                                           |
| ------------------------------------------ | ------------------------------------------------------------------- |
| Gantt Chart (basic)                        | ✅ Fully aligned                                                    |
| Critical Path Network Diagram              | ✅ Fully aligned                                                    |
| Forward/Backward Pass (ES/EF/LS/LF)        | ✅ Fully aligned                                                    |
| Float/Slack Calculation                    | ✅ Fully aligned                                                    |
| PERT Expected Time & Variance              | ✅ Fully aligned                                                    |
| Schedule Probability of Success (z-score)  | ✅ Fully aligned                                                    |
| Schedule Compression / Crashing            | ✅ Fully aligned                                                    |
| Resource Histograms (from leveling module) | ⚠️ Partially aligned — available but different context              |
| PERT-based probability distribution chart  | ⚠️ Partially aligned — schedule only, no cost distribution          |
| Contingency planning                       | ⚠️ Partially aligned — different model (delay-based, not p×I-based) |

---

## 5. Recommended Architecture for the New Version

The target product is essentially a new **Earned Value Management (EVM) + Risk Register** application. The recommended modules to build are:

1. **EVM Data Model** — Time-phased project baseline: WBS tasks with budgets + period-by-period PV/EV/AC inputs
2. **EVM Calculation Engine** — CV, SV, CPI, SPI, PC, PS, CR, EAC (multiple formulas), VAC, TCPI, ES
3. **EV S-Curve Chart** — Multi-line cumulative chart (PV, EV, AC ± ETC/BAC forecast)
4. **EVM Dashboard** — KPI cards with RAG (Red/Amber/Green) color coding and trend arrows
5. **Risk Register Module** — List of risks with probability (0–1) and impact ($); compute RE = p × I; total exposure
6. **Risk Heat Map** — 5×5 (or configurable) grid, color-coded by severity; plotted from risk register
7. **Advanced Gantt** — Extend existing: add baseline bar, % complete shading, actual vs. planned overlay
8. **Monte Carlo Engine** — Full N-trial simulation for both duration and cost uncertainty

Existing PMhelper modules to **reuse**:

- CPM engine (`cpm_analyzer.py`, `network_builder.py`) — critical path, float, network diagram
- PERT engine (`pert_analyzer.py`) — three-point estimates, TE/σ, schedule probability
- Crashing module — schedule compression calculations
- Gantt tab — extend for baseline and % complete tracking

---

_Generated: March 5, 2026_
