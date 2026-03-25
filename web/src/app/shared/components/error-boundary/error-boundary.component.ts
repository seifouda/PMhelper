import { Component, ErrorHandler, Injectable, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

/**
 * Lightweight error boundary: catches errors in child component tree
 * and shows a recovery UI instead of a blank screen.
 */
@Component({
  selector: 'app-error-boundary',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    @if (hasError()) {
      <div class="error-boundary">
        <mat-icon class="error-boundary__icon">warning</mat-icon>
        <h3>Something went wrong</h3>
        <p class="error-boundary__message">{{ errorMessage() }}</p>
        <button mat-flat-button color="primary" (click)="retry()">
          <mat-icon>refresh</mat-icon>
          Retry
        </button>
      </div>
    } @else {
      <ng-content></ng-content>
    }
  `,
  styles: [
    `
      .error-boundary {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 48px 24px;
        text-align: center;
        color: #546e7a;
        min-height: 300px;
      }
      .error-boundary__icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        color: #f57c00;
      }
      .error-boundary__message {
        font-size: 14px;
        color: #78909c;
        max-width: 400px;
      }
    `,
  ],
})
export class ErrorBoundaryComponent {
  readonly hasError = signal(false);
  readonly errorMessage = signal('An unexpected error occurred in this view.');

  catchError(error: Error): void {
    this.hasError.set(true);
    this.errorMessage.set(error.message || 'An unexpected error occurred in this view.');
  }

  retry(): void {
    this.hasError.set(false);
  }
}
