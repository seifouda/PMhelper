import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { pgOnlyGuard } from './pg-only.guard';
import { academicLevel } from '../store/project.store';

describe('pgOnlyGuard', () => {
  let router: jasmine.SpyObj<Router>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

  beforeEach(() => {
    router = jasmine.createSpyObj('Router', ['navigate']);
    snackBar = jasmine.createSpyObj('MatSnackBar', ['open']);

    TestBed.configureTestingModule({
      providers: [
        { provide: Router, useValue: router },
        { provide: MatSnackBar, useValue: snackBar },
      ],
    });
  });

  afterEach(() => academicLevel.set('ug'));

  it('should allow PG users', () => {
    academicLevel.set('pg');
    const result = TestBed.runInInjectionContext(() => pgOnlyGuard({} as any, {} as any));
    expect(result).toBeTrue();
  });

  it('should block UG users and redirect to dashboard', () => {
    academicLevel.set('ug');
    const result = TestBed.runInInjectionContext(() => pgOnlyGuard({} as any, {} as any));
    expect(result).toBeFalse();
    expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
  });

  it('should show snackbar when blocking UG users', () => {
    academicLevel.set('ug');
    TestBed.runInInjectionContext(() => pgOnlyGuard({} as any, {} as any));
    expect(snackBar.open).toHaveBeenCalledWith(
      'Switch to PG mode to access this feature.',
      'Dismiss',
      jasmine.objectContaining({ duration: 4000 }),
    );
  });
});
