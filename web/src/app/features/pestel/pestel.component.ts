import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';

import { PESTELFactor, PESTELAnalysis } from '../../core/models/project.model';
import { pestelAnalysis, riskRegister, viewMode } from '../../core/store/project.store';
import { PestelFactorDialogComponent } from './pestel-factor-dialog.component';

type PCategory = 'Political' | 'Economic' | 'Social' | 'Technological' | 'Environmental' | 'Legal';

const CATEGORIES: { key: PCategory; icon: string; color: string }[] = [
  { key: 'Political', icon: 'account_balance', color: '#1565c0' },
  { key: 'Economic', icon: 'attach_money', color: '#2e7d32' },
  { key: 'Social', icon: 'groups', color: '#6a1b9a' },
  { key: 'Technological', icon: 'computer', color: '#00838f' },
  { key: 'Environmental', icon: 'eco', color: '#558b2f' },
  { key: 'Legal', icon: 'gavel', color: '#bf360c' },
];

@Component({
  selector: 'app-pestel',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
  ],
  template: `
    <div class="pestel-host">
      <!-- ── Toolbar ── -->
      <div class="toolbar">
        <button mat-flat-button color="primary" (click)="addFactor()">
          <mat-icon>add</mat-icon> Add Factor
        </button>
        <button mat-stroked-button (click)="clearAll()" [disabled]="!hasData()">
          <mat-icon>clear_all</mat-icon> Clear All
        </button>
        <button mat-stroked-button (click)="exportCsv()" [disabled]="!hasData()">
          <mat-icon>download</mat-icon> Export CSV
        </button>
      </div>

      <!-- ── Category cards (heatmap intensity) ── -->
      <div class="cat-grid">
        @for (cat of categories; track cat.key) {
          <div
            class="cat-card"
            [style.border-left-color]="cat.color"
            [class.active]="selectedCategory() === cat.key"
            (click)="selectCategory(cat.key)"
          >
            <mat-icon [style.color]="cat.color">{{ cat.icon }}</mat-icon>
            <div class="cat-label">{{ cat.key }}</div>
            <div class="cat-count" [style.background]="heatColor(catCount(cat.key))">
              {{ catCount(cat.key) }}
            </div>
          </div>
        }
      </div>

      <!-- ── Factor table ── -->
      @if (filteredFactors().length) {
        <div class="section">
          <div class="section-title">
            <mat-icon>table_chart</mat-icon>
            {{ selectedCategory() ?? 'All' }} Factors
          </div>
          <div class="table-scroll">
            <table class="pestel-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Description</th>
                  <th class="num-col">Impact</th>
                  <th class="num-col">Probability</th>
                  <th class="num-col">Exposure</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                @for (f of filteredFactors(); track f.id) {
                  <tr>
                    <td>
                      <span class="cat-badge" [style.color]="catColor(f.category)">{{
                        f.category
                      }}</span>
                    </td>
                    <td>{{ f.description }}</td>
                    <td class="num">{{ f.impact_score }}</td>
                    <td class="num">{{ f.probability_score }}</td>
                    <td class="num exposure">{{ f.exposure }}</td>
                    <td>
                      <button
                        mat-icon-button
                        (click)="createRisk(f)"
                        matTooltip="Push to Risk Register"
                      >
                        <mat-icon>add_alert</mat-icon>
                      </button>
                      <button mat-icon-button (click)="removeFactor(f.id)">
                        <mat-icon>delete_outline</mat-icon>
                      </button>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>
      } @else {
        <div class="empty-state">
          <mat-icon>public</mat-icon>
          <p>No PESTEL factors yet. Click <strong>Add Factor</strong> to start.</p>
        </div>
      }

      <!-- ── Learn mode ── -->
      @if (isLearnMode()) {
        <div class="section learn-section">
          <div class="section-title"><mat-icon>school</mat-icon> PESTEL Concepts</div>
          <div class="learn-body">
            <div class="formula-step">
              <div class="step-num">1</div>
              <div>
                <strong>PESTEL:</strong> Analyse 6 categories of external factors: Political,
                Economic, Social, Technological, Environmental, Legal.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">2</div>
              <div>
                <strong>Exposure:</strong> <code>Impact × Probability</code> — higher exposure =
                greater priority for mitigation.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">3</div>
              <div>
                <strong>Create Risk:</strong> Promote a high-exposure PESTEL factor to the project
                Risk Register for formal tracking.
              </div>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .pestel-host {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 16px;
        height: 100%;
        overflow-y: auto;
      }
      .toolbar {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .cat-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 8px;
      }
      @media (max-width: 900px) {
        .cat-grid {
          grid-template-columns: repeat(3, 1fr);
        }
      }
      .cat-card {
        border: 1px solid #e0e0e0;
        border-left: 4px solid;
        border-radius: 6px;
        padding: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        cursor: pointer;
        transition: background 0.15s;
      }
      .cat-card:hover {
        background: #f5f5f5;
      }
      .cat-card.active {
        background: #e3f2fd;
        border-color: #42a5f5;
      }
      .cat-label {
        font-size: 11px;
        font-weight: 600;
        color: #546e7a;
      }
      .cat-count {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        color: #fff;
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
      .table-scroll {
        overflow-x: auto;
      }
      .pestel-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .pestel-table th {
        background: #f5f5f5;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #e0e0e0;
        font-weight: 500;
        color: #546e7a;
      }
      .pestel-table td {
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
      .exposure {
        font-weight: 600;
        color: #e65100;
      }
      .cat-badge {
        font-size: 12px;
        font-weight: 500;
      }
      .learn-section {
        background: #fff3e0;
        border-color: #ffcc80;
        flex-shrink: 0;
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
        background: #e65100;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 600;
        flex-shrink: 0;
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
export class PestelComponent {
  private readonly dialogService = inject(MatDialog);

  readonly categories = CATEGORIES;
  readonly isLearnMode = computed(() => viewMode() === 'learn');
  readonly selectedCategory = signal<PCategory | null>(null);

  readonly hasData = computed(() => (pestelAnalysis()?.factors.length ?? 0) > 0);

  readonly filteredFactors = computed(() => {
    const all = pestelAnalysis()?.factors ?? [];
    const sel = this.selectedCategory();
    return sel ? all.filter((f) => f.category === sel) : all;
  });

  catCount(cat: PCategory): number {
    return (pestelAnalysis()?.factors ?? []).filter((f) => f.category === cat).length;
  }

  catColor(cat: PCategory): string {
    return CATEGORIES.find((c) => c.key === cat)?.color ?? '#546e7a';
  }

  heatColor(count: number): string {
    if (count === 0) return '#bdbdbd';
    if (count <= 2) return '#ffb74d';
    if (count <= 4) return '#ff9800';
    return '#e65100';
  }

  selectCategory(cat: PCategory): void {
    this.selectedCategory.set(this.selectedCategory() === cat ? null : cat);
  }

  addFactor(): void {
    const ref = this.dialogService.open(PestelFactorDialogComponent, {
      data: { defaultCategory: this.selectedCategory() },
      width: '400px',
    });
    ref.afterClosed().subscribe((result: Omit<PESTELFactor, 'id' | 'exposure'> | undefined) => {
      if (!result) return;
      const current = pestelAnalysis() ?? { factors: [] };
      const factor: PESTELFactor = {
        ...result,
        id: this.uid(),
        exposure: result.impact_score * result.probability_score,
      };
      pestelAnalysis.set({ factors: [...current.factors, factor] });
    });
  }

  removeFactor(id: string): void {
    const current = pestelAnalysis();
    if (!current) return;
    pestelAnalysis.set({ factors: current.factors.filter((f) => f.id !== id) });
  }

  createRisk(f: PESTELFactor): void {
    // Push to risk register
    const risks = riskRegister();
    const exists = risks.some((r) => r.name === f.description);
    if (exists) return;
    riskRegister.set([
      ...risks,
      {
        id: 'pestel_' + Math.random().toString(36).slice(2, 9),
        name: f.description,
        description: `From PESTEL (${f.category})`,
        probability: f.probability_score / 5,
        impact: f.impact_score * 1000,
        category: 'Other',
        exposure: (f.probability_score / 5) * (f.impact_score * 1000),
      },
    ]);
  }

  clearAll(): void {
    pestelAnalysis.set({ factors: [] });
  }

  exportCsv(): void {
    const factors = pestelAnalysis()?.factors ?? [];
    const header = 'Category,Description,Impact,Probability,Exposure\n';
    const rows = factors
      .map(
        (f) =>
          `${f.category},"${f.description}",${f.impact_score},${f.probability_score},${f.exposure}`,
      )
      .join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'pestel_analysis.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  private uid(): string {
    return 'pestel_' + Math.random().toString(36).slice(2, 9);
  }
}
