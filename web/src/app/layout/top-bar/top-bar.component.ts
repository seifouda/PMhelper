import { Component, input, output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { viewMode, academicLevel } from '../../core/store/project.store';
import { ProjectIOService } from '../../core/services/project-io.service';

@Component({
  selector: 'app-top-bar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatMenuModule,
    MatDividerModule,
  ],
  templateUrl: './top-bar.component.html',
  styleUrl: './top-bar.component.scss',
})
export class TopBarComponent {
  private readonly io = inject(ProjectIOService);
  readonly mode = viewMode;
  readonly level = academicLevel;
  readonly sidebarCollapsed = input(false);
  readonly toggleSidebar = output();

  onToggleSidebar(): void {
    this.toggleSidebar.emit();
  }

  toggleMode(): void {
    viewMode.set(this.mode() === 'learn' ? 'clean' : 'learn');
  }

  toggleLevel(): void {
    academicLevel.set(this.level() === 'ug' ? 'pg' : 'ug');
  }

  openProject(): void {
    this.io.load();
  }

  saveProject(): void {
    this.io.save();
  }

  exportCsv(): void {
    this.io.exportCsv();
  }
}
