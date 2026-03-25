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
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { Risk, RiskCategory } from '../../../../core/models/risk.model';

@Component({
  selector: 'app-risk-entry',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
  ],
  template: `
    <div class="risk-wrapper">
      <div class="grid-toolbar">
        <button mat-stroked-button color="primary" (click)="addRisk()" type="button">
          <mat-icon>add</mat-icon> Add Risk
        </button>
        <span class="row-count"
          >{{ rowsArray.length }} risk{{ rowsArray.length !== 1 ? 's' : '' }}</span
        >
      </div>

      <div class="table-scroll-container">
        <form [formGroup]="form">
          <table
            mat-table
            [dataSource]="rowsArray.controls"
            formArrayName="rows"
            class="risk-table"
          >
            <ng-container matColumnDef="index">
              <th mat-header-cell *matHeaderCellDef class="col-num">#</th>
              <td mat-cell *matCellDef="let r; let i = index" class="col-num">{{ i + 1 }}</td>
            </ng-container>

            <ng-container matColumnDef="id">
              <th mat-header-cell *matHeaderCellDef>ID</th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--sm">
                  <input matInput formControlName="id" placeholder="R1" />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Risk Name</th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--wide">
                  <input matInput formControlName="name" placeholder="Budget overrun" />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="category">
              <th mat-header-cell *matHeaderCellDef>Category</th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--cat">
                  <mat-select formControlName="category">
                    @for (cat of categories; track cat) {
                      <mat-option [value]="cat">{{ cat }}</mat-option>
                    }
                  </mat-select>
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="probability">
              <th mat-header-cell *matHeaderCellDef>
                Probability
                <mat-icon class="help-icon" matTooltip="0.0 – 1.0 (e.g., 0.3 = 30%)"
                  >help_outline</mat-icon
                >
              </th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--num">
                  <input
                    matInput
                    type="number"
                    min="0"
                    max="1"
                    step="0.05"
                    formControlName="probability"
                    placeholder="0.3"
                  />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="impact">
              <th mat-header-cell *matHeaderCellDef>
                Impact ($)
                <mat-icon class="help-icon" matTooltip="Financial impact if risk occurs"
                  >help_outline</mat-icon
                >
              </th>
              <td mat-cell *matCellDef="let r; let i = index" [formGroupName]="i">
                <mat-form-field appearance="outline" class="cell-field cell-field--num">
                  <input
                    matInput
                    type="number"
                    min="0"
                    formControlName="impact"
                    placeholder="50000"
                  />
                </mat-form-field>
              </td>
            </ng-container>

            <ng-container matColumnDef="exposure">
              <th mat-header-cell *matHeaderCellDef>
                Exposure
                <mat-icon class="help-icon" matTooltip="= Probability × Impact (auto-calculated)"
                  >help_outline</mat-icon
                >
              </th>
              <td
                mat-cell
                *matCellDef="let r; let i = index"
                [formGroupName]="i"
                class="exposure-cell"
              >
                {{ computeExposure(i) | number: '1.0-0' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let r; let i = index">
                <button mat-icon-button color="warn" (click)="deleteRisk(i)" type="button">
                  <mat-icon>delete_outline</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="cols; sticky: true"></tr>
            <tr mat-row *matRowDef="let r; columns: cols"></tr>
            <tr class="mat-row" *matNoDataRow>
              <td [attr.colspan]="cols.length" class="empty-message">
                No risks yet — click <strong>Add Risk</strong> to begin.
              </td>
            </tr>
          </table>
        </form>
      </div>
    </div>
  `,
  styles: [
    `
      .risk-wrapper {
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
      .risk-table {
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
      .cell-field--sm {
        max-width: 70px;
      }
      .cell-field--wide {
        min-width: 200px;
      }
      .cell-field--num {
        max-width: 100px;
      }
      .cell-field--cat {
        min-width: 120px;
      }
      .exposure-cell {
        font-weight: 600;
        color: #7c3aed;
        font-size: 0.9rem;
      }
      .empty-message {
        text-align: center;
        padding: 32px;
        color: #94a3b8;
      }
    `,
  ],
})
export class RiskEntryComponent implements OnInit, OnChanges, OnDestroy {
  @Input() risks: Risk[] = [];
  @Output() risksChange = new EventEmitter<Risk[]>();

  private readonly fb = inject(FormBuilder);
  private readonly destroy$ = new Subject<void>();

  form!: FormGroup;
  readonly cols = [
    'index',
    'id',
    'name',
    'category',
    'probability',
    'impact',
    'exposure',
    'actions',
  ];
  readonly categories: RiskCategory[] = ['Schedule', 'Cost', 'Quality', 'Scope', 'Other'];

  get rowsArray(): FormArray {
    return this.form.get('rows') as FormArray;
  }

  ngOnInit(): void {
    this.form = this.fb.group({ rows: this.fb.array([]) });
    this._populate(this.risks);
    this.rowsArray.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => this._emit());
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['risks'] && !changes['risks'].firstChange && this.form) this._populate(this.risks);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  addRisk(): void {
    const idx = this.rowsArray.length + 1;
    this.rowsArray.push(
      this.fb.group({
        id: [`R${idx}`, Validators.required],
        name: ['', Validators.required],
        category: ['Cost'],
        probability: [0.3, [Validators.min(0), Validators.max(1)]],
        impact: [0, Validators.min(0)],
      }),
    );
  }

  deleteRisk(i: number): void {
    this.rowsArray.removeAt(i);
  }

  computeExposure(i: number): number {
    const ctrl = this.rowsArray.at(i);
    return +(ctrl.get('probability')?.value ?? 0) * +(ctrl.get('impact')?.value ?? 0);
  }

  private _populate(risks: Risk[]): void {
    this.rowsArray.clear({ emitEvent: false });
    (risks ?? []).forEach((r) =>
      this.rowsArray.push(
        this.fb.group({
          id: [r.id, Validators.required],
          name: [r.name, Validators.required],
          category: [r.category ?? 'Cost'],
          probability: [r.probability, [Validators.min(0), Validators.max(1)]],
          impact: [r.impact, Validators.min(0)],
        }),
        { emitEvent: false },
      ),
    );
  }

  private _emit(): void {
    const risks: Risk[] = this.rowsArray.controls.map((c) => ({
      id: c.get('id')?.value,
      name: c.get('name')?.value,
      description: '',
      category: c.get('category')?.value,
      probability: +(c.get('probability')?.value ?? 0),
      impact: +(c.get('impact')?.value ?? 0),
      exposure: +(c.get('probability')?.value ?? 0) * +(c.get('impact')?.value ?? 0),
    }));
    this.risksChange.emit(risks);
  }
}
