import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Risk, RiskResults } from '../models/risk.model';

@Injectable({ providedIn: 'root' })
export class RiskService {
  private readonly api = inject(ApiService);

  analyze(risks: Risk[]): Observable<RiskResults> {
    return this.api.post<RiskResults>('/analysis/risk', { risks });
  }
}
