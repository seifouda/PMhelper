import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

type PCategory = 'Political' | 'Economic' | 'Social' | 'Technological' | 'Environmental' | 'Legal';

const ALL_CATEGORIES: PCategory[] = [
  'Political',
  'Economic',
  'Social',
  'Technological',
  'Environmental',
  'Legal',
];

@Component({
  selector: 'app-pestel-factor-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
  ],
  template: `
    <h2 mat-dialog-title>Add PESTEL Factor</h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Category</mat-label>
        <mat-select [(ngModel)]="category" required>
          @for (c of categories; track c) {
            <mat-option [value]="c">{{ c }}</mat-option>
          }
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Description</mat-label>
        <textarea matInput [(ngModel)]="description" rows="3" required></textarea>
      </mat-form-field>

      <div class="score-row">
        <mat-form-field appearance="outline">
          <mat-label>Impact (1–5)</mat-label>
          <mat-select [(ngModel)]="impact">
            @for (n of scores; track n) {
              <mat-option [value]="n">{{ n }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Probability (1–5)</mat-label>
          <mat-select [(ngModel)]="probability">
            @for (n of scores; track n) {
              <mat-option [value]="n">{{ n }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button
        mat-flat-button
        color="primary"
        [disabled]="!category || !description.trim()"
        (click)="save()"
      >
        Add
      </button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .full-width {
        width: 100%;
      }
      mat-dialog-content {
        min-width: 320px;
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .score-row {
        display: flex;
        gap: 12px;
      }
      .score-row mat-form-field {
        flex: 1;
      }
    `,
  ],
})
export class PestelFactorDialogComponent {
  categories = ALL_CATEGORIES;
  scores = [1, 2, 3, 4, 5];
  category: PCategory;
  description = '';
  impact = 3;
  probability = 3;

  constructor(
    private readonly dialogRef: MatDialogRef<PestelFactorDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { defaultCategory: PCategory | null },
  ) {
    this.category = data.defaultCategory ?? 'Political';
  }

  save(): void {
    this.dialogRef.close({
      category: this.category,
      description: this.description.trim(),
      impact_score: this.impact,
      probability_score: this.probability,
    });
  }
}
