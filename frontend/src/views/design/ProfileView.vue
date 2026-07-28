<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="app" />

<AppSearchDialog />

<main id="app-main" data-scroll-region="primary" class="min-h-0 overflow-y-auto transition-all duration-300" style="margin-left:260px;">
  <div class="max-w-[780px] mx-auto px-8 py-12">
    <div class="mb-10">
      <h1 class="text-[28px] leading-tight" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">个人中心</h1>
      <p class="mt-2 text-sm" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-serif);">管理个人资料与模型配置</p>
    </div>

    <div class="mb-12 px-1 py-5 flex items-center gap-5">
      <div class="relative w-16 h-16 shrink-0">
        <button id="profile-avatar" type="button" @click="triggerAvatarUpload()" class="group relative w-16 h-16 rounded-full flex items-center justify-center text-lg font-semibold overflow-hidden cursor-pointer" style="background:var(--claude-accent);color:var(--claude-brand-700);border:none;" title="点击更换头像">U</button>
        <div id="avatar-upload-hint" class="hidden pointer-events-none absolute inset-0 rounded-full items-center justify-center text-[11px] font-medium" style="display:none;background:rgba(28,25,23,.62);color:#fff;">更换头像</div>
      </div>
      <input id="profile-avatar-input" type="file" class="hidden" accept="image/png,image/jpeg,image/webp,image/gif" @change="uploadAvatar($event.currentTarget)">
      <div id="profile-fields" class="min-w-0 flex-1">
        <p id="profile-nickname" class="text-lg font-semibold truncate" style="color:var(--claude-foreground);">用户</p>
        <p id="profile-email" class="text-sm mt-1 truncate" style="color:var(--claude-muted-foreground);">未设置邮箱</p>
      </div>
      <div class="flex items-center gap-2">
        <button id="profile-cancel-button" type="button" @click="cancelProfileEdit()" class="hidden h-9 px-4 rounded-lg text-sm font-medium cursor-pointer transition-opacity hover:opacity-75 active:scale-[0.98]" style="background:transparent;border:1px solid var(--claude-border);color:var(--claude-foreground);">取消</button>
        <button id="profile-edit-button" type="button" @click="editProfile()" class="h-9 px-4 rounded-lg text-sm font-medium cursor-pointer transition-opacity hover:opacity-75 active:scale-[0.98]" style="background:var(--claude-secondary);border:1px solid var(--claude-border);color:var(--claude-foreground);">编辑资料</button>
      </div>
    </div>

    <div class="mb-12">
      <h3 class="text-base font-semibold mb-1" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">大模型配置</h3>
      <p class="text-xs mb-5" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-serif);">用于知识推理和问答的大模型 API，支持添加多个模型</p>

      <div id="llm-capsules" class="flex flex-wrap items-center gap-2 mb-1">
        <div class="group inline-flex items-center gap-1.5 h-8 pl-3 pr-1.5 rounded-full transition-colors" style="background:var(--claude-card);border:1px solid var(--claude-border);">
          <span class="text-xs font-medium" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);">gpt-4o</span>
          <button type="button" @click="editCapsule($event.currentTarget)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑" aria-label="编辑模型">
            <i data-lucide="pencil" style="width:11px;height:11px;"></i>
          </button>
          <button type="button" @click="removeCapsule($event.currentTarget)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="删除" aria-label="删除模型">
            <i data-lucide="x" style="width:11px;height:11px;"></i>
          </button>
        </div>
        <div class="group inline-flex items-center gap-1.5 h-8 pl-3 pr-1.5 rounded-full transition-colors" style="background:var(--claude-card);border:1px solid var(--claude-border);">
          <span class="text-xs font-medium" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);">claude-3.5-sonnet</span>
          <button type="button" @click="editCapsule($event.currentTarget)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑" aria-label="编辑模型">
            <i data-lucide="pencil" style="width:11px;height:11px;"></i>
          </button>
          <button type="button" @click="removeCapsule($event.currentTarget)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="删除" aria-label="删除模型">
            <i data-lucide="x" style="width:11px;height:11px;"></i>
          </button>
        </div>
        <button type="button" @click="openLlmModal()" class="inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);border:1px dashed var(--claude-border);color:var(--claude-muted-foreground);" title="添加大模型" aria-label="添加大模型">
          <i data-lucide="plus" style="width:14px;height:14px;"></i>
        </button>
      </div>
    </div>

    <div class="mb-20">
      <h3 class="text-base font-semibold mb-1" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">向量嵌入配置</h3>
      <p class="text-xs mb-5" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-serif);">用于知识索引和实体向量化，支持配置多个嵌入模型</p>

      <div id="embed-capsules" class="flex flex-wrap items-center gap-2 mb-1">
        <div class="group inline-flex items-center gap-1.5 h-8 pl-3 pr-1.5 rounded-full transition-colors" style="background:var(--claude-card);border:1px solid var(--claude-border);">
          <span class="text-xs font-medium" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);">text-embedding-3-small</span>
          <button type="button" @click="editCapsule($event.currentTarget)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑" aria-label="编辑嵌入模型">
            <i data-lucide="pencil" style="width:11px;height:11px;"></i>
          </button>
          <button type="button" @click="removeCapsule($event.currentTarget)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="删除" aria-label="删除嵌入模型">
            <i data-lucide="x" style="width:11px;height:11px;"></i>
          </button>
        </div>
        <button type="button" @click="openEmbedModal()" class="inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);border:1px dashed var(--claude-border);color:var(--claude-muted-foreground);" title="添加嵌入模型" aria-label="添加嵌入模型">
          <i data-lucide="plus" style="width:14px;height:14px;"></i>
        </button>
      </div>
    </div>
  </div>
</main>

<TaskCenter />

<div id="modal-llm" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:440px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 id="modal-llm-title" class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">添加大模型</h3>
      <button @click="closeLlmModal()" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;">
        <i data-lucide="x" style="width:16px;height:16px;color:var(--claude-muted-foreground);"></i>
      </button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">Model</label>
        <input type="text" id="llm-model-input" placeholder="gpt-4o" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">API Key</label>
        <div class="relative">
          <input type="password" id="llm-key-input" placeholder="sk-..." class="w-full h-9 px-3 pr-10 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'">
          <button @click="togglePassword('llm-key-input')" class="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 transition-opacity hover:opacity-70 cursor-pointer" style="color:var(--claude-muted-foreground);background:none;border:none;" aria-label="切换密码可见性">
            <i data-lucide="eye" style="width:16px;height:16px;"></i>
          </button>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">Base URL</label>
        <input type="text" id="llm-url-input" placeholder="https://api.openai.com/v1" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'">
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="closeLlmModal()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="saveLlmCapsule()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">保存</button>
    </div>
  </div>
</div>

<div id="modal-embed" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:440px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 id="modal-embed-title" class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">添加嵌入模型</h3>
      <button @click="closeEmbedModal()" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;">
        <i data-lucide="x" style="width:16px;height:16px;color:var(--claude-muted-foreground);"></i>
      </button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">Model</label>
        <input type="text" id="embed-model-input" placeholder="text-embedding-3-small" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">API Key</label>
        <div class="relative">
          <input type="password" id="embed-key-input" placeholder="sk-..." class="w-full h-9 px-3 pr-10 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'">
          <button @click="togglePassword('embed-key-input')" class="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 transition-opacity hover:opacity-70 cursor-pointer" style="color:var(--claude-muted-foreground);background:none;border:none;" aria-label="切换密码可见性">
            <i data-lucide="eye" style="width:16px;height:16px;"></i>
          </button>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">Base URL</label>
        <input type="text" id="embed-url-input" placeholder="https://api.openai.com/v1" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" onfocus="this.style.borderColor='var(--claude-brand-500)'" onblur="this.style.borderColor='var(--claude-border)'">
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="closeEmbedModal()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="saveEmbedCapsule()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">保存</button>
    </div>
  </div>
</div>
  </div>
</template>

<script>
import { createProfileViewController } from '@/controllers/ProfileView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'ProfileView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "个人中心";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createProfileViewController();
  },
  methods: {
    togglePassword(id) {
      const input = document.getElementById(id);
      if (input) input.type = input.type === 'password' ? 'text' : 'password';
    },
    closeEmbedModal(...args) {
      return this.controller?.closeEmbedModal(...args);
    },
    closeLlmModal(...args) {
      return this.controller?.closeLlmModal(...args);
    },
    editCapsule(...args) {
      return this.controller?.editCapsule(...args);
    },
    editProfile(...args) {
      return this.controller?.editProfile(...args);
    },
    cancelProfileEdit(...args) {
      return this.controller?.cancelProfileEdit(...args);
    },
    triggerAvatarUpload(...args) {
      return this.controller?.triggerAvatarUpload(...args);
    },
    uploadAvatar(...args) {
      return this.controller?.uploadAvatar(...args);
    },
    openEmbedModal(...args) {
      return this.controller?.openEmbedModal(...args);
    },
    openLlmModal(...args) {
      return this.controller?.openLlmModal(...args);
    },
    removeCapsule(...args) {
      return this.controller?.removeCapsule(...args);
    },
    saveEmbedCapsule(...args) {
      return this.controller?.saveEmbedCapsule(...args);
    },
    saveLlmCapsule(...args) {
      return this.controller?.saveLlmCapsule(...args);
    },
    toggleTaskPanel(...args) {
      return this.controller?.toggleTaskPanel(...args);
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
  --claude-shadow-xl: 0 20px 25px rgba(0,0,0,0.08), 0 8px 10px rgba(0,0,0,0.04);
  --claude-radius-sm: 8px;--claude-radius-md: 12px;--claude-radius: 16px;--claude-radius-xl: 20px;--claude-radius-2xl: 24px;
  --claude-radius-full: 9999px;--claude-radius-lg: 16px;--claude-spacing: 0.25rem;
  --claude-font-display: Newsreader, Georgia, ui-serif, serif;--claude-font-sans: Poppins, ui-sans-serif, system-ui, sans-serif;
  --claude-font-serif: Lora, Georgia, ui-serif, serif;--claude-font-mono: Geist Mono, ui-monospace, monospace;
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



.bg-background{background-color:var(--claude-background)}.text-foreground{color:var(--claude-foreground)}
.bg-card{background-color:var(--claude-card)}.text-card-foreground{color:var(--claude-card-foreground)}
.bg-popover{background-color:var(--claude-popover)}.text-popover-foreground{color:var(--claude-popover-foreground)}
.bg-primary{background-color:var(--claude-primary)}.text-primary-foreground{color:var(--claude-primary-foreground)}
.bg-secondary{background-color:var(--claude-secondary)}.text-secondary-foreground{color:var(--claude-secondary-foreground)}
.bg-muted{background-color:var(--claude-muted)}.text-muted-foreground{color:var(--claude-muted-foreground)}
.bg-accent{background-color:var(--claude-accent)}.text-accent-foreground{color:var(--claude-accent-foreground)}
.bg-destructive{background-color:var(--claude-destructive)}.text-destructive-foreground{color:var(--claude-destructive-foreground)}
.border-border{border-color:var(--claude-border)}.ring-ring{--tw-ring-color:var(--claude-ring)}

</style>
