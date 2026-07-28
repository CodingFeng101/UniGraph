import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { isLogin } from '@/utils/auth';

async function loadGraphRuntime() {
  const { ensureGraphRuntime } = await import('@/graph/runtime');
  ensureGraphRuntime();
  return true;
}
const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/design/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/share/:publicId',
    name: 'shared-chat',
    component: () => import('@/views/design/SharedChatView.vue'),
    meta: { public: true },
  },
  {
    path: '/workspace',
    name: 'workspace',
    component: () => import('@/views/design/KnowledgeBaseListView.vue'),
  },
  {
    path: '/unigraphs/:uuid/info',
    name: 'knowledge-base-info',
    component: () => import('@/views/design/KnowledgeBaseInfoView.vue'),
  },
  {
    path: '/unigraphs/:uuid/structure',
    name: 'graph-design',
    component: () => import('@/views/design/GraphDesignView.vue'),
    beforeEnter: loadGraphRuntime,
  },
  {
    path: '/unigraphs/:uuid/graph',
    name: 'graph-build',
    component: () => import('@/views/design/GraphBuildView.vue'),
    beforeEnter: loadGraphRuntime,
  },
  {
    path: '/unigraphs/:uuid/qa',
    name: 'graph-application',
    component: () => import('@/views/design/GraphApplicationView.vue'),
  },
  { path: '/docs', name: 'docs', component: () => import('@/views/design/DocsView.vue') },
  { path: '/tutorial', name: 'tutorials', component: () => import('@/views/design/TutorialsView.vue') },
  { path: '/usercenter', name: 'profile', component: () => import('@/views/design/ProfileView.vue') },
  { path: '/settings', name: 'settings', component: () => import('@/views/design/SettingsView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/workspace' },
];

const router = createRouter({
  history: createWebHistory('/unigraph'),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.public) {
    if (to.name === 'login' && isLogin()) return { name: 'workspace' };
    return true;
  }
  if (!isLogin()) return { name: 'login', query: { redirect: to.fullPath } };
  return true;
});

export default router;
