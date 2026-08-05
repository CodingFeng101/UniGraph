import { defineStore } from 'pinia';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

function readProfile() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) as string | null,
    profile: readProfile() as Record<string, any> | null,
    hydrated: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    setToken(token: string | null) {
      this.token = token || null;
      if (this.token) localStorage.setItem(TOKEN_KEY, this.token);
      else localStorage.removeItem(TOKEN_KEY);
    },
    setProfile(incoming: Record<string, any> | null) {
      if (!incoming) {
        this.profile = null;
        localStorage.removeItem(USER_KEY);
        return;
      }
      const cached = this.profile || {};
      const sameUser = Boolean(
        (cached.uuid && incoming.uuid && cached.uuid === incoming.uuid)
        || (cached.user_uuid && incoming.user_uuid && cached.user_uuid === incoming.user_uuid)
        || (cached.id && incoming.id && cached.id === incoming.id)
        || (cached.username && incoming.username && cached.username === incoming.username)
      );
      this.profile = {
        ...cached,
        ...incoming,
        avatar: incoming.avatar || (sameUser ? cached.avatar : null),
      };
      localStorage.setItem(USER_KEY, JSON.stringify(this.profile));
    },
    markHydrated() {
      this.hydrated = true;
    },
    syncFromStorage() {
      this.token = localStorage.getItem(TOKEN_KEY);
      this.profile = readProfile();
      this.hydrated = true;
    },
    clear() {
      this.setToken(null);
      this.setProfile(null);
      this.hydrated = false;
    },
  },
});
