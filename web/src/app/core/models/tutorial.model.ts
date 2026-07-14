export interface TutorialStep {
  /** CSS selector for the element to highlight */
  selector: string;
  /** Title shown in the tooltip */
  title: string;
  /** Description text */
  description: string;
  /** Optional route to navigate to before highlighting */
  route?: string;
  /** Tooltip placement relative to the highlighted element */
  placement?: 'top' | 'bottom' | 'left' | 'right';
  /** Optional group for contextual/per-feature tutorials */
  group?: string;
}
