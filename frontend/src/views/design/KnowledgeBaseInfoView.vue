<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="info" />

<AppSearchDialog />

<main id="app-main" class="h-screen min-h-0 overflow-y-auto transition-all duration-300" style="margin-left:260px;" data-scroll-region="primary">
  <div class="max-w-[800px] w-full mx-auto px-10 py-14">

    <section class="mb-12">
      <div class="flex items-start justify-between gap-6 mb-5">
        <h1 id="kb-name" contenteditable="false" class="text-[36px] font-normal leading-tight" style="font-family:var(--claude-font-display);color:var(--claude-foreground);letter-spacing:-0.02em;">
          企业知识图谱
        </h1>
        <div class="flex items-center gap-2 shrink-0">
        <button id="kb-edit-button" @click="toggleEdit()" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all hover:opacity-90" style="background:var(--claude-primary);color:var(--claude-primary-foreground);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          <span id="kb-edit-label">编辑</span>
        </button>
        <button id="kb-cancel-button" @click="cancelEdit()" class="hidden inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-75" style="color:var(--claude-muted-foreground);background:transparent;border:1px solid var(--claude-border);">取消</button>
        </div>
      </div>

      <div class="flex items-center gap-2 mb-6">
        <span id="kb-uuid" class="text-[13px] tabular-nums" style="font-family:var(--claude-font-mono);color:var(--claude-muted-foreground);">KB-2024-001</span>
        <button class="copy-btn" @click="copyUUID()" aria-label="复制 UUID">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </button>
      </div>

      <p id="kb-desc" contenteditable="false" class="text-[15px] leading-[1.85] mb-8" style="font-family:var(--claude-font-serif);color:var(--claude-foreground);max-width:640px;">
        企业内部知识管理系统，包含人员、部门、项目、技能等实体及其关联关系，支持智能问答和知识推理。
      </p>

      <div class="flex items-center gap-3 flex-wrap">
        <div class="inline-flex items-center gap-2 px-3 py-2 rounded-lg" style="background:var(--claude-secondary);border:1px solid var(--claude-border);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          <span class="text-[11px]" style="color:var(--claude-muted-foreground);">创建</span>
          <span id="kb-created-time" class="text-[12px] tabular-nums" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);">2024年01月15日</span>
        </div>
        <div class="inline-flex items-center gap-2 px-3 py-2 rounded-lg" style="background:var(--claude-secondary);border:1px solid var(--claude-border);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          <span class="text-[11px]" style="color:var(--claude-muted-foreground);">更新</span>
          <span id="kb-updated-time" class="text-[12px] tabular-nums" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);">2024年01月15日</span>
        </div>
      </div>
    </section>

    <section class="mb-12">
      <div id="kb-cover" class="w-full rounded-2xl overflow-hidden relative" style="height:260px;background:var(--claude-muted);">
        <svg class="absolute inset-0 w-full h-full opacity-[0.15]" viewBox="0 0 800 260" preserveAspectRatio="none">
          <defs>
            <pattern id="coverPattern" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
              <circle cx="3" cy="3" r="1" fill="var(--claude-border)"/>
              <circle cx="15" cy="15" r="1" fill="var(--claude-border)"/>
            </pattern>
          </defs>
          <rect width="800" height="260" fill="url(#coverPattern)"/>
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="flex flex-col items-center gap-2 opacity-40">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--claude-muted-foreground);"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            <span class="text-[12px]" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">知识库封面</span>
          </div>
        </div>
        <div id="cover-edit-overlay" class="hidden absolute inset-0 items-center justify-center opacity-0 hover:opacity-100 transition-opacity cursor-pointer" style="background:rgba(0,0,0,0.25);" @click="triggerCoverUpload()">
          <div class="flex flex-col items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            <span class="text-[13px] font-medium" style="color:var(--claude-primary-foreground);">上传封面</span>
          </div>
        </div>
      </div>
    </section>

    <section id="edit-section" class="hidden mb-12">
      <div class="py-8" style="border-top:1px solid var(--claude-border);">
        <div class="flex flex-col gap-6" style="max-width:560px;">
          <h3 class="text-[16px] font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">编辑知识库信息</h3>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-medium" style="color:var(--claude-muted-foreground);">名称</label>
            <input id="edit-name" type="text" value="企业知识图谱" class="edit-input" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-medium" style="color:var(--claude-muted-foreground);">描述</label>
            <textarea id="edit-desc" rows="4" class="edit-textarea">企业内部知识管理系统，包含人员、部门、项目、技能等实体及其关联关系，支持智能问答和知识推理。</textarea>
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-medium" style="color:var(--claude-muted-foreground);">封面</label>
            <div class="h-24 rounded-lg flex items-center justify-center transition-colors cursor-pointer" style="border:2px dashed var(--claude-border);background:var(--claude-card);" @click="triggerCoverUpload()">
              <div class="flex flex-col items-center gap-1.5">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="color:var(--claude-muted-foreground);"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span class="text-[12px]" style="color:var(--claude-muted-foreground);">点击或拖拽上传</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3 pt-4" style="border-top:1px solid var(--claude-border);">
            <button @click="saveEdit()" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all hover:opacity-90" style="background:var(--claude-primary);color:var(--claude-primary-foreground);">
              保存修改
            </button>
            <button @click="toggleEdit()" class="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-colors hover:opacity-75" style="color:var(--claude-muted-foreground);background:transparent;">
              取消
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-12">
      <div class="flex items-center gap-8 flex-wrap">
        <div class="flex flex-col gap-1">
          <span class="text-[11px] tracking-wider font-medium" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">架构</span>
          <span id="kb-schema-count" class="text-[22px] font-semibold tabular-nums" style="color:var(--claude-foreground);font-family:var(--claude-font-sans);">12</span>
        </div>
        <div class="stat-divider"></div>
        <div class="flex flex-col gap-1">
          <span class="text-[11px] tracking-wider font-medium" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">知识图谱</span>
          <span id="kb-graph-count" class="text-[22px] font-semibold tabular-nums" style="color:var(--claude-foreground);font-family:var(--claude-font-sans);">0</span>
        </div>
        <div class="stat-divider"></div>
        <div class="flex flex-col gap-1">
          <span class="text-[11px] uppercase tracking-wider font-medium" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">实体</span>
          <span id="kb-entity-count" class="text-[22px] font-semibold tabular-nums" style="color:var(--claude-foreground);font-family:var(--claude-font-sans);">0</span>
        </div>
        <div class="stat-divider"></div>
        <div class="flex flex-col gap-1">
          <span class="text-[11px] uppercase tracking-wider font-medium" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">三元组</span>
          <span id="kb-triple-count" class="text-[22px] font-semibold tabular-nums" style="color:var(--claude-foreground);font-family:var(--claude-font-sans);">0</span>
        </div>
      </div>
    </section>

  </div>
</main>

<input id="kb-cover-file" type="file" accept="image/*" class="hidden" @change="uploadCover($event.currentTarget)">

<TaskCenter />


  </div>
</template>

<script>
import { createKnowledgeBaseInfoViewController } from '@/controllers/KnowledgeBaseInfoView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'KnowledgeBaseInfoView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "图知识库信息";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createKnowledgeBaseInfoViewController();
  },
  methods: {
    cancelEdit(...args) {
      return this.controller?.cancelEdit(...args);
    },
    copyUUID(...args) {
      return this.controller?.copyUUID(...args);
    },
    saveEdit(...args) {
      return this.controller?.saveEdit(...args);
    },
    toggleEdit(...args) {
      return this.controller?.toggleEdit(...args);
    },
    triggerCoverUpload(...args) {
      return this.controller?.triggerCoverUpload(...args);
    },
    uploadCover(...args) {
      return this.controller?.uploadCover(...args);
    },
  },
};
</script>

<style>

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
