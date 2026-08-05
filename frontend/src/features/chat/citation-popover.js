const citationCloseTimers = new WeakMap();

function isOpen(popup) {
  try {
    return popup.matches(':popover-open');
  } catch {
    return false;
  }
}

export function showCitationPopup(citation) {
  const popup = citation?.querySelector('.source-popup');
  if (!popup) return;
  citation.classList.add('is-open');
  citation.setAttribute('aria-expanded', 'true');
  if (typeof popup.showPopover === 'function' && !isOpen(popup)) {
    try { popup.showPopover(); } catch { /* CSS-positioned fallback remains visible. */ }
  }
  positionCitationPopup(citation);
}

export function hideCitationPopup(citation) {
  const popup = citation?.querySelector('.source-popup');
  citation?.classList.remove('is-open');
  citation?.setAttribute('aria-expanded', 'false');
  if (popup && typeof popup.hidePopover === 'function' && isOpen(popup)) {
    try { popup.hidePopover(); } catch { /* It may already be dismissed. */ }
  }
}

export function hideAllCitationPopups() {
  document.querySelectorAll('[data-citation].is-open').forEach(hideCitationPopup);
}

function positionCitationPopup(citation) {
  const popup = citation?.querySelector('.source-popup');
  if (!popup) return;
  const pageElement = document.getElementById('chat-message-list') || document.getElementById('app-main');
  const page = pageElement?.getBoundingClientRect();
  const boundary = {
    left: Math.max(12, page?.left || 0) + 12,
    right: Math.min(window.innerWidth - 12, page?.right || window.innerWidth) - 12,
    top: Math.max(12, page?.top || 0) + 12,
    bottom: Math.min(window.innerHeight - 12, page?.bottom || window.innerHeight) - 12,
  };
  const heightCap = citation.classList.contains('citation-tag--overview') ? 320 : 300;
  popup.classList.remove('source-popup--below');
  popup.style.removeProperty('max-height');
  popup.style.maxWidth = `${Math.max(220, boundary.right - boundary.left)}px`;
  popup.style.setProperty('--source-popup-shift-x', '0px');

  const citationRect = citation.getBoundingClientRect();
  const spaceAbove = Math.max(0, citationRect.top - boundary.top - 8);
  const spaceBelow = Math.max(0, boundary.bottom - citationRect.bottom - 8);
  if (typeof popup.showPopover === 'function' && isOpen(popup)) {
    const desiredHeight = Math.min(popup.scrollHeight, heightCap);
    const showBelow = desiredHeight > spaceAbove && spaceBelow > spaceAbove;
    const maxHeight = Math.max(96, Math.min(heightCap, Math.floor(showBelow ? spaceBelow : spaceAbove)));
    popup.style.position = 'fixed';
    popup.style.transform = 'none';
    popup.style.maxHeight = `${maxHeight}px`;
    const popupRect = popup.getBoundingClientRect();
    const left = Math.min(Math.max(citationRect.left, boundary.left), boundary.right - popupRect.width);
    const top = showBelow ? citationRect.bottom + 8 : citationRect.top - popupRect.height - 8;
    popup.style.left = `${Math.round(Math.max(boundary.left, left))}px`;
    popup.style.top = `${Math.round(Math.min(Math.max(top, boundary.top), boundary.bottom - popupRect.height))}px`;
    popup.style.right = 'auto';
    popup.style.bottom = 'auto';
    return;
  }

  const popupRect = popup.getBoundingClientRect();
  let shiftX = 0;
  if (popupRect.right > boundary.right) shiftX -= popupRect.right - boundary.right;
  if (popupRect.left + shiftX < boundary.left) shiftX += boundary.left - (popupRect.left + shiftX);
  popup.style.setProperty('--source-popup-shift-x', `${Math.round(shiftX)}px`);
  const showBelow = popupRect.height > spaceAbove && spaceBelow > spaceAbove;
  popup.classList.toggle('source-popup--below', showBelow);
  popup.style.maxHeight = `${Math.max(96, Math.min(heightCap, Math.floor(showBelow ? spaceBelow : spaceAbove)))}px`;
}

function scheduleClose(citation) {
  const existingTimer = citationCloseTimers.get(citation);
  if (existingTimer) window.clearTimeout(existingTimer);
  const timer = window.setTimeout(() => {
    citationCloseTimers.delete(citation);
    if (citation.matches(':hover') || citation.contains(document.activeElement)) return;
    hideCitationPopup(citation);
    citation.blur();
  }, 180);
  citationCloseTimers.set(citation, timer);
}

export function installCitationPopoverEvents() {
  const onPointerOver = (event) => {
    const citation = event.target.closest?.('[data-citation]');
    if (!citation) return;
    const timer = citationCloseTimers.get(citation);
    if (timer) window.clearTimeout(timer);
    citationCloseTimers.delete(citation);
    showCitationPopup(citation);
  };
  const onFocusIn = (event) => {
    const citation = event.target.closest?.('[data-citation]');
    if (citation) showCitationPopup(citation);
  };
  const onPointerOut = (event) => {
    const citation = event.target.closest?.('[data-citation]');
    if (!citation || citation.contains(event.relatedTarget)) return;
    scheduleClose(citation);
  };
  document.addEventListener('pointerover', onPointerOver);
  document.addEventListener('focusin', onFocusIn);
  document.addEventListener('pointerout', onPointerOut);
  return () => {
    document.removeEventListener('pointerover', onPointerOver);
    document.removeEventListener('focusin', onFocusIn);
    document.removeEventListener('pointerout', onPointerOut);
  };
}
