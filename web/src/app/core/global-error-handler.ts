import { ErrorHandler, Injectable, inject, NgZone } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private readonly snackBar = inject(MatSnackBar);
  private readonly zone = inject(NgZone);
  private readonly http = inject(HttpClient);

  handleError(error: unknown): void {
    // Log to console for debugging
    console.error('Unhandled error:', error);

    // Send telemetry (fire-and-forget)
    try {
      const payload = {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      };
      this.http.post('/api/web/telemetry/error', payload).subscribe({
        error: () => {
          /* silently ignore telemetry failures */
        },
      });
    } catch {
      // Telemetry must never throw
    }

    // Show user-facing toast (run inside zone to trigger change detection)
    this.zone.run(() => {
      this.snackBar.open('An unexpected error occurred.', 'Dismiss', {
        duration: 8000,
        panelClass: 'error-snackbar',
      });
    });
  }
}
