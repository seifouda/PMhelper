import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';

import { GanttCanvasComponent } from './components/gantt-canvas/gantt-canvas.component';
import { cpmResults, viewMode } from '../../core/store/project.store';

@Component({
  selector: 'app-gantt',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatButtonToggleModule, MatIconModule, FormsModule, GanttCanvasComponent],
  template: `
    <div class="gantt-host">
      <!-- Header bar -->
      <div class="gantt-header">
        <div class="gantt-title">
          <mat-icon>calendar_view_week</mat-icon>
          <span>Gantt Chart</span>
          @if (hasData()) {
            <span class="stat-chip">Duration: {{ duration() }}</span>
            <span class="stat-chip critical">Critical: {{ criticalCount() }}</span>
          }
        </div>
      </div>

      <!-- Canvas -->
      <div class="gantt-body">
        <app-gantt-canvas />
      </div>

      <!-- Learn mode tip -->
      @if (isLearnMode() && hasData()) {
        <div class="learn-tip">
          <mat-icon>lightbulb</mat-icon>
          <span>
            <strong>Gantt Legend:</strong>
            Dark bar = Early schedule (ES→EF). &nbsp; Light extension = Float (EF→LF). &nbsp; Dashed
            arrows = Finish-to-Start dependencies.
          </span>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .gantt-host {
        display: flex;
        flex-direction: column;
        height: 100%;
        gap: 0;
      }
      .gantt-header {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        background: white;
        border-bottom: 1px solid #e0e0e0;
        min-height: 44px;
      }
      .gantt-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        font-size: 13px;
        color: #37474f;
        mat-icon {
          color: #1565c0;
          font-size: 18px;
          width: 18px;
          height: 18px;
        }
      }
      .stat-chip {
        background: #e3f2fd;
        color: #1565c0;
        border-radius: 12px;
        padding: 1px 8px;
        font-size: 11px;
        font-weight: 500;
      }
      .stat-chip.critical {
        background: #ffebee;
        color: #c62828;
      }
      .gantt-body {
        flex: 1;
        overflow: hidden;
        padding: 8px;
      }
      .learn-tip {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: #fffde7;
        border-top: 1px solid #fff176;
        font-size: 12px;
        color: #555;
        mat-icon {
          color: #f9a825;
          font-size: 16px;
          width: 16px;
          height: 16px;
        }
      }
    `,
  ],
})
export class GanttComponent {
  readonly hasData = computed(() => cpmResults() !== null);
  readonly duration = computed(() => cpmResults()?.project_duration ?? 0);
  readonly criticalCount = computed(() => cpmResults()?.critical_activities?.length ?? 0);
  readonly isLearnMode = computed(() => viewMode() === 'learn');
}
