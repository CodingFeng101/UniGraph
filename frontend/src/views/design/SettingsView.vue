<template>
  <div class="min-h-[100dvh]" style="background:var(--claude-background);">
    <AppSidebar active="settings" />
    <main id="app-main" class="min-h-[100dvh] transition-all duration-300" style="margin-left:260px;">
      <div class="max-w-[780px] mx-auto px-8 py-12">
        <h1 class="text-[28px] leading-tight" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">设置</h1>
        <p class="mt-2 text-sm" style="color:var(--claude-muted-foreground);">调整图谱交互和任务通知偏好</p>

        <section class="settings-section mt-10">
          <div class="setting-row">
            <span>
              <strong>双击展开跳数</strong>
              <small>控制双击实体时展开周围关系的范围，支持 1–5 跳。</small>
            </span>
            <div ref="depthMenu" class="depth-picker">
              <button type="button" class="depth-trigger" :aria-expanded="depthMenuOpen" @click="depthMenuOpen = !depthMenuOpen">
                <span>{{ graphExpansionDepth }} 跳</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
              </button>
              <div v-show="depthMenuOpen" class="depth-menu">
                <button v-for="depth in 5" :key="depth" type="button" :class="{ active: graphExpansionDepth === depth }" @click="selectDepth(depth)">
                  <span>{{ depth }} 跳</span>
                  <svg v-if="graphExpansionDepth === depth" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><polyline points="20 6 9 17 4 12"/></svg>
                </button>
              </div>
            </div>
          </div>
        </section>

        <section class="settings-section mt-8">
          <div class="settings-heading">
            <h2>任务通知</h2>
            <p>后台任务完成后提醒你，不影响任务执行。</p>
          </div>
          <label class="setting-row">
            <span>
              <strong>完成提示音</strong>
              <small>任务成功完成时播放一声简短提示。</small>
            </span>
            <input v-model="taskSound" type="checkbox" class="setting-switch" @change="persist" />
          </label>
          <label class="setting-row">
            <span>
              <strong>桌面通知</strong>
              <small>{{ notificationHint }}</small>
            </span>
            <input v-model="desktopNotifications" type="checkbox" class="setting-switch" @change="toggleDesktopNotifications" />
          </label>
        </section>
      </div>
    </main>
    <TaskCenter />
  </div>
</template>

<script>
import AppSidebar from '@/components/layout/AppSidebar.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';
import {
  getGraphExpansionDepth,
  getTaskNotificationPreferences,
  savePreferences,
} from '@/services/preferences';

export default {
  name: 'SettingsView',
  components: { AppSidebar, TaskCenter },
  data() {
    const notifications = getTaskNotificationPreferences();
    return {
      graphExpansionDepth: getGraphExpansionDepth(),
      depthMenuOpen: false,
      taskSound: notifications.sound,
      desktopNotifications: notifications.desktop,
      notificationHint: '任务完成时发送系统桌面通知。',
    };
  },
  mounted() {
    document.title = '设置';
    document.addEventListener('pointerdown', this.closeDepthMenu);
  },
  beforeUnmount() {
    document.removeEventListener('pointerdown', this.closeDepthMenu);
  },
  methods: {
    persist() {
      savePreferences(this);
    },
    async toggleDesktopNotifications() {
      if (!this.desktopNotifications) {
        this.persist();
        return;
      }
      if (!('Notification' in window)) {
        this.desktopNotifications = false;
        this.notificationHint = '当前浏览器不支持桌面通知。';
        this.persist();
        return;
      }
      const permission = Notification.permission === 'granted'
        ? 'granted'
        : await Notification.requestPermission();
      this.desktopNotifications = permission === 'granted';
      this.notificationHint = this.desktopNotifications
        ? '已授权，任务完成时会发送桌面通知。'
        : '通知权限未开启，可在浏览器站点设置中允许。';
      this.persist();
    },
    selectDepth(depth) {
      this.graphExpansionDepth = depth;
      this.depthMenuOpen = false;
      this.persist();
    },
    closeDepthMenu(event) {
      if (!this.$refs.depthMenu?.contains(event.target)) this.depthMenuOpen = false;
    },
  },
};
</script>

<style scoped>
.settings-section {
  padding: 0;
}

.settings-heading {
  padding: 0 2px 12px;
}

.settings-section h2 {
  margin: 0;
  color: var(--claude-foreground);
  font-size: 15px;
  font-weight: 650;
}

.settings-section p,
.setting-row small {
  color: var(--claude-muted-foreground);
  font-size: 12px;
  line-height: 1.55;
}

.settings-section p { margin: 5px 0 0; }

.setting-row {
  min-height: 68px;
  padding: 12px 2px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.setting-row + .setting-row { margin-top: 4px; }

.setting-row > span {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-row strong {
  color: var(--claude-foreground);
  font-size: 13px;
  font-weight: 550;
}

.depth-picker { position: relative; flex: none; }

.depth-trigger {
  width: 108px;
  height: 36px;
  padding: 0 11px 0 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--claude-border);
  border-radius: 11px;
  outline: none;
  color: var(--claude-foreground);
  background: var(--claude-card);
  font-size: 13px;
  cursor: pointer;
}

.depth-trigger:hover { background: var(--claude-secondary); }
.depth-trigger:active { transform: scale(.98); }

.depth-menu {
  position: absolute;
  z-index: 100;
  top: calc(100% + 6px);
  right: 0;
  width: 128px;
  padding: 5px;
  border: 1px solid var(--claude-border);
  border-radius: 13px;
  background: var(--claude-card);
  box-shadow: var(--claude-shadow-lg);
}

.depth-menu button {
  width: 100%;
  height: 34px;
  padding: 0 9px 0 11px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 0;
  border-radius: 9px;
  color: var(--claude-foreground);
  background: transparent;
  font-size: 13px;
  cursor: pointer;
}

.depth-menu button:hover,
.depth-menu button.active { background: var(--claude-secondary); }
.depth-menu button svg { color: var(--claude-brand-500); }

.setting-switch {
  width: 38px;
  height: 22px;
  flex: none;
  accent-color: var(--claude-brand-500);
  cursor: pointer;
}
</style>
