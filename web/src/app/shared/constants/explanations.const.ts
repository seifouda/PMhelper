/**
 * Centralized PM glossary for Learn Mode tooltips.
 * Key = short label used in the UI; value = concise educational definition.
 */
export const EXPLANATIONS: Record<string, string> = {
  // CPM / Network
  ES: 'Early Start - the earliest time an activity can begin.',
  EF: 'Early Finish - the earliest an activity can complete. EF = ES + Duration.',
  LS: 'Late Start - the latest an activity can start without delaying the project.',
  LF: 'Late Finish - the latest an activity can finish without delaying the project.',
  Float:
    'Total Float - the time an activity can slip without affecting the project end date. Float = LS - ES.',
  'Critical Path':
    'The longest sequence of dependent activities - determines minimum project duration.',
  'Forward Pass': 'Calculates ES and EF for each activity from project start to finish.',
  'Backward Pass': 'Calculates LS and LF for each activity from project finish to start.',

  // PERT
  PERT: 'Program Evaluation and Review Technique - uses 3-point estimates to model uncertainty.',
  'Optimistic (O)': 'Best-case activity duration under ideal conditions.',
  'Most Likely (M)': 'Most probable activity duration under normal conditions.',
  'Pessimistic (P)': 'Worst-case activity duration under adverse conditions.',
  'Expected Time': 'te = (O + 4M + P) / 6 - weighted average from the Beta distribution.',
  Variance: 'Var = ((P - O) / 6)^2 - measures the spread of the estimate.',
  'Standard Deviation': 'SD = sqrt(project variance) - measures overall schedule uncertainty.',
  'Z-Score': 'Z = (T - mean) / SD - number of standard deviations between target and mean.',

  // EVM
  BAC: 'Budget at Completion - total planned budget for the project.',
  PV: 'Planned Value - budgeted cost of work scheduled to date.',
  EV: 'Earned Value - budgeted cost of work actually completed.',
  AC: 'Actual Cost - real cost incurred for work completed.',
  CV: 'Cost Variance (EV - AC) - negative means over budget.',
  SV: 'Schedule Variance (EV - PV) - negative means behind schedule.',
  CPI: 'Cost Performance Index (EV / AC) - below 1.0 = over budget.',
  SPI: 'Schedule Performance Index (EV / PV) - below 1.0 = behind schedule.',
  EAC: 'Estimate at Completion - projected total cost. EAC = BAC / CPI (typical).',
  VAC: 'Variance at Completion (BAC - EAC) - positive = expected savings.',
  TCPI: 'To-Complete Performance Index - required efficiency to meet BAC.',
  CR: 'Critical Ratio (CPI x SPI) - combined cost-schedule performance.',
  'S-Curve': 'Cumulative plot of PV, EV, AC over time - reveals variance trends.',

  // Risk
  'Risk Probability': 'Likelihood that a risk event will occur (0-1 or 1-5 scale).',
  'Risk Impact': 'Consequence of the risk event, often in monetary terms.',
  'Risk Exposure': 'Expected monetary value = Probability x Impact.',
  'Contingency Reserve': 'Sum of all risk exposures - budget set aside for known risks.',
  'Monte Carlo':
    'Stochastic simulation - runs thousands of random samples to model schedule/cost outcomes.',
  'P50 / P80 / P95':
    'Percentile durations from Monte Carlo - P80 means 80% chance of finishing within that duration.',

  // WBS
  WBS: 'Work Breakdown Structure - hierarchical decomposition of total project scope.',
  '100% Rule': 'Every WBS level must represent 100% of the parent scope - no gaps, no overlaps.',
  'Work Package': 'Lowest-level WBS element - can be estimated, scheduled, and tracked.',
  'Cost Rollup': 'Summing child element costs to compute parent cost.',

  // SWOT
  Strengths: 'Internal positive factors that give the project an advantage.',
  Weaknesses: 'Internal negative factors that put the project at a disadvantage.',
  Opportunities: 'External positive factors the project could exploit.',
  Threats: 'External negative factors that could cause problems.',

  // PESTEL
  PESTEL:
    'Macro-environment analysis across Political, Economic, Social, Technological, Environmental, Legal factors.',
  'Impact Score': 'Severity of the factor effect on the project (1-5 scale).',
  'Probability Score': 'Likelihood the factor materialises (1-5 scale).',

  // Resource Leveling / RCPS
  'Resource Leveling':
    'Adjusts activity start dates so resource demand stays within availability limits.',
  RCPS: 'Resource-Constrained Project Scheduling - extends project if resources are limited.',
  'Burgess Method': 'Heuristic that minimises the sum of squared daily resource usage.',

  // Crashing
  Crashing:
    'Compressing schedule by adding resources to critical-path activities - increases cost.',
  'Crash Cost': 'The extra cost to reduce an activity by one time unit.',
  'Cost Slope': '(Crash Cost - Normal Cost) / (Normal Duration - Crash Duration).',
};
