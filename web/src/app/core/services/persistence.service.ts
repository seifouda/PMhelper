import { Injectable, effect, Injector, runInInjectionContext } from '@angular/core';
import {
  activities,
  projectName,
  evmProject,
  riskRegister,
  viewMode,
  academicLevel,
  wbsNodes,
  swotAnalysis,
  pestelAnalysis,
  cpmResults,
  pertResults,
  evmKpis,
  crashingResults,
  rcpsResults,
  monteCarloResults,
  selectedTaskId,
  resetProject,
} from '../store/project.store';

const STORAGE_KEY = 'pmhelper-edu-state';
const DEBOUNCE_MS = 1000;

interface PersistedState {
  projectName: string;
  activities: unknown[];
  evmProject: unknown | null;
  riskRegister: unknown[];
  viewMode: 'learn' | 'clean';
  academicLevel: 'ug' | 'pg';
  wbsNodes: unknown[];
  swotAnalysis: unknown | null;
  pestelAnalysis: unknown | null;
}

@Injectable({ providedIn: 'root' })
export class PersistenceService {
  private debounceTimer: ReturnType<typeof setTimeout> | null = null;

  init(injector: Injector): void {
    this.restoreState();

    runInInjectionContext(injector, () => {
      effect(() => {
        // Read all signals we want to persist (this registers them as dependencies)
        const state: PersistedState = {
          projectName: projectName(),
          activities: activities(),
          evmProject: evmProject(),
          riskRegister: riskRegister(),
          viewMode: viewMode(),
          academicLevel: academicLevel(),
          wbsNodes: wbsNodes(),
          swotAnalysis: swotAnalysis(),
          pestelAnalysis: pestelAnalysis(),
        };
        this.debouncedSave(state);
      });
    });
  }

  private debouncedSave(state: PersistedState): void {
    if (this.debounceTimer !== null) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch {
        // Storage full or unavailable — silently ignore
      }
    }, DEBOUNCE_MS);
  }

  private restoreState(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const state: PersistedState = JSON.parse(raw);

      if (state.projectName) projectName.set(state.projectName);
      if (Array.isArray(state.activities) && state.activities.length > 0) {
        activities.set(state.activities as any);
      }
      if (state.evmProject) evmProject.set(state.evmProject as any);
      if (Array.isArray(state.riskRegister)) riskRegister.set(state.riskRegister as any);
      if (state.viewMode === 'learn' || state.viewMode === 'clean') viewMode.set(state.viewMode);
      if (state.academicLevel === 'ug' || state.academicLevel === 'pg')
        academicLevel.set(state.academicLevel);
      if (Array.isArray(state.wbsNodes)) wbsNodes.set(state.wbsNodes as any);
      if (state.swotAnalysis) swotAnalysis.set(state.swotAnalysis as any);
      if (state.pestelAnalysis) pestelAnalysis.set(state.pestelAnalysis as any);
    } catch {
      // Corrupt data — ignore and start fresh
    }
  }

  clearPersistedState(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore
    }
    resetProject();
  }
}
