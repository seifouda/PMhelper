import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { ValidationError } from '../../../features/input/components/task-grid/task-grid.component';

@Component({
  selector: 'app-validation-panel',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatIconModule, MatButtonModule],
  template: `
    @if (errors.length > 0) {
      <div class="validation-panel" role="alert">
        <div class="panel-header">
          <mat-icon class="error-icon">error_outline</mat-icon>
          <span>{{ errors.length }} issue{{ errors.length !== 1 ? 's' : '' }} found</span>
        </div>
        <ul class="error-list">
          @for (err of errors; track $index) {
            <li class="error-item" (click)="errorClick.emit(err)" [class.clickable]="err.row > 0">
              @if (err.row > 0) {
                <span class="row-badge">Row {{ err.row }}</span>
              } @else {
                <span class="row-badge row-badge--global">Global</span>
              }
              <span class="field-name">{{ err.field }}:</span>
              <span class="error-msg">{{ err.message }}</span>
            </li>
          }
        </ul>
      </div>
    }
  `,
  styles: [
    `
      .validation-panel {
        background: #fef2f2;
        border: 1px solid #fca5a5;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.85rem;
      }
      .panel-header {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        color: #dc2626;
        margin-bottom: 8px;
      }
      .error-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
      .error-list {
        margin: 0;
        padding: 0;
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .error-item {
        display: flex;
        align-items: baseline;
        gap: 6px;
      }
      .error-item.clickable {
        cursor: pointer;
        &:hover {
          text-decoration: underline;
        }
      }
      .row-badge {
        background: #fee2e2;
        color: #dc2626;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.75rem;
        font-weight: 700;
        white-space: nowrap;
      }
      .row-badge--global {
        background: #fef3c7;
        color: #d97706;
      }
      .field-name {
        font-weight: 600;
        color: #374151;
      }
      .error-msg {
        color: #4b5563;
      }
    `,
  ],
})
export class ValidationPanelComponent {
  @Input() errors: ValidationError[] = [];
  @Output() errorClick = new EventEmitter<ValidationError>();
}
