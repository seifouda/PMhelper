import { ChangeDetectionStrategy, Component, computed, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { EXPLANATIONS } from '../../constants/explanations.const';
import { viewMode } from '../../../core/store/project.store';

@Component({
  selector: 'app-explainer',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MatIconModule, MatTooltipModule],
  template: `
    @if (visible() && tip) {
      <mat-icon class="explainer-icon" [matTooltip]="tip" matTooltipPosition="above"
        >help_outline</mat-icon
      >
    }
  `,
  styles: [
    `
      .explainer-icon {
        font-size: 14px;
        width: 14px;
        height: 14px;
        color: #90a4ae;
        cursor: help;
        vertical-align: middle;
        margin-left: 2px;
      }
    `,
  ],
})
export class ExplainerTooltipComponent {
  @Input() term = '';

  readonly visible = computed(() => viewMode() === 'learn');

  get tip(): string {
    return EXPLANATIONS[this.term] ?? '';
  }
}
