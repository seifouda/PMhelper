import { Pipe, PipeTransform } from '@angular/core';

/**
 * Formats a duration number with an appropriate unit label.
 * Usage: {{ 5 | durationFormat }}       →  "5 days"
 *        {{ 1 | durationFormat:'week' }} →  "1 week"
 */
@Pipe({ name: 'durationFormat', standalone: true })
export class DurationFormatPipe implements PipeTransform {
  transform(value: number | null | undefined, unit = 'day'): string {
    if (value == null) return '—';
    const label = value === 1 ? unit : `${unit}s`;
    return `${value} ${label}`;
  }
}
