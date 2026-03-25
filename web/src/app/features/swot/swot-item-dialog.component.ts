import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'app-swot-item-dialog',
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
    <h2 mat-dialog-title>Add {{ data.quadrant | titlecase }} Item</h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Description</mat-label>
        <textarea matInput [(ngModel)]="text" rows="3" required></textarea>
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="!text.trim()" (click)="save()">
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
        min-width: 280px;
      }
    `,
  ],
})
export class SwotItemDialogComponent {
  text = '';

  constructor(
    private readonly dialogRef: MatDialogRef<SwotItemDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { quadrant: string },
  ) {}

  save(): void {
    this.dialogRef.close({ text: this.text.trim() });
  }
}
