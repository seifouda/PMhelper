import {
  ApplicationConfig,
  ErrorHandler,
  APP_INITIALIZER,
  inject,
  Injector,
  provideZoneChangeDetection,
} from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

import { routes } from './app.routes';
import { loadingInterceptor } from './core/interceptors/loading.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { GlobalErrorHandler } from './core/global-error-handler';
import { PersistenceService } from './core/services/persistence.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([loadingInterceptor, errorInterceptor])),
    provideAnimationsAsync(),
    { provide: ErrorHandler, useClass: GlobalErrorHandler },
    {
      provide: APP_INITIALIZER,
      useFactory: () => {
        const persistence = inject(PersistenceService);
        const injector = inject(Injector);
        return () => persistence.init(injector);
      },
      multi: true,
    },
  ],
};
