import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  ViewChild,
  afterNextRender,
  effect,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import * as d3 from 'd3';

import { cpmResults, selectedTaskId } from '../../../../core/store/project.store';
import { CPMNode, CPMEdge } from '../../../../core/models/cpm-result.model';
import { sugiyamaLayout, LayoutResult } from '../../utils/sugiyama-layout';

// Node box dimensions (SVG pixels)
const NODE_W = 124;
const NODE_H = 92;
const H1 = 22; // ES/EF row height
const H2 = 26; // ID + Duration row height
const H3 = 22; // LS/LF row height
const H4 = 22; // Float row height

@Component({
  selector: 'app-network-canvas',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatTooltipModule],
  template: `
    <div class="network-canvas-wrapper">
      <svg
        #svgEl
        class="network-svg"
        role="img"
        aria-label="Network diagram showing project activities, dependencies and critical path"
      >
        <defs>
          <marker
            id="arr-normal"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#607d8b" />
          </marker>
          <marker
            id="arr-critical"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c62828" />
          </marker>
        </defs>
      </svg>

      @if (!hasData()) {
        <div class="empty-state">
          <mat-icon class="empty-icon">account_tree</mat-icon>
          <p class="empty-title">No network data</p>
          <p class="empty-hint">Enter activities in the Input view and click Analyze</p>
        </div>
      }

      <div class="network-toolbar">
        <button mat-icon-button (click)="fitToView()" matTooltip="Fit to view">
          <mat-icon>fit_screen</mat-icon>
        </button>
        <button mat-icon-button (click)="resetZoom()" matTooltip="Reset zoom">
          <mat-icon>center_focus_strong</mat-icon>
        </button>
        @if (hasData()) {
          <span class="legend-item critical"> <span class="legend-swatch"></span> Critical </span>
          <span class="legend-item normal"> <span class="legend-swatch"></span> Normal </span>
        }
      </div>
    </div>
  `,
  styleUrl: './network-canvas.component.scss',
})
export class NetworkCanvasComponent {
  private readonly destroyRef = inject(DestroyRef);
  @ViewChild('svgEl') svgEl!: ElementRef<SVGElement>;

  readonly hasData = signal(false);

  private svgSel?: d3.Selection<SVGElement, unknown, null, undefined>;
  private zoomGroup?: d3.Selection<SVGGElement, unknown, null, undefined>;
  private zoomBehavior?: d3.ZoomBehavior<SVGElement, unknown>;
  private layout?: LayoutResult;
  private d3Ready = false;

  constructor() {
    // React to CPM results changes
    effect(() => {
      const results = cpmResults();
      this.hasData.set(results !== null);
      if (results && this.d3Ready) {
        this.renderNetwork(results.nodes, results.edges, results.critical_activities);
      }
    });

    // React to selected task changes (cross-view highlighting)
    effect(() => {
      const selected = selectedTaskId();
      if (this.d3Ready) {
        this.applySelection(selected);
      }
    });

    // Initialize D3 after the first render (SVG is in DOM)
    afterNextRender(() => {
      this.initD3();
      const results = cpmResults();
      if (results) {
        this.renderNetwork(results.nodes, results.edges, results.critical_activities);
      }
    });
  }

  private initD3(): void {
    const el = this.svgEl.nativeElement;
    this.svgSel = d3.select(el);
    this.zoomGroup = this.svgSel.append<SVGGElement>('g').attr('class', 'zoom-g');

    this.zoomBehavior = d3
      .zoom<SVGElement, unknown>()
      .scaleExtent([0.04, 4])
      .on('zoom', (event: d3.D3ZoomEvent<SVGElement, unknown>) => {
        this.zoomGroup!.attr('transform', event.transform.toString());
      });

    this.svgSel.call(this.zoomBehavior);
    this.d3Ready = true;
  }

  private renderNetwork(nodes: CPMNode[], edges: CPMEdge[], criticalActivities: string[]): void {
    if (!this.zoomGroup || !this.svgSel) return;

    const criticalSet = new Set(criticalActivities);
    this.layout = sugiyamaLayout(nodes, edges, criticalActivities, 200, 120);
    const { nodePositions, edgePaths } = this.layout;

    // Clear previous render
    this.zoomGroup.selectAll('*').remove();

    // ── Draw edges ──────────────────────────────────────────────────────────
    const edgesG = this.zoomGroup.append('g').attr('class', 'edges-g');

    for (const ep of edgePaths) {
      if (ep.waypoints.length < 2) continue;
      const wps = ep.waypoints;
      const color = ep.isCritical ? '#c62828' : '#607d8b';
      const sw = ep.isCritical ? 2 : 1.5;

      // Offset start/end away from node centers to node borders
      const startPt = offsetPt(wps[0], wps[1], NODE_W / 2 + 3);
      const endPt = offsetPt(wps[wps.length - 1], wps[wps.length - 2], NODE_W / 2 + 3);

      const pathPoints = [startPt, ...wps.slice(1, -1), endPt];
      const lineGen = d3
        .line<{ x: number; y: number }>()
        .x((d) => d.x)
        .y((d) => d.y);

      edgesG
        .append('path')
        .attr('class', `edge edge-${ep.originalFrom}-${ep.originalTo}`)
        .attr('d', lineGen(pathPoints) ?? '')
        .attr('stroke', color)
        .attr('stroke-width', sw)
        .attr('fill', 'none')
        .attr('marker-end', ep.isCritical ? 'url(#arr-critical)' : 'url(#arr-normal)');
    }

    // ── Draw nodes ──────────────────────────────────────────────────────────
    const nodesG = this.zoomGroup.append('g').attr('class', 'nodes-g');

    for (const node of nodes) {
      const p = nodePositions.get(node.id);
      if (!p) continue;

      const crit = criticalSet.has(node.id);
      const bg = crit ? '#ffebee' : '#e3f2fd';
      const border = crit ? '#c62828' : '#1565c0';
      const divider = crit ? '#ef9a9a' : '#90caf9';
      const textCol = crit ? '#b71c1c' : '#0d47a1';
      const dimCol = crit ? '#ef9a9a' : '#90caf9';

      const gNode = nodesG
        .append('g')
        .attr('class', `node node-${node.id}${crit ? ' node-critical' : ''}`)
        .attr('transform', `translate(${p.x - NODE_W / 2},${p.y - NODE_H / 2})`)
        .style('cursor', 'pointer')
        .on('click', () => {
          selectedTaskId.set(selectedTaskId() === node.id ? null : node.id);
        })
        .on('mouseenter', () => this.onHover(node.id))
        .on('mouseleave', () => this.onHoverEnd());

      // Background rect
      gNode
        .append('rect')
        .attr('width', NODE_W)
        .attr('height', NODE_H)
        .attr('rx', 4)
        .attr('fill', bg)
        .attr('stroke', border)
        .attr('stroke-width', crit ? 2 : 1);

      // Horizontal dividers
      for (const y of [H1, H1 + H2, H1 + H2 + H3]) {
        gNode
          .append('line')
          .attr('x1', 0)
          .attr('y1', y)
          .attr('x2', NODE_W)
          .attr('y2', y)
          .attr('stroke', divider)
          .attr('stroke-width', 0.5);
      }
      // Vertical dividers (ES|EF and LS|LF sections)
      gNode
        .append('line')
        .attr('x1', NODE_W / 2)
        .attr('y1', 0)
        .attr('x2', NODE_W / 2)
        .attr('y2', H1)
        .attr('stroke', divider)
        .attr('stroke-width', 0.5);
      gNode
        .append('line')
        .attr('x1', NODE_W / 2)
        .attr('y1', H1 + H2)
        .attr('x2', NODE_W / 2)
        .attr('y2', H1 + H2 + H3)
        .attr('stroke', divider)
        .attr('stroke-width', 0.5);

      const q = NODE_W / 4; // quarter width for centering in each cell
      const y1 = H1;
      const y2 = H1 + H2;
      const y3 = H1 + H2 + H3;

      // Row 0 — ES / EF
      addLabel(gNode, 'ES', 4, 9, dimCol);
      addValue(gNode, fmt(node.ES), q, 15, textCol);
      addLabel(gNode, 'EF', NODE_W / 2 + 4, 9, dimCol);
      addValue(gNode, fmt(node.EF), NODE_W / 2 + q, 15, textCol);

      // Row 1 — Activity ID + Duration
      const label = node.id.length > 12 ? node.id.slice(0, 11) + '…' : node.id;
      gNode
        .append('text')
        .text(label)
        .attr('x', NODE_W / 2)
        .attr('y', y1 + 11)
        .attr('text-anchor', 'middle')
        .attr('font-size', 9)
        .attr('fill', textCol)
        .attr('font-weight', 'bold');
      gNode
        .append('text')
        .text(`dur = ${fmt(node.duration)}`)
        .attr('x', NODE_W / 2)
        .attr('y', y1 + 22)
        .attr('text-anchor', 'middle')
        .attr('font-size', 8)
        .attr('fill', textCol);

      // Row 2 — LS / LF
      addLabel(gNode, 'LS', 4, y2 + 9, dimCol);
      addValue(gNode, fmt(node.LS), q, y2 + 15, textCol);
      addLabel(gNode, 'LF', NODE_W / 2 + 4, y2 + 9, dimCol);
      addValue(gNode, fmt(node.LF), NODE_W / 2 + q, y2 + 15, textCol);

      // Row 3 — Float
      const floatZero = node.total_float === 0;
      if (floatZero) {
        gNode
          .append('rect')
          .attr('x', 0)
          .attr('y', y3)
          .attr('width', NODE_W)
          .attr('height', H4)
          .attr('rx', 0)
          .attr('fill', '#ffcdd2');
      }
      addLabel(gNode, 'Float', 4, y3 + 9, floatZero ? '#c62828' : dimCol);
      addValue(
        gNode,
        fmt(node.total_float),
        NODE_W / 2 + q,
        y3 + 15,
        floatZero ? '#c62828' : textCol,
      );
    }

    this.fitToView();
  }

  private applySelection(selected: string | null): void {
    if (!this.zoomGroup) return;
    this.zoomGroup.selectAll<SVGGElement, unknown>('.node').style('opacity', function () {
      if (selected === null) return 1;
      return (this.getAttribute('class') ?? '').includes(`node-${selected}`) ? 1 : 0.3;
    });
  }

  private onHover(nodeId: string): void {
    if (!this.layout || !this.zoomGroup) return;

    const connected = new Set([nodeId]);
    for (const ep of this.layout.edgePaths) {
      if (ep.originalFrom === nodeId) connected.add(ep.originalTo);
      if (ep.originalTo === nodeId) connected.add(ep.originalFrom);
    }

    this.zoomGroup.selectAll<SVGGElement, unknown>('.node').style('opacity', function () {
      const cls = this.getAttribute('class') ?? '';
      for (const id of connected) {
        if (cls.includes(`node-${id}`)) return 1;
      }
      return 0.2;
    });

    this.zoomGroup.selectAll<SVGPathElement, unknown>('.edge').style('opacity', function () {
      const cls = this.getAttribute('class') ?? '';
      return cls.includes(`-${nodeId}-`) || cls.endsWith(`-${nodeId}`) ? 1 : 0.1;
    });
  }

  private onHoverEnd(): void {
    if (!this.zoomGroup) return;
    this.zoomGroup.selectAll('.node').style('opacity', 1);
    this.zoomGroup.selectAll('.edge').style('opacity', 1);
  }

  fitToView(): void {
    if (!this.svgSel || !this.zoomBehavior || !this.layout) return;
    const el = this.svgSel.node();
    if (!el) return;
    const { clientWidth: w, clientHeight: h } = el;
    if (w === 0 || h === 0) return;

    const { minX, maxX, minY, maxY } = this.layout.bounds;
    const gw = maxX - minX + NODE_W;
    const gh = maxY - minY + NODE_H;
    const pad = 40;
    const scaleX = (w - 2 * pad) / gw;
    const scaleY = (h - 2 * pad) / gh;
    const scale = Math.min(scaleX, scaleY, 1.5);
    const tx = (w - gw * scale) / 2 - (minX - NODE_W / 2) * scale;
    const ty = (h - gh * scale) / 2 - (minY - NODE_H / 2) * scale;

    this.svgSel
      .transition()
      .duration(400)
      .call(this.zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
  }

  resetZoom(): void {
    this.svgSel?.transition().duration(300).call(this.zoomBehavior!.transform, d3.zoomIdentity);
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

function offsetPt(
  from: { x: number; y: number },
  towards: { x: number; y: number },
  radius: number,
): { x: number; y: number } {
  const dx = towards.x - from.x;
  const dy = towards.y - from.y;
  const d = Math.sqrt(dx * dx + dy * dy);
  if (d === 0) return from;
  return { x: from.x + (radius * dx) / d, y: from.y + (radius * dy) / d };
}

function addLabel(
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  text: string,
  x: number,
  y: number,
  fill: string,
): void {
  g.append('text')
    .text(text)
    .attr('x', x)
    .attr('y', y)
    .attr('font-size', 7)
    .attr('fill', fill)
    .attr('font-weight', 'bold');
}

function addValue(
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  text: string,
  x: number,
  y: number,
  fill: string,
): void {
  g.append('text')
    .text(text)
    .attr('x', x)
    .attr('y', y)
    .attr('text-anchor', 'middle')
    .attr('font-size', 10)
    .attr('fill', fill)
    .attr('font-weight', 'bold');
}
