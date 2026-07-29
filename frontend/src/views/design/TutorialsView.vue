<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="app" />

<AppSearchDialog />

<!-- MAIN CONTENT -->
<main id="app-main" class="min-h-0 overflow-y-auto relative transition-all duration-300" style="margin-left:260px;" data-scroll-region="primary">
  <div class="max-w-[900px] w-full mx-auto px-8 py-10 flex flex-col gap-8 min-w-0">

    <!-- Page Header -->
    <header class="min-w-0">
      <h1 class="text-[28px] font-normal leading-tight mb-2" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">视频教程</h1>
      <p class="text-sm leading-relaxed" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">学习如何使用 UniGraph 构建和管理知识图谱</p>
    </header>

    <!-- Category Tabs -->
    <div class="flex items-center gap-0 min-w-0" style="border-bottom:1px solid var(--claude-border);">
      <button @click="filterVideos('all', $event.currentTarget)" class="tab-btn px-4 pb-2.5 text-sm font-medium transition-colors cursor-pointer" style="color:var(--claude-primary);border-bottom:2px solid var(--claude-primary);margin-bottom:-1px;">全部</button>
      <button @click="filterVideos('入门', $event.currentTarget)" class="tab-btn px-4 pb-2.5 text-sm font-medium transition-colors hover:opacity-70 cursor-pointer" style="color:var(--claude-muted-foreground);border-bottom:2px solid transparent;margin-bottom:-1px;">快速入门</button>
      <button @click="filterVideos('进阶', $event.currentTarget)" class="tab-btn px-4 pb-2.5 text-sm font-medium transition-colors hover:opacity-70 cursor-pointer" style="color:var(--claude-muted-foreground);border-bottom:2px solid transparent;margin-bottom:-1px;">图谱设计</button>
      <button @click="filterVideos('高级', $event.currentTarget)" class="tab-btn px-4 pb-2.5 text-sm font-medium transition-colors hover:opacity-70 cursor-pointer" style="color:var(--claude-muted-foreground);border-bottom:2px solid transparent;margin-bottom:-1px;">知识推理</button>
      <button @click="filterVideos('入门', $event.currentTarget)" class="tab-btn px-4 pb-2.5 text-sm font-medium transition-colors hover:opacity-70 cursor-pointer" style="color:var(--claude-muted-foreground);border-bottom:2px solid transparent;margin-bottom:-1px;">数据导入</button>
    </div>

    <!-- Video Grid (2 columns) -->
    <section id="video-grid" class="grid grid-cols-1 md:grid-cols-2 gap-6 min-w-0">

      <!-- Video 1 -->
      <article data-level="入门" class="video-item flex flex-col gap-2.5 cursor-pointer group" @click="showToast('播放：快速入门')">
        <div class="relative aspect-video flex items-center justify-center rounded-lg" style="background:var(--claude-accent);">
          <div class="w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)"><polygon points="9 6 19 12 9 18 9 6"/></svg>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">快速入门: 5分钟创建你的第一个知识图谱</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--claude-muted-foreground);">12:30</span>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">入门</span>
          </div>
          <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">从零开始学习 UniGraph 的基本操作，包括创建项目、导入数据和生成知识图谱的完整流程。</p>
        </div>
      </article>

      <!-- Video 2 -->
      <article data-level="进阶" class="video-item flex flex-col gap-2.5 cursor-pointer group" @click="showToast('播放：图谱设计进阶')">
        <div class="relative aspect-video flex items-center justify-center rounded-lg" style="background:var(--claude-accent);">
          <div class="w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)"><polygon points="9 6 19 12 9 18 9 6"/></svg>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">图谱设计进阶: 实体关系建模技巧</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--claude-muted-foreground);">18:45</span>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">进阶</span>
          </div>
          <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">深入讲解图谱设计模式，包括实体类型定义、关系边建模以及本体设计的最佳实践。</p>
        </div>
      </article>

      <!-- Video 3 -->
      <article data-level="高级" class="video-item flex flex-col gap-2.5 cursor-pointer group" @click="showToast('播放：知识推理详解')">
        <div class="relative aspect-video flex items-center justify-center rounded-lg" style="background:var(--claude-accent);">
          <div class="w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)"><polygon points="9 6 19 12 9 18 9 6"/></svg>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">知识推理详解: 图谱推理引擎工作原理</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--claude-muted-foreground);">24:10</span>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">高级</span>
          </div>
          <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">了解 UniGraph 的推理引擎如何进行知识推理，包括路径推理、关系预测和实体链接。</p>
        </div>
      </article>

      <!-- Video 4 -->
      <article data-level="入门" class="video-item flex flex-col gap-2.5 cursor-pointer group" @click="showToast('播放：数据导入指南')">
        <div class="relative aspect-video flex items-center justify-center rounded-lg" style="background:var(--claude-accent);">
          <div class="w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)"><polygon points="9 6 19 12 9 18 9 6"/></svg>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">数据导入指南: 批量导入与格式转换</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--claude-muted-foreground);">15:20</span>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">入门</span>
          </div>
          <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">学习如何将 CSV、JSON 和 RDF 等格式数据批量导入 UniGraph，并进行格式转换与清洗。</p>
        </div>
      </article>

      <!-- Video 5 -->
      <article data-level="进阶" class="video-item flex flex-col gap-2.5 cursor-pointer group" @click="showToast('播放：可视化分析')">
        <div class="relative aspect-video flex items-center justify-center rounded-lg" style="background:var(--claude-accent);">
          <div class="w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)"><polygon points="9 6 19 12 9 18 9 6"/></svg>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">可视化分析: 图谱探索与查询技巧</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--claude-muted-foreground);">20:55</span>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">进阶</span>
          </div>
          <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">掌握 UniGraph 可视化工具的使用方法，包括节点搜索、路径查询和图谱布局调整。</p>
        </div>
      </article>

      <!-- Video 6 -->
      <article data-level="高级" class="video-item flex flex-col gap-2.5 cursor-pointer group" @click="showToast('播放：API集成开发')">
        <div class="relative aspect-video flex items-center justify-center rounded-lg" style="background:var(--claude-accent);">
          <div class="w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)"><polygon points="9 6 19 12 9 18 9 6"/></svg>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">API 集成开发: 调用图谱服务接口</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--claude-muted-foreground);">28:40</span>
            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">高级</span>
          </div>
          <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">学习如何通过 REST API 和 SDK 调用 UniGraph 服务，实现知识图谱的程序化访问与集成。</p>
        </div>
      </article>

    </section>

  </div>

  <TaskCenter />



</main>

  </div>
</template>

<script>
import { createTutorialsViewController } from '@/controllers/TutorialsView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'TutorialsView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "教程";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createTutorialsViewController();
  },
  methods: {
    filterVideos(...args) {
      return this.controller?.filterVideos(...args);
    },
    showToast(...args) {
      return this.controller?.showToast(...args);
    },
  },
};
</script>

<style>

@layer base { body { background: var(--claude-background); color: var(--claude-foreground); font-family: var(--claude-font-sans); -webkit-font-smoothing: antialiased; } *, *::before, *::after { box-sizing: border-box; } }



:root {
  --claude-background: #FDFBF7;--claude-foreground: #1C1917;--claude-card: #FFFFFF;--claude-card-foreground: #1C1917;
  --claude-popover: #FFFFFF;--claude-popover-foreground: #1C1917;--claude-primary: #C96442;--claude-primary-foreground: #FFFFFF;
  --claude-secondary: #F0EAE0;--claude-secondary-foreground: #3D3530;--claude-muted: #E8E0D4;--claude-muted-foreground: #78716C;
  --claude-accent: #FAF0E4;--claude-accent-foreground: #5C3A1E;--claude-destructive: #B91C1C;--claude-destructive-foreground: #FFFFFF;
  --claude-border: #D6CEC4;--claude-ring: #C96442;--claude-input: #D6CEC4;
  --claude-brand-500: #C96442;--claude-brand-300: #E8A88C;--claude-brand-700: #A0502F;--claude-success-500: #22C55E;
  --claude-shadow-xs: 0 1px 2px rgba(0,0,0,0.05);--claude-shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --claude-shadow-md: 0 4px 6px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);--claude-shadow-lg: 0 10px 15px rgba(0,0,0,0.06), 0 4px 6px rgba(0,0,0,0.03);
  --claude-radius-sm: 8px;--claude-radius-md: 12px;--claude-radius: 16px;--claude-radius-xl: 20px;--claude-radius-2xl: 24px;
  --claude-radius-full: 9999px;--claude-radius-lg: 16px;--claude-spacing: 0.25rem;
  --claude-font-display: Newsreader, Georgia, ui-serif, serif;--claude-font-sans: Poppins, ui-sans-serif, system-ui, sans-serif;
  --claude-font-serif: Lora, Georgia, ui-serif, serif;--claude-font-mono: Geist Mono, ui-monospace, monospace;
}



.bg-background{background-color:var(--claude-background)}.bg-foreground{background-color:var(--claude-foreground)}
.bg-card{background-color:var(--claude-card)}.bg-card-foreground{background-color:var(--claude-card-foreground)}
.bg-popover{background-color:var(--claude-popover)}.bg-popover-foreground{background-color:var(--claude-popover-foreground)}
.bg-primary{background-color:var(--claude-primary)}.bg-primary-foreground{background-color:var(--claude-primary-foreground)}
.bg-secondary{background-color:var(--claude-secondary)}.bg-secondary-foreground{background-color:var(--claude-secondary-foreground)}
.bg-muted{background-color:var(--claude-muted)}.bg-muted-foreground{background-color:var(--claude-muted-foreground)}
.bg-accent{background-color:var(--claude-accent)}.bg-accent-foreground{background-color:var(--claude-accent-foreground)}
.bg-destructive{background-color:var(--claude-destructive)}.bg-destructive-foreground{background-color:var(--claude-destructive-foreground)}
.bg-border{background-color:var(--claude-border)}.bg-ring{background-color:var(--claude-ring)}.bg-input{background-color:var(--claude-input)}
.text-background{color:var(--claude-background)}.text-foreground{color:var(--claude-foreground)}
.text-card{color:var(--claude-card)}.text-card-foreground{color:var(--claude-card-foreground)}
.text-popover{color:var(--claude-popover)}.text-popover-foreground{color:var(--claude-popover-foreground)}
.text-primary{color:var(--claude-primary)}.text-primary-foreground{color:var(--claude-primary-foreground)}
.text-secondary{color:var(--claude-secondary)}.text-secondary-foreground{color:var(--claude-secondary-foreground)}
.text-muted{color:var(--claude-muted)}.text-muted-foreground{color:var(--claude-muted-foreground)}
.text-accent{color:var(--claude-accent)}.text-accent-foreground{color:var(--claude-accent-foreground)}
.text-destructive{color:var(--claude-destructive)}.text-destructive-foreground{color:var(--claude-destructive-foreground)}
.text-border{color:var(--claude-border)}.text-ring{color:var(--claude-ring)}.text-input{color:var(--claude-input)}
.border-border{border-color:var(--claude-border)}



.line-clamp-2{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}



.sidebar-logo { display: flex; }
#app-sidebar.sidebar-collapsed { width: 48px; }
#app-sidebar.sidebar-collapsed .sidebar-text { display: none; }
#app-sidebar.sidebar-collapsed .sidebar-logo { display: none; }
#app-sidebar.sidebar-collapsed nav a span { display: none; }
#app-sidebar.sidebar-collapsed .sidebar-content { display: none; }
#app-sidebar.sidebar-collapsed .sidebar-collapsed-hide,
#app-sidebar.sidebar-collapsed ~ #app-main .sidebar-collapsed-hide { display: none; }
#app-sidebar.sidebar-collapsed .h-12 { justify-content: center; }
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn {
  position: relative;
  margin: 0;
}
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn::after {
  content: attr(data-title);
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
  z-index: 100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
}
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn:hover::after {
  opacity: 1;
}
#app-sidebar.sidebar-collapsed nav a {
  position: relative;
}
#app-sidebar.sidebar-collapsed nav a:hover::after {
  content: attr(data-title);
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
  z-index: 100;
}
#app-sidebar.sidebar-collapsed button[data-title]:hover::after {
  content: attr(data-title);
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
  z-index: 100;
}
@keyframes trace-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

</style>
