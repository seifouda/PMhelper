import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Output,
  ViewChild,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ApiService } from '../../../core/services/api.service';
import { Activity } from '../../../core/models/activity.model';

interface ImportResponse {
  activities: Activity[];
  errors: string[];
  row_count: number;
}

@Component({
  selector: 'app-file-dropzone',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
  template: `
    <div
      class="dropzone"
      [class.drag-over]="isDragging()"
      [class.loading]="isLoading()"
      (dragenter)="onDragEnter($event)"
      (dragover)="onDragOver($event)"
      (dragleave)="onDragLeave($event)"
      (drop)="onDrop($event)"
      matTooltip="Drag a CSV file here, or click Browse to select"
    >
      @if (isLoading()) {
        <mat-spinner diameter="24"></mat-spinner>
        <span class="dropzone-text">Importing…</span>
      } @else {
        <mat-icon class="dropzone-icon">upload_file</mat-icon>
        <span class="dropzone-text">Import CSV</span>
        <button mat-stroked-button type="button" (click)="fileInput.click()">Browse</button>
      }
    </div>
    <input
      #fileInput
      type="file"
      accept=".csv,.xlsx,.xls"
      style="display:none"
      (change)="onFileSelected($event)"
    />
  `,
  styles: [
    `
      .dropzone {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border: 1.5px dashed #94a3b8;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        background: white;
        min-width: 170px;

        &.drag-over {
          border-color: #3b82f6;
          background: #eff6ff;
        }
        &.loading {
          opacity: 0.7;
          pointer-events: none;
        }
      }
      .dropzone-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
        color: #64748b;
      }
      .dropzone-text {
        font-size: 0.82rem;
        color: #64748b;
        flex: 1;
      }
    `,
  ],
})
export class FileDropzoneComponent {
  @Output() fileLoaded = new EventEmitter<Activity[]>();
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  readonly isDragging = signal(false);
  readonly isLoading = signal(false);

  private readonly api = inject(ApiService);
  private readonly snackBar = inject(MatSnackBar);

  onDragEnter(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(true);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  onDragLeave(event: DragEvent): void {
    this.isDragging.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) this._upload(file);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) this._upload(file);
    input.value = '';
  }

  private _upload(file: File): void {
    const formData = new FormData();
    formData.append('file', file);
    this.isLoading.set(true);
    this.api.postForm<ImportResponse>('/import/csv', formData).subscribe({
      next: (result) => {
        this.isLoading.set(false);
        if (result.errors?.length > 0) {
          this.snackBar.open(
            `Imported ${result.row_count} rows with ${result.errors.length} warnings.`,
            'OK',
            { duration: 4000 },
          );
        } else {
          this.snackBar.open(`Imported ${result.activities.length} activities.`, 'OK', {
            duration: 3000,
          });
        }
        this.fileLoaded.emit(result.activities);
      },
      error: (err: Error) => {
        this.isLoading.set(false);
        this.snackBar.open(`Import failed: ${err.message}`, 'Dismiss', { duration: 5000 });
      },
    });
  }
}
