import { Directive, TemplateRef, ViewContainerRef, inject, effect } from '@angular/core';
import { viewMode } from '../../core/store/project.store';

/**
 * Structural directive that renders the host element only in Learn Mode.
 * Usage: <div *appLearnMode>Show only in Learn Mode</div>
 *
 * In Clean View, the element is removed from the DOM entirely —
 * not just hidden — so it has zero layout impact.
 */
@Directive({
  selector: '[appLearnMode]',
  standalone: true,
})
export class LearnModeDirective {
  private readonly tpl = inject(TemplateRef);
  private readonly vcr = inject(ViewContainerRef);
  private rendered = false;

  constructor() {
    effect(() => {
      const isLearn = viewMode() === 'learn';
      if (isLearn && !this.rendered) {
        this.vcr.createEmbeddedView(this.tpl);
        this.rendered = true;
      } else if (!isLearn && this.rendered) {
        this.vcr.clear();
        this.rendered = false;
      }
    });
  }
}
