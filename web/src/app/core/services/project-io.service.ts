import { Injectable, inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import {
  projectName,
  activities,
  evmProject,
  riskRegister,
  wbsNodes,
  swotAnalysis,
  pestelAnalysis,
  viewMode,
  academicLevel,
  cpmResults,
  pertResults,
  evmKpis,
  crashingResults,
  rcpsResults,
  monteCarloResults,
} from '../store/project.store';

interface PMProject {
  version: 1;
  projectName: string;
  viewMode: 'learn' | 'clean';
  academicLevel: 'ug' | 'pg';
  activities: unknown[];
  evmProject: unknown | null;
  riskRegister: unknown[];
  wbsNodes: unknown[];
  swotAnalysis: unknown | null;
  pestelAnalysis: unknown | null;
  cpmResults: unknown | null;
  pertResults: unknown | null;
  evmKpis: unknown | null;
  crashingResults: unknown | null;
  rcpsResults: unknown | null;
  monteCarloResults: unknown | null;
}

@Injectable({ providedIn: 'root' })
export class ProjectIOService {
  private readonly snack = inject(MatSnackBar);

  /** Runtime validation for loaded project files */
  private isValidProject(data: unknown): data is PMProject {
    if (typeof data !== 'object' || data === null) return false;
    const d = data as Record<string, unknown>;
    if (d['version'] !== 1) return false;
    if (typeof d['projectName'] !== 'string') return false;
    if (!Array.isArray(d['activities'])) return false;
    if (d['viewMode'] !== undefined && d['viewMode'] !== 'learn' && d['viewMode'] !== 'clean')
      return false;
    if (
      d['academicLevel'] !== undefined &&
      d['academicLevel'] !== 'ug' &&
      d['academicLevel'] !== 'pg'
    )
      return false;
    return true;
  }

  /** Download current state as .pmproj JSON file */
  save(): void {
    const data: PMProject = {
      version: 1,
      projectName: projectName(),
      viewMode: viewMode(),
      academicLevel: academicLevel(),
      activities: activities(),
      evmProject: evmProject(),
      riskRegister: riskRegister(),
      wbsNodes: wbsNodes(),
      swotAnalysis: swotAnalysis(),
      pestelAnalysis: pestelAnalysis(),
      cpmResults: cpmResults(),
      pertResults: pertResults(),
      evmKpis: evmKpis(),
      crashingResults: crashingResults(),
      rcpsResults: rcpsResults(),
      monteCarloResults: monteCarloResults(),
    };

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName().replace(/[^a-zA-Z0-9_-]/g, '_')}.pmproj`;
    a.click();
    URL.revokeObjectURL(url);
    this.snack.open('Project saved', 'OK', { duration: 2000 });
  }

  /** Open file picker and load .pmproj file */
  load(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pmproj,.json';
    input.onchange = () => {
      const file = input.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const raw = JSON.parse(reader.result as string);
          if (!this.isValidProject(raw)) {
            this.snack.open('Incompatible or corrupt project file', 'Dismiss', { duration: 4000 });
            return;
          }
          this.applyProject(raw);
          this.snack.open(`Loaded: ${raw.projectName}`, 'OK', { duration: 2000 });
        } catch {
          this.snack.open('Invalid project file', 'Dismiss', { duration: 3000 });
        }
      };
      reader.readAsText(file);
    };
    input.click();
  }

  /** Export a simple CSV of activities */
  exportCsv(): void {
    const acts = activities();
    if (!acts.length) {
      this.snack.open('No activities to export', 'OK', { duration: 2000 });
      return;
    }
    const headers = ['ID', 'Name', 'Duration', 'Predecessors'];
    const rows = acts.map((a: any) => [
      a.id,
      a.name ?? '',
      a.duration ?? '',
      Array.isArray(a.predecessors) ? a.predecessors.join(';') : '',
    ]);
    const csv = [headers, ...rows]
      .map((r) => r.map((c: any) => `"${String(c).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName().replace(/[^a-zA-Z0-9_-]/g, '_')}_activities.csv`;
    a.click();
    URL.revokeObjectURL(url);
    this.snack.open('CSV exported', 'OK', { duration: 2000 });
  }

  private applyProject(data: PMProject): void {
    if (data.projectName) projectName.set(data.projectName);
    if (data.viewMode) viewMode.set(data.viewMode);
    if (data.academicLevel) academicLevel.set(data.academicLevel);
    if (Array.isArray(data.activities)) activities.set(data.activities as any);
    evmProject.set((data.evmProject as any) ?? null);
    if (Array.isArray(data.riskRegister)) riskRegister.set(data.riskRegister as any);
    if (Array.isArray(data.wbsNodes)) wbsNodes.set(data.wbsNodes as any);
    swotAnalysis.set((data.swotAnalysis as any) ?? null);
    pestelAnalysis.set((data.pestelAnalysis as any) ?? null);
    cpmResults.set((data.cpmResults as any) ?? null);
    pertResults.set((data.pertResults as any) ?? null);
    evmKpis.set((data.evmKpis as any) ?? null);
    crashingResults.set((data.crashingResults as any) ?? null);
    rcpsResults.set((data.rcpsResults as any) ?? null);
    monteCarloResults.set((data.monteCarloResults as any) ?? null);
  }
}
