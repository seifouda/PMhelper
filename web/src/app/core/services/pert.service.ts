import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Activity } from '../models/activity.model';
import { PERTResults } from '../models/pert-result.model';
import { CalculationStep } from '../models/step.model';

@Injectable({ providedIn: 'root' })
export class PertService {
  private readonly api = inject(ApiService);

  analyze(activities: Activity[], target_duration?: number): Observable<PERTResults> {
    return this.api.post<PERTResults>('/analysis/pert', { activities, target_duration });
  }

  getSteps(activities: Activity[]): Observable<CalculationStep[]> {
    return this.api.post<CalculationStep[]>('/analysis/steps/pert', { activities });
  }
}
