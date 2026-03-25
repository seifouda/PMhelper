import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { ApiService } from './api.service';
import { environment } from '../../../environments/environment';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  // ── GET ────────────────────────────────────────────────────────────────

  it('get() should issue GET and return data', () => {
    const mockData = [{ id: 'sample1' }];
    service.get<any[]>('/samples').subscribe((data) => {
      expect(data).toEqual(mockData);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/samples`);
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  // ── POST ───────────────────────────────────────────────────────────────

  it('post() should issue POST with JSON body', () => {
    const body = { activities: [{ id: 'A' }] };
    const mockResult = { project_duration: 10 };

    service.post<any>('/analysis/cpm', body).subscribe((data) => {
      expect(data).toEqual(mockResult);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/analysis/cpm`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(body);
    req.flush(mockResult);
  });

  // ── POST Form ──────────────────────────────────────────────────────────

  it('postForm() should issue POST with FormData', () => {
    const formData = new FormData();
    formData.append('file', new Blob(['a,b,c']), 'test.csv');

    service.postForm<any>('/import/csv', formData).subscribe((data) => {
      expect(data).toEqual({ activities: [] });
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/import/csv`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toBe(formData);
    req.flush({ activities: [] });
  });

  // ── Error handling ─────────────────────────────────────────────────────

  it('should extract detail from error response', () => {
    service.get('/bad').subscribe({
      next: () => fail('should error'),
      error: (err: Error) => {
        expect(err.message).toBe('Not found');
      },
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/bad`);
    req.flush({ detail: 'Not found' }, { status: 404, statusText: 'Not Found' });
  });

  it('should extract message from error response', () => {
    service.get('/fail').subscribe({
      next: () => fail('should error'),
      error: (err: Error) => {
        expect(err.message).toBe('Server error');
      },
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/fail`);
    req.flush({ message: 'Server error' }, { status: 500, statusText: 'Internal Server Error' });
  });

  it('should fall back to HTTP status on generic error', () => {
    service.get('/timeout').subscribe({
      next: () => fail('should error'),
      error: (err: Error) => {
        expect(err.message).toContain('504');
      },
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/timeout`);
    req.flush(null, { status: 504, statusText: 'Gateway Timeout' });
  });
});
