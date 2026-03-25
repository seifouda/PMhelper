import { Pipe, PipeTransform } from '@angular/core';
import { RAGStatus } from '../../core/models/evm.model';

/**
 * Converts a numeric ratio to a RAG (Red / Amber / Green) traffic-light status.
 * Default thresholds: green ≥ 1.0, amber ≥ 0.9, red < 0.9
 * Pass a boolean `invert` = true for metrics where higher is worse (e.g. CRI).
 */
@Pipe({ name: 'rag', standalone: true })
export class RagPipe implements PipeTransform {
  transform(value: number, greenMin = 1.0, amberMin = 0.9): RAGStatus {
    if (value >= greenMin) return 'green';
    if (value >= amberMin) return 'amber';
    return 'red';
  }
}
