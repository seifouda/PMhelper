import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';

import { CPMResults, CPMNode } from '../../../../core/models/cpm-result.model';

@Component({
  selector: 'app-cpm-results-table',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatTableModule,
    MatSortModule,
    MatIconModule,
    MatChipsModule,
    MatTooltipModule,
    MatButtonModule,
  ],
  templateUrl: './cpm-results-table.component.html',
  styleUrls: ['./cpm-results-table.component.scss'],
})
export class CpmResultsTableComponent implements OnChanges {
  @Input() results: CPMResults | null = null;

  readonly sortedNodes = signal<CPMNode[]>([]);
  readonly activeSortField = signal<string>('id');
  readonly activeSortDir = signal<'asc' | 'desc'>('asc');

  readonly displayedColumns = [
    'is_critical',
    'id',
    'activity',
    'duration',
    'ES',
    'EF',
    'LS',
    'LF',
    'total_float',
    'free_float',
  ];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['results']) {
      this._sort();
    }
  }

  onSort(sort: Sort): void {
    if (sort.direction) {
      this.activeSortField.set(sort.active);
      this.activeSortDir.set(sort.direction as 'asc' | 'desc');
    }
    this._sort();
  }

  private _sort(): void {
    const nodes = this.results?.nodes ?? [];
    if (!nodes.length) {
      this.sortedNodes.set([]);
      return;
    }
    const field = this.activeSortField() as keyof CPMNode;
    const dir = this.activeSortDir() === 'asc' ? 1 : -1;
    const sorted = [...nodes].sort((a, b) => {
      const av = a[field];
      const bv = b[field];
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir;
      return String(av).localeCompare(String(bv)) * dir;
    });
    this.sortedNodes.set(sorted);
  }
}
