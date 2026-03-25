import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
  AfterViewInit,
  ElementRef,
  viewChild,
  OnDestroy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import * as d3 from 'd3';

import { WBSNode } from '../../core/models/project.model';
import { wbsNodes, viewMode } from '../../core/store/project.store';
import { WbsEditDialogComponent } from './wbs-edit-dialog.component';

/* ── internal layout types ── */
interface LayoutNode {
  id: string;
  code: string;
  name: string;
  cost: number;
  duration: number;
  progress: number;
  x: number;
  y: number;
  w: number;
  h: number;
  children: LayoutNode[];
  parent?: LayoutNode;
  collapsed: boolean;
}

const NODE_W = 160;
const NODE_H = 72;
const H_GAP = 24;
const V_GAP = 48;

@Component({
  selector: 'app-wbs',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatTooltipModule,
    MatDialogModule,
  ],
  template: `
    <div class="wbs-host">
      <!-- ── Toolbar ── -->
      <div class="toolbar">
        <button mat-flat-button color="primary" (click)="addRoot()" [disabled]="hasRoot()">
          <mat-icon>add</mat-icon> Add Root
        </button>
        <button
          mat-stroked-button
          (click)="undo()"
          [disabled]="!canUndo()"
          matTooltip="Undo (Ctrl+Z)"
        >
          <mat-icon>undo</mat-icon>
        </button>
        <button mat-stroked-button (click)="expandAll()">
          <mat-icon>unfold_more</mat-icon> Expand All
        </button>
        <button mat-stroked-button (click)="collapseAll()">
          <mat-icon>unfold_less</mat-icon> Collapse All
        </button>
        <button mat-stroked-button (click)="exportJSON()" [disabled]="!hasRoot()">
          <mat-icon>download</mat-icon> Export JSON
        </button>

        @if (hasRoot()) {
          <div class="rollup-stats">
            <span class="stat"
              >Cost: <strong>{{ totalCost() | number: '1.0-0' }}</strong></span
            >
            <span class="stat"
              >Duration: <strong>{{ totalDuration() }}</strong> days</span
            >
            <span class="stat"
              >Progress: <strong>{{ totalProgress() | number: '1.0-0' }}%</strong></span
            >
          </div>
        }
      </div>

      @if (!hasRoot()) {
        <div class="empty-state">
          <mat-icon>account_tree</mat-icon>
          <p>Click <strong>Add Root</strong> to start your Work Breakdown Structure.</p>
        </div>
      } @else {
        <div class="canvas-wrapper" #canvasWrapper (contextmenu)="$event.preventDefault()">
          <svg #svgEl></svg>
        </div>
      }

      <!-- ── Context menu (attached to right-click) ── -->
      <div
        class="ctx-menu"
        [class.visible]="ctxVisible()"
        [style.left.px]="ctxX()"
        [style.top.px]="ctxY()"
      >
        <button (click)="ctxAddChild()"><mat-icon>add</mat-icon> Add Child</button>
        <button (click)="ctxEdit()"><mat-icon>edit</mat-icon> Edit</button>
        <button (click)="ctxToggle()">
          <mat-icon>{{ ctxNode()?.collapsed ? 'unfold_more' : 'unfold_less' }}</mat-icon>
          {{ ctxNode()?.collapsed ? 'Expand' : 'Collapse' }}
        </button>
        <button (click)="ctxDelete()" class="danger">
          <mat-icon>delete</mat-icon> Delete Subtree
        </button>
      </div>

      <!-- ── Learn mode ── -->
      @if (isLearnMode() && hasRoot()) {
        <div class="section learn-section">
          <div class="section-title"><mat-icon>school</mat-icon> WBS Concepts</div>
          <div class="learn-body">
            <div class="formula-step">
              <div class="step-num">1</div>
              <div>
                <strong>100% Rule:</strong> The work in child elements must add up to 100% of the
                parent's scope.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">2</div>
              <div>
                <strong>Decomposition:</strong> Break work down until packages are small enough to
                estimate and assign.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">3</div>
              <div>
                <strong>Work Packages:</strong> Leaf nodes are the deliverable work packages — the
                lowest estimable unit.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">4</div>
              <div>
                <strong>Cost Rollup:</strong> Parent cost = Σ child costs. Duration = max(children).
                Progress = weighted avg by cost.
              </div>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .wbs-host {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 16px;
        height: 100%;
        overflow: hidden;
      }
      .toolbar {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
      }
      .rollup-stats {
        margin-left: auto;
        display: flex;
        gap: 16px;
        font-size: 13px;
        color: #546e7a;
      }
      .rollup-stats .stat strong {
        color: #263238;
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
      .canvas-wrapper {
        flex: 1;
        overflow: auto;
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        position: relative;
      }
      .canvas-wrapper svg {
        display: block;
      }
      .ctx-menu {
        position: fixed;
        z-index: 1000;
        background: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: none;
        min-width: 160px;
      }
      .ctx-menu.visible {
        display: block;
      }
      .ctx-menu button {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        padding: 8px 14px;
        border: none;
        background: none;
        cursor: pointer;
        font-size: 13px;
        color: #37474f;
      }
      .ctx-menu button:hover {
        background: #f5f5f5;
      }
      .ctx-menu button.danger {
        color: #c62828;
      }
      .section {
        background: #fff;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e0e0e0;
      }
      .learn-section {
        background: #e8f5e9;
        border-color: #a5d6a7;
        flex-shrink: 0;
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
export class WbsComponent implements AfterViewInit, OnDestroy {
  private readonly dialogService = inject(MatDialog);

  readonly svgEl = viewChild<ElementRef<SVGSVGElement>>('svgEl');
  readonly canvasWrapper = viewChild<ElementRef<HTMLDivElement>>('canvasWrapper');

  readonly isLearnMode = computed(() => viewMode() === 'learn');
  readonly hasRoot = computed(() => wbsNodes().length > 0);

  /* ── context menu state ── */
  readonly ctxVisible = signal(false);
  readonly ctxX = signal(0);
  readonly ctxY = signal(0);
  readonly ctxNode = signal<LayoutNode | null>(null);

  /* ── undo stack (snapshots of flat WBSNode[]) ── */
  private undoStack: WBSNode[][] = [];
  readonly canUndo = signal(false);

  /* ── collapsed set (node IDs) ── */
  private collapsedIds = new Set<string>();

  /* ── layout tree cache ── */
  private rootLayout: LayoutNode | null = null;

  /* ── rollup signals ── */
  readonly totalCost = computed(() => this.computeRollupCost(wbsNodes()));
  readonly totalDuration = computed(() => this.computeRollupDuration(wbsNodes()));
  readonly totalProgress = computed(() => this.computeRollupProgress(wbsNodes()));

  private clickListener = (e: MouseEvent) => {
    if (this.ctxVisible()) this.ctxVisible.set(false);
  };

  ngAfterViewInit(): void {
    document.addEventListener('click', this.clickListener);
    document.addEventListener('keydown', this.keyListener);
    if (this.hasRoot()) setTimeout(() => this.render(), 0);
  }

  ngOnDestroy(): void {
    document.removeEventListener('click', this.clickListener);
    document.removeEventListener('keydown', this.keyListener);
  }

  private keyListener = (e: KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'z') {
      e.preventDefault();
      this.undo();
    }
  };

  /* ── Actions ── */
  addRoot(): void {
    this.pushUndo();
    const root: WBSNode = {
      id: this.uid(),
      code: '1',
      name: 'Project',
      cost: 0,
      duration: 0,
      progress: 0,
      children: [],
    };
    wbsNodes.set([root]);
    setTimeout(() => this.render(), 0);
  }

  undo(): void {
    const snap = this.undoStack.pop();
    if (snap) {
      wbsNodes.set(snap);
      this.canUndo.set(this.undoStack.length > 0);
      setTimeout(() => this.render(), 0);
    }
  }

  expandAll(): void {
    this.collapsedIds.clear();
    this.render();
  }
  collapseAll(): void {
    this.forEachNode(wbsNodes(), (n) => {
      if (n.children?.length) this.collapsedIds.add(n.id);
    });
    this.render();
  }

  exportJSON(): void {
    const blob = new Blob([JSON.stringify(wbsNodes(), null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'wbs.json';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  /* ── Context menu actions ── */
  ctxAddChild(): void {
    const node = this.ctxNode();
    if (!node) return;
    this.ctxVisible.set(false);
    const ref = this.dialogService.open(WbsEditDialogComponent, {
      data: { mode: 'add' },
      width: '360px',
    });
    ref
      .afterClosed()
      .subscribe((result: { name: string; cost: number; duration: number } | undefined) => {
        if (!result) return;
        this.pushUndo();
        const parentFlat = this.findNode(wbsNodes(), node.id);
        if (!parentFlat) return;
        if (!parentFlat.children) parentFlat.children = [];
        const childIndex = parentFlat.children.length + 1;
        parentFlat.children.push({
          id: this.uid(),
          code: `${parentFlat.code}.${childIndex}`,
          name: result.name,
          cost: result.cost,
          duration: result.duration,
          progress: 0,
          children: [],
        });
        this.collapsedIds.delete(node.id);
        this.recomputeCodes(wbsNodes());
        wbsNodes.set([...wbsNodes()]);
        setTimeout(() => this.render(), 0);
      });
  }

  ctxEdit(): void {
    const node = this.ctxNode();
    if (!node) return;
    this.ctxVisible.set(false);
    const flat = this.findNode(wbsNodes(), node.id);
    if (!flat) return;
    const ref = this.dialogService.open(WbsEditDialogComponent, {
      data: {
        mode: 'edit',
        name: flat.name,
        cost: flat.cost ?? 0,
        duration: flat.duration ?? 0,
        progress: flat.progress ?? 0,
      },
      width: '360px',
    });
    ref
      .afterClosed()
      .subscribe(
        (
          result: { name: string; cost: number; duration: number; progress: number } | undefined,
        ) => {
          if (!result) return;
          this.pushUndo();
          flat.name = result.name;
          flat.cost = result.cost;
          flat.duration = result.duration;
          flat.progress = result.progress;
          wbsNodes.set([...wbsNodes()]);
          setTimeout(() => this.render(), 0);
        },
      );
  }

  ctxToggle(): void {
    const node = this.ctxNode();
    if (!node) return;
    this.ctxVisible.set(false);
    if (this.collapsedIds.has(node.id)) this.collapsedIds.delete(node.id);
    else this.collapsedIds.add(node.id);
    this.render();
  }

  ctxDelete(): void {
    const node = this.ctxNode();
    if (!node) return;
    this.ctxVisible.set(false);
    this.pushUndo();
    this.removeNode(wbsNodes(), node.id);
    this.recomputeCodes(wbsNodes());
    wbsNodes.set([...wbsNodes()]);
    setTimeout(() => this.render(), 0);
  }

  /* ── Rendering ── */
  render(): void {
    const svg = this.svgEl()?.nativeElement;
    if (!svg) return;
    const nodes = wbsNodes();
    if (!nodes.length) return;

    d3.select(svg).selectAll('*').remove();

    // Build layout tree
    const root = this.buildLayoutTree(nodes[0], undefined, 0);
    this.rootLayout = root;

    // Walker-style x-assignment (simplified)
    this.assignPositions(root);

    // Compute bounding box
    let maxX = 0,
      maxY = 0;
    this.walkLayout(root, (n) => {
      maxX = Math.max(maxX, n.x + n.w);
      maxY = Math.max(maxY, n.y + n.h);
    });
    const pad = 24;
    const svgW = maxX + pad * 2;
    const svgH = maxY + pad * 2;

    d3.select(svg).attr('width', svgW).attr('height', svgH);
    const g = d3.select(svg).append('g').attr('transform', `translate(${pad},${pad})`);

    // Draw edges first
    this.walkLayout(root, (node) => {
      for (const child of node.children) {
        const x1 = node.x + node.w / 2;
        const y1 = node.y + node.h;
        const x2 = child.x + child.w / 2;
        const y2 = child.y;
        const mid = (y1 + y2) / 2;
        g.append('path')
          .attr('d', `M${x1},${y1} C${x1},${mid} ${x2},${mid} ${x2},${y2}`)
          .attr('fill', 'none')
          .attr('stroke', '#b0bec5')
          .attr('stroke-width', 1.5);
      }
    });

    // Draw nodes
    this.walkLayout(root, (node) => {
      const ng = g.append('g').attr('transform', `translate(${node.x},${node.y})`);
      const depth = this.nodeDepth(node);
      const fill =
        depth === 0 ? '#1565c0' : depth === 1 ? '#42a5f5' : depth === 2 ? '#90caf9' : '#e3f2fd';
      const textFill = depth <= 1 ? '#fff' : '#263238';

      ng.append('rect')
        .attr('width', node.w)
        .attr('height', node.h)
        .attr('rx', 6)
        .attr('fill', fill);

      // Progress bar
      if (node.progress > 0) {
        ng.append('rect')
          .attr('y', node.h - 4)
          .attr('width', (node.w * Math.min(node.progress, 100)) / 100)
          .attr('height', 4)
          .attr('rx', 2)
          .attr('fill', '#66bb6a')
          .attr('opacity', 0.8);
      }

      // WBS Code (bold)
      ng.append('text')
        .attr('x', 8)
        .attr('y', 16)
        .attr('font-size', '10px')
        .attr('font-weight', 700)
        .attr('fill', textFill)
        .text(node.code);
      // Name
      const dispName = node.name.length > 18 ? node.name.slice(0, 16) + '…' : node.name;
      ng.append('text')
        .attr('x', 8)
        .attr('y', 32)
        .attr('font-size', '12px')
        .attr('fill', textFill)
        .text(dispName);
      // Cost / Duration
      ng.append('text')
        .attr('x', 8)
        .attr('y', 48)
        .attr('font-size', '10px')
        .attr('fill', textFill)
        .attr('opacity', 0.8)
        .text(`$${(node.cost ?? 0).toLocaleString()} · ${node.duration ?? 0}d`);
      // Collapse indicator
      if (this.collapsedIds.has(node.id)) {
        ng.append('text')
          .attr('x', node.w - 16)
          .attr('y', 16)
          .attr('font-size', '10px')
          .attr('fill', textFill)
          .attr('opacity', 0.6)
          .text('+');
      }

      // Interactions
      ng.on('contextmenu', (event: MouseEvent) => {
        event.preventDefault();
        event.stopPropagation();
        this.ctxNode.set(node);
        this.ctxX.set(event.clientX);
        this.ctxY.set(event.clientY);
        this.ctxVisible.set(true);
      });
      ng.on('dblclick', () => {
        this.ctxNode.set(node);
        this.ctxEdit();
      });
      ng.style('cursor', 'pointer');
    });
  }

  /* ── Layout engine (simplified Walker) ── */
  private buildLayoutTree(
    node: WBSNode,
    parent: LayoutNode | undefined,
    depth: number,
  ): LayoutNode {
    const ln: LayoutNode = {
      id: node.id,
      code: node.code ?? '',
      name: node.name,
      cost: node.cost ?? 0,
      duration: node.duration ?? 0,
      progress: node.progress ?? 0,
      x: 0,
      y: depth * (NODE_H + V_GAP),
      w: NODE_W,
      h: NODE_H,
      children: [],
      parent,
      collapsed: this.collapsedIds.has(node.id),
    };
    if (node.children && !ln.collapsed) {
      ln.children = node.children.map((c) => this.buildLayoutTree(c, ln, depth + 1));
    }
    // Rollup for non-leaf
    if (ln.children.length > 0) {
      ln.cost = ln.children.reduce((s, c) => s + c.cost, 0);
      ln.duration = Math.max(...ln.children.map((c) => c.duration), 0);
      const totalCost = ln.children.reduce((s, c) => s + c.cost, 0);
      ln.progress =
        totalCost > 0
          ? ln.children.reduce((s, c) => s + c.progress * c.cost, 0) / totalCost
          : ln.children.reduce((s, c) => s + c.progress, 0) / ln.children.length;
    }
    return ln;
  }

  private assignPositions(root: LayoutNode): void {
    // Bottom-up: compute subtree widths, then top-down: assign x
    const subtreeWidth = (n: LayoutNode): number => {
      if (n.children.length === 0) return n.w;
      const childWidths = n.children.map((c) => subtreeWidth(c));
      return childWidths.reduce((a, b) => a + b, 0) + (n.children.length - 1) * H_GAP;
    };
    const assign = (n: LayoutNode, left: number): void => {
      const sw = subtreeWidth(n);
      n.x = left + (sw - n.w) / 2;
      let childLeft = left;
      for (const child of n.children) {
        const cw = subtreeWidth(child);
        assign(child, childLeft);
        childLeft += cw + H_GAP;
      }
    };
    assign(root, 0);
  }

  /* ── Helpers ── */
  private pushUndo(): void {
    this.undoStack.push(JSON.parse(JSON.stringify(wbsNodes())));
    if (this.undoStack.length > 20) this.undoStack.shift();
    this.canUndo.set(true);
  }

  private uid(): string {
    return 'wbs_' + Math.random().toString(36).slice(2, 9);
  }

  private findNode(nodes: WBSNode[], id: string): WBSNode | null {
    for (const n of nodes) {
      if (n.id === id) return n;
      if (n.children) {
        const found = this.findNode(n.children, id);
        if (found) return found;
      }
    }
    return null;
  }

  private removeNode(nodes: WBSNode[], id: string): boolean {
    for (let i = 0; i < nodes.length; i++) {
      if (nodes[i].id === id) {
        nodes.splice(i, 1);
        return true;
      }
      if (nodes[i].children && this.removeNode(nodes[i].children!, id)) return true;
    }
    return false;
  }

  private recomputeCodes(nodes: WBSNode[], prefix = ''): void {
    nodes.forEach((n, i) => {
      n.code = prefix ? `${prefix}.${i + 1}` : `${i + 1}`;
      if (n.children) this.recomputeCodes(n.children, n.code);
    });
  }

  private forEachNode(nodes: WBSNode[], fn: (n: WBSNode) => void): void {
    for (const n of nodes) {
      fn(n);
      if (n.children) this.forEachNode(n.children, fn);
    }
  }

  private walkLayout(node: LayoutNode, fn: (n: LayoutNode) => void): void {
    fn(node);
    for (const c of node.children) this.walkLayout(c, fn);
  }

  private nodeDepth(n: LayoutNode): number {
    let d = 0;
    let p = n.parent;
    while (p) {
      d++;
      p = p.parent;
    }
    return d;
  }

  private computeRollupCost(nodes: WBSNode[]): number {
    if (!nodes.length) return 0;
    const roll = (n: WBSNode): number =>
      n.children?.length ? n.children.reduce((s, c) => s + roll(c), 0) : (n.cost ?? 0);
    return roll(nodes[0]);
  }

  private computeRollupDuration(nodes: WBSNode[]): number {
    if (!nodes.length) return 0;
    const roll = (n: WBSNode): number =>
      n.children?.length ? Math.max(...n.children.map((c) => roll(c)), 0) : (n.duration ?? 0);
    return roll(nodes[0]);
  }

  private computeRollupProgress(nodes: WBSNode[]): number {
    if (!nodes.length) return 0;
    const roll = (n: WBSNode): number => {
      if (!n.children?.length) return n.progress ?? 0;
      const totalCost = n.children.reduce((s, c) => s + (c.cost ?? 0), 0);
      if (totalCost <= 0) return n.children.reduce((s, c) => s + roll(c), 0) / n.children.length;
      return n.children.reduce((s, c) => s + roll(c) * (c.cost ?? 0), 0) / totalCost;
    };
    return roll(nodes[0]);
  }
}
