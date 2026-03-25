import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
  AfterViewInit,
  OnDestroy,
  ElementRef,
  viewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { finalize } from 'rxjs';
import * as d3 from 'd3';

import { MonteCarloService, MCConfig } from '../../core/services/monte-carlo.service';
import { MCResults } from '../../core/models/monte-carlo.model';
import {
  activities,
  cpmResults,
  monteCarloResults,
  viewMode,
} from '../../core/store/project.store';

@Component({
  selector: 'app-monte-carlo',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
  template: `
    <div class="mc-host">
      @if (!hasData()) {
        <div class="empty-state">
          <mat-icon>casino</mat-icon>
          <p>
            Run CPM analysis first. Activities need three-point estimates for Monte Carlo
            simulation.
          </p>
        </div>
      } @else {
        <!-- ── Config + Run ── -->
        <div class="run-bar">
          <mat-form-field appearance="outline" class="small-field">
            <mat-label>Trials</mat-label>
            <input matInput type="number" [(ngModel)]="nTrials" [min]="100" [max]="50000" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="small-field">
            <mat-label>Seed (optional)</mat-label>
            <input matInput type="number" [(ngModel)]="seed" />
          </mat-form-field>

          <button mat-flat-button color="primary" (click)="runSimulation()" [disabled]="running()">
            @if (running()) {
              <mat-spinner diameter="16" />
            } @else {
              <mat-icon>play_arrow</mat-icon>
            }
            Run Simulation
          </button>

          @if (monteCarloResults()) {
            <span class="run-status ok"
              ><mat-icon>check_circle</mat-icon> {{ monteCarloResults()!.n_trials | number }} trials
              complete
            </span>
          }
          @if (error()) {
            <span class="run-status err"><mat-icon>error</mat-icon> {{ error() }}</span>
          }
        </div>

        @if (monteCarloResults()) {
          <!-- ── Percentile summary ── -->
          <div class="section summary-row" aria-live="polite">
            <div class="stat-box">
              <div class="stat-label">P50 Duration</div>
              <div class="stat-value">
                {{ monteCarloResults()!.p50_duration | number: '1.1-1' }}
              </div>
              <div class="stat-unit">days</div>
            </div>
            <div class="stat-box accent">
              <div class="stat-label">P80 Duration</div>
              <div class="stat-value">
                {{ monteCarloResults()!.p80_duration | number: '1.1-1' }}
              </div>
              <div class="stat-unit">days</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">P90 Duration</div>
              <div class="stat-value">
                {{ monteCarloResults()!.p90_duration | number: '1.1-1' }}
              </div>
              <div class="stat-unit">days</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">P(Cost ≤ BAC)</div>
              <div class="stat-value">
                {{ monteCarloResults()!.p_cost_within_bac | percent: '1.0-0' }}
              </div>
            </div>
          </div>

          <!-- ── Duration histogram ── -->
          <div class="section">
            <div class="section-title"><mat-icon>bar_chart</mat-icon> Duration Distribution</div>
            <div
              class="chart-container"
              #durationChart
              role="img"
              aria-label="Duration distribution histogram"
            ></div>
          </div>

          <!-- ── Cost histogram ── -->
          <div class="section">
            <div class="section-title"><mat-icon>bar_chart</mat-icon> Cost Distribution</div>
            <div
              class="chart-container"
              #costChart
              role="img"
              aria-label="Cost distribution histogram"
            ></div>
          </div>

          <!-- ── CP frequency table ── -->
          @if (cpFreqs().length) {
            <div class="section">
              <div class="section-title"><mat-icon>route</mat-icon> Critical Path Frequency</div>
              <div class="table-scroll">
                <table class="mc-table">
                  <thead>
                    <tr>
                      <th>Critical Path</th>
                      <th class="num-col">Frequency</th>
                      <th class="num-col">%</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (cp of cpFreqs(); track cp.path) {
                      <tr>
                        <td class="mono">{{ cp.path }}</td>
                        <td class="num">{{ cp.count }}</td>
                        <td class="num">{{ cp.pct | number: '1.1-1' }}%</td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            </div>
          }

          <!-- ── P(T ≤ X) lookup ── -->
          <div class="section">
            <div class="section-title"><mat-icon>search</mat-icon> P(T ≤ X) Lookup</div>
            <div class="lookup-row">
              <mat-form-field appearance="outline" class="small-field">
                <mat-label>Target duration (X)</mat-label>
                <input matInput type="number" [(ngModel)]="lookupX" />
              </mat-form-field>
              <span class="lookup-result" [class.highlight]="lookupResult() !== null">
                @if (lookupResult() !== null) {
                  P(T ≤ {{ lookupX }}) = <strong>{{ lookupResult()! | percent: '1.1-1' }}</strong>
                }
              </span>
            </div>
          </div>

          <!-- ── Learn mode ── -->
          @if (isLearnMode()) {
            <div class="section learn-section">
              <div class="section-title"><mat-icon>school</mat-icon> Monte Carlo Concepts</div>
              <div class="learn-body">
                <div class="formula-step">
                  <div class="step-num">1</div>
                  <div>
                    <strong>Simulation:</strong><br />
                    Each trial samples a random duration for every activity (from its distribution)
                    and computes the project completion time.
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">2</div>
                  <div>
                    <strong>Percentiles:</strong><br />
                    P80 = 80% of simulated outcomes finish at or before this duration. A common
                    confidence level for project baselines.
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">3</div>
                  <div>
                    <strong>Critical Path Frequency:</strong><br />
                    Tracks which path was critical in each trial — reveals paths that may become
                    critical under uncertainty.
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
      .mc-host {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 16px;
        overflow-y: auto;
        height: 100%;
      }
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 48px;
        color: #78909c;
        text-align: center;
      }
      .empty-state mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        opacity: 0.5;
      }
      .run-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
      }
      .small-field {
        width: 160px;
      }
      .run-status {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
      }
      .run-status.ok {
        color: #2e7d32;
      }
      .run-status.err {
        color: #c62828;
      }
      .summary-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
      }
      .stat-box {
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
      }
      .stat-box.accent {
        border-color: #7b1fa2;
        background: #f3e5f5;
      }
      .stat-label {
        font-size: 12px;
        color: #78909c;
      }
      .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: #263238;
      }
      .stat-unit {
        font-size: 12px;
        color: #90a4ae;
      }
      .section {
        background: #fff;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e0e0e0;
      }
      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        font-size: 15px;
        margin-bottom: 12px;
        color: #37474f;
      }
      .chart-container {
        width: 100%;
        min-height: 200px;
        overflow-x: auto;
      }
      .table-scroll {
        overflow-x: auto;
      }
      .mc-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .mc-table th {
        background: #f5f5f5;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #e0e0e0;
        font-weight: 500;
        color: #546e7a;
      }
      .mc-table td {
        padding: 8px;
        border-bottom: 1px solid #eee;
      }
      .num-col {
        text-align: right;
      }
      .num {
        text-align: right;
        font-variant-numeric: tabular-nums;
      }
      .mono {
        font-family: monospace;
        font-size: 12px;
      }
      .lookup-row {
        display: flex;
        align-items: center;
        gap: 16px;
      }
      .lookup-result {
        font-size: 15px;
        color: #546e7a;
      }
      .lookup-result.highlight {
        color: #263238;
      }
      .learn-section {
        background: #f3e5f5;
        border-color: #ce93d8;
      }
      .learn-body {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .formula-step {
        display: flex;
        gap: 12px;
        align-items: flex-start;
      }
      .step-num {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #7b1fa2;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 600;
        flex-shrink: 0;
      }
    `,
  ],
})
export class MonteCarloComponent implements AfterViewInit, OnDestroy {
  private readonly mcService = inject(MonteCarloService);
  private resizeObserver?: ResizeObserver;

  readonly durationChart = viewChild<ElementRef<HTMLDivElement>>('durationChart');
  readonly costChart = viewChild<ElementRef<HTMLDivElement>>('costChart');

  readonly activities = activities;
  readonly monteCarloResults = monteCarloResults;
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly running = signal(false);
  readonly error = signal<string | null>(null);

  nTrials = 5000;
  seed: number | null = null;
  lookupX = 0;

  readonly hasData = computed(() => cpmResults() !== null && activities().length > 0);

  readonly cpFreqs = computed(() => {
    const res = monteCarloResults();
    if (!res) return [];
    return Object.entries(res.cp_frequencies)
      .map(([path, count]) => ({ path, count, pct: (count / res.n_trials) * 100 }))
      .sort((a, b) => b.count - a.count);
  });

  readonly lookupResult = computed(() => {
    const res = monteCarloResults();
    if (!res || !this.lookupX || !res.durations.length) return null;
    const below = res.durations.filter((d) => d <= this.lookupX).length;
    return below / res.durations.length;
  });

  ngAfterViewInit(): void {
    if (monteCarloResults()) this.drawCharts();
    // Observe both chart containers for resize
    this.resizeObserver = new ResizeObserver(() => {
      if (monteCarloResults()) this.drawCharts();
    });
    const dEl = this.durationChart()?.nativeElement;
    const cEl = this.costChart()?.nativeElement;
    if (dEl) this.resizeObserver.observe(dEl);
    if (cEl) this.resizeObserver.observe(cEl);
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
  }

  runSimulation(): void {
    const acts = activities();
    if (!acts.length) return;
    this.running.set(true);
    this.error.set(null);

    const config: MCConfig = { n_trials: this.nTrials };
    if (this.seed !== null) config.seed = this.seed;

    this.mcService
      .run(acts, config)
      .pipe(finalize(() => this.running.set(false)))
      .subscribe({
        next: (result) => {
          monteCarloResults.set(result);
          setTimeout(() => this.drawCharts(), 0);
        },
        error: (err) => this.error.set(err?.message ?? 'Monte Carlo simulation failed'),
      });
  }

  private drawCharts(): void {
    this.drawHistogram(
      this.durationChart()?.nativeElement,
      monteCarloResults()?.durations ?? [],
      'Duration (days)',
      '#7b1fa2',
      [
        monteCarloResults()!.p50_duration,
        monteCarloResults()!.p80_duration,
        monteCarloResults()!.p90_duration,
      ],
      ['P50', 'P80', 'P90'],
    );
    this.drawHistogram(
      this.costChart()?.nativeElement,
      monteCarloResults()?.costs ?? [],
      'Cost',
      '#00695c',
      [],
      [],
    );
  }

  private drawHistogram(
    container: HTMLDivElement | undefined,
    data: number[],
    xlabel: string,
    barColor: string,
    markers: number[],
    markerLabels: string[],
  ): void {
    if (!container || !data.length) return;

    d3.select(container).selectAll('*').remove();

    const margin = { top: 10, right: 20, bottom: 40, left: 55 };
    const width = Math.max(300, container.clientWidth) - margin.left - margin.right;
    const height = 180 - margin.top - margin.bottom;

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3
      .scaleLinear()
      .domain(d3.extent(data) as [number, number])
      .nice()
      .range([0, width]);
    const bins = d3
      .bin()
      .domain(x.domain() as [number, number])
      .thresholds(40)(data);
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(bins, (b) => b.length)!])
      .range([height, 0]);

    svg
      .selectAll('.bar')
      .data(bins)
      .enter()
      .append('rect')
      .attr('x', (d) => x(d.x0!))
      .attr('y', (d) => y(d.length))
      .attr('width', (d) => Math.max(0, x(d.x1!) - x(d.x0!) - 1))
      .attr('height', (d) => height - y(d.length))
      .attr('fill', barColor)
      .attr('opacity', 0.75);

    // Percentile markers
    const markerColors = ['#f57f17', '#c62828', '#1b5e20'];
    markers.forEach((val, i) => {
      svg
        .append('line')
        .attr('x1', x(val))
        .attr('x2', x(val))
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', markerColors[i] ?? '#000')
        .attr('stroke-width', 1.5)
        .attr('stroke-dasharray', '5,3');
      svg
        .append('text')
        .attr('x', x(val) + 3)
        .attr('y', 10 + i * 12)
        .attr('font-size', '10px')
        .attr('fill', markerColors[i] ?? '#000')
        .text(`${markerLabels[i]}: ${val.toFixed(1)}`);
    });

    svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x).ticks(8));
    svg.append('g').call(d3.axisLeft(y).ticks(5));

    svg
      .append('text')
      .attr('x', width / 2)
      .attr('y', height + 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text(xlabel);
    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -42)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Frequency');
  }
}
