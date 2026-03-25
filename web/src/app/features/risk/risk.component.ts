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
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { finalize } from 'rxjs';
import * as d3 from 'd3';

import { RiskService } from '../../core/services/risk.service';
import { Risk, RiskResults } from '../../core/models/risk.model';
import { riskRegister, viewMode } from '../../core/store/project.store';

@Component({
  selector: 'app-risk',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
  template: `
    <div class="risk-host">
      @if (riskRegister().length === 0) {
        <div class="empty-state">
          <mat-icon>warning_amber</mat-icon>
          <p>No risks in the register. Add risks to your project first.</p>
        </div>
      } @else {
        <!-- ── Run bar ── -->
        <div class="run-bar">
          <span class="risk-count">{{ riskRegister().length }} risks loaded</span>
          <button mat-flat-button color="primary" (click)="runAnalysis()" [disabled]="running()">
            @if (running()) {
              <mat-spinner diameter="16" />
            } @else {
              <mat-icon>play_arrow</mat-icon>
            }
            Analyze Risks
          </button>
          @if (results()) {
            <span class="run-status ok"><mat-icon>check_circle</mat-icon> Analysis complete</span>
          }
          @if (error()) {
            <span class="run-status err"><mat-icon>error</mat-icon> {{ error() }}</span>
          }
        </div>

        @if (results()) {
          <!-- ── Summary ── -->
          <div class="section summary-row">
            <div class="stat-box accent">
              <div class="stat-label">Total Exposure (EMV)</div>
              <div class="stat-value">{{ results()!.total_exposure | number: '1.0-0' }}</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Contingency Reserve</div>
              <div class="stat-value">{{ results()!.contingency_reserve | number: '1.0-0' }}</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Risks Assessed</div>
              <div class="stat-value">{{ results()!.risks.length }}</div>
            </div>
          </div>

          <!-- ── Heat map ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>grid_on</mat-icon> Probability × Impact Heat Map
            </div>
            <div class="chart-container" #heatContainer></div>
          </div>

          <!-- ── Exposure bar chart ── -->
          <div class="section">
            <div class="section-title"><mat-icon>bar_chart</mat-icon> Risk Exposure (sorted)</div>
            <div class="chart-container" #barContainer></div>
          </div>

          <!-- ── Risk table ── -->
          <div class="section">
            <div class="section-title"><mat-icon>table_chart</mat-icon> Risk Register Detail</div>
            <div class="table-scroll">
              <table class="risk-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th class="num-col">Prob</th>
                    <th class="num-col">Impact</th>
                    <th class="num-col">EMV</th>
                  </tr>
                </thead>
                <tbody>
                  @for (r of sortedRisks(); track r.id) {
                    <tr>
                      <td class="mono">{{ r.id }}</td>
                      <td>{{ r.name }}</td>
                      <td>
                        <span class="cat-badge" [attr.data-cat]="r.category">{{ r.category }}</span>
                      </td>
                      <td class="num">{{ r.probability | number: '1.2-2' }}</td>
                      <td class="num">{{ r.impact | number: '1.0-0' }}</td>
                      <td class="num emv">{{ r.exposure | number: '1.0-0' }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          </div>

          <!-- ── Learn mode ── -->
          @if (isLearnMode()) {
            <div class="section learn-section">
              <div class="section-title"><mat-icon>school</mat-icon> Risk Analysis Concepts</div>
              <div class="learn-body">
                <div class="formula-step">
                  <div class="step-num">1</div>
                  <div>
                    <strong>Expected Monetary Value (EMV):</strong><br />
                    <code>EMV = Probability × Impact</code><br />
                    <span class="hint">Quantifies each risk's weighted cost</span>
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">2</div>
                  <div>
                    <strong>Total Exposure:</strong><br />
                    <code>Total = Σ EMV(risk_i)</code><br />
                    <span class="hint">Sum of all individual risk EMVs</span>
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">3</div>
                  <div>
                    <strong>Contingency Reserve:</strong><br />
                    A budget buffer to cover the total expected risk exposure.
                  </div>
                </div>
                <div class="formula-step">
                  <div class="step-num">4</div>
                  <div>
                    <strong>Heat Map:</strong><br />
                    A 5×5 grid crossing probability (Y) and impact (X). Green = low risk, Red = high
                    risk.
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
      .risk-host {
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
      .risk-count {
        font-size: 13px;
        color: #546e7a;
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
      .risk-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .risk-table th {
        background: #f5f5f5;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #e0e0e0;
        font-weight: 500;
        color: #546e7a;
      }
      .risk-table td {
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
      .emv {
        font-weight: 600;
        color: #e65100;
      }
      .cat-badge {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 10px;
        background: #eceff1;
        color: #546e7a;
      }
      .learn-section {
        background: #fff3e0;
        border-color: #ffcc80;
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
        background: #ff6f00;
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
export class RiskComponent implements AfterViewInit {
  private readonly riskService = inject(RiskService);

  readonly heatContainer = viewChild<ElementRef<HTMLDivElement>>('heatContainer');
  readonly barContainer = viewChild<ElementRef<HTMLDivElement>>('barContainer');

  readonly riskRegister = riskRegister;
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly running = signal(false);
  readonly error = signal<string | null>(null);
  readonly results = signal<RiskResults | null>(null);

  readonly sortedRisks = computed(() => {
    const res = this.results();
    if (!res) return [];
    return [...res.risks].sort((a, b) => b.exposure - a.exposure);
  });

  ngAfterViewInit(): void {
    if (this.results()) this.drawCharts();
  }

  runAnalysis(): void {
    const risks = riskRegister();
    if (!risks.length) return;
    this.running.set(true);
    this.error.set(null);

    this.riskService
      .analyze(risks)
      .pipe(finalize(() => this.running.set(false)))
      .subscribe({
        next: (res) => {
          this.results.set(res);
          setTimeout(() => this.drawCharts(), 0);
        },
        error: (err) => this.error.set(err?.message ?? 'Risk analysis failed'),
      });
  }

  private drawCharts(): void {
    this.drawHeatMap();
    this.drawBarChart();
  }

  /* ── 5×5 Heat Map ── */
  private drawHeatMap(): void {
    const container = this.heatContainer()?.nativeElement;
    if (!container) return;
    const res = this.results();
    if (!res) return;

    d3.select(container).selectAll('*').remove();

    const cellSize = 48;
    const labels = ['1', '2', '3', '4', '5'];
    const margin = { top: 10, right: 10, bottom: 40, left: 50 };
    const size = cellSize * 5;

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', size + margin.left + margin.right)
      .attr('height', size + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // risk level color: probability row × impact col (each 1-5)
    const color = (p: number, i: number): string => {
      const score = p * i;
      if (score >= 15) return '#c62828';
      if (score >= 10) return '#e65100';
      if (score >= 5) return '#f9a825';
      return '#2e7d32';
    };

    // Draw grid cells
    for (let row = 0; row < 5; row++) {
      for (let col = 0; col < 5; col++) {
        const prob = 5 - row; // top = 5
        const imp = col + 1;
        svg
          .append('rect')
          .attr('x', col * cellSize)
          .attr('y', row * cellSize)
          .attr('width', cellSize - 2)
          .attr('height', cellSize - 2)
          .attr('rx', 4)
          .attr('fill', color(prob, imp))
          .attr('opacity', 0.6);
        svg
          .append('text')
          .attr('x', col * cellSize + cellSize / 2)
          .attr('y', row * cellSize + cellSize / 2)
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'central')
          .attr('font-size', '11px')
          .attr('fill', '#fff')
          .text(prob * imp);
      }
    }

    // Plot risks as dots (scale probability & impact to 1-5 grid)
    res.risks.forEach((r) => {
      const pBin = Math.max(
        1,
        Math.min(5, Math.round(r.probability <= 1 ? r.probability * 5 : r.probability)),
      );
      const iBin = Math.max(1, Math.min(5, Math.round(r.impact <= 1 ? r.impact * 5 : r.impact)));
      const row = 5 - pBin;
      const col = iBin - 1;
      svg
        .append('circle')
        .attr('cx', col * cellSize + cellSize / 2)
        .attr('cy', row * cellSize + cellSize / 2)
        .attr('r', 8)
        .attr('fill', '#fff')
        .attr('stroke', '#263238')
        .attr('stroke-width', 2);
    });

    // Axis labels
    svg
      .append('text')
      .attr('x', size / 2)
      .attr('y', size + 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Impact →');
    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -size / 2)
      .attr('y', -35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#546e7a')
      .text('Probability →');

    labels.forEach((l, i) => {
      svg
        .append('text')
        .attr('x', i * cellSize + cellSize / 2)
        .attr('y', size + 14)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('fill', '#78909c')
        .text(l);
      svg
        .append('text')
        .attr('x', -8)
        .attr('y', (4 - i) * cellSize + cellSize / 2)
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '10px')
        .attr('fill', '#78909c')
        .text(l);
    });
  }

  /* ── Horizontal Exposure Bar Chart ── */
  private drawBarChart(): void {
    const container = this.barContainer()?.nativeElement;
    if (!container) return;
    const res = this.results();
    if (!res || !res.risks.length) return;

    d3.select(container).selectAll('*').remove();

    const sorted = [...res.risks].sort((a, b) => b.exposure - a.exposure);
    const margin = { top: 10, right: 20, bottom: 30, left: 120 };
    const barH = 22;
    const height = sorted.length * barH + margin.top + margin.bottom;
    const width = Math.max(300, container.clientWidth) - margin.left - margin.right;

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3
      .scaleLinear()
      .domain([0, d3.max(sorted, (d) => d.exposure)!])
      .range([0, width]);

    const y = d3
      .scaleBand<number>()
      .domain(sorted.map((_, i) => i))
      .range([0, sorted.length * barH])
      .padding(0.2);

    svg
      .selectAll('.bar')
      .data(sorted)
      .enter()
      .append('rect')
      .attr('x', 0)
      .attr('y', (_, i) => y(i)!)
      .attr('width', (d) => x(d.exposure))
      .attr('height', y.bandwidth())
      .attr('rx', 3)
      .attr('fill', '#ff6f00');

    svg
      .selectAll('.bar-label')
      .data(sorted)
      .enter()
      .append('text')
      .attr('x', (d) => x(d.exposure) + 4)
      .attr('y', (_, i) => y(i)! + y.bandwidth() / 2)
      .attr('dominant-baseline', 'central')
      .attr('font-size', '11px')
      .attr('fill', '#546e7a')
      .text((d) => d.exposure.toFixed(0));

    svg
      .selectAll('.name-label')
      .data(sorted)
      .enter()
      .append('text')
      .attr('x', -6)
      .attr('y', (_, i) => y(i)! + y.bandwidth() / 2)
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'central')
      .attr('font-size', '11px')
      .attr('fill', '#37474f')
      .text((d) => (d.name.length > 18 ? d.name.slice(0, 16) + '…' : d.name));

    svg
      .append('g')
      .attr('transform', `translate(0,${sorted.length * barH})`)
      .call(d3.axisBottom(x).ticks(5));
  }
}
