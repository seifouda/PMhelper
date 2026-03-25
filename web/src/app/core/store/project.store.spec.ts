import {
  viewMode,
  academicLevel,
  isLoading,
  selectedTaskId,
  projectName,
  activities,
  evmProject,
  riskRegister,
  wbsNodes,
  swotAnalysis,
  pestelAnalysis,
  cpmResults,
  pertResults,
  evmKpis,
  crashingResults,
  rcpsResults,
  monteCarloResults,
  criticalPath,
  projectDuration,
  isAnalyzed,
  pgVisible,
  taskCount,
  criticalCount,
  resetProject,
  clearResults,
} from './project.store';
import { CPMResults } from '../models/cpm-result.model';

describe('ProjectStore', () => {
  beforeEach(() => resetProject());

  // ── Default values ──────────────────────────────────────────────────────

  it('should have default project name', () => {
    expect(projectName()).toBe('Untitled Project');
  });

  it('should default to learn mode / ug level', () => {
    expect(viewMode()).toBe('learn');
    expect(academicLevel()).toBe('ug');
  });

  it('should default activities to empty', () => {
    expect(activities()).toEqual([]);
    expect(taskCount()).toBe(0);
  });

  it('should default analysis results to null', () => {
    expect(cpmResults()).toBeNull();
    expect(pertResults()).toBeNull();
    expect(evmKpis()).toBeNull();
    expect(crashingResults()).toBeNull();
    expect(rcpsResults()).toBeNull();
    expect(monteCarloResults()).toBeNull();
  });

  // ── Computed signals ────────────────────────────────────────────────────

  it('criticalPath should be empty when no results', () => {
    expect(criticalPath()).toEqual([]);
  });

  it('projectDuration should be 0 when no results', () => {
    expect(projectDuration()).toBe(0);
  });

  it('isAnalyzed should be false initially', () => {
    expect(isAnalyzed()).toBeFalse();
  });

  it('pgVisible should reflect academicLevel', () => {
    expect(pgVisible()).toBeFalse();
    academicLevel.set('pg');
    expect(pgVisible()).toBeTrue();
  });

  it('taskCount should reflect activities length', () => {
    activities.set([
      { id: 'A', activity: 'Task A', duration: 3, predecessors: [] },
      { id: 'B', activity: 'Task B', duration: 5, predecessors: ['A'] },
    ]);
    expect(taskCount()).toBe(2);
  });

  it('criticalCount should reflect critical_activities length', () => {
    cpmResults.set({
      project_duration: 10,
      critical_paths: [['A', 'B']],
      critical_activities: ['A', 'B'],
      nodes: [],
      edges: [],
    } as CPMResults);
    expect(criticalCount()).toBe(2);
  });

  it('isAnalyzed should be true after setting cpmResults', () => {
    cpmResults.set({
      project_duration: 5,
      critical_paths: [],
      critical_activities: [],
      nodes: [],
      edges: [],
    } as CPMResults);
    expect(isAnalyzed()).toBeTrue();
  });

  // ── clearResults ────────────────────────────────────────────────────────

  it('clearResults should null all analysis signals', () => {
    cpmResults.set({
      project_duration: 1,
      critical_paths: [],
      critical_activities: [],
      nodes: [],
      edges: [],
    } as CPMResults);
    selectedTaskId.set('A');
    clearResults();

    expect(cpmResults()).toBeNull();
    expect(pertResults()).toBeNull();
    expect(evmKpis()).toBeNull();
    expect(crashingResults()).toBeNull();
    expect(rcpsResults()).toBeNull();
    expect(monteCarloResults()).toBeNull();
    expect(selectedTaskId()).toBeNull();
  });

  // ── resetProject ────────────────────────────────────────────────────────

  it('resetProject should restore all defaults', () => {
    projectName.set('My Project');
    activities.set([{ id: 'A', activity: 'A', duration: 1, predecessors: [] }]);
    riskRegister.set([{ id: '1' } as any]);
    wbsNodes.set([{ id: '1' } as any]);
    swotAnalysis.set({ strengths: [] } as any);
    pestelAnalysis.set({ political: [] } as any);
    evmProject.set({ tasks: [] } as any);
    cpmResults.set({
      project_duration: 1,
      critical_paths: [],
      critical_activities: [],
      nodes: [],
      edges: [],
    } as CPMResults);

    resetProject();

    expect(projectName()).toBe('Untitled Project');
    expect(activities()).toEqual([]);
    expect(riskRegister()).toEqual([]);
    expect(wbsNodes()).toEqual([]);
    expect(swotAnalysis()).toBeNull();
    expect(pestelAnalysis()).toBeNull();
    expect(evmProject()).toBeNull();
    expect(cpmResults()).toBeNull();
  });
});
