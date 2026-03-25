import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { RouterModule } from '@angular/router';

import { KpiCardComponent } from '../../shared/components/kpi-card/kpi-card.component';
import { activities, cpmResults, viewMode } from '../../core/store/project.store';
import { RAGStatus } from '../../core/models/evm.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatIconModule, MatButtonModule, RouterModule, KpiCardComponent],
  template: `
    <div class="dash-host">
      @if (!hasData()) {
        <!-- ── No data state ── -->
        <div class="no-data-state">
          <mat-icon>dashboard</mat-icon>
          <h3>No project data yet</h3>
          <p>Enter activities and run CPM analysis to see the summary dashboard.</p>
          <a mat-stroked-button routerLink="/input"> <mat-icon>edit</mat-icon> Go to Data Entry </a>
        </div>
      } @else {
        <!-- ── KPI cards row ── -->
        <div class="kpi-row">
          <app-kpi-card
            label="Project Duration"
            [value]="duration()"
            unit="days"
            icon="schedule"
            tooltip="Earliest project completion time (critical path length)"
            formula="Duration = max(EF of terminal activities)"
          />
          <app-kpi-card
            label="Critical Activities"
            [value]="criticalCount()"
            [unit]="'of ' + taskCount()"
            icon="warning"
            [rag]="criticalRag()"
            tooltip="Activities on the critical path — any delay extends the project"
          />
          <app-kpi-card
            label="Total Activities"
            [value]="taskCount()"
            icon="list_alt"
            tooltip="Number of activities in the project network"
          />
          <app-kpi-card
            label="Critical Paths"
            [value]="pathCount()"
            icon="account_tree"
            tooltip="Number of distinct critical paths through the network"
          />
          <app-kpi-card
            label="Avg Float"
            [value]="avgFloat()"
            unit="days"
            icon="hourglass_empty"
            [rag]="floatRag()"
            tooltip="Average total float of non-critical activities"
            formula="Float = LS − ES"
          />
          <app-kpi-card
            label="Network Density"
            [value]="densityPct()"
            unit="%"
            icon="hub"
            tooltip="Edge density = edges / (n×(n−1)/2) — how interconnected the network is"
          />
        </div>

        <!-- ── Critical path display ── -->
        <div class="section">
          <div class="section-title">
            <mat-icon>route</mat-icon>
            Critical Path{{ pathCount() > 1 ? 's' : '' }}
          </div>
          @for (path of criticalPaths(); track $index) {
            <div class="cp-row">
              <span class="cp-index">CP {{ $index + 1 }}</span>
              @for (node of path; track node; let last = $last) {
                <span class="cp-chip">{{ node }}</span>
                @if (!last) {
                  <mat-icon class="cp-arrow">chevron_right</mat-icon>
                }
              }
              <span class="cp-len">({{ path.length }} activities)</span>
            </div>
          }
        </div>

        <!-- ── Float distribution ── -->
        <div class="section">
          <div class="section-title">
            <mat-icon>bar_chart</mat-icon>
            Float Distribution
          </div>
          <div class="float-chart">
            <svg [attr.width]="floatBarWidth()" height="70">
              @for (bar of floatBars(); track bar.label) {
                <g [attr.transform]="'translate(' + bar.x + ', 0)'">
                  <rect
                    [attr.x]="0"
                    [attr.y]="60 - bar.height"
                    [attr.width]="bar.w - 2"
                    [attr.height]="bar.height"
                    [attr.fill]="bar.color"
                    rx="2"
                  />
                  <text x="0" y="68" font-size="9" fill="#78909c">{{ bar.label }}</text>
                  <text
                    [attr.x]="(bar.w - 2) / 2"
                    [attr.y]="55 - bar.height"
                    font-size="9"
                    text-anchor="middle"
                    fill="#546e7a"
                  >
                    {{ bar.count }}
                  </text>
                </g>
              }
            </svg>
            <div class="float-legend">
              <span class="swatch red"></span>Critical (0) <span class="swatch amber"></span>Low
              (1–2) <span class="swatch blue"></span>Medium (3–9)
              <span class="swatch green"></span>High (10+)
            </div>
          </div>
        </div>

        <!-- ── Schedule alerts ── -->
        @if (alerts().length > 0) {
          <div class="section">
            <div class="section-title">
              <mat-icon>notifications</mat-icon>
              Schedule Insights
            </div>
            <div class="alerts">
              @for (a of alerts(); track a.text) {
                <div class="alert-item" [class]="'alert-' + a.type">
                  <mat-icon>{{ a.icon }}</mat-icon>
                  <span>{{ a.text }}</span>
                </div>
              }
            </div>
          </div>
        }

        <!-- ── Learn mode: formula recap ── -->
        @if (isLearnMode()) {
          <div class="section learn-section">
            <div class="section-title">
              <mat-icon>school</mat-icon>
              Key CPM Formulae
            </div>
            <div class="formula-grid">
              <div class="formula-card">
                <div class="fc-label">Early Start</div>
                <div class="fc-formula">ES = max(EF of predecessors)</div>
              </div>
              <div class="formula-card">
                <div class="fc-label">Early Finish</div>
                <div class="fc-formula">EF = ES + Duration</div>
              </div>
              <div class="formula-card">
                <div class="fc-label">Late Finish</div>
                <div class="fc-formula">LF = min(LS of successors)</div>
              </div>
              <div class="formula-card">
                <div class="fc-label">Late Start</div>
                <div class="fc-formula">LS = LF − Duration</div>
              </div>
              <div class="formula-card">
                <div class="fc-label">Total Float</div>
                <div class="fc-formula">TF = LS − ES = LF − EF</div>
              </div>
              <div class="formula-card">
                <div class="fc-label">Critical</div>
                <div class="fc-formula">TF = 0</div>
              </div>
            </div>
          </div>
        }
      }
    </div>
  `,
  styles: [
    `
      .dash-host {
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        overflow-y: auto;
        height: 100%;
      }
      /* No-data */
      .no-data-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 60px 24px;
        color: #90a4ae;
        mat-icon {
          font-size: 56px;
          width: 56px;
          height: 56px;
        }
        h3 {
          margin: 0;
          font-size: 18px;
          color: #546e7a;
        }
        p {
          margin: 0;
          font-size: 13px;
        }
      }
      /* KPI row */
      .kpi-row {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 12px;
      }
      /* Section */
      .section {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 12px 16px;
      }
      .section-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 600;
        color: #37474f;
        margin-bottom: 10px;
        mat-icon {
          font-size: 16px;
          width: 16px;
          height: 16px;
          color: #1565c0;
        }
      }
      /* Critical path */
      .cp-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
        margin-bottom: 6px;
        font-size: 12px;
      }
      .cp-index {
        font-weight: 600;
        color: #c62828;
        min-width: 36px;
      }
      .cp-chip {
        background: #ffebee;
        color: #c62828;
        border: 1px solid #ef9a9a;
        border-radius: 4px;
        padding: 1px 6px;
        font-family: 'Roboto Mono', monospace;
      }
      .cp-arrow {
        font-size: 14px;
        width: 14px;
        height: 14px;
        color: #bdbdbd;
      }
      .cp-len {
        color: #90a4ae;
        font-size: 11px;
        margin-left: 4px;
      }
      /* Float chart */
      .float-chart {
        display: flex;
        align-items: flex-end;
        gap: 16px;
      }
      .float-legend {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 11px;
        color: #546e7a;
        flex-wrap: wrap;
      }
      .swatch {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 2px;
        &.red {
          background: #e53935;
        }
        &.amber {
          background: #fb8c00;
        }
        &.blue {
          background: #1e88e5;
        }
        &.green {
          background: #43a047;
        }
      }
      /* Alerts */
      .alerts {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .alert-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 12px;
        mat-icon {
          font-size: 16px;
          width: 16px;
          height: 16px;
        }
      }
      .alert-warn {
        background: #fff8e1;
        color: #e65100;
        mat-icon {
          color: #fb8c00;
        }
      }
      .alert-info {
        background: #e3f2fd;
        color: #0d47a1;
        mat-icon {
          color: #1565c0;
        }
      }
      .alert-ok {
        background: #e8f5e9;
        color: #1b5e20;
        mat-icon {
          color: #43a047;
        }
      }
      /* Learn formulae */
      .learn-section {
        background: #fffde7;
        border-color: #fff176;
      }
      .formula-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 8px;
      }
      .formula-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px 10px;
      }
      .fc-label {
        font-size: 11px;
        color: #78909c;
        margin-bottom: 2px;
      }
      .fc-formula {
        font-family: 'Roboto Mono', monospace;
        font-size: 12px;
        color: #1565c0;
      }
    `,
  ],
})
export class DashboardComponent {
  readonly hasData = computed(() => cpmResults() !== null);
  readonly taskCount = computed(() => activities().length);
  readonly duration = computed(() => cpmResults()?.project_duration ?? 0);
  readonly criticalPaths = computed(() => cpmResults()?.critical_paths ?? []);
  readonly pathCount = computed(() => this.criticalPaths().length);
  readonly criticalCount = computed(() => cpmResults()?.critical_activities?.length ?? 0);
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly avgFloat = computed(() => {
    const nodes = cpmResults()?.nodes ?? [];
    const nonCrit = nodes.filter((n) => !n.is_critical);
    if (!nonCrit.length) return 0;
    const sum = nonCrit.reduce((acc, n) => acc + n.total_float, 0);
    return +(sum / nonCrit.length).toFixed(1);
  });

  readonly densityPct = computed(() => {
    const r = cpmResults();
    if (!r) return 0;
    const n = r.nodes.length;
    const max = (n * (n - 1)) / 2;
    if (max === 0) return 0;
    return +((r.edges.length / max) * 100).toFixed(1);
  });

  readonly criticalRag = computed((): RAGStatus => {
    const ratio = this.criticalCount() / Math.max(1, this.taskCount());
    if (ratio > 0.6) return 'red';
    if (ratio > 0.35) return 'amber';
    return 'green';
  });

  readonly floatRag = computed((): RAGStatus => {
    const af = this.avgFloat();
    if (af >= 5) return 'green';
    if (af >= 2) return 'amber';
    return 'red';
  });

  readonly floatBars = computed(() => {
    const nodes = cpmResults()?.nodes ?? [];
    const buckets = [
      { label: '0', min: 0, max: 0, color: '#e53935', count: 0 },
      { label: '1-2', min: 1, max: 2, color: '#fb8c00', count: 0 },
      { label: '3-9', min: 3, max: 9, color: '#1e88e5', count: 0 },
      { label: '10+', min: 10, max: Infinity, color: '#43a047', count: 0 },
    ];
    for (const n of nodes) {
      const b = buckets.find((b) => n.total_float >= b.min && n.total_float <= b.max);
      if (b) b.count++;
    }
    const BAR_W = 40;
    const MAX_H = 55;
    const maxCount = Math.max(1, ...buckets.map((b) => b.count));
    return buckets.map((b, i) => ({
      ...b,
      x: i * BAR_W,
      w: BAR_W,
      height: Math.max(3, Math.round((b.count / maxCount) * MAX_H)),
    }));
  });

  readonly floatBarWidth = computed(() => this.floatBars().length * 40 + 10);

  readonly alerts = computed(() => {
    const r = cpmResults();
    if (!r) return [];
    const alerts: Array<{ type: string; icon: string; text: string }> = [];
    const ratio = r.critical_activities.length / Math.max(1, r.nodes.length);
    if (ratio > 0.6) {
      alerts.push({
        type: 'warn',
        icon: 'warning',
        text: `${Math.round(ratio * 100)}% of activities are critical — schedule is very sensitive to delays.`,
      });
    }
    if (this.pathCount() > 1) {
      alerts.push({
        type: 'warn',
        icon: 'account_tree',
        text: `${this.pathCount()} parallel critical paths detected — multiple risk points.`,
      });
    }
    const starts = r.nodes.filter((n) => !r.edges.some((e) => e.to === n.id));
    if (starts.length > 1) {
      alerts.push({
        type: 'info',
        icon: 'play_circle',
        text: `${starts.length} start activities — ensure they can all begin simultaneously.`,
      });
    }
    const ends = r.nodes.filter((n) => !r.edges.some((e) => e.from === n.id));
    if (ends.length > 1) {
      alerts.push({
        type: 'info',
        icon: 'stop_circle',
        text: `${ends.length} end activities — project finishes when the last one completes.`,
      });
    }
    if (ratio <= 0.3 && this.avgFloat() >= 5) {
      alerts.push({
        type: 'ok',
        icon: 'check_circle',
        text: 'Good schedule flexibility — most activities have healthy float.',
      });
    }
    return alerts;
  });
}
