<template>
<Teleport to="body">
  <div
    v-if="showFab"
    id="task-fab-wrapper"
    class="task-fab"
    :class="{ 'task-fab--tucked': !panelOpen && !hovered && !dragging }"
    :style="fabStyle"
    @pointerdown="startDrag"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
  >
    <button type="button" class="task-orb-button" aria-label="后台任务" @click.stop="togglePanel">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 11 12 14 22 4" />
        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
      </svg>
    </button>
    <span data-task-fab-count class="task-fab-count">0</span>
  </div>

  <div ref="panel" v-show="panelOpen" id="task-panel" class="task-panel" :style="panelStyle">
    <section class="task-panel-surface">
      <header class="task-panel-header" @pointerdown="startDrag">
        <h2>后台任务</h2>
        <span data-task-running-count class="task-running-count">0 进行中</span>
      </header>
      <div data-task-list class="task-list">
        <div class="task-empty">暂无后台任务</div>
      </div>
    </section>
  </div>
</Teleport>
</template>

<script>
import { gsap } from 'gsap';

export default {
  name: 'TaskCenter',
  props: {
    showFab: { type: Boolean, default: true },
  },
  data() {
    return {
      panelOpen: false,
      hovered: false,
      dragging: false,
      moved: false,
      position: { x: 0, y: 0 },
      dragOffset: { x: 0, y: 0 },
    };
  },
  computed: {
    fabStyle() {
      let x = this.position.x;
      if (this.panelOpen || this.hovered || this.dragging) {
        x = x < 0 ? 10 : Math.min(x, window.innerWidth - 62);
      }
      return {
        left: `${x}px`,
        top: `${this.position.y}px`,
        cursor: this.dragging ? 'grabbing' : 'grab',
      };
    },
    panelStyle() {
      const width = Math.min(340, window.innerWidth - 24);
      const height = Math.min(580, window.innerHeight - 24);
      const dockLeft = this.position.x < window.innerWidth / 2;
      const orbLeft = dockLeft ? 10 : window.innerWidth - 62;
      const left = dockLeft
        ? Math.min(window.innerWidth - width - 12, orbLeft + 58)
        : Math.max(12, orbLeft - width - 8);
      const style = { width: `${width}px`, height: `${height}px`, left: `${left}px` };
      if (this.position.y > window.innerHeight / 2) {
        return {
          ...style,
          top: 'auto',
          bottom: `${Math.max(12, window.innerHeight - this.position.y - 52)}px`,
        };
      }
      return { ...style, top: `${Math.max(12, this.position.y)}px`, bottom: 'auto' };
    },
  },
  mounted() {
    const saved = JSON.parse(localStorage.getItem('unigraph-task-fab-position') || 'null');
    this.position = saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)
      ? this.clampPosition(saved.x, saved.y)
      : this.clampPosition(window.innerWidth - 40, window.innerHeight - 76);
    window.addEventListener('resize', this.handleResize);
    document.addEventListener('pointerdown', this.handleOutsidePointer);
    this.$nextTick(() => window.TaskManager?.render());
  },
  beforeUnmount() {
    gsap.killTweensOf([this.$refs.panel, this.$refs.panel?.querySelector('.task-panel-surface')].filter(Boolean));
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('pointerdown', this.handleOutsidePointer);
    window.removeEventListener('pointermove', this.drag);
    window.removeEventListener('pointerup', this.stopDrag);
  },
  methods: {
    togglePanel() {
      if (this.moved) {
        this.moved = false;
        return;
      }
      if (this.panelOpen) {
        this.closePanel();
        return;
      }
      this.panelOpen = true;
      this.$nextTick(() => {
        window.TaskManager?.render();
        const surface = this.$refs.panel?.querySelector('.task-panel-surface');
        if (!surface || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        gsap.fromTo(surface, { autoAlpha: 0, x: this.position.x < window.innerWidth / 2 ? -10 : 10, scale: 0.985 }, {
          autoAlpha: 1,
          x: 0,
          scale: 1,
          duration: 0.26,
          ease: 'power2.out',
          overwrite: 'auto',
          onComplete: () => gsap.set(surface, { clearProps: 'opacity,visibility,transform' }),
        });
      });
    },
    closePanel() {
      const surface = this.$refs.panel?.querySelector('.task-panel-surface');
      if (!surface || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        this.panelOpen = false;
        return;
      }
      gsap.to(surface, {
        autoAlpha: 0,
        x: this.position.x < window.innerWidth / 2 ? -8 : 8,
        scale: 0.988,
        duration: 0.16,
        ease: 'power1.in',
        overwrite: 'auto',
        onComplete: () => {
          this.panelOpen = false;
          gsap.set(surface, { clearProps: 'opacity,visibility,transform' });
        },
      });
    },
    clampPosition(x, y) {
      return {
        x: Math.max(-12, Math.min(x, window.innerWidth - 40)),
        y: Math.max(12, Math.min(y, window.innerHeight - 60)),
      };
    },
    startDrag(event) {
      if (event.button !== 0) return;
      this.dragging = true;
      this.moved = false;
      this.dragOffset = {
        x: event.clientX - this.position.x,
        y: event.clientY - this.position.y,
      };
      window.addEventListener('pointermove', this.drag);
      window.addEventListener('pointerup', this.stopDrag, { once: true });
    },
    drag(event) {
      this.moved = true;
      this.position = this.clampPosition(
        event.clientX - this.dragOffset.x,
        event.clientY - this.dragOffset.y,
      );
    },
    stopDrag() {
      this.dragging = false;
      window.removeEventListener('pointermove', this.drag);
      const dockLeft = this.position.x + 24 < window.innerWidth / 2;
      this.position.x = dockLeft ? -12 : window.innerWidth - 40;
      localStorage.setItem('unigraph-task-fab-position', JSON.stringify(this.position));
    },
    handleResize() {
      this.position = this.clampPosition(this.position.x, this.position.y);
    },
    handleOutsidePointer(event) {
      if (!this.panelOpen) return;
      if (event.target.closest('#task-panel') || event.target.closest('#task-fab-wrapper')) return;
      this.closePanel();
    },
  },
};
</script>

<style scoped>
.task-fab,
.task-panel {
  position: fixed;
  z-index: 2147483000;
}

.task-fab {
  opacity: .96;
  transition: transform .22s cubic-bezier(.16, 1, .3, 1), opacity .18s ease;
  will-change: transform;
}

.task-fab--tucked {
  opacity: .58;
  transform: scale(.94);
}

.task-fab:hover {
  opacity: 1;
  transform: scale(1);
}

.task-orb-button {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: var(--claude-primary-foreground);
  background: var(--task-orb-color, #a7cfb2);
  border: 2px solid var(--claude-card);
  box-shadow: 0 10px 24px rgba(78, 55, 42, .18), 0 0 0 1px var(--claude-border);
  cursor: pointer;
  transition: transform .18s cubic-bezier(.16, 1, .3, 1), background-color .35s ease;
}

.task-orb-button::after {
  content: '';
  position: absolute;
  inset: -7px;
  border: 2px solid var(--task-orb-color, #a7cfb2);
  border-radius: inherit;
  pointer-events: none;
  animation: task-orb-breathe var(--task-orb-duration, 3.4s) cubic-bezier(.16, 1, .3, 1) infinite;
}

.task-orb-button svg { position: relative; z-index: 1; }

@keyframes task-orb-breathe {
  0%, 100% { opacity: .42; transform: scale(.84); }
  70% { opacity: 0; transform: scale(1.18); }
}

.task-orb-button:hover { transform: scale(1.05); }
.task-orb-button:active { transform: scale(.96); }

.task-fab-count {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  display: none;
  align-items: center;
  justify-content: center;
  color: var(--claude-destructive-foreground);
  background: var(--task-orb-color, #a7cfb2);
  font-size: 10px;
  font-weight: 700;
}

.task-panel-surface {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  color: var(--claude-foreground);
  background: var(--claude-card);
  border: 1px solid color-mix(in srgb, var(--claude-border) 82%, transparent);
  box-shadow: 0 16px 42px rgba(74, 55, 42, .14), inset 0 1px 0 rgba(255, 255, 255, .58);
}

.task-panel-header {
  min-height: 46px;
  padding: 10px 14px 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: move;
  user-select: none;
}

.task-panel-header h2 {
  margin: 0;
  font-size: 13px;
  line-height: 1;
  font-weight: 650;
}

.task-running-count {
  padding: 4px 9px;
  border-radius: 999px;
  color: var(--claude-brand-500);
  background: color-mix(in srgb, var(--claude-brand-500) 9%, var(--claude-card));
  font-size: 10px;
  line-height: 1;
  font-weight: 500;
}

.task-list {
  min-height: 0;
  flex: 1;
  padding: 0 10px 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  scrollbar-width: thin;
  overscroll-behavior: contain;
}

.task-empty {
  padding: 40px 16px;
  text-align: center;
  color: var(--claude-muted-foreground);
  font-size: 13px;
}

:deep(.task-card) {
  overflow: hidden;
  border-radius: 12px;
  background: var(--claude-background);
  border: 1px solid transparent;
}

:deep(.task-card__summary) {
  width: 100%;
  min-height: 42px;
  padding: 10px 10px 7px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  column-gap: 7px;
  color: var(--claude-foreground);
  background: transparent;
}

:deep(.task-card__toggle) {
  min-width: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 13px 7px minmax(0, 1fr);
  align-items: center;
  column-gap: 6px;
  color: var(--claude-foreground);
  background: transparent;
  border: 0;
  text-align: left;
  cursor: pointer;
}

:deep(.task-card__toggle:active) { transform: translateY(1px); }

:deep(.task-chevron) {
  width: 13px;
  height: 13px;
  transition: transform .2s cubic-bezier(.16, 1, .3, 1);
}

:deep(.task-status-check) {
  width: 12px;
  height: 12px;
  stroke-width: 2.4;
}

:deep(.task-status-dot) {
  width: 7px;
  height: 7px;
  border-radius: 999px;
}

:deep(.task-card__title) {
  min-width: 0;
  overflow: hidden;
  margin: 0;
  color: var(--claude-foreground);
  font-size: 11px;
  line-height: 1.25;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.task-card__state) {
  min-width: 30px;
  text-align: right;
  font-size: 10px;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

:deep(.task-inline-actions) {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

:deep(.task-inline-action) {
  width: 22px;
  height: 22px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 5px;
  color: var(--claude-muted-foreground);
  background: color-mix(in srgb, var(--claude-border) 36%, transparent);
  cursor: pointer;
  transition: color .16s ease, background-color .16s ease, transform .16s ease;
}

:deep(.task-inline-action:hover) {
  color: var(--claude-foreground);
  background: color-mix(in srgb, var(--claude-border) 62%, transparent);
}

:deep(.task-inline-action:active) { transform: scale(.94); }
:deep(.task-inline-action:disabled) { opacity: .38; cursor: not-allowed; }
:deep(.task-delete-action) { color: var(--claude-destructive); }
:deep(.task-inline-action svg) { width: 12px; height: 12px; stroke-width: 1.8; }

:deep(.task-progress) {
  height: 3px;
  margin: 0 10px 9px 36px;
  overflow: hidden;
  border-radius: 999px;
  background: color-mix(in srgb, var(--claude-border) 82%, transparent);
}

:deep(.task-progress__value) {
  height: 100%;
  border-radius: inherit;
  transition: width .28s cubic-bezier(.16, 1, .3, 1);
}

:deep(.task-detail) {
  margin: 0 11px 9px 27px;
  padding: 10px 0 1px;
  border-top: 1px dashed color-mix(in srgb, var(--claude-border) 82%, transparent);
  background: transparent;
}

:deep(.task-detail.hidden) { display: none; }

:deep(.task-timeline) {
  max-height: 250px;
  padding: 1px 6px 1px 0;
  overflow-y: auto;
  scrollbar-width: thin;
  overscroll-behavior: contain;
}

:deep(.task-step) {
  position: relative;
  min-height: 40px;
  padding: 0 0 9px 18px;
  opacity: .74;
  transition: opacity 180ms ease;
}

:deep(.task-step.is-latest) {
  opacity: 1;
}

:deep(.task-step.is-new) {
  animation: task-log-enter 240ms ease-out both;
}

:deep(.task-card__start-time) {
  margin-left: 6px;
  color: var(--claude-muted-foreground);
  font-family: var(--claude-font-mono);
  font-size: 9px;
  font-weight: 400;
  letter-spacing: .02em;
}

:deep(.task-step:not(:last-child)::after) {
  content: '';
  position: absolute;
  left: 4px;
  top: 11px;
  bottom: -2px;
  width: 1px;
  background: color-mix(in srgb, var(--claude-border) 92%, transparent);
}

:deep(.task-step__dot) {
  position: absolute;
  left: 0;
  top: 3px;
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--step-color);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--step-color) 22%, var(--claude-card));
}

:deep(.task-step.is-running .task-step__dot::after) {
  content: '';
  position: absolute;
  inset: -1px;
  border: 1px solid var(--step-color);
  border-radius: inherit;
  pointer-events: none;
  animation: task-step-ripple 1.8s cubic-bezier(.16, 1, .3, 1) infinite;
}

:deep(.task-step.is-running .task-step__label) {
  animation: task-step-breathe 1.8s ease-in-out infinite;
}

:deep(.task-step__head) {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

:deep(.task-step__label) {
  overflow: hidden;
  color: var(--claude-foreground);
  font-size: 10px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.task-step__time) {
  flex: none;
  color: var(--claude-muted-foreground);
  font-family: var(--claude-font-mono);
  font-size: 9px;
  letter-spacing: .04em;
}

:deep(.task-step__description) {
  margin: 3px 0 0;
  color: var(--claude-muted-foreground);
  font-size: 10px;
  line-height: 1.35;
}

@keyframes task-log-enter {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes task-step-ripple {
  0% { opacity: .75; transform: scale(.7); }
  75%, 100% { opacity: 0; transform: scale(2.5); }
}

@keyframes task-step-breathe {
  0%, 100% { opacity: .72; }
  50% { opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  :deep(.task-step.is-running .task-step__dot::after),
  :deep(.task-step.is-running .task-step__label),
  :deep(.task-step.is-new) {
    animation: none;
  }
}

@media (max-width: 560px) {
  .task-panel { left: 12px !important; right: 12px; width: auto !important; }
}
</style>
