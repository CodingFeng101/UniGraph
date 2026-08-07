import { defineStore } from 'pinia';

export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [] as any[],
    storageKey: '' as string,
  }),
  actions: {
    hydrate(storageKey: string, sanitize: (task: any) => any) {
      this.storageKey = storageKey;
      try {
        const value = JSON.parse(localStorage.getItem(storageKey) || '[]');
        this.tasks = Array.isArray(value) ? value.map(sanitize) : [];
      } catch {
        this.tasks = [];
      }
    },
    persist(sanitize: (task: any) => any) {
      if (!this.storageKey) return;
      localStorage.setItem(this.storageKey, JSON.stringify(this.tasks.map(sanitize)));
    },
    reset() {
      this.tasks = [];
      this.storageKey = '';
    },
  },
});
