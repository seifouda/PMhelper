import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLinkActive } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';
import { pgVisible } from '../../core/store/project.store';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  pgOnly?: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    RouterLinkActive,
    MatListModule,
    MatIconModule,
    MatTooltipModule,
    MatBadgeModule,
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  readonly pgVisible = pgVisible;
  readonly collapsed = input(false);

  readonly navItems: NavItem[] = [
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Input / Data', icon: 'table_chart', route: '/input' },
    { label: 'Network', icon: 'account_tree', route: '/network' },
    { label: 'Gantt Chart', icon: 'view_timeline', route: '/gantt' },
    { label: 'PERT', icon: 'bar_chart', route: '/pert' },
    { label: 'EVM', icon: 'trending_up', route: '/evm' },
    { label: 'Crashing', icon: 'compress', route: '/crashing' },
    { label: 'Risk', icon: 'warning', route: '/risk' },
    { label: 'RCPS', icon: 'people', route: '/rcps', pgOnly: true },
    { label: 'Monte Carlo', icon: 'scatter_plot', route: '/monte-carlo', pgOnly: true },
    { label: 'WBS', icon: 'account_tree', route: '/wbs', pgOnly: true },
    { label: 'SWOT', icon: 'grid_4x4', route: '/swot', pgOnly: true },
    { label: 'PESTEL', icon: 'public', route: '/pestel', pgOnly: true },
  ];

  visibleItems(): NavItem[] {
    return this.navItems.filter((item) => !item.pgOnly || this.pgVisible());
  }
}
