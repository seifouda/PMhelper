import { Pipe, PipeTransform } from '@angular/core';

/**
 * Formats a monetary value with a currency symbol.
 * Usage: {{ 12500 | currencyFormat:'$' }}  →  $12,500
 */
@Pipe({ name: 'currencyFormat', standalone: true })
export class CurrencyFormatPipe implements PipeTransform {
  transform(value: number | null | undefined, symbol = '$', decimals = 0): string {
    if (value == null) return '—';
    return (
      symbol +
      value.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    );
  }
}
