import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/user';

export function useCurrentUser() {
  const store = useUserStore();
  return {
    store,
    ...storeToRefs(store),
  };
}
