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

import { CrashingService, CrashingRequest } from '../../core/services/crashing.service';
import { activities, cpmResults, crashingResults, viewMode } from '../../core/store/project.store';
import { CrashingResults, CrashingStep } from '../../core/models/project.model';

@Component({
  selector: 'app-crashing',
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
    <div class="crash-host">
      @if (!hasData()) {
        <div class="empty-state">
          <mat-icon>compress</mat-icon>
          <p>
            Run CPM analysis first and ensure activities have <strong>min_duration</strong> and
            <strong>crash_cost</strong> data.
          </p>
        </div>
      } @else {
        <!-- ── Config + Run ── -->
        <div class="run-bar">
          <mat-form-field appearance="outline" class="rate-field">
            <mat-label>Indirect cost / day</mat-label>
            <input matInput type="number" [(ngModel)]="indirectCostRate" [min]="0" />
          </mat-form-field>

          <button mat-flat-button color="primary" (click)="runCrashing()" [disabled]="running()">
            @if (running()) {
              <mat-spinner diameter="16" />
            } @else {
              <mat-icon>play_arrow</mat-icon>
            }
            Run Crashing
          </button>

          @if (crashingResults()) {
            <span class="run-status ok"><mat-icon>check_circle</mat-icon> Analysis complete</span>
          }
          @if (error()) {
            <span class="run-status err"><mat-icon>error</mat-icon> {{ error() }}</span>
          }
        </div>

        @if (crashingResults()) {
          <!-- ── Optimum summary ── -->
          <div class="section summary-row" aria-live="polite">
            <div class="stat-box accent">
              <div class="stat-label">Optimal Duration</div>
              <div class="stat-value">{{ crashingResults()!.optimal_duration }}</div>
              <div class="stat-unit">days</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Optimal Cost</div>
              <div class="stat-value">{{ crashingResults()!.optimal_cost | number: '1.0-0' }}</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Steps</div>
              <div class="stat-value">{{ crashingResults()!.steps.length }}</div>
            </div>
          </div>

          <!-- ── Cost-Time chart ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>show_chart</mat-icon>
              Cost–Time Tradeoff
            </div>
            <div
              class="chart-container"
              #chartContainer
              role="img"
              aria-label="Cost-Time tradeoff chart showing crashing steps"
            ></div>
          </div>

          <!-- ── Step table ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>table_chart</mat-icon>
              Crashing Steps
            </div>
            <div class="table-scroll">
              <table class="crash-table">
                <thead>
                  <tr>
                    <th>Step</th>
                    <th>Activity Crashed</th>
                    <th>Cost Slope</th>
                    <th>New Duration</th>
                    <th>Total Cost</th>
                    <th>Critical Path</th>
                  </tr>
                </thead>
                <tbody>
                  @for (step of crashingResults()!.steps; track step.step) {
                    <tr [class.optimal]="step.new_duration === crashingResults()!.optimal_duration">
                      <td class="mono">{{ step.step }}</td>
                      <td class="mono">{{ step.activity_crashed }}</td>
                      <td class="num">{{ step.cost_slope | number: '1.0-0' }}</td>
                      <td class="num">{{ step.new_duration }}</td>
                      <td class="num">{{ step.total_cost | number: '1.0-0' }}</td>
                      <td class="cp-cell">{{ step.critical_path.join(' → ') }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          </div>

          <!-- ── Learn mode ── -->
          @if (isLearnMode()) {
            <div class="section learn-section">
              <div class="section-title"><mat-icon>school</mat-icon> Crashing Concepts</div>
              <div class="learn-body">
                <div class="formula-step">
                  <div class="step-num">1</div>
                  <div>
                    <strong>Cost Slope:</strong><br />
                    <code
                      >Cost Slope = (Crash Cost − Normal Cost) / (Normal Duration − Crash
                      Duration)</code
                    ><br />
                    <span class="hint">Lower slope = cheaper to crash</span>
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">2</div>
                  <div>
                    <strong>Selection Rule:</strong><br />
                    At each step, crash the critical activity with the <em>lowest cost slope</em>.
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">3</div>
                  <div>
                    <strong>Optimum Point:</strong><br />
                    Stop when indirect cost savings &lt; direct cost increase, or all critical
                    activities are fully crashed.
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
      .crash-host {
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
        padding: 48px 24px;
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
      .rate-field {
        width: 180px;
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
        border-color: #1976d2;
        background: #e3f2fd;
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
        min-height: 260px;
        overflow-x: auto;
      }
      .table-scroll {
        overflow-x: auto;
      }
      .crash-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .crash-table th {
        background: #f5f5f5;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #e0e0e0;
        font-weight: 500;
        color: #546e7a;
      }
      .crash-table td {
        padding: 8px;
        border-bottom: 1px solid #eeeeee;
      }
      .crash-table tr.optimal {
        background: #e3f2fd;
      }
      .mono {
        font-family: monospace;
      }
      .num {
        text-align: right;
        font-variant-numeric: tabular-nums;
      }
      .cp-cell {
        font-size: 12px;
        color: #78909c;
      }
      .learn-section {
        background: #e3f2fd;
        border-color: #90caf9;
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
        background: #1976d2;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 600;
        flex-shrink: 0;
      }
      .hint {
        font-size: 12px;
        color: #78909c;
      }
      code {
        background: #f5f5f5;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 13px;
      }
    `,
  ],
})
export class CrashingComponent implements AfterViewInit, OnDestroy {
  private readonly crashingService = inject(CrashingService);
  private resizeObserver?: ResizeObserver;

  readonly chartContainer = viewChild<ElementRef<HTMLDivElement>>('chartContainer');

  readonly activities = activities;
  readonly cpmResults = cpmResults;
  readonly crashingResults = crashingResults;
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly running = signal(false);
  readonly error = signal<string | null>(null);
  indirectCostRate = 0;

  readonly hasData = computed(() => {
    const acts = activities();
    return (
      cpmResults() !== null && acts.some((a) => a.min_duration != null && a.crash_cost != null)
    );
  });

  ngAfterViewInit(): void {
    if (crashingResults()) this.drawChart();
    const el = this.chartContainer()?.nativeElement;
    if (el) {
      this.resizeObserver = new ResizeObserver(() => this.drawChart());
      this.resizeObserver.observe(el);
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
  }

  runCrashing(): void {
    const acts = activities();
    if (!acts.length) return;
    this.running.set(true);
    this.error.set(null);

    const req: CrashingRequest = {
      activities: acts,
      indirect_cost_rate: this.indirectCostRate > 0 ? this.indirectCostRate : undefined,
    };

    this.crashingService
      .analyze(req)
      .pipe(finalize(() => this.running.set(false)))
      .subscribe({
        next: (result) => {
          crashingResults.set(result);
          setTimeout(() => this.drawChart(), 0);
        },
        error: (err) => this.error.set(err?.message ?? 'Crashing analysis failed'),
      });
  }

  private drawChart(): void {
    const container = this.chartContainer()?.nativeElement;
    if (!container) return;
    const res = crashingResults();
    if (!res || res.steps.length === 0) return;

    d3.select(container).selectAll('*').remove();

    const steps = res.steps;
    const margin = { top: 20, right: 30, bottom: 40, left: 70 };
    const width = Math.max(400, container.clientWidth) - margin.left - margin.right;
    const height = 220 - margin.top - margin.bottom;

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const durations = steps.map((s) => s.new_duration);
    const costs = steps.map((s) => s.total_cost);

    const x = d3
      .scaleLinear()
      .domain([d3.min(durations)! - 1, d3.max(durations)! + 1])
      .range([0, width]);
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(costs)! * 1.1])
      .range([height, 0]);

    svg
      .append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(durations.length));
    svg.append('g').call(d3.axisLeft(y).ticks(6));

    // Cost line
    const line = d3
      .line<CrashingStep>()
      .x((d) => x(d.new_duration))
      .y((d) => y(d.total_cost))
      .curve(d3.curveMonotoneX);

    svg
      .append('path')
      .datum(steps)
      .attr('d', line)
      .attr('fill', 'none')
      .attr('stroke', '#1976d2')
      .attr('stroke-width', 2.5);

    // Points
    svg
      .selectAll('.point')
      .data(steps)
      .enter()
      .append('circle')
      .attr('cx', (d) => x(d.new_duration))
      .attr('cy', (d) => y(d.total_cost))
      .attr('r', (d) => (d.new_duration === res.optimal_duration ? 6 : 4))
      .attr('fill', (d) => (d.new_duration === res.optimal_duration ? '#c62828' : '#1976d2'));

    // Optimal marker
    const opt = steps.find((s) => s.new_duration === res.optimal_duration);
    if (opt) {
      svg
        .append('line')
        .attr('x1', x(opt.new_duration))
        .attr('x2', x(opt.new_duration))
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', '#c62828')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '4,3');
      svg
        .append('text')
        .attr('x', x(opt.new_duration) + 4)
        .attr('y', 12)
        .text('Optimal')
        .attr('font-size', '11px')
        .attr('fill', '#c62828');
    }

    // Axis labels
    svg
      .append('text')
      .attr('x', width / 2)
      .attr('y', height + 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Duration (days)');
    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -55)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Total Cost');
  }
}
