import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { finalize } from 'rxjs';

import { PertService } from '../../core/services/pert.service';
import { StepWalkthroughComponent } from '../../shared/components/step-walkthrough/step-walkthrough.component';
import { activities, pertResults, viewMode } from '../../core/store/project.store';
import { CalculationStep } from '../../core/models/step.model';

// ── Bell curve SVG constants ───────────────────────────────────────────────
const CURVE_W = 420;
const CURVE_H = 100;
const CURVE_PADDING_X = 24;
const CURVE_POINTS = 120;

@Component({
  selector: 'app-pert',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    StepWalkthroughComponent,
  ],
  template: `
    <div class="pert-host">
      <!-- ── No activities ── -->
      @if (!hasActivities()) {
        <div class="empty-state">
          <mat-icon>functions</mat-icon>
          <p>Enter activities with 3-point estimates (O / M / P) to use PERT analysis.</p>
        </div>
      } @else {
        <!-- ── 3-point estimates table ── -->
        <div class="section">
          <div class="section-title">
            <mat-icon>table_chart</mat-icon>
            3-Point Estimates
            @if (missingEstimates()) {
              <span class="badge warn">Some estimates missing — using duration as M</span>
            }
          </div>
          <div class="table-scroll">
            <table class="pert-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Activity</th>
                  <th title="Optimistic">O</th>
                  <th title="Most Likely">M</th>
                  <th title="Pessimistic">P</th>
                  <th title="Expected time = (O + 4M + P) / 6">
                    tₑ <span class="formula-hint">=(O+4M+P)/6</span>
                  </th>
                  <th title="Variance = ((P − O) / 6)²">
                    σ² <span class="formula-hint">=((P−O)/6)²</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                @for (row of pertRows(); track row.id) {
                  <tr [class.missing]="row.missing">
                    <td class="mono">{{ row.id }}</td>
                    <td>{{ row.activity }}</td>
                    <td class="num">{{ row.o }}</td>
                    <td class="num">{{ row.m }}</td>
                    <td class="num">{{ row.p }}</td>
                    <td class="num accent">{{ row.te | number: '1.2-2' }}</td>
                    <td class="num muted">{{ row.variance | number: '1.3-3' }}</td>
                  </tr>
                }
              </tbody>
              <tfoot>
                <tr class="totals">
                  <td colspan="5" class="right-label">Project (critical path sum):</td>
                  <td class="num accent bold">
                    @if (pertResults()) {
                      {{ pertResults()!.project_expected_duration | number: '1.2-2' }}
                    } @else {
                      —
                    }
                  </td>
                  <td class="num muted bold">
                    @if (pertResults()) {
                      {{ pertResults()!.project_variance | number: '1.3-3' }}
                    } @else {
                      —
                    }
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Run button -->
          <div class="run-row">
            <button mat-flat-button color="primary" (click)="runPert()" [disabled]="running()">
              @if (running()) {
                <mat-spinner diameter="16" />
              } @else {
                <mat-icon>play_arrow</mat-icon>
              }
              Run PERT Analysis
            </button>
            @if (pertResults()) {
              <span class="run-status ok">
                <mat-icon>check_circle</mat-icon>
                Analysis complete
              </span>
            }
            @if (error()) {
              <span class="run-status err">
                <mat-icon>error</mat-icon>
                {{ error() }}
              </span>
            }
          </div>
        </div>

        <!-- ── Results ── -->
        @if (pertResults()) {
          <div class="section results-row">
            <div class="stat-box">
              <div class="stat-label">Expected Duration (μ)</div>
              <div class="stat-value">
                {{ pertResults()!.project_expected_duration | number: '1.2-2' }}
              </div>
              <div class="stat-unit">days</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Variance (σ²)</div>
              <div class="stat-value">{{ pertResults()!.project_variance | number: '1.3-3' }}</div>
            </div>
            <div class="stat-box accent">
              <div class="stat-label">Std Deviation (σ)</div>
              <div class="stat-value">{{ pertResults()!.project_std_dev | number: '1.2-2' }}</div>
              <div class="stat-unit">days</div>
            </div>
          </div>

          <!-- ── Probability calculator ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>percent</mat-icon>
              Probability Calculator
            </div>
            <div class="prob-row">
              <mat-form-field appearance="outline" class="target-field">
                <mat-label>Target duration (T)</mat-label>
                <input
                  matInput
                  type="number"
                  [(ngModel)]="targetDuration"
                  (ngModelChange)="onTargetChange()"
                  [min]="1"
                  placeholder="e.g. 30"
                />
                <mat-hint>days</mat-hint>
              </mat-form-field>

              @if (targetDuration > 0) {
                <div class="prob-result">
                  <span class="z-score">Z = {{ zScore() | number: '1.3-3' }}</span>
                  <span
                    class="prob-value"
                    [class.high]="probability() >= 0.8"
                    [class.mid]="probability() >= 0.5 && probability() < 0.8"
                    [class.low]="probability() < 0.5"
                  >
                    P(T ≤ {{ targetDuration }}) = {{ probability() * 100 | number: '1.1-1' }}%
                  </span>
                </div>
              }
            </div>

            <!-- Bell curve SVG -->
            <div class="curve-wrap">
              <svg [attr.width]="CURVE_W" [attr.height]="CURVE_H + 20" class="bell-svg">
                <!-- Shaded area under curve for T -->
                @if (targetDuration > 0) {
                  <path [attr.d]="shadedPath()" fill="#1976d2" opacity="0.15" />
                }
                <!-- Main curve -->
                <polyline
                  [attr.points]="curvePoints()"
                  fill="none"
                  stroke="#1976d2"
                  stroke-width="2"
                  stroke-linejoin="round"
                />
                <!-- μ line -->
                <line
                  [attr.x1]="muX()"
                  y1="4"
                  [attr.x2]="muX()"
                  [attr.y2]="CURVE_H + 2"
                  stroke="#555"
                  stroke-width="1"
                  stroke-dasharray="4,3"
                />
                <text
                  [attr.x]="muX()"
                  [attr.y]="CURVE_H + 14"
                  text-anchor="middle"
                  font-size="10"
                  fill="#555"
                >
                  μ={{ pertResults()!.project_expected_duration | number: '1.1-1' }}
                </text>
                <!-- Target line -->
                @if (targetDuration > 0) {
                  <line
                    [attr.x1]="targetX()"
                    y1="4"
                    [attr.x2]="targetX()"
                    [attr.y2]="CURVE_H + 2"
                    stroke="#e53935"
                    stroke-width="1.5"
                    stroke-dasharray="4,2"
                  />
                  <text
                    [attr.x]="targetX()"
                    [attr.y]="CURVE_H + 14"
                    text-anchor="middle"
                    font-size="10"
                    fill="#e53935"
                  >
                    T={{ targetDuration }}
                  </text>
                }
                <!-- Baseline -->
                <line
                  x1="0"
                  [attr.y1]="CURVE_H"
                  [attr.x2]="CURVE_W"
                  [attr.y2]="CURVE_H"
                  stroke="#ccc"
                  stroke-width="1"
                />
              </svg>
            </div>
          </div>

          <!-- ── Learn mode: formula walkthrough ── -->
          @if (isLearnMode()) {
            @if (workedSteps().length) {
              <div class="section">
                <app-step-walkthrough title="PERT Worked Solution" [steps]="workedSteps()" />
              </div>
            }
            <div class="section learn-section">
              <div class="section-title">
                <mat-icon>school</mat-icon>
                PERT Formula Walkthrough
              </div>
              <div class="learn-body">
                <div class="formula-step">
                  <div class="step-num">1</div>
                  <div>
                    <strong>Expected Time per Activity:</strong><br />
                    <code>tₑ = (O + 4M + P) / 6</code><br />
                    <span class="hint"
                      >Beta distribution mean approximation (weighted average)</span
                    >
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">2</div>
                  <div>
                    <strong>Variance per Activity:</strong><br />
                    <code>σ² = ((P − O) / 6)²</code><br />
                    <span class="hint">Square of the "one-sixth rule" range estimate</span>
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">3</div>
                  <div>
                    <strong>Project Expected Duration:</strong><br />
                    <code>μ = Σ tₑ (critical path activities)</code><br />
                    <span class="hint">Sum of expected times along the critical path</span>
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">4</div>
                  <div>
                    <strong>Project Variance:</strong><br />
                    <code>σ² = Σ σ²ᵢ (critical path activities)</code><br />
                    <span class="hint">Variances of independent activities are additive</span>
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">5</div>
                  <div>
                    <strong>Z-Score for target duration T:</strong><br />
                    <code>Z = (T − μ) / σ</code><br />
                    @if (targetDuration > 0) {
                      <span class="hint substituted">
                        = ({{ targetDuration }} −
                        {{ pertResults()!.project_expected_duration | number: '1.2-2' }}) /
                        {{ pertResults()!.project_std_dev | number: '1.2-2' }} =
                        {{ zScore() | number: '1.3-3' }}
                      </span>
                    }
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">6</div>
                  <div>
                    <strong>Probability:</strong><br />
                    <code>P(T ≤ target) = Φ(Z)</code><br />
                    <span class="hint">Standard normal CDF evaluated at Z</span>
                    @if (targetDuration > 0) {
                      <span class="hint substituted"
                        >= Φ({{ zScore() | number: '1.3-3' }}) =
                        {{ probability() * 100 | number: '1.1-1' }}%</span
                      >
                    }
                  </div>
                </div>
              </div>
            </div>
          }
        }
      }
    </div>
  `,
  styles: [
    `
      .pert-host {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 16px;
        overflow-y: auto;
        height: 100%;
      }
      .empty-state {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 40px 24px;
        color: #90a4ae;
        mat-icon {
          font-size: 40px;
          width: 40px;
          height: 40px;
        }
        p {
          margin: 0;
          font-size: 13px;
        }
      }
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
      .badge {
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 400;
      }
      .badge.warn {
        background: #fff3e0;
        color: #e65100;
      }
      /* Table */
      .table-scroll {
        overflow-x: auto;
      }
      .pert-table {
        border-collapse: collapse;
        font-size: 12px;
        width: 100%;
        th,
        td {
          padding: 5px 10px;
          border: 1px solid #e0e0e0;
          white-space: nowrap;
        }
        th {
          background: #f5f7fa;
          color: #546e7a;
          font-weight: 600;
        }
        .formula-hint {
          font-size: 10px;
          color: #90a4ae;
          font-weight: 400;
        }
        .mono {
          font-family: 'Roboto Mono', monospace;
        }
        .num {
          text-align: right;
        }
        .accent {
          color: #1565c0;
          font-weight: 600;
        }
        .muted {
          color: #78909c;
        }
        .bold {
          font-weight: 700;
        }
        .right-label {
          text-align: right;
          font-style: italic;
          color: #546e7a;
          font-size: 11px;
        }
        .missing td {
          background: #fff8e1;
        }
        tfoot tr.totals {
          background: #f5f7fa;
        }
      }
      /* Run row */
      .run-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 10px;
        mat-spinner {
          display: inline-flex;
        }
      }
      .run-status {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        mat-icon {
          font-size: 14px;
          width: 14px;
          height: 14px;
        }
      }
      .run-status.ok {
        color: #2e7d32;
        mat-icon {
          color: #43a047;
        }
      }
      .run-status.err {
        color: #c62828;
        mat-icon {
          color: #e53935;
        }
      }
      /* Results row */
      .results-row {
        display: flex;
        gap: 12px;
        padding: 14px 16px;
      }
      .stat-box {
        flex: 1;
        background: #f5f7fa;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 10px 14px;
      }
      .stat-box.accent {
        background: #e3f2fd;
        border-color: #90caf9;
      }
      .stat-label {
        font-size: 11px;
        color: #78909c;
      }
      .stat-value {
        font-size: 22px;
        font-weight: 700;
        color: #1565c0;
        line-height: 1.2;
      }
      .stat-unit {
        font-size: 11px;
        color: #90a4ae;
      }
      /* Probability */
      .prob-row {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
      }
      .target-field {
        width: 200px;
      }
      .prob-result {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .z-score {
        font-family: 'Roboto Mono', monospace;
        font-size: 14px;
        color: #546e7a;
      }
      .prob-value {
        font-size: 18px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 4px;
        &.high {
          background: #e8f5e9;
          color: #2e7d32;
        }
        &.mid {
          background: #fff8e1;
          color: #e65100;
        }
        &.low {
          background: #ffebee;
          color: #c62828;
        }
      }
      /* Bell curve */
      .curve-wrap {
        margin-top: 8px;
        overflow-x: auto;
      }
      .bell-svg {
        display: block;
      }
      /* Learn */
      .learn-section {
        background: #fffde7;
        border-color: #fff176;
      }
      .learn-body {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .formula-step {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 8px 10px;
        background: white;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
      }
      .step-num {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #1565c0;
        color: white;
        font-size: 11px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }
      code {
        font-family: 'Roboto Mono', monospace;
        font-size: 12px;
        color: #1565c0;
        background: #e3f2fd;
        padding: 1px 4px;
        border-radius: 2px;
      }
      .hint {
        font-size: 11px;
        color: #78909c;
      }
      .hint.substituted {
        color: #1b5e20;
        font-weight: 500;
        display: block;
        margin-top: 2px;
      }
    `,
  ],
})
export class PertComponent {
  private readonly pertService = inject(PertService);

  readonly CURVE_W = CURVE_W;
  readonly CURVE_H = CURVE_H;

  // Store signals
  readonly activities = activities;
  readonly pertResults = pertResults;
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly running = signal(false);
  readonly error = signal<string | null>(null);
  readonly workedSteps = signal<CalculationStep[]>([]);

  targetDuration = 0;

  readonly hasActivities = computed(() => activities().length > 0);

  readonly missingEstimates = computed(() =>
    activities().some(
      (a) => a.optimistic == null || a.most_likely == null || a.pessimistic == null,
    ),
  );

  readonly pertRows = computed(() =>
    activities().map((a) => {
      const o = a.optimistic ?? a.duration;
      const m = a.most_likely ?? a.duration;
      const p = a.pessimistic ?? a.duration;
      const te = (o + 4 * m + p) / 6;
      const variance = Math.pow((p - o) / 6, 2);
      return {
        id: a.id,
        activity: a.activity,
        o,
        m,
        p,
        te,
        variance,
        missing: a.optimistic == null || a.most_likely == null || a.pessimistic == null,
      };
    }),
  );

  readonly zScore = computed(() => {
    const pr = pertResults();
    if (!pr || this.targetDuration <= 0) return 0;
    if (pr.project_std_dev === 0) return 0;
    return (this.targetDuration - pr.project_expected_duration) / pr.project_std_dev;
  });

  readonly probability = computed(() => normalCdf(this.zScore()));

  // ── Bell curve ─────────────────────────────────────────────────────────

  private curveDomain = computed(() => {
    const pr = pertResults();
    if (!pr) return { min: 0, max: 1 };
    const mu = pr.project_expected_duration;
    const sigma = Math.max(pr.project_std_dev, 0.01);
    return { min: mu - 4 * sigma, max: mu + 4 * sigma };
  });

  readonly curvePoints = computed(() => {
    const pr = pertResults();
    if (!pr) return '';
    const { min, max } = this.curveDomain();
    const mu = pr.project_expected_duration;
    const sigma = Math.max(pr.project_std_dev, 0.01);
    const step = (max - min) / CURVE_POINTS;
    const pts: string[] = [];
    for (let i = 0; i <= CURVE_POINTS; i++) {
      const x = min + i * step;
      const y = normalPdf(x, mu, sigma);
      pts.push(`${xToSvg(x, min, max)},${yToSvg(y, normalPdf(mu, mu, sigma))}`);
    }
    return pts.join(' ');
  });

  readonly shadedPath = computed(() => {
    const pr = pertResults();
    if (!pr || this.targetDuration <= 0) return '';
    const { min, max } = this.curveDomain();
    const mu = pr.project_expected_duration;
    const sigma = Math.max(pr.project_std_dev, 0.01);
    const maxPdf = normalPdf(mu, mu, sigma);
    const tClamp = Math.min(this.targetDuration, max);
    const step =
      (tClamp - min) / Math.max(1, Math.round(((tClamp - min) / (max - min)) * CURVE_POINTS));
    const pts: string[] = [];
    const startX = xToSvg(min, min, max);
    pts.push(`${startX},${CURVE_H}`);
    const steps = Math.max(2, Math.round((CURVE_POINTS * (tClamp - min)) / (max - min)));
    for (let i = 0; i <= steps; i++) {
      const x = min + (i / steps) * (tClamp - min);
      const y = normalPdf(x, mu, sigma);
      pts.push(`${xToSvg(x, min, max)},${yToSvg(y, maxPdf)}`);
    }
    const endX = xToSvg(tClamp, min, max);
    pts.push(`${endX},${CURVE_H}`);
    return `M ${pts[0]} L ${pts.slice(1).join(' L ')} Z`;
  });

  readonly muX = computed(() => {
    const pr = pertResults();
    if (!pr) return CURVE_W / 2;
    const { min, max } = this.curveDomain();
    return xToSvg(pr.project_expected_duration, min, max);
  });

  readonly targetX = computed(() => {
    const { min, max } = this.curveDomain();
    return xToSvg(this.targetDuration, min, max);
  });

  // ── Actions ────────────────────────────────────────────────────────────

  runPert(): void {
    const acts = activities();
    if (!acts.length) return;
    this.running.set(true);
    this.error.set(null);
    this.pertService
      .analyze(acts, this.targetDuration > 0 ? this.targetDuration : undefined)
      .pipe(finalize(() => this.running.set(false)))
      .subscribe({
        next: (result) => {
          pertResults.set(result);
          // Fetch worked-solution steps for learn mode
          this.pertService.getSteps(acts).subscribe({
            next: (steps) => this.workedSteps.set(steps),
            error: () => this.workedSteps.set([]),
          });
        },
        error: (err) => this.error.set(err?.error?.detail ?? 'Analysis failed'),
      });
  }

  onTargetChange(): void {
    // Computed signals auto-update — nothing extra to do
  }
}

// ── Math helpers ─────────────────────────────────────────────────────────────

function normalPdf(x: number, mu: number, sigma: number): number {
  const z = (x - mu) / sigma;
  return Math.exp(-0.5 * z * z) / (sigma * Math.sqrt(2 * Math.PI));
}

/** Abramowitz & Stegun 5-term approximation of the standard normal CDF */
export function normalCdf(z: number): number {
  if (z >= 8.0) return 1.0;
  if (z <= -8.0) return 0.0;
  const t = 1.0 / (1.0 + 0.2316419 * Math.abs(z));
  const poly =
    t *
    (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  const pdf = Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI);
  const p = 1.0 - pdf * poly;
  return z >= 0 ? p : 1 - p;
}

function xToSvg(x: number, domainMin: number, domainMax: number): number {
  const range = domainMax - domainMin;
  return CURVE_PADDING_X + ((x - domainMin) / range) * (CURVE_W - CURVE_PADDING_X * 2);
}

function yToSvg(y: number, yMax: number): number {
  const usableH = CURVE_H - 8;
  return CURVE_H - (y / yMax) * usableH;
}
