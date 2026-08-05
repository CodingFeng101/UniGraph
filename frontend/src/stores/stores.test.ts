import { beforeEach, describe, expect, it } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useChatStore } from './chat';
import { useTaskStore } from './task';
import { useUserStore } from './user';

describe('application stores', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
  });

  it('keeps the current avatar when a same-user response omits it', () => {
    const store = useUserStore();
    store.setProfile({ uuid: 'user-1', username: 'alice', avatar: '/avatar/a.png' });
    store.setProfile({ uuid: 'user-1', username: 'alice-new', avatar: null });

    expect(store.profile?.avatar).toBe('/avatar/a.png');
    expect(store.profile?.username).toBe('alice-new');
    expect(JSON.parse(localStorage.getItem('user') || '{}').avatar).toBe('/avatar/a.png');
  });

  it('does not leak an avatar across users', () => {
    const store = useUserStore();
    store.setProfile({ uuid: 'user-1', username: 'alice', avatar: '/avatar/a.png' });
    store.setProfile({ uuid: 'user-2', username: 'bob' });
    expect(store.profile?.avatar).toBeNull();
  });

  it('keeps chat selection and history in one store', () => {
    const store = useChatStore();
    store.replaceItems([{ uuid: 'chat-1' }, { uuid: 'chat-2' }]);
    store.currentChatUuid = 'chat-1';
    store.removeItem('chat-1');
    expect(store.items.map((item) => item.uuid)).toEqual(['chat-2']);
    expect(store.currentChatUuid).toBeNull();
  });

  it('hydrates task state from the user-specific storage key', () => {
    localStorage.setItem('tasks:user-1', JSON.stringify([{ uid: 'task-1', kwargs: { token: 'safe' } }]));
    const store = useTaskStore();
    store.hydrate('tasks:user-1', (task) => task);
    expect(store.tasks[0].uid).toBe('task-1');
    expect(store.storageKey).toBe('tasks:user-1');
  });
});
