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
  var container = document.getElementById('toast-container');
  var toast = document.createElement('div');
  toast.className = 'px-4 py-2.5 rounded-lg text-sm font-medium';
  toast.style.background = 'var(--claude-card)';
  toast.style.color = 'var(--claude-foreground)';
  toast.style.border = '1px solid var(--claude-border)';
  toast.style.boxShadow = 'var(--claude-shadow-md)';
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(function() { toast.remove(); }, 2000);
}


  return {
    copyCode,
    selectDocNav,
  };
}
