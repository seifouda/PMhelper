import { HttpInterceptorFn } from '@angular/common/http';
import { finalize } from 'rxjs';
import { isLoading } from '../store/project.store';

let activeRequests = 0;

export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  activeRequests++;
  if (activeRequests === 1) {
    isLoading.set(true);
  }

  return next(req).pipe(
    finalize(() => {
      activeRequests--;
      if (activeRequests === 0) {
        isLoading.set(false);
      }
    }),
  );
};
