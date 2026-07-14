import {
  Component,
  inject,
  effect,
  signal,
  ChangeDetectionStrategy,
  HostListener,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TutorialService } from '../../services/tutorial.service';

@Component({
  selector: 'app-tutorial-overlay',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    @if (tutorial.isActive()) {
      <!-- Backdrop -->
      <div class="tut-backdrop" (click)="tutorial.close()"></div>

      <!-- Highlight ring around target element -->
      <div
        class="tut-highlight"
        [style.top.px]="rect().top"
        [style.left.px]="rect().left"
        [style.width.px]="rect().width"
        [style.height.px]="rect().height"
      ></div>

      <!-- Tooltip card -->
      <div
        class="tut-tooltip"
        [class]="'tut-tooltip tut-tooltip--' + placement()"
        [style.top.px]="tip().top"
        [style.left.px]="tip().left"
        role="dialog"
        aria-modal="true"
        [attr.aria-label]="tutorial.currentStep()?.title"
      >
        <div class="tut-tooltip__header">
          <span class="tut-tooltip__badge">
            {{ tutorial.currentIndex() + 1 }} / {{ tutorial.totalSteps() }}
          </span>
          <h4 class="tut-tooltip__title">{{ tutorial.currentStep()?.title }}</h4>
          <button mat-icon-button (click)="tutorial.close()" aria-label="Close tutorial">
            <mat-icon>close</mat-icon>
          </button>
        </div>
        <p class="tut-tooltip__desc">{{ tutorial.currentStep()?.description }}</p>
        <div class="tut-tooltip__actions">
          <button
            mat-stroked-button
            [disabled]="tutorial.currentIndex() === 0"
            (click)="tutorial.back()"
          >
            Back
          </button>
          <button mat-flat-button color="primary" (click)="tutorial.next()">
            {{ tutorial.currentIndex() === tutorial.totalSteps() - 1 ? 'Finish' : 'Next' }}
          </button>
        </div>
      </div>
    }
  `,
  styleUrl: './tutorial-overlay.component.scss',
})
export class TutorialOverlayComponent {
  readonly tutorial = inject(TutorialService);

  readonly rect = signal({ top: 0, left: 0, width: 0, height: 0 });
  readonly tip = signal({ top: 0, left: 0 });
  readonly placement = signal<string>('bottom');

  constructor() {
    effect(() => {
      const step = this.tutorial.currentStep();
      if (step) {
        requestAnimationFrame(() => this.position(step.selector, step.placement));
      }
    });
  }

  @HostListener('window:resize')
  onResize(): void {
    const step = this.tutorial.currentStep();
    if (step) this.position(step.selector, step.placement);
  }

  @HostListener('window:keydown.Escape')
  onEsc(): void {
    if (this.tutorial.isActive()) this.tutorial.close();
  }

  @HostListener('window:keydown.ArrowRight')
  onRight(): void {
    if (this.tutorial.isActive()) this.tutorial.next();
  }

  @HostListener('window:keydown.ArrowLeft')
  onLeft(): void {
    if (this.tutorial.isActive()) this.tutorial.back();
  }

  private position(selector: string, dir?: string): void {
    const el = document.querySelector(selector);
    if (!el) {
      // Element not in DOM — skip to next step automatically
      this.tutorial.next();
      return;
    }

    const r = el.getBoundingClientRect();
    const pad = 6;

    this.rect.set({
      top: r.top - pad + window.scrollY,
      left: r.left - pad + window.scrollX,
      width: r.width + pad * 2,
      height: r.height + pad * 2,
    });

    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    const d = dir ?? 'bottom';
    this.placement.set(d);

    const tooltipWidth = 320;
    const tooltipGap = 12;
    const t = { top: 0, left: 0 };

    switch (d) {
      case 'bottom':
        t.top = r.bottom + tooltipGap + window.scrollY;
        t.left = Math.max(
          8,
          Math.min(r.left + window.scrollX, window.innerWidth - tooltipWidth - 8),
        );
        break;
      case 'top':
        t.top = r.top - tooltipGap - 160 + window.scrollY;
        t.left = Math.max(
          8,
          Math.min(r.left + window.scrollX, window.innerWidth - tooltipWidth - 8),
        );
        break;
      case 'right':
        t.top = r.top + window.scrollY;
        t.left = r.right + tooltipGap + window.scrollX;
        break;
      case 'left':
        t.top = r.top + window.scrollY;
        t.left = r.left - tooltipWidth - tooltipGap + window.scrollX;
        break;
    }

    this.tip.set(t);
  }
}
