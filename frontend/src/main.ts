import { createApp } from 'vue';
import {
  Check,
  ChevronRight,
  CircleAlert,
  CircleCheck,
  Clock3,
  ContactRound,
  createIcons,
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
import './graph/renderer';
import { installFeedback } from './utils/feedback';

installFeedback();

window.lucide = {
  createIcons: () => createIcons({
    icons: {
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
    },
  }),
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
    window.showToast?.('页面发生异常，请重试；若问题持续请刷新页面');
    lastGlobalErrorAt = now;
  }
};
app.config.errorHandler = (error) => reportGlobalError(error);
window.addEventListener('error', (event) => reportGlobalError(event.error || event.message));
window.addEventListener('unhandledrejection', (event) => reportGlobalError(event.reason));
app.use(router);
app.mount('#app');
