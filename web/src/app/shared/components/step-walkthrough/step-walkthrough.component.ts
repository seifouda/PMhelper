import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { CalculationStep } from '../../../core/models/step.model';
import { FormulaDisplayComponent } from '../formula-display/formula-display.component';

@Component({
  selector: 'app-step-walkthrough',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatIconModule, MatExpansionModule, FormulaDisplayComponent],
  template: `
    @if (steps.length) {
      <div class="walkthrough">
        <div class="walkthrough-title">
          <mat-icon>menu_book</mat-icon>
          {{ title }}
        </div>
        <mat-accordion multi>
          @for (step of steps; track step.title; let i = $index) {
            <mat-expansion-panel>
              <mat-expansion-panel-header>
                <mat-panel-title>
                  <span class="step-num">{{ i + 1 }}</span>
                  {{ step.title }}
                </mat-panel-title>
              </mat-expansion-panel-header>

              <div class="step-body">
                @if (step.formula) {
                  <div class="step-row">
                    <span class="step-label">Formula</span>
                    <app-formula-display [tex]="step.formula"></app-formula-display>
                  </div>
                }
                @if (step.substitution) {
                  <div class="step-row">
                    <span class="step-label">Substitution</span>
                    <app-formula-display [tex]="step.substitution"></app-formula-display>
                  </div>
                }
                @if (step.result) {
                  <div class="step-row result-row">
                    <span class="step-label">Result</span>
                    <app-formula-display [tex]="step.result"></app-formula-display>
                  </div>
                }
                @if (step.explanation) {
                  <div class="step-row explanation">
                    <mat-icon>lightbulb</mat-icon>
                    {{ step.explanation }}
                  </div>
                }
              </div>
            </mat-expansion-panel>
          }
        </mat-accordion>
      </div>
    }
  `,
  styles: [
    `
      .walkthrough {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .walkthrough-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        font-size: 15px;
        color: #37474f;
        margin-bottom: 4px;
      }
      .step-num {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #1565c0;
        color: #fff;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        margin-right: 8px;
        flex-shrink: 0;
      }
      .step-body {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 4px 0;
      }
      .step-row {
        display: flex;
        align-items: baseline;
        gap: 12px;
      }
      .step-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: #78909c;
        min-width: 90px;
        flex-shrink: 0;
      }
      .result-row {
        background: #e8f5e9;
        border-radius: 4px;
        padding: 6px 10px;
      }
      .explanation {
        font-size: 13px;
        color: #546e7a;
        align-items: center;
        gap: 6px;
      }
      .explanation mat-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
        color: #ffb300;
      }
    `,
  ],
})
export class StepWalkthroughComponent {
  @Input() title = 'Worked Solution';
  @Input() steps: CalculationStep[] = [];
}
