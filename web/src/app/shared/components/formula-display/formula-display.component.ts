import {
  Component,
  Input,
  ElementRef,
  OnChanges,
  ViewChild,
  ChangeDetectionStrategy,
  AfterViewInit,
} from '@angular/core';
import katex from 'katex';

@Component({
  selector: 'app-formula-display',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<span #container class="formula-display"></span>`,
  styles: [
    `
      .formula-display {
        display: inline-block;
        line-height: 1.6;
      }
    `,
  ],
})
export class FormulaDisplayComponent implements OnChanges, AfterViewInit {
  @Input() tex = '';
  @Input() displayMode = false;
  @ViewChild('container', { static: true }) container!: ElementRef<HTMLSpanElement>;

  ngAfterViewInit(): void {
    this.render();
  }

  ngOnChanges(): void {
    this.render();
  }

  private render(): void {
    if (!this.container?.nativeElement || !this.tex) return;
    try {
      katex.render(this.tex, this.container.nativeElement, {
        displayMode: this.displayMode,
        throwOnError: false,
      });
    } catch {
      this.container.nativeElement.textContent = this.tex;
    }
  }
}
