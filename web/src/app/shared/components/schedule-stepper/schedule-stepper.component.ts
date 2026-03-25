import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

export type StepState = 'complete' | 'pending' | 'optional';

export interface PmStep {
  number: number;
  label: string;
  state: StepState;
  tooltip: string;
}

@Component({
  selector: 'app-schedule-stepper',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatIconModule, MatTooltipModule],
  template: `
    <div class="stepper" role="list">
      @for (step of steps; track step.number) {
        <div class="step-wrapper" role="listitem">
          <button
            class="step-badge"
            [class.complete]="step.state === 'complete'"
            [class.pending]="step.state === 'pending'"
            [class.optional]="step.state === 'optional'"
            [matTooltip]="step.tooltip"
            matTooltipPosition="below"
            (click)="stepClick.emit(step.number)"
            type="button"
            [attr.aria-label]="'Step ' + step.number + ': ' + step.label + ' (' + step.state + ')'"
          >
            @if (step.state === 'complete') {
              <mat-icon class="badge-icon">check</mat-icon>
            } @else if (step.state === 'optional') {
              <span class="badge-num">{{ step.number }}</span>
            } @else {
              <span class="badge-num">{{ step.number }}</span>
            }
          </button>

          <div class="step-label-group">
            <span class="step-label">{{ step.label }}</span>
            @if (step.state === 'optional') {
              <span class="optional-tag">optional</span>
            }
          </div>

          @if (!$last) {
            <div class="connector" [class.active]="step.state === 'complete'"></div>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .stepper {
        display: flex;
        align-items: center;
        gap: 0;
        padding: 8px 0;
        overflow-x: auto;
      }
      .step-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        flex-shrink: 0;
      }
      .step-badge {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        border: 2px solid #cbd5e1;
        background: #f1f5f9;
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 700;
        transition: all 0.2s;
        outline: none;

        &:hover {
          border-color: #3b82f6;
          color: #3b82f6;
        }

        &.complete {
          border-color: #22c55e;
          background: #22c55e;
          color: white;
          .badge-icon {
            font-size: 18px;
            width: 18px;
            height: 18px;
          }
        }

        &.optional {
          border-style: dashed;
        }
      }
      .badge-num {
        line-height: 1;
      }
      .badge-icon {
        line-height: 1;
      }

      .step-label-group {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 4px;
        gap: 2px;
      }
      .step-label {
        font-size: 0.72rem;
        color: #475569;
        white-space: nowrap;
        font-weight: 500;
      }
      .optional-tag {
        font-size: 0.65rem;
        color: #94a3b8;
        font-style: italic;
      }
      .connector {
        position: absolute;
        top: 16px;
        left: calc(100% + 0px);
        width: 40px;
        height: 2px;
        background: #cbd5e1;
        &.active {
          background: #22c55e;
        }
      }
      .step-wrapper:not(:last-child) {
        margin-right: 52px;
      }
    `,
  ],
})
export class ScheduleStepperComponent {
  @Input() steps: PmStep[] = [];
  @Output() stepClick = new EventEmitter<number>();
}
