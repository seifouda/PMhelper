import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { CpmService } from './cpm.service';
import { Activity } from '../models/activity.model';
import { CPMResults } from '../models/cpm-result.model';
import { CalculationStep } from '../models/step.model';
import { environment } from '../../../environments/environment';

describe('CpmService', () => {
  let service: CpmService;
  let httpMock: HttpTestingController;

  const sampleActivities: Activity[] = [
    { id: 'A', activity: 'Design', duration: 3, predecessors: [] },
    { id: 'B', activity: 'Build', duration: 5, predecessors: ['A'] },
  ];

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(CpmService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('analyze() should POST activities and return CPMResults', () => {
    const mockResults: CPMResults = {
      project_duration: 8,
      critical_paths: [['A', 'B']],
      critical_activities: ['A', 'B'],
      nodes: [],
      edges: [],
    };

    service.analyze(sampleActivities).subscribe((result) => {
      expect(result.project_duration).toBe(8);
      expect(result.critical_activities).toEqual(['A', 'B']);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/analysis/cpm`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ activities: sampleActivities });
    req.flush(mockResults);
  });

  it('getSteps() should POST activities and return steps', () => {
    const mockSteps: CalculationStep[] = [
      {
        title: 'Forward Pass',
        formula: 'ES_j = max(EF_i)',
        substitution: 'ES_B = max(EF_A) = max(3)',
        result: 'ES_B = 3',
        explanation: 'Earliest start of B',
      },
    ];

    service.getSteps(sampleActivities).subscribe((steps) => {
      expect(steps.length).toBe(1);
      expect(steps[0].title).toBe('Forward Pass');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/analysis/steps/cpm`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ activities: sampleActivities });
    req.flush(mockSteps);
  });
});
