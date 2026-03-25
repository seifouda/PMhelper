import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Activity } from '../models/activity.model';
import { MCResults } from '../models/monte-carlo.model';

export interface MCConfig {
  n_trials?: number;
  seed?: number;
  cost_min_factor?: number;
  cost_max_factor?: number;
}

@Injectable({ providedIn: 'root' })
export class MonteCarloService {
  private readonly api = inject(ApiService);

  run(activities: Activity[], config: MCConfig = {}): Observable<MCResults> {
    return this.api.post<MCResults>('/analysis/monte-carlo', { activities, ...config });
  }
}
