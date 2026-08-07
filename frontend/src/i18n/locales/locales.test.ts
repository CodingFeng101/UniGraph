import { describe, expect, it } from 'vitest';
import zhCN from './zh-CN';
import enUS from './en-US';

function keys(value: Record<string, unknown>, prefix = ''): string[] {
  return Object.entries(value).flatMap(([key, entry]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    return entry && typeof entry === 'object' ? keys(entry as Record<string, unknown>, path) : [path];
  }).sort();
}

describe('locale dictionaries', () => {
  it('keep Chinese and English semantic keys identical', () => {
    expect(keys(zhCN)).toEqual(keys(enUS));
  });
});
