import { createApp } from 'vue';
import {
  Check,
  ChevronRight,
  CircleAlert,
  CircleCheck,
  Clock3,
  ContactRound,
  Database,
  Eye,
  FileSearch,
  FileText,
  Layers3,
  ListTodo,
  LoaderCircle,
  Lock,
  Mail,
  MessageSquareText,
  Network,
  Pencil,
  Pause,
  Plus,
  RotateCcw,
  Search,
  ShieldCheck,
  Sparkles,
  Trash2,
  User,
  X,
} from 'lucide';
import App from './App.vue';
import router from './router';
import './assets/styles/index.css';
import './assets/styles/chat-citations.css';
import './api';
import './services/task-manager';
import './services/sidebar-chat';
import './services/i18n';
import { t } from './services/i18n';
import './graph/renderer';
import { installFeedback } from './utils/feedback';
import { pinia } from './stores';
import { useUserStore } from './stores/user';
import { i18n } from './i18n';

installFeedback();

const userStore = useUserStore(pinia);
window.addEventListener('storage', (event) => {
  if (event.key === 'user' || event.key === 'access_token') userStore.syncFromStorage();
});

const lucideIcons = {
  ContactRound,
  Check,
  ChevronRight,
  CircleAlert,
  CircleCheck,
  Clock3,
  Eye,
  Database,
  FileSearch,
  FileText,
  Layers3,
  ListTodo,
  LoaderCircle,
  Lock,
  Mail,
  MessageSquareText,
  Network,
  Pencil,
  Pause,
  Plus,
  RotateCcw,
  Search,
  ShieldCheck,
  Sparkles,
  Trash2,
  User,
  X,
};

const iconName = (value: string) => value
  .split('-')
  .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
  .join('');

window.lucide = {
  createIcons: () => {
    document.querySelectorAll<HTMLElement>('i[data-lucide]').forEach((element) => {
      const name = element.dataset.lucide || '';
      const definition = lucideIcons[iconName(name) as keyof typeof lucideIcons];
      if (!definition) return;

      element.style.display = 'inline-flex';
      element.style.alignItems = 'center';
      element.style.justifyContent = 'center';
      element.style.flexShrink = '0';

      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 24 24');
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', '100%');
      svg.setAttribute('fill', 'none');
      svg.setAttribute('stroke', 'currentColor');
      svg.setAttribute('stroke-width', '2');
      svg.setAttribute('stroke-linecap', 'round');
      svg.setAttribute('stroke-linejoin', 'round');
      svg.setAttribute('aria-hidden', 'true');
      svg.style.display = 'block';
      svg.classList.add('lucide', `lucide-${name}`);
      definition.forEach(([tag, attributes]) => {
        const child = document.createElementNS('http://www.w3.org/2000/svg', tag);
        Object.entries(attributes).forEach(([key, value]) => child.setAttribute(key, String(value)));
        svg.appendChild(child);
      });
      element.replaceChildren(svg);
    });
  },
};

window.getUniGraphSearchParams = () => {
  const params = new URLSearchParams(window.location.search);
  const match = window.location.pathname.match(/^\/unigraph\/unigraphs\/([^/]+)/);
  if (match && !params.has('uuid')) params.set('uuid', decodeURIComponent(match[1]));
  return params;
};

const app = createApp(App);
let lastGlobalErrorAt = 0;
const reportGlobalError = (error: unknown) => {
  console.error('Unhandled application error:', error);
  const now = Date.now();
  if (now - lastGlobalErrorAt > 2000) {
    window.showToast?.(t('errors.page'));
    lastGlobalErrorAt = now;
  }
};
app.config.errorHandler = (error) => reportGlobalError(error);
window.addEventListener('error', (event) => reportGlobalError(event.error || event.message));
window.addEventListener('unhandledrejection', (event) => reportGlobalError(event.reason));
app.use(pinia);
app.use(i18n);
app.use(router);
app.mount('#app');
