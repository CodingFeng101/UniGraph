/**
 * Shared background-task queue.
 * Keeps the supplied task-panel UI, but replaces demo rows with real Celery jobs.
 */
import { Auth } from '@/api/runtime/auth';
import { KgBaseAPI } from '@/api';
import { getTaskNotificationPreferences } from '@/services/preferences';

export const TaskManager = window.TaskManager = (() => {
  const STORAGE_KEY = 'unigraph_task_queue';
  const completionById = new Map();
  let audioContext = null;
  let tasks = load();
  const expandedTasks = new Set();

  function load() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      return Array.isArray(value) ? value : [];
    } catch (error) {
      return [];
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, (char) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    })[char]);
  }

  function notify(message) {
    if (typeof window.showToast === 'function') {
      window.showToast(message);
    }
  }

  function primeAudio() {
    if (!getTaskNotificationPreferences().sound) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    audioContext ||= new AudioContext();
    if (audioContext.state === 'suspended') audioContext.resume().catch(() => {});
  }

  function playCompletionSound() {
    if (!getTaskNotificationPreferences().sound) return;
    primeAudio();
    if (!audioContext || audioContext.state !== 'running') return;
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(660, audioContext.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(880, audioContext.currentTime + 0.14);
    gain.gain.setValueAtTime(0.0001, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.12, audioContext.currentTime + 0.025);
    gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.24);
    oscillator.connect(gain);
    gain.connect(audioContext.destination);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.25);
  }

  function sendDesktopNotification(task) {
    const preferences = getTaskNotificationPreferences();
    if (!preferences.desktop || !('Notification' in window) || Notification.permission !== 'granted') return;
    try {
      const notification = new Notification('UniGraph 后台任务已完成', {
        body: [task.displayName, task.objectName].filter(Boolean).join('：'),
        tag: `unigraph-task-${task.uid}`,
      });
      notification.onclick = () => {
        window.focus();
        notification.close();
      };
    } catch {
      // Notification delivery must not change the completed task result.
    }
  }

  function notifyCompletion(task) {
    if (task.completionNotified) return;
    task.completionNotified = true;
    save();
    playCompletionSound();
    sendDesktopNotification(task);
  }

  function stateLabel(state) {
    return {
      PENDING: '等待中',
      STARTED: '执行中',
      PROGRESS: '执行中',
      RETRY: '重试中',
      SUCCESS: '已完成',
      FAILURE: '失败',
      REVOKE: '已撤销',
      REVOKED: '已撤销',
    }[state] || state;
  }

  function stateColor(state) {
    if (state === 'SUCCESS') return 'var(--claude-success-500)';
    if (state === 'FAILURE') return 'var(--claude-destructive)';
    if (state === 'REVOKE' || state === 'REVOKED') return 'var(--claude-muted-foreground)';
    return 'var(--claude-info-500, #3b82f6)';
  }

  function formatTaskTime(value) {
    const text = String(value || '');
    const match = text.match(/(\d{1,2}):(\d{2}):(\d{2})/);
    if (match) return `${match[1].padStart(2, '0')}:${match[2]}:${match[3]}`;
    return new Date().toLocaleTimeString('zh-CN', { hour12: false });
  }

  function getTaskSteps(task) {
    const steps = Array.isArray(task.steps) ? task.steps.slice() : [];
    if (!steps.length) {
      steps.push({ label: '任务已创建', time: formatTaskTime(task.createdAt), progress: 0 });
    }
    const currentLabel = task.message || stateLabel(task.state);
    if (!steps.some((step) => step.label === currentLabel)) {
      steps.push({
        label: currentLabel,
        time: formatTaskTime(task.updatedAt || task.createdAt),
        progress: Number(task.progress) || 0,
      });
    }
    return steps.slice(-60);
  }

  function persistAndRender() {
    save();
    render();
  }

  function render() {
    const panel = document.getElementById('task-panel');
    if (!panel) return;

    const running = tasks.filter((task) => ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state));
    const headerBadge = panel.querySelector('[data-task-running-count]');
    if (headerBadge) headerBadge.textContent = `${running.length} 进行中`;

    const fabBadge = document.querySelector('[data-task-fab-count]');
    const fab = document.getElementById('task-fab-wrapper');
    if (fab) {
      const palette = ['#b7d8bf', '#91cda3', '#69bb89', '#48a973', '#2f915e', '#21764c', '#185f3d'];
      const level = Math.min(running.length, palette.length - 1);
      const duration = Math.max(1.25, 3.4 - running.length * 0.34);
      fab.style.setProperty('--task-orb-color', palette[level]);
      fab.style.setProperty('--task-orb-duration', `${duration}s`);
    }
    if (fabBadge) {
      fabBadge.textContent = String(running.length);
      fabBadge.style.display = running.length ? 'flex' : 'none';
    }

    const container = panel.querySelector('[data-task-list]');
    if (!container) return;

    if (!tasks.length) {
      container.innerHTML = '<div class="task-empty">暂无后台任务</div>';
      return;
    }

    const previousScrollTop = container.scrollTop;
    container.innerHTML = tasks.slice().reverse().map((task) => {
      const progress = Math.max(0, Math.min(100, Number(task.progress) || 0));
      const canCancel = ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state);
      const isOpen = expandedTasks.has(task.uid);
      const steps = getTaskSteps(task);
      const title = [task.displayName, task.objectName].filter(Boolean).join(': ');
      const statusText = canCancel ? `${Math.round(progress)}%` : (task.state === 'SUCCESS' ? '完成' : stateLabel(task.state));
      const stepMarkup = steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        const color = isLast ? stateColor(task.state) : 'var(--claude-success-500)';
        const description = step.detail || (Number(step.progress) > 0 && Number(step.progress) < 100
          ? `已处理 ${Math.round(Number(step.progress))}%`
          : '');
        return `
          <div class="task-step${isLast ? ' is-latest' : ''}" style="--step-color:${color};">
            <span class="task-step__dot"></span>
            <div class="task-step__head">
              <span class="task-step__label">${escapeHtml(step.label)}</span>
              <span class="task-step__time">${escapeHtml(formatTaskTime(step.time))}</span>
            </div>
            ${description ? `<p class="task-step__description">${escapeHtml(description)}</p>` : ''}
          </div>`;
      }).join('');
      return `
        <div class="task-card" data-task-id="${escapeHtml(task.uid)}">
          <button type="button" onclick="TaskManager.toggle(this)" class="task-card__summary">
            <svg class="task-chevron" style="transform:${isOpen ? 'rotate(90deg)' : 'rotate(0deg)'}" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            <span class="task-status-dot" style="background:${stateColor(task.state)};"></span>
            <p class="task-card__title">${escapeHtml(title || '后台任务')}</p>
            <span class="task-card__state" style="color:${stateColor(task.state)};">${escapeHtml(statusText)}</span>
          </button>
          <div class="task-progress"><div class="task-progress__value" style="width:${progress}%;background:${stateColor(task.state)};"></div></div>
          <div class="task-detail${isOpen ? '' : ' hidden'}">
            <div class="task-timeline">${stepMarkup}</div>
            <div class="task-actions">
              <button type="button" onclick="TaskManager.pause('${escapeHtml(task.uid)}')" class="task-action" ${canCancel ? '' : 'disabled'}><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>暂停</button>
              <button type="button" onclick="TaskManager.retry('${escapeHtml(task.uid)}')" class="task-action"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 3-6.7"/><polyline points="3 4 3 10 9 10"/></svg>重启</button>
              <button type="button" onclick="TaskManager.remove('${escapeHtml(task.uid)}')" class="task-action task-action--delete"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4h8v2"/></svg>删除</button>
            </div>
          </div>
        </div>`;
    }).join('');
    requestAnimationFrame(() => {
      container.scrollTop = previousScrollTop;
      container.querySelectorAll('.task-detail:not(.hidden) .task-timeline').forEach((timeline) => {
        timeline.scrollTop = timeline.scrollHeight;
      });
    });
  }

  function toggle(button) {
    const card = button.closest('.task-card');
    const detail = card?.querySelector('.task-detail');
    const chevron = button.querySelector('.task-chevron');
    if (!detail) return;
    detail.classList.toggle('hidden');
    const isOpen = !detail.classList.contains('hidden');
    if (isOpen) expandedTasks.add(card.dataset.taskId);
    else expandedTasks.delete(card.dataset.taskId);
    if (chevron) chevron.style.transform = isOpen ? 'rotate(90deg)' : 'rotate(0deg)';
    if (isOpen) {
      requestAnimationFrame(() => {
        const container = card.closest('[data-task-list]');
        if (!container) return;
        const timeline = card.querySelector('.task-timeline');
        if (timeline) timeline.scrollTop = timeline.scrollHeight;
        const target = card.offsetTop + card.offsetHeight - container.clientHeight;
        container.scrollTo({ top: Math.max(0, target), behavior: 'smooth' });
      });
    }
  }

  function updateFromStatus(task, status) {
    const meta = status.meta || {};
    const previousMessage = task.message;
    task.state = status.state || task.state;
    if (task.state === 'SUCCESS' && (meta.type === 'error' || meta.error)) task.state = 'FAILURE';
    task.progress = task.state === 'SUCCESS' ? 100 : Number(meta.progress ?? task.progress ?? 0);
    task.message = meta.message || meta.error?.message || stateLabel(task.state);
    task.updatedAt = new Date().toLocaleString();
    if (Array.isArray(meta.logs) && meta.logs.length) {
      task.steps = meta.logs.slice(-60).map((log) => ({
        id: log.id,
        label: log.message || task.message,
        detail: log.detail || '',
        time: log.time || task.updatedAt,
        progress: Number(log.progress ?? task.progress ?? 0),
        metrics: log.metrics || {},
      }));
    } else if (task.message !== previousMessage) {
      task.steps = Array.isArray(task.steps) ? task.steps : [];
      task.steps.push({
        label: task.message,
        detail: meta.detail || '',
        time: formatTaskTime(task.updatedAt),
        progress: task.progress,
      });
      task.steps = task.steps.slice(-60);
    } else if (Array.isArray(task.steps) && task.steps.length) {
      task.steps[task.steps.length - 1].progress = task.progress;
      task.steps[task.steps.length - 1].time = formatTaskTime(task.updatedAt);
    }
    task.result = meta.data ?? meta.result ?? null;
    persistAndRender();
  }

  async function poll(task) {
    while (['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const response = await KgBaseAPI.task.getStatus(task.uid);
      if (response.code !== 200 || !response.data) {
        task.state = 'FAILURE';
        task.message = response.msg || '任务状态查询失败';
        persistAndRender();
        throw new Error(task.message);
      }
      updateFromStatus(task, response.data);
    }
    if (task.state === 'SUCCESS') {
      notifyCompletion(task);
      notify(`${task.displayName}已完成`);
      return task.result;
    }
    if (task.state === 'REVOKE' || task.state === 'REVOKED') return null;
    throw new Error(task.message || `${task.displayName}失败`);
  }

  async function submit(name, displayName, objectName, kwargs) {
    const response = await KgBaseAPI.task.submit(name, kwargs || {});
    if (response.code !== 200 || !response.data?.task_id) {
      throw new Error(response.msg || '任务提交失败');
    }
    const task = {
      uid: response.data.task_id,
      name,
      displayName,
      objectName,
      kwargs: kwargs || {},
      state: 'PENDING',
      progress: 0,
      message: '任务已创建',
      createdAt: new Date().toLocaleString(),
      updatedAt: new Date().toLocaleString(),
      steps: [],
      result: null,
      completionNotified: false,
    };
    task.steps.push({ label: task.message, time: formatTaskTime(task.createdAt), progress: 0 });
    tasks.push(task);
    persistAndRender();
    notify(`${displayName}任务已提交`);
    const completion = poll(task);
    completionById.set(task.uid, completion);
    completion.then(
      () => completionById.delete(task.uid),
      () => completionById.delete(task.uid),
    );
    return { ...task, completion };
  }

  async function cancel(uid) {
    const task = tasks.find((item) => item.uid === uid);
    if (!task) return;
    const response = await KgBaseAPI.task.revoke(uid);
    if (response.code !== 200) throw new Error(response.msg || '撤销失败');
    task.state = 'REVOKE';
    task.message = '任务已撤销';
    task.updatedAt = new Date().toLocaleString();
    task.steps = Array.isArray(task.steps) ? task.steps : [];
    task.steps.push({ label: task.message, time: formatTaskTime(task.updatedAt), progress: task.progress });
    persistAndRender();
    notify('任务已撤销');
  }

  async function retry(uid) {
    const task = tasks.find((item) => item.uid === uid);
    if (!task) return;
    if (['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)) {
      await cancel(uid);
    }
    await submit(task.name, task.displayName, task.objectName, task.kwargs);
  }

  async function pause(uid) {
    await cancel(uid);
    const task = tasks.find((item) => item.uid === uid);
    if (task) {
      task.message = '任务已暂停，可点击重启重新执行';
      task.updatedAt = new Date().toLocaleString();
      task.steps = Array.isArray(task.steps) ? task.steps : [];
      task.steps.push({ label: task.message, time: formatTaskTime(task.updatedAt), progress: task.progress });
      persistAndRender();
    }
  }

  async function remove(uid) {
    const task = tasks.find((item) => item.uid === uid);
    if (!task) return;
    if (typeof window.confirmAction === 'function') {
      const confirmed = await window.confirmAction({ title: '删除任务', message: '确定要删除这条后台任务记录吗？' });
      if (!confirmed) return;
    }
    if (['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)) await cancel(uid);
    tasks = tasks.filter((item) => item.uid !== uid);
    expandedTasks.delete(uid);
    persistAndRender();
  }

  function resume() {
    tasks.filter((task) => ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)).forEach((task) => {
      if (completionById.has(task.uid)) return;
      const completion = poll(task).catch(() => null);
      completionById.set(task.uid, completion);
      completion.then(
        () => completionById.delete(task.uid),
        () => completionById.delete(task.uid),
      );
    });
  }

  function init() {
    render();
    document.addEventListener('pointerdown', primeAudio, { once: true });
    window.addEventListener('unigraph:preferences-changed', primeAudio);
    if (typeof Auth !== 'undefined' && Auth.isLogin()) resume();
  }

  document.addEventListener('DOMContentLoaded', init);
  if (document.readyState !== 'loading') init();

  return { submit, cancel, pause, retry, remove, toggle, render, resume };
})();
