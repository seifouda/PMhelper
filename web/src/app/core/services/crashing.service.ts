import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Activity } from '../models/activity.model';
import { CrashingResults } from '../models/project.model';

export interface CrashingRequest {
  activities: Activity[];
  indirect_cost_rate?: number;
}

@Injectable({ providedIn: 'root' })
export class CrashingService {
  private readonly api = inject(ApiService);

  analyze(request: CrashingRequest): Observable<CrashingResults> {
    return this.api.post<CrashingResults>('/analysis/crashing', request);
  }
}
