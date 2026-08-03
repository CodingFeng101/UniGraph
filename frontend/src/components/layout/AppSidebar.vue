<template>
<aside id="app-sidebar" class="fixed left-0 top-0 bottom-0 z-[80] w-[260px] flex flex-col transition-all duration-300" style="background:var(--claude-card);">
  <div class="h-12 flex items-center justify-center">
    <div class="sidebar-logo flex items-center gap-2.5 w-full px-4">
      <svg width="24" height="24" viewBox="0 0 28 28" fill="none" class="shrink-0"><circle cx="8" cy="8" r="3" fill="var(--claude-brand-500)"/><circle cx="20" cy="6" r="2.5" fill="var(--claude-brand-500)" opacity="0.6"/><circle cx="14" cy="20" r="2.5" fill="var(--claude-brand-500)" opacity="0.6"/><line x1="10" y1="9" x2="18" y2="7" stroke="var(--claude-brand-500)" stroke-width="1.2"/><line x1="9" y1="10" x2="13" y2="18" stroke="var(--claude-brand-500)" stroke-width="1.2"/><line x1="18" y1="8" x2="15" y2="18" stroke="var(--claude-brand-500)" stroke-width="1.2" opacity="0.5"/></svg>
      <span class="sidebar-text text-sm font-semibold flex-1" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">UniGraph</span>
    </div>
    <button type="button" @click="toggleSearchModal()" data-title="搜索" class="sidebar-collapsed-hide w-8 h-8 flex items-center justify-center rounded-lg cursor-pointer transition-colors hover:opacity-70" style="background:transparent;border:none;color:var(--claude-muted-foreground);" aria-label="搜索聊天记录">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    </button>
    <button type="button" @click="toggleSidebar()" data-title="收起" class="sidebar-toggle-btn w-8 h-8 flex items-center justify-center rounded-lg cursor-pointer transition-colors hover:opacity-70" style="background:transparent;border:none;color:var(--claude-muted-foreground);" aria-label="收起侧栏">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
    </button>
  </div>

  <nav class="px-3 pt-1 pb-2 space-y-0">
    <a href="/unigraph/workspace" data-title="图知识库列表" class="sidebar-nav-item flex items-center justify-center gap-2.5 px-3 py-[7px] rounded-lg transition-colors" style="background:var(--claude-accent);color:var(--claude-foreground);text-decoration:none;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="shrink-0"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
      <span class="sidebar-text flex-1 text-left">图知识库列表</span>
    </a>
    <a id="workspace-info-link" href="/unigraph/workspace" data-title="信息" class="sidebar-nav-item flex items-center justify-center gap-2.5 px-3 py-[7px] rounded-lg transition-colors" style="color:var(--claude-muted-foreground);text-decoration:none;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
      <span class="sidebar-text flex-1 text-left">信息</span>
    </a>
    <a id="workspace-design-link" href="/unigraph/workspace" data-title="设计" class="sidebar-nav-item flex items-center justify-center gap-2.5 px-3 py-[7px] rounded-lg transition-colors" style="color:var(--claude-muted-foreground);text-decoration:none;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="shrink-0"><circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><line x1="12" y1="8" x2="5" y2="16"/><line x1="12" y1="8" x2="19" y2="16"/><line x1="8" y1="19" x2="16" y2="19"/></svg>
      <span class="sidebar-text flex-1 text-left">设计</span>
    </a>
    <a id="workspace-build-link" href="/unigraph/workspace" data-title="构建" class="sidebar-nav-item flex items-center justify-center gap-2.5 px-3 py-[7px] rounded-lg transition-colors" style="color:var(--claude-muted-foreground);text-decoration:none;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="shrink-0"><polygon points="12,2 22,20 2,20"/></svg>
      <span class="sidebar-text flex-1 text-left">构建</span>
    </a>
    <a id="workspace-app-link" href="/unigraph/workspace" data-title="新建对话" @click="handleNewChat" class="sidebar-nav-item flex items-center justify-center gap-2.5 px-3 py-[7px] rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" style="color:var(--claude-muted-foreground);text-decoration:none;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" class="shrink-0"><circle cx="12" cy="12" r="10" fill="var(--claude-muted)" stroke="none"/><line x1="12" y1="7" x2="12" y2="17" stroke="white" stroke-width="2.5"/><line x1="7" y1="12" x2="17" y2="12" stroke="white" stroke-width="2.5"/></svg>
      <span class="sidebar-text flex-1 text-left">新建对话</span>
    </a>
  </nav>

  <div class="sidebar-content flex-1 overflow-y-auto px-3 pt-2 pb-1 min-h-0">
    <div class="hidden items-center justify-between px-3 mb-1.5">
      <span class="text-[11px] font-medium uppercase tracking-wider" style="color:var(--claude-muted-foreground);">Recents</span>
      <button type="button" @click="showToast('排序')" class="w-6 h-6 flex items-center justify-center rounded transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" aria-label="排序">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/></svg>
      </button>
    </div>

    <div v-once class="space-y-0.5" style="visibility:hidden;">
      <div class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]" style="background:var(--claude-accent);">
        <a href="#" class="block" style="text-decoration:none;">
          <p class="text-[13px] truncate pr-6" style="color:var(--claude-foreground);">关于张磊的技能查询</p>
          <span class="text-[11px] block mt-0.5" style="color:var(--claude-muted-foreground);">今天 14:32</span>
        </a>
        <button type="button" @click="toggleMenu($event.currentTarget)" class="absolute right-2 top-2 w-6 h-6 flex items-center justify-center rounded opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
        </button>
        <div class="hidden absolute right-2 top-8 rounded-lg overflow-hidden z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:110px;">
          <button type="button" @click="showToast('重命名')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
            重命名
          </button>
          <button type="button" @click="showToast('收藏')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            收藏
          </button>
          <div style="border-top:1px solid var(--claude-border);margin:2px 0;"></div>
          <button type="button" @click="showToast('删除')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-destructive);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            删除
          </button>
        </div>
      </div>
      <div class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]">
        <a href="#" class="block" style="text-decoration:none;">
          <p class="text-[13px] truncate pr-6" style="color:var(--claude-foreground);">技术研发部的组织架构是什么</p>
          <span class="text-[11px] block mt-0.5" style="color:var(--claude-muted-foreground);">今天 11:08</span>
        </a>
        <button type="button" @click="toggleMenu($event.currentTarget)" class="absolute right-2 top-2 w-6 h-6 flex items-center justify-center rounded opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
        </button>
        <div class="hidden absolute right-2 top-8 rounded-lg overflow-hidden z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:110px;">
          <button type="button" @click="showToast('重命名')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
            重命名
          </button>
          <button type="button" @click="showToast('收藏')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            收藏
          </button>
          <div style="border-top:1px solid var(--claude-border);margin:2px 0;"></div>
          <button type="button" @click="showToast('删除')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-destructive);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            删除
          </button>
        </div>
      </div>
      <div class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]">
        <a href="#" class="block" style="text-decoration:none;">
          <p class="text-[13px] truncate pr-6" style="color:var(--claude-foreground);">有哪些跨部门协作项目</p>
          <span class="text-[11px] block mt-0.5" style="color:var(--claude-muted-foreground);">昨天 16:45</span>
        </a>
        <button type="button" @click="toggleMenu($event.currentTarget)" class="absolute right-2 top-2 w-6 h-6 flex items-center justify-center rounded opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
        </button>
        <div class="hidden absolute right-2 top-8 rounded-lg overflow-hidden z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:110px;">
          <button type="button" @click="showToast('重命名')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
            重命名
          </button>
          <button type="button" @click="showToast('收藏')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            收藏
          </button>
          <div style="border-top:1px solid var(--claude-border);margin:2px 0;"></div>
          <button type="button" @click="showToast('删除')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-destructive);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            删除
          </button>
        </div>
      </div>
      <div class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]">
        <a href="#" class="block" style="text-decoration:none;">
          <p class="text-[13px] truncate pr-6" style="color:var(--claude-foreground);">供应链优化系统包含哪些模块</p>
          <span class="text-[11px] block mt-0.5" style="color:var(--claude-muted-foreground);">昨天 10:22</span>
        </a>
        <button type="button" @click="toggleMenu($event.currentTarget)" class="absolute right-2 top-2 w-6 h-6 flex items-center justify-center rounded opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
        </button>
        <div class="hidden absolute right-2 top-8 rounded-lg overflow-hidden z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:110px;">
          <button type="button" @click="showToast('重命名')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
            重命名
          </button>
          <button type="button" @click="showToast('收藏')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            收藏
          </button>
          <div style="border-top:1px solid var(--claude-border);margin:2px 0;"></div>
          <button type="button" @click="showToast('删除')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-destructive);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            删除
          </button>
        </div>
      </div>
      <div class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]">
        <a href="#" class="block" style="text-decoration:none;">
          <p class="text-[13px] truncate pr-6" style="color:var(--claude-foreground);">产品部与运维部之间的协作关系</p>
          <span class="text-[11px] block mt-0.5" style="color:var(--claude-muted-foreground);">3天前</span>
        </a>
        <button type="button" @click="toggleMenu($event.currentTarget)" class="absolute right-2 top-2 w-6 h-6 flex items-center justify-center rounded opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
        </button>
        <div class="hidden absolute right-2 top-8 rounded-lg overflow-hidden z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:110px;">
          <button type="button" @click="showToast('重命名')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
            重命名
          </button>
          <button type="button" @click="showToast('收藏')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            收藏
          </button>
          <div style="border-top:1px solid var(--claude-border);margin:2px 0;"></div>
          <button type="button" @click="showToast('删除')" class="flex items-center gap-2 w-full px-3 py-2 text-xs transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;color:var(--claude-destructive);">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            删除
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="px-3 py-2.5 relative mt-auto">
    <button type="button" data-role="user-menu-trigger" @click="toggleUserDropdown()" class="w-full flex items-center justify-center gap-3 rounded-lg px-2 py-1.5 transition-colors hover:opacity-80 cursor-pointer" style="background:transparent;border:none;">
      <div class="relative w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium shrink-0 overflow-hidden" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);">
        <span>{{ userInitials }}</span>
        <img v-if="avatarSrc" :key="avatarSrc" :src="avatarSrc" :alt="`${userName}的头像`" class="absolute inset-0 w-full h-full object-cover transition-opacity duration-200" :class="avatarImageLoaded ? 'opacity-100' : 'opacity-0'" @load="handleAvatarLoad" @error="handleAvatarError" />
      </div>
      <div class="flex-1 min-w-0 text-left sidebar-collapsed-hide">
        <p class="text-sm font-medium truncate" style="color:var(--claude-foreground);">{{ userName }}</p>
        <p class="text-[10px]" style="color:var(--claude-muted-foreground);">{{ userRole }}</p>
      </div>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);flex-shrink:0;" class="sidebar-collapsed-hide"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <div id="user-dropdown" class="hidden absolute bottom-full left-3 w-[236px] mb-2 rounded-xl overflow-visible z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
      <div class="px-4 py-3" style="border-bottom:1px solid var(--claude-border);"><p class="text-xs truncate" style="color:var(--claude-muted-foreground);">{{ userInfo.email || '未设置邮箱' }}</p></div>
      <div class="py-1">
        <a href="/unigraph/usercenter" class="user-menu-item flex items-center gap-3 px-4 py-2.5 text-sm transition-colors" style="color:var(--claude-foreground);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          个人中心
        </a>
        <a href="/unigraph/tutorial" class="user-menu-item flex items-center gap-3 px-4 py-2.5 text-sm transition-colors" style="color:var(--claude-foreground);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
          视频教程
        </a>
        <a href="/unigraph/docs" class="user-menu-item flex items-center gap-3 px-4 py-2.5 text-sm transition-colors" style="color:var(--claude-foreground);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          技术文档
        </a>
        <div style="border-top:1px solid var(--claude-border);margin:4px 0;"></div>
        <a href="/unigraph/settings" class="user-menu-item flex items-center gap-3 px-4 py-2.5 text-sm transition-colors" style="color:var(--claude-foreground);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          设置
        </a>
        <div class="relative" @mouseenter="openThemeSubmenu()" @mouseleave="closeThemeSubmenu()">
          <button type="button" @click="toggleThemeSubmenu()" class="user-menu-item w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
            <span class="flex items-center gap-3">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              主题
            </span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
          <div id="theme-submenu" class="hidden absolute left-full bottom-0 ml-1 rounded-xl overflow-hidden z-50 p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:150px;">
            <button type="button" @click="setTheme('light')" class="claude-menu-item w-full flex items-center gap-2 px-3.5 py-2 text-sm rounded-lg transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
              <svg data-theme-check="light" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              <span>亮色</span>
            </button>
            <button type="button" @click="setTheme('dark')" class="claude-menu-item w-full flex items-center gap-2 px-3.5 py-2 text-sm rounded-lg transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
              <svg data-theme-check="dark" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              <span>暗色</span>
            </button>
            <button type="button" @click="setTheme('system')" class="claude-menu-item w-full flex items-center gap-2 px-3.5 py-2 text-sm rounded-lg transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
              <svg data-theme-check="system" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              <span>跟随系统</span>
            </button>
          </div>
        </div>
        <div class="relative" @mouseenter="openLangSubmenu()" @mouseleave="closeLangSubmenu()">
          <button type="button" @click="toggleLangSubmenu()" class="user-menu-item w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
            <span class="flex items-center gap-3">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              语言
            </span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
          <div id="lang-submenu" class="hidden absolute left-full top-0 ml-1 rounded-xl overflow-hidden z-50 p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);min-width:150px;">
            <button type="button" @click="setLang('zh')" class="claude-menu-item w-full flex items-center gap-2 px-3.5 py-2 text-sm rounded-lg transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
              <svg data-lang-check="zh" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              中文
            </button>
            <button type="button" @click="setLang('en')" class="claude-menu-item w-full flex items-center gap-2 px-3.5 py-2 text-sm rounded-lg transition-colors cursor-pointer" style="background:none;border:none;color:var(--claude-foreground);">
              <svg data-lang-check="en" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              English
            </button>
          </div>
        </div>
        <div style="border-top:1px solid var(--claude-border);margin:4px 0;"></div>
        <button type="button" @click="handleLogout" class="user-menu-item w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors cursor-pointer" style="background:transparent;border:none;color:var(--claude-destructive);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          退出登录
        </button>
      </div>
    </div>
  </div>
</aside>
</template>

<script>
import { Auth } from '@/api/runtime/auth';
import { KgBaseAPI } from '@/api';
import { resolveImageUrl } from '@/utils/image-url';

export default {
  name: 'AppSidebar',
  props: {
    active: { type: String, default: 'list' },
  },
  data() {
    return {
      userInfo: Auth.getUserInfo() || {},
      avatarImageLoaded: false,
      avatarRetryCount: 0,
      avatarRevision: Date.now(),
      avatarRetryTimer: null,
      defaultKnowledgeBaseUuid: '',
    };
  },
  computed: {
    userName() {
      return this.userInfo.nickname || this.userInfo.username || '用户';
    },
    userInitials() {
      return this.userName.slice(0, 2).toUpperCase();
    },
    userRole() {
      return this.userInfo.is_superuser ? '管理员' : '用户';
    },
    avatarSrc() {
      const path = this.userInfo.avatar;
      if (!path) return '';
      const resolved = resolveImageUrl(path);
      if (/^(data:|blob:)/i.test(resolved)) return resolved;
      const url = new URL(resolved);
      url.searchParams.set('avatar_v', String(this.avatarRevision));
      return url.href;
    },
  },
  async mounted() {
    this.applySavedPreferences();
    this.updateNavigation();
    const history = this.$el.querySelector('.sidebar-content .space-y-0\\.5');
    if (history) {
      history.innerHTML = '';
      history.style.visibility = 'visible';
    }
    if (this.$route.name !== 'graph-application') {
      window.ChatSidebar?.render();
      await window.ChatSidebar?.load();
      if (!this.defaultKnowledgeBaseUuid) await this.resolveDefaultKnowledgeBase();
    }
    window.TaskManager?.render();
    window.addEventListener('unigraph:user-updated', this.syncUserInfo);
    window.addEventListener('unigraph:knowledge-base-default', this.handleDefaultKnowledgeBase);
    window.addEventListener('storage', this.handleUserStorage);
    this.refreshUserInfo();
  },
  beforeUnmount() {
    window.removeEventListener('unigraph:user-updated', this.syncUserInfo);
    window.removeEventListener('unigraph:knowledge-base-default', this.handleDefaultKnowledgeBase);
    window.removeEventListener('storage', this.handleUserStorage);
    if (this.avatarRetryTimer) window.clearTimeout(this.avatarRetryTimer);
  },
  updated() {
    this.updateNavigation();
  },
  methods: {
    async refreshUserInfo() {
      try {
        const response = await KgBaseAPI.auth.getUserInfo();
        if (response.code === 200 && response.data) {
          Auth.setUserInfo(response.data);
        }
      } catch {
        // Keep the cached user when the profile endpoint is temporarily unavailable.
      }
    },
    syncUserInfo(event) {
      const nextUser = event.detail || Auth.getUserInfo() || {};
      const mergedUser = {
        ...this.userInfo,
        ...nextUser,
        avatar: nextUser.avatar || this.userInfo.avatar || null,
      };
      const avatarChanged = mergedUser.avatar !== this.userInfo.avatar;
      this.userInfo = mergedUser;
      if (avatarChanged) {
        this.avatarImageLoaded = false;
        this.avatarRetryCount = 0;
        this.avatarRevision = Date.now();
      }
    },
    handleAvatarLoad() {
      this.avatarImageLoaded = true;
      this.avatarRetryCount = 0;
      if (this.avatarRetryTimer) {
        window.clearTimeout(this.avatarRetryTimer);
        this.avatarRetryTimer = null;
      }
    },
    handleAvatarError() {
      this.avatarImageLoaded = false;
      if (!this.userInfo.avatar || this.avatarRetryCount >= 12) return;
      this.avatarRetryCount += 1;
      if (this.avatarRetryTimer) window.clearTimeout(this.avatarRetryTimer);
      this.avatarRetryTimer = window.setTimeout(() => {
        this.avatarRevision = Date.now();
        this.avatarRetryTimer = null;
      }, Math.min(5000, 500 * this.avatarRetryCount));
    },
    handleUserStorage(event) {
      if (event.key === 'user') this.syncUserInfo({ detail: Auth.getUserInfo() });
    },
    handleDefaultKnowledgeBase(event) {
      this.defaultKnowledgeBaseUuid = event.detail?.uuid || '';
      this.$nextTick(this.updateNavigation);
    },
    async handleLogout() {
      document.getElementById('user-dropdown')?.classList.add('hidden');
      await Auth.logout();
    },
    async handleNewChat(event) {
      event.preventDefault();
      if (this.$route.name === 'graph-application' && typeof window.newConversation === 'function') {
        window.newConversation();
        return;
      }
      const uuid = this.$route.params.uuid || this.defaultKnowledgeBaseUuid || await this.resolveDefaultKnowledgeBase();
      if (!uuid) {
        this.showToast('请先创建知识库并完成索引构建');
        return;
      }
      await this.$router.push(`/unigraphs/${uuid}/qa`);
    },
    async resolveDefaultKnowledgeBase() {
      try {
        const basesResponse = await KgBaseAPI.kgBase.getAll();
        const bases = basesResponse.code === 200 && Array.isArray(basesResponse.data) ? basesResponse.data : [];
        const contexts = await Promise.all(bases.map(async (base) => {
          try {
            const response = await KgBaseAPI.knowledgeGraph.getAll(base.uuid);
            const hasIndex = response.code === 200 && Array.isArray(response.data)
              && response.data.some((graph) => Number(graph.index_status) === 1);
            return { base, hasIndex };
          } catch {
            return { base, hasIndex: false };
          }
        }));
        const preferred = contexts
          .filter((context) => context.hasIndex)
          .sort((left, right) => new Date(right.base.created_time || 0) - new Date(left.base.created_time || 0))[0]?.base;
        this.defaultKnowledgeBaseUuid = preferred?.uuid || '';
        this.$nextTick(this.updateNavigation);
        return this.defaultKnowledgeBaseUuid;
      } catch {
        return '';
      }
    },
    updateNavigation() {
      const uuid = this.$route.params.uuid || this.$route.query.uuid || '';
      const appUuid = uuid || this.defaultKnowledgeBaseUuid;
      const links = {
        list: '/unigraph/workspace',
        info: uuid ? `/unigraph/unigraphs/${uuid}/info` : '/unigraph/workspace',
        design: uuid ? `/unigraph/unigraphs/${uuid}/structure` : '/unigraph/workspace',
        build: uuid ? `/unigraph/unigraphs/${uuid}/graph` : '/unigraph/workspace',
        app: appUuid ? `/unigraph/unigraphs/${appUuid}/qa` : '/unigraph/workspace',
      };
      const items = [...this.$el.querySelectorAll('nav > a')].slice(0, 5);
      Object.keys(links).forEach((key, index) => {
        const item = items[index];
        if (!item) return;
        const disabled = !uuid && ['info', 'design', 'build'].includes(key);
        const isActivePage = key === this.active && key !== 'app';
        item.href = links[key];
        item.style.background = isActivePage ? 'var(--claude-accent)' : '';
        item.style.color = isActivePage
          ? 'var(--claude-foreground)'
          : 'var(--claude-muted-foreground)';
        item.setAttribute('aria-disabled', disabled ? 'true' : 'false');
        item.style.pointerEvents = disabled ? 'none' : '';
        item.style.opacity = disabled ? '0.42' : '';
        item.style.cursor = disabled ? 'not-allowed' : '';
        item.tabIndex = disabled ? -1 : 0;
        if (isActivePage) item.setAttribute('aria-current', 'page');
        else item.removeAttribute('aria-current');
      });
    },
    applySavedPreferences() {
      this.setTheme(localStorage.getItem('unigraph-theme') || 'system', false);
      this.setLang(localStorage.getItem('unigraph-language') || 'zh', false);
    },
    setLang(lang, notify = true) {
      const names = { zh: '中文', en: 'English' };
      if (!names[lang]) return;
      localStorage.setItem('unigraph-language', lang);
      document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
      document.documentElement.dataset.language = lang;
      document.querySelectorAll('[data-lang-check]').forEach((icon) => {
        icon.style.visibility = icon.dataset.langCheck === lang ? 'visible' : 'hidden';
      });
      document.getElementById('lang-submenu')?.classList.add('hidden');
      window.dispatchEvent(new CustomEvent('unigraph:language-change', { detail: { lang } }));
      if (notify) this.showToast(lang === 'zh' ? `语言已切换为：${names[lang]}` : 'Language changed to English');
    },
    setTheme(theme, notify = true) {
      if (!['light', 'dark', 'system'].includes(theme)) return;
      localStorage.setItem('unigraph-theme', theme);
      const resolved = theme === 'system'
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
        : theme;
      document.documentElement.dataset.theme = resolved;
      document.documentElement.dataset.themePreference = theme;
      document.querySelectorAll('[data-theme-check]').forEach((icon) => {
        icon.style.visibility = icon.dataset.themeCheck === theme ? 'visible' : 'hidden';
      });
      document.getElementById('theme-submenu')?.classList.add('hidden');
      if (notify) this.showToast(`主题已切换为：${{ light: '亮色', dark: '暗色', system: '跟随系统' }[theme]}`);
    },
    showToast(message) {
      if (typeof window.showToast === 'function') {
        window.showToast(message);
        return;
      }
      const toast = document.createElement('div');
      toast.textContent = message;
      toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-2.5 rounded-lg text-sm z-[200]';
      toast.style.cssText = 'background:var(--claude-foreground);color:var(--claude-background);box-shadow:var(--claude-shadow-lg);';
      document.body.appendChild(toast);
      window.setTimeout(() => toast.remove(), 1800);
    },
    toggleLangSubmenu() {
      document.getElementById('theme-submenu')?.classList.add('hidden');
      document.getElementById('lang-submenu')?.classList.toggle('hidden');
    },
    toggleThemeSubmenu() {
      document.getElementById('lang-submenu')?.classList.add('hidden');
      document.getElementById('theme-submenu')?.classList.toggle('hidden');
    },
    openThemeSubmenu() {
      document.getElementById('lang-submenu')?.classList.add('hidden');
      document.getElementById('theme-submenu')?.classList.remove('hidden');
    },
    closeThemeSubmenu() {
      document.getElementById('theme-submenu')?.classList.add('hidden');
    },
    openLangSubmenu() {
      document.getElementById('theme-submenu')?.classList.add('hidden');
      document.getElementById('lang-submenu')?.classList.remove('hidden');
    },
    closeLangSubmenu() {
      document.getElementById('lang-submenu')?.classList.add('hidden');
    },
    toggleMenu(button) {
      button?.nextElementSibling?.classList.toggle('hidden');
    },
    toggleSearchModal() {
      const modal = document.getElementById('search-modal');
      modal?.classList.toggle('hidden');
      if (modal && !modal.classList.contains('hidden')) {
        document.getElementById('search-input')?.focus();
      }
    },
    toggleSidebar() {
      const sidebar = document.getElementById('app-sidebar');
      const main = document.getElementById('app-main');
      const collapsed = sidebar?.classList.toggle('sidebar-collapsed');
      if (main) {
        main.style.marginLeft = collapsed ? '48px' : '260px';
        main.style.width = collapsed ? 'calc(100% - 48px)' : 'calc(100% - 260px)';
      }
    },
    toggleUserDropdown() {
      document.getElementById('user-dropdown')?.classList.toggle('hidden');
    },
  },
};
</script>

<style scoped>
#app-sidebar {
  font-family: Arial, "PingFang SC", "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif;
  font-feature-settings: "kern";
  letter-spacing: -0.01em;
}

#app-sidebar.sidebar-collapsed { width: 48px; }
#app-sidebar.sidebar-collapsed .sidebar-text,
#app-sidebar.sidebar-collapsed .sidebar-logo,
#app-sidebar.sidebar-collapsed .sidebar-content,
#app-sidebar.sidebar-collapsed .sidebar-collapsed-hide,
#app-sidebar.sidebar-collapsed nav a span { display: none; }
#app-sidebar.sidebar-collapsed .h-12 { justify-content: center; }
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn { margin: 0; }

.sidebar-nav-item {
  font-size: 15px;
  font-weight: 400;
  line-height: 22px;
}

.sidebar-nav-item:not([aria-disabled="true"]):hover {
  background: var(--claude-secondary) !important;
  color: var(--claude-foreground) !important;
}

.user-menu-item {
  border-radius: 8px;
  text-decoration: none;
}

.user-menu-item:hover {
  background: var(--claude-accent) !important;
}
</style>
