const KEYS = {
  graphExpansionDepth: 'unigraph-graph-expansion-depth',
  taskSound: 'unigraph-task-sound-enabled',
  desktopNotifications: 'unigraph-desktop-notifications-enabled',
};

function readBoolean(key, fallback = false) {
  const value = localStorage.getItem(key);
  return value == null ? fallback : value === 'true';
}

export function getGraphExpansionDepth() {
  const value = Number(localStorage.getItem(KEYS.graphExpansionDepth) || 1);
  return Math.max(1, Math.min(5, Number.isFinite(value) ? Math.round(value) : 1));
}

export function getTaskNotificationPreferences() {
  return {
    sound: readBoolean(KEYS.taskSound),
    desktop: readBoolean(KEYS.desktopNotifications),
  };
}

export function savePreferences(preferences) {
  localStorage.setItem(KEYS.graphExpansionDepth, String(preferences.graphExpansionDepth));
  localStorage.setItem(KEYS.taskSound, String(Boolean(preferences.taskSound)));
  localStorage.setItem(KEYS.desktopNotifications, String(Boolean(preferences.desktopNotifications)));
  window.dispatchEvent(new CustomEvent('unigraph:preferences-changed'));
}

