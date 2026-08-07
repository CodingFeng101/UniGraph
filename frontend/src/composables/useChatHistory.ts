import { storeToRefs } from 'pinia';
import { useChatStore } from '@/stores/chat';

export function useChatHistory() {
  const store = useChatStore();
  return {
    store,
    ...storeToRefs(store),
  };
}
