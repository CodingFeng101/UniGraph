export function createChatSharingController({ api, copyText, getChatUuid, notify }) {
  let currentShare = null;

  function buildShareUrl(publicId) {
    return new URL(`/unigraph/share/${encodeURIComponent(publicId)}`, window.location.origin).toString();
  }

  function renderShareState(share) {
    currentShare = share || null;
    const emptyState = document.getElementById('share-empty-state');
    const activeState = document.getElementById('share-active-state');
    const subtitle = document.getElementById('share-subtitle');
    const link = document.getElementById('share-link');
    emptyState?.classList.toggle('hidden', Boolean(share));
    activeState?.classList.toggle('hidden', !share);
    if (link) link.value = share ? buildShareUrl(share.public_id) : '';
    if (subtitle) subtitle.textContent = share
      ? `已分享 ${share.message_count} 条消息，之后的新消息不会自动加入`
      : '创建截至当前消息的只读快照';
  }

  async function toggleShareModal() {
    const modal = document.getElementById('share-modal');
    if (!modal) return;
    if (!modal.classList.contains('hidden')) {
      modal.classList.add('hidden');
      return;
    }
    const chatUuid = getChatUuid();
    if (!chatUuid) return notify('请先发送一条消息再分享');
    modal.classList.remove('hidden');
    renderShareState(null);
    const subtitle = document.getElementById('share-subtitle');
    if (subtitle) subtitle.textContent = '正在读取分享状态';
    const response = await api.getShare(chatUuid);
    if (response.code !== 200) {
      modal.classList.add('hidden');
      notify(response.msg || '读取分享状态失败');
      return;
    }
    renderShareState(response.data);
  }

  async function copyShareLink() {
    const link = document.getElementById('share-link');
    if (!link?.value) return;
    await copyText(link.value);
    notify('分享链接已复制');
  }

  async function createShareLink() {
    const chatUuid = getChatUuid();
    if (!chatUuid) return;
    const response = await api.createShare(chatUuid);
    if (response.code !== 200 || !response.data) return notify(response.msg || '创建分享链接失败');
    renderShareState(response.data);
    notify('分享链接已创建');
  }

  async function updateShareSnapshot() {
    const chatUuid = getChatUuid();
    if (!chatUuid || !currentShare) return;
    const response = await api.updateShare(chatUuid);
    if (response.code !== 200 || !response.data) return notify(response.msg || '更新分享失败');
    renderShareState(response.data);
    notify('分享快照已更新');
  }

  async function rotateShareLink() {
    const chatUuid = getChatUuid();
    if (!chatUuid || !currentShare) return;
    const confirmed = typeof window.confirmAction === 'function'
      ? await window.confirmAction({
        title: '重新生成分享链接',
        message: '重新生成后，当前分享链接会立即失效，已获得旧链接的人将无法继续访问。',
        confirmText: '重新生成',
      })
      : window.confirm('重新生成后，当前分享链接会立即失效。是否继续？');
    if (!confirmed) return;
    const response = await api.rotateShare(chatUuid);
    if (response.code !== 200 || !response.data) return notify(response.msg || '重新生成分享链接失败');
    renderShareState(response.data);
    notify('新分享链接已生成，旧链接已失效');
  }

  async function stopSharing() {
    const chatUuid = getChatUuid();
    if (!chatUuid || !currentShare) return;
    const response = await api.revokeShare(chatUuid);
    if (response.code !== 200) return notify(response.msg || '停止分享失败');
    renderShareState(null);
    notify('已停止分享');
  }

  return { copyShareLink, createShareLink, rotateShareLink, stopSharing, toggleShareModal, updateShareSnapshot };
}
