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
  window.showToast(message);
}


  return {
    filterVideos,
    showToast,
  };
}
