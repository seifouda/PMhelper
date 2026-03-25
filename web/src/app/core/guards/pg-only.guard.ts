import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { academicLevel } from '../store/project.store';

export const pgOnlyGuard: CanActivateFn = () => {
  if (academicLevel() === 'pg') return true;

  inject(Router).navigate(['/dashboard']);
  inject(MatSnackBar).open('Switch to PG mode to access this feature.', 'Dismiss', {
    duration: 4000,
    panelClass: 'pm-snack-info',
  });
  return false;
};
