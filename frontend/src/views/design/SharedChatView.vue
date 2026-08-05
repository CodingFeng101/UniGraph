<template>
  <main
    class="shared-chat-page"
    @click="handlePageClick"
    @focusin="handleCitationFocusIn"
    @pointerover="handleCitationPointerOver"
    @pointerout="handleCitationPointerOut"
  >
    <header class="shared-chat-header">
      <a class="shared-chat-brand" href="/unigraph/login" aria-label="返回 UniGraph">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="6" cy="6" r="2.4" fill="currentColor" />
          <circle cx="18" cy="7" r="2.4" fill="currentColor" />
          <circle cx="12" cy="18" r="2.4" fill="currentColor" />
          <path d="M8 7l8 0M7 8l4 8M17 9l-4 7" stroke="currentColor" stroke-width="1.6" />
        </svg>
        <span>UniGraph</span>
      </a>
      <span class="shared-chat-badge">共享对话</span>
    </header>

    <section v-if="loading" class="shared-chat-state" aria-live="polite">
      <span class="shared-chat-loader"></span>
      <p>正在加载对话快照</p>
    </section>

    <section v-else-if="error" class="shared-chat-state shared-chat-state--error">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
        <circle cx="12" cy="12" r="9" /><path d="M12 7v6M12 17h.01" />
      </svg>
      <h1>无法查看此对话</h1>
      <p>{{ error }}</p>
    </section>

    <article v-else class="shared-chat-content">
      <div class="shared-chat-title">
        <p>只读快照</p>
        <h1>{{ share.title || '共享对话' }}</h1>
        <span>分享于 {{ formatDate(share.shared_time) }} · 共 {{ share.message_count }} 条消息</span>
      </div>

      <div class="shared-chat-transcript">
        <section
          v-for="(message, index) in share.conversation"
          :key="`${message.sequence}-${index}`"
          class="shared-chat-message"
          :class="`shared-chat-message--${message.role}`"
        >
          <template v-if="message.role === 'user'">
            <div class="shared-chat-user-row">
              <div class="shared-chat-user-shell">
                <div v-if="parseMessageAttachments(message.content).attachments.length" class="shared-chat-attachments">
                  <a
                    v-for="attachment in parseMessageAttachments(message.content).attachments"
                    :key="attachment.url"
                    class="shared-chat-file"
                    :href="attachmentHref(attachment.url)"
                    target="_blank"
                    rel="noopener"
                    :title="attachment.name"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <path d="M14 2v6h6M8 13h8M8 17h6" />
                    </svg>
                    <span class="shared-chat-file__name">{{ attachment.name }}</span>
                    <span class="shared-chat-file__type">{{ attachment.extension }}</span>
                  </a>
                </div>
                <div
                  v-if="parseMessageAttachments(message.content).body"
                  class="shared-chat-user-bubble shared-chat-user-text"
                  v-html="renderChatMarkdown(parseMessageAttachments(message.content).body)"
                ></div>
              </div>
            </div>
            <span class="shared-chat-message__time">{{ formatMessageTime(message.created_time) }}</span>
          </template>
          <div v-else class="shared-chat-assistant-shell">
            <div
              class="shared-chat-answer ai-answer text-[15px] leading-[1.75] space-y-3"
              v-html="renderAnswerWithCitations(message.content, message.sources)"
            ></div>
          </div>
        </section>
      </div>

      <footer class="shared-chat-footer">
        这是创建分享链接时生成的只读快照，之后的新消息不会自动显示。
      </footer>
    </article>
  </main>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { KgBaseAPI } from '@/api';
import { renderAnswerWithCitations, renderChatMarkdown } from '@/utils/chat-content';
import { enhanceChatContent } from '@/features/chat/chat-content-enhancer';
import { parseMessageAttachments } from '@/features/chat/message-attachments';

const route = useRoute();
const loading = ref(true);
const error = ref('');
const share = ref({ conversation: [] });
const originalTitle = document.title;
let robotsMeta = null;
const citationCloseTimers = new WeakMap();

function formatDate(value) {
  if (!value) return '未知时间';
  return new Date(value).toLocaleString('zh-CN', { hour12: false });
}

function formatMessageTime(value) {
  if (!value) return '';
  return new Date(value).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function attachmentHref(path) {
  if (/^https?:\/\//i.test(path)) return path;
  return (window.AppConfig?.SHOW_IMAGE_API || '') + String(path || '').replace(/^\/+/, '');
}

function isCitationPopoverOpen(popup) {
  try {
    return popup.matches(':popover-open');
  } catch {
    return false;
  }
}

function positionCitationPopup(citation) {
  const popup = citation?.querySelector('.source-popup');
  if (!popup) return;
  const page = document.querySelector('.shared-chat-content')?.getBoundingClientRect();
  const boundary = {
    left: Math.max(12, page?.left || 0) + 12,
    right: Math.min(window.innerWidth - 12, page?.right || window.innerWidth) - 12,
    top: Math.max(12, page?.top || 0) + 12,
    bottom: Math.min(window.innerHeight - 12, page?.bottom || window.innerHeight) - 12,
  };
  const citationRect = citation.getBoundingClientRect();
  const heightCap = citation.classList.contains('citation-tag--overview') ? 320 : 300;
  const spaceAbove = Math.max(0, citationRect.top - boundary.top - 8);
  const spaceBelow = Math.max(0, boundary.bottom - citationRect.bottom - 8);

  popup.style.position = 'fixed';
  popup.style.transform = 'none';
  popup.style.maxWidth = Math.max(220, boundary.right - boundary.left) + 'px';
  const desiredHeight = Math.min(popup.scrollHeight, heightCap);
  const showBelow = desiredHeight > spaceAbove && spaceBelow > spaceAbove;
  popup.style.maxHeight = Math.max(96, Math.min(heightCap, Math.floor(showBelow ? spaceBelow : spaceAbove))) + 'px';

  const popupRect = popup.getBoundingClientRect();
  const left = Math.min(Math.max(citationRect.left, boundary.left), boundary.right - popupRect.width);
  const top = showBelow ? citationRect.bottom + 8 : citationRect.top - popupRect.height - 8;
  popup.style.left = Math.round(Math.max(boundary.left, left)) + 'px';
  popup.style.top = Math.round(Math.min(Math.max(top, boundary.top), boundary.bottom - popupRect.height)) + 'px';
  popup.style.right = 'auto';
  popup.style.bottom = 'auto';
}

function openCitation(citation) {
  const popup = citation?.querySelector('.source-popup');
  if (!popup) return;
  const timer = citationCloseTimers.get(citation);
  if (timer) {
    window.clearTimeout(timer);
    citationCloseTimers.delete(citation);
  }
  citation.classList.add('is-open');
  citation.setAttribute('aria-expanded', 'true');
  if (typeof popup.showPopover === 'function' && !isCitationPopoverOpen(popup)) {
    try {
      popup.showPopover();
    } catch {
      // Browsers without Popover API support use the existing positioned panel.
    }
  }
  positionCitationPopup(citation);
}

function closeCitation(citation) {
  const popup = citation?.querySelector('.source-popup');
  citation.classList.remove('is-open');
  citation.setAttribute('aria-expanded', 'false');
  if (popup && typeof popup.hidePopover === 'function' && isCitationPopoverOpen(popup)) {
    try {
      popup.hidePopover();
    } catch {
      // The browser may already have dismissed the panel.
    }
  }
}

function closeCitations(except) {
  document.querySelectorAll('[data-citation].is-open').forEach((citation) => {
    if (citation === except) return;
    closeCitation(citation);
  });
}

function handlePageClick(event) {
  const citation = event.target.closest('[data-citation]');
  if (citation && !event.target.closest('.source-popup')) {
    const shouldOpen = !citation.classList.contains('is-open');
    closeCitations();
    if (shouldOpen) openCitation(citation);
    return;
  }
  if (!event.target.closest('.source-popup')) closeCitations();
}

function handleCitationPointerOver(event) {
  const citation = event.target.closest('[data-citation]');
  if (citation) openCitation(citation);
}

function handleCitationFocusIn(event) {
  const citation = event.target.closest('[data-citation]');
  if (citation) openCitation(citation);
}

function handleCitationPointerOut(event) {
  const citation = event.target.closest('[data-citation]');
  if (!citation || citation.contains(event.relatedTarget)) return;
  const existingTimer = citationCloseTimers.get(citation);
  if (existingTimer) window.clearTimeout(existingTimer);
  const timer = window.setTimeout(() => {
    citationCloseTimers.delete(citation);
    if (citation.matches(':hover') || citation.contains(document.activeElement)) return;
    closeCitation(citation);
    citation.blur();
  }, 180);
  citationCloseTimers.set(citation, timer);
}

onMounted(async () => {
  robotsMeta = document.createElement('meta');
  robotsMeta.name = 'robots';
  robotsMeta.content = 'noindex,nofollow,noarchive';
  document.head.appendChild(robotsMeta);
  try {
    const response = await KgBaseAPI.chatLibrary.getPublicShare(String(route.params.publicId));
    if (response.code !== 200 || !response.data) throw new Error(response.msg || '分享链接不存在或已失效');
    share.value = response.data;
    loading.value = false;
    await nextTick();
    document.querySelectorAll('.shared-chat-answer').forEach(enhanceChatContent);
    document.title = `${response.data.title || '共享对话'} · UniGraph`;
  } catch (requestError) {
    error.value = requestError.message || '分享链接不存在或已失效';
  } finally {
    loading.value = false;
  }
});

onUnmounted(() => {
  robotsMeta?.remove();
  document.title = originalTitle;
});
</script>

<style scoped>
.shared-chat-page {
  min-height: 100dvh;
  background: var(--claude-background);
  color: var(--claude-foreground);
  font-family: var(--claude-font-sans);
}

.shared-chat-header {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 58px;
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--claude-border);
  background: color-mix(in srgb, var(--claude-background) 92%, transparent);
  backdrop-filter: blur(12px);
}

.shared-chat-brand {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: var(--claude-foreground);
  font-size: 17px;
  font-weight: 650;
  text-decoration: none;
}

.shared-chat-brand svg { color: var(--claude-primary); }

.shared-chat-badge {
  color: var(--claude-muted-foreground);
  font-size: 12px;
}

.shared-chat-content {
  width: min(760px, calc(100% - 40px));
  margin: 0 auto;
  padding: 64px 0 48px;
}

.shared-chat-title {
  width: min(680px, 100%);
  margin: 0 auto;
  padding-bottom: 34px;
  border-bottom: 1px solid var(--claude-border);
}

.shared-chat-title p {
  margin: 0 0 10px;
  color: var(--claude-primary);
  font-size: 12px;
  font-weight: 650;
  letter-spacing: .08em;
}

.shared-chat-title h1 {
  margin: 0 0 12px;
  font-size: clamp(26px, 4vw, 38px);
  line-height: 1.16;
  letter-spacing: -.025em;
}

.shared-chat-title span,
.shared-chat-footer {
  color: var(--claude-muted-foreground);
  font-size: 12px;
}

.shared-chat-transcript {
  display: grid;
  gap: 24px;
  width: min(680px, 100%);
  margin: 0 auto;
  padding-top: 28px;
}

.shared-chat-message { min-width: 0; }

.shared-chat-user-row { display: flex; justify-content: flex-end; }
.shared-chat-user-shell { width: fit-content; max-width: 520px; }
.shared-chat-user-bubble {
  padding: 12px 20px;
  border-radius: 16px;
  background: var(--claude-secondary);
  color: var(--claude-foreground);
  font-size: 15px;
  line-height: 1.625;
}
.shared-chat-user-text :deep(p) { margin: 0; white-space: pre-wrap; }
.shared-chat-attachments {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}
.shared-chat-attachments { margin-bottom: 10px; }
.shared-chat-file {
  width: 148px;
  min-height: 82px;
  padding: 11px;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr) auto;
  column-gap: 9px;
  border: 1px solid var(--claude-border);
  border-radius: 12px;
  color: var(--claude-foreground);
  background: var(--claude-card);
  box-shadow: var(--claude-shadow-xs);
  text-decoration: none;
  transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease;
}
.shared-chat-file:hover {
  border-color: color-mix(in srgb, var(--claude-primary) 45%, var(--claude-border));
  box-shadow: var(--claude-shadow-sm);
  transform: translateY(-1px);
}
.shared-chat-file svg {
  grid-row: 1 / 3;
  align-self: start;
  width: 24px;
  height: 24px;
  color: var(--claude-muted-foreground);
}
.shared-chat-file__name {
  min-width: 0;
  overflow: hidden;
  align-self: start;
  font-size: 12px;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.shared-chat-file__type {
  justify-self: start;
  padding: 2px 5px;
  border: 1px solid var(--claude-border);
  border-radius: 5px;
  color: var(--claude-muted-foreground);
  font-size: 9px;
  line-height: 1;
}
.shared-chat-message__time {
  display: block;
  margin-top: 6px;
  padding-right: 6px;
  color: var(--claude-muted-foreground);
  font-size: 11px;
  text-align: right;
}
.shared-chat-assistant-shell { width: 100%; max-width: 680px; }
.shared-chat-answer { color: var(--claude-card-foreground); font-family: var(--claude-font-serif); }

.shared-chat-footer {
  padding-top: 28px;
  text-align: center;
}

.shared-chat-state {
  min-height: calc(100dvh - 58px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--claude-muted-foreground);
  text-align: center;
}

.shared-chat-state h1 { margin: 8px 0 0; color: var(--claude-foreground); font-size: 20px; }
.shared-chat-state p { margin: 0; font-size: 13px; }
.shared-chat-state--error svg { color: var(--claude-destructive); }

.shared-chat-loader {
  width: 22px;
  height: 22px;
  border: 2px solid var(--claude-border);
  border-top-color: var(--claude-primary);
  border-radius: 50%;
  animation: shared-chat-spin .8s linear infinite;
}

@keyframes shared-chat-spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .shared-chat-header { padding: 0 18px; }
  .shared-chat-content { width: min(100% - 28px, 760px); padding-top: 38px; }
}
</style>
