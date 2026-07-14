---
name: pm-concepts-explained
description: Use to understand the project-management concepts PMHelper implements (CPM, PERT, EVM, crashing, RCPS, resource leveling, cost/NPV/multi-objective optimization, project selection/AHP, risk, RACI, WBS, PESTEL/SWOT) and to find the exact source module for each. Great for learning the domain and for writing the paper.
---

# PM concepts → where they live in the code

Each concept below is implemented as **pure logic in `core/`**, usually with a
matching `*_step_generator.py` that produces the worked-out explanation. Open the
module to see the formulas in code.

## Scheduling
- **CPM (Critical Path Method)** — forward/backward pass computing ES/EF/LS/LF and
  float; the critical path is the zero-float chain that sets project duration.
  → `core/cpm_analyzer.py`; networks `core/network_builder.py`,
  `core/aoa_network_builder.py` (activity-on-arrow).
- **PERT** — three-point (optimistic/most-likely/pessimistic) beta estimate:
  expected `= (O + 4M + P)/6`, variance `= ((P−O)/6)²`; combine with the z-table for
  "probability of finishing by date T." → `core/pert_analyzer.py`,
  `core/three_point_engine.py`, `core/ztable_loader.py`.
- **Monte Carlo simulation** — sample task durations many times to get a completion
  distribution. → `core/monte_carlo_edu.py`, `core/cpm_sampler_edu.py`.

## Cost & value
- **EVM (Earned Value)** — PV, EV, AC → CV, SV, CPI, SPI, three EAC formulas, VAC,
  TCPI. → `core/evm_calculations_edu.py` (pure KPI funcs), models
  `core/evm_models_edu.py`. Note (`DECISIONS.md`): EAC₁ is the default; CPM and EVM
  tasks are separate classes linked by optional `cpm_task_id`.
- **Project crashing** — shorten the schedule by spending on the cheapest
  time-saving activities first (cost slope). → `core/crashing_step_generator.py`.
- **Cost estimation** — `core/cost_estimation.py`.
- **Cost / NPV / multi-objective optimization** — trade duration vs cost vs NPV;
  Pareto fronts. → `core/cost_optimization.py`, `core/npv_optimization.py`,
  `core/financial_calcs.py`, `core/multi_objective.py`.

## Resources
- **RCPS (resource-constrained scheduling)** — schedule when resources are limited.
  → `core/rcps_analyzer.py`.
- **Resource leveling** — smooth over-allocated resources (e.g. Burgess/min-moment).
  → `core/resource_leveling.py`, `core/leveling_step_generator.py`.

## Selection & risk
- **Project selection / AHP** — Analytic Hierarchy Process with 1–9 pairwise scale
  and a consistency ratio (published Random Index table); also linear scoring,
  benefit/cost, portfolio optimization. → `core/selection.py`,
  `core/factor_scoring.py`.
- **Risk** — delay probability, contingency buffers, variance-reduction strategy
  ROI, prioritization, and a risk register. → `core/risk_analysis.py`,
  `core/risk_register_edu.py`.

## Governance & strategy
- **RACI** — Responsible/Accountable/Consulted/Informed matrix.
  → `core/raci_model.py`.
- **RAG status** — Red/Amber/Green health, carried on each `Step`'s `rag` field.
- **WBS (Work Breakdown Structure)** — `core/wbs_models_edu.py`,
  `core/wbs_validator_edu.py`.
- **PESTEL / SWOT** — strategic-analysis models. → `core/pestel_models_edu.py`,
  `core/swot_models_edu.py`.
- **Project Charter** — `gui/tabs/charter_tab.py` and friends.

## The teaching device
For any concept, the `core/<x>_step_generator.py` returns `Step`s with the formula,
the number substitution, the result, and a plain-English interpretation — this is
what the app shows learners and what you can lift into a paper appendix.

## Related skills
[[understand-this-codebase]] for the architecture · [[writing-the-paper]] to turn
these into an academic write-up.
