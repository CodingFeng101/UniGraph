/* Generated from pages/graph-app.html; keep behavior changes in the source controller during migration. */
import { copyText } from '@/utils/clipboard';
import { gsap } from 'gsap';
import { validateUploadSize } from '@/utils/upload';
import { displayChatName } from '@/utils/chat-name';
import { t } from '@/services/i18n';
import {
  normalizeChatSources as normalizeSources,
  renderAnswerWithCitations,
  renderChatMarkdown as renderMarkdown,
} from '@/utils/chat-content';

export function createGraphApplicationViewController() {
  const { API, Auth, KgBaseAPI } = window;

lucide.createIcons();

var currentShare = null;
var messageSequence = 0;
var motionContext = null;
var effortRetrievalDepth = { Low: 1, Medium: 2, High: 3, Max: 4 };

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function animateElement(element, fromVars, toVars) {
  if (!element || prefersReducedMotion()) return;
  var tween = function() {
    gsap.fromTo(element, fromVars, {
      duration: 0.32,
      ease: 'power2.out',
      overwrite: 'auto',
      ...toVars,
      onComplete: function() {
        gsap.set(element, { clearProps: 'opacity,visibility,transform,will-change' });
      },
    });
  };
  if (motionContext) motionContext.add(tween);
  else tween();
}

function setChatMode(empty) {
  var main = document.getElementById('app-main');
  var composer = document.getElementById('chat-composer');
  var outline = document.getElementById('chat-outline');
  main?.classList.toggle('chat-is-empty', empty);
  outline?.classList.toggle('hidden', empty);
  animateElement(composer, { autoAlpha: 0, y: empty ? 14 : -10, scale: 0.99 }, { autoAlpha: 1, y: 0, scale: 1 });
}

function renderEmptyState() {
  var container = document.getElementById('chat-message-list');
  if (!container) return;
  container.style.visibility = 'visible';
  container.innerHTML = '<section class="chat-empty-state" aria-label="新对话">有什么可以帮你的？</section>';
  setChatMode(true);
  renderChatOutline();
}

function buildShareUrl(publicId) {
  return new URL('/unigraph/share/' + encodeURIComponent(publicId), window.location.origin).toString();
}

function renderShareState(share) {
  currentShare = share || null;
  var emptyState = document.getElementById('share-empty-state');
  var activeState = document.getElementById('share-active-state');
  var subtitle = document.getElementById('share-subtitle');
  var link = document.getElementById('share-link');
  if (emptyState) emptyState.classList.toggle('hidden', Boolean(share));
  if (activeState) activeState.classList.toggle('hidden', !share);
  if (link) link.value = share ? buildShareUrl(share.public_id) : '';
  if (subtitle) {
    subtitle.textContent = share
      ? `已分享 ${share.message_count} 条消息，之后的新消息不会自动加入`
      : '创建截至当前消息的只读快照';
  }
}

async function toggleShareModal() {
  var modal = document.getElementById('share-modal');
  if (!modal) return;
  if (!modal.classList.contains('hidden')) {
    modal.classList.add('hidden');
    return;
  }
  if (!currentChatUuid) {
    showToast('请先发送一条消息再分享');
    return;
  }
  modal.classList.remove('hidden');
  renderShareState(null);
  var subtitle = document.getElementById('share-subtitle');
  if (subtitle) subtitle.textContent = '正在读取分享状态';
  var response = await KgBaseAPI.chatLibrary.getShare(currentChatUuid);
  if (response.code !== 200) {
    modal.classList.add('hidden');
    showToast(response.msg || '读取分享状态失败');
    return;
  }
  renderShareState(response.data);
}

async function copyShareLink() {
  var link = document.getElementById('share-link');
  if (!link || !link.value) return;
  await copyText(link.value);
  showToast('分享链接已复制');
}

async function createShareLink() {
  if (!currentChatUuid) return;
  var response = await KgBaseAPI.chatLibrary.createShare(currentChatUuid);
  if (response.code !== 200 || !response.data) {
    showToast(response.msg || '创建分享链接失败');
    return;
  }
  renderShareState(response.data);
  showToast('分享链接已创建');
}

async function updateShareSnapshot() {
  if (!currentChatUuid || !currentShare) return;
  var response = await KgBaseAPI.chatLibrary.updateShare(currentChatUuid);
  if (response.code !== 200 || !response.data) {
    showToast(response.msg || '更新分享失败');
    return;
  }
  renderShareState(response.data);
  showToast('分享快照已更新');
}

async function rotateShareLink() {
  if (!currentChatUuid || !currentShare) return;
  var confirmed = typeof window.confirmAction === 'function'
    ? await window.confirmAction({
      title: '重新生成分享链接',
      message: '重新生成后，当前分享链接会立即失效，已获得旧链接的人将无法继续访问。',
      confirmText: '重新生成',
    })
    : window.confirm('重新生成后，当前分享链接会立即失效。是否继续？');
  if (!confirmed) return;
  var response = await KgBaseAPI.chatLibrary.rotateShare(currentChatUuid);
  if (response.code !== 200 || !response.data) {
    showToast(response.msg || '重新生成分享链接失败');
    return;
  }
  renderShareState(response.data);
  showToast('新分享链接已生成，旧链接已失效');
}

async function stopSharing() {
  if (!currentChatUuid || !currentShare) return;
  var response = await KgBaseAPI.chatLibrary.revokeShare(currentChatUuid);
  if (response.code !== 200) {
    showToast(response.msg || '停止分享失败');
    return;
  }
  renderShareState(null);
  showToast('已停止分享');
}

function showToast(message) {
  window.showToast(message);
}

function syncCurrentChatQuery(chatUuid) {
  var url = new URL(window.location.href);
  if (chatUuid) url.searchParams.set('chat', chatUuid);
  else url.searchParams.delete('chat');
  window.history.replaceState(window.history.state, '', url);
}

function copyMessage(button) {
  var group = button.closest('.group');
  var message = group?.querySelector('p') || button.closest('.max-w-[680px]')?.querySelector('p');
  var content = group?.dataset.rawMessage || message?.textContent || '';
  if (content) {
    copyText(content).then(function(copied) {
      showToast(copied ? '已复制' : '复制失败');
    });
  }
}

async function regenerateAnswer(button) {
  if (isStreaming) {
    showToast('正在生成回答，请稍候...');
    return;
  }
  var assistantGroup = button.closest('.chat-assistant-message');
  var userGroup = assistantGroup?.previousElementSibling;
  while (userGroup && !userGroup.classList.contains('chat-user-message')) {
    userGroup = userGroup.previousElementSibling;
  }
  var requestText = userGroup?.dataset.rawMessage || '';
  var messageUuid = userGroup?.dataset.messageUuid || '';
  if (!currentChatUuid || !requestText || !messageUuid) {
    showToast('当前消息暂时无法重新生成');
    return;
  }
  button.disabled = true;
  try {
    var response = await KgBaseAPI.chatLibrary.updateMessage(currentChatUuid, messageUuid, requestText);
    if (response.code !== 200) throw new Error(response.msg || '重新生成失败');
    while (userGroup.nextElementSibling) userGroup.nextElementSibling.remove();
    await streamAnswer(requestText, { message_uuid: messageUuid }, Promise.resolve());
  } catch (error) {
    if (document.body.contains(button)) button.disabled = false;
    showToast(error.message || '重新生成失败');
  }
}

function cancelUserMessageEdit(button) {
  var group = button.closest('.chat-user-message');
  var bubble = group?.querySelector('.chat-user-bubble');
  if (!group || !bubble || group.__originalBubbleHtml == null) return;
  bubble.innerHTML = group.__originalBubbleHtml;
  group.__originalBubbleHtml = null;
  group.classList.remove('is-editing');
  group.querySelector('.chat-user-actions')?.classList.remove('hidden');
  lucide.createIcons();
}

async function saveUserMessageEdit(button) {
  if (isStreaming) {
    showToast('正在生成回答，请稍候...');
    return;
  }
  var group = button.closest('.chat-user-message');
  var bubble = group?.querySelector('.chat-user-bubble');
  var textarea = group?.querySelector('.chat-inline-edit__input');
  if (!group || !bubble || !textarea) return;
  var parsed = parseMessageAttachments(group.dataset.rawMessage || '');
  var content = composeMessageText(textarea.value.trim(), parsed.attachments);
  if (!content) {
    showToast('消息内容不能为空');
    textarea.focus();
    return;
  }
  if (!currentChatUuid || !group.dataset.messageUuid) {
    showToast('消息尚未同步，请稍后再试');
    return;
  }
  button.disabled = true;
  button.textContent = '保存中…';
  try {
    var response = await KgBaseAPI.chatLibrary.updateMessage(
      currentChatUuid,
      group.dataset.messageUuid,
      content,
    );
    if (response.code !== 200) throw new Error(response.msg || '保存失败');
    group.dataset.rawMessage = content;
    group.dataset.question = questionLabel(content);
    group.__originalBubbleHtml = null;
    group.classList.remove('is-editing');
    bubble.innerHTML = renderSentAttachments(parsed.attachments) +
      (textarea.value.trim()
        ? '<p class="text-[15px] leading-relaxed whitespace-pre-wrap" style="color:var(--claude-foreground);">' + escapeHtml(textarea.value.trim()) + '</p>'
        : '');
    group.querySelector('.chat-user-actions')?.classList.remove('hidden');
    while (group.nextElementSibling) group.nextElementSibling.remove();
    lucide.createIcons();
    renderChatOutline();
    await streamAnswer(content, { message_uuid: group.dataset.messageUuid }, Promise.resolve());
  } catch (error) {
    if (document.body.contains(button)) {
      button.disabled = false;
      button.textContent = '保存';
    }
    showToast(error.message || '重新发送失败');
  }
}

function editUserMessage(button) {
  var group = button.closest('.chat-user-message');
  var bubble = group?.querySelector('.chat-user-bubble');
  if (!group || !bubble || group.classList.contains('is-editing')) return;
  var activeEditor = document.querySelector('.chat-user-message.is-editing .chat-inline-edit__cancel');
  if (activeEditor) cancelUserMessageEdit(activeEditor);
  var parsed = parseMessageAttachments(group.dataset.rawMessage || '');
  group.__originalBubbleHtml = bubble.innerHTML;
  group.classList.add('is-editing');
  group.querySelector('.chat-user-actions')?.classList.add('hidden');
  bubble.innerHTML = renderSentAttachments(parsed.attachments) +
    '<div class="chat-inline-edit">' +
      '<textarea rows="1" class="chat-inline-edit__input" aria-label="编辑消息"></textarea>' +
      '<div class="chat-inline-edit__actions">' +
        '<button type="button" onclick="cancelUserMessageEdit(this)" class="chat-inline-edit__button chat-inline-edit__cancel">取消</button>' +
        '<button type="button" onclick="saveUserMessageEdit(this)" class="chat-inline-edit__button chat-inline-edit__save">保存</button>' +
      '</div>' +
    '</div>';
  var textarea = bubble.querySelector('.chat-inline-edit__input');
  textarea.value = parsed.body;
  textarea.style.height = Math.min(Math.max(textarea.scrollHeight, 46), 180) + 'px';
  textarea.addEventListener('input', function() {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(Math.max(textarea.scrollHeight, 46), 180) + 'px';
  });
  textarea.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') cancelUserMessageEdit(bubble.querySelector('.chat-inline-edit__cancel'));
  });
  window.setTimeout(function() {
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
  }, prefersReducedMotion() ? 0 : 80);
}

function adjustTextareaHeight(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
}

function triggerChatAttachments() {
  document.getElementById('chat-attachment-input')?.click();
}

async function handleChatAttachments(input) {
  var files = Array.from(input?.files || []);
  input.value = '';
  for (var index = 0; index < files.length; index += 1) {
    var file = files[index];
    try {
      validateUploadSize(file);
      var response = await API.uploadFile(file);
      if (response.code !== 200 || !response.data?.url) {
        throw new Error(response.msg || '附件上传失败');
      }
      pendingAttachments.push({
        name: file.name,
        url: response.data.url,
        extension: (file.name.split('.').pop() || 'FILE').toUpperCase(),
      });
      renderChatAttachments();
      updateSendBtn();
    } catch (error) {
      showToast(error.message || '附件上传失败');
    }
  }
}

function removeChatAttachment(index) {
  pendingAttachments.splice(index, 1);
  renderChatAttachments();
  updateSendBtn();
}

function renderChatAttachments() {
  var container = document.getElementById('chat-attachment-list');
  if (!container) return;
  container.classList.toggle('hidden', pendingAttachments.length === 0);
  container.innerHTML = pendingAttachments.map(function(attachment, index) {
    return '<article class="chat-attachment-card" title="' + escapeHtml(attachment.name) + '">' +
      '<button type="button" onclick="removeChatAttachment(' + index + ')" class="chat-attachment-card__remove" aria-label="移除附件"><i data-lucide="x" style="width:13px;height:13px;"></i></button>' +
      '<span class="chat-attachment-card__name">' + escapeHtml(attachment.name) + '</span>' +
      '<span class="chat-attachment-card__type">' + escapeHtml(attachment.extension || 'FILE') + '</span>' +
      '</article>';
  }).join('');
  lucide.createIcons();
  container.querySelectorAll('.chat-attachment-card').forEach(function(card, index) {
    animateElement(card, { autoAlpha: 0, y: 8, scale: 0.97 }, { autoAlpha: 1, y: 0, scale: 1, delay: index * 0.035 });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  updateSendBtn();
  var ta = document.getElementById('message-input');
  if (ta) adjustTextareaHeight(ta);
});

function toggleModelDropdown() {
  var dropdown = document.getElementById('model-dropdown');
  dropdown.classList.toggle('hidden');
  if (dropdown.classList.contains('hidden')) {
    document.getElementById('effort-panel').classList.add('hidden');
    document.getElementById('more-models-panel').classList.add('hidden');
  }
}

function toggleEffortPanel() {
  var panel = document.getElementById('effort-panel');
  document.getElementById('more-models-panel').classList.add('hidden');
  panel.classList.toggle('hidden');
}

function toggleMoreModelsPanel() {
  var panel = document.getElementById('more-models-panel');
  document.getElementById('effort-panel').classList.add('hidden');
  panel.classList.toggle('hidden');
}

function selectModel(el, name, modelUuid, notify = true) {
  selectedLlmModelUuid = modelUuid || null;
  document.getElementById('model-value').textContent = name;
  var currentModelItem = document.getElementById('current-model-item');
  currentModelItem.innerHTML = '<div class="flex items-center justify-between"><span class="text-[13px] font-medium" style="color:var(--claude-foreground);">' + name + '</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
  document.getElementById('model-dropdown').classList.add('hidden');
  renderOtherModels();
  if (notify) showToast('已切换模型：' + name);
}

function renderOtherModels() {
  var panel = document.querySelector('#more-models-panel .px-2.space-y-0\\.5');
  if (!panel) return;
  panel.innerHTML = '';
  var otherModels = availableLlmModels.filter(function(model) {
    return model.uuid !== selectedLlmModelUuid;
  });
  if (!otherModels.length) {
    panel.innerHTML = '<div class="px-2.5 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">暂无其它已配置模型</div>';
    return;
  }
  otherModels.forEach(function(model) {
    var item = document.createElement('button');
    item.type = 'button';
    item.className = 'w-full px-2 py-1.5 rounded-lg text-left text-[12px] cursor-pointer';
    item.style.cssText = 'background:none;border:none;color:var(--claude-foreground);';
    item.textContent = model.name;
    item.onclick = function() { selectModel(item, model.name, model.uuid); };
    panel.appendChild(item);
  });
}

function selectEffort(level) {
  document.getElementById('effort-value').textContent = level;
  document.getElementById('effort-label').textContent = level;
  var levels = ['Low', 'Medium', 'High', 'Max'];
  var container = document.querySelector('#effort-panel .space-y-0\\.5');
  container.innerHTML = '';
  levels.forEach(function(lv) {
    var div = document.createElement('div');
    div.className = 'px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]';
    div.setAttribute('onclick', "selectEffort('" + lv + "')");
    if (lv === level) {
      var badge = lv === 'Low' ? '<span class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:var(--claude-accent);color:var(--claude-muted-foreground);">Default</span>' : '';
      div.innerHTML = '<div class="flex items-center justify-between"><div class="flex items-center gap-1.5"><span class="text-[13px] font-medium" style="color:var(--claude-foreground);">' + lv + ' · ' + effortRetrievalDepth[lv] + ' 跳</span>' + badge + '</div><svg class="effort-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
    } else {
      div.innerHTML = '<span class="text-[13px]" style="color:var(--claude-muted-foreground);">' + lv + ' · ' + effortRetrievalDepth[lv] + ' 跳</span>';
    }
    container.appendChild(div);
  });
  showToast('已切换检索档位：' + level + '（' + effortRetrievalDepth[level] + ' 跳）');
}

function getSelectedEffort() {
  var level = document.getElementById('effort-value')?.textContent || 'Low';
  return effortRetrievalDepth[level] ? level : 'Low';
}

function hasRunningQuestionTask(chatUuid) {
  if (!chatUuid || !window.TaskManager?.getTasks) return false;
  return window.TaskManager.getTasks().some(function(task) {
    return task.name === 'knowledge_graph.ask' &&
      task.kwargs?.obj_data?.chat_library_uuid === chatUuid &&
      ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state);
  });
}

function updateSendBtn() {
  var input = document.getElementById('message-input');
  var btn = document.getElementById('send-btn');
  if (input.value.trim() || pendingAttachments.length) {
    btn.style.background = 'var(--claude-primary)';
    btn.style.color = 'var(--claude-primary-foreground)';
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
  } else {
    btn.style.background = 'var(--claude-accent)';
    btn.style.color = 'var(--claude-muted-foreground)';
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
  }
}

async function sendMessage() {
  var input = document.getElementById('message-input');
  var text = input.value.trim();
  if (!text && !pendingAttachments.length) return;
  var requestText = composeMessageText(text, pendingAttachments);
  if (isStreaming || hasRunningQuestionTask(currentChatUuid)) {
    showToast('正在生成回答，请稍候...');
    return;
  }
  if (!currentGraphUuid) {
    showToast('未找到可用知识图谱');
    return;
  }
  try {
    await ensureCurrentChat(text || pendingAttachments[0]?.name);
  } catch (error) {
    showToast(error.message || '创建对话失败');
    return;
  }

  var userMessageElement = appendUserMessage(requestText);
  input.value = '';
  input.style.height = 'auto';
  pendingAttachments = [];
  renderChatAttachments();
  updateSendBtn();

  var savedMessage;
  try {
    savedMessage = await saveConversationMessage('user', requestText);
    if (userMessageElement && savedMessage?.message_uuid) {
      userMessageElement.dataset.messageUuid = savedMessage.message_uuid;
    }
  } catch (error) {
    showToast(error.message || 'Failed to save conversation');
    return;
  }

  var titlePromise = KgBaseAPI.chatLibrary.generateTitle(currentChatUuid, requestText)
    .then(function(response) {
      if (controllerDestroyed) return;
      if (response.code === 200) {
        if (response.data) {
          currentChatName = response.data;
          setConversationTitle(response.data);
        }
        return loadChatHistory();
      }
    })
    .catch(function() {
      // Title generation is secondary and must never block the answer.
    });

  return streamAnswer(requestText, savedMessage, titlePromise);
}

async function streamAnswer(requestText, savedMessage, titlePromise) {
  var aiDiv = appendAIThinking();
  var thinkingEl = aiDiv.querySelector('.ai-thinking');
  var answerEl = aiDiv.querySelector('.ai-answer');

  isStreaming = true;
  var finalAnswer = '';
  var finalSources = {};
  var hasAnswerDelta = false;
  var hasRenderedError = false;
  var renderFrame = null;
  var displayedAnswer = '';
  var finalReceived = false;
  var resolveStreamFlush;
  var streamFlush = new Promise(function(resolve) { resolveStreamFlush = resolve; });

  function finishStreamFlush() {
    if (!resolveStreamFlush) return;
    resolveStreamFlush();
    resolveStreamFlush = null;
  }

  function renderAskFailure(message) {
    if (hasRenderedError) return;
    hasRenderedError = true;
    if (renderFrame != null) cancelAnimationFrame(renderFrame);
    renderFrame = null;
    var safeMessage = normalizeAskErrorMessage(message);
    failThinkingLog(thinkingEl, safeMessage);
    answerEl.innerHTML = '<div class="ai-answer-error" role="alert">' +
      '<i data-lucide="circle-alert" aria-hidden="true"></i>' +
      '<span>' + escapeHtml(safeMessage) + '</span></div>';
    lucide.createIcons();
    scrollToBottom();
    finishStreamFlush();
  }

  function scheduleStreamRender() {
    if (renderFrame != null) return;
    renderFrame = requestAnimationFrame(function renderStreamingFrame() {
      renderFrame = null;
      if (!finalAnswer.startsWith(displayedAnswer)) displayedAnswer = '';
      var pendingLength = finalAnswer.length - displayedAnswer.length;
      if (pendingLength > 0) {
        var revealLength = Math.max(1, Math.min(28, Math.ceil(pendingLength / 9)));
        displayedAnswer = finalAnswer.slice(0, displayedAnswer.length + revealLength);
      }
      if (finalReceived && displayedAnswer.length >= finalAnswer.length) {
        answerEl.innerHTML = renderAnswerWithCitations(finalAnswer, finalSources);
        finishStreamFlush();
      } else {
        answerEl.innerHTML = renderMarkdown(displayedAnswer) + '<span class="streaming-caret" aria-hidden="true"></span>';
      }
      scrollToBottom();
      if (displayedAnswer.length < finalAnswer.length) scheduleStreamRender();
    });
  }

  var selectedEffort = getSelectedEffort();
  var taskChatUuid = currentChatUuid;
  var askTaskUid = null;
  var renderedTaskSteps = new Set();
  var thinkingQueueTail = Promise.resolve();
  var answerRevealUnlocked = false;
  var pendingAnswer = '';

  function enqueueThinkingStep(step, unlockAnswer = false) {
    var interval = step.metrics?.retrieval ? 760 : 620;
    thinkingQueueTail = thinkingQueueTail.then(async function() {
      if (controllerDestroyed || !thinkingEl?.isConnected) return;
      appendThinkingLog(
        thinkingEl,
        t(step.label),
        step.detail ? t(step.detail) : '',
        step.metrics?.retrieval || null,
      );
      if (unlockAnswer) {
        answerRevealUnlocked = true;
        if (pendingAnswer) {
          finalAnswer = pendingAnswer;
          scheduleStreamRender();
        }
      }
      await new Promise((resolve) => window.setTimeout(resolve, interval));
    });
    return thinkingQueueTail;
  }

  function applyAskTaskUpdate(task) {
    if (controllerDestroyed || !task || task.uid !== askTaskUid) return;
    var steps = Array.isArray(task.steps) ? task.steps : [];
    steps.forEach(function(step, index) {
      if (!step?.label || step.label === '任务已创建') return;
      var key = step.id != null ? String(step.id) : `${step.label}:${index}`;
      if (renderedTaskSteps.has(key)) return;
      renderedTaskSteps.add(key);
      var unlockAnswer = step.label === '正在生成回答';
      if (unlockAnswer) hasAnswerDelta = true;
      enqueueThinkingStep(step, unlockAnswer);
    });
    if (task.partialAnswer) {
      pendingAnswer = task.partialAnswer;
      if (!hasAnswerDelta) {
        hasAnswerDelta = true;
        enqueueThinkingStep({
          label: '正在生成回答',
          detail: '正在根据检索到的知识逐步生成回答',
          metrics: {},
        }, true);
      }
      if (answerRevealUnlocked) {
        finalAnswer = pendingAnswer;
        scheduleStreamRender();
      }
    }
    if (task.state === 'FAILURE') renderAskFailure(task.message || '请求失败');
  }

  function handleAskTaskUpdate(event) {
    applyAskTaskUpdate(event.detail?.task);
  }

  window.addEventListener('unigraph:task-updated', handleAskTaskUpdate);
  try {
    var submitted = await window.TaskManager.submit(
      'knowledge_graph.ask',
      '知识问答',
      currentChatName,
      {
        uuid: currentGraphUuid,
        obj_data: {
          message: requestText,
          infer: true,
          depth: effortRetrievalDepth[selectedEffort],
          chat_library_uuid: taskChatUuid,
          current_message_uuid: savedMessage?.message_uuid || null,
          llm_model_uuid: selectedLlmModelUuid,
          effort: selectedEffort,
        },
      },
    );
    askTaskUid = submitted.uid;
    var result = await submitted.completion;
    pendingAnswer = result?.results || pendingAnswer || finalAnswer;
    finalSources = result?.context_data || {};
    if (controllerDestroyed || !aiDiv.isConnected) return;
    if (!hasAnswerDelta && pendingAnswer) {
      hasAnswerDelta = true;
      enqueueThinkingStep({
        label: '正在生成回答',
        detail: '正在根据检索到的知识逐步生成回答',
        metrics: {},
      }, true);
    }
    await thinkingQueueTail;
    finalAnswer = pendingAnswer || finalAnswer;
    finalReceived = true;
    completeThinkingLog(thinkingEl);
    scheduleStreamRender();
    await streamFlush;
    if (finalAnswer) finalizeAssistantMessage(aiDiv, finalAnswer);
    await titlePromise;
    if (currentChatUuid === taskChatUuid) await loadChatHistory();
  } catch (error) {
    renderAskFailure(error.message || '请求失败');
  } finally {
    window.removeEventListener('unigraph:task-updated', handleAskTaskUpdate);
    isStreaming = false;
  }
}

function normalizeAskErrorMessage(message) {
  var text = String(message || '').trim();
  if (/401|unauthorized|无效的令牌|invalid\s+(token|api\s*key)/i.test(text)) {
    return '当前模型凭据无效，请到个人中心重新配置 API Key';
  }
  if (/500:\s*error code|request id|v_api_error/i.test(text)) {
    return '模型服务调用失败，请检查模型配置或稍后重试';
  }
  return text || '请求失败，请稍后重试';
}

document.addEventListener('click', function(e) {
  var citation = e.target.closest('[data-citation]');
  if (citation && !e.target.closest('.source-popup')) {
    var shouldOpen = !citation.classList.contains('is-open');
    document.querySelectorAll('[data-citation].is-open').forEach(function(item) {
      hideCitationPopup(item);
    });
    if (shouldOpen) {
      showCitationPopup(citation);
    }
    return;
  }
  if (!e.target.closest('.source-popup')) {
    document.querySelectorAll('[data-citation].is-open').forEach(function(item) {
      hideCitationPopup(item);
    });
  }
  var modelDropdown = document.getElementById('model-dropdown');
  if (modelDropdown && !modelDropdown.contains(e.target) && !e.target.closest('[data-role="model-trigger"]')) {
    modelDropdown.classList.add('hidden');
    document.getElementById('effort-panel').classList.add('hidden');
    document.getElementById('more-models-panel').classList.add('hidden');
  }
  var shareModal = document.getElementById('share-modal');
  if (shareModal && !shareModal.contains(e.target) && !e.target.closest('[data-role="share-trigger"]')) {
    shareModal.classList.add('hidden');
  }
  var graphMenu = document.getElementById('kg-selector-menu');
  if (graphMenu && !graphMenu.contains(e.target) && !e.target.closest('[data-role="kg-trigger"]')) {
    graphMenu.classList.add('hidden');
  }
});

var citationCloseTimers = new WeakMap();

function isCitationPopoverOpen(popup) {
  try {
    return popup.matches(':popover-open');
  } catch {
    return false;
  }
}

function showCitationPopup(citation) {
  var popup = citation?.querySelector('.source-popup');
  if (!popup) return;
  citation.classList.add('is-open');
  citation.setAttribute('aria-expanded', 'true');
  if (typeof popup.showPopover === 'function' && !isCitationPopoverOpen(popup)) {
    try {
      popup.showPopover();
    } catch {
      // Fall back to the existing positioned panel in browsers without popover support.
    }
  }
  positionCitationPopup(citation);
}

function hideCitationPopup(citation) {
  var popup = citation?.querySelector('.source-popup');
  citation.classList.remove('is-open');
  citation.setAttribute('aria-expanded', 'false');
  if (popup && typeof popup.hidePopover === 'function' && isCitationPopoverOpen(popup)) {
    try {
      popup.hidePopover();
    } catch {
      // The panel may already have been dismissed by the browser.
    }
  }
}

function positionCitationPopup(citation) {
  var popup = citation?.querySelector('.source-popup');
  if (!popup) return;
  var pageElement = document.getElementById('chat-message-list') || document.getElementById('app-main');
  var page = pageElement?.getBoundingClientRect();
  var boundary = {
    left: Math.max(12, page?.left || 0) + 12,
    right: Math.min(window.innerWidth - 12, page?.right || window.innerWidth) - 12,
    top: Math.max(12, page?.top || 0) + 12,
    bottom: Math.min(window.innerHeight - 12, page?.bottom || window.innerHeight) - 12,
  };
  var heightCap = citation.classList.contains('citation-tag--overview') ? 320 : 300;
  popup.classList.remove('source-popup--below');
  popup.style.removeProperty('max-height');
  popup.style.maxWidth = Math.max(220, boundary.right - boundary.left) + 'px';
  popup.style.setProperty('--source-popup-shift-x', '0px');

  var citationRect = citation.getBoundingClientRect();
  var spaceAbove = Math.max(0, citationRect.top - boundary.top - 8);
  var spaceBelow = Math.max(0, boundary.bottom - citationRect.bottom - 8);

  if (typeof popup.showPopover === 'function' && isCitationPopoverOpen(popup)) {
    var desiredHeight = Math.min(popup.scrollHeight, heightCap);
    var showBelowInTopLayer = desiredHeight > spaceAbove && spaceBelow > spaceAbove;
    var availableHeight = showBelowInTopLayer ? spaceBelow : spaceAbove;
    var maxHeight = Math.max(96, Math.min(heightCap, Math.floor(availableHeight)));
    popup.style.position = 'fixed';
    popup.style.transform = 'none';
    popup.style.maxHeight = maxHeight + 'px';

    var topLayerRect = popup.getBoundingClientRect();
    var left = Math.min(Math.max(citationRect.left, boundary.left), boundary.right - topLayerRect.width);
    var top = showBelowInTopLayer
      ? citationRect.bottom + 8
      : citationRect.top - topLayerRect.height - 8;
    popup.style.left = Math.round(Math.max(boundary.left, left)) + 'px';
    popup.style.top = Math.round(Math.min(Math.max(top, boundary.top), boundary.bottom - topLayerRect.height)) + 'px';
    popup.style.right = 'auto';
    popup.style.bottom = 'auto';
    return;
  }

  var popupRect = popup.getBoundingClientRect();
  var shiftX = 0;
  if (popupRect.right > boundary.right) shiftX -= popupRect.right - boundary.right;
  if (popupRect.left + shiftX < boundary.left) shiftX += boundary.left - (popupRect.left + shiftX);
  popup.style.setProperty('--source-popup-shift-x', Math.round(shiftX) + 'px');

  var showBelow = popupRect.height > spaceAbove && spaceBelow > spaceAbove;
  popup.classList.toggle('source-popup--below', showBelow);
  popup.style.maxHeight = Math.max(96, Math.min(heightCap, Math.floor(showBelow ? spaceBelow : spaceAbove))) + 'px';
}

function scheduleCitationClose(citation) {
  var existingTimer = citationCloseTimers.get(citation);
  if (existingTimer) window.clearTimeout(existingTimer);
  var timer = window.setTimeout(function() {
    citationCloseTimers.delete(citation);
    if (citation.matches(':hover') || citation.contains(document.activeElement)) return;
    hideCitationPopup(citation);
    citation.blur();
  }, 180);
  citationCloseTimers.set(citation, timer);
}

document.addEventListener('pointerover', function(e) {
  var citation = e.target.closest('[data-citation]');
  if (!citation) return;
  var existingTimer = citationCloseTimers.get(citation);
  if (existingTimer) {
    window.clearTimeout(existingTimer);
    citationCloseTimers.delete(citation);
  }
  showCitationPopup(citation);
});

document.addEventListener('focusin', function(e) {
  var citation = e.target.closest('[data-citation]');
  if (citation) showCitationPopup(citation);
});

document.addEventListener('pointerout', function(e) {
  var citation = e.target.closest('[data-citation]');
  if (!citation || citation.contains(e.relatedTarget)) return;
  scheduleCitationClose(citation);
});

document.querySelectorAll('.trace-toggle').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var chevron = this.querySelector('.chevron-icon');
    var detail = this.nextElementSibling;
    if (detail && detail.classList.contains('step-detail')) {
      detail.style.opacity = detail.style.opacity === '0' ? '1' : '0';
      detail.style.maxHeight = detail.style.maxHeight === '0px' ? '200px' : '0px';
    } else {
      var body = this.closest('.trace-section').querySelector('.trace-body');
      if (body) {
        body.style.opacity = body.style.opacity === '0' ? '1' : '0';
        body.style.maxHeight = body.style.maxHeight === '0px' ? '800px' : '0px';
      }
    }
    if (chevron) {
      chevron.style.transform = chevron.style.transform === 'rotate(180deg)' ? 'rotate(0deg)' : 'rotate(180deg)';
    }
  });
});

// ===== API Integration =====
// Check login status
if (!Auth.requireAuth()) throw new Error('Not logged in');

// Get UUID from URL
const urlParams = window.getUniGraphSearchParams();
const kgBaseUuid = urlParams.get('uuid');

// State
var currentGraphUuid = null;
var currentChatUuid = null;
var currentChatName = '新对话';
var availableLlmModels = [];
var selectedLlmModelUuid = null;
var knowledgeGraphList = [];
var chatHistoryItems = [];
var chatSortAscending = false;
var isStreaming = false;
var resumedAskViews = new Map();
var controllerDestroyed = false;
var pendingAttachments = [];

// Update sidebar navigation links with UUID
function updateSidebarLinks(uuid) {
  if (!uuid) return;
  var infoLink = document.querySelector('a[data-title="信息"]');
  var designLink = document.querySelector('a[data-title="设计"]');
  var buildLink = document.querySelector('a[data-title="构建"]');
  if (infoLink) infoLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/info';
  if (designLink) designLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/structure';
  if (buildLink) buildLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/graph';
}

// HTML escape helper
function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/[&<>"']/g, function(m) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
  });
}

// Escape single quotes for inline onclick strings
function escapeQuotes(str) {
  if (str == null) return '';
  return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

// Scroll chat container to bottom
function scrollToBottom() {
  var container = document.getElementById('chat-container');
  if (container) container.scrollTop = container.scrollHeight;
}

// Clear the chat container
function clearChatContainer() {
  var container = document.getElementById('chat-message-list');
  messageSequence = 0;
  if (container) {
    container.style.visibility = 'visible';
    container.innerHTML = '';
  }
  renderChatOutline();
}

function showEmptyConversation() {
  clearChatContainer();
  renderEmptyState();
}

function questionLabel(text) {
  var parsed = parseMessageAttachments(text);
  return String(parsed.body || parsed.attachments[0]?.name || '')
    .split('\n')[0]
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 52) || '附件提问';
}

function parseMessageAttachments(text) {
  var source = String(text || '');
  var marker = source.match(/(?:^|\n)附件[：:]\s*\n/);
  if (!marker || marker.index == null) return { body: source.trim(), attachments: [] };
  var body = source.slice(0, marker.index).trim();
  var attachmentBlock = source.slice(marker.index + marker[0].length);
  var attachments = attachmentBlock.split('\n').map(function(line) {
    var match = line.trim().match(/^-\s+(.+?):\s+(\S+)\s*$/);
    if (!match) return null;
    var name = match[1].trim();
    return {
      name: name,
      url: match[2].trim(),
      extension: (name.split('.').pop() || 'FILE').toUpperCase(),
    };
  }).filter(Boolean);
  return { body: body, attachments: attachments };
}

function composeMessageText(body, attachments) {
  var attachmentText = (attachments || []).map(function(attachment) {
    return '- ' + attachment.name + ': ' + attachment.url;
  }).join('\n');
  return body + (attachmentText ? (body ? '\n\n' : '') + '附件：\n' + attachmentText : '');
}

function attachmentHref(path) {
  if (/^https?:\/\//i.test(path)) return path;
  return (window.AppConfig?.SHOW_IMAGE_API || '') + String(path || '').replace(/^\/+/, '');
}

function renderSentAttachments(attachments) {
  if (!attachments.length) return '';
  return '<div class="chat-sent-attachments">' + attachments.map(function(attachment) {
    return '<a class="chat-sent-file" href="' + escapeHtml(attachmentHref(attachment.url)) + '" target="_blank" rel="noopener" title="' + escapeHtml(attachment.name) + '">' +
      '<i data-lucide="file-text" class="chat-sent-file__icon"></i>' +
      '<span class="chat-sent-file__name">' + escapeHtml(attachment.name) + '</span>' +
      '<span class="chat-sent-file__type">' + escapeHtml(attachment.extension || 'FILE') + '</span>' +
      '</a>';
  }).join('') + '</div>';
}

function jumpToChatQuestion(id) {
  var target = document.getElementById(id);
  if (!target) return;
  target.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
  var bubble = target.querySelector('.chat-user-bubble');
  if (bubble && !prefersReducedMotion()) {
    gsap.fromTo(bubble, { scale: 0.985 }, { scale: 1, duration: 0.34, ease: 'power2.out', overwrite: 'auto' });
  }
}

function renderChatOutline() {
  var outline = document.getElementById('chat-outline');
  if (!outline) return;
  var questions = Array.from(document.querySelectorAll('.chat-user-message[data-question]'));
  outline.classList.toggle('hidden', questions.length === 0 || document.getElementById('app-main')?.classList.contains('chat-is-empty'));
  if (!questions.length) {
    outline.innerHTML = '';
    return;
  }
  var markers = questions.map(function(item) {
    return '<button type="button" class="chat-outline__marker" aria-label="跳转到：' + escapeHtml(item.dataset.question) + '" title="' + escapeHtml(item.dataset.question) + '" data-chat-target="' + escapeHtml(item.id) + '"></button>';
  }).join('');
  var list = questions.map(function(item, index) {
    return '<button type="button" class="chat-outline__item" data-chat-target="' + escapeHtml(item.id) + '"><span style="color:var(--claude-muted-foreground);margin-right:8px;">' + (index + 1) + '</span>' + escapeHtml(item.dataset.question) + '</button>';
  }).join('');
  outline.innerHTML = '<div class="chat-outline__rail">' + markers + '</div><div class="chat-outline__panel"><p class="chat-outline__title">本次对话的问题</p>' + list + '</div>';
  outline.querySelectorAll('[data-chat-target]').forEach(function(button) {
    button.addEventListener('click', function() { jumpToChatQuestion(button.dataset.chatTarget); });
  });
}

// Append user message (right-side bubble)
function appendUserMessage(text, messageUuid) {
  var container = document.getElementById('chat-message-list');
  if (!container) return;
  container.querySelector('.chat-empty-state')?.remove();
  setChatMode(false);
  var parsedMessage = parseMessageAttachments(text);
  var bodyHtml = parsedMessage.body
    ? '<p class="text-[15px] leading-relaxed whitespace-pre-wrap" style="color:var(--claude-foreground);">' + escapeHtml(parsedMessage.body) + '</p>'
    : '';
  var time = new Date().toTimeString().slice(0, 5);
  var div = document.createElement('div');
  messageSequence += 1;
  div.id = 'chat-question-' + messageSequence;
  div.dataset.question = questionLabel(text);
  div.dataset.rawMessage = String(text || '');
  if (messageUuid) div.dataset.messageUuid = messageUuid;
  div.className = 'group chat-user-message';
  div.innerHTML =
    '<div class="flex justify-end">' +
      '<div class="chat-user-message-shell max-w-[520px]">' +
        '<div class="chat-user-bubble px-5 py-3 rounded-2xl" style="background:var(--claude-secondary);">' +
          renderSentAttachments(parsedMessage.attachments) + bodyHtml +
        '</div>' +
      '</div>' +
    '</div>' +
    '<div class="chat-user-actions flex items-center justify-end gap-1 mt-1.5 opacity-0 transition-opacity duration-150 group-hover:opacity-100">' +
      '<span class="text-[11px] mr-1.5" style="color:var(--claude-muted-foreground);">' + time + '</span>' +
      '<button type="button" onclick="copyMessage(this)" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="复制">' +
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>' +
      '</button>' +
      '<button type="button" onclick="editUserMessage(this)" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑">' +
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>' +
      '</button>' +
    '</div>';
  container.appendChild(div);
  lucide.createIcons();
  animateElement(div, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0 });
  renderChatOutline();
  scrollToBottom();
  return div;
}

// Append AI thinking bubble; returns the created element
function appendAIThinking() {
  var container = document.getElementById('chat-message-list');
  if (!container) return null;
  var div = document.createElement('div');
  div.className = 'group chat-assistant-message';
  div.innerHTML =
    '<div class="max-w-[680px] w-full">' +
      '<details class="ai-thinking mb-4" data-state="running" aria-label="回答处理进度" open>' +
        '<summary class="ai-thinking-summary">' +
          '<span class="ai-thinking-summary__status"><i data-lucide="sparkles" aria-hidden="true"></i></span>' +
          '<span class="ai-thinking-summary__text">正在思考...</span>' +
          '<i class="ai-thinking-summary__chevron" data-lucide="chevron-right" aria-hidden="true"></i>' +
        '</summary>' +
        '<div class="ai-thinking-body"><div class="ai-thinking-log"></div></div>' +
      '</details>' +
      '<div class="ai-answer text-[15px] leading-[1.75] space-y-3" style="font-family:var(--claude-font-serif);color:var(--claude-card-foreground);"></div>' +
    '</div>';
  container.appendChild(div);
  animateElement(div, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0 });
  scrollToBottom();
  return div;
}

function appendThinkingLog(thinkingEl, message, detail, retrieval) {
  if (!thinkingEl) return;
  updateThinkingSummary(thinkingEl, message, 'running');
  var log = thinkingEl.querySelector('.ai-thinking-log');
  if (!log) return;
  var last = log.lastElementChild;
  if (last && last.dataset.message === message) {
    var detailEl = last.querySelector('.ai-thinking-log__detail');
    if (detailEl && detail) detailEl.textContent = detail;
    lucide.createIcons();
    return;
  }
  if (last) {
    last.classList.remove('is-current');
    last.classList.add('is-complete');
    last.querySelector('.ai-thinking-log__retrieval')?.removeAttribute('open');
  }
  var item = document.createElement('div');
  item.className = 'ai-thinking-log__item is-current' + (/对话上下文|conversation context/i.test(message) ? ' is-context' : '');
  item.dataset.message = message;
  item.innerHTML = '<span class="ai-thinking-log__marker"><i data-lucide="' + thinkingIcon(message) + '" aria-hidden="true"></i></span>' +
    '<div class="ai-thinking-log__content"><div class="ai-thinking-log__label">' + escapeHtml(message) + '</div>' +
    (retrieval ? renderThinkingRetrieval(retrieval, detail) : (detail ? '<div class="ai-thinking-log__detail">' + escapeHtml(detail) + '</div>' : '')) + '</div>';
  log.appendChild(item);
  while (log.children.length > 12) log.removeChild(log.firstElementChild);
  lucide.createIcons();
  scrollToBottom();
}

function renderThinkingRetrieval(data, detail) {
  var sourceType = data?.source_type || '';
  var items = Array.isArray(data?.items) ? data.items : [];
  var itemHtml = items.map(function(item, index) {
    var title;
    var meta = '';
    var content;
    if (sourceType === 'Entities') {
      title = item.entity_name || item.name || `${t('实体')} ${index + 1}`;
      meta = item.entity_type || '';
      content = thinkingRetrievalPreview(item.text);
    } else if (sourceType === 'Relationships') {
      title = [item.source, item.target].filter(Boolean).join(' → ') || `${t('关系')} ${index + 1}`;
      meta = item.name || '';
      content = thinkingRetrievalPreview(item.text);
    } else if (sourceType === 'Reports') {
      var reportText = String(item.text || '');
      title = reportText.match(/社区名称\s*[:：]\s*([^\n]+)/)?.[1] || `${t('社区报告')} ${index + 1}`;
      content = thinkingRetrievalPreview(reportText.match(/社区摘要\s*[:：]\s*([^\n]+)/)?.[1] || reportText);
    } else {
      title = `${t('信息源')} ${index + 1}`;
      content = thinkingRetrievalPreview(item.text);
    }
    return '<div class="ai-thinking-retrieval__item">' +
      '<div class="ai-thinking-retrieval__heading"><span>' + escapeHtml(title) + '</span>' +
      (meta ? '<small>' + escapeHtml(meta) + '</small>' : '') + '</div>' +
      (content ? '<p>' + escapeHtml(content) + '</p>' : '') + '</div>';
  }).join('');
  var truncated = data?.truncated ? '<div class="ai-thinking-retrieval__more">' + escapeHtml(t('仅展示前 24 条，完整记录保留在回答引用中')) + '</div>' : '';
  return '<details class="ai-thinking-log__retrieval" open>' +
    '<summary><span>' + escapeHtml(detail || t(`检索到 ${data?.total || items.length} 条记录`)) + '</span>' +
    '<i data-lucide="chevron-right" aria-hidden="true"></i></summary>' +
    '<div class="ai-thinking-retrieval__list">' + itemHtml + truncated + '</div></details>';
}

function thinkingRetrievalPreview(value, limit = 260) {
  var text = String(value || '').replace(/\s+/g, ' ').trim();
  return text.length > limit ? text.slice(0, limit).trimEnd() + '…' : text;
}

function thinkingIcon(message) {
  var text = String(message || '');
  if (/接收|问题|question/i.test(text)) return 'message-square-text';
  if (/加载|索引|数据|load|index|data/i.test(text)) return 'database';
  if (/检索|查询|召回|匹配|retriev|search|match/i.test(text)) return 'search';
  if (/实体|关系|图谱|上下文|entit|relation|graph|context/i.test(text)) return 'network';
  if (/历史|社区|摘要|概览|history|communit|summary|overview/i.test(text)) return 'layers-3';
  if (/来源|证据|引用|整理|source|evidence|citation|prepar/i.test(text)) return 'file-search';
  if (/生成|回答|generat|answer/i.test(text)) return 'sparkles';
  return 'clock-3';
}

function completeThinkingLog(thinkingEl) {
  if (!thinkingEl) return;
  var items = thinkingEl.querySelectorAll('.ai-thinking-log__item');
  items.forEach(function(item) {
    item.classList.remove('is-current');
    item.classList.add('is-complete');
  });
  updateThinkingSummary(thinkingEl, '已完成知识图谱检索与回答生成。', 'complete');
  thinkingEl.removeAttribute('open');
  lucide.createIcons();
}

function updateThinkingSummary(thinkingEl, message, state) {
  if (!thinkingEl) return;
  var text = thinkingEl.querySelector('.ai-thinking-summary__text');
  var status = thinkingEl.querySelector('.ai-thinking-summary__status');
  if (text) text.textContent = message;
  thinkingEl.dataset.state = state;
  if (status) {
    var icon = state === 'complete' ? 'circle-check' : state === 'error' ? 'circle-alert' : 'sparkles';
    status.innerHTML = '<i data-lucide="' + icon + '" aria-hidden="true"></i>';
  }
}

function assistantActionsHtml() {
  return '<div class="chat-assistant-actions flex items-center gap-1 mt-2">' +
    '<button type="button" onclick="copyMessage(this)" class="chat-assistant-action" title="复制回答" aria-label="复制回答">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>' +
    '<button type="button" onclick="regenerateAnswer(this)" class="chat-assistant-action" title="重新生成" aria-label="重新生成">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M20 11a8.1 8.1 0 0 0-15.5-2M4 4v5h5"/><path d="M4 13a8.1 8.1 0 0 0 15.5 2M20 20v-5h-5"/></svg></button>' +
    '</div>';
}

function finalizeAssistantMessage(aiDiv, text) {
  if (!aiDiv) return;
  aiDiv.dataset.rawMessage = String(text || '');
  var answer = aiDiv.querySelector('.ai-answer');
  if (answer && !aiDiv.querySelector('.chat-assistant-actions')) {
    answer.insertAdjacentHTML('afterend', assistantActionsHtml());
  }
  lucide.createIcons();
}

function failThinkingLog(thinkingEl, message) {
  if (!thinkingEl) return;
  var item = thinkingEl.querySelector('.ai-thinking-log__item.is-current') ||
    thinkingEl.querySelector('.ai-thinking-log__item:last-child');
  if (!item) {
    appendThinkingLog(thinkingEl, '处理失败', message);
    item = thinkingEl.querySelector('.ai-thinking-log__item:last-child');
  }
  if (!item) return;
  item.classList.remove('is-current', 'is-complete');
  item.classList.add('is-error');
  updateThinkingSummary(thinkingEl, '思考过程未完成', 'error');
  thinkingEl.setAttribute('open', '');
  var marker = item.querySelector('.ai-thinking-log__marker');
  if (marker) marker.innerHTML = '<i data-lucide="circle-alert" aria-hidden="true"></i>';
  var detail = item.querySelector('.ai-thinking-log__detail');
  if (!detail) {
    detail = document.createElement('div');
    detail.className = 'ai-thinking-log__detail';
    item.appendChild(detail);
  }
  detail.textContent = message;
  lucide.createIcons();
}

// Append a final AI message (no streaming)
function appendAIMessage(text, sources) {
  var aiDiv = appendAIThinking();
  if (!aiDiv) return;
  var thinkingEl = aiDiv.querySelector('.ai-thinking');
  var answerEl = aiDiv.querySelector('.ai-answer');
  if (thinkingEl) thinkingEl.style.display = 'none';
  answerEl.innerHTML = renderAnswerWithCitations(text, sources || {});
  finalizeAssistantMessage(aiDiv, text);
  scrollToBottom();
}

// Update the top-bar conversation title
function setConversationTitle(title) {
  var titleEl = document.getElementById('conversation-title');
  if (!titleEl) return;
  var rawTitle = String(title || '').trim();
  var normalizedTitle = rawTitle ? displayChatName(rawTitle) : '';
  var titleWrap = document.getElementById('conversation-title-wrap');
  var shouldShow = normalizedTitle !== '' && normalizedTitle !== '新对话' && normalizedTitle !== '对话';
  if (titleWrap) titleWrap.classList.toggle('hidden', !shouldShow);
  if (titleEl.tagName === 'INPUT') {
    var span = document.createElement('span');
    span.id = 'conversation-title';
    span.className = 'text-sm font-medium truncate';
    span.style.color = 'var(--claude-foreground)';
    span.textContent = normalizedTitle;
    titleEl.replaceWith(span);
    return;
  }
  titleEl.textContent = normalizedTitle;
}

function renameCurrentChat() {
  if (!currentChatUuid) return showToast('请先开始一段对话');
  var title = document.getElementById('conversation-title');
  if (!title || title.tagName === 'INPUT') return;
  var input = document.createElement('input');
  input.id = 'conversation-title';
  input.value = currentChatName || title.textContent || '';
  input.maxLength = 64;
  input.className = 'h-8 w-[260px] px-2 rounded-md text-sm outline-none';
  input.style.cssText = 'background:var(--claude-background);border:1px solid var(--claude-primary);color:var(--claude-foreground);';
  title.replaceWith(input);
  input.focus();
  input.select();
  var done = false;
  async function finish(save) {
    if (done) return;
    done = true;
    var value = input.value.trim();
    if (save && value && value !== currentChatName) await persistChatName(currentChatUuid, value);
    else setConversationTitle(currentChatName);
  }
  input.addEventListener('click', function(event) { event.stopPropagation(); });
  input.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') finish(true);
    if (event.key === 'Escape') finish(false);
  });
  input.addEventListener('blur', function() { finish(true); });
}

// Update the knowledge-graph index indicator text
function updateGraphIndicator(graph) {
  var label = document.getElementById('kg-selector-label');
  var trigger = document.querySelector('[data-role="kg-trigger"]');
  var hasGraph = Boolean(graph);
  if (label) label.textContent = graph?.name || '暂无可用索引';
  if (trigger) {
    trigger.disabled = !hasGraph;
    trigger.title = hasGraph ? '选择知识图谱索引' : '暂无已建立索引的图谱';
    trigger.style.color = hasGraph ? 'var(--claude-foreground)' : 'var(--claude-muted-foreground)';
  }
}

function chatNameFromMessage(message) {
  var compact = String(message || '').replace(/\s+/g, ' ').trim();
  return compact.slice(0, 24) || '新对话';
}

async function ensureCurrentChat(firstMessage) {
  if (currentChatUuid) return currentChatUuid;
  currentChatName = chatNameFromMessage(firstMessage);
  var response = await KgBaseAPI.chatLibrary.create({
    kg_base_uuid: kgBaseUuid,
    name: currentChatName + '-' + Date.now().toString().slice(-6)
  });
  if (response.code !== 200 || !response.data) {
    throw new Error(response.msg || '创建对话失败');
  }
  currentChatUuid = response.data;
  syncCurrentChatQuery(currentChatUuid);
  return currentChatUuid;
}

async function saveConversationMessage(role, content, sources) {
  if (!currentChatUuid) return;
  var response = await KgBaseAPI.chatLibrary.appendMessage(currentChatUuid, {
    role: role,
    content: content,
    knowledge_graph_uuid: currentGraphUuid,
    model_name: role === 'assistant' ? document.getElementById('model-value')?.textContent || null : null,
    effort: role === 'assistant' ? getSelectedEffort() : null,
    sources: normalizeSources(sources),
  });
  if (response.code !== 200) throw new Error(response.msg || '保存对话失败');
  return response.data;
}

function parseStoredMessages(messages) {
  if (Array.isArray(messages)) return messages;
  if (!messages || typeof messages !== 'object') return [];
  var parsed = [];
  Object.keys(messages).sort().forEach(function(key) {
    var item = messages[key];
    if (typeof item === 'string') {
      try {
        item = JSON.parse(item);
      } catch (error) {
        item = { ai: item };
      }
    }
    if (item.user) parsed.push({ role: 'user', content: item.user });
    if (item.ai) parsed.push({ role: 'assistant', content: item.ai });
  });
  return parsed;
}

// Load knowledge graph list and select the first graph
async function loadKnowledgeGraphs() {
  if (!kgBaseUuid) {
    showToast('缺少知识库 UUID');
    return;
  }
  try {
    var basesResponse = await KgBaseAPI.kgBase.getAll();
    if (basesResponse.code === 200 && Array.isArray(basesResponse.data)) {
      var graphGroups = await Promise.all(basesResponse.data.map(async function(base) {
        try {
          var graphResponse = await KgBaseAPI.knowledgeGraph.getAll(base.uuid);
          if (graphResponse.code !== 200 || !Array.isArray(graphResponse.data)) return [];
          return graphResponse.data
            .filter(function(graph) { return Number(graph.index_status) === 1; })
            .map(function(graph) {
              return { ...graph, kg_base_uuid: base.uuid, kg_base_name: base.name || '' };
            });
        } catch {
          return [];
        }
      }));
      knowledgeGraphList = graphGroups.flat();
      var selectedGraph = knowledgeGraphList.find(function(graph) {
        return graph.uuid === currentGraphUuid;
      }) || knowledgeGraphList.find(function(graph) {
        return graph.kg_base_uuid === kgBaseUuid;
      }) || knowledgeGraphList[0] || null;
      currentGraphUuid = selectedGraph?.uuid || null;
      updateGraphIndicator(selectedGraph);
      renderKnowledgeGraphMenu();
    } else {
      showToast(basesResponse.msg || '加载知识图谱失败');
    }
  } catch (err) {
    console.error('Failed to load knowledge graphs:', err);
    showToast('加载知识图谱列表失败');
  }
}

function selectKnowledgeGraph() {
  if (!knowledgeGraphList.length) {
    showToast('所有知识库中暂无已建立索引的图谱');
    return;
  }
  renderKnowledgeGraphMenu();
  document.getElementById('kg-selector-menu')?.classList.toggle('hidden');
}

function renderKnowledgeGraphMenu() {
  var menu = document.getElementById('kg-selector-menu');
  if (!menu) return;
  if (!knowledgeGraphList.length) {
    menu.innerHTML = '';
    menu.classList.add('hidden');
    return;
  }
  menu.innerHTML = knowledgeGraphList.map(function(item) {
    var active = item.uuid === currentGraphUuid;
    return '<button type="button" data-kg-uuid="' + escapeHtml(item.uuid) + '" class="claude-menu-item w-full flex flex-col items-start gap-0.5 px-2 py-2 rounded-lg text-left cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);font-weight:' +
      (active ? '600' : '400') + ';">' +
      '<span class="text-xs truncate w-full">' + escapeHtml(item.name || '未命名图谱') + '</span>' +
      '<span class="text-[10px] truncate w-full" style="color:var(--claude-muted-foreground);font-weight:400;">' + escapeHtml(item.kg_base_name || '未命名知识库') + '</span></button>';
  }).join('');
  menu.querySelectorAll('[data-kg-uuid]').forEach(function(button) {
    button.onclick = function() {
      var graph = knowledgeGraphList.find(function(item) { return item.uuid === button.dataset.kgUuid; });
      if (!graph) return;
      currentGraphUuid = graph.uuid;
      updateGraphIndicator(graph);
      menu.classList.add('hidden');
    };
  });
}

async function loadAvailableModels() {
  var panel = document.querySelector('#more-models-panel .px-2.space-y-0\\.5');
  try {
    var response = await KgBaseAPI.llm.getProviders();
    if (response.code !== 200 || !Array.isArray(response.data)) return;
    var configuredProviders = response.data.filter(function(provider) {
      return provider.status !== 0 && provider.api_key && provider.api_url;
    });
    var details = await Promise.all(configuredProviders.map(async function(provider) {
      var detail = await KgBaseAPI.llm.getProviderDetail(provider.uuid);
      return detail.code === 200 ? detail.data : null;
    }));
    var models = details.filter(Boolean).flatMap(function(provider) {
      return (provider.models || []).filter(function(model) {
        return model.status !== 0 && model.type === 'llm';
      });
    });
    if (!models.length) {
      availableLlmModels = [];
      selectedLlmModelUuid = null;
      var modelTrigger = document.querySelector('[data-role="model-trigger"]');
      if (modelTrigger) modelTrigger.disabled = true;
      document.getElementById('model-value').textContent = '暂无可用模型';
      var currentModel = document.getElementById('current-model-item');
      if (currentModel) currentModel.onclick = null;
      if (panel) panel.innerHTML = '<div class="px-2.5 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">请先在个人中心配置模型</div>';
      return;
    }
    modelTrigger = document.querySelector('[data-role="model-trigger"]');
    if (modelTrigger) {
      modelTrigger.disabled = false;
      modelTrigger.style.color = 'var(--claude-foreground)';
    }
    availableLlmModels = models;
    selectedLlmModelUuid = models[0].uuid;
    document.getElementById('model-value').textContent = models[0].name;
    var current = document.getElementById('current-model-item');
    if (current) current.onclick = null;
    if (current) {
      var nameElement = current.querySelector('span');
      if (nameElement) nameElement.textContent = models[0].name;
    }
    renderOtherModels();
  } catch (error) {
    console.error('Failed to load models:', error);
  }
}

// Load chat library history and render into the sidebar
async function loadChatHistory() {
  try {
    var basesResponse = await KgBaseAPI.kgBase.getAll();
    if (basesResponse.code !== 200) throw new Error(basesResponse.msg || '加载知识库失败');
    var bases = Array.isArray(basesResponse.data) ? basesResponse.data : [];
    var histories = await Promise.all(bases.map(async function(base) {
      try {
        var response = await KgBaseAPI.chatLibrary.getAll(base.uuid);
        return response.code === 200 && Array.isArray(response.data)
          ? response.data.map(function(item) { return { ...item, kg_base_uuid: base.uuid }; })
          : [];
      } catch (error) {
        return [];
      }
    }));
    chatHistoryItems = histories.flat();
    renderChatHistory(chatHistoryItems);
  } catch (err) {
    console.error('Failed to load chat history:', err);
  }
}

function toggleChatSort() {
  chatSortAscending = !chatSortAscending;
  chatHistoryItems.sort(function(left, right) {
    var leftTime = new Date(left.updated_time || left.created_time || 0).getTime();
    var rightTime = new Date(right.updated_time || right.created_time || 0).getTime();
    return chatSortAscending ? leftTime - rightTime : rightTime - leftTime;
  });
  renderChatHistory(chatHistoryItems);
}

// Render chat history items into the sidebar
function renderChatHistory(list) {
  var sidebarContent = document.querySelector('#app-sidebar .sidebar-content');
  if (!sidebarContent) return;
  var container = sidebarContent.getElementsByClassName('space-y-0.5')[0];
  if (!container) return;
  if (!list || list.length === 0) {
    container.innerHTML = '<div class="px-3 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">暂无历史对话</div>';
    renderChatSearchResults([]);
    return;
  }
  function renderRows(rows) {
    return rows.map(function(item) {
      var name = displayChatName(item.name || item.title || '未命名对话');
      var uuid = item.uuid || '';
      var isActive = uuid === currentChatUuid;
      var bgStyle = (isActive || item.is_favorite) ? 'style="background:var(--claude-accent);"' : '';
      var itemKgBaseUuid = item.kg_base_uuid || kgBaseUuid;
      var chatHref = '/unigraph/unigraphs/' + encodeURIComponent(itemKgBaseUuid) + '/qa?chat=' + encodeURIComponent(uuid);
      var chatAction = itemKgBaseUuid === kgBaseUuid
        ? 'href="javascript:void(0)" onclick="switchChat(\'' + escapeQuotes(uuid) + '\', \'' + escapeQuotes(name) + '\')"'
        : 'href="' + chatHref + '"';
      return '<div data-chat-uuid="' + escapeHtml(uuid) + '" class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]" ' + bgStyle + '>' +
        '<a ' + chatAction + ' class="block" style="text-decoration:none;">' +
          '<p class="text-[15px] leading-[22px] font-normal truncate pr-7" style="color:var(--claude-foreground);">' + escapeHtml(name) + '</p>' +
        '</a>' +
        '<button type="button" onclick="event.stopPropagation();toggleChatMenu(this)" class="absolute right-2 top-1.5 flex w-6 h-6 items-center justify-center rounded-md claude-menu-item opacity-55 group-hover:opacity-100 transition-opacity" style="background:transparent;border:none;color:var(--claude-muted-foreground);font-size:18px;line-height:1;" aria-label="对话菜单">⋮</button>' +
        '<div class="chat-context-menu hidden absolute right-2 top-8 z-50 min-w-28 rounded-xl p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">' +
          '<button type="button" onclick="event.stopPropagation();renameChat(\'' + escapeQuotes(uuid) + '\',\'' + escapeQuotes(name) + '\')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-foreground);">重命名</button>' +
          '<button type="button" onclick="event.stopPropagation();favoriteChat(\'' + escapeQuotes(uuid) + '\',' + (!item.is_favorite) + ')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-foreground);">' + (item.is_favorite ? '取消收藏' : '收藏') + '</button>' +
          '<button type="button" onclick="event.stopPropagation();deleteChat(\'' + escapeQuotes(uuid) + '\')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-destructive);">删除</button>' +
        '</div>' +
      '</div>';
    }).join('');
  }
  var starred = list.filter(function(item) { return item.is_favorite; });
  var recent = list.filter(function(item) { return !item.is_favorite; });
  var recentHeading = '<div class="flex items-center justify-between px-3 pt-4 pb-1 text-[13px] font-normal" style="color:var(--claude-muted-foreground);">' +
    '<span>Recents</span>' +
    '<button type="button" onclick="toggleChatSort()" class="w-6 h-6 flex items-center justify-center rounded-md claude-menu-item cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);" aria-label="排序">' +
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><line x1="7" y1="3" x2="7" y2="21"/><circle cx="7" cy="8" r="2"/><line x1="17" y1="3" x2="17" y2="21"/><circle cx="17" cy="16" r="2"/></svg>' +
    '</button></div>';
  container.innerHTML =
    (starred.length ? '<div class="px-3 pt-1 pb-1 text-[13px] font-normal" style="color:var(--claude-muted-foreground);">Starred</div>' + renderRows(starred) : '') +
    recentHeading + renderRows(recent);
  renderChatSearchResults(list);
}

function toggleChatMenu(button) {
  var menu = button.nextElementSibling;
  var shouldOpen = menu?.classList.contains('hidden');
  document.querySelectorAll('.chat-context-menu').forEach(function(element) {
    element.classList.add('hidden');
  });
  if (shouldOpen) menu?.classList.remove('hidden');
}

document.addEventListener('click', function(event) {
  if (event.target.closest('.chat-context-menu')) return;
  document.querySelectorAll('.chat-context-menu').forEach(function(element) {
    element.classList.add('hidden');
  });
});

async function favoriteChat(uuid, isFavorite) {
  try {
    var response = await KgBaseAPI.chatLibrary.setFavorite(uuid, isFavorite);
    if (response.code !== 200) throw new Error(response.msg || '收藏失败');
    await loadChatHistory();
  } catch (error) {
    showToast(error.message || '收藏失败');
  }
}

function renderChatSearchResults(list) {
  var container = document.querySelector('#search-modal .max-h-\\[50vh\\]');
  if (!container) return;
  if (!list.length) {
    container.innerHTML = '<div class="px-4 py-8 text-center text-sm" style="color:var(--claude-muted-foreground);">暂无历史对话</div>';
    return;
  }
  container.innerHTML = '<div class="px-2 py-2">' + list.map(function(item) {
    var name = displayChatName(item.name || item.title || '未命名对话');
    var uuid = item.uuid || '';
    var itemKgBaseUuid = item.kg_base_uuid || kgBaseUuid;
    var chatHref = '/unigraph/unigraphs/' + encodeURIComponent(itemKgBaseUuid) + '/qa?chat=' + encodeURIComponent(uuid);
    var chatAction = itemKgBaseUuid === kgBaseUuid
      ? 'href="javascript:void(0)" onclick="switchChat(\'' + escapeQuotes(uuid) + '\',\'' + escapeQuotes(name) + '\');toggleSearchModal();"'
      : 'href="' + chatHref + '"';
    return '<a ' + chatAction + ' class="chat-search-item flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" style="text-decoration:none;">' +
      '<span class="text-sm" style="color:var(--claude-foreground);">' + escapeHtml(name) + '</span>' +
      '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + escapeHtml(item.updated_time || item.created_time || '') + '</span>' +
      '</a>';
  }).join('') + '</div>';
}

async function renameChat(uuid, oldName) {
  var row = document.querySelector('[data-chat-uuid="' + CSS.escape(uuid) + '"]');
  var title = row?.querySelector('p');
  if (!title) return;
  var input = document.createElement('input');
  input.type = 'text';
  input.value = oldName || '';
  input.maxLength = 64;
  input.style.cssText = 'width:100%;height:34px;padding:0 8px;border:1px solid #2f6feb;border-radius:7px;background:var(--claude-background);color:var(--claude-foreground);font-size:15px;outline:none;';
  title.replaceWith(input);
  input.focus();
  input.select();
  var finished = false;
  async function finish(save) {
    if (finished) return;
    finished = true;
    var name = input.value.trim();
    var displayName = save && name ? name : oldName;
    var title = document.createElement('p');
    title.className = 'text-[15px] leading-[22px] font-normal truncate pr-7';
    title.style.color = 'var(--claude-foreground)';
    title.textContent = displayName;
    input.replaceWith(title);
    if (!save || !name || name === oldName) {
      return;
    }
    await persistChatName(uuid, name);
  }
  input.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      finish(true);
    }
    if (event.key === 'Escape') {
      event.preventDefault();
      finish(false);
    }
  });
  input.addEventListener('blur', function() { finish(true); });
}

async function persistChatName(uuid, name) {
  try {
    var detail = await KgBaseAPI.chatLibrary.getDetail(uuid);
    if (detail.code !== 200 || !detail.data) throw new Error(detail.msg || '加载对话失败');
    var response = await KgBaseAPI.chatLibrary.update(uuid, {
      kg_base_uuid: detail.data.kg_base_uuid || kgBaseUuid,
      name: name,
      messages: detail.data.messages || {}
    });
    if (response.code !== 200) throw new Error(response.msg || '重命名失败');
    if (currentChatUuid === uuid) {
      currentChatName = name;
      setConversationTitle(name);
    }
    await loadChatHistory();
  } catch (error) {
    showToast(error.message || '重命名失败');
  }
}

async function deleteChat(uuid) {
  if (!uuid || !await window.confirmAction({
    title: '删除对话',
    message: '确定要删除这段对话吗？',
    confirmText: '删除',
  })) return;
  try {
    var response = await KgBaseAPI.chatLibrary.delete(uuid);
    if (response.code !== 200) throw new Error(response.msg || '删除对话失败');
    if (currentChatUuid === uuid) {
      currentChatUuid = null;
      currentChatName = '新对话';
      clearChatContainer();
      syncCurrentChatQuery(null);
      setConversationTitle('新对话');
    }
    await loadChatHistory();
    showToast('对话已删除');
  } catch (error) {
    showToast(error.message || '删除对话失败');
  }
}

// Switch to a historical conversation
async function switchChat(chatUuid, name) {
  if (!chatUuid) return;
  currentChatUuid = chatUuid;
  syncCurrentChatQuery(chatUuid);
  currentChatName = displayChatName(name || '对话');
  setConversationTitle(currentChatName);
  clearChatContainer();
  setChatMode(false);
  var loadedMessages = 0;
  try {
    var res = await KgBaseAPI.chatLibrary.getDetail(chatUuid);
    if (res.code === 200 && res.data) {
      var messages = Array.isArray(res.data.conversation) && res.data.conversation.length
        ? res.data.conversation
        : parseStoredMessages(res.data.messages || res.data.chats || res.data.history || []);
      if (messages.length > 0) {
        loadedMessages = messages.length;
        messages.forEach(function(msg) {
          var role = msg.role || msg.type || (msg.is_user ? 'user' : 'assistant');
          var content = msg.content || msg.message || msg.answer || '';
          if (role === 'user' || role === 'human') {
            appendUserMessage(content, msg.uuid);
          } else {
            var sources = {};
            if (Array.isArray(msg.sources)) {
              msg.sources.forEach(function(source) {
                sources[source.source_type] = source.content;
              });
            } else {
              sources = normalizeSources(msg.sources);
            }
            appendAIMessage(content, sources);
          }
        });
      }
    }
  } catch (err) {
    console.error('Failed to load chat detail:', err);
    showToast('加载对话失败');
  }
  if (!loadedMessages) renderEmptyState();
  resumeActiveAskForCurrentChat();
  loadChatHistory();
}

function isRunningAskTask(task) {
  return task?.name === 'knowledge_graph.ask' &&
    ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state);
}

function renderResumedAskTask(task) {
  if (!task || task.kwargs?.obj_data?.chat_library_uuid !== currentChatUuid) return;
  var view = resumedAskViews.get(task.uid);
  if (!view?.aiDiv?.isConnected) {
    var aiDiv = appendAIThinking();
    if (!aiDiv) return;
    aiDiv.dataset.askTaskUid = task.uid;
    view = { aiDiv: aiDiv, renderedSteps: new Set() };
    resumedAskViews.set(task.uid, view);
  }
  var thinkingEl = view.aiDiv.querySelector('.ai-thinking');
  var answerEl = view.aiDiv.querySelector('.ai-answer');
  (Array.isArray(task.steps) ? task.steps : []).forEach(function(step, index) {
    if (!step?.label || step.label === '任务已创建') return;
    var key = step.id != null ? String(step.id) : `${step.label}:${index}`;
    if (view.renderedSteps.has(key)) return;
    view.renderedSteps.add(key);
    appendThinkingLog(
      thinkingEl,
      t(step.label),
      step.detail ? t(step.detail) : '',
      step.metrics?.retrieval || null,
    );
  });
  if (task.partialAnswer && answerEl) {
    answerEl.innerHTML = renderMarkdown(task.partialAnswer) +
      '<span class="streaming-caret" aria-hidden="true"></span>';
  }
  scrollToBottom();
}

function resumeActiveAskForCurrentChat() {
  if (!currentChatUuid || !window.TaskManager?.getTasks) return;
  window.TaskManager.getTasks()
    .filter(isRunningAskTask)
    .filter(function(task) {
      return task.kwargs?.obj_data?.chat_library_uuid === currentChatUuid;
    })
    .forEach(renderResumedAskTask);
}

function handleBackgroundAskTaskUpdate(event) {
  var task = event.detail?.task;
  var taskChatUuid = task?.kwargs?.obj_data?.chat_library_uuid;
  if (task?.name !== 'knowledge_graph.ask' || !taskChatUuid || taskChatUuid !== currentChatUuid) return;
  if (isRunningAskTask(task)) {
    renderResumedAskTask(task);
    return;
  }
  var view = resumedAskViews.get(task.uid);
  if (task.state === 'FAILURE' && view?.aiDiv?.isConnected) {
    failThinkingLog(view.aiDiv.querySelector('.ai-thinking'), task.message || '请求失败');
    resumedAskViews.delete(task.uid);
    return;
  }
  if (task.state === 'SUCCESS' && !isStreaming) {
    resumedAskViews.delete(task.uid);
    switchChat(currentChatUuid, currentChatName);
  }
}

// Start a new conversation
async function newConversation() {
  currentChatUuid = null;
  currentChatName = '新对话';
  pendingAttachments = [];
  syncCurrentChatQuery(null);
  setConversationTitle('新对话');
  renderChatAttachments();
  updateSendBtn();
  showEmptyConversation();
  renderChatHistory(chatHistoryItems);
}

// Enter to send (without Shift)
var messageInput = document.getElementById('message-input');
if (messageInput) {
  messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

// Initialize page
updateSidebarLinks(kgBaseUuid);
var appMain = document.getElementById('app-main');
if (appMain) motionContext = gsap.context(function() {}, appMain);
window.addEventListener('unigraph:task-updated', handleBackgroundAskTaskUpdate);
showEmptyConversation();
setConversationTitle('新对话');
(async function initializeApp() {
  await Promise.all([loadKnowledgeGraphs(), loadChatHistory(), loadAvailableModels()]);
  var requestedChatUuid = urlParams.get('chat');
  if (requestedChatUuid) await switchChat(requestedChatUuid, '对话');
})();

  window.copyMessage = copyMessage;
  window.regenerateAnswer = regenerateAnswer;
  window.cancelUserMessageEdit = cancelUserMessageEdit;
  window.editUserMessage = editUserMessage;
  window.saveUserMessageEdit = saveUserMessageEdit;
  window.deleteChat = deleteChat;
  window.favoriteChat = favoriteChat;
  window.newConversation = newConversation;
  window.removeChatAttachment = removeChatAttachment;
  window.renameChat = renameChat;
  window.switchChat = switchChat;
  window.toggleChatSort = toggleChatSort;
  window.toggleChatMenu = toggleChatMenu;

  function destroy() {
    controllerDestroyed = true;
    resumedAskViews.clear();
    window.removeEventListener('unigraph:task-updated', handleBackgroundAskTaskUpdate);
    motionContext?.revert();
    motionContext = null;
  }

  return {
    adjustTextareaHeight,
    copyMessage,
    copyShareLink,
    createShareLink,
    destroy,
    handleChatAttachments,
    selectEffort,
    selectKnowledgeGraph,
    selectModel,
    renameCurrentChat,
    rotateShareLink,
    sendMessage,
    showToast,
    triggerChatAttachments,
    toggleEffortPanel,
    toggleModelDropdown,
    toggleMoreModelsPanel,
    toggleShareModal,
    stopSharing,
    updateShareSnapshot,
    updateSendBtn,
  };
}
