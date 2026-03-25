import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Activity } from '../models/activity.model';
import { RCPSResults, SampleProject } from '../models/project.model';

@Injectable({ providedIn: 'root' })
export class RcpsService {
  private readonly api = inject(ApiService);

  analyze(
    activities: Activity[],
    resource_limit: number,
    algorithm: 'burgess' | 'min_moment' = 'burgess',
  ): Observable<RCPSResults> {
    return this.api.post<RCPSResults>('/analysis/rcps', {
      activities,
      resource_limit,
      algorithm,
    });
  }
}

@Injectable({ providedIn: 'root' })
export class SamplesService {
  private readonly api = inject(ApiService);

  list(): Observable<SampleProject[]> {
    return this.api.get<SampleProject[]>('/samples');
  }

  load(id: string): Observable<{ activities: Activity[] }> {
    return this.api.get<{ activities: Activity[] }>(`/samples/${id}`);
  }
}
