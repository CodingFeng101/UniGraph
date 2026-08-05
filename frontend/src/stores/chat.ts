import { defineStore } from 'pinia';

export const useChatStore = defineStore('chat', {
  state: () => ({
    items: [] as any[],
    currentChatUuid: null as string | null,
    currentKnowledgeBaseUuid: null as string | null,
    selectedIndexUuid: null as string | null,
    availableIndexes: [] as any[],
    pendingAttachments: [] as any[],
    sortAscending: false,
    loading: false,
  }),
  actions: {
    replaceItems(items: any[]) {
      this.items = Array.isArray(items) ? items : [];
    },
    patchItem(uuid: string, patch: Record<string, any>) {
      const item = this.items.find((entry) => entry.uuid === uuid);
      if (item) Object.assign(item, patch);
    },
    removeItem(uuid: string) {
      this.items = this.items.filter((item) => item.uuid !== uuid);
      if (this.currentChatUuid === uuid) this.currentChatUuid = null;
    },
    reset() {
      this.$reset();
    },
  },
});
