import { createApp } from 'vue';
import {
  Check,
  ChevronRight,
  ContactRound,
  createIcons,
  Eye,
  ListTodo,
  Lock,
  Mail,
  Pencil,
  Pause,
  Plus,
  RotateCcw,
  Search,
  ShieldCheck,
  Trash2,
  User,
  X,
} from 'lucide';
import App from './App.vue';
import router from './router';
import './assets/styles/index.css';
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
      Eye,
      ListTodo,
      Lock,
      Mail,
      Pencil,
      Pause,
      Plus,
      RotateCcw,
      Search,
      ShieldCheck,
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
app.use(router);
app.mount('#app');
