import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';

import { SWOTAnalysis, SWOTItem } from '../../core/models/project.model';
import { swotAnalysis, riskRegister, evmKpis, viewMode } from '../../core/store/project.store';
import { SwotItemDialogComponent } from './swot-item-dialog.component';

type Quadrant = 'strengths' | 'weaknesses' | 'opportunities' | 'threats';

@Component({
  selector: 'app-swot',
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
    <div class="swot-host">
      <!-- ── Toolbar ── -->
      <div class="toolbar">
        <button
          mat-stroked-button
          (click)="autoExtract()"
          matTooltip="Auto-extract from Risk Register & EVM KPIs"
        >
          <mat-icon>auto_fix_high</mat-icon> Auto-Extract
        </button>
        <button mat-stroked-button (click)="clearAll()" [disabled]="!hasData()">
          <mat-icon>clear_all</mat-icon> Clear All
        </button>
        <button mat-stroked-button (click)="exportPng()" [disabled]="!hasData()">
          <mat-icon>download</mat-icon> Export PNG
        </button>
      </div>

      <!-- ── 2×2 Matrix ── -->
      <div class="matrix">
        @for (q of quadrants; track q.key) {
          <div class="quadrant" [style.background]="q.bg" [style.border-color]="q.border">
            <div class="q-header" [style.color]="q.color">
              <mat-icon>{{ q.icon }}</mat-icon>
              <span>{{ q.label }}</span>
              <button mat-icon-button (click)="addItem(q.key)" matTooltip="Add item">
                <mat-icon>add_circle_outline</mat-icon>
              </button>
            </div>
            <div class="q-items">
              @for (item of getItems(q.key); track item.id) {
                <div class="q-item">
                  <span class="item-text">{{ item.text }}</span>
                  @if (item.source) {
                    <span class="item-source">{{ item.source }}</span>
                  }
                  <button mat-icon-button class="del-btn" (click)="removeItem(q.key, item.id)">
                    <mat-icon>close</mat-icon>
                  </button>
                </div>
              }
              @if (getItems(q.key).length === 0) {
                <div class="q-empty">No items yet</div>
              }
            </div>
          </div>
        }
      </div>

      <!-- ── Learn mode ── -->
      @if (isLearnMode()) {
        <div class="section learn-section">
          <div class="section-title"><mat-icon>school</mat-icon> SWOT Analysis Concepts</div>
          <div class="learn-body">
            <div class="formula-step">
              <div class="step-num">1</div>
              <div>
                <strong>Strengths:</strong> Internal positive factors — what the project does well.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">2</div>
              <div>
                <strong>Weaknesses:</strong> Internal negative factors — limitations or resource
                gaps.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">3</div>
              <div>
                <strong>Opportunities:</strong> External positive factors — market conditions or
                stakeholder support.
              </div>
            </div>
            <div class="formula-step">
              <div class="step-num">4</div>
              <div>
                <strong>Threats:</strong> External negative factors — risks, competition, regulatory
                changes.
              </div>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .swot-host {
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
      .matrix {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        flex: 1;
        min-height: 300px;
      }
      .quadrant {
        border-radius: 8px;
        border: 2px solid;
        padding: 12px;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
      }
      .q-header {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
      }
      .q-header button {
        margin-left: auto;
      }
      .q-items {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .q-item {
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
      }
      .item-text {
        flex: 1;
      }
      .item-source {
        font-size: 10px;
        color: #78909c;
        background: #eceff1;
        padding: 1px 6px;
        border-radius: 8px;
      }
      .del-btn {
        width: 24px;
        height: 24px;
        line-height: 24px;
      }
      .del-btn mat-icon {
        font-size: 14px;
        width: 14px;
        height: 14px;
      }
      .q-empty {
        font-size: 12px;
        color: #90a4ae;
        font-style: italic;
      }
      .section {
        background: #fff;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e0e0e0;
        flex-shrink: 0;
      }
      .learn-section {
        background: #e3f2fd;
        border-color: #90caf9;
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
        background: #1976d2;
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
export class SwotComponent {
  private readonly dialogService = inject(MatDialog);

  readonly isLearnMode = computed(() => viewMode() === 'learn');
  readonly hasData = computed(() => {
    const s = swotAnalysis();
    return (
      s !== null &&
      s.strengths.length + s.weaknesses.length + s.opportunities.length + s.threats.length > 0
    );
  });

  readonly quadrants: {
    key: Quadrant;
    label: string;
    icon: string;
    bg: string;
    border: string;
    color: string;
  }[] = [
    {
      key: 'strengths',
      label: 'Strengths',
      icon: 'thumb_up',
      bg: '#e8f5e9',
      border: '#66bb6a',
      color: '#2e7d32',
    },
    {
      key: 'weaknesses',
      label: 'Weaknesses',
      icon: 'thumb_down',
      bg: '#fff3e0',
      border: '#ffa726',
      color: '#e65100',
    },
    {
      key: 'opportunities',
      label: 'Opportunities',
      icon: 'lightbulb',
      bg: '#e3f2fd',
      border: '#42a5f5',
      color: '#1565c0',
    },
    {
      key: 'threats',
      label: 'Threats',
      icon: 'warning',
      bg: '#fce4ec',
      border: '#ef5350',
      color: '#c62828',
    },
  ];

  getItems(q: Quadrant): SWOTItem[] {
    return swotAnalysis()?.[q] ?? [];
  }

  addItem(q: Quadrant): void {
    const ref = this.dialogService.open(SwotItemDialogComponent, {
      data: { quadrant: q },
      width: '360px',
    });
    ref.afterClosed().subscribe((result: { text: string } | undefined) => {
      if (!result) return;
      const current = swotAnalysis() ?? {
        strengths: [],
        weaknesses: [],
        opportunities: [],
        threats: [],
      };
      const updated = { ...current };
      updated[q] = [...updated[q], { id: this.uid(), text: result.text, source: 'Manual' }];
      swotAnalysis.set(updated);
    });
  }

  removeItem(q: Quadrant, id: string): void {
    const current = swotAnalysis();
    if (!current) return;
    const updated = { ...current };
    updated[q] = updated[q].filter((i) => i.id !== id);
    swotAnalysis.set(updated);
  }

  autoExtract(): void {
    const current = swotAnalysis() ?? {
      strengths: [],
      weaknesses: [],
      opportunities: [],
      threats: [],
    };
    const updated = {
      ...current,
      strengths: [...current.strengths],
      weaknesses: [...current.weaknesses],
      opportunities: [...current.opportunities],
      threats: [...current.threats],
    };
    const existingTexts = new Set([
      ...updated.strengths.map((i) => i.text),
      ...updated.weaknesses.map((i) => i.text),
      ...updated.opportunities.map((i) => i.text),
      ...updated.threats.map((i) => i.text),
    ]);

    const add = (q: Quadrant, text: string, source: string) => {
      if (!existingTexts.has(text)) {
        updated[q].push({ id: this.uid(), text, source });
        existingTexts.add(text);
      }
    };

    // Extract from Risk Register — high-exposure risks → Threats
    const risks = riskRegister();
    for (const r of risks) {
      if (r.exposure > 0) {
        add('threats', `Risk: ${r.name} (EMV: ${r.exposure.toFixed(0)})`, 'Risk Register');
      }
    }

    // Extract from EVM KPIs
    const kpis = evmKpis();
    if (kpis) {
      if (kpis.cpi >= 1.0) add('strengths', `CPI = ${kpis.cpi.toFixed(2)} — under budget`, 'EVM');
      else add('weaknesses', `CPI = ${kpis.cpi.toFixed(2)} — over budget`, 'EVM');
      if (kpis.spi >= 1.0)
        add('strengths', `SPI = ${kpis.spi.toFixed(2)} — on/ahead of schedule`, 'EVM');
      else add('weaknesses', `SPI = ${kpis.spi.toFixed(2)} — behind schedule`, 'EVM');
      if (kpis.cr >= 1.0)
        add('opportunities', `Critical Ratio ${kpis.cr.toFixed(2)} — healthy project`, 'EVM');
    }

    swotAnalysis.set(updated);
  }

  clearAll(): void {
    swotAnalysis.set({ strengths: [], weaknesses: [], opportunities: [], threats: [] });
  }

  exportPng(): void {
    // Simple export: serialize the SWOT matrix to a downloadable JSON (PNG would need html2canvas)
    const blob = new Blob([JSON.stringify(swotAnalysis(), null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'swot_analysis.json';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  private uid(): string {
    return 'swot_' + Math.random().toString(36).slice(2, 9);
  }
}
