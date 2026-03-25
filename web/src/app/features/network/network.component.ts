import { ChangeDetectionStrategy, Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';

import { NetworkCanvasComponent } from './components/network-canvas/network-canvas.component';
import { ForwardPassStepperComponent } from './components/forward-pass-stepper/forward-pass-stepper.component';
import { BackwardPassStepperComponent } from './components/backward-pass-stepper/backward-pass-stepper.component';
import { cpmResults, viewMode } from '../../core/store/project.store';

type PassMode = 'none' | 'forward' | 'backward';

@Component({
  selector: 'app-network',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatButtonToggleModule,
    MatIconModule,
    MatDividerModule,
    NetworkCanvasComponent,
    ForwardPassStepperComponent,
    BackwardPassStepperComponent,
  ],
  template: `
    <div class="network-view">
      <!-- Toolbar -->
      <div class="view-toolbar">
        <h2 class="view-title">
          <mat-icon>account_tree</mat-icon>
          Network Diagram
        </h2>

        @if (isLearnMode() && hasData()) {
          <div class="pass-toggle">
            <span class="toggle-label">Step Through:</span>
            <mat-button-toggle-group [value]="passMode()" (change)="setPassMode($event.value)">
              <mat-button-toggle value="none">
                <mat-icon>visibility</mat-icon> Full View
              </mat-button-toggle>
              <mat-button-toggle value="forward">
                <mat-icon>arrow_forward</mat-icon> Forward Pass
              </mat-button-toggle>
              <mat-button-toggle value="backward">
                <mat-icon>arrow_back</mat-icon> Backward Pass
              </mat-button-toggle>
            </mat-button-toggle-group>
          </div>
        }

        @if (hasData()) {
          <div class="project-stats">
            <span class="stat">
              <mat-icon>schedule</mat-icon>
              Duration: <strong>{{ projectDuration() }}</strong>
            </span>
            <span class="stat critical">
              <mat-icon>warning</mat-icon>
              Critical: <strong>{{ criticalCount() }}</strong>
            </span>
          </div>
        }
      </div>

      <mat-divider />

      <!-- Main area -->
      <div class="network-main" [class.with-stepper]="passMode() !== 'none'">
        <!-- Canvas (always visible) -->
        <div class="canvas-area">
          <app-network-canvas />
        </div>

        <!-- Stepper panel (Learn Mode only) -->
        @if (isLearnMode() && passMode() === 'forward') {
          <div class="stepper-panel">
            <app-forward-pass-stepper />
          </div>
        }
        @if (isLearnMode() && passMode() === 'backward') {
          <div class="stepper-panel">
            <app-backward-pass-stepper />
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .network-view {
        display: flex;
        flex-direction: column;
        height: 100%;
        overflow: hidden;
      }
      .view-toolbar {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 8px 16px;
        flex-shrink: 0;
        flex-wrap: wrap;
      }
      .view-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1565c0;
        margin: 0;
        mat-icon {
          font-size: 1.2rem;
          width: 1.2rem;
          height: 1.2rem;
        }
      }
      .pass-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        .toggle-label {
          font-size: 0.85rem;
          color: #546e7a;
        }
      }
      .project-stats {
        display: flex;
        gap: 16px;
        margin-left: auto;
      }
      .stat {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 0.85rem;
        color: #546e7a;
        mat-icon {
          font-size: 1rem;
          width: 1rem;
          height: 1rem;
        }
        strong {
          color: #263238;
        }
        &.critical mat-icon,
        &.critical strong {
          color: #c62828;
        }
      }
      .network-main {
        display: flex;
        flex: 1;
        overflow: hidden;
        &.with-stepper .canvas-area {
          flex: 1;
        }
      }
      .canvas-area {
        flex: 1;
        overflow: hidden;
      }
      .stepper-panel {
        width: 300px;
        border-left: 1px solid #e0e0e0;
        background: white;
        overflow: hidden;
        display: flex;
        flex-direction: column;
      }
    `,
  ],
})
export class NetworkComponent {
  readonly isLearnMode = computed(() => viewMode() === 'learn');
  readonly hasData = computed(() => cpmResults() !== null);
  readonly projectDuration = computed(() => cpmResults()?.project_duration ?? 0);
  readonly criticalCount = computed(() => cpmResults()?.critical_activities?.length ?? 0);
  readonly passMode = signal<PassMode>('none');

  setPassMode(mode: PassMode): void {
    this.passMode.set(mode);
  }
}
