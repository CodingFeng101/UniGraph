const RELOAD_KEY = 'unigraph:chunk-recovery';
const CHUNK_ERROR = /Failed to fetch dynamically imported module|Importing a module script failed|error loading dynamically imported module/i;

export function isChunkLoadError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error || '');
  return CHUNK_ERROR.test(message);
}

export function recoverFromChunkError(
  error: unknown,
  href = window.location.href,
  reload: () => void = () => window.location.reload(),
): boolean {
  if (!isChunkLoadError(error)) return false;
  const attemptedHref = sessionStorage.getItem(RELOAD_KEY);
  if (attemptedHref === href) {
    sessionStorage.removeItem(RELOAD_KEY);
    return false;
  }
  sessionStorage.setItem(RELOAD_KEY, href);
  reload();
  return true;
}

export function clearChunkRecoveryMarker(): void {
  sessionStorage.removeItem(RELOAD_KEY);
}
