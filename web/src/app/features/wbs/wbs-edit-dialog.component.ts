import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

export interface WbsEditData {
  mode: 'add' | 'edit';
  name?: string;
  cost?: number;
  duration?: number;
  progress?: number;
}

@Component({
  selector: 'app-wbs-edit-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ data.mode === 'add' ? 'Add WBS Node' : 'Edit WBS Node' }}</h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Name</mat-label>
        <input matInput [(ngModel)]="name" required />
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Cost</mat-label>
        <input matInput type="number" [(ngModel)]="cost" [min]="0" />
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Duration (days)</mat-label>
        <input matInput type="number" [(ngModel)]="duration" [min]="0" />
      </mat-form-field>
      @if (data.mode === 'edit') {
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Progress (%)</mat-label>
          <input matInput type="number" [(ngModel)]="progress" [min]="0" [max]="100" />
        </mat-form-field>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="!name.trim()" (click)="save()">
        {{ data.mode === 'add' ? 'Add' : 'Save' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .full-width {
        width: 100%;
      }
      mat-dialog-content {
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 280px;
      }
    `,
  ],
})
export class WbsEditDialogComponent {
  name: string;
  cost: number;
  duration: number;
  progress: number;

  constructor(
    private readonly dialogRef: MatDialogRef<WbsEditDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: WbsEditData,
  ) {
    this.name = data.name ?? '';
    this.cost = data.cost ?? 0;
    this.duration = data.duration ?? 0;
    this.progress = data.progress ?? 0;
  }

  save(): void {
    this.dialogRef.close({
      name: this.name.trim(),
      cost: this.cost,
      duration: this.duration,
      progress: this.progress,
    });
  }
}
