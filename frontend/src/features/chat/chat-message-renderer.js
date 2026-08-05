import { gsap } from 'gsap';
import { t } from '@/services/i18n';
import { renderAnswerWithCitations } from '@/utils/chat-content';
import { enhanceChatContent } from '@/features/chat/chat-content-enhancer';
import { composeMessageText, parseMessageAttachments } from '@/features/chat/message-attachments';

export function createChatMessageRenderer(context) {
  var messageSequence = 0;

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
  function scrollToBottom(options) {
    var container = document.getElementById('chat-container');
    if (!container) return;
    container.scrollTo({
      top: container.scrollHeight,
      behavior: options?.smooth ? 'smooth' : 'auto',
    });
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
    context.renderEmptyState();
  }

  function questionLabel(text) {
    var parsed = parseMessageAttachments(text);
    return String(parsed.body || parsed.attachments[0]?.name || '')
      .split('\n')[0]
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 52) || '附件提问';
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
    target.scrollIntoView({ behavior: context.prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
    var bubble = target.querySelector('.chat-user-bubble');
    if (bubble && !context.prefersReducedMotion()) {
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
    context.setChatMode(false);
    var parsedMessage = parseMessageAttachments(text);
    var bodyHtml = parsedMessage.body
      ? '<p class="text-[15px] leading-relaxed whitespace-pre-wrap" style="color:var(--claude-foreground);">' + escapeHtml(parsedMessage.body) + '</p>'
      : '';
    var time = new Date().toTimeString().slice(0, 5);
    var userBubble = bodyHtml
      ? '<div class="chat-user-bubble px-5 py-3 rounded-2xl" style="background:var(--claude-secondary);">' + bodyHtml + '</div>'
      : '';
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
          renderSentAttachments(parsedMessage.attachments) + userBubble +
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
    context.animateElement(div, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0 });
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
    context.animateElement(div, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0 });
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
    enhanceChatContent(answerEl);
    finalizeAssistantMessage(aiDiv, text);
    scrollToBottom();
  }

  return {
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
  };
}
