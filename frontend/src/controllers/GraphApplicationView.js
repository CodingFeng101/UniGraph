/* Generated from pages/graph-app.html; keep behavior changes in the source controller during migration. */
import { copyText } from '@/utils/clipboard';
import DOMPurify from 'dompurify';
import MarkdownIt from 'markdown-it';
import { gsap } from 'gsap';

export function createGraphApplicationViewController() {
  const { API, Auth, KgBaseAPI } = window;

lucide.createIcons();

var currentShare = null;
var messageSequence = 0;
var motionContext = null;

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
    lucide.createIcons();
    renderChatOutline();
    showToast('消息已更新');
  } catch (error) {
    button.disabled = false;
    button.textContent = '保存';
    showToast(error.message || '保存失败');
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

function selectModel(el, name) {
  document.getElementById('model-value').textContent = name;
  var currentModelItem = document.getElementById('current-model-item');
  currentModelItem.innerHTML = '<div class="flex items-center justify-between"><span class="text-[13px] font-medium" style="color:var(--claude-foreground);">' + name + '</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
  document.getElementById('model-dropdown').classList.add('hidden');
  showToast('已切换模型：' + name);
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
      var badge = lv === 'Medium' ? '<span class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:var(--claude-accent);color:var(--claude-muted-foreground);">Default</span>' : '';
      div.innerHTML = '<div class="flex items-center justify-between"><div class="flex items-center gap-1.5"><span class="text-[13px] font-medium" style="color:var(--claude-foreground);">' + lv + '</span>' + badge + '</div><svg class="effort-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
    } else {
      div.innerHTML = '<span class="text-[13px]" style="color:var(--claude-muted-foreground);">' + lv + '</span>';
    }
    container.appendChild(div);
  });
  showToast('已切换 Effort：' + level);
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
  if (isStreaming) {
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

  try {
    var savedMessage = await saveConversationMessage('user', requestText);
    if (userMessageElement && savedMessage?.message_uuid) {
      userMessageElement.dataset.messageUuid = savedMessage.message_uuid;
    }
  } catch (error) {
    showToast(error.message || 'Failed to save conversation');
    return;
  }

  var titlePromise = KgBaseAPI.chatLibrary.generateTitle(currentChatUuid, requestText)
    .then(function(response) {
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

  var aiDiv = appendAIThinking();
  var thinkingEl = aiDiv.querySelector('.ai-thinking');
  var answerEl = aiDiv.querySelector('.ai-answer');

  isStreaming = true;
  var finalAnswer = '';
  var finalSources = {};

  KgBaseAPI.knowledgeGraph.ask(currentGraphUuid, {
    message: requestText,
    infer: false,
    depth: 1
  }, function(event) {
    if (!event) return;
    if (event.type === 'processing') {
      var msg = event.message || (event.data && event.data.message) || '正在思考...';
      var span = thinkingEl.querySelector('.ai-thinking-text');
      if (span) span.textContent = msg;
      appendThinkingLog(thinkingEl, msg, event.detail || '');
    } else if (event.type === 'final_result') {
      if (thinkingEl) thinkingEl.style.display = 'none';
      var content = '';
      if (event.data) {
        if (typeof event.data === 'string') content = event.data;
        else content = event.data.results || event.data.answer || event.data.content || event.data.message || event.data.response || '';
        finalSources = event.data.context_data || {};
      }
      finalAnswer = content;
      answerEl.innerHTML = renderMarkdown(content) + renderSourceBadges(finalSources);
      scrollToBottom();
    } else if (event.type === 'error') {
      if (thinkingEl) thinkingEl.style.display = 'none';
      var errMsg = event.msg || event.message || '请求失败';
      answerEl.innerHTML = '<p style="color:var(--claude-destructive);">' + escapeHtml(errMsg) + '</p>';
      scrollToBottom();
    }
  }).then(async function() {
    isStreaming = false;
    if (finalAnswer) {
      try {
        await saveConversationMessage('assistant', finalAnswer, finalSources);
        await titlePromise;
        await loadChatHistory();
      } catch (error) {
        showToast(error.message || '保存对话失败');
      }
    }
  }).catch(function(err) {
    isStreaming = false;
    if (thinkingEl) thinkingEl.style.display = 'none';
    answerEl.innerHTML = '<p style="color:var(--claude-destructive);">' + escapeHtml(err.message || '请求失败') + '</p>';
    scrollToBottom();
  });
}

document.addEventListener('click', function(e) {
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
var knowledgeGraphList = [];
var chatHistoryItems = [];
var chatSortAscending = false;
var isStreaming = false;
var pendingAttachments = [];

const markdown = new MarkdownIt({ breaks: true, linkify: true });

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

// Render markdown content and sanitize backend/LLM output before inserting it.
function renderMarkdown(text) {
  if (text == null || text === '') return '';
  try {
    return DOMPurify.sanitize(markdown.render(String(text)));
  } catch (e) {
    return escapeHtml(text).replace(/\n/g, '<br>');
  }
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
  div.className = 'group';
  div.innerHTML =
    '<div class="max-w-[680px] w-full">' +
      '<div class="ai-thinking mb-3">' +
        '<div class="flex items-center gap-2">' +
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="color:var(--claude-muted-foreground);">' +
          '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>' +
        '</svg>' +
        '<span class="ai-thinking-text text-[15px]" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-serif);">正在思考</span>' +
        '<span class="inline-flex gap-0.5">' +
          '<span class="w-1 h-1 rounded-full" style="background:var(--claude-muted-foreground);animation:dot-blink 1.2s infinite 0s;"></span>' +
          '<span class="w-1 h-1 rounded-full" style="background:var(--claude-muted-foreground);animation:dot-blink 1.2s infinite 0.2s;"></span>' +
          '<span class="w-1 h-1 rounded-full" style="background:var(--claude-muted-foreground);animation:dot-blink 1.2s infinite 0.4s;"></span>' +
        '</span>' +
        '</div>' +
        '<div class="ai-thinking-log"></div>' +
      '</div>' +
      '<div class="ai-answer text-[15px] leading-[1.75] space-y-3" style="font-family:var(--claude-font-serif);color:var(--claude-card-foreground);"></div>' +
    '</div>';
  container.appendChild(div);
  animateElement(div, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0 });
  scrollToBottom();
  return div;
}

function appendThinkingLog(thinkingEl, message, detail) {
  if (!thinkingEl) return;
  var log = thinkingEl.querySelector('.ai-thinking-log');
  if (!log) return;
  var last = log.lastElementChild;
  if (last && last.dataset.message === message) {
    var detailEl = last.querySelector('.ai-thinking-log__detail');
    if (detailEl && detail) detailEl.textContent = detail;
    return;
  }
  var item = document.createElement('div');
  item.className = 'ai-thinking-log__item';
  item.dataset.message = message;
  item.innerHTML = '<span class="ai-thinking-log__dot"></span><span>' + escapeHtml(message) + '</span>' +
    (detail ? '<small class="ai-thinking-log__detail">' + escapeHtml(detail) + '</small>' : '');
  log.appendChild(item);
  while (log.children.length > 6) log.removeChild(log.firstElementChild);
  Array.from(log.children).forEach(function(child, index, list) {
    child.style.opacity = index === list.length - 1 ? '1' : '.48';
  });
  scrollToBottom();
}

// Append a final AI message (no streaming)
function appendAIMessage(text, sources) {
  var aiDiv = appendAIThinking();
  if (!aiDiv) return;
  var thinkingEl = aiDiv.querySelector('.ai-thinking');
  var answerEl = aiDiv.querySelector('.ai-answer');
  if (thinkingEl) thinkingEl.style.display = 'none';
  answerEl.innerHTML = renderMarkdown(text) + renderSourceBadges(sources || {});
  scrollToBottom();
}

// Update the top-bar conversation title
function setConversationTitle(title) {
  var titleEl = document.getElementById('conversation-title');
  if (!titleEl) return;
  var normalizedTitle = String(title || '').trim();
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
  var dot = document.getElementById('kg-status-dot');
  if (label) label.textContent = graph?.name || '选择知识图谱';
  if (dot) dot.style.background = isGraphIndexed(graph)
    ? 'var(--claude-success-500)'
    : 'var(--claude-destructive)';
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
    effort: role === 'assistant' ? document.getElementById('effort-value')?.textContent || null : null,
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

function normalizeSources(sources) {
  var normalized = {};
  ['Sources', 'Entities', 'Relationships', 'Communities'].forEach(function(type) {
    normalized[type] = sources && sources[type] != null ? sources[type] : [];
  });
  return normalized;
}

function renderSourceBadges(sources) {
  var normalized = normalizeSources(sources);
  var labels = { Sources: '原始来源', Entities: '实体', Relationships: '关系', Communities: '社区' };
  return '<div class="flex flex-wrap gap-2 mt-4">' + Object.keys(labels).map(function(type) {
    var content = normalized[type];
    var detail = escapeHtml(JSON.stringify(content, null, 2));
    return '<span class="source-tag inline-flex items-center px-2 py-1 rounded-md text-[11px] cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);">' +
      labels[type] +
      '<span class="source-popup"><span class="source-popup-title">' + labels[type] + '</span><pre class="source-popup-row whitespace-pre-wrap">' + detail + '</pre></span>' +
      '</span>';
  }).join('') + '</div>';
}

function isGraphIndexed(graph) {
  return Boolean(graph && (Number(graph.index_status) === 1 || Number(graph.depth) > 0));
}

// Load knowledge graph list and select the first graph
async function loadKnowledgeGraphs() {
  if (!kgBaseUuid) {
    showToast('缺少知识库 UUID');
    return;
  }
  try {
    var res = await KgBaseAPI.knowledgeGraph.getAll(kgBaseUuid);
    if (res.code === 200 && res.data && res.data.length > 0) {
      knowledgeGraphList = res.data;
      currentGraphUuid = res.data[0].uuid;
      updateGraphIndicator(res.data[0]);
      renderKnowledgeGraphMenu();
    } else if (res.code === 200) {
      showToast('当前知识库暂无知识图谱');
    } else {
      showToast(res.msg || '加载知识图谱失败');
    }
  } catch (err) {
    console.error('Failed to load knowledge graphs:', err);
    showToast('加载知识图谱列表失败');
  }
}

function selectKnowledgeGraph() {
  if (!knowledgeGraphList.length) {
    showToast('当前知识库暂无知识图谱');
    return;
  }
  renderKnowledgeGraphMenu();
  document.getElementById('kg-selector-menu')?.classList.toggle('hidden');
}

function renderKnowledgeGraphMenu() {
  var menu = document.getElementById('kg-selector-menu');
  if (!menu) return;
  menu.innerHTML = knowledgeGraphList.map(function(item) {
    var indexed = isGraphIndexed(item);
    var active = item.uuid === currentGraphUuid;
    return '<button type="button" data-kg-uuid="' + escapeHtml(item.uuid) + '" class="claude-menu-item w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left cursor-pointer" style="background:' +
      (active ? 'var(--claude-accent)' : 'transparent') + ';border:none;color:var(--claude-foreground);">' +
      '<span data-status="' + (indexed ? 'indexed' : 'unindexed') + '" class="w-2 h-2 rounded-full shrink-0" style="background:' + (indexed ? 'var(--claude-success-500)' : 'var(--claude-destructive)') + ';"></span>' +
      '<span class="text-xs truncate flex-1">' + escapeHtml(item.name || '未命名图谱') + '</span></button>';
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
      if (panel) panel.innerHTML = '<div class="px-2.5 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">请先在个人中心配置模型</div>';
      return;
    }
    document.getElementById('model-value').textContent = models[0].name;
    var current = document.getElementById('current-model-item');
    if (current) current.onclick = function() { selectModel(current, models[0].name); };
    if (current) {
      var nameElement = current.querySelector('span');
      if (nameElement) nameElement.textContent = models[0].name;
    }
    if (!panel) return;
    panel.innerHTML = '';
    var otherModels = models.slice(1);
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
      item.onclick = function() { selectModel(item, model.name); };
      panel.appendChild(item);
    });
  } catch (error) {
    console.error('Failed to load models:', error);
  }
}

async function loadCurrentSidebarUser() {
  try {
    var response = await KgBaseAPI.auth.getUserInfo();
    if (response.code !== 200 || !response.data) return;
    var user = response.data;
    var footer = document.querySelector('#app-sidebar > .px-3.py-2\\.5.relative.mt-auto');
    if (!footer) return;
    var name = user.nickname || user.username || '用户';
    var avatar = footer.querySelector('.w-8.h-8.rounded-full');
    var nameElement = footer.querySelector('p.text-sm');
    var roleElement = footer.querySelector('p.text-\\[10px\\]');
    if (avatar) avatar.textContent = name.slice(0, 2).toUpperCase();
    if (nameElement) nameElement.textContent = name;
    if (roleElement) roleElement.textContent = user.is_superuser ? '管理员' : '用户';
  } catch (error) {
    console.error('Failed to load user:', error);
  }
}

// Load chat library history and render into the sidebar
async function loadChatHistory() {
  if (!kgBaseUuid) return;
  try {
    var res = await KgBaseAPI.chatLibrary.getAll(kgBaseUuid);
    if (res.code === 200) {
      chatHistoryItems = Array.isArray(res.data) ? res.data : [];
      renderChatHistory(chatHistoryItems);
    }
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
      var name = item.name || item.title || '未命名对话';
      var uuid = item.uuid || '';
      var isActive = uuid === currentChatUuid;
      var bgStyle = (isActive || item.is_favorite) ? 'style="background:var(--claude-accent);"' : '';
      return '<div data-chat-uuid="' + escapeHtml(uuid) + '" class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]" ' + bgStyle + '>' +
        '<a href="javascript:void(0)" class="block" style="text-decoration:none;" onclick="switchChat(\'' + escapeQuotes(uuid) + '\', \'' + escapeQuotes(name) + '\')">' +
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
    var name = item.name || item.title || '未命名对话';
    return '<div class="chat-search-item flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" onclick="switchChat(\'' +
      escapeQuotes(item.uuid || '') + '\',\'' + escapeQuotes(name) + '\');toggleSearchModal();">' +
      '<span class="text-sm" style="color:var(--claude-foreground);">' + escapeHtml(name) + '</span>' +
      '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + escapeHtml(item.updated_time || item.created_time || '') + '</span>' +
      '</div>';
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
  if (isStreaming) {
    showToast('正在生成回答，请稍候...');
    return;
  }
  currentChatUuid = chatUuid;
  syncCurrentChatQuery(chatUuid);
  currentChatName = name || '对话';
  setConversationTitle(name || '对话');
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
            (msg.sources || []).forEach(function(source) {
              sources[source.source_type] = source.content;
            });
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
  loadChatHistory();
}

// Start a new conversation
async function newConversation() {
  if (isStreaming) {
    showToast('正在生成回答，请稍候...');
    return;
  }
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
showEmptyConversation();
setConversationTitle('新对话');
(async function initializeApp() {
  await Promise.all([loadKnowledgeGraphs(), loadChatHistory(), loadAvailableModels(), loadCurrentSidebarUser()]);
  var requestedChatUuid = urlParams.get('chat');
  if (requestedChatUuid) await switchChat(requestedChatUuid, '对话');
})();

  window.copyMessage = copyMessage;
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
