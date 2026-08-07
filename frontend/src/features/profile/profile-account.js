import { MAX_IMAGE_SIZE, validateUploadSize } from '@/utils/upload';
import { resolveImageUrl } from '@/utils/image-url';

export function createProfileAccountController({ Auth, API, KgBaseAPI, notify }) {
  let editing = false;

  function renderAvatar(avatar, user, name) {
    avatar.replaceChildren();
    if (!user.avatar) {
      avatar.textContent = name.slice(0, 2).toUpperCase();
      return;
    }
    const image = document.createElement('img');
    let retries = 0;
    const avatarSource = () => {
      const resolved = resolveImageUrl(user.avatar);
      if (/^(data:|blob:)/i.test(resolved)) return resolved;
      const url = new URL(resolved);
      url.searchParams.set('avatar_v', String(Date.now()));
      return url.href;
    };
    image.src = avatarSource();
    image.alt = `${name}的头像`;
    image.className = 'w-full h-full object-cover';
    image.addEventListener('error', () => {
      if (retries < 12) {
        retries += 1;
        window.setTimeout(() => { image.src = avatarSource(); }, Math.min(5000, retries * 500));
        return;
      }
      avatar.replaceChildren();
      avatar.textContent = name.slice(0, 2).toUpperCase();
    });
    avatar.appendChild(image);
  }

  async function ensureCurrentUser() {
    const cached = Auth.getUserInfo() || {};
    try {
      const response = await KgBaseAPI.auth.getUserInfo();
      if (response.code === 200 && response.data) {
        const current = { ...cached, ...response.data, avatar: response.data.avatar || cached.avatar || null };
        Auth.setUserInfo(current);
        return current;
      }
    } catch {
      if (cached.uuid || cached.user_uuid) return cached;
    }
    if (cached.uuid || cached.user_uuid) return cached;
    throw new Error('无法获取当前用户');
  }

  async function loadProfile() {
    try {
      const user = await ensureCurrentUser();
      const name = user.nickname || user.username || '用户';
      const avatar = document.getElementById('profile-avatar');
      if (avatar) renderAvatar(avatar, user, name);
      const nickname = document.getElementById('profile-nickname');
      const email = document.getElementById('profile-email');
      if (nickname) nickname.textContent = name;
      if (email) email.textContent = user.email || '未设置邮箱';
    } catch (error) {
      notify(error.message || '加载个人资料失败');
    }
  }

  function setAvatarHint(visible) {
    const hint = document.getElementById('avatar-upload-hint');
    if (!hint) return;
    hint.classList.toggle('hidden', !visible);
    hint.style.display = visible ? 'flex' : 'none';
  }

  function renderProfileFields(user) {
    const container = document.getElementById('profile-fields');
    if (!container) return;
    container.innerHTML = '<p id="profile-nickname" class="text-lg font-semibold truncate" style="color:var(--claude-foreground);"></p>'
      + '<p id="profile-email" class="text-sm mt-1 truncate" style="color:var(--claude-muted-foreground);"></p>';
    container.querySelector('#profile-nickname').textContent = user.nickname || user.username || '用户';
    container.querySelector('#profile-email').textContent = user.email || '未设置邮箱';
  }

  async function editProfile() {
    const user = await ensureCurrentUser();
    const nickname = document.getElementById('profile-nickname');
    const email = document.getElementById('profile-email');
    const button = document.getElementById('profile-edit-button');
    const cancelButton = document.getElementById('profile-cancel-button');
    if (!nickname || !email || !button) return;
    if (editing) {
      const username = nickname.value.trim();
      if (!username) return notify('用户名不能为空');
      if (username.length > 20) return notify('用户名不能超过 20 个字符');
      const response = await KgBaseAPI.auth.updateUser(user.username, {
        username,
        nickname: username,
        email: email.value.trim(),
      });
      if (response.code !== 200) return notify(response.msg || '保存资料失败');
      Auth.setUserInfo({ ...user, username, nickname: username, email: email.value.trim() });
      editing = false;
      button.textContent = '编辑资料';
      cancelButton?.classList.add('hidden');
      setAvatarHint(false);
      renderProfileFields(Auth.getUserInfo());
      notify('个人资料已更新，下次请使用新用户名登录');
      return;
    }
    const nicknameInput = document.createElement('input');
    const emailInput = document.createElement('input');
    nicknameInput.id = 'profile-nickname';
    emailInput.id = 'profile-email';
    nicknameInput.value = user.nickname || user.username || '';
    emailInput.value = user.email || '';
    [nicknameInput, emailInput].forEach((input) => {
      input.className = 'block w-full h-9 px-3 rounded-lg border outline-none text-sm';
      input.style.cssText = 'background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);';
    });
    emailInput.classList.add('mt-2');
    nickname.replaceWith(nicknameInput);
    email.replaceWith(emailInput);
    editing = true;
    button.textContent = '保存';
    cancelButton?.classList.remove('hidden');
    setAvatarHint(true);
  }

  async function cancelProfileEdit() {
    editing = false;
    document.getElementById('profile-edit-button').textContent = '编辑资料';
    document.getElementById('profile-cancel-button')?.classList.add('hidden');
    setAvatarHint(false);
    renderProfileFields(await ensureCurrentUser());
  }

  function triggerAvatarUpload() {
    document.getElementById('profile-avatar-input')?.click();
  }

  async function uploadAvatar(input) {
    const file = input?.files?.[0];
    if (!file) return;
    try {
      validateUploadSize(file, MAX_IMAGE_SIZE);
      const user = await ensureCurrentUser();
      const upload = await API.uploadFile(file);
      if (upload.code !== 200 || !upload.data?.url) throw new Error(upload.msg || '头像上传失败');
      const response = await KgBaseAPI.auth.updateAvatar(user.username, upload.data.url);
      if (response.code !== 200) throw new Error(response.msg || '头像更新失败');
      const currentUser = await KgBaseAPI.auth.getUserInfo();
      Auth.setUserInfo(currentUser.code === 200 && currentUser.data
        ? { ...user, ...currentUser.data, avatar: currentUser.data.avatar || upload.data.url }
        : { ...user, avatar: upload.data.url });
      await loadProfile();
      notify('头像已更新');
    } catch (error) {
      notify(error.message || '头像上传失败');
    } finally {
      if (input) input.value = '';
    }
  }

  return { cancelProfileEdit, editProfile, ensureCurrentUser, loadProfile, triggerAvatarUpload, uploadAvatar };
}
