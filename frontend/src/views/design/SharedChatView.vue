<template>
  <main class="shared-chat-page">
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
          <div class="shared-chat-message__role">{{ message.role === 'user' ? '用户' : 'UniGraph' }}</div>
          <div class="shared-chat-message__body" v-html="renderContent(message.content)"></div>
          <div v-if="message.role === 'assistant' && message.sources?.length" class="shared-chat-sources">
            <details v-for="source in message.sources" :key="source.source_type" class="shared-chat-source">
              <summary>{{ sourceLabel(source.source_type) }}</summary>
              <pre>{{ formatSource(source.content) }}</pre>
            </details>
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
import { onMounted, onUnmounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import DOMPurify from 'dompurify';
import MarkdownIt from 'markdown-it';
import { KgBaseAPI } from '@/api';

const route = useRoute();
const markdown = new MarkdownIt({ html: false, linkify: true, breaks: true });
const loading = ref(true);
const error = ref('');
const share = ref({ conversation: [] });
const originalTitle = document.title;
let robotsMeta = null;

function renderContent(content) {
  return DOMPurify.sanitize(markdown.render(String(content || '')));
}

function sourceLabel(type) {
  return ({
    Sources: '原文来源',
    Entities: '相关实体',
    Relationships: '相关关系',
    Communities: '相关社区',
  })[type] || type;
}

function formatSource(content) {
  if (typeof content === 'string') return content;
  return JSON.stringify(content, null, 2);
}

function formatDate(value) {
  if (!value) return '未知时间';
  return new Date(value).toLocaleString('zh-CN', { hour12: false });
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

.shared-chat-transcript { padding-top: 10px; }

.shared-chat-message {
  padding: 30px 0;
  border-bottom: 1px solid color-mix(in srgb, var(--claude-border) 76%, transparent);
}

.shared-chat-message__role {
  margin-bottom: 10px;
  color: var(--claude-muted-foreground);
  font-size: 12px;
  font-weight: 650;
}

.shared-chat-message--user .shared-chat-message__body {
  padding: 14px 17px;
  border-radius: 13px;
  background: var(--claude-muted);
}

.shared-chat-message__body {
  font-size: 15px;
  line-height: 1.75;
}

.shared-chat-message__body :deep(p) { margin: 0 0 12px; }
.shared-chat-message__body :deep(p:last-child) { margin-bottom: 0; }
.shared-chat-message__body :deep(pre) { overflow: auto; padding: 14px; border-radius: 9px; background: var(--claude-muted); }
.shared-chat-message__body :deep(code) { font-family: var(--claude-font-mono); font-size: .9em; }

.shared-chat-sources {
  margin-top: 18px;
  display: grid;
  gap: 6px;
}

.shared-chat-source {
  border-top: 1px solid var(--claude-border);
  color: var(--claude-muted-foreground);
  font-size: 12px;
}

.shared-chat-source summary {
  padding: 9px 2px;
  cursor: pointer;
}

.shared-chat-source pre {
  max-height: 220px;
  margin: 0 0 10px;
  padding: 10px 12px;
  overflow: auto;
  border-radius: 8px;
  background: var(--claude-muted);
  white-space: pre-wrap;
  font-family: var(--claude-font-mono);
  font-size: 11px;
}

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
