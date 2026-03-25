import { Routes } from '@angular/router';
import { pgOnlyGuard } from './core/guards/pg-only.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: '',
    loadComponent: () =>
      import('./layout/app-shell/app-shell.component').then((m) => m.AppShellComponent),
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },
      {
        path: 'input',
        loadComponent: () =>
          import('./features/input/input.component').then((m) => m.InputComponent),
      },
      {
        path: 'network',
        loadComponent: () =>
          import('./features/network/network.component').then((m) => m.NetworkComponent),
      },
      {
        path: 'gantt',
        loadComponent: () =>
          import('./features/gantt/gantt.component').then((m) => m.GanttComponent),
      },
      {
        path: 'pert',
        loadComponent: () => import('./features/pert/pert.component').then((m) => m.PertComponent),
      },
      {
        path: 'evm',
        loadComponent: () => import('./features/evm/evm.component').then((m) => m.EvmComponent),
      },
      {
        path: 'crashing',
        loadComponent: () =>
          import('./features/crashing/crashing.component').then((m) => m.CrashingComponent),
      },
      {
        path: 'risk',
        loadComponent: () => import('./features/risk/risk.component').then((m) => m.RiskComponent),
      },
      // PG-only routes
      {
        path: 'rcps',
        canActivate: [pgOnlyGuard],
        loadComponent: () => import('./features/rcps/rcps.component').then((m) => m.RcpsComponent),
      },
      {
        path: 'monte-carlo',
        canActivate: [pgOnlyGuard],
        loadComponent: () =>
          import('./features/monte-carlo/monte-carlo.component').then((m) => m.MonteCarloComponent),
      },
      {
        path: 'wbs',
        canActivate: [pgOnlyGuard],
        loadComponent: () => import('./features/wbs/wbs.component').then((m) => m.WbsComponent),
      },
      {
        path: 'swot',
        canActivate: [pgOnlyGuard],
        loadComponent: () => import('./features/swot/swot.component').then((m) => m.SwotComponent),
      },
      {
        path: 'pestel',
        canActivate: [pgOnlyGuard],
        loadComponent: () =>
          import('./features/pestel/pestel.component').then((m) => m.PestelComponent),
      },
    ],
  },
  { path: '**', redirectTo: '/dashboard' },
];
