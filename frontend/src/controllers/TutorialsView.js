/* Generated from pages/tutorials.html; keep behavior changes in the source controller during migration. */
export function createTutorialsViewController() {
  lucide.createIcons();

function filterVideos(level, btn) {
  // 切换 Tab 样式
  document.querySelectorAll('.tab-btn').forEach(function(t) {
    t.style.color = 'var(--claude-muted-foreground)';
    t.style.borderBottom = '2px solid transparent';
  });
  btn.style.color = 'var(--claude-primary)';
  btn.style.borderBottom = '2px solid var(--claude-primary)';

  // 过滤视频
  var videos = document.querySelectorAll('.video-item');
  videos.forEach(function(v) {
    if (level === 'all' || v.getAttribute('data-level') === level) {
      v.style.display = '';
    } else {
      v.style.display = 'none';
    }
  });
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
    filterVideos,
    showToast,
  };
}
