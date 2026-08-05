/* Generated from pages/graph-app.html; keep behavior changes in the source controller during migration. */
import { copyText } from '@/utils/clipboard';
import { gsap } from 'gsap';
import { validateUploadSize } from '@/utils/upload';
import { t } from '@/services/i18n';
import { pinia } from '@/stores';
import { useChatStore } from '@/stores/chat';
import {
  hideAllCitationPopups,
  installCitationPopoverEvents,
  showCitationPopup,
} from '@/features/chat/citation-popover';
import { createChatSharingController } from '@/features/chat/chat-sharing';
import { createChatMessageRenderer } from '@/features/chat/chat-message-renderer';
import { createChatSessionController } from '@/features/chat/chat-session';
import { enhanceChatContent } from '@/features/chat/chat-content-enhancer';
import { renderAnswerWithCitations } from '@/utils/chat-content';

export function createGraphApplicationViewController() {
  const { API, Auth, KgBaseAPI } = window;
  const chatStore = useChatStore(pinia);

lucide.createIcons();

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

function showToast(message) {
  window.showToast(message);
}

const {
  copyShareLink,
  createShareLink,
  rotateShareLink,
  stopSharing,
  toggleShareModal,
  updateShareSnapshot,
} = createChatSharingController({
  api: KgBaseAPI.chatLibrary,
  copyText,
  getChatUuid: () => currentChatUuid,
  notify: showToast,
});

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
  if (isCurrentChatStreaming()) {
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
    await streamAnswer(
      requestText,
      { message_uuid: messageUuid },
      Promise.resolve(),
      parseMessageAttachments(requestText).attachments,
    );
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
  if (isCurrentChatStreaming()) {
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
      ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state) &&
      (typeof window.TaskManager.isActive !== 'function' || window.TaskManager.isActive(task.uid));
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
  if (isCurrentChatStreaming() || hasRunningQuestionTask(currentChatUuid)) {
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
  var sentAttachments = pendingAttachments.map(function(attachment) { return { ...attachment }; });
  input.value = '';
  input.style.height = 'auto';
  pendingAttachments.splice(0);
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

  return streamAnswer(requestText, savedMessage, titlePromise, sentAttachments);
}

async function streamAnswer(requestText, savedMessage, titlePromise, attachments = []) {
  var aiDiv = appendAIThinking();
  var thinkingEl = aiDiv.querySelector('.ai-thinking');
  var answerEl = aiDiv.querySelector('.ai-answer');

  var taskChatUuid = currentChatUuid;
  activeStreamingChats.add(taskChatUuid);
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
        answerEl.innerHTML = renderAnswerWithCitations(displayedAnswer, finalSources) +
          '<span class="streaming-caret" aria-hidden="true"></span>';
      }
      enhanceChatContent(answerEl);
      scrollToBottom();
      if (displayedAnswer.length < finalAnswer.length) scheduleStreamRender();
    });
  }

  var selectedEffort = getSelectedEffort();
  var askTaskUid = null;
  var renderedTaskSteps = new Set();
  var thinkingQueueTail = Promise.resolve();
  var answerRevealUnlocked = false;
  var pendingAnswer = '';
  var foregroundView = {
    aiDiv: aiDiv,
    chatUuid: taskChatUuid,
    messageUuid: savedMessage?.message_uuid || null,
    taskUid: null,
  };
  foregroundAskViews.set(taskChatUuid, foregroundView);

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
          attachments: attachments.map(function(attachment) {
            return { name: attachment.name, url: attachment.url };
          }),
        },
      },
    );
    askTaskUid = submitted.uid;
    aiDiv.dataset.askTaskUid = askTaskUid;
    if (foregroundAskViews.get(taskChatUuid)?.aiDiv === aiDiv) foregroundView.taskUid = askTaskUid;
    var result = await submitted.completion;
    pendingAnswer = result?.results || pendingAnswer || finalAnswer;
    finalSources = result?.context_data || {};
    if (controllerDestroyed) return;
    if (!aiDiv.isConnected) {
      if (currentChatUuid === taskChatUuid) await switchChat(taskChatUuid, currentChatName);
      return;
    }
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
    if (foregroundAskViews.get(taskChatUuid)?.aiDiv === aiDiv) foregroundAskViews.delete(taskChatUuid);
    activeStreamingChats.delete(taskChatUuid);
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
    hideAllCitationPopups();
    if (shouldOpen) {
      showCitationPopup(citation);
    }
    return;
  }
  if (!e.target.closest('.source-popup')) {
    hideAllCitationPopups();
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

var removeCitationPopoverEvents = installCitationPopoverEvents();

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
var currentGraphUuid = chatStore.selectedIndexUuid;
var currentChatUuid = chatStore.currentChatUuid;
var currentChatName = '新对话';
var availableLlmModels = [];
var selectedLlmModelUuid = null;
var knowledgeGraphList = [];
var chatHistoryItems = chatStore.items;
var chatSortAscending = chatStore.sortAscending;
var activeStreamingChats = new Set();
var foregroundAskViews = new Map();
var resumedAskViews = new Map();
var answeredMessageUuids = new Set();
var controllerDestroyed = false;
var pendingAttachments = chatStore.pendingAttachments;

chatStore.currentKnowledgeBaseUuid = kgBaseUuid || null;

function setCurrentChatUuid(value) {
  currentChatUuid = value || null;
  chatStore.currentChatUuid = currentChatUuid;
}

function isCurrentChatStreaming() {
  return Boolean(currentChatUuid && activeStreamingChats.has(currentChatUuid));
}

function setCurrentGraphUuid(value) {
  currentGraphUuid = value || null;
  chatStore.selectedIndexUuid = currentGraphUuid;
}

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

const {
  appendAIMessage,
  appendAIThinking,
  appendThinkingLog,
  appendUserMessage,
  clearChatContainer,
  completeThinkingLog,
  composeMessageText,
  escapeHtml,
  escapeQuotes,
  failThinkingLog,
  finalizeAssistantMessage,
  parseMessageAttachments,
  questionLabel,
  renderChatOutline,
  renderSentAttachments,
  scrollToBottom,
  showEmptyConversation,
} = createChatMessageRenderer({
  animateElement,
  prefersReducedMotion,
  renderEmptyState,
  setChatMode,
});

const {
  deleteChat,
  ensureCurrentChat,
  favoriteChat,
  loadAvailableModels,
  loadChatHistory,
  loadKnowledgeGraphs,
  renameChat,
  renameCurrentChat,
  renderChatHistory,
  saveConversationMessage,
  selectKnowledgeGraph,
  setConversationTitle,
  switchChat,
  toggleChatMenu,
  toggleChatSort,
} = createChatSessionController({
  api: KgBaseAPI,
  appendAIMessage,
  appendUserMessage,
  chatStore,
  clearChatContainer,
  escapeHtml,
  escapeQuotes,
  getSelectedEffort,
  kgBaseUuid,
  notify: showToast,
  renderEmptyState,
  renderOtherModels,
  resumeActiveAskForCurrentChat: () => resumeActiveAskForCurrentChat(),
  resetRecoveredAskState: () => {
    resumedAskViews.forEach(function(view) { view.aiDiv?.remove(); });
    resumedAskViews.clear();
    answeredMessageUuids.clear();
  },
  setAnsweredMessageUuids: (uuids) => {
    answeredMessageUuids = new Set(Array.isArray(uuids) ? uuids : []);
  },
  setChatMode,
  setCurrentChatUuid,
  setCurrentGraphUuid,
  syncCurrentChatQuery,
  get availableLlmModels() { return availableLlmModels; },
  set availableLlmModels(value) { availableLlmModels = value; },
  get chatHistoryItems() { return chatHistoryItems; },
  set chatHistoryItems(value) { chatHistoryItems = value; },
  get chatSortAscending() { return chatSortAscending; },
  set chatSortAscending(value) { chatSortAscending = value; },
  get currentChatName() { return currentChatName; },
  set currentChatName(value) { currentChatName = value; },
  get currentChatUuid() { return currentChatUuid; },
  get currentGraphUuid() { return currentGraphUuid; },
  get knowledgeGraphList() { return knowledgeGraphList; },
  set knowledgeGraphList(value) { knowledgeGraphList = value; },
  get selectedLlmModelUuid() { return selectedLlmModelUuid; },
  set selectedLlmModelUuid(value) { selectedLlmModelUuid = value; },
});

function isRunningAskTask(task) {
  return task?.name === 'knowledge_graph.ask' &&
    ['PENDING', 'STARTED', 'PROGRESS', 'RETRY'].includes(task.state);
}

function hasPersistedAnswerForTask(task) {
  var messageUuid = task?.kwargs?.obj_data?.current_message_uuid;
  return Boolean(messageUuid && answeredMessageUuids.has(messageUuid));
}

function renderResumedAskTask(task) {
  if (!task || task.kwargs?.obj_data?.chat_library_uuid !== currentChatUuid) return;
  if (hasPersistedAnswerForTask(task)) return;
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
    .filter(function(task) { return !hasPersistedAnswerForTask(task); })
    .forEach(renderResumedAskTask);
}

function isForegroundAskTask(task) {
  var taskData = task?.kwargs?.obj_data || {};
  var view = foregroundAskViews.get(taskData.chat_library_uuid);
  if (!view?.aiDiv?.isConnected) return false;
  if (view.messageUuid && taskData.current_message_uuid !== view.messageUuid) return false;
  if (view.taskUid && view.taskUid !== task.uid) return false;
  if (!view.taskUid) {
    view.taskUid = task.uid;
    view.aiDiv.dataset.askTaskUid = task.uid;
  }
  return true;
}

function handleBackgroundAskTaskUpdate(event) {
  var task = event.detail?.task;
  var taskChatUuid = task?.kwargs?.obj_data?.chat_library_uuid;
  if (task?.name !== 'knowledge_graph.ask' || !taskChatUuid || taskChatUuid !== currentChatUuid) return;
  if (isForegroundAskTask(task)) return;
  if (hasPersistedAnswerForTask(task)) return;
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
  if (task.state === 'SUCCESS' && !activeStreamingChats.has(currentChatUuid)) {
    resumedAskViews.delete(task.uid);
    switchChat(currentChatUuid, currentChatName);
  }
}

// Start a new conversation
async function newConversation() {
  resumedAskViews.clear();
  answeredMessageUuids.clear();
  setCurrentChatUuid(null);
  currentChatName = '新对话';
  pendingAttachments.splice(0);
  syncCurrentChatQuery(null);
  setConversationTitle('新对话');
  renderChatAttachments();
  updateSendBtn();
  showEmptyConversation();
  renderChatHistory(chatHistoryItems);
}

function handleDeletedCurrentChat(event) {
  if (!event.detail?.uuid || event.detail.uuid !== currentChatUuid) return;
  newConversation();
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

var chatContainer = document.getElementById('chat-container');
var scrollBottomButton = document.getElementById('chat-scroll-bottom');
var scrollButtonFrame = 0;
function updateScrollBottomButton() {
  scrollButtonFrame = 0;
  if (!chatContainer || !scrollBottomButton) return;
  var distanceFromBottom = chatContainer.scrollHeight - chatContainer.clientHeight - chatContainer.scrollTop;
  scrollBottomButton.classList.toggle('is-visible', distanceFromBottom > 96);
}
function scheduleScrollBottomButtonUpdate() {
  if (!scrollButtonFrame) scrollButtonFrame = window.requestAnimationFrame(updateScrollBottomButton);
}
function scrollChatToBottom() {
  scrollToBottom({ smooth: !prefersReducedMotion() });
}
chatContainer?.addEventListener('scroll', scheduleScrollBottomButtonUpdate, { passive: true });
var chatMessageObserver = typeof MutationObserver === 'undefined' ? null : new MutationObserver(scheduleScrollBottomButtonUpdate);
var chatMessageList = document.getElementById('chat-message-list');
if (chatMessageList) chatMessageObserver?.observe(chatMessageList, { childList: true, subtree: true, characterData: true });
scheduleScrollBottomButtonUpdate();

// Initialize page
updateSidebarLinks(kgBaseUuid);
var appMain = document.getElementById('app-main');
if (appMain) motionContext = gsap.context(function() {}, appMain);
window.addEventListener('unigraph:task-updated', handleBackgroundAskTaskUpdate);
window.addEventListener('unigraph:chat-deleted', handleDeletedCurrentChat);
var requestedChatUuid = urlParams.get('chat');
if (!requestedChatUuid) {
  showEmptyConversation();
  setConversationTitle('新对话');
}
(async function initializeApp() {
  await Promise.all([loadKnowledgeGraphs(), loadChatHistory(), loadAvailableModels()]);
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
    foregroundAskViews.clear();
    resumedAskViews.clear();
    removeCitationPopoverEvents();
    window.removeEventListener('unigraph:task-updated', handleBackgroundAskTaskUpdate);
    window.removeEventListener('unigraph:chat-deleted', handleDeletedCurrentChat);
    chatContainer?.removeEventListener('scroll', scheduleScrollBottomButtonUpdate);
    chatMessageObserver?.disconnect();
    if (scrollButtonFrame) window.cancelAnimationFrame(scrollButtonFrame);
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
    scrollChatToBottom,
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
