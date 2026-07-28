<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="list" />

<AppSearchDialog />

<TaskCenter />



<main id="app-main" class="min-h-0 overflow-y-auto transition-all duration-300" style="margin-left:260px;" data-scroll-region="primary">
  <div class="max-w-[1200px] w-full mx-auto px-8 pt-6 pb-8 flex flex-col gap-6 min-w-0">
    <header class="flex items-end justify-between gap-4 min-w-0">
      <div class="min-w-0 flex-1">
        <h1 class="text-2xl font-normal leading-tight mb-1.5" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">图知识库列表</h1>
        <p class="text-sm leading-relaxed" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">浏览和管理你的图知识库项目</p>
      </div>
      <button @click="toggleNewKBCard()" class="shrink-0 inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer hover:opacity-90 active:scale-[0.98]" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);">
        <i data-lucide="plus" style="width:16px;height:16px;"></i>
        新建知识库
      </button>
    </header>

    <section class="flex items-center justify-between gap-4 min-w-0">
      <div class="flex items-center gap-2 flex-1 min-w-[200px] max-w-[480px] h-10 px-3 rounded-lg" style="background:var(--claude-card);border:1px solid var(--claude-border);">
        <i data-lucide="search" style="width:16px;height:16px;color:var(--claude-muted-foreground);flex-shrink:0;"></i>
        <input type="search" id="kb-search-input" placeholder="搜索知识库..." class="flex-1 min-w-0 bg-transparent border-none outline-none text-sm" style="color:var(--claude-foreground);font-family:var(--claude-font-sans);" @input="filterKBList()" />
      </div>
      <div class="flex items-center gap-3 shrink-0">
        <div class="relative">
          <button id="kb-sort-select" type="button" @click="sortMenuOpen = !sortMenuOpen" class="h-9 min-w-[132px] px-3 flex items-center justify-between gap-3 rounded-lg text-sm font-normal cursor-pointer transition-colors hover:bg-[var(--claude-secondary)] active:scale-[0.98]" style="background:var(--claude-card);border:1px solid var(--claude-border);color:var(--claude-foreground);font-family:var(--claude-font-sans);">
            <span>{{ sortLabel }}</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" :style="{ transform: sortMenuOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform .2s ease' }"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div v-if="sortMenuOpen" class="absolute right-0 top-full mt-1.5 w-[172px] p-1.5 rounded-xl z-30" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
            <button v-for="item in sortOptions" :key="item.value" type="button" @click="selectKBSort(item)" class="w-full h-9 px-3 flex items-center justify-between rounded-lg text-sm font-normal text-left cursor-pointer transition-colors hover:bg-[var(--claude-secondary)]" :style="{ background: sortMode === item.value ? 'var(--claude-accent)' : 'transparent', border: 'none', color: 'var(--claude-foreground)', fontFamily: 'var(--claude-font-sans)' }">
              <span>{{ item.label }}</span>
              <svg v-if="sortMode === item.value" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg>
            </button>
          </div>
        </div>
        <span id="kb-count" class="text-xs whitespace-nowrap" style="color:var(--claude-muted-foreground);">共 0 个知识库</span>
      </div>
    </section>

    <section id="kb-list-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 min-w-0">
      <article class="kb-card flex flex-col rounded-lg overflow-hidden transition-shadow hover:shadow-md" style="background:var(--claude-popover);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xs);">
        <div class="h-[160px] relative overflow-hidden" style="background:var(--claude-accent);">
          <svg class="absolute inset-0 w-full h-full opacity-[0.06]" viewBox="0 0 400 160" fill="none">
            <circle cx="80" cy="60" r="40" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="200" cy="40" r="30" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="320" cy="80" r="35" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="150" cy="120" r="25" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="280" cy="130" r="28" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <line x1="110" y1="70" x2="175" y2="50" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="225" y1="50" x2="290" y2="72" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="105" y1="85" x2="130" y2="110" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="175" y1="50" x2="165" y2="100" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="290" y1="100" x2="300" y2="115" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="165" y1="125" x2="255" y2="130" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
          </svg>
        </div>
        <div class="p-4 flex flex-col gap-3 min-w-0">
          <h2 class="text-base font-medium truncate" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">企业知识图谱</h2>
          <p class="text-xs leading-relaxed line-clamp-2" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">企业内部知识管理，包含人员、部门、项目等实体及其关联关系，支持多维度知识检索与推理</p>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] truncate" style="font-family:var(--claude-font-mono);color:var(--claude-muted-foreground);">KB-2024-001</span>
            <div class="flex items-center gap-3 shrink-0 text-[10px]" style="color:var(--claude-muted-foreground);">
              <span>架构: 12</span>
              <span>实体: 3,847</span>
            </div>
          </div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] truncate" style="color:var(--claude-muted-foreground);">2 小时前更新</span>
            <div class="flex items-center gap-2 shrink-0">
              <a href="/unigraph/unigraphs/enterprise/info" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors hover:opacity-90 cursor-pointer" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);">进入项目</a>
              <button class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer" style="color:var(--claude-muted-foreground);" @mouseenter="$event.currentTarget.style.color='var(--claude-destructive)'" @mouseleave="$event.currentTarget.style.color='var(--claude-muted-foreground)'" @click="deleteKB($event.currentTarget)">
                <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </article>

      <article class="kb-card flex flex-col rounded-lg overflow-hidden transition-shadow hover:shadow-md" style="background:var(--claude-popover);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xs);">
        <div class="h-[160px] relative overflow-hidden" style="background:var(--claude-muted);">
          <svg class="absolute inset-0 w-full h-full opacity-[0.06]" viewBox="0 0 400 160" fill="none">
            <circle cx="100" cy="50" r="25" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="180" cy="80" r="20" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="250" cy="45" r="28" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="330" cy="70" r="22" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="140" cy="120" r="18" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <circle cx="290" cy="120" r="24" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <line x1="123" y1="55" x2="163" y2="75" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="198" y1="78" x2="225" y2="55" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="275" y1="55" x2="312" y2="65" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="115" y1="68" x2="135" y2="108" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="195" y1="95" x2="275" y2="112" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="310" y1="90" x2="300" y2="100" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
          </svg>
          <span class="absolute bottom-3 right-3 inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-semibold whitespace-nowrap" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);">
            <span class="inline-block w-1.5 h-1.5 rounded-full" style="background:var(--claude-primary-foreground);animation:pulse 1.5s infinite;"></span>
            构建中
          </span>
        </div>
        <div class="p-4 flex flex-col gap-3 min-w-0">
          <h2 class="text-base font-medium truncate" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">科研文献图谱</h2>
          <p class="text-xs leading-relaxed line-clamp-2" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">学术论文、作者、研究方向的关联网络，支持文献引证分析与跨领域知识发现</p>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] truncate" style="font-family:var(--claude-font-mono);color:var(--claude-muted-foreground);">KB-2024-002</span>
            <div class="flex items-center gap-3 shrink-0 text-[10px]" style="color:var(--claude-muted-foreground);">
              <span>架构: 8</span>
              <span>实体: 15,230</span>
            </div>
          </div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] truncate" style="color:var(--claude-muted-foreground);">进行中</span>
            <div class="flex items-center gap-2 shrink-0">
              <a href="/unigraph/unigraphs/research/info" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors hover:opacity-90 cursor-pointer" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);">进入项目</a>
              <button class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer" style="color:var(--claude-muted-foreground);" @mouseenter="$event.currentTarget.style.color='var(--claude-destructive)'" @mouseleave="$event.currentTarget.style.color='var(--claude-muted-foreground)'" @click="deleteKB($event.currentTarget)">
                <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </article>

      <article class="kb-card flex flex-col rounded-lg overflow-hidden transition-shadow hover:shadow-md" style="background:var(--claude-popover);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xs);">
        <div class="h-[160px] relative overflow-hidden" style="background:var(--claude-secondary);">
          <svg class="absolute inset-0 w-full h-full opacity-[0.06]" viewBox="0 0 400 160" fill="none">
            <rect x="50" y="30" width="60" height="40" rx="6" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <rect x="170" y="20" width="55" height="50" rx="6" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <rect x="280" y="35" width="70" height="35" rx="6" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <rect x="100" y="100" width="50" height="35" rx="6" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <rect x="230" y="95" width="65" height="40" rx="6" stroke="currentColor" stroke-width="1" style="color:var(--claude-foreground);"/>
            <line x1="110" y1="55" x2="170" y2="45" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="225" y1="45" x2="280" y2="50" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="80" y1="70" x2="110" y2="100" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="200" y1="65" x2="245" y2="100" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
            <line x1="150" y1="120" x2="230" y2="115" stroke="currentColor" stroke-width="0.8" style="color:var(--claude-foreground);"/>
          </svg>
        </div>
        <div class="p-4 flex flex-col gap-3 min-w-0">
          <h2 class="text-base font-medium truncate" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">产品技术图谱</h2>
          <p class="text-xs leading-relaxed line-clamp-2" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">产品模块、技术栈、依赖关系的知识网络，辅助技术架构决策与影响分析</p>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] truncate" style="font-family:var(--claude-font-mono);color:var(--claude-muted-foreground);">KB-2024-003</span>
            <div class="flex items-center gap-3 shrink-0 text-[10px]" style="color:var(--claude-muted-foreground);">
              <span>架构: 6</span>
              <span>实体: 892</span>
            </div>
          </div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] truncate" style="color:var(--claude-muted-foreground);">1 天前更新</span>
            <div class="flex items-center gap-2 shrink-0">
              <a href="/unigraph/unigraphs/product/info" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors hover:opacity-90 cursor-pointer" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);">进入项目</a>
              <button class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer" style="color:var(--claude-muted-foreground);" @mouseenter="$event.currentTarget.style.color='var(--claude-destructive)'" @mouseleave="$event.currentTarget.style.color='var(--claude-muted-foreground)'" @click="deleteKB($event.currentTarget)">
                <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </article>

    </section>
  </div>
</main>

<div id="new-kb-card" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);backdrop-filter:blur(4px);">
  <article class="rounded-2xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:460px;max-width:calc(100vw - 32px);">
    <div class="flex items-center justify-between px-6 py-5" style="border-bottom:1px solid var(--claude-border);">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:var(--claude-accent);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        </div>
        <h2 class="text-base font-semibold" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">新建知识库</h2>
      </div>
      <button @click="toggleNewKBCard()" class="w-8 h-8 flex items-center justify-center rounded-lg transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;" aria-label="关闭">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="p-6 flex flex-col gap-5 min-w-0">
      <div id="new-kb-cover-picker" class="h-[110px] rounded-xl relative overflow-hidden flex flex-col items-center justify-center gap-2 cursor-pointer transition-all" style="border:1.5px dashed var(--claude-border);background:var(--claude-secondary);" @click="triggerNewKBCoverUpload()" @mouseenter="$event.currentTarget.style.borderColor='var(--claude-brand-500)'" @mouseleave="$event.currentTarget.style.borderColor='var(--claude-border)'">
        <img id="new-kb-cover-preview" class="hidden absolute inset-0 w-full h-full object-cover" alt="知识库封面预览" />
        <div id="new-kb-cover-prompt" class="relative flex flex-col items-center gap-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m17 8-5-5-5 5"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/></svg>
          <span id="new-kb-cover-status" class="text-xs" style="color:var(--claude-muted-foreground);">上传封面图</span>
          <span class="text-[10px]" style="color:var(--claude-muted-foreground);opacity:0.75;">支持 JPG、PNG、WebP，最大 5 MB</span>
        </div>
      </div>
      <input id="new-kb-cover-file" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="uploadNewKBCover($event.currentTarget)" />
      <div class="flex flex-col gap-2">
        <label class="text-xs font-medium" style="color:var(--claude-foreground);">名称</label>
        <input type="text" id="new-kb-name" placeholder="输入知识库名称" class="h-10 px-3.5 rounded-lg text-sm outline-none transition-colors" style="background:var(--claude-secondary);border:1px solid var(--claude-border);color:var(--claude-foreground);font-family:var(--claude-font-sans);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'" />
      </div>
      <div class="flex flex-col gap-2">
        <label class="text-xs font-medium" style="color:var(--claude-foreground);">描述</label>
        <textarea id="new-kb-desc" placeholder="输入知识库描述" rows="3" class="px-3.5 py-2.5 rounded-lg text-sm outline-none resize-none transition-colors" style="background:var(--claude-secondary);border:1px solid var(--claude-border);color:var(--claude-foreground);font-family:var(--claude-font-sans);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'"></textarea>
      </div>
      <div class="flex items-center justify-end gap-2.5 pt-1">
        <button @click="toggleNewKBCard()" class="px-4 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-muted-foreground);border:1px solid var(--claude-border);">取消</button>
        <button @click="createKB()" class="px-4 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer hover:opacity-90 active:scale-[0.98]" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);border:none;">创建</button>
      </div>
    </div>
  </article>
</div>

<div id="delete-confirm" class="hidden fixed inset-0 z-[100] flex items-center justify-center px-4" style="background:rgba(28,25,23,0.18);backdrop-filter:blur(3px);">
  <div class="rounded-xl overflow-hidden" role="dialog" aria-modal="true" aria-labelledby="delete-dialog-title" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:400px;max-width:100%;">
    <div class="flex items-start gap-4 px-6 pt-6 pb-5">
      <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background:var(--claude-accent);color:var(--claude-brand-500);">
        <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 11v6"/><path d="M14 11v6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
      </div>
      <div class="min-w-0 pt-0.5">
        <h3 id="delete-dialog-title" class="text-[15px] font-semibold mb-1.5" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">删除这个知识库？</h3>
        <p class="text-[13px] leading-5" style="color:var(--claude-muted-foreground);">“<span id="delete-kb-name" style="color:var(--claude-foreground);font-weight:500;"></span>”及其关联内容将被永久删除，此操作无法撤销。</p>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2.5 px-6 py-4" style="border-top:1px solid var(--claude-border);">
      <button @click="cancelDeleteKB()" class="px-4 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer claude-menu-item" style="background:transparent;color:var(--claude-foreground);border:1px solid var(--claude-border);">取消</button>
      <button @click="confirmDeleteKB()" class="px-4 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer hover:opacity-90 active:scale-[0.98]" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);border:none;">删除知识库</button>
    </div>
  </div>
</div>
  </div>
</template>

<script>
import { createKnowledgeBaseListViewController } from '@/controllers/KnowledgeBaseListView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'KnowledgeBaseListView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({
    controller: null,
    sortMenuOpen: false,
    sortMode: 'time-desc',
    sortLabel: '最近创建',
    sortOptions: [
      { value: 'time-desc', label: '最近创建' },
      { value: 'time-asc', label: '最早创建' },
      { value: 'name-asc', label: '名称 A–Z' },
      { value: 'name-desc', label: '名称 Z–A' },
    ],
  }),
  mounted() {
    document.title = "图知识库列表";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createKnowledgeBaseListViewController();
  },
  methods: {
    cancelDeleteKB(...args) {
      return this.controller?.cancelDeleteKB(...args);
    },
    confirmDeleteKB(...args) {
      return this.controller?.confirmDeleteKB(...args);
    },
    createKB(...args) {
      return this.controller?.createKB(...args);
    },
    deleteKB(...args) {
      return this.controller?.deleteKB(...args);
    },
    filterKBList(...args) {
      return this.controller?.filterKBList(...args);
    },
    sortKBList(...args) {
      return this.controller?.sortKBList(...args);
    },
    selectKBSort(item) {
      this.sortMode = item.value;
      this.sortLabel = item.label;
      this.sortMenuOpen = false;
      return this.controller?.sortKBList(item.value);
    },
    triggerNewKBCoverUpload(...args) {
      return this.controller?.triggerNewKBCoverUpload(...args);
    },
    toggleNewKBCard(...args) {
      return this.controller?.toggleNewKBCard(...args);
    },
    uploadNewKBCover(...args) {
      return this.controller?.uploadNewKBCover(...args);
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



@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
@keyframes trace-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
}
.task-action-btn { position: relative; }
.task-tooltip {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--claude-foreground);
  color: var(--claude-background);
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
  z-index: 10;
  font-family: var(--claude-font-sans);
}
.task-action-btn:hover .task-tooltip { opacity: 1; }

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

</style>
