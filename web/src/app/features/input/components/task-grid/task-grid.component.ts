import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  OnInit,
  Output,
  SimpleChanges,
  inject,
} from '@angular/core';
import {
  AbstractControl,
  FormArray,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';

import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { CommonModule } from '@angular/common';

import { Activity } from '../../../../core/models/activity.model';

export interface ValidationError {
  row: number;
  field: string;
  message: string;
}

/** Detects cycles in the predecessor DAG using DFS. Returns true if cycle exists. */
function hasCycle(activities: Activity[]): boolean {
  const idSet = new Set(activities.map((a) => a.id));
  const adj = new Map<string, string[]>();
  for (const a of activities) {
    adj.set(
      a.id,
      (a.predecessors ?? []).filter((p) => idSet.has(p)),
    );
  }

  const WHITE = 0,
    GRAY = 1,
    BLACK = 2;
  const color = new Map<string, number>();
  for (const id of idSet) color.set(id, WHITE);

  function dfs(u: string): boolean {
    color.set(u, GRAY);
    for (const v of adj.get(u) ?? []) {
      if (color.get(v) === GRAY) return true;
      if (color.get(v) === WHITE && dfs(v)) return true;
    }
    color.set(u, BLACK);
    return false;
  }

  for (const id of idSet) {
    if (color.get(id) === WHITE && dfs(id)) return true;
  }
  return false;
}

/** Validates that all predecessor IDs in a cell exist in the current ID list. */
function predecessorExistsValidator(allIds: () => string[]): ValidatorFn {
  return (ctrl: AbstractControl) => {
    const raw = ((ctrl.value as string) ?? '').trim();
    if (!raw) return null;
    const parts = raw
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    const ids = allIds();
    const missing = parts.filter((p) => !ids.includes(p));
    if (missing.length > 0) {
      return { unknownPredecessors: missing.join(', ') };
    }
    return null;
  };
}

@Component({
  selector: 'app-task-grid',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatCheckboxModule,
  ],
  templateUrl: './task-grid.component.html',
  styleUrls: ['./task-grid.component.scss'],
})
export class TaskGridComponent implements OnInit, OnChanges, OnDestroy {
  @Input() tasks: Activity[] = [];
  @Output() tasksChange = new EventEmitter<Activity[]>();
  @Output() validationErrors = new EventEmitter<ValidationError[]>();

  private readonly fb = inject(FormBuilder);
  private readonly destroy$ = new Subject<void>();

  form!: FormGroup;

  readonly displayedColumns = [
    'index',
    'id',
    'activity',
    'duration',
    'predecessors',
    'optimistic',
    'most_likely',
    'pessimistic',
    'resource_demand',
    'normal_cost',
    'min_duration',
    'crash_cost',
    'actions',
  ];

  get rowsArray(): FormArray {
    return this.form.get('rows') as FormArray;
  }

  ngOnInit(): void {
    this.form = this.fb.group({ rows: this.fb.array([]) });
    this._populateRows(this.tasks);
    this.rowsArray.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => this._emit());
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['tasks'] && !changes['tasks'].firstChange && this.form) {
      this._populateRows(this.tasks);
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  addRow(): void {
    const nextId = this._nextId();
    this.rowsArray.push(this._buildRow({ id: nextId } as Activity));
  }

  deleteRow(index: number): void {
    this.rowsArray.removeAt(index);
  }

  trackByIndex(index: number): number {
    return index;
  }

  private _populateRows(tasks: Activity[]): void {
    this.rowsArray.clear({ emitEvent: false });
    (tasks ?? []).forEach((t) => this.rowsArray.push(this._buildRow(t), { emitEvent: false }));
  }

  private _buildRow(task: Partial<Activity>): FormGroup {
    const ids = () => this.rowsArray.controls.map((c) => c.get('id')?.value as string);
    return this.fb.group({
      id: [task.id ?? '', [Validators.required, Validators.pattern(/^\S+$/)]],
      activity: [task.activity ?? '', Validators.required],
      duration: [task.duration ?? null, [Validators.min(0)]],
      predecessors: [(task.predecessors ?? []).join(', '), predecessorExistsValidator(ids)],
      optimistic: [task.optimistic ?? null, [Validators.min(0)]],
      most_likely: [task.most_likely ?? null, [Validators.min(0)]],
      pessimistic: [task.pessimistic ?? null, [Validators.min(0)]],
      resource_demand: [task.resource_demand ?? null, [Validators.min(0)]],
      normal_cost: [task.normal_cost ?? null, [Validators.min(0)]],
      min_duration: [task.min_duration ?? null, [Validators.min(0)]],
      crash_cost: [task.crash_cost ?? null, [Validators.min(0)]],
    });
  }

  private _emit(): void {
    const activities = this._toActivities();
    const errors = this._collectErrors(activities);
    this.tasksChange.emit(activities);
    this.validationErrors.emit(errors);
  }

  private _toActivities(): Activity[] {
    return this.rowsArray.controls.map((ctrl) => {
      const v = ctrl.value;
      const preds = ((v.predecessors as string) ?? '')
        .split(',')
        .map((s: string) => s.trim())
        .filter(Boolean);
      return {
        id: v.id,
        activity: v.activity,
        duration: v.duration !== null && v.duration !== '' ? +v.duration : 0,
        predecessors: preds,
        optimistic: v.optimistic !== null && v.optimistic !== '' ? +v.optimistic : undefined,
        most_likely: v.most_likely !== null && v.most_likely !== '' ? +v.most_likely : undefined,
        pessimistic: v.pessimistic !== null && v.pessimistic !== '' ? +v.pessimistic : undefined,
        resource_demand:
          v.resource_demand !== null && v.resource_demand !== '' ? +v.resource_demand : undefined,
        normal_cost: v.normal_cost !== null && v.normal_cost !== '' ? +v.normal_cost : undefined,
        min_duration:
          v.min_duration !== null && v.min_duration !== '' ? +v.min_duration : undefined,
        crash_cost: v.crash_cost !== null && v.crash_cost !== '' ? +v.crash_cost : undefined,
      } as Activity;
    });
  }

  private _collectErrors(activities: Activity[]): ValidationError[] {
    const errors: ValidationError[] = [];
    const seen = new Set<string>();
    const allIds = activities.map((a) => a.id);

    activities.forEach((a, i) => {
      if (!a.id) errors.push({ row: i + 1, field: 'ID', message: 'ID is required.' });
      if (seen.has(a.id))
        errors.push({ row: i + 1, field: 'ID', message: `Duplicate ID "${a.id}".` });
      seen.add(a.id);

      if (!a.activity)
        errors.push({ row: i + 1, field: 'Name', message: 'Activity name is required.' });
      if (a.duration < 0)
        errors.push({ row: i + 1, field: 'Duration', message: 'Duration must be ≥ 0.' });

      (a.predecessors ?? []).forEach((p) => {
        if (!allIds.includes(p)) {
          errors.push({
            row: i + 1,
            field: 'Predecessors',
            message: `Unknown predecessor "${p}".`,
          });
        }
      });
    });

    if (hasCycle(activities.filter((a) => a.id))) {
      errors.push({
        row: 0,
        field: 'Predecessors',
        message: 'Circular dependency detected in predecessor chain.',
      });
    }

    return errors;
  }

  private _nextId(): string {
    const ids = this.rowsArray.controls.map((c) => c.get('id')?.value as string).filter(Boolean);
    // Generate next letter: A, B, C, ... AA, AB, ...
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for (let i = 0; i < 26; i++) {
      if (!ids.includes(alphabet[i])) return alphabet[i];
    }
    for (let i = 0; i < 26; i++) {
      for (let j = 0; j < 26; j++) {
        const id = alphabet[i] + alphabet[j];
        if (!ids.includes(id)) return id;
      }
    }
    return `T${Date.now()}`;
  }
}
