import { Auth } from '@/api/runtime/auth';
import { KgBaseAPI } from '@/api';

export const ChatSidebar = window.ChatSidebar = (() => {
  let items = [];
  let sortAscending = false;

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    })[char]);
  }

  function notify(message) {
    if (typeof window.showToast === 'function') window.showToast(message);
  }

  function hrefFor(item) {
    return `/unigraph/unigraphs/${encodeURIComponent(item.kg_base_uuid)}/qa?chat=${encodeURIComponent(item.uuid)}`;
  }

  function row(item) {
    const active = new URLSearchParams(location.search).get('chat') === item.uuid;
    return `
      <div class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]"${active ? ' style="background:var(--claude-accent);"' : ''}>
        <a href="${hrefFor(item)}" class="block" style="text-decoration:none;">
          <p class="text-[15px] leading-[22px] font-normal truncate pr-7" style="color:var(--claude-foreground);">${escapeHtml(item.name || '未命名对话')}</p>
        </a>
        <button type="button" onclick="event.stopPropagation();ChatSidebar.toggleMenu(this)" class="absolute right-2 top-1.5 flex w-6 h-6 items-center justify-center rounded-md claude-menu-item opacity-55 group-hover:opacity-100 transition-opacity" style="background:transparent;border:none;color:var(--claude-muted-foreground);font-size:18px;line-height:1;" aria-label="对话菜单">⋮</button>
        <div class="chat-context-menu hidden absolute right-2 top-8 z-50 min-w-28 rounded-xl p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
          <button type="button" onclick="ChatSidebar.rename('${item.uuid}')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-foreground);">重命名</button>
          <button type="button" onclick="ChatSidebar.favorite('${item.uuid}',${!item.is_favorite})" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-foreground);">${item.is_favorite ? '取消收藏' : '收藏'}</button>
          <button type="button" onclick="ChatSidebar.remove('${item.uuid}')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-destructive);">删除</button>
        </div>
      </div>`;
  }

  function render() {
    const container = document.querySelector('#app-sidebar .sidebar-content .space-y-0\\.5');
    if (!container) return;
    const sorted = items.slice().sort((a, b) => {
      const left = new Date(a.updated_time || a.created_time || 0);
      const right = new Date(b.updated_time || b.created_time || 0);
      return sortAscending ? left - right : right - left;
    });
    const starred = sorted.filter((item) => item.is_favorite);
    const recent = sorted.filter((item) => !item.is_favorite);
    const recentHeading = `<div class="flex items-center justify-between px-3 pt-4 pb-1 text-[13px] font-normal" style="color:var(--claude-muted-foreground);"><span>Recents</span><button type="button" onclick="ChatSidebar.toggleSort()" class="w-6 h-6 flex items-center justify-center rounded-md claude-menu-item cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);" aria-label="排序"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><line x1="7" y1="3" x2="7" y2="21"/><circle cx="7" cy="8" r="2"/><line x1="17" y1="3" x2="17" y2="21"/><circle cx="17" cy="16" r="2"/></svg></button></div>`;
    container.innerHTML = sorted.length
      ? `${starred.length ? `<div class="px-3 pt-1 pb-1 text-[13px] font-normal" style="color:var(--claude-muted-foreground);">Starred</div>${starred.map(row).join('')}` : ''}
         ${recentHeading}${recent.map(row).join('')}`
      : '<div class="px-3 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">暂无历史对话</div>';
    renderSearch(sorted);
  }

  function renderSearch(list) {
    const container = document.querySelector('#search-modal .max-h-\\[50vh\\]');
    if (!container) return;
    container.innerHTML = list.length
      ? `<div class="px-2 py-2">${list.map((item) => `<a href="${hrefFor(item)}" class="chat-search-item block px-3 py-2.5 rounded-lg claude-menu-item text-sm" style="color:var(--claude-foreground);">${escapeHtml(item.name || '未命名对话')}</a>`).join('')}</div>`
      : '<div class="px-4 py-8 text-center text-sm" style="color:var(--claude-muted-foreground);">暂无历史对话</div>';
  }

  function filterSearch(query) {
    const value = String(query || '').toLowerCase();
    document.querySelectorAll('#search-modal .chat-search-item').forEach((element) => {
      element.style.display = element.textContent.toLowerCase().includes(value) ? '' : 'none';
    });
  }

  async function hydrateUser() {
    const response = await KgBaseAPI.auth.getUserInfo();
    if (response.code !== 200 || !response.data) return;
    const user = response.data;
    const footer = document.querySelector('#app-sidebar > .px-3.py-2\\.5.relative.mt-auto');
    if (!footer) return;
    const name = user.nickname || user.username || '用户';
    const avatar = footer.querySelector('.w-8.h-8.rounded-full');
    const nameElement = footer.querySelector('p.text-sm');
    const roleElement = footer.querySelector('p.text-\\[10px\\]');
    const emailElement = document.querySelector('#user-dropdown > div:first-child p');
    if (avatar) avatar.textContent = name.slice(0, 2).toUpperCase();
    if (nameElement) nameElement.textContent = name;
    if (roleElement) roleElement.textContent = user.is_superuser ? '管理员' : '用户';
    if (emailElement) emailElement.textContent = user.email || '未设置邮箱';
  }

  async function load() {
    if (!Auth.isLogin()) return;
    try {
      const basesResponse = await KgBaseAPI.kgBase.getAll();
      if (basesResponse.code !== 200) throw new Error(basesResponse.msg || '加载知识库失败');
      const bases = Array.isArray(basesResponse.data) ? basesResponse.data : [];
      const newChatLink = document.getElementById('workspace-app-link');
      if (newChatLink && bases.length && !location.pathname.includes('/unigraphs/')) {
        const latestBase = bases.slice().sort((a, b) =>
          new Date(b.created_time || 0) - new Date(a.created_time || 0))[0];
        newChatLink.href = `/unigraph/unigraphs/${encodeURIComponent(latestBase.uuid)}/qa`;
      }
      const results = await Promise.all(bases.map(async (base) => {
        try {
          const response = await KgBaseAPI.chatLibrary.getAll(base.uuid);
          return response.code === 200 && Array.isArray(response.data)
            ? response.data.map((item) => ({ ...item, kg_base_uuid: base.uuid }))
            : [];
        } catch {
          return [];
        }
      }));
      items = results.flat();
      await hydrateUser();
      const searchInput = document.getElementById('search-input');
      if (searchInput) searchInput.oninput = () => filterSearch(searchInput.value);
      if (!/\/qa\/?$/.test(location.pathname)) render();
    } catch (error) {
      notify(error.message || '加载历史对话失败');
    }
  }

  function toggleMenu(button) {
    const menu = button?.nextElementSibling;
    const shouldOpen = menu?.classList.contains('hidden');
    document.querySelectorAll('.chat-context-menu').forEach((element) => element.classList.add('hidden'));
    if (shouldOpen) menu?.classList.remove('hidden');
  }

  function toggleSort() {
    sortAscending = !sortAscending;
    render();
  }

  async function rename(uuid) {
    const item = items.find((entry) => entry.uuid === uuid);
    if (!item) return;
    const name = window.prompt('请输入新的对话名称', item.name || '');
    if (!name || name === item.name) return;
    const detail = await KgBaseAPI.chatLibrary.getDetail(uuid);
    const response = await KgBaseAPI.chatLibrary.update(uuid, {
      kg_base_uuid: item.kg_base_uuid,
      name,
      messages: detail.data?.messages || {},
      is_favorite: Boolean(item.is_favorite),
    });
    if (response.code !== 200) return notify(response.msg || '重命名失败');
    item.name = name;
    render();
  }

  async function favorite(uuid, isFavorite) {
    const response = await KgBaseAPI.chatLibrary.setFavorite(uuid, isFavorite);
    if (response.code !== 200) return notify(response.msg || '收藏失败');
    const item = items.find((entry) => entry.uuid === uuid);
    if (item) item.is_favorite = isFavorite;
    render();
  }

  async function remove(uuid) {
    if (!window.confirm('确认删除该对话？')) return;
    const response = await KgBaseAPI.chatLibrary.delete(uuid);
    if (response.code !== 200) return notify(response.msg || '删除失败');
    items = items.filter((item) => item.uuid !== uuid);
    render();
  }

  document.addEventListener('DOMContentLoaded', load);
  document.addEventListener('click', (event) => {
    if (event.target.closest('.chat-context-menu')) return;
    document.querySelectorAll('.chat-context-menu').forEach((element) => element.classList.add('hidden'));
  });
  if (document.readyState !== 'loading') load();

  return {
    favorite,
    filterSearch,
    load,
    remove,
    rename,
    render,
    toggleMenu,
    toggleSort,
  };
})();
