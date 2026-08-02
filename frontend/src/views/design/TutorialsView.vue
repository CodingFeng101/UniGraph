<template>
  <div class="h-screen overflow-hidden min-h-0">
    <AppSidebar active="app" />
    <AppSearchDialog />

    <main id="app-main" class="min-h-0 overflow-y-auto relative transition-all duration-300" style="margin-left:260px;" data-scroll-region="primary">
      <div class="max-w-[900px] w-full mx-auto px-8 py-10 flex flex-col gap-8 min-w-0">
        <header class="min-w-0">
          <h1 class="text-[28px] font-normal leading-tight mb-2" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">视频教程</h1>
          <p class="text-sm leading-relaxed" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">从知识架构设计到图谱构建、检索与智能体集成</p>
        </header>

        <div class="flex items-center gap-0 min-w-0 overflow-x-auto" style="border-bottom:1px solid var(--claude-border);">
          <button
            v-for="category in categories"
            :key="category.value"
            type="button"
            class="tab-btn px-4 pb-2.5 text-sm font-medium transition-colors hover:opacity-70 cursor-pointer whitespace-nowrap"
            :style="categoryStyle(category.value)"
            @click="selectedCategory = category.value"
          >
            {{ category.label }}
          </button>
        </div>

        <section id="video-grid" class="grid grid-cols-1 md:grid-cols-2 gap-6 min-w-0">
          <a
            v-for="video in filteredVideos"
            :key="video.url"
            :href="video.url"
            target="_blank"
            rel="noopener noreferrer"
            class="video-item flex flex-col gap-2.5 cursor-pointer group no-underline"
          >
            <div class="video-cover relative aspect-video flex items-center justify-center rounded-lg overflow-hidden" style="background:var(--claude-accent);">
              <img
                :src="video.cover"
                :alt="`${video.title} 视频封面`"
                class="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.025]"
                loading="lazy"
                referrerpolicy="no-referrer"
                @error="$event.currentTarget.style.display = 'none'"
              />
              <div class="video-cover__shade absolute inset-0" aria-hidden="true"></div>
              <div class="relative w-12 h-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110" style="background:var(--claude-primary);box-shadow:var(--claude-shadow-lg);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--claude-primary-foreground)" aria-hidden="true"><polygon points="9 6 19 12 9 18 9 6"/></svg>
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <h3 class="text-sm font-medium leading-snug" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">{{ video.title }}</h3>
              <div class="flex items-center gap-2">
                <span class="text-xs" style="color:var(--claude-muted-foreground);">哔哩哔哩</span>
                <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">{{ video.category }}</span>
              </div>
              <p class="text-xs leading-relaxed line-clamp-2" style="color:var(--claude-muted-foreground);">{{ video.description }}</p>
            </div>
          </a>
        </section>
      </div>

      <TaskCenter />
    </main>
  </div>
</template>

<script>
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'TutorialsView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({
    selectedCategory: 'all',
    categories: [
      { value: 'all', label: '全部' },
      { value: '总览', label: '总览' },
      { value: '设计', label: '图谱设计' },
      { value: '构建', label: '图谱构建' },
      { value: '检索', label: '图谱检索' },
      { value: '集成', label: '智能体集成' },
    ],
    videos: [
      {
        category: '总览',
        title: '一站式知识图谱智造平台',
        description: '系统了解 UniGraph 的完整工作流与核心能力。',
        url: 'https://www.bilibili.com/video/BV1jkivYZEyB',
        cover: 'https://i1.hdslb.com/bfs/archive/28a393a50a1dcbbe1792d64750cfbe838d4c2b53.jpg',
      },
      {
        category: '设计',
        title: '知识架构设计解说',
        description: '讲解实体类型、关系类型、属性与知识架构设计流程。',
        url: 'https://www.bilibili.com/video/BV1weR8YeEPh',
        cover: 'https://i0.hdslb.com/bfs/archive/a1ea3888aa76832689fb230764844ecd2afe7b9a.jpg',
      },
      {
        category: '构建',
        title: '知识图谱构建解说',
        description: '演示从文件上传、知识抽取到图谱生成的完整过程。',
        url: 'https://www.bilibili.com/video/BV1ceR8YeEhD',
        cover: 'https://i2.hdslb.com/bfs/archive/6dd89c00275b733dfdb50ad7949eef22cd7a9b09.jpg',
      },
      {
        category: '检索',
        title: '知识图谱检索解说',
        description: '介绍图谱索引、上下文检索与知识问答能力。',
        url: 'https://www.bilibili.com/video/BV1weR8YeEjv',
        cover: 'https://i0.hdslb.com/bfs/archive/2a2641bbc602b0516db8af5d4790cf67c2ed7006.jpg',
      },
      {
        category: '集成',
        title: 'UniGraph & Sapper',
        description: '将 UniGraph 生成的知识能力接入智能体平台。',
        url: 'https://www.bilibili.com/video/BV1kcZuYjEuM',
        cover: 'https://i1.hdslb.com/bfs/archive/73262ab4fae706faed1c8f479650fd07a08cd794.jpg',
      },
    ],
  }),
  computed: {
    filteredVideos() {
      if (this.selectedCategory === 'all') return this.videos;
      return this.videos.filter((video) => video.category === this.selectedCategory);
    },
  },
  mounted() {
    document.title = '教程';
    document.body.className = 'h-screen overflow-hidden min-h-0';
  },
  methods: {
    categoryStyle(value) {
      const active = this.selectedCategory === value;
      return {
        color: active ? 'var(--claude-primary)' : 'var(--claude-muted-foreground)',
        borderBottom: active ? '2px solid var(--claude-primary)' : '2px solid transparent',
        marginBottom: '-1px',
      };
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
.video-cover__shade {
  background: linear-gradient(180deg, rgba(28,25,23,0.04), rgba(28,25,23,0.22));
}
.video-item:focus-visible .video-cover {
  outline: 2px solid var(--claude-ring);
  outline-offset: 3px;
}



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
