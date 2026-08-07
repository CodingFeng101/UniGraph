export default {
  common: {
    create: 'Create', update: 'Update', delete: 'Delete', edit: 'Edit', save: 'Save', cancel: 'Cancel',
    close: 'Close', copy: 'Copy', copied: 'Copied', send: 'Send', search: 'Search', refresh: 'Refresh',
    loading: 'Loading', retry: 'Retry', success: 'Success', failed: 'Failed', inProgress: 'In progress', completed: 'Completed',
  },
  nav: {
    knowledgeBases: 'Knowledge bases', info: 'Info', design: 'Design', build: 'Build', newChat: 'New chat',
    profile: 'Profile', docs: 'Technical docs', tutorials: 'Tutorials', tasks: 'Background tasks', settings: 'Settings', logout: 'Log out',
  },
  auth: {
    login: 'Log in', register: 'Sign up', username: 'Username', email: 'Email', password: 'Password',
    sessionExpired: 'Your session has expired. Please log in again.',
  },
  chat: {
    empty: 'How can I help?', historyEmpty: 'No conversation history', newConversation: 'New chat',
    selectIndex: 'Select knowledge graph index', noIndex: 'No index available', regenerate: 'Regenerate', share: 'Share conversation',
  },
  task: {
    title: 'Background tasks', empty: 'No background tasks', pending: 'Pending', running: 'Running', retrying: 'Retrying',
    succeeded: 'Completed', failed: 'Failed', revoked: 'Revoked', runningCount: '{count} running',
  },
  profile: {
    title: 'Profile', changeAvatar: 'Change avatar', editProfile: 'Edit profile', modelConfig: 'Model configuration',
    profileUpdated: 'Profile updated. Use the new username next time you log in.',
  },
  settings: {
    language: 'Language', theme: 'Theme', light: 'Light', dark: 'Dark', system: 'System',
    chinese: 'Chinese', english: 'English', user: 'User', administrator: 'Administrator', emailUnset: 'Email not set',
  },
  errors: {
    page: 'The page encountered an error. Please try again or refresh if it persists.', network: 'Network request failed', request: 'Request failed',
    load: 'Load failed', operation: 'Operation failed',
  },
} as const;
