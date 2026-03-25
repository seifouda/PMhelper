import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      const message =
        error.error?.detail ?? error.error?.message ?? `HTTP ${error.status}: ${error.statusText}`;
      snackBar.open(message, 'Dismiss', { duration: 6000, panelClass: 'error-snackbar' });
      return throwError(() => error);
    }),
  );
};
