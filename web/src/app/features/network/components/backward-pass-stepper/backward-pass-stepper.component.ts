/**
 * BackwardPassStepperComponent
 * Animates the CPM backward-pass (LS/LF/Float computation) step by step.
 * Visible only in Learn Mode.
 */
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { cpmResults, selectedTaskId } from '../../../../core/store/project.store';
import { CPMNode } from '../../../../core/models/cpm-result.model';

interface BackwardStep {
  nodeId: string;
  lf: number;
  ls: number;
  totalFloat: number;
  duration: number;
  successorLSs: Array<{ id: string; ls: number }>;
  explanation: string;
}

@Component({
  selector: 'app-backward-pass-stepper',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div class="pass-stepper backward">
      <div class="stepper-header">
        <mat-icon class="header-icon">arrow_back</mat-icon>
        <span class="header-title">Backward Pass — Late Times & Float</span>
        <span class="step-badge">{{ currentIndex() + 1 }} / {{ steps().length }}</span>
      </div>

      @if (currentStep(); as step) {
        <div class="step-card">
          <div class="node-id">
            Activity <strong>{{ step.nodeId }}</strong>
          </div>

          @if (step.successorLSs.length === 0) {
            <div class="formula-line">
              <span class="formula-label">LF =</span>
              <span class="formula-value">{{ step.lf }}</span>
              <span class="formula-note">(project duration — end activity)</span>
            </div>
          } @else {
            <div class="formula-line">
              <span class="formula-label">LF =</span>
              <span class="formula-code">min(LS of successors)</span>
            </div>
            <div class="sub-values">
              @for (succ of step.successorLSs; track succ.id) {
                <span class="sub-val">LS({{ succ.id }}) = {{ succ.ls }}</span>
              }
            </div>
            <div class="formula-line result">
              <span class="formula-label">LF =</span>
              <span class="formula-value">{{ step.lf }}</span>
            </div>
          }

          <div class="formula-line result">
            <span class="formula-label">LS =</span>
            <span class="formula-code">LF − Duration = </span>
            <span class="formula-value">{{ step.lf }} − {{ step.duration }} = {{ step.ls }}</span>
          </div>

          <div class="formula-line float" [class.zero-float]="step.totalFloat === 0">
            <span class="formula-label">Float =</span>
            <span class="formula-code">LS − ES = </span>
            <span class="formula-value"
              >{{ step.ls }} − {{ step.lf - step.duration - step.totalFloat }} =
              {{ step.totalFloat }}</span
            >
            @if (step.totalFloat === 0) {
              <span class="critical-badge">CRITICAL</span>
            }
          </div>

          <p class="explanation">{{ step.explanation }}</p>
        </div>
      }

      <div class="stepper-controls">
        <button mat-stroked-button (click)="prev()" [disabled]="currentIndex() === 0">
          <mat-icon>chevron_left</mat-icon> Prev
        </button>
        <button mat-stroked-button (click)="reset()">
          <mat-icon>restart_alt</mat-icon>
        </button>
        <button
          mat-flat-button
          color="accent"
          (click)="next()"
          [disabled]="currentIndex() >= steps().length - 1"
        >
          Next <mat-icon>chevron_right</mat-icon>
        </button>
      </div>
    </div>
  `,
  styles: [
    `
      .pass-stepper {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 12px;
        height: 100%;
        &.backward .stepper-header {
          color: #6a1b9a;
        }
      }
      .stepper-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        .header-icon {
          font-size: 1.2rem;
          width: 1.2rem;
          height: 1.2rem;
        }
        .header-title {
          flex: 1;
          font-size: 0.9rem;
        }
        .step-badge {
          background: #f3e5f5;
          color: #6a1b9a;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 700;
        }
      }
      .step-card {
        background: #fdf8ff;
        border: 1px solid #e1bee7;
        border-radius: 8px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        flex: 1;
        overflow-y: auto;
      }
      .node-id {
        font-size: 0.9rem;
        color: #37474f;
        strong {
          color: #6a1b9a;
        }
      }
      .formula-line {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85rem;
        &.result {
          margin-top: 4px;
        }
        &.float {
          padding: 4px 6px;
          border-radius: 4px;
          background: #f5f5f5;
        }
        &.zero-float {
          background: #ffebee;
        }
        .formula-label {
          color: #546e7a;
          font-weight: 600;
          min-width: 42px;
        }
        .formula-code {
          color: #455a64;
          font-family: monospace;
        }
        .formula-value {
          color: #6a1b9a;
          font-weight: 700;
          font-size: 0.95rem;
        }
        .formula-note {
          color: #90a4ae;
          font-size: 0.8rem;
        }
        .critical-badge {
          margin-left: auto;
          background: #c62828;
          color: white;
          padding: 1px 8px;
          border-radius: 10px;
          font-size: 0.7rem;
          font-weight: 700;
        }
      }
      .sub-values {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        padding-left: 50px;
        .sub-val {
          background: #fce4ec;
          color: #880e4f;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 0.78rem;
          font-family: monospace;
        }
      }
      .explanation {
        margin: 0;
        color: #607d8b;
        font-size: 0.8rem;
        line-height: 1.4;
        border-top: 1px dashed #cfd8dc;
        padding-top: 6px;
      }
      .stepper-controls {
        display: flex;
        gap: 8px;
        justify-content: center;
        align-items: center;
      }
    `,
  ],
})
export class BackwardPassStepperComponent {
  private readonly destroyRef = inject(DestroyRef);
  readonly steps = computed<BackwardStep[]>(() => {
    const results = cpmResults();
    if (!results) return [];
    return buildBackwardSteps(results.nodes, results.edges, results.project_duration);
  });

  readonly currentIndex = signal(0);
  readonly currentStep = computed(() => this.steps()[this.currentIndex()] ?? null);

  constructor() {
    effect(() => {
      const step = this.currentStep();
      selectedTaskId.set(step?.nodeId ?? null);
    });
  }

  next(): void {
    if (this.currentIndex() < this.steps().length - 1) {
      this.currentIndex.update((i) => i + 1);
    }
  }

  prev(): void {
    if (this.currentIndex() > 0) {
      this.currentIndex.update((i) => i - 1);
    }
  }

  reset(): void {
    this.currentIndex.set(0);
  }
}

function buildBackwardSteps(
  nodes: CPMNode[],
  edges: Array<{ from: string; to: string }>,
  projectDuration: number,
): BackwardStep[] {
  const nodeMap = new Map<string, CPMNode>(nodes.map((n) => [n.id, n]));
  const successors = new Map<string, string[]>(nodes.map((n) => [n.id, []]));
  for (const e of edges) {
    successors.get(e.from)?.push(e.to);
  }

  // Reverse topological order (process from end nodes backwards)
  const predecessors = new Map<string, string[]>(nodes.map((n) => [n.id, []]));
  for (const e of edges) {
    predecessors.get(e.to)?.push(e.from);
  }
  const fwdOrder = topSort(
    nodes.map((n) => n.id),
    predecessors,
  );
  const revOrder = [...fwdOrder].reverse();

  const steps: BackwardStep[] = [];
  for (const id of revOrder) {
    const node = nodeMap.get(id);
    if (!node) continue;
    const succs = successors.get(id) ?? [];
    const succLSs = succs
      .map((sid) => nodeMap.get(sid))
      .filter((n): n is CPMNode => n !== undefined)
      .map((n) => ({ id: n.id, ls: n.LS }));

    const lfNote =
      succs.length === 0
        ? `Activity ${id} ends the project at time ${projectDuration}.`
        : `LF(${id}) = min(${succLSs.map((s) => `LS(${s.id})=${s.ls}`).join(', ')}) = ${node.LF}`;
    const lsNote = `LS(${id}) = LF − Duration = ${node.LF} − ${node.duration} = ${node.LS}.`;
    const floatNote =
      node.total_float === 0
        ? `Float = ${node.total_float} → Activity ${id} is on the critical path!`
        : `Float = ${node.total_float} → this activity can slip up to ${node.total_float} time unit(s) without delaying the project.`;

    steps.push({
      nodeId: id,
      lf: node.LF,
      ls: node.LS,
      totalFloat: node.total_float,
      duration: node.duration,
      successorLSs: succLSs,
      explanation: `${lfNote} ${lsNote} ${floatNote}`,
    });
  }
  return steps;
}

function topSort(ids: string[], predecessors: Map<string, string[]>): string[] {
  const inDeg = new Map<string, number>(ids.map((id) => [id, (predecessors.get(id) ?? []).length]));
  const queue = ids.filter((id) => (inDeg.get(id) ?? 0) === 0).sort();
  const result: string[] = [];
  while (queue.length > 0) {
    const id = queue.shift()!;
    result.push(id);
    for (const other of ids) {
      if ((predecessors.get(other) ?? []).includes(id)) {
        const nd = (inDeg.get(other) ?? 0) - 1;
        inDeg.set(other, nd);
        if (nd === 0) queue.push(other);
      }
    }
  }
  return result;
}
