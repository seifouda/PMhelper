import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { EVMProject, EVMKPIs } from '../models/evm.model';
import { CalculationStep } from '../models/step.model';

export interface EVMAnalysisRequest {
  project: EVMProject;
  current_period_index?: number;
}

export interface EVMAnalysisResponse {
  kpis: EVMKPIs;
  period_kpis: Array<{ period: number; kpis: EVMKPIs }>;
}

@Injectable({ providedIn: 'root' })
export class EvmService {
  private readonly api = inject(ApiService);

  analyze(request: EVMAnalysisRequest): Observable<EVMAnalysisResponse> {
    return this.api.post<EVMAnalysisResponse>('/analysis/evm', request);
  }

  getSteps(request: EVMAnalysisRequest): Observable<CalculationStep[]> {
    return this.api.post<CalculationStep[]>('/analysis/steps/evm', request);
  }
}
