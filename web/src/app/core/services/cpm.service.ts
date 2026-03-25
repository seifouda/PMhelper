import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Activity } from '../models/activity.model';
import { CPMResults } from '../models/cpm-result.model';
import { CalculationStep } from '../models/step.model';

@Injectable({ providedIn: 'root' })
export class CpmService {
  private readonly api = inject(ApiService);

  analyze(activities: Activity[]): Observable<CPMResults> {
    return this.api.post<CPMResults>('/analysis/cpm', { activities });
  }

  getSteps(activities: Activity[]): Observable<CalculationStep[]> {
    return this.api.post<CalculationStep[]>('/analysis/steps/cpm', { activities });
  }
}
