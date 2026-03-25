import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RAGStatus } from '../../../core/models/evm.model';
import { FormulaDisplayComponent } from '../formula-display/formula-display.component';
import { ExplainerTooltipComponent } from '../explainer-tooltip/explainer-tooltip.component';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatTooltipModule,
    FormulaDisplayComponent,
    ExplainerTooltipComponent,
  ],
  templateUrl: './kpi-card.component.html',
  styleUrl: './kpi-card.component.scss',
})
export class KpiCardComponent {
  @Input() label = '';
  @Input() value: number | string = '—';
  @Input() unit = '';
  @Input() icon = 'analytics';
  @Input() rag: RAGStatus | null = null;
  @Input() tooltip = '';
  @Input() formula = '';
  /** Click event bubbles to parent for navigation */
  @Input() clickable = false;
}
