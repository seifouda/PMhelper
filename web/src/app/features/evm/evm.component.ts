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
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { finalize } from 'rxjs';
import * as d3 from 'd3';

import { KpiCardComponent } from '../../shared/components/kpi-card/kpi-card.component';
import { StepWalkthroughComponent } from '../../shared/components/step-walkthrough/step-walkthrough.component';
import { EvmService, EVMAnalysisRequest } from '../../core/services/evm.service';
import { evmProject, evmKpis, viewMode } from '../../core/store/project.store';
import { RAGStatus, EVMKPIs } from '../../core/models/evm.model';
import { CalculationStep } from '../../core/models/step.model';

@Component({
  selector: 'app-evm',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    MatOptionModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    KpiCardComponent,
    StepWalkthroughComponent,
  ],
  template: `
    <div class="evm-host">
      @if (!hasProject()) {
        <div class="empty-state">
          <mat-icon>trending_up</mat-icon>
          <p>
            Enter EVM period data (PV, EV, AC) in the
            <strong>Input / Data</strong> tab to use Earned Value Management.
          </p>
        </div>
      } @else {
        <!-- ── Period selector + Run ── -->
        <div class="run-bar">
          <mat-form-field appearance="outline" class="period-field">
            <mat-label>Analysis Period</mat-label>
            <mat-select [(value)]="selectedPeriod">
              @for (p of periods(); track p.index) {
                <mat-option [value]="p.index">{{ p.label }}</mat-option>
              }
            </mat-select>
          </mat-form-field>

          <button mat-flat-button color="primary" (click)="runEvm()" [disabled]="running()">
            @if (running()) {
              <mat-spinner diameter="16" />
            } @else {
              <mat-icon>play_arrow</mat-icon>
            }
            Run EVM
          </button>

          @if (evmKpis()) {
            <span class="run-status ok"><mat-icon>check_circle</mat-icon> Analysis complete</span>
          }
          @if (error()) {
            <span class="run-status err"><mat-icon>error</mat-icon> {{ error() }}</span>
          }
        </div>

        <!-- ── KPI Cards ── -->
        @if (evmKpis()) {
          <div class="kpi-row" aria-live="polite">
            <app-kpi-card
              label="EV"
              [value]="(kpi().ev | number: '1.0-0') ?? '—'"
              [unit]="currency()"
              icon="paid"
              tooltip="Earned Value — value of work completed"
              formula="EV = BAC × % Complete"
            />
            <app-kpi-card
              label="CV"
              [value]="(kpi().cv | number: '1.0-0') ?? '—'"
              [unit]="currency()"
              icon="account_balance"
              [rag]="cvRag()"
              tooltip="Cost Variance — negative = over budget"
              formula="CV = EV − AC"
            />
            <app-kpi-card
              label="SV"
              [value]="(kpi().sv | number: '1.0-0') ?? '—'"
              [unit]="currency()"
              icon="schedule"
              [rag]="svRag()"
              tooltip="Schedule Variance — negative = behind schedule"
              formula="SV = EV − PV"
            />
            <app-kpi-card
              label="CPI"
              [value]="(kpi().cpi | number: '1.2-2') ?? '—'"
              icon="speed"
              [rag]="cpiRag()"
              tooltip="Cost Performance Index — below 1 = over budget"
              formula="CPI = EV / AC"
            />
            <app-kpi-card
              label="SPI"
              [value]="(kpi().spi | number: '1.2-2') ?? '—'"
              icon="timer"
              [rag]="spiRag()"
              tooltip="Schedule Performance Index — below 1 = behind"
              formula="SPI = EV / PV"
            />
          </div>
          <div class="kpi-row">
            <app-kpi-card
              label="% Complete"
              [value]="(kpi().pc * 100 | number: '1.1-1') ?? '—'"
              unit="%"
              icon="pie_chart"
              tooltip="Physical % complete"
            />
            <app-kpi-card
              label="% Spent"
              [value]="(kpi().ps * 100 | number: '1.1-1') ?? '—'"
              unit="%"
              icon="payments"
              tooltip="Budget consumption"
            />
            <app-kpi-card
              label="CR"
              [value]="(kpi().cr | number: '1.2-2') ?? '—'"
              icon="security"
              [rag]="crRag()"
              tooltip="Critical Ratio = CPI × SPI"
              formula="CR = CPI × SPI"
            />
          </div>

          <!-- ── EAC variants ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>analytics</mat-icon>
              Estimate at Completion (EAC)
            </div>
            <div class="eac-grid">
              <div
                class="eac-card"
                [class.selected]="eacVariant === 1"
                (click)="eacVariant = 1"
                (keydown.enter)="eacVariant = 1"
                tabindex="0"
                role="button"
              >
                <div class="eac-label">EAC₁ (Typical)</div>
                <div class="eac-value">{{ kpi().eac1 | number: '1.0-0' }} {{ currency() }}</div>
                <div class="eac-formula">BAC / CPI</div>
              </div>
              <div
                class="eac-card"
                [class.selected]="eacVariant === 2"
                (click)="eacVariant = 2"
                (keydown.enter)="eacVariant = 2"
                tabindex="0"
                role="button"
              >
                <div class="eac-label">EAC₂ (Atypical)</div>
                <div class="eac-value">{{ kpi().eac2 | number: '1.0-0' }} {{ currency() }}</div>
                <div class="eac-formula">AC + (BAC − EV)</div>
              </div>
              <div
                class="eac-card"
                [class.selected]="eacVariant === 3"
                (click)="eacVariant = 3"
                (keydown.enter)="eacVariant = 3"
                tabindex="0"
                role="button"
              >
                <div class="eac-label">EAC₃ (Combined)</div>
                <div class="eac-value">{{ kpi().eac3 | number: '1.0-0' }} {{ currency() }}</div>
                <div class="eac-formula">AC + (BAC − EV) / (CPI × SPI)</div>
              </div>
            </div>
            <div class="vac-row">
              VAC = {{ kpi().vac | number: '1.0-0' }} {{ currency() }}
              <span class="vac-hint">(BAC − EAC₁; positive = under budget)</span>
            </div>
          </div>

          <!-- ── S-Curve ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>show_chart</mat-icon>
              S-Curve (PV / EV / AC)
            </div>
            <div
              class="chart-container"
              #scurveContainer
              role="img"
              aria-label="S-Curve chart showing Planned Value, Earned Value and Actual Cost over project periods"
            ></div>
          </div>

          <!-- ── TCPI ── -->
          <div class="section">
            <div class="section-title">
              <mat-icon>flag</mat-icon>
              To-Complete Performance Index
            </div>
            <div class="tcpi-row">
              <div class="tcpi-box">
                <div class="tcpi-label">TCPI (BAC)</div>
                <div
                  class="tcpi-value"
                  [class.red]="kpi().tcpi_bac > 1.1"
                  [class.amber]="kpi().tcpi_bac > 1.0 && kpi().tcpi_bac <= 1.1"
                  [class.green]="kpi().tcpi_bac <= 1.0"
                >
                  {{ kpi().tcpi_bac | number: '1.3-3' }}
                </div>
                <div class="tcpi-formula">(BAC − EV) / (BAC − AC)</div>
              </div>
            </div>
          </div>

          <!-- ── Learn mode ── -->
          @if (isLearnMode()) {
            @if (workedSteps().length) {
              <div class="section">
                <app-step-walkthrough title="EVM Worked Solution" [steps]="workedSteps()" />
              </div>
            }
            <div class="section learn-section">
              <div class="section-title"><mat-icon>school</mat-icon> EVM Formula Reference</div>
              <div class="formula-grid">
                <div class="formula-card">
                  <div class="fc-label">Cost Variance</div>
                  <div class="fc-formula">CV = EV − AC</div>
                </div>
                <div class="formula-card">
                  <div class="fc-label">Schedule Variance</div>
                  <div class="fc-formula">SV = EV − PV</div>
                </div>
                <div class="formula-card">
                  <div class="fc-label">CPI</div>
                  <div class="fc-formula">CPI = EV / AC</div>
                </div>
                <div class="formula-card">
                  <div class="fc-label">SPI</div>
                  <div class="fc-formula">SPI = EV / PV</div>
                </div>
                <div class="formula-card">
                  <div class="fc-label">EAC (Typical)</div>
                  <div class="fc-formula">EAC = BAC / CPI</div>
                </div>
                <div class="formula-card">
                  <div class="fc-label">TCPI</div>
                  <div class="fc-formula">TCPI = (BAC − EV) / (BAC − AC)</div>
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
      .evm-host {
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
      .period-field {
        width: 200px;
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
      .kpi-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
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
      .eac-grid {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
      .eac-card {
        flex: 1;
        min-width: 180px;
        padding: 12px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        cursor: pointer;
        transition: border-color 0.2s;
        text-align: center;
      }
      .eac-card:hover,
      .eac-card.selected {
        border-color: #1976d2;
      }
      .eac-label {
        font-size: 13px;
        color: #78909c;
        margin-bottom: 4px;
      }
      .eac-value {
        font-size: 20px;
        font-weight: 600;
        color: #263238;
      }
      .eac-formula {
        font-size: 12px;
        color: #90a4ae;
        margin-top: 4px;
        font-family: monospace;
      }
      .vac-row {
        margin-top: 8px;
        font-size: 14px;
        color: #546e7a;
      }
      .vac-hint {
        font-size: 12px;
        color: #90a4ae;
      }
      .chart-container {
        width: 100%;
        min-height: 280px;
        overflow-x: auto;
      }
      .tcpi-row {
        display: flex;
        gap: 16px;
      }
      .tcpi-box {
        text-align: center;
        padding: 12px 24px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
      }
      .tcpi-label {
        font-size: 13px;
        color: #78909c;
      }
      .tcpi-value {
        font-size: 28px;
        font-weight: 700;
      }
      .tcpi-value.red {
        color: #c62828;
      }
      .tcpi-value.amber {
        color: #f57f17;
      }
      .tcpi-value.green {
        color: #2e7d32;
      }
      .tcpi-formula {
        font-size: 12px;
        color: #90a4ae;
        font-family: monospace;
        margin-top: 4px;
      }
      .learn-section {
        background: #e3f2fd;
        border-color: #90caf9;
      }
      .formula-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }
      .formula-card {
        flex: 1 1 140px;
        padding: 10px;
        border-radius: 6px;
        background: #fff;
        border: 1px solid #bbdefb;
      }
      .fc-label {
        font-size: 12px;
        color: #1565c0;
        font-weight: 500;
      }
      .fc-formula {
        font-family: monospace;
        font-size: 13px;
        color: #263238;
        margin-top: 4px;
      }
    `,
  ],
})
export class EvmComponent implements AfterViewInit, OnDestroy {
  private readonly evmService = inject(EvmService);
  private resizeObserver?: ResizeObserver;

  readonly scurveContainer = viewChild<ElementRef<HTMLDivElement>>('scurveContainer');

  readonly evmProject = evmProject;
  readonly evmKpis = evmKpis;
  readonly isLearnMode = computed(() => viewMode() === 'learn');

  readonly running = signal(false);
  readonly error = signal<string | null>(null);
  readonly workedSteps = signal<CalculationStep[]>([]);
  eacVariant = 1;
  selectedPeriod = -1;

  readonly hasProject = computed(
    () => evmProject() !== null && (evmProject()?.periods?.length ?? 0) > 0,
  );
  readonly periods = computed(() => evmProject()?.periods ?? []);
  readonly currency = computed(() => evmProject()?.currency_symbol ?? '$');

  readonly kpi = computed(
    () =>
      evmKpis() ??
      ({
        ev: 0,
        cv: 0,
        sv: 0,
        cpi: 0,
        spi: 0,
        pc: 0,
        ps: 0,
        cr: 0,
        eac1: 0,
        eac2: 0,
        eac3: 0,
        vac: 0,
        tcpi_bac: 0,
      } as EVMKPIs),
  );

  readonly cpiRag = computed(
    (): RAGStatus => (this.kpi().cpi >= 1.0 ? 'green' : this.kpi().cpi >= 0.9 ? 'amber' : 'red'),
  );
  readonly spiRag = computed(
    (): RAGStatus => (this.kpi().spi >= 1.0 ? 'green' : this.kpi().spi >= 0.9 ? 'amber' : 'red'),
  );
  readonly cvRag = computed(
    (): RAGStatus =>
      this.kpi().cv >= 0 ? 'green' : this.kpi().cv >= -this.bac() * 0.1 ? 'amber' : 'red',
  );
  readonly svRag = computed(
    (): RAGStatus =>
      this.kpi().sv >= 0 ? 'green' : this.kpi().sv >= -this.bac() * 0.1 ? 'amber' : 'red',
  );
  readonly crRag = computed(
    (): RAGStatus => (this.kpi().cr >= 1.0 ? 'green' : this.kpi().cr >= 0.8 ? 'amber' : 'red'),
  );

  private readonly bac = computed(() => evmProject()?.bac ?? 1);

  ngAfterViewInit(): void {
    const p = this.periods();
    if (p.length > 0 && this.selectedPeriod < 0) {
      this.selectedPeriod = p.length - 1;
    }
    // Observe chart container for resize
    const el = this.scurveContainer()?.nativeElement;
    if (el) {
      this.resizeObserver = new ResizeObserver(() => this.drawScurve());
      this.resizeObserver.observe(el);
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
  }

  runEvm(): void {
    const proj = evmProject();
    if (!proj) return;
    this.running.set(true);
    this.error.set(null);

    const req: EVMAnalysisRequest = {
      project: proj,
      current_period_index: this.selectedPeriod >= 0 ? this.selectedPeriod : undefined,
    };

    this.evmService
      .analyze(req)
      .pipe(finalize(() => this.running.set(false)))
      .subscribe({
        next: (res) => {
          evmKpis.set(res.kpis);
          this.drawScurve();
          // Fetch worked-solution steps for learn mode
          this.evmService.getSteps(req).subscribe({
            next: (steps) => this.workedSteps.set(steps),
            error: () => this.workedSteps.set([]),
          });
        },
        error: (err) => this.error.set(err?.message ?? 'EVM analysis failed'),
      });
  }

  private drawScurve(): void {
    const container = this.scurveContainer()?.nativeElement;
    if (!container) return;
    const proj = evmProject();
    if (!proj) return;

    d3.select(container).selectAll('*').remove();

    const periods = proj.periods;
    if (periods.length === 0) return;

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = Math.max(400, container.clientWidth) - margin.left - margin.right;
    const height = 240 - margin.top - margin.bottom;

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3
      .scaleLinear()
      .domain([0, periods.length - 1])
      .range([0, width]);
    const maxVal =
      d3.max(periods, (p) => Math.max(p.pv_cumulative, p.ev_cumulative, p.ac_cumulative)) ?? 1;
    const y = d3
      .scaleLinear()
      .domain([0, maxVal * 1.1])
      .range([height, 0]);

    svg
      .append('g')
      .attr('transform', `translate(0,${height})`)
      .call(
        d3
          .axisBottom(x)
          .ticks(periods.length)
          .tickFormat((d) => {
            const idx = d as number;
            return periods[idx]?.label ?? `P${idx}`;
          }),
      );
    svg.append('g').call(d3.axisLeft(y).ticks(6));

    const line = (accessor: (p: any) => number) =>
      d3
        .line<any>()
        .x((_d, i) => x(i))
        .y((d) => y(accessor(d)))
        .curve(d3.curveMonotoneX);

    svg
      .append('path')
      .datum(periods)
      .attr(
        'd',
        line((p) => p.pv_cumulative),
      )
      .attr('fill', 'none')
      .attr('stroke', '#1976d2')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '6,3');

    svg
      .append('path')
      .datum(periods)
      .attr(
        'd',
        line((p) => p.ev_cumulative),
      )
      .attr('fill', 'none')
      .attr('stroke', '#2e7d32')
      .attr('stroke-width', 2.5);

    svg
      .append('path')
      .datum(periods)
      .attr(
        'd',
        line((p) => p.ac_cumulative),
      )
      .attr('fill', 'none')
      .attr('stroke', '#c62828')
      .attr('stroke-width', 2);

    const legend = svg.append('g').attr('transform', `translate(${width - 140}, 0)`);
    [
      { label: 'PV (Planned)', color: '#1976d2', dash: '6,3' },
      { label: 'EV (Earned)', color: '#2e7d32', dash: '' },
      { label: 'AC (Actual)', color: '#c62828', dash: '' },
    ].forEach((item, i) => {
      const g = legend.append('g').attr('transform', `translate(0, ${i * 18})`);
      g.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 6)
        .attr('y2', 6)
        .attr('stroke', item.color)
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', item.dash);
      g.append('text')
        .attr('x', 26)
        .attr('y', 10)
        .text(item.label)
        .attr('font-size', '11px')
        .attr('fill', '#546e7a');
    });

    const bac = proj.bac;
    if (bac > 0) {
      svg
        .append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', y(bac))
        .attr('y2', y(bac))
        .attr('stroke', '#78909c')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '3,3');
      svg
        .append('text')
        .attr('x', width - 40)
        .attr('y', y(bac) - 4)
        .text(`BAC=${bac}`)
        .attr('font-size', '10px')
        .attr('fill', '#78909c');
    }
  }
}
