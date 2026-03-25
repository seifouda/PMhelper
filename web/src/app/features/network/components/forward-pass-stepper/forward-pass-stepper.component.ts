/**
 * ForwardPassStepperComponent
 * Animates the CPM forward-pass (ES/EF computation) step by step.
 * Visible only in Learn Mode. Highlights the current node via selectedTaskId.
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
import { MatCardModule } from '@angular/material/card';

import { cpmResults, selectedTaskId } from '../../../../core/store/project.store';
import { CPMNode } from '../../../../core/models/cpm-result.model';

interface ForwardStep {
  nodeId: string;
  es: number;
  ef: number;
  duration: number;
  predecessorEFs: Array<{ id: string; ef: number }>;
  formula: string;
  explanation: string;
}

@Component({
  selector: 'app-forward-pass-stepper',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatCardModule],
  template: `
    <div class="pass-stepper">
      <div class="stepper-header">
        <mat-icon class="header-icon">arrow_forward</mat-icon>
        <span class="header-title">Forward Pass — Early Times</span>
        <span class="step-badge">{{ currentIndex() + 1 }} / {{ steps().length }}</span>
      </div>

      @if (currentStep(); as step) {
        <div class="step-card">
          <div class="node-id">
            Activity <strong>{{ step.nodeId }}</strong>
          </div>

          @if (step.predecessorEFs.length === 0) {
            <div class="formula-line">
              <span class="formula-label">ES =</span>
              <span class="formula-value">0</span>
              <span class="formula-note">(start activity)</span>
            </div>
          } @else {
            <div class="formula-line">
              <span class="formula-label">ES =</span>
              <span class="formula-code">max(EF of predecessors)</span>
            </div>
            <div class="sub-values">
              @for (pred of step.predecessorEFs; track pred.id) {
                <span class="sub-val">EF({{ pred.id }}) = {{ pred.ef }}</span>
              }
            </div>
            <div class="formula-line result">
              <span class="formula-label">ES =</span>
              <span class="formula-value">{{ step.es }}</span>
            </div>
          }
          <div class="formula-line result">
            <span class="formula-label">EF =</span>
            <span class="formula-code">ES + Duration = </span>
            <span class="formula-value">{{ step.es }} + {{ step.duration }} = {{ step.ef }}</span>
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
          color="primary"
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
      }
      .stepper-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        color: #1565c0;
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
          background: #e3f2fd;
          color: #1565c0;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 700;
        }
      }
      .step-card {
        background: #f8f9fa;
        border: 1px solid #e3f2fd;
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
          color: #1565c0;
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
        .formula-label {
          color: #546e7a;
          font-weight: 600;
          min-width: 30px;
        }
        .formula-code {
          color: #455a64;
          font-family: monospace;
        }
        .formula-value {
          color: #1565c0;
          font-weight: 700;
          font-size: 0.95rem;
        }
        .formula-note {
          color: #90a4ae;
          font-size: 0.8rem;
        }
      }
      .sub-values {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        padding-left: 38px;
        .sub-val {
          background: #e8f5e9;
          color: #2e7d32;
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
export class ForwardPassStepperComponent {
  private readonly destroyRef = inject(DestroyRef);
  readonly steps = computed<ForwardStep[]>(() => {
    const results = cpmResults();
    if (!results) return [];
    return buildForwardSteps(results.nodes, results.edges);
  });

  readonly currentIndex = signal(0);
  readonly currentStep = computed(() => this.steps()[this.currentIndex()] ?? null);

  constructor() {
    // Highlight current node in network as steps advance
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

// ── Build forward-pass steps from CPM results ──────────────────────────────

function buildForwardSteps(
  nodes: CPMNode[],
  edges: Array<{ from: string; to: string }>,
): ForwardStep[] {
  const nodeMap = new Map<string, CPMNode>(nodes.map((n) => [n.id, n]));
  const predecessors = new Map<string, string[]>(nodes.map((n) => [n.id, []]));
  for (const e of edges) {
    predecessors.get(e.to)?.push(e.from);
  }

  // Topological order
  const order = topSort(
    nodes.map((n) => n.id),
    predecessors,
  );
  const steps: ForwardStep[] = [];

  for (const id of order) {
    const node = nodeMap.get(id);
    if (!node) continue;
    const preds = predecessors.get(id) ?? [];
    const predEFs = preds
      .map((pid) => nodeMap.get(pid))
      .filter((n): n is CPMNode => n !== undefined)
      .map((n) => ({ id: n.id, ef: n.EF }));

    const esExplain =
      predEFs.length === 0
        ? `Activity ${id} has no predecessors, so it can start immediately at time 0.`
        : `ES(${id}) = max(${predEFs.map((p) => `EF(${p.id})=${p.ef}`).join(', ')}) = ${node.ES}`;
    const efExplain = `EF(${id}) = ES + Duration = ${node.ES} + ${node.duration} = ${node.EF}`;

    steps.push({
      nodeId: id,
      es: node.ES,
      ef: node.EF,
      duration: node.duration,
      predecessorEFs: predEFs,
      formula: `ES = max(predecessor EFs); EF = ES + ${node.duration}`,
      explanation: `${esExplain}. ${efExplain}.`,
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
    // Find successors
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
