import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';

import { TaskGridComponent, ValidationError } from './components/task-grid/task-grid.component';
import { EvmPeriodGridComponent } from './components/evm-period-grid/evm-period-grid.component';
import { RiskEntryComponent } from './components/risk-entry/risk-entry.component';
import { CpmResultsTableComponent } from './components/cpm-results-table/cpm-results-table.component';
import { ValidationPanelComponent } from '../../shared/components/validation-panel/validation-panel.component';
import { FileDropzoneComponent } from '../../shared/components/file-dropzone/file-dropzone.component';
import { SampleSelectorComponent } from '../../shared/components/sample-selector/sample-selector.component';
import {
  ScheduleStepperComponent,
  PmStep,
} from '../../shared/components/schedule-stepper/schedule-stepper.component';

import {
  activities,
  evmProject,
  riskRegister,
  cpmResults,
  isLoading,
} from '../../core/store/project.store';
import { Activity } from '../../core/models/activity.model';
import { EVMPeriod, EVMProject } from '../../core/models/evm.model';
import { Risk } from '../../core/models/risk.model';
import { CpmService } from '../../core/services/cpm.service';

@Component({
  selector: 'app-input',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatTabsModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatProgressBarModule,
    MatDividerModule,
    TaskGridComponent,
    EvmPeriodGridComponent,
    RiskEntryComponent,
    CpmResultsTableComponent,
    ValidationPanelComponent,
    FileDropzoneComponent,
    SampleSelectorComponent,
    ScheduleStepperComponent,
  ],
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.scss'],
})
export class InputComponent {
  // Store signals
  readonly tasks = activities;
  readonly evm = evmProject;
  readonly risks = riskRegister;
  readonly loading = isLoading;
  readonly cpmResults = cpmResults;

  // Local validation state
  readonly validationErrors = signal<ValidationError[]>([]);

  // Compute stepper steps reactively
  readonly stepperSteps = computed<PmStep[]>(() => {
    const acts = this.tasks();
    const analyzed = cpmResults() !== null;
    const hasTasks = acts.length > 0;
    const hasPredecessors = acts.some((a) => (a.predecessors ?? []).length > 0);
    const hasResources = acts.some((a) => (a.resource_demand ?? 0) > 0);
    const hasDurations = acts.length > 0 && acts.every((a) => a.duration > 0);

    return [
      {
        number: 1,
        label: 'Define Activities',
        state: hasTasks ? 'complete' : 'pending',
        tooltip: 'Enter your project activities in the table below, or load data from a CSV file.',
      },
      {
        number: 2,
        label: 'Sequence Activities',
        state: hasPredecessors ? 'complete' : 'pending',
        tooltip:
          "Set the Predecessors column to define task dependencies (e.g., 'A, B'). The first activity has no predecessors.",
      },
      {
        number: 3,
        label: 'Estimate Resources',
        state: hasResources ? 'complete' : 'optional',
        tooltip:
          'Optional: Set Resource Demand per activity to enable resource-constrained scheduling.',
      },
      {
        number: 4,
        label: 'Estimate Durations',
        state: hasDurations ? 'complete' : 'pending',
        tooltip:
          'Enter a Duration for each activity (CPM) or Optimistic/Most-Likely/Pessimistic estimates (PERT).',
      },
      {
        number: 5,
        label: 'Develop Schedule',
        state: analyzed ? 'complete' : 'pending',
        tooltip:
          'Click ▶ Analyze to calculate the critical path, float values, and project duration.',
      },
    ];
  });

  private readonly cpmService = inject(CpmService);
  private readonly snackBar = inject(MatSnackBar);

  onTasksChange(updated: Activity[]): void {
    activities.set(updated);
  }

  onPeriodsChange(periods: EVMPeriod[]): void {
    const current = this.evm();
    const updated: EVMProject = current
      ? { ...current, periods }
      : {
          project_name: 'My Project',
          bac: 0,
          currency_symbol: '$',
          periods,
          tasks: [],
        };
    evmProject.set(updated);
  }

  onRisksChange(risks: Risk[]): void {
    riskRegister.set(risks);
  }

  onValidationErrors(errors: ValidationError[]): void {
    this.validationErrors.set(errors);
  }

  onFileLoaded(data: Activity[]): void {
    activities.set(data);
  }

  onSampleLoaded(data: {
    activities?: Activity[];
    evm_project?: EVMProject;
    risks?: Risk[];
  }): void {
    if (data.activities) activities.set(data.activities);
    if (data.evm_project) evmProject.set(data.evm_project);
    if (data.risks) riskRegister.set(data.risks);
  }

  analyze(): void {
    const acts = this.tasks();
    if (acts.length === 0) {
      this.snackBar.open('Add at least one activity before analyzing.', 'OK', { duration: 3000 });
      return;
    }
    if (this.validationErrors().length > 0) {
      this.snackBar.open('Fix validation errors before analyzing.', 'OK', { duration: 3000 });
      return;
    }
    isLoading.set(true);
    this.cpmService.analyze(acts).subscribe({
      next: (result) => {
        cpmResults.set(result);
        isLoading.set(false);
        this.snackBar.open(
          `Analysis complete — project duration: ${result.project_duration} periods`,
          'OK',
          { duration: 4000, panelClass: 'snack-success' },
        );
      },
      error: (err: Error) => {
        isLoading.set(false);
        this.snackBar.open(`Analysis failed: ${err.message}`, 'Dismiss', {
          duration: 5000,
          panelClass: 'snack-error',
        });
      },
    });
  }

  onStepperStepClick(step: number): void {
    // Step 5 — trigger analyze
    if (step === 5) {
      this.analyze();
    }
  }
}
