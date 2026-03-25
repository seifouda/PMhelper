import { signal, computed } from '@angular/core';
import { Activity } from '../models/activity.model';
import { CPMResults } from '../models/cpm-result.model';
import { PERTResults } from '../models/pert-result.model';
import { EVMProject, EVMKPIs } from '../models/evm.model';
import { Risk } from '../models/risk.model';
import { MCResults } from '../models/monte-carlo.model';
import {
  WBSNode,
  SWOTAnalysis,
  PESTELAnalysis,
  CrashingResults,
  RCPSResults,
} from '../models/project.model';

// ── UI State ─────────────────────────────────────────────────────────────────
export const viewMode = signal<'learn' | 'clean'>('learn');
export const academicLevel = signal<'ug' | 'pg'>('ug');
export const isLoading = signal(false);
export const selectedTaskId = signal<string | null>(null);

// ── Project Data ──────────────────────────────────────────────────────────────
export const projectName = signal<string>('Untitled Project');
export const activities = signal<Activity[]>([]);
export const evmProject = signal<EVMProject | null>(null);
export const riskRegister = signal<Risk[]>([]);
export const wbsNodes = signal<WBSNode[]>([]);
export const swotAnalysis = signal<SWOTAnalysis | null>(null);
export const pestelAnalysis = signal<PESTELAnalysis | null>(null);

// ── Analysis Results ──────────────────────────────────────────────────────────
export const cpmResults = signal<CPMResults | null>(null);
export const pertResults = signal<PERTResults | null>(null);
export const evmKpis = signal<EVMKPIs | null>(null);
export const crashingResults = signal<CrashingResults | null>(null);
export const rcpsResults = signal<RCPSResults | null>(null);
export const monteCarloResults = signal<MCResults | null>(null);

// ── Derived (Computed) ────────────────────────────────────────────────────────
export const criticalPath = computed(() => cpmResults()?.critical_paths?.[0] ?? []);
export const projectDuration = computed(() => cpmResults()?.project_duration ?? 0);
export const isAnalyzed = computed(() => cpmResults() !== null);
export const pgVisible = computed(() => academicLevel() === 'pg');
export const taskCount = computed(() => activities().length);
export const criticalCount = computed(() => cpmResults()?.critical_activities?.length ?? 0);

// ── Reset ─────────────────────────────────────────────────────────────────────
export function resetProject(): void {
  projectName.set('Untitled Project');
  activities.set([]);
  evmProject.set(null);
  riskRegister.set([]);
  wbsNodes.set([]);
  swotAnalysis.set(null);
  pestelAnalysis.set(null);
  viewMode.set('learn');
  academicLevel.set('ug');
  clearResults();
}

export function clearResults(): void {
  cpmResults.set(null);
  pertResults.set(null);
  evmKpis.set(null);
  crashingResults.set(null);
  rcpsResults.set(null);
  monteCarloResults.set(null);
  selectedTaskId.set(null);
}
