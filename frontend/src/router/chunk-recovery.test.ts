import { beforeEach, describe, expect, it, vi } from 'vitest';
import { clearChunkRecoveryMarker, isChunkLoadError, recoverFromChunkError } from './chunk-recovery';

describe('dynamic chunk recovery', () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  it('recognizes Vite dynamic import failures', () => {
    expect(isChunkLoadError(new Error('Failed to fetch dynamically imported module: /assets/page.js'))).toBe(true);
    expect(isChunkLoadError(new Error('ordinary API error'))).toBe(false);
  });

  it('reloads only once for the same URL', () => {
    const reload = vi.fn();
    expect(recoverFromChunkError(new Error('Failed to fetch dynamically imported module'), 'http://app/page', reload)).toBe(true);
    expect(recoverFromChunkError(new Error('Failed to fetch dynamically imported module'), 'http://app/page', reload)).toBe(false);
    expect(reload).toHaveBeenCalledTimes(1);
  });

  it('clears the marker after successful navigation', () => {
    sessionStorage.setItem('unigraph:chunk-recovery', 'http://app/page');
    clearChunkRecoveryMarker();
    expect(sessionStorage.getItem('unigraph:chunk-recovery')).toBeNull();
  });
});
