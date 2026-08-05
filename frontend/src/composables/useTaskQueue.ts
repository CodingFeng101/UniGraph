import { storeToRefs } from 'pinia';
import { useTaskStore } from '@/stores/task';

export function useTaskQueue() {
  const store = useTaskStore();
  return {
    store,
    ...storeToRefs(store),
  };
}
