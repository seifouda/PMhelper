import { Injectable, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { TutorialStep } from '../../core/models/tutorial.model';
import { academicLevel } from '../../core/store/project.store';

const STORAGE_KEY = 'pmhelper_tutorial_seen';

@Injectable({ providedIn: 'root' })
export class TutorialService {
  /** Master registry of all steps (populated via registerSteps) */
  private readonly _allSteps: TutorialStep[] = [];
  /** Steps for the active run (may be filtered by group / academic level) */
  private readonly _steps = signal<TutorialStep[]>([]);
  private readonly _currentIndex = signal(-1); // -1 = inactive

  readonly steps = this._steps.asReadonly();
  readonly currentIndex = this._currentIndex.asReadonly();
  readonly isActive = computed(() => this._currentIndex() >= 0);
  readonly currentStep = computed(() => {
    const i = this._currentIndex();
    return i >= 0 ? (this._steps()[i] ?? null) : null;
  });
  readonly totalSteps = computed(() => this._steps().length);

  constructor(private router: Router) {}

  /**
   * Register steps into the master list.
   * Can be called multiple times — from app init and from individual feature components.
   */
  registerSteps(steps: TutorialStep[]): void {
    this._allSteps.push(...steps);
  }

  /** Whether the user has seen the tutorial at least once */
  hasSeenTutorial(): boolean {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  }

  /** Mark the tutorial as seen */
  private markSeen(): void {
    try {
      localStorage.setItem(STORAGE_KEY, 'true');
    } catch {
      // localStorage unavailable — ignore
    }
  }

  /** Start the tutorial, optionally filtering to a specific group */
  async start(group?: string): Promise<void> {
    const isPg = academicLevel() === 'pg';
    let steps = this._allSteps.filter((s) => {
      // Filter by group if requested
      if (group && s.group && s.group !== group) return false;
      // Hide PG-only steps when in UG mode
      if (!isPg && s.group === 'pg') return false;
      return true;
    });
    if (steps.length === 0) return;
    this._steps.set(steps);
    this._currentIndex.set(0);
    await this.navigateIfNeeded();
  }

  async next(): Promise<void> {
    const nextIdx = this._currentIndex() + 1;
    if (nextIdx >= this._steps().length) {
      this.close();
      return;
    }
    this._currentIndex.set(nextIdx);
    await this.navigateIfNeeded();
  }

  async back(): Promise<void> {
    const prevIdx = this._currentIndex() - 1;
    if (prevIdx < 0) return;
    this._currentIndex.set(prevIdx);
    await this.navigateIfNeeded();
  }

  close(): void {
    this._currentIndex.set(-1);
    this.markSeen();
  }

  /** Navigate to the step's route if specified and not already there */
  private async navigateIfNeeded(): Promise<void> {
    const step = this.currentStep();
    if (step?.route && this.router.url !== step.route) {
      await this.router.navigateByUrl(step.route);
      // Allow DOM to settle after route change
      await new Promise((resolve) => setTimeout(resolve, 350));
    }
  }
}
