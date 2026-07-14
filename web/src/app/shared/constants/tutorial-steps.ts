import { TutorialStep } from '../../core/models/tutorial.model';

/**
 * Global tutorial steps for the app-wide guided tour.
 *
 * To add a new step:
 *   1. Add an entry to this array at the appropriate position.
 *   2. Set `selector` to a stable CSS selector for the target element.
 *   3. Optionally set `route` if the element lives on a specific page.
 *   4. Optionally set `group` for feature-scoped tutorials.
 *
 * Feature components can also register their own steps dynamically
 * via `TutorialService.registerSteps()`.
 */
export const GLOBAL_TUTORIAL_STEPS: TutorialStep[] = [
  // ── Top bar ───────────────────────────────────────────────────────────────
  {
    selector: '.pm-topbar__hamburger',
    title: 'Toggle Sidebar',
    description: 'Expand or collapse the navigation sidebar to show or hide the menu.',
    placement: 'bottom',
  },
  {
    selector: '.pm-topbar__brand',
    title: 'PM Scholar',
    description:
      'Welcome to PM Scholar! This is your project management learning companion. Use the sidebar to navigate between features.',
    placement: 'bottom',
  },
  {
    selector: '.pm-topbar__toggle:not(.pm-topbar__toggle--level)',
    title: 'Learn / Clean Mode',
    description:
      'Toggle between Learn Mode (shows formulas, step-by-step explanations, and educational content) and Clean View (shows results only).',
    placement: 'bottom',
  },
  {
    selector: '.pm-topbar__toggle--level',
    title: 'Academic Level',
    description:
      'Switch between Undergraduate (UG) and Postgraduate (PG) mode. PG unlocks advanced features: RCPS, Monte Carlo, WBS, SWOT, and PESTEL.',
    placement: 'bottom',
  },
  {
    selector: '.pm-topbar [matMenuTriggerFor]',
    title: 'Project Actions',
    description:
      'Open an existing project, save your current project, or export data to CSV from this menu.',
    placement: 'bottom',
  },

  // ── Sidebar navigation ────────────────────────────────────────────────────
  {
    selector: 'a[routerLink="/dashboard"]',
    title: 'Dashboard',
    description:
      'View KPIs, critical path summary, float distribution, and schedule insights at a glance.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/input"]',
    title: 'Data Entry',
    description:
      'Enter project activities with their durations, predecessors, and resource requirements. This is where you start every project.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/network"]',
    title: 'Network Diagram',
    description:
      'Visualize the Activity-on-Node (AoN) network diagram. The critical path is highlighted in red.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/gantt"]',
    title: 'Gantt Chart',
    description:
      'View the project schedule as a Gantt chart with early start bars, float bars, and critical path highlighting.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/pert"]',
    title: 'PERT Analysis',
    description:
      'Run three-point estimates (Optimistic, Most Likely, Pessimistic) and compute expected durations and variances.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/evm"]',
    title: 'Earned Value Management',
    description:
      'Track cost and schedule performance using EVM KPIs: CPI, SPI, EAC, ETC, and variance analysis.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/crashing"]',
    title: 'Crashing',
    description:
      'Analyze time-cost trade-offs to compress the project schedule by crashing critical activities.',
    route: '/dashboard',
    placement: 'right',
  },
  {
    selector: 'a[routerLink="/risk"]',
    title: 'Risk Analysis',
    description:
      'Build a risk register, assess probability and impact, and visualize risks on a heat map matrix.',
    route: '/dashboard',
    placement: 'right',
  },

  // ── PG-only features (shown only when in PG mode) ────────────────────────
  {
    selector: 'a[routerLink="/rcps"]',
    title: 'RCPS (Resource Scheduling)',
    description:
      'Resource-Constrained Project Scheduling — level resources across the project timeline. PG feature.',
    route: '/dashboard',
    placement: 'right',
    group: 'pg',
  },
  {
    selector: 'a[routerLink="/monte-carlo"]',
    title: 'Monte Carlo Simulation',
    description:
      'Run Monte Carlo simulations to estimate project completion probability distributions. PG feature.',
    route: '/dashboard',
    placement: 'right',
    group: 'pg',
  },
  {
    selector: 'a[routerLink="/wbs"]',
    title: 'Work Breakdown Structure',
    description:
      'Create and manage a hierarchical WBS with deliverables, work packages, and cost tracking. PG feature.',
    route: '/dashboard',
    placement: 'right',
    group: 'pg',
  },
  {
    selector: 'a[routerLink="/swot"]',
    title: 'SWOT Analysis',
    description:
      'Identify project Strengths, Weaknesses, Opportunities, and Threats with weighted scoring. PG feature.',
    route: '/dashboard',
    placement: 'right',
    group: 'pg',
  },
  {
    selector: 'a[routerLink="/pestel"]',
    title: 'PESTEL Analysis',
    description:
      'Analyze Political, Economic, Social, Technological, Environmental, and Legal factors. PG feature.',
    route: '/dashboard',
    placement: 'right',
    group: 'pg',
  },
];
