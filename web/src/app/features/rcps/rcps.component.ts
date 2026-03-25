import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
  AfterViewInit,
  ElementRef,
  viewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { finalize } from 'rxjs';
import * as d3 from 'd3';

import { RcpsService } from '../../core/services/rcps.service';
import { RCPSResults } from '../../core/models/project.model';
import { activities, cpmResults, rcpsResults, viewMode } from '../../core/store/project.store';

@Component({
  selector: 'app-rcps',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
  template: `
    <div class="rcps-host">
      @if (!hasData()) {
        <div class="empty-state">
          <mat-icon>tune</mat-icon>
          <p>Run CPM first. Activities need resource requirements for leveling.</p>
        </div>
      } @else {
        <!-- ── Config + Run ── -->
        <div class="run-bar">
          <mat-form-field appearance="outline" class="small-field">
            <mat-label>Resource limit</mat-label>
            <input matInput type="number" [(ngModel)]="resourceLimit" [min]="1" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="small-field">
            <mat-label>Algorithm</mat-label>
            <mat-select [(ngModel)]="algorithm">
              <mat-option value="burgess">Burgess</mat-option>
              <mat-option value="min_moment">Min Moment</mat-option>
            </mat-select>
          </mat-form-field>

          <button mat-flat-button color="primary" (click)="runRcps()" [disabled]="running()">
            @if (running()) {
              <mat-spinner diameter="16" />
            } @else {
              <mat-icon>play_arrow</mat-icon>
            }
            Run RCPS
          </button>

          @if (rcpsResults()) {
            <span class="run-status ok"><mat-icon>check_circle</mat-icon> Leveling complete</span>
          }
          @if (error()) {
            <span class="run-status err"><mat-icon>error</mat-icon> {{ error() }}</span>
          }
        </div>

        @if (rcpsResults()) {
          <!-- ── Summary ── -->
          <div class="section summary-row">
            <div class="stat-box">
              <div class="stat-label">Original Duration</div>
              <div class="stat-value">{{ rcpsResults()!.original_duration }}</div>
              <div class="stat-unit">days</div>
            </div>
            <div
              class="stat-box"
              [class.accent]="rcpsResults()!.leveled_duration > rcpsResults()!.original_duration"
            >
              <div class="stat-label">Leveled Duration</div>
              <div class="stat-value">{{ rcpsResults()!.leveled_duration }}</div>
              <div class="stat-unit">days</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Duration Δ</div>
              <div class="stat-value">
                +{{ rcpsResults()!.leveled_duration - rcpsResults()!.original_duration }}
              </div>
              <div class="stat-unit">days</div>
            </div>
          </div>

          <!-- ── Resource histogram ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>equalizer</mat-icon>
              Resource Usage per Period
            </div>
            <div class="chart-container" #histContainer></div>
          </div>

          <!-- ── Schedule table ── -->
          <div class="section">
            <div class="section-title"><mat-icon>table_chart</mat-icon> Leveled Schedule</div>
            <div class="table-scroll">
              <table class="rcps-table">
                <thead>
                  <tr>
                    <th>Activity</th>
                    <th class="num-col">Start Period</th>
                  </tr>
                </thead>
                <tbody>
                  @for (entry of scheduleEntries(); track entry.id) {
                    <tr>
                      <td class="mono">{{ entry.id }}</td>
                      <td class="num">{{ entry.start }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          </div>

          <!-- ── Learn mode ── -->
          @if (isLearnMode()) {
            <div class="section learn-section">
              <div class="section-title"><mat-icon>school</mat-icon> RCPS Concepts</div>
              <div class="learn-body">
                <div class="formula-step">
                  <div class="step-num">1</div>
                  <div>
                    <strong>Resource-Constrained Project Scheduling (RCPS):</strong><br />
                    Re-schedules activities so that resource usage never exceeds the limit,
                    potentially extending the project.
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">2</div>
                  <div>
                    <strong>Burgess Algorithm:</strong><br />
                    Minimises the sum of squared resource usage across all periods, producing a
                    smoother resource profile.
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">3</div>
                  <div>
                    <strong>Min Moment:</strong><br />
                    Alternative heuristic that shifts non-critical activities within their float to
                    reduce peak demand.
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
      .rcps-host {
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
        border-color: #ff6f00;
        background: #fff3e0;
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
      .rcps-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .rcps-table th {
        background: #f5f5f5;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #e0e0e0;
        font-weight: 500;
        color: #546e7a;
      }
      .rcps-table td {
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
      }
      .learn-section {
        background: #e8f5e9;
        border-color: #a5d6a7;
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
        background: #2e7d32;
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
export class RcpsComponent implements AfterViewInit {
  private readonly rcpsService = inject(RcpsService);

  readonly histContainer = viewChild<ElementRef<HTMLDivElement>>('histContainer');

  readonly activities = activities;
  readonly cpmResults = cpmResults;
  readonly rcpsResults = rcpsResults;
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly running = signal(false);
  readonly error = signal<string | null>(null);

  resourceLimit = 5;
  algorithm: 'burgess' | 'min_moment' = 'burgess';

  readonly hasData = computed(() => cpmResults() !== null && activities().length > 0);

  readonly scheduleEntries = computed(() => {
    const res = rcpsResults();
    if (!res) return [];
    return Object.entries(res.schedule)
      .map(([id, start]) => ({ id, start }))
      .sort((a, b) => a.start - b.start);
  });

  ngAfterViewInit(): void {
    if (rcpsResults()) this.drawHistogram();
  }

  runRcps(): void {
    const acts = activities();
    if (!acts.length) return;
    this.running.set(true);
    this.error.set(null);

    this.rcpsService
      .analyze(acts, this.resourceLimit, this.algorithm)
      .pipe(finalize(() => this.running.set(false)))
      .subscribe({
        next: (result) => {
          rcpsResults.set(result);
          setTimeout(() => this.drawHistogram(), 0);
        },
        error: (err) => this.error.set(err?.message ?? 'RCPS analysis failed'),
      });
  }

  private drawHistogram(): void {
    const container = this.histContainer()?.nativeElement;
    if (!container) return;
    const res = rcpsResults();
    if (!res || !res.resource_usage.length) return;

    d3.select(container).selectAll('*').remove();

    const data = res.resource_usage;
    const margin = { top: 10, right: 10, bottom: 35, left: 45 };
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
      .scaleBand<number>()
      .domain(data.map((_, i) => i))
      .range([0, width])
      .padding(0.15);

    const y = d3
      .scaleLinear()
      .domain([0, Math.max(d3.max(data)! * 1.1, this.resourceLimit * 1.2)])
      .range([height, 0]);

    // Bars
    svg
      .selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', (_, i) => x(i)!)
      .attr('y', (d) => y(d))
      .attr('width', x.bandwidth())
      .attr('height', (d) => height - y(d))
      .attr('rx', 2)
      .attr('fill', (d) => (d > this.resourceLimit ? '#c62828' : '#1976d2'));

    // Resource limit line
    svg
      .append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', y(this.resourceLimit))
      .attr('y2', y(this.resourceLimit))
      .attr('stroke', '#c62828')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '6,3');
    svg
      .append('text')
      .attr('x', width - 4)
      .attr('y', y(this.resourceLimit) - 4)
      .attr('text-anchor', 'end')
      .attr('font-size', '10px')
      .attr('fill', '#c62828')
      .text(`Limit: ${this.resourceLimit}`);

    // Axes
    svg
      .append('g')
      .attr('transform', `translate(0,${height})`)
      .call(
        d3
          .axisBottom(x)
          .tickValues(
            data
              .map((_, i) => i)
              .filter((_, i) => i % Math.max(1, Math.floor(data.length / 10)) === 0),
          ),
      );
    svg.append('g').call(d3.axisLeft(y).ticks(5));

    // Labels
    svg
      .append('text')
      .attr('x', width / 2)
      .attr('y', height + 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Period');
    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Resources');
  }
}
