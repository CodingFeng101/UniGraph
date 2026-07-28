import { gsap } from 'gsap';

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function installFeedback() {
  window.showToast = function showToast(message) {
    document.getElementById('global-feedback-toast')?.remove();
    const toast = document.createElement('div');
    toast.id = 'global-feedback-toast';
    toast.setAttribute('role', 'status');
    toast.innerHTML =
      '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="8" r="1" fill="currentColor" stroke="none"/></svg>' +
      '<span></span>' +
      '<button type="button" aria-label="关闭"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>';
    toast.querySelector('span').textContent = message;
    toast.style.cssText = [
      'position:fixed', 'top:20px', 'left:50%', 'transform:translateX(-50%)',
      'display:flex', 'align-items:center', 'gap:10px', 'min-width:190px', 'max-width:min(520px,calc(100vw - 32px))',
      'padding:11px 12px 11px 14px', 'border-radius:13px', 'z-index:10000',
      'background:var(--claude-card)', 'color:var(--claude-foreground)', 'border:1px solid var(--claude-border)',
      'box-shadow:var(--claude-shadow-lg)', 'font-size:13px',
    ].join(';');
    toast.querySelector('span').style.cssText = 'flex:1;line-height:1.35;';
    toast.querySelector('button').style.cssText = 'display:flex;align-items:center;justify-content:center;background:none;border:none;color:var(--claude-muted-foreground);cursor:pointer;padding:2px;';
    document.body.appendChild(toast);

    const duration = prefersReducedMotion() ? 0 : 0.24;
    let expiry;
    const dismiss = () => {
      expiry?.kill();
      if (!toast.isConnected) return;
      gsap.to(toast, {
        autoAlpha: 0,
        y: -8,
        duration: prefersReducedMotion() ? 0 : 0.16,
        ease: 'power1.in',
        overwrite: 'auto',
        onComplete: () => toast.remove(),
      });
    };

    toast.querySelector('button').onclick = dismiss;
    gsap.fromTo(
      toast,
      { autoAlpha: 0, y: -8 },
      { autoAlpha: 1, y: 0, duration, ease: 'power2.out', overwrite: 'auto' },
    );
    expiry = gsap.delayedCall(2.6, dismiss);
  };

  window.confirmAction = function confirmAction(options = {}) {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.style.cssText = 'position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;background:rgba(28,25,23,.28);padding:16px;';
      overlay.innerHTML =
        '<div role="dialog" aria-modal="true" style="width:min(496px,100%);background:var(--claude-card);border:1px solid var(--claude-border);border-radius:16px;box-shadow:var(--claude-shadow-xl);padding:26px 28px 30px;">' +
          '<h2 style="margin:0;color:var(--claude-foreground);font-size:25px;line-height:1.2;font-weight:650;"></h2>' +
          '<p style="margin:8px 0 22px;color:var(--claude-muted-foreground);font-size:15px;line-height:1.5;"></p>' +
          '<div style="display:flex;justify-content:flex-end;gap:10px;">' +
            '<button data-cancel type="button" style="height:40px;padding:0 16px;border-radius:10px;background:var(--claude-card);border:1px solid var(--claude-border);color:var(--claude-foreground);font-size:14px;cursor:pointer;">取消</button>' +
            '<button data-confirm type="button" style="height:40px;padding:0 18px;border-radius:10px;background:var(--claude-destructive);border:none;color:white;font-size:14px;font-weight:600;cursor:pointer;">删除</button>' +
          '</div>' +
        '</div>';
      overlay.querySelector('h2').textContent = options.title || '确认删除';
      overlay.querySelector('p').textContent = options.message || '删除后无法恢复，是否继续？';
      overlay.querySelector('[data-confirm]').textContent = options.confirmText || '删除';

      const dialog = overlay.querySelector('[role="dialog"]');
      const duration = prefersReducedMotion() ? 0 : 0.24;
      let settled = false;
      const finish = (value) => {
        if (settled) return;
        settled = true;
        gsap.to(dialog, {
          autoAlpha: 0,
          y: 6,
          scale: 0.99,
          duration: prefersReducedMotion() ? 0 : 0.14,
          ease: 'power1.in',
          overwrite: 'auto',
        });
        gsap.to(overlay, {
          autoAlpha: 0,
          duration: prefersReducedMotion() ? 0 : 0.16,
          ease: 'power1.in',
          overwrite: 'auto',
          onComplete: () => {
            overlay.remove();
            resolve(value);
          },
        });
      };

      overlay.querySelector('[data-cancel]').onclick = () => finish(false);
      overlay.querySelector('[data-confirm]').onclick = () => finish(true);
      overlay.onclick = (event) => {
        if (event.target === overlay) finish(false);
      };
      document.body.appendChild(overlay);
      overlay.querySelector('[data-cancel]').focus();

      gsap.fromTo(
        overlay,
        { autoAlpha: 0 },
        { autoAlpha: 1, duration: duration * 0.75, ease: 'power1.out', overwrite: 'auto' },
      );
      gsap.fromTo(
        dialog,
        { autoAlpha: 0, y: 10, scale: 0.985 },
        { autoAlpha: 1, y: 0, scale: 1, duration, ease: 'power2.out', overwrite: 'auto' },
      );
    });
  };
}
