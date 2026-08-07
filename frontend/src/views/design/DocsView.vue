<template>
  <div class="docs-page min-h-[100dvh] overflow-hidden">
    <AppSidebar active="app" />
    <AppSearchDialog />

    <div id="app-main" class="docs-layout transition-all duration-300" style="margin-left:260px;">
      <aside class="docs-nav" aria-label="技术文档章节">
        <div class="docs-nav__head">
          <span class="docs-nav__eyebrow">Architecture</span>
          <strong>技术架构</strong>
          <span>从资料到可引用答案</span>
        </div>
        <nav>
          <a
            v-for="heading in navigationHeadings"
            :key="heading.id"
            :href="`#${heading.id}`"
            :class="[
              'docs-nav__link',
              `docs-nav__link--level-${heading.level}`,
              { 'is-active': heading.level === 2 ? activeModuleId === heading.id : activeHeading === heading.id },
            ]"
            @click="handleNavigation($event, heading)"
          >
            {{ heading.text }}
          </a>
        </nav>
      </aside>

      <main ref="scrollRegion" class="docs-main" data-scroll-region="primary">
        <header class="docs-hero">
          <div class="docs-hero__copy">
            <span class="docs-hero__eyebrow">技术文档 · 系统架构</span>
            <h1>UniGraph 技术架构</h1>
            <p>说明资料接入、知识建模、图谱构建、混合检索和可引用问答的实现链路，并对应到当前代码模块。</p>
          </div>
          <div class="docs-hero__meta" aria-label="技术栈">
            <span>Vue 3</span><span>FastAPI</span><span>Celery</span><span>GraphRAG</span>
          </div>
          <div class="runtime-path" aria-label="运行链路">
            <div><small>01</small><strong>资料接入</strong><span>文档与结构化数据</span></div>
            <i aria-hidden="true"></i>
            <div><small>02</small><strong>知识建模</strong><span>Schema 与图谱</span></div>
            <i aria-hidden="true"></i>
            <div><small>03</small><strong>混合检索</strong><span>实体、关系与社区</span></div>
            <i aria-hidden="true"></i>
            <div><small>04</small><strong>引用回答</strong><span>索引定位证据</span></div>
          </div>
        </header>

        <label class="docs-mobile-module">
          <span>当前模块</span>
          <select v-model="activeModuleId" @change="selectModule(activeModuleId)">
            <option v-for="module in modules" :key="module.id" :value="module.id">{{ module.text }}</option>
          </select>
        </label>

        <article ref="article" class="technical-doc" v-html="renderedDocument"></article>
        <TaskCenter />
      </main>
    </div>

    <button
      v-if="previewImage"
      type="button"
      class="docs-preview"
      aria-label="关闭架构图预览"
      @click="previewImage = ''"
    >
      <img :src="previewImage" alt="架构图大图预览" />
      <span>点击任意位置关闭</span>
    </button>
  </div>
</template>

<script>
import DOMPurify from 'dompurify';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import css from 'highlight.js/lib/languages/css';
import javascript from 'highlight.js/lib/languages/javascript';
import json from 'highlight.js/lib/languages/json';
import MarkdownIt from 'markdown-it';
import python from 'highlight.js/lib/languages/python';
import xml from 'highlight.js/lib/languages/xml';
import technicalArchitecture from '../../../../docs/TECHNICAL_ARCHITECTURE.md?raw';
import technicalArchitectureEn from '../../../../docs/TECHNICAL_ARCHITECTURE.en.md?raw';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';
import { getLocale, t } from '@/services/i18n';

const architectureBase = `${import.meta.env.BASE_URL}docs/architecture/`;

hljs.registerLanguage('bash', bash);
hljs.registerLanguage('css', css);
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('json', json);
hljs.registerLanguage('python', python);
hljs.registerLanguage('xml', xml);

function headingId(text) {
  return String(text)
    .replace(/[`*_]/g, '')
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '');
}

function documentSource(locale = getLocale()) {
  const source = locale === 'en' ? technicalArchitectureEn : technicalArchitecture;
  return source
    .replace(/\]\(assets\/architecture\/([^)]+)\)/g, `](${architectureBase}$1)`)
    .replace(/^#\s+.+\r?\n+/, '');
}

function splitDocumentModules(source) {
  const matches = [...source.matchAll(/^##\s+(.+)$/gm)];
  return matches.map((match, index) => {
    const sectionStart = match.index;
    const contentStart = index === 0 ? 0 : sectionStart;
    const contentEnd = matches[index + 1]?.index ?? source.length;
    const text = match[1].trim();
    const moduleSource = source.slice(contentStart, contentEnd).trim();
    const headings = moduleSource.split('\n').flatMap((line) => {
      const heading = line.match(/^(##|###)\s+(.+)$/);
      if (!heading) return [];
      return [{ level: heading[1].length, text: heading[2], id: headingId(heading[2]) }];
    });
    return { id: headingId(text), text, source: moduleSource, headings };
  });
}

function createMarkdownRenderer() {
  const markdown = new MarkdownIt({ breaks: false, linkify: true, html: false });
  markdown.renderer.rules.heading_open = (tokens, index) => {
    const level = tokens[index].tag;
    const title = tokens[index + 1]?.content || '';
    return `<${level} id="${headingId(title)}">`;
  };
  const defaultImage = markdown.renderer.rules.image;
  markdown.renderer.rules.image = (tokens, index, options, env, self) => {
    const token = tokens[index];
    token.attrSet('loading', 'lazy');
    token.attrSet('decoding', 'async');
    const image = defaultImage
      ? defaultImage(tokens, index, options, env, self)
      : self.renderToken(tokens, index, options);
    const caption = markdown.utils.escapeHtml(token.content || '架构图');
    return `<figure class="architecture-figure"><div class="architecture-figure__canvas">${image}</div><figcaption>${caption}<span>${t('点击查看大图')}</span></figcaption></figure>`;
  };
  markdown.renderer.rules.fence = (tokens, index) => {
    const token = tokens[index];
    const language = String(token.info || 'text').trim().split(/\s+/)[0];
    const pathMatch = token.content.match(/^(?:#|\/\/)\s+([^\n]+)\n/);
    const path = pathMatch?.[1] || language;
    const code = pathMatch ? token.content.slice(pathMatch[0].length) : token.content;
    const languageAliases = { js: 'javascript', py: 'python', html: 'xml', shell: 'bash', sh: 'bash' };
    const highlightLanguage = languageAliases[language] || language;
    const highlightedCode = hljs.getLanguage(highlightLanguage)
      ? hljs.highlight(code, { language: highlightLanguage }).value
      : markdown.utils.escapeHtml(code);
    return `<section class="code-sample"><header><span class="code-sample__path">${markdown.utils.escapeHtml(path)}</span><span class="code-sample__actions"><span class="code-sample__language">${markdown.utils.escapeHtml(language)}</span><button type="button" data-copy-code>${t('复制')}</button></span></header><pre><code class="hljs language-${markdown.utils.escapeHtml(language)}">${highlightedCode}</code></pre></section>`;
  };
  markdown.renderer.rules.table_open = () => '<div class="markdown-table-wrap"><table>';
  markdown.renderer.rules.table_close = () => '</table></div>';
  return markdown;
}

const markdown = createMarkdownRenderer();

export default {
  name: 'DocsView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({
    source: documentSource(),
    localeRevision: 0,
    activeModuleId: '',
    activeHeading: '',
    previewImage: '',
    headingObserver: null,
  }),
  computed: {
    modules() {
      return splitDocumentModules(this.source);
    },
    activeModule() {
      return this.modules.find((module) => module.id === this.activeModuleId) || this.modules[0];
    },
    navigationHeadings() {
      return this.modules.flatMap((module) => [
        module.headings[0],
        ...(module.id === this.activeModuleId ? module.headings.slice(1) : []),
      ].filter(Boolean));
    },
    renderedDocument() {
      return DOMPurify.sanitize(markdown.render(this.activeModule?.source || ''));
    },
  },
  mounted() {
    document.title = `${t('技术架构')} · UniGraph`;
    document.body.className = 'overflow-hidden min-h-0';
    this.activeModuleId = this.modules[0]?.id || '';
    this.activeHeading = this.activeModuleId;
    this.$refs.article?.addEventListener('click', this.handleArticleClick);
    this.$nextTick(this.observeHeadings);
    window.addEventListener('keydown', this.handleKeydown);
    window.addEventListener('unigraph:language-change', this.handleLanguageChange);
  },
  beforeUnmount() {
    this.$refs.article?.removeEventListener('click', this.handleArticleClick);
    this.headingObserver?.disconnect();
    window.removeEventListener('keydown', this.handleKeydown);
    window.removeEventListener('unigraph:language-change', this.handleLanguageChange);
  },
  methods: {
    observeHeadings() {
      this.headingObserver?.disconnect();
      this.headingObserver = new IntersectionObserver(this.handleHeadingVisibility, {
        root: this.$refs.scrollRegion,
        rootMargin: '-16% 0px -72% 0px',
        threshold: 0,
      });
      this.$refs.article?.querySelectorAll('h2, h3').forEach((heading) => this.headingObserver.observe(heading));
    },
    selectModule(moduleId) {
      this.activeModuleId = moduleId;
      this.activeHeading = moduleId;
      this.$nextTick(() => {
        this.observeHeadings();
        this.$refs.scrollRegion?.scrollTo({ top: this.$refs.article?.offsetTop - 24, behavior: 'smooth' });
      });
    },
    handleNavigation(event, heading) {
      if (heading.level !== 2) return;
      event.preventDefault();
      this.selectModule(heading.id);
    },
    async handleArticleClick(event) {
      const copyButton = event.target.closest('[data-copy-code]');
      if (copyButton) {
        const code = copyButton.closest('.code-sample')?.querySelector('code')?.textContent || '';
        await navigator.clipboard.writeText(code);
        copyButton.textContent = t('已复制');
        window.setTimeout(() => { copyButton.textContent = t('复制'); }, 1200);
        return;
      }
      const image = event.target.closest('.architecture-figure img');
      if (image) this.previewImage = image.currentSrc || image.src;
    },
    handleHeadingVisibility(entries) {
      const visible = entries.find((entry) => entry.isIntersecting);
      if (visible) this.activeHeading = visible.target.id;
    },
    handleKeydown(event) {
      if (event.key === 'Escape') this.previewImage = '';
    },
    handleLanguageChange(event) {
      this.source = documentSource(event.detail?.lang || getLocale());
      this.localeRevision += 1;
      this.$nextTick(() => {
        this.activeModuleId = this.modules[0]?.id || '';
        this.activeHeading = this.activeModuleId;
        this.observeHeadings();
      });
    },
  },
};
</script>

<style>
.docs-page { background: var(--claude-background); color: var(--claude-foreground); }
.docs-layout { display: grid; grid-template-columns: 248px minmax(0, 1fr); height: 100dvh; min-height: 0; }
.docs-nav { min-height: 0; overflow-y: auto; padding: 30px 18px 40px; border-right: 1px solid var(--claude-border); background: color-mix(in srgb, var(--claude-background) 92%, var(--claude-card)); }
.docs-nav__head { display: grid; gap: 4px; margin: 0 8px 20px; padding-bottom: 18px; border-bottom: 1px solid var(--claude-border); }
.docs-nav__head strong { font-size: 16px; font-weight: 620; letter-spacing: -.01em; }
.docs-nav__head > span:last-child { color: var(--claude-muted-foreground); font-size: 11px; }
.docs-nav__eyebrow { color: var(--claude-primary); font-family: var(--claude-font-mono); font-size: 9px; letter-spacing: .14em; }
.docs-nav nav { display: grid; gap: 1px; }
.docs-nav__link { position: relative; padding: 7px 10px 7px 14px; color: var(--claude-muted-foreground); font-size: 12px; line-height: 1.45; text-decoration: none; transition: color .18s ease, transform .18s ease; }
.docs-nav__link::before { content: ''; position: absolute; left: 0; top: 9px; bottom: 9px; width: 2px; border-radius: 2px; background: transparent; }
.docs-nav__link:hover,
.docs-nav__link:focus-visible,
.docs-nav__link.is-active { color: var(--claude-foreground); transform: translateX(2px); outline: none; }
.docs-nav__link.is-active::before { background: var(--claude-primary); }
.docs-nav__link--level-3 { padding-left: 26px; font-size: 11px; }
.docs-main { min-width: 0; min-height: 0; overflow-y: auto; scroll-behavior: smooth; }
.docs-hero { width: min(1060px, calc(100% - 72px)); margin: 0 auto; padding: 36px 0 28px; border-bottom: 1px solid var(--claude-border); }
.docs-hero__copy { max-width: 770px; }
.docs-hero__eyebrow { display: block; margin-bottom: 10px; color: var(--claude-primary); font-family: var(--claude-font-sans); font-size: 11px; font-weight: 600; letter-spacing: .04em; }
.docs-hero h1 { max-width: 720px; margin: 0; font-family: var(--claude-font-sans); font-size: clamp(27px, 2.6vw, 34px); font-weight: 650; letter-spacing: -.025em; line-height: 1.2; }
.docs-hero__copy p { max-width: 680px; margin: 12px 0 0; color: var(--claude-muted-foreground); font-size: 14px; line-height: 1.7; }
.docs-hero__meta { display: flex; flex-wrap: wrap; gap: 7px 18px; margin-top: 18px; color: var(--claude-muted-foreground); font-family: var(--claude-font-mono); font-size: 10px; }
.docs-hero__meta span::before { content: '/'; margin-right: 7px; color: var(--claude-primary); }
.runtime-path { display: grid; grid-template-columns: minmax(0,1fr) 28px minmax(0,1fr) 28px minmax(0,1fr) 28px minmax(0,1fr); align-items: center; margin-top: 32px; }
.runtime-path > div { min-width: 0; padding-top: 12px; border-top: 2px solid var(--claude-foreground); }
.runtime-path small { display: block; margin-bottom: 11px; color: var(--claude-primary); font-family: var(--claude-font-mono); font-size: 9px; }
.runtime-path strong,
.runtime-path span { display: block; }
.runtime-path strong { font-size: 13px; font-weight: 600; }
.runtime-path span { margin-top: 4px; color: var(--claude-muted-foreground); font-size: 10px; }
.runtime-path i { height: 1px; background: var(--claude-border); }
.technical-doc { width: min(940px, calc(100% - 72px)); margin: 0 auto; padding: 28px 0 110px; color: var(--claude-muted-foreground); font-family: var(--claude-font-sans); }
.docs-mobile-module { display: none; }
.technical-doc > p:first-child { max-width: 760px; margin: 0 0 18px; color: var(--claude-foreground); font-size: 14px; line-height: 1.75; }
.technical-doc h2,
.technical-doc h3,
.technical-doc h4 { color: var(--claude-foreground); font-family: var(--claude-font-sans); }
.technical-doc h2 { scroll-margin-top: 28px; margin: 36px 0 18px; font-size: 23px; font-weight: 650; letter-spacing: -.018em; line-height: 1.35; }
.technical-doc > h2:first-child { margin-top: 0; }
.technical-doc h3 { scroll-margin-top: 28px; margin: 32px 0 13px; font-size: 17px; font-weight: 620; letter-spacing: -.01em; line-height: 1.45; }
.technical-doc h4 { margin: 24px 0 10px; font-size: 14px; font-weight: 620; line-height: 1.5; }
.technical-doc p,
.technical-doc li { color: var(--claude-muted-foreground); font-size: 14px; line-height: 1.85; }
.technical-doc p { max-width: 78ch; margin: 0 0 17px; }
.technical-doc strong { color: var(--claude-foreground); font-weight: 620; }
.technical-doc em { color: var(--claude-foreground); }
.technical-doc a { color: var(--claude-brand-700); text-decoration-thickness: 1px; text-underline-offset: 3px; }
.technical-doc a:hover { text-decoration-thickness: 2px; }
.technical-doc ul,
.technical-doc ol { margin: 12px 0 24px; padding-left: 1.45rem; }
.technical-doc ul { list-style: disc; }
.technical-doc ol { list-style: decimal; }
.technical-doc li { padding-left: 5px; }
.technical-doc li + li { margin-top: 7px; }
.technical-doc li::marker { color: var(--claude-primary); font-weight: 600; }
.technical-doc li > p { margin-bottom: 8px; }
.technical-doc blockquote { margin: 28px 0 36px; padding: 15px 18px; border-left: 3px solid var(--claude-primary); background: color-mix(in srgb, var(--claude-accent) 62%, transparent); }
.technical-doc blockquote p { max-width: none; margin: 0; color: var(--claude-accent-foreground); }
.technical-doc hr { height: 1px; margin: 42px 0; border: 0; background: var(--claude-border); }
.architecture-figure { margin: 24px 0 34px; }
.architecture-figure__canvas { overflow: hidden; border: 1px solid var(--claude-border); border-radius: 10px; background: #fff; cursor: zoom-in; }
.technical-doc .architecture-figure img { display: block; width: 100%; height: auto; padding: 16px; transition: transform .28s ease; }
.architecture-figure__canvas:hover img { transform: scale(1.012); }
.architecture-figure figcaption { display: flex; justify-content: space-between; gap: 16px; padding-top: 9px; color: var(--claude-muted-foreground); font-size: 11px; line-height: 1.5; }
.architecture-figure figcaption span { flex: none; color: var(--claude-primary); }
.markdown-table-wrap { width: 100%; overflow-x: auto; margin: 24px 0 34px; border: 1px solid var(--claude-border); border-radius: 9px; }
.technical-doc table { width: 100%; min-width: 620px; border-collapse: collapse; font-size: 12px; }
.technical-doc th,
.technical-doc td { padding: 11px 13px; border-right: 1px solid var(--claude-border); border-bottom: 1px solid var(--claude-border); text-align: left; vertical-align: top; line-height: 1.65; }
.technical-doc th { padding: 10px 13px; border-right: 1px solid var(--claude-border); border-bottom: 1px solid var(--claude-border); color: var(--claude-foreground); font-weight: 620; text-align: left; background: var(--claude-secondary); }
.technical-doc tr:last-child td { border-bottom: 0; }
.technical-doc th:last-child,
.technical-doc td:last-child { border-right: 0; }
.technical-doc tbody tr:nth-child(even) { background: color-mix(in srgb, var(--claude-secondary) 34%, transparent); }
.technical-doc td { color: var(--claude-muted-foreground); }
.technical-doc code { padding: .14em .4em; border: 1px solid color-mix(in srgb, var(--claude-border) 80%, transparent); border-radius: 4px; background: var(--claude-secondary); color: var(--claude-foreground); font-family: var(--claude-font-mono); font-size: .86em; }
.code-sample { overflow: hidden; margin: 22px 0 30px; border: 1px solid color-mix(in srgb, var(--claude-foreground) 14%, var(--claude-border)); border-radius: 10px; background: #242321; box-shadow: 0 14px 34px rgb(28 26 23 / 8%); }
.code-sample header { display: flex; align-items: center; justify-content: space-between; min-height: 38px; padding: 0 12px 0 15px; border-bottom: 1px solid rgb(255 255 255 / 9%); color: #bdb8b0; font-family: var(--claude-font-mono); font-size: 10px; }
.code-sample__path { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.code-sample__actions { display: flex; flex: none; align-items: center; gap: 7px; margin-left: 14px; }
.code-sample__language { padding: 2px 5px; border: 1px solid rgb(255 255 255 / 10%); border-radius: 4px; color: #918d86; text-transform: uppercase; letter-spacing: .05em; }
.code-sample header button { flex: none; padding: 4px 7px; border: 0; border-radius: 5px; background: transparent; color: #d9d4cb; font: inherit; cursor: pointer; transition: background-color .16s ease, color .16s ease; }
.code-sample header button:hover,
.code-sample header button:focus-visible { background: rgb(255 255 255 / 9%); color: #fff; outline: none; }
.technical-doc .code-sample pre { overflow-x: auto; margin: 0; padding: 18px 20px 20px; background: transparent; tab-size: 2; }
.technical-doc .code-sample code { padding: 0; border: 0; border-radius: 0; background: transparent; color: #eee9e1; font-size: 11px; line-height: 1.78; white-space: pre; }
.code-sample .hljs-comment,
.code-sample .hljs-quote { color: #8c8882; font-style: italic; }
.code-sample .hljs-keyword,
.code-sample .hljs-selector-tag,
.code-sample .hljs-literal { color: #ff9d76; }
.code-sample .hljs-string,
.code-sample .hljs-doctag,
.code-sample .hljs-regexp { color: #a8d1a2; }
.code-sample .hljs-number,
.code-sample .hljs-symbol,
.code-sample .hljs-bullet { color: #8ec5e8; }
.code-sample .hljs-title,
.code-sample .hljs-title.function_,
.code-sample .hljs-section { color: #d9b8ff; }
.code-sample .hljs-built_in,
.code-sample .hljs-type,
.code-sample .hljs-class .hljs-title { color: #f2cc8f; }
.code-sample .hljs-attr,
.code-sample .hljs-attribute,
.code-sample .hljs-variable,
.code-sample .hljs-template-variable { color: #b8d7ee; }
.code-sample .hljs-meta { color: #c6a0f6; }
.code-sample .hljs-params,
.code-sample .hljs-subst { color: #eee9e1; }
.docs-preview { position: fixed; inset: 0; z-index: 500; display: grid; place-items: center; padding: 50px; border: 0; background: rgb(20 19 18 / 88%); cursor: zoom-out; animation: docs-preview-in .18s ease-out both; }
.docs-preview img { display: block; max-width: min(1320px, 94vw); max-height: 86vh; padding: 16px; border-radius: 10px; background: #fff; box-shadow: 0 24px 80px rgb(0 0 0 / 35%); }
.docs-preview span { position: absolute; bottom: 20px; color: rgb(255 255 255 / 72%); font-size: 11px; }
@keyframes docs-preview-in { from { opacity: 0; } to { opacity: 1; } }
@media (max-width: 900px) {
  .docs-layout { display: block; }
  .docs-nav { display: none; }
  .docs-hero,
  .technical-doc { width: calc(100% - 32px); }
  .docs-hero { padding: 28px 0 24px; }
  .docs-hero h1 { font-size: clamp(25px, 7vw, 30px); }
  .docs-mobile-module { display: grid; gap: 7px; width: calc(100% - 32px); margin: 20px auto 4px; color: var(--claude-muted-foreground); font-size: 11px; }
  .docs-mobile-module select { width: 100%; min-height: 40px; padding: 0 34px 0 12px; border: 1px solid var(--claude-border); border-radius: 8px; background: var(--claude-card); color: var(--claude-foreground); font: inherit; font-size: 13px; }
  .runtime-path { grid-template-columns: 1fr 1fr; gap: 22px; }
  .runtime-path i { display: none; }
  .technical-doc { padding-bottom: 72px; }
  .technical-doc h2 { margin-top: 32px; }
  .technical-doc > h2:first-child { margin-top: 0; }
  .technical-doc .architecture-figure img { padding: 8px; }
  .architecture-figure figcaption span { display: none; }
  .technical-doc .code-sample pre { padding: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .docs-main { scroll-behavior: auto; }
  .architecture-figure__canvas:hover img { transform: none; }
}
</style>
