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
import { CommonModule } from '@angular/common';
import { FormArray, FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { EVMPeriod } from '../../../../core/models/evm.model';

@Component({
  selector: 'app-evm-period-grid',
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
  ],
  template: `
    <div class="evm-grid-wrapper">
      <div class="grid-toolbar">
        <button mat-stroked-button color="primary" (click)="addPeriod()" type="button">
          <mat-icon>add</mat-icon> Add Period
        </button>
        <span class="row-count"
          >{{ rowsArray.length }} period{{ rowsArray.length !== 1 ? 's' : '' }}</span
        >
      </div>

      <div class="table-scroll-container">
        <form [formGroup]="form">
          <table mat-table [dataSource]="rowsArray.controls" formArrayName="rows" class="evm-table">
            <ng-container matColumnDef="index">
              <th mat-header-cell *matHeaderCellDef class="col-num">#</th>
              <td mat-cell *matCellDef="let r; let i = index" class="col-num">{{ i + 1 }}</td>
            </ng-container>

            <ng-container matColumnDef="label">
              <th mat-header-cell *matHeaderCellDef>Period Label</th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field">
                  <input matInput formControlName="label" placeholder="e.g. Week 1" />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="pv">
              <th mat-header-cell *matHeaderCellDef>
                PV (Cumulative)
                <mat-icon
                  class="help-icon"
                  matTooltip="Planned Value — budgeted work scheduled to be done by this period"
                  >help_outline</mat-icon
                >
              </th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--num">
                  <input
                    matInput
                    type="number"
                    min="0"
                    formControlName="pv_cumulative"
                    placeholder="0"
                  />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="ev">
              <th mat-header-cell *matHeaderCellDef>
                EV (Cumulative)
                <mat-icon
                  class="help-icon"
                  matTooltip="Earned Value — budgeted value of work actually performed"
                  >help_outline</mat-icon
                >
              </th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--num">
                  <input
                    matInput
                    type="number"
                    min="0"
                    formControlName="ev_cumulative"
                    placeholder="0"
                  />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="ac">
              <th mat-header-cell *matHeaderCellDef>
                AC (Cumulative)
                <mat-icon
                  class="help-icon"
                  matTooltip="Actual Cost — money actually spent by this period"
                  >help_outline</mat-icon
                >
              </th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--num">
                  <input
                    matInput
                    type="number"
                    min="0"
                    formControlName="ac_cumulative"
                    placeholder="0"
                  />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let r; let i = index">
                <button
                  mat-icon-button
                  color="warn"
                  (click)="deletePeriod(i)"
                  type="button"
                  matTooltip="Delete period"
                >
                  <mat-icon>delete_outline</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="cols; sticky: true"></tr>
            <tr mat-row *matRowDef="let r; columns: cols"></tr>

            <tr class="mat-row" *matNoDataRow>
              <td [attr.colspan]="cols.length" class="empty-message">
                No periods yet — click <strong>Add Period</strong> to start.
              </td>
            </tr>
          </table>
        </form>
      </div>
    </div>
  `,
  styles: [
    `
      .evm-grid-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
        gap: 8px;
      }
      .grid-toolbar {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .row-count {
        font-size: 0.8rem;
        color: #6b7280;
      }
      .table-scroll-container {
        flex: 1;
        overflow: auto;
        border: 1px solid rgba(0, 0, 0, 0.12);
        border-radius: 8px;
      }
      .evm-table {
        width: 100%;
      }
      th.mat-mdc-header-cell {
        background: #f8fafc;
        font-weight: 600;
        font-size: 0.78rem;
        padding: 6px 8px;
      }
      td.mat-mdc-cell {
        padding: 2px 8px;
      }
      .col-num {
        width: 40px;
        text-align: center;
        color: #94a3b8;
        font-size: 0.75rem;
      }
      .help-icon {
        font-size: 14px;
        width: 14px;
        height: 14px;
        vertical-align: middle;
        color: #94a3b8;
        margin-left: 3px;
      }
      .cell-field {
        width: 100%;
      }
      .cell-field ::ng-deep .mat-mdc-form-field-subscript-wrapper {
        display: none;
      }
      .cell-field ::ng-deep .mat-mdc-form-field-infix {
        padding-top: 8px;
        padding-bottom: 6px;
        min-height: 36px;
      }
      .cell-field--num {
        max-width: 120px;
      }
      .empty-message {
        text-align: center;
        padding: 32px;
        color: #94a3b8;
      }
    `,
  ],
})
export class EvmPeriodGridComponent implements OnInit, OnChanges, OnDestroy {
  @Input() periods: EVMPeriod[] = [];
  @Output() periodsChange = new EventEmitter<EVMPeriod[]>();

  private readonly fb = inject(FormBuilder);
  private readonly destroy$ = new Subject<void>();

  form!: FormGroup;
  readonly cols = ['index', 'label', 'pv', 'ev', 'ac', 'actions'];

  get rowsArray(): FormArray {
    return this.form.get('rows') as FormArray;
  }

  ngOnInit(): void {
    this.form = this.fb.group({ rows: this.fb.array([]) });
    this._populate(this.periods);
    this.rowsArray.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => this._emit());
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['periods'] && !changes['periods'].firstChange && this.form) {
      this._populate(this.periods);
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  addPeriod(): void {
    const idx = this.rowsArray.length + 1;
    this.rowsArray.push(
      this.fb.group({
        index: [idx],
        label: [`Period ${idx}`],
        pv_cumulative: [null, Validators.min(0)],
        ev_cumulative: [null, Validators.min(0)],
        ac_cumulative: [null, Validators.min(0)],
      }),
    );
  }

  deletePeriod(i: number): void {
    this.rowsArray.removeAt(i);
  }

  private _populate(periods: EVMPeriod[]): void {
    this.rowsArray.clear({ emitEvent: false });
    (periods ?? []).forEach((p) =>
      this.rowsArray.push(
        this.fb.group({
          index: [p.index],
          label: [p.label ?? ''],
          pv_cumulative: [p.pv_cumulative, Validators.min(0)],
          ev_cumulative: [p.ev_cumulative, Validators.min(0)],
          ac_cumulative: [p.ac_cumulative, Validators.min(0)],
        }),
        { emitEvent: false },
      ),
    );
  }

  private _emit(): void {
    const ps: EVMPeriod[] = this.rowsArray.controls.map((c, i) => ({
      index: i + 1,
      label: c.get('label')?.value ?? `Period ${i + 1}`,
      pv_cumulative: +(c.get('pv_cumulative')?.value ?? 0),
      ev_cumulative: +(c.get('ev_cumulative')?.value ?? 0),
      ac_cumulative: +(c.get('ac_cumulative')?.value ?? 0),
    }));
    this.periodsChange.emit(ps);
  }
}
