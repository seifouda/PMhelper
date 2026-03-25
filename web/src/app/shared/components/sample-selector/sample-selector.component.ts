import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  OnInit,
  Output,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatListModule } from '@angular/material/list';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ApiService } from '../../../core/services/api.service';
import { SampleProject } from '../../../core/models/project.model';
import { Activity } from '../../../core/models/activity.model';
import { EVMProject } from '../../../core/models/evm.model';
import { Risk } from '../../../core/models/risk.model';
import { academicLevel } from '../../../core/store/project.store';

interface SampleLoadResult {
  activities?: Activity[];
  evm_project?: EVMProject;
  risks?: Risk[];
}

@Component({
  selector: 'app-sample-selector',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatListModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
  template: `
    <button
      mat-stroked-button
      type="button"
      (click)="open()"
      matTooltip="Load a sample project dataset"
    >
      <mat-icon>folder_open</mat-icon>
      Samples
    </button>

    @if (showDialog()) {
      <div class="dialog-overlay" (click)="close()">
        <div
          class="dialog-panel"
          (click)="$event.stopPropagation()"
          role="dialog"
          aria-label="Select sample project"
        >
          <div class="dialog-header">
            <mat-icon>folder_open</mat-icon>
            <h3>Load Sample Project</h3>
            <button mat-icon-button (click)="close()" aria-label="Close dialog">
              <mat-icon>close</mat-icon>
            </button>
          </div>

          @if (loading()) {
            <div class="loading-state">
              <mat-spinner diameter="36"></mat-spinner>
              <span>Loading samples…</span>
            </div>
          } @else {
            <div class="sample-list">
              @for (sample of samples(); track sample.id) {
                <button
                  class="sample-card"
                  [class.loading]="loadingId() === sample.id"
                  (click)="loadSample(sample)"
                  type="button"
                >
                  <div class="sample-card__main">
                    <span class="sample-name">{{ sample.name }}</span>
                    <span class="sample-desc">{{ sample.description }}</span>
                  </div>
                  <div class="sample-card__meta">
                    <mat-chip [color]="sample.level === 'pg' ? 'accent' : 'primary'" highlighted>
                      {{ sample.level.toUpperCase() }}
                    </mat-chip>
                    <span class="task-count">{{ sample.task_count }} tasks</span>
                    @if (loadingId() === sample.id) {
                      <mat-spinner diameter="20"></mat-spinner>
                    }
                  </div>
                </button>
              }
            </div>
          }
        </div>
      </div>
    }
  `,
  styles: [
    `
      .dialog-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.4);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .dialog-panel {
        background: white;
        border-radius: 12px;
        padding: 0;
        min-width: 380px;
        max-width: 480px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        overflow: hidden;
      }
      .dialog-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 16px 20px;
        border-bottom: 1px solid #e2e8f0;
        h3 {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
          flex: 1;
        }
        mat-icon:first-child {
          color: #3b82f6;
        }
      }
      .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 40px;
      }
      .sample-list {
        display: flex;
        flex-direction: column;
        gap: 0;
        max-height: 380px;
        overflow-y: auto;
      }
      .sample-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 14px 20px;
        border: none;
        border-bottom: 1px solid #f1f5f9;
        background: white;
        cursor: pointer;
        text-align: left;
        width: 100%;
        transition: background 0.15s;
        &:hover {
          background: #f8fafc;
        }
        &.loading {
          opacity: 0.6;
          pointer-events: none;
        }
      }
      .sample-card__main {
        display: flex;
        flex-direction: column;
        gap: 3px;
      }
      .sample-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: #1e293b;
      }
      .sample-desc {
        font-size: 0.78rem;
        color: #64748b;
      }
      .sample-card__meta {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .task-count {
        font-size: 0.75rem;
        color: #94a3b8;
        white-space: nowrap;
      }
    `,
  ],
})
export class SampleSelectorComponent implements OnInit {
  @Output() sampleLoaded = new EventEmitter<SampleLoadResult>();

  readonly showDialog = signal(false);
  readonly loading = signal(false);
  readonly loadingId = signal<string | null>(null);
  readonly samples = signal<SampleProject[]>([]);
  readonly level = academicLevel;

  private readonly api = inject(ApiService);

  ngOnInit(): void {
    this._loadList();
  }

  open(): void {
    this.showDialog.set(true);
  }

  close(): void {
    this.showDialog.set(false);
  }

  loadSample(sample: SampleProject): void {
    this.loadingId.set(sample.id);
    this.api.get<SampleLoadResult>(`/samples/${sample.id}`).subscribe({
      next: (data) => {
        this.loadingId.set(null);
        this.showDialog.set(false);
        this.sampleLoaded.emit(data);
      },
      error: () => {
        this.loadingId.set(null);
      },
    });
  }

  private _loadList(): void {
    this.loading.set(true);
    this.api.get<SampleProject[]>('/samples').subscribe({
      next: (list) => {
        this.loading.set(false);
        this.samples.set(list);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }
}
