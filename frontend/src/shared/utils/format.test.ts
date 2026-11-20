import { describe, expect, it } from 'vitest';
import { elapsedMinutes, formatCOP } from './format';

describe('format helpers', () => {
  it('formats Colombian pesos without decimal noise', () => {
    expect(formatCOP(1284500)).toContain('1.284.500');
  });

  it('never returns a negative elapsed time for future timestamps', () => {
    expect(elapsedMinutes(new Date(Date.now() + 60_000).toISOString())).toBe(0);
  });
});
