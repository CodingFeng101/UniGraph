/* Generated from pages/docs.html; keep behavior changes in the source controller during migration. */
import { copyText } from '@/utils/clipboard';

export function createDocsViewController() {
  lucide.createIcons();

function copyCode(btn) {
  var code = btn.closest('.relative').querySelector('code');
  if (!code) return;
  copyText(code.textContent).then(function(copied) {
    if (!copied) return;
    btn.classList.add('copy-done');
    setTimeout(function() { btn.classList.remove('copy-done'); }, 1500);
  });
}

function selectDocNav(el) {
  document.querySelectorAll('.doc-nav-item').forEach(function(item) {
    item.style.background = 'transparent';
    item.style.color = 'var(--claude-muted-foreground)';
    item.classList.remove('font-medium');
  });
  el.style.background = 'var(--claude-accent)';
  el.style.color = 'var(--claude-foreground)';
  el.classList.add('font-medium');
  showToast('已切换到：' + el.textContent.trim());
}

function showToast(message) {
  window.showToast(message);
}


  return {
    copyCode,
    selectDocNav,
  };
}
