<template>
<div id="search-modal" class="hidden fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]" style="background:rgba(0,0,0,0.3);">
  <div class="w-[520px] rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
    <div class="flex items-center gap-2 px-4 py-3 border-b" style="border-color:var(--claude-border);">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input type="text" id="search-input" placeholder="Search chats and projects" class="flex-1 bg-transparent text-sm outline-none" style="color:var(--claude-foreground);font-family:var(--claude-font-sans);" @input="filterSearchResults($event.currentTarget.value)">
      <button @click="toggleSearchModal()" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="max-h-[50vh] overflow-y-auto">
      <div class="px-4 py-2 border-b" style="border-color:var(--claude-border);">
        <div class="flex items-center justify-between cursor-pointer px-3 py-2 rounded-lg transition-colors" style="background:var(--claude-accent);" @click="showToast('进入对话');toggleSearchModal();">
          <div class="flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="text-sm font-medium" style="color:var(--claude-foreground);">关于张磊的技能查询</span>
          </div>
          <span class="text-xs" style="color:var(--claude-muted-foreground);">Enter</span>
        </div>
      </div>
      <div class="px-2">
        <div class="flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" @click="showToast('进入对话');toggleSearchModal();">
          <div class="flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="text-sm" style="color:var(--claude-foreground);">企业架构设计方案讨论</span>
          </div>
          <span class="text-xs" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">Past month</span>
        </div>
        <div class="flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" @click="showToast('进入对话');toggleSearchModal();">
          <div class="flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="text-sm" style="color:var(--claude-foreground);">知识图谱构建进度</span>
          </div>
          <span class="text-xs" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">Past month</span>
        </div>
        <div class="flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" @click="showToast('进入对话');toggleSearchModal();">
          <div class="flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="text-sm" style="color:var(--claude-foreground);">人员技能匹配分析</span>
          </div>
          <span class="text-xs" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">Past year</span>
        </div>
        <div class="flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" @click="showToast('进入对话');toggleSearchModal();">
          <div class="flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="text-sm" style="color:var(--claude-foreground);">部门协作关系图谱</span>
          </div>
          <span class="text-xs" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">Past year</span>
        </div>
        <div class="flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" @click="showToast('进入对话');toggleSearchModal();">
          <div class="flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span class="text-sm" style="color:var(--claude-foreground);">项目依赖关系分析</span>
          </div>
          <span class="text-xs" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">Past year</span>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  name: 'AppSearchDialog',
  mounted() {
    this.globalToggleSearchModal = () => this.toggleSearchModal();
    window.toggleSearchModal = this.globalToggleSearchModal;
  },
  beforeUnmount() {
    if (window.toggleSearchModal === this.globalToggleSearchModal) {
      delete window.toggleSearchModal;
    }
  },
  methods: {
    filterSearchResults(query) {
      if (window.ChatSidebar?.filterSearch) {
        window.ChatSidebar.filterSearch(query);
        return;
      }
      const normalized = String(query || '').toLowerCase();
      this.$el.querySelectorAll('.chat-search-item').forEach((item) => {
        item.style.display = item.textContent.toLowerCase().includes(normalized) ? '' : 'none';
      });
    },
    showToast(message) {
      if (typeof window.showToast === 'function') window.showToast(message);
    },
    toggleSearchModal() {
      document.getElementById('search-modal')?.classList.toggle('hidden');
    },
  },
};
</script>
