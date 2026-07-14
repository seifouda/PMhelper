# PMhelper Edu — Full Feature List

A focused educational tool covering Project Management Charts, KPIs, and Metrics at both undergraduate and postgraduate levels.

---

## 1. Charts & Visualizations

### Undergraduate

- **Gantt Chart** — ✅ Ready | 🎯 V1
  - Task list with start date, duration, and end date
  - Dependency links between tasks
  - Horizontal bar chart (tasks on vertical axis, time on horizontal axis)
  - Critical path highlighting

- **Critical Path Network Diagram** — ✅ Ready | 🎯 V1
  - Node-and-arrow network of all tasks and dependencies
  - Forward pass: Earliest Start (ES) and Earliest Finish (EF) per task
  - Backward pass: Latest Start (LS) and Latest Finish (LF) per task
  - Critical path highlighted (zero float tasks)

- **Earned Value S-Curve Chart** — ❌ Not built | 🎯 V1
  - Cumulative line chart with three series: Planned Value (PV), Earned Value (EV), Actual Cost (AC)
  - S-shaped curves over project timeline (weeks/periods)
  - Visual identification of cost and schedule performance trends

- **Risk Impact-Probability Matrix** — ❌ Not built | 🎯 V1
  - 5×5 (configurable) heat-map grid
  - Axes: Probability (0–1) vs. Impact ($)
  - Color coding: red (high), yellow (medium), green (low)
  - Each risk plotted as a point on the grid
  - Risk Exposure (RE = p × I) displayed per cell

### Postgraduate

- **Advanced Gantt / Tracking Gantt** — ⚠️ Semi-ready | 🎯 V1
  - Baseline bars (planned) vs. actual progress bars
  - Percent-complete shading on task bars
  - Actual vs. planned overlay comparison

- **Integrated Earned Value Dashboard Chart** — ❌ Not built
  - Extended S-curve including ETC (Estimate to Complete) and BAC (Budget at Completion) lines
  - Forecast trend lines extending beyond current date
  - Schedule and cost performance trend visualization

- **Risk Probability Distribution Chart** — ⚠️ Semi-ready | 🎯 V1
  - Histogram of possible project finish dates and/or costs
  - Derived from Monte Carlo simulation or PERT three-point estimates
  - Overlay of percentile markers (P50, P80, P90)

- **Resource & Cost Histograms** — ⚠️ Semi-ready | 🎯 V1
  - Bar or line chart of resource usage (man-hours) or cost per period
  - Before and after resource leveling comparison

- **Earned Schedule (ES) Chart**
  - Chart comparing Earned Schedule (in time units) vs. actual elapsed time
  - Highlights schedule performance in days, not dollars

- **Cumulative SPI/CPI Trend Chart**
  - Week-by-week line chart of CPI and SPI values over project life
  - Warning threshold line at 1.0
  - Trend direction indicators

---

## 2. KPIs & Metrics

### Undergraduate

| KPI                                  | Formula                                          | Indicator Type | Status       | Version |
| ------------------------------------ | ------------------------------------------------ | -------------- | ------------ | ------- |
| Cost Variance (CV)                   | $CV = EV - AC$                                   | Lagging        | ❌ Not built | 🎯 V1   |
| Schedule Variance (SV)               | $SV = EV - PV$                                   | Lagging        | ❌ Not built | 🎯 V1   |
| Cost Performance Index (CPI)         | $CPI = EV / AC$                                  | Lagging        | ❌ Not built | 🎯 V1   |
| Schedule Performance Index (SPI)     | $SPI = EV / PV$                                  | Lagging        | ❌ Not built | 🎯 V1   |
| Percent Complete (PC)                | $PC = EV / BAC \times 100\%$                     | Lagging        | ❌ Not built | 🎯 V1   |
| Percent Budget Spent (PS)            | $PS = AC / BAC \times 100\%$                     | Lagging        | ❌ Not built | 🎯 V1   |
| Critical Ratio (CR)                  | $CR = CPI \times SPI$                            | Lagging        | ❌ Not built | 🎯 V1   |
| Estimate at Completion (EAC)         | $EAC = AC + (BAC - EV)$ or $EAC = BAC / CPI$     | Leading        | ❌ Not built | 🎯 V1   |
| Variance at Completion (VAC)         | $VAC = BAC - EAC$                                | Leading        | ❌ Not built | 🎯 V1   |
| To-Complete Performance Index (TCPI) | $TCPI = (BAC - EV) / (BAC - AC)$                 | Leading        | ❌ Not built | 🎯 V1   |
| Project Risk Exposure (RE)           | $RE = p \times I$ per risk; sum = total exposure | Leading        | ❌ Not built | 🎯 V1   |

- RAG (Red / Amber / Green) color coding for each KPI based on configurable thresholds
- KPI cards panel with current value, status, and trend arrow

### Postgraduate

| KPI                               | Formula                                           | Indicator Type | Status        | Version |
| --------------------------------- | ------------------------------------------------- | -------------- | ------------- | ------- |
| Earned Schedule (ES)              | Time at which PV = EV                             | Leading        | ❌ Not built  | —       |
| Schedule Variance in Time SV(t)   | $SV(t) = ES - \text{actual time}$                 | Leading        | ❌ Not built  | —       |
| Risk-Adjusted EAC                 | $EAC_{risk} = EAC + k \times RE_{total}$          | Leading        | ❌ Not built  | —       |
| TCPI toward BAC                   | $TCPI = (BAC - EV) / (BAC - AC)$                  | Leading        | ❌ Not built  | 🎯 V1   |
| TCPI toward EAC                   | $TCPI = (BAC - EV) / (EAC - AC)$                  | Leading        | ❌ Not built  | —       |
| Schedule Probability of Success   | $P(T \leq T_{target})$ via z-score from PERT      | Leading        | ✅ Ready      | 🎯 V1   |
| Aggregate Risk Exposure           | $\sum p_i I_i$ across all risks                   | Leading        | ❌ Not built  | 🎯 V1   |
| Monte Carlo P50 / P90 EAC         | 50th and 90th percentile cost from simulation     | Leading        | ❌ Not built  | —       |
| Monte Carlo P50 / P90 Finish Date | 50th and 90th percentile end date from simulation | Leading        | ⚠️ Semi-ready | 🎯 V1   |
| Probability of Meeting Budget     | $P(\text{cost} \leq BAC)$ from Monte Carlo        | Leading        | ❌ Not built  | 🎯 V1   |
| Net Present Value (NPV)           | Standard DCF formula                              | Lagging        | ⚠️ Semi-ready | —       |
| Return on Investment (ROI)        | $ROI = (Benefits - Costs) / Costs$                | Lagging        | ❌ Not built  | —       |
| Change Request Rate               | Number of approved changes per period             | Leading        | ❌ Not built  | —       |
| Defect Density                    | Defects per deliverable / work package            | Lagging        | ❌ Not built  | —       |

---

## 3. Core Calculations

### Undergraduate

- **Critical Path Method (CPM)** — ✅ Ready | 🎯 V1
  - Forward pass: ES = max(EF of predecessors), EF = ES + Duration
  - Backward pass: LF = min(LS of successors), LS = LF − Duration
  - Total Float = LF − EF (or LS − ES)
  - Identification of all critical paths (zero float)
  - Handling of multiple equal-length critical paths

- **Float / Slack** — ✅ Ready | 🎯 V1
  - Total Float per task
  - Identification of flexible (non-critical) tasks
  - Edge case: negative float detection

- **Earned Value (EV) Computation** — ❌ Not built | 🎯 V1
  - $EV = \sum (Budget_i \times \%complete_i)$ across all WBS tasks
  - Per-task budget and % complete input
  - Cumulative EV over time periods

- **Schedule & Cost Variances** — ❌ Not built | 🎯 V1
  - PV from baseline schedule; EV from % complete; AC from actuals input
  - SV = EV − PV, CV = EV − AC
  - SPI = EV / PV, CPI = EV / AC
  - Interpretation guide and color status per result

- **Estimate at Completion (EAC)** — ❌ Not built | 🎯 V1
  - Formula 1: $EAC = AC + (BAC - EV)$ — remaining work at planned rate
  - Formula 2: $EAC = BAC / CPI$ — current cost trend continues
  - Side-by-side comparison of both results

- **Variance at Completion (VAC)** — ❌ Not built | 🎯 V1
  - $VAC = BAC - EAC$
  - Positive = projected underrun; negative = overrun

- **To-Complete Performance Index (TCPI)** — ❌ Not built | 🎯 V1
  - $TCPI = (BAC - EV) / (BAC - AC)$
  - Threshold flag: TCPI > 1 = red (must outperform past efficiency)
  - Edge case: denominator ≤ 0 detection

- **Risk Exposure** — ❌ Not built | 🎯 V1
  - $RE = p \times I$ per risk entry
  - Total exposure = sum across all risks
  - Ranked risk list by exposure value

### Postgraduate

- **PERT Three-Point Estimation** — ✅ Ready | 🎯 V1
  - Expected time: $T_E = (O + 4M + P) / 6$
  - Standard deviation: $\sigma = (P - O) / 6$
  - Variance: $\sigma^2$
  - Critical path expected duration = $\sum T_E$ of critical tasks
  - Critical path variance = $\sum \sigma^2$ of critical tasks

- **Schedule Probability of Success** — ✅ Ready | 🎯 V1
  - Z-score: $Z = (T_{target} - T_{E,path}) / \sigma_{path}$
  - $P(T \leq T_{target})$ from normal distribution
  - Inverse: duration for a given target probability

- **Advanced EAC (Multiple Formulas)** — ❌ Not built | 🎯 V1
  - Formula 3: $EAC = AC + (BAC - EV) / (CPI \times SPI)$ — combined performance
  - Scenario comparison table for all three EAC formulas

- **TCPI Scenarios** — ❌ Not built
  - TCPI toward BAC (original budget goal)
  - TCPI toward EAC (revised forecast goal)
  - Interpretation and threshold display for both

- **Earned Schedule (ES) Calculation** — ❌ Not built
  - ES = time point where cumulative PV equals current EV
  - $SV(t) = ES - \text{current time}$ in days/weeks

- **Cost of Risk / Contingency Reserve** — ⚠️ Semi-ready | 🎯 V1
  - $\text{Total Contingency} = \sum p_i I_i + \text{management reserve}$
  - Comparison of expected-case vs. worst-case budgeting

- **Risk-Adjusted EAC** — ❌ Not built
  - $EAC_{risk} = EAC + k \times RE_{total}$
  - Configurable confidence factor $k$

- **Schedule Compression (Crashing)** — ✅ Ready | 🎯 V1
  - Crash cost per day = $(CC - NC) / (NT - CT)$
  - Sequential crashing of cheapest critical task
  - Cost-time trade-off curve output

- **Monte Carlo Simulation** — ⚠️ Semi-ready | 🎯 V1
  - N-trial random sampling (configurable, e.g. 1,000–10,000 runs)
  - Duration distributions: triangular or beta (PERT) per task
  - Cost distributions: triangular per task
  - Outputs: mean, P50, P80, P90 for project duration and total cost
  - $P(\text{cost} \leq BAC)$ and $P(T \leq T_{target})$ from simulation histogram

- **Probabilistic Critical Path** — ⚠️ Semi-ready | 🎯 V1
  - Distribution of critical path identity across simulation trials
  - Tasks ranked by frequency of appearing on critical path

- **Aggregate Risk Exposure** — ❌ Not built | 🎯 V1
  - Sum of all $p_i I_i$ with optional probabilistic model weighting
  - Risk tolerance threshold comparison (e.g. flag if > 5% of BAC)

- **NPV / ROI** — ⚠️ Semi-ready
  - $NPV = \sum CF_t / (1 + r)^t$
  - $ROI = (\text{Total Benefits} - \text{Total Costs}) / \text{Total Costs}$

---

## 4. Data Management

- WBS task entry (name, budget, duration, dependencies, O/M/P estimates) — ⚠️ Semi-ready | 🎯 V1
- Period-by-period PV/EV/AC data entry (weekly/monthly toggle) — ❌ Not built | 🎯 V1
- Risk register entry (name, probability, impact, description) — ❌ Not built | 🎯 V1
- CSV and Excel import/export for all data types — ✅ Ready | 🎯 V1
- Project save and load (JSON format) — ✅ Ready | 🎯 V1
- Sample/demo datasets for undergraduate and postgraduate scenarios — ⚠️ Semi-ready | 🎯 V1

---

## 5. UI & UX

- Undergraduate mode and Postgraduate mode toggle (hides advanced features in undergrad mode) — ❌ Not built | 🎯 V1
- Step-by-step calculation walkthrough panel (shows formula → substitution → result) — ❌ Not built | 🎯 V1
- RAG color coding on all KPI values with configurable thresholds — ❌ Not built | 🎯 V1
- Tabbed layout: Input | CPM/Gantt | EVM | Risk | PERT/Monte Carlo | Summary Dashboard — ✅ Ready | 🎯 V1
- Export charts as PNG/PDF — ⚠️ Semi-ready | 🎯 V1
- Printable project performance report (summary of all KPIs + key charts) — ❌ Not built
