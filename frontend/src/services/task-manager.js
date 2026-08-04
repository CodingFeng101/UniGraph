/**
 * Shared background-task queue.
 * Keeps the supplied task-panel UI, but replaces demo rows with real Celery jobs.
 */
import { Auth } from '@/api/runtime/auth';
import { KgBaseAPI } from '@/api';
import { getLocale, t } from '@/services/i18n';
import { getTaskNotificationPreferences } from '@/services/preferences';
import { gsap } from 'gsap';

export const TaskManager = window.TaskManager = (() => {
  const LEGACY_STORAGE_KEY = 'unigraph_task_queue';
  const completionById = new Map();
  let audioContext = null;
  let tasks = load();
  const expandedTasks = new Set();
  const renderedStepCounts = new Map();
  const timelineScrollStates = new Map();

  function storageKey() {
    const userUuid = Auth.getUserInfo()?.uuid || 'anonymous';
    return `unigraph_task_queue:${userUuid}`;
  }

  function sanitizeKwargs(kwargs) {
    const safe = { ...(kwargs || {}) };
    delete safe.user_token;
    return safe;
  }

  function load() {
    try {
      const value = JSON.parse(localStorage.getItem(storageKey()) || '[]');
      localStorage.removeItem(LEGACY_STORAGE_KEY);
      return Array.isArray(value)
        ? value.map((task) => ({ ...task, kwargs: sanitizeKwargs(task.kwargs) }))
        : [];
    } catch (error) {
      return [];
    }
  }

  function save() {
    localStorage.setItem(storageKey(), JSON.stringify(tasks));
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
      const notification = new Notification(t('UniGraph 后台任务已完成'), {
        body: [t(task.displayName), task.objectName].filter(Boolean).join(': '),
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
    return t({
      PENDING: '等待中',
      STARTED: '执行中',
      PROGRESS: '执行中',
      RETRY: '重试中',
      SUCCESS: '已完成',
      FAILURE: '失败',
      REVOKE: '已撤销',
      REVOKED: '已撤销',
    }[state] || state);
  }

  function stateColor(state) {
    if (state === 'SUCCESS') return 'var(--claude-success-500)';
    if (['FAILURE', 'REVOKE', 'REVOKED'].includes(state)) return 'var(--claude-destructive)';
    return 'var(--task-running-color, #3b82f6)';
  }

  function formatTaskTime(value) {
    const text = String(value || '');
    const match = text.match(/(\d{1,2}):(\d{2}):(\d{2})/);
    if (match) return `${match[1].padStart(2, '0')}:${match[2]}:${match[3]}`;
    return new Date().toLocaleTimeString(getLocale() === 'en' ? 'en-US' : 'zh-CN', { hour12: false });
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

  function emitTaskUpdate(task) {
    window.dispatchEvent(new CustomEvent('unigraph:task-updated', {
      detail: { task: { ...task, kwargs: sanitizeKwargs(task.kwargs) } },
    }));
  }

  function isTaskCenterVisible(task) {
    return task.name !== 'knowledge_graph.ask';
  }

  function render() {
    const panel = document.getElementById('task-panel');
    if (!panel) return;

    const visibleTasks = tasks.filter(isTaskCenterVisible);
    const running = visibleTasks.filter((task) => ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state));
    const headerBadge = panel.querySelector('[data-task-running-count]');
    if (headerBadge) headerBadge.textContent = t(`${running.length} 进行中`);

    const fabBadge = document.querySelector('[data-task-fab-count]');
    const fab = document.getElementById('task-fab-wrapper');
    if (fab) {
      const palette = ['#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af'];
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

    if (!visibleTasks.length) {
      container.innerHTML = `<div class="task-empty">${escapeHtml(t('暂无后台任务'))}</div>`;
      return;
    }

    const previousScrollTop = container.scrollTop;
    container.querySelectorAll('.task-card').forEach((card) => {
      const timeline = card.querySelector('.task-detail:not(.hidden) .task-timeline');
      if (!timeline) return;
      const distanceFromBottom = timeline.scrollHeight - timeline.clientHeight - timeline.scrollTop;
      timelineScrollStates.set(card.dataset.taskId, {
        scrollTop: timeline.scrollTop,
        followLatest: distanceFromBottom <= 24,
      });
    });
    container.innerHTML = visibleTasks.slice().reverse().map((task) => {
      const progress = Math.max(0, Math.min(100, Number(task.progress) || 0));
      const canCancel = ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state);
      const canRetry = !canCancel && task.state !== 'SUCCESS';
      const isOpen = expandedTasks.has(task.uid);
      const steps = getTaskSteps(task);
      const previousStepCount = renderedStepCounts.get(task.uid) ?? steps.length;
      const title = [t(task.displayName), task.objectName].filter(Boolean).join(': ');
      const statusText = canCancel ? `${Math.round(progress)}%` : (task.state === 'SUCCESS' ? t('完成') : stateLabel(task.state));
      const taskColor = stateColor(task.state);
      const stepMarkup = steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        const description = t(step.detail || (Number(step.progress) > 0 && Number(step.progress) < 100
          ? `已处理 ${Math.round(Number(step.progress))}%`
          : ''));
        return `
          <div class="task-step${isLast ? ' is-latest' : ''}${isLast && canCancel ? ' is-running' : ''}${index >= previousStepCount ? ' is-new' : ''}" style="--step-color:${taskColor};">
            <span class="task-step__dot"></span>
            <div class="task-step__head">
              <span class="task-step__label">${escapeHtml(t(step.label))}</span>
              <span class="task-step__time">${escapeHtml(formatTaskTime(step.time))}</span>
            </div>
            ${description ? `<p class="task-step__description">${escapeHtml(description)}</p>` : ''}
          </div>`;
      }).join('');
      return `
        <div class="task-card" data-task-id="${escapeHtml(task.uid)}" style="--task-state-color:${taskColor};">
          <div class="task-card__summary">
            <button type="button" onclick="TaskManager.toggle(this)" class="task-card__toggle" aria-label="${escapeHtml(t(isOpen ? '收起任务日志' : '展开任务日志'))}">
              <i data-lucide="chevron-right" class="task-chevron" style="transform:${isOpen ? 'rotate(90deg)' : 'rotate(0deg)'}"></i>
              ${task.state === 'SUCCESS'
                ? '<i data-lucide="check" class="task-status-check" style="color:' + taskColor + ';"></i>'
                : '<span class="task-status-dot" style="background:' + taskColor + ';"></span>'}
              <p class="task-card__title">${escapeHtml(title || t('后台任务'))}<span class="task-card__start-time">${escapeHtml(formatTaskTime(task.createdAt))}</span></p>
            </button>
            <div class="task-inline-actions">
              ${canCancel ? `<button type="button" onclick="TaskManager.pause('${escapeHtml(task.uid)}')" class="task-inline-action" title="${escapeHtml(t('暂停'))}" aria-label="${escapeHtml(t('暂停'))}"><i data-lucide="pause"></i></button>` : ''}
              ${(canCancel || canRetry) ? `<button type="button" onclick="TaskManager.retry('${escapeHtml(task.uid)}')" class="task-inline-action" title="${escapeHtml(t('重启'))}" aria-label="${escapeHtml(t('重启'))}"><i data-lucide="rotate-ccw"></i></button>` : ''}
              <button type="button" onclick="TaskManager.remove('${escapeHtml(task.uid)}')" class="task-inline-action task-delete-action" title="${escapeHtml(t('删除'))}" aria-label="${escapeHtml(t('删除'))}"><i data-lucide="trash-2"></i></button>
            </div>
            <span class="task-card__state">${escapeHtml(statusText)}</span>
          </div>
          <div class="task-progress${canCancel ? ' is-running' : ''}"><div class="task-progress__value" style="width:${progress}%;background:${taskColor};"></div></div>
          <div class="task-detail${isOpen ? '' : ' hidden'}">
            <div class="task-timeline">${stepMarkup}</div>
          </div>
        </div>`;
    }).join('');
    visibleTasks.forEach((task) => renderedStepCounts.set(task.uid, getTaskSteps(task).length));
    window.lucide?.createIcons();
    requestAnimationFrame(() => {
      container.scrollTop = previousScrollTop;
      container.querySelectorAll('.task-detail:not(.hidden) .task-timeline').forEach((timeline) => {
        const taskId = timeline.closest('.task-card')?.dataset.taskId;
        const saved = timelineScrollStates.get(taskId);
        const maxScrollTop = Math.max(0, timeline.scrollHeight - timeline.clientHeight);
        timeline.scrollTop = !saved || saved.followLatest
          ? maxScrollTop
          : Math.min(saved.scrollTop, maxScrollTop);
        timeline.addEventListener('scroll', () => {
          const distanceFromBottom = timeline.scrollHeight - timeline.clientHeight - timeline.scrollTop;
          timelineScrollStates.set(taskId, {
            scrollTop: timeline.scrollTop,
            followLatest: distanceFromBottom <= 24,
          });
        }, { passive: true });
      });
    });
  }

  function toggle(button) {
    const card = button.closest('.task-card');
    const detail = card?.querySelector('.task-detail');
    const chevron = button.querySelector('.task-chevron');
    if (!detail) return;
    const isOpen = detail.classList.contains('hidden');
    if (isOpen) expandedTasks.add(card.dataset.taskId);
    else expandedTasks.delete(card.dataset.taskId);
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (chevron) gsap.to(chevron, { rotation: isOpen ? 90 : 0, duration: reducedMotion ? 0 : 0.2, ease: 'power2.out', overwrite: 'auto' });
    if (isOpen) {
      detail.classList.remove('hidden');
      if (!reducedMotion) {
        gsap.fromTo(detail, { autoAlpha: 0, y: -6 }, {
          autoAlpha: 1,
          y: 0,
          duration: 0.24,
          ease: 'power2.out',
          overwrite: 'auto',
          onComplete: () => gsap.set(detail, { clearProps: 'opacity,visibility,transform' }),
        });
      }
      requestAnimationFrame(() => {
        const container = card.closest('[data-task-list]');
        if (!container) return;
        const timeline = card.querySelector('.task-timeline');
        if (timeline) {
          timeline.scrollTop = timeline.scrollHeight;
          timelineScrollStates.set(card.dataset.taskId, {
            scrollTop: timeline.scrollTop,
            followLatest: true,
          });
        }
        const target = card.offsetTop + card.offsetHeight - container.clientHeight;
        container.scrollTo({ top: Math.max(0, target), behavior: 'smooth' });
      });
    } else if (reducedMotion) {
      detail.classList.add('hidden');
    } else {
      gsap.to(detail, {
        autoAlpha: 0,
        y: -5,
        duration: 0.16,
        ease: 'power1.in',
        overwrite: 'auto',
        onComplete: () => {
          detail.classList.add('hidden');
          gsap.set(detail, { clearProps: 'opacity,visibility,transform' });
        },
      });
    }
  }

  function updateFromStatus(task, status) {
    const meta = status.meta || {};
    const previousMessage = task.message;
    task.state = status.state || task.state;
    if (task.state === 'SUCCESS' && (meta.type === 'error' || meta.error)) task.state = 'FAILURE';
    task.progress = task.state === 'SUCCESS' ? 100 : Number(meta.progress ?? task.progress ?? 0);
    const errorMessage = typeof meta.error === 'string' ? meta.error : meta.error?.message;
    task.message = meta.message || errorMessage || stateLabel(task.state);
    if (typeof meta.partial_answer === 'string') task.partialAnswer = meta.partial_answer;
    if (task.state === 'SUCCESS' && typeof meta.data?.results === 'string') {
      task.partialAnswer = meta.data.results;
    }
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
    }
    task.result = meta.data ?? meta.result ?? null;
    persistAndRender();
    emitTaskUpdate(task);
  }

  async function poll(task, taskUid = task.uid) {
    let statusFailures = 0;
    while (task.uid === taskUid && ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)) {
      await new Promise((resolve) => setTimeout(resolve, task.name === 'knowledge_graph.ask' ? 500 : 1500));
      if (task.uid !== taskUid) return null;
      let response;
      try {
        response = await KgBaseAPI.task.getStatus(taskUid);
        statusFailures = 0;
      } catch (error) {
        statusFailures += 1;
        if (statusFailures < 5) continue;
        task.state = 'FAILURE';
        task.message = '无法获取任务状态，请检查后端服务后重试';
        task.steps = Array.isArray(task.steps) ? task.steps : [];
        task.steps.push({
          label: '任务状态同步失败',
          detail: error?.message || '网络连接异常',
          time: formatTaskTime(new Date().toLocaleString()),
          progress: task.progress,
        });
        persistAndRender();
        throw new Error(task.message, { cause: error });
      }
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
      notify(t(`${task.displayName}已完成`));
      return task.result;
    }
    if (task.state === 'REVOKE' || task.state === 'REVOKED') return null;
    throw new Error(t(task.message || `${task.displayName}失败`));
  }

  async function submit(name, displayName, objectName, kwargs) {
    const safeKwargs = sanitizeKwargs(kwargs);
    const response = await KgBaseAPI.task.submit(name, safeKwargs);
    if (response.code !== 200 || !response.data?.task_id) {
      throw new Error(response.msg || '任务提交失败');
    }
    const task = {
      uid: response.data.task_id,
      name,
      displayName,
      objectName,
      kwargs: safeKwargs,
      state: 'PENDING',
      progress: 0,
      message: '任务已创建',
      createdAt: new Date().toLocaleString(),
      updatedAt: new Date().toLocaleString(),
      steps: [],
      result: null,
      completionNotified: false,
      partialAnswer: '',
    };
    task.steps.push({ label: task.message, time: formatTaskTime(task.createdAt), progress: 0 });
    tasks.push(task);
    persistAndRender();
    emitTaskUpdate(task);
    notify(t(`${displayName}任务已提交`));
    const taskUid = task.uid;
    const completion = poll(task, taskUid);
    completionById.set(taskUid, completion);
    completion.then(
      () => completionById.delete(taskUid),
      () => completionById.delete(taskUid),
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
    notify(t('任务已撤销'));
  }

  async function retry(uid) {
    const task = tasks.find((item) => item.uid === uid);
    if (!task) return;
    if (['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)) {
      await cancel(uid);
    }
    const response = await KgBaseAPI.task.submit(task.name, task.kwargs || {});
    if (response.code !== 200 || !response.data?.task_id) {
      throw new Error(response.msg || '任务重启失败');
    }

    const newUid = response.data.task_id;
    const wasExpanded = expandedTasks.delete(uid);
    completionById.delete(uid);
    renderedStepCounts.delete(uid);
    timelineScrollStates.delete(uid);

    task.uid = newUid;
    task.state = 'PENDING';
    task.progress = 0;
    task.message = '任务已重新启动';
    task.createdAt = new Date().toLocaleString();
    task.updatedAt = task.createdAt;
    task.steps = [{ label: task.message, time: formatTaskTime(task.createdAt), progress: 0 }];
    task.result = null;
    task.completionNotified = false;
    if (wasExpanded) expandedTasks.add(newUid);
    persistAndRender();
    notify(t(`${task.displayName}已重新启动`));

    const completion = poll(task, newUid);
    completionById.set(newUid, completion);
    completion.then(
      () => completionById.delete(newUid),
      () => completionById.delete(newUid),
    );
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
    if (['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)) await cancel(uid);
    tasks = tasks.filter((item) => item.uid !== uid);
    expandedTasks.delete(uid);
    renderedStepCounts.delete(uid);
    timelineScrollStates.delete(uid);
    persistAndRender();
  }

  function resume() {
    tasks.filter((task) => ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state)).forEach((task) => {
      if (completionById.has(task.uid)) return;
      const taskUid = task.uid;
      const completion = poll(task, taskUid).catch(() => null);
      completionById.set(taskUid, completion);
      completion.then(
        () => completionById.delete(taskUid),
        () => completionById.delete(taskUid),
      );
    });
  }

  function init() {
    render();
    document.addEventListener('pointerdown', primeAudio, { once: true });
    window.addEventListener('unigraph:preferences-changed', primeAudio);
    window.addEventListener('unigraph:language-change', render);
    if (typeof Auth !== 'undefined' && Auth.isLogin()) resume();
  }

  document.addEventListener('DOMContentLoaded', init);
  if (document.readyState !== 'loading') init();

  function getTasks() {
    return tasks.map((task) => ({ ...task, kwargs: sanitizeKwargs(task.kwargs) }));
  }

  return { submit, cancel, pause, retry, remove, toggle, render, resume, getTasks };
})();
