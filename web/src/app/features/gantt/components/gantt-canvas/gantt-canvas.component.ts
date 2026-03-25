import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  ViewChild,
  afterNextRender,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { cpmResults, selectedTaskId } from '../../../../core/store/project.store';
import { CPMNode } from '../../../../core/models/cpm-result.model';

// Layout constants
const ROW_H = 32; // height per task row
const HEADER_H = 36; // time axis header height
const LABEL_W = 140; // left panel width for task labels
const BAR_PADDING = 6; // vertical padding inside a row for bars
const BAR_H = ROW_H - BAR_PADDING * 2;
const MIN_UNIT_PX = 28; // minimum pixels per time unit
const ARROW_H_OFFSET = ROW_H / 2; // vertical centre of bar for arrows

@Component({
  selector: 'app-gantt-canvas',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatTooltipModule],
  template: `
    <div class="gantt-wrapper" #wrapper>
      @if (!hasData()) {
        <div class="empty-state">
          <mat-icon>calendar_view_week</mat-icon>
          <p>Run CPM analysis to see the Gantt chart</p>
        </div>
      } @else {
        <!-- Label column (fixed, non-scrolling) -->
        <div class="gantt-labels" [style.width.px]="LABEL_W">
          <div class="gantt-lbl-header">Activity</div>
          @for (node of nodes(); track node.id) {
            <div
              class="gantt-lbl-row"
              [class.selected]="selectedId() === node.id"
              [class.critical]="isCritical(node.id)"
              [style.height.px]="ROW_H"
              (click)="selectNode(node.id)"
            >
              {{ node.id }}
            </div>
          }
        </div>

        <!-- Scrollable chart area -->
        <div class="gantt-chart-area" #chartArea (scroll)="onScroll($event)">
          <svg #svgEl [style.width.px]="svgWidth()" [style.height.px]="svgHeight()">
            <!-- Time axis -->
            <g class="time-axis">
              <rect x="0" y="0" [attr.width]="svgWidth()" [attr.height]="HEADER_H" fill="#f5f7fa" />
              <line
                x1="0"
                [attr.y1]="HEADER_H"
                [attr.x2]="svgWidth()"
                [attr.y2]="HEADER_H"
                stroke="#cfd8dc"
                stroke-width="1"
              />
              @for (tick of timeTicks(); track tick.t) {
                <text [attr.x]="tick.x + 2" [attr.y]="HEADER_H - 6" font-size="10" fill="#546e7a">
                  {{ tick.label }}
                </text>
                <line
                  [attr.x1]="tick.x"
                  [attr.y1]="HEADER_H"
                  [attr.x2]="tick.x"
                  [attr.y2]="svgHeight()"
                  stroke="#eceff1"
                  stroke-width="1"
                  stroke-dasharray="4,3"
                />
              }
            </g>

            <!-- Bars -->
            <g class="bars">
              @for (node of nodes(); track node.id; let i = $index) {
                <!-- Row background (alternating) -->
                <rect
                  x="0"
                  [attr.y]="HEADER_H + i * ROW_H"
                  [attr.width]="svgWidth()"
                  [attr.height]="ROW_H"
                  [attr.fill]="i % 2 === 0 ? '#fafbfc' : '#ffffff'"
                />
                <!-- Float bar (EF → LF) -->
                @if (node.total_float > 0) {
                  <rect
                    [attr.x]="timeToX(node.EF)"
                    [attr.y]="HEADER_H + i * ROW_H + BAR_PADDING"
                    [attr.width]="timeToX(node.LF) - timeToX(node.EF)"
                    [attr.height]="BAR_H"
                    [attr.fill]="isCritical(node.id) ? '#ef9a9a' : '#90caf9'"
                    opacity="0.35"
                    rx="2"
                  />
                }
                <!-- Main activity bar (ES → EF) -->
                <rect
                  [attr.x]="timeToX(node.ES)"
                  [attr.y]="HEADER_H + i * ROW_H + BAR_PADDING"
                  [attr.width]="Math.max(timeToX(node.EF) - timeToX(node.ES), 2)"
                  [attr.height]="BAR_H"
                  [attr.fill]="barColor(node)"
                  [attr.stroke]="selectedId() === node.id ? '#ff6f00' : 'transparent'"
                  [attr.stroke-width]="selectedId() === node.id ? 2 : 0"
                  rx="2"
                  style="cursor:pointer"
                  (click)="selectNode(node.id)"
                >
                  <title>
                    {{ node.id }} | ES={{ node.ES }} EF={{ node.EF }} | Float={{ node.total_float }}
                  </title>
                </rect>
                <!-- Duration label inside bar -->
                @if (timeToX(node.EF) - timeToX(node.ES) > 28) {
                  <text
                    [attr.x]="timeToX(node.ES) + (timeToX(node.EF) - timeToX(node.ES)) / 2"
                    [attr.y]="HEADER_H + i * ROW_H + ROW_H / 2 + 3"
                    text-anchor="middle"
                    font-size="9"
                    fill="white"
                    style="pointer-events:none"
                  >
                    {{ node.duration }}
                  </text>
                }
              }
            </g>

            <!-- Dependency arrows -->
            <g class="arrows">
              @for (arrow of arrows(); track arrow.key) {
                <path
                  [attr.d]="arrow.d"
                  fill="none"
                  [attr.stroke]="arrow.critical ? '#c62828' : '#78909c'"
                  [attr.stroke-width]="arrow.critical ? 1.5 : 1"
                  stroke-dasharray="3,2"
                  marker-end="url(#gantt-arrow)"
                />
              }
            </g>

            <defs>
              <marker
                id="gantt-arrow"
                viewBox="0 0 8 8"
                refX="7"
                refY="4"
                markerWidth="4"
                markerHeight="4"
                orient="auto"
              >
                <path d="M 0 0 L 8 4 L 0 8 z" fill="#78909c" />
              </marker>
            </defs>
          </svg>
        </div>
      }
    </div>
  `,
  styleUrl: './gantt-canvas.component.scss',
})
export class GanttCanvasComponent {
  private readonly destroyRef = inject(DestroyRef);
  @ViewChild('wrapper') wrapper!: ElementRef<HTMLDivElement>;
  @ViewChild('chartArea') chartArea!: ElementRef<HTMLDivElement>;

  readonly LABEL_W = LABEL_W;
  readonly HEADER_H = HEADER_H;
  readonly ROW_H = ROW_H;
  readonly BAR_PADDING = BAR_PADDING;
  readonly BAR_H = BAR_H;
  readonly Math = Math;

  readonly hasData = computed(() => cpmResults() !== null);
  readonly nodes = computed(() => cpmResults()?.nodes ?? []);
  readonly edges = computed(() => cpmResults()?.edges ?? []);
  readonly criticalSet = computed(() => new Set(cpmResults()?.critical_activities ?? []));
  readonly selectedId = selectedTaskId;

  readonly projectDuration = computed(() => cpmResults()?.project_duration ?? 0);
  readonly unitPx = computed(() => {
    const pd = this.projectDuration();
    return pd > 0 ? Math.max(MIN_UNIT_PX, 800 / pd) : MIN_UNIT_PX;
  });
  readonly svgWidth = computed(() => Math.max(600, this.projectDuration() * this.unitPx() + 40));
  readonly svgHeight = computed(() => HEADER_H + this.nodes().length * ROW_H + 8);

  readonly timeTicks = computed(() => {
    const pd = this.projectDuration();
    const upx = this.unitPx();
    const ticks: Array<{ t: number; x: number; label: string }> = [];
    const step = tickStep(pd);
    for (let t = 0; t <= pd; t += step) {
      ticks.push({ t, x: t * upx, label: `${t}` });
    }
    return ticks;
  });

  readonly arrows = computed(() => {
    const ns = this.nodes();
    const es = this.edges();
    const crit = this.criticalSet();
    const rowMap = new Map<string, number>(ns.map((n, i) => [n.id, i]));
    const upx = this.unitPx();
    const result: Array<{ key: string; d: string; critical: boolean }> = [];

    for (const edge of es) {
      const fromNode = ns.find((n) => n.id === edge.from);
      const fi = rowMap.get(edge.from);
      const ti = rowMap.get(edge.to);
      if (fromNode === undefined || fi === undefined || ti === undefined) continue;

      const x1 = fromNode.EF * upx;
      const y1 = HEADER_H + fi * ROW_H + ARROW_H_OFFSET;
      const x2 = fromNode.EF * upx + 4; // arrive at EF column
      const toNode = ns.find((n) => n.id === edge.to);
      if (!toNode) continue;
      const x3 = toNode.ES * upx;
      const y3 = HEADER_H + ti * ROW_H + ARROW_H_OFFSET;

      const midX = (x1 + x3) / 2;
      const d = `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y3} L ${x3} ${y3}`;
      result.push({
        key: `${edge.from}-${edge.to}`,
        d,
        critical: crit.has(edge.from) && crit.has(edge.to),
      });
    }
    return result;
  });

  constructor() {
    effect(() => {
      // React to data changes — no DOM manipulation needed (template-driven)
      cpmResults();
    });
  }

  timeToX(t: number): number {
    return t * this.unitPx();
  }

  isCritical(id: string): boolean {
    return this.criticalSet().has(id);
  }

  barColor(node: CPMNode): string {
    if (this.criticalSet().has(node.id)) return '#e53935';
    return '#1e88e5';
  }

  selectNode(id: string): void {
    selectedTaskId.set(selectedTaskId() === id ? null : id);
  }

  onScroll(_event: Event): void {
    // Future: sync label scroll if needed
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function tickStep(duration: number): number {
  if (duration <= 10) return 1;
  if (duration <= 30) return 2;
  if (duration <= 60) return 5;
  if (duration <= 120) return 10;
  if (duration <= 300) return 20;
  return Math.ceil(duration / 15 / 5) * 5;
}
