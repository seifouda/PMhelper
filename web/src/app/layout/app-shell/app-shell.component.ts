import { Component, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { TopBarComponent } from '../top-bar/top-bar.component';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { TutorialOverlayComponent } from '../../shared/components/tutorial/tutorial-overlay.component';

@Component({
  selector: 'app-app-shell',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    RouterOutlet,
    TopBarComponent,
    SidebarComponent,
    TutorialOverlayComponent,
  ],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {
  readonly sidebarCollapsed = signal(false);
  readonly isMobile = signal(false);

  constructor(bp: BreakpointObserver) {
    bp.observe(['(max-width: 768px)']).subscribe((state) => {
      this.isMobile.set(state.matches);
      if (state.matches) this.sidebarCollapsed.set(true);
    });
  }

  toggleSidebar(): void {
    this.sidebarCollapsed.update((v) => !v);
  }
}
