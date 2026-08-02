const KEYS = {
  graphExpansionDepth: 'unigraph-graph-expansion-depth',
  taskSound: 'unigraph-task-sound-enabled',
  desktopNotifications: 'unigraph-desktop-notifications-enabled',
};

function userKey(key) {
  const userUuid = Auth.getUserInfo()?.uuid || 'anonymous';
  return `${key}:${userUuid}`;
}

function readValue(key) {
  return localStorage.getItem(userKey(key)) ?? localStorage.getItem(key);
}

function readBoolean(key, fallback = false) {
  const value = readValue(key);
  return value == null ? fallback : value === 'true';
}

function readDepth(key, fallback = 1) {
  const value = Number(readValue(key) ?? fallback);
  return Math.max(1, Math.min(5, Number.isFinite(value) ? Math.round(value) : fallback));
}

export function getGraphExpansionDepth() {
  return readDepth(KEYS.graphExpansionDepth);
}

export function getTaskNotificationPreferences() {
  return {
    sound: readBoolean(KEYS.taskSound),
    desktop: readBoolean(KEYS.desktopNotifications),
  };
}

export function savePreferences(preferences) {
  localStorage.setItem(userKey(KEYS.graphExpansionDepth), String(preferences.graphExpansionDepth));
  localStorage.setItem(userKey(KEYS.taskSound), String(Boolean(preferences.taskSound)));
  localStorage.setItem(userKey(KEYS.desktopNotifications), String(Boolean(preferences.desktopNotifications)));
  window.dispatchEvent(new CustomEvent('unigraph:preferences-changed'));
}
import { Auth } from '@/api/runtime/auth';
