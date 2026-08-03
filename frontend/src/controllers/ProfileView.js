/* Generated from pages/profile.html; keep behavior changes in the source controller during migration. */
import { MAX_IMAGE_SIZE, validateUploadSize } from '@/utils/upload';
import { resolveImageUrl } from '@/utils/image-url';

export function createProfileViewController() {
  const { Auth, API, KgBaseAPI } = window;

  if (!Auth.requireAuth()) throw new Error('Not logged in');
  lucide.createIcons();

  var editingLlmCapsule = null;
  var editingProfile = false;
  var hasEmbeddingModel = false;
  var draggedLlmCapsule = null;
  var dragHoldTimer = null;
  var dragPreview = null;
  var dragStartPoint = null;
  var dragPreviewFrame = 0;

  function renderAvatar(avatar, user, name) {
    avatar.replaceChildren();
    if (!user.avatar) {
      avatar.textContent = name.slice(0, 2).toUpperCase();
      return;
    }

    var image = document.createElement('img');
    var retries = 0;
    var avatarSource = function() {
      var resolved = resolveImageUrl(user.avatar);
      if (/^(data:|blob:)/i.test(resolved)) return resolved;
      var url = new URL(resolved);
      url.searchParams.set('avatar_v', String(Date.now()));
      return url.href;
    };
    image.src = avatarSource();
    image.alt = `${name}的头像`;
    image.className = 'w-full h-full object-cover';
    image.addEventListener('error', function() {
      if (retries < 12) {
        retries += 1;
        window.setTimeout(function() { image.src = avatarSource(); }, Math.min(5000, retries * 500));
        return;
      }
      avatar.replaceChildren();
      avatar.textContent = name.slice(0, 2).toUpperCase();
    });
    avatar.appendChild(image);
  }

  async function ensureCurrentUser() {
    var cached = Auth.getUserInfo() || {};
    try {
      var response = await KgBaseAPI.auth.getUserInfo();
      if (response.code === 200 && response.data) {
        var current = {
          ...cached,
          ...response.data,
          avatar: response.data.avatar || cached.avatar || null,
        };
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
      var user = await ensureCurrentUser();
      var name = user.nickname || user.username || '用户';
      var avatar = document.getElementById('profile-avatar');
      var nickname = document.getElementById('profile-nickname');
      var email = document.getElementById('profile-email');
      if (avatar) {
        renderAvatar(avatar, user, name);
      }
      if (nickname) nickname.textContent = name;
      if (email) email.textContent = user.email || '未设置邮箱';
    } catch (error) {
      showToast(error.message || '加载个人资料失败');
    }
  }

  async function editProfile() {
    var user = await ensureCurrentUser();
    var nickname = document.getElementById('profile-nickname');
    var email = document.getElementById('profile-email');
    var button = document.getElementById('profile-edit-button');
    var cancelButton = document.getElementById('profile-cancel-button');
    if (!nickname || !email || !button) return;
    if (editingProfile) {
      var username = nickname.value.trim();
      if (!username) return showToast('用户名不能为空');
      if (username.length > 20) return showToast('用户名不能超过 20 个字符');
      var response = await KgBaseAPI.auth.updateUser(user.username, {
        username: username,
        nickname: username,
        email: email.value.trim(),
      });
      if (response.code !== 200) return showToast(response.msg || '保存资料失败');
      Auth.setUserInfo({
        ...user,
        username: username,
        nickname: username,
        email: email.value.trim(),
      });
      editingProfile = false;
      button.textContent = '编辑资料';
      cancelButton?.classList.add('hidden');
      setAvatarHint(false);
      renderProfileFields(Auth.getUserInfo());
      showToast('个人资料已更新，下次请使用新用户名登录');
      return;
    }
    var nicknameInput = document.createElement('input');
    var emailInput = document.createElement('input');
    nicknameInput.id = 'profile-nickname';
    emailInput.id = 'profile-email';
    nicknameInput.value = user.nickname || user.username || '';
    emailInput.value = user.email || '';
    [nicknameInput, emailInput].forEach(function(input) {
      input.className = 'block w-full h-9 px-3 rounded-lg border outline-none text-sm';
      input.style.cssText = 'background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);';
    });
    emailInput.classList.add('mt-2');
    nickname.replaceWith(nicknameInput);
    email.replaceWith(emailInput);
    editingProfile = true;
    button.textContent = '保存';
    cancelButton?.classList.remove('hidden');
    setAvatarHint(true);
  }

  function setAvatarHint(visible) {
    var hint = document.getElementById('avatar-upload-hint');
    if (!hint) return;
    hint.classList.toggle('hidden', !visible);
    hint.style.display = visible ? 'flex' : 'none';
  }

  function renderProfileFields(user) {
    var container = document.getElementById('profile-fields');
    if (!container) return;
    container.innerHTML = '<p id="profile-nickname" class="text-lg font-semibold truncate" style="color:var(--claude-foreground);"></p>' +
      '<p id="profile-email" class="text-sm mt-1 truncate" style="color:var(--claude-muted-foreground);"></p>';
    container.querySelector('#profile-nickname').textContent = user.nickname || user.username || '用户';
    container.querySelector('#profile-email').textContent = user.email || '未设置邮箱';
  }

  async function cancelProfileEdit() {
    editingProfile = false;
    document.getElementById('profile-edit-button').textContent = '编辑资料';
    document.getElementById('profile-cancel-button')?.classList.add('hidden');
    setAvatarHint(false);
    renderProfileFields(await ensureCurrentUser());
  }

  function triggerAvatarUpload() {
    document.getElementById('profile-avatar-input')?.click();
  }

  async function uploadAvatar(input) {
    var file = input?.files?.[0];
    if (!file) return;
    try {
      validateUploadSize(file, MAX_IMAGE_SIZE);
      var user = await ensureCurrentUser();
      var upload = await API.uploadFile(file);
      if (upload.code !== 200 || !upload.data?.url) throw new Error(upload.msg || '头像上传失败');
      var response = await KgBaseAPI.auth.updateAvatar(user.username, upload.data.url);
      if (response.code !== 200) throw new Error(response.msg || '头像更新失败');
      var currentUser = await KgBaseAPI.auth.getUserInfo();
      Auth.setUserInfo(
        currentUser.code === 200 && currentUser.data
          ? { ...user, ...currentUser.data, avatar: currentUser.data.avatar || upload.data.url }
          : { ...user, avatar: upload.data.url }
      );
      await loadProfile();
      showToast('头像已更新');
    } catch (error) {
      showToast(error.message || '头像上传失败');
    } finally {
      if (input) input.value = '';
    }
  }

  function showToast(msg) {
    window.showToast(msg);
  }

  function refreshLlmDefaults() {
    document.querySelectorAll('#llm-capsules > [data-model-uuid]').forEach(function(capsule, index) {
      var badge = capsule.querySelector('[data-role="default-badge"]');
      if (badge) badge.classList.toggle('hidden', index !== 0);
    });
  }

  async function persistLlmOrder() {
    var providerUuids = Array.from(document.querySelectorAll('#llm-capsules > [data-provider-uuid]'))
      .map(function(capsule) { return capsule.dataset.providerUuid; })
      .filter(Boolean);
    if (!providerUuids.length) return;
    var response = await KgBaseAPI.llm.reorderProviders(providerUuids);
    if (response.code !== 200) throw new Error(response.msg || '模型顺序保存失败');
  }

  function enableLongPressSort(capsule) {
    capsule.addEventListener('pointerdown', function(event) {
      if (event.target.closest('button')) return;
      event.preventDefault();
      var pointerId = event.pointerId;
      dragStartPoint = { x: event.clientX, y: event.clientY };
      dragHoldTimer = window.setTimeout(function() {
        draggedLlmCapsule = capsule;
        capsule.setPointerCapture(pointerId);
        var rect = capsule.getBoundingClientRect();
        dragPreview = capsule.cloneNode(true);
        dragPreview.removeAttribute('data-model-uuid');
        dragPreview.removeAttribute('data-provider-uuid');
        dragPreview.querySelectorAll('button').forEach(function(button) { button.remove(); });
        dragPreview.classList.add('llm-drag-preview');
        dragPreview.style.width = rect.width + 'px';
        dragPreview.style.height = rect.height + 'px';
        dragPreview.style.left = rect.left + 'px';
        dragPreview.style.top = rect.top + 'px';
        document.body.appendChild(dragPreview);
        document.body.classList.add('llm-sorting-active');
        capsule.classList.add('llm-capsule-dragging');
        capsule.style.cursor = 'grabbing';
        if (navigator.vibrate) navigator.vibrate(18);
      }, 350);
    });
    capsule.addEventListener('pointermove', function(event) {
      if (!draggedLlmCapsule && dragStartPoint
        && Math.hypot(event.clientX - dragStartPoint.x, event.clientY - dragStartPoint.y) > 7) {
        window.clearTimeout(dragHoldTimer);
        dragHoldTimer = null;
        return;
      }
      if (!draggedLlmCapsule) return;
      if (dragPreview) {
        var previewX = event.clientX - dragStartPoint.x;
        var previewY = event.clientY - dragStartPoint.y;
        window.cancelAnimationFrame(dragPreviewFrame);
        dragPreviewFrame = window.requestAnimationFrame(function() {
          if (dragPreview) dragPreview.style.transform = `translate3d(${previewX}px,${previewY}px,0) scale(1.04)`;
        });
      }
      var siblings = Array.from(capsule.parentNode.querySelectorAll(':scope > [data-model-uuid]'));
      var candidates = siblings.filter(function(item) { return item !== capsule; });
      var target = candidates.reduce(function(nearest, item) {
        var rect = item.getBoundingClientRect();
        var distance = Math.abs(event.clientX - (rect.left + rect.width / 2))
          + Math.abs(event.clientY - (rect.top + rect.height / 2)) * 2;
        return !nearest || distance < nearest.distance ? { item: item, distance: distance } : nearest;
      }, null)?.item;
      if (!target) return;
      var rect = target.getBoundingClientRect();
      var targetCenterX = rect.left + rect.width / 2;
      var targetCenterY = rect.top + rect.height / 2;
      var sameRow = Math.abs(event.clientY - targetCenterY) <= rect.height;
      var insertBefore = sameRow ? event.clientX < targetCenterX : event.clientY < targetCenterY;
      var alreadyPlaced = insertBefore
        ? capsule.nextElementSibling === target
        : target.nextElementSibling === capsule;
      if (alreadyPlaced) return;
      var before = new Map(siblings.map(function(item) { return [item, item.getBoundingClientRect()]; }));
      target.parentNode.insertBefore(capsule, insertBefore ? target : target.nextSibling);
      siblings.forEach(function(item) {
        if (item === capsule) return;
        var previous = before.get(item);
        var current = item.getBoundingClientRect();
        var dx = previous.left - current.left;
        var dy = previous.top - current.top;
        if (dx || dy) {
          item.getAnimations().forEach(function(animation) { animation.cancel(); });
          item.animate(
            [{ transform: `translate3d(${dx}px,${dy}px,0)` }, { transform: 'translate3d(0,0,0)' }],
            { duration: 165, easing: 'cubic-bezier(.22,1,.36,1)' }
          );
        }
      });
      refreshLlmDefaults();
    });
    var finish = async function() {
      window.clearTimeout(dragHoldTimer);
      dragHoldTimer = null;
      if (!draggedLlmCapsule) {
        dragStartPoint = null;
        return;
      }
      draggedLlmCapsule.classList.remove('llm-capsule-dragging');
      draggedLlmCapsule.style.cursor = 'grab';
      window.cancelAnimationFrame(dragPreviewFrame);
      dragPreviewFrame = 0;
      dragPreview?.remove();
      dragPreview = null;
      dragStartPoint = null;
      document.body.classList.remove('llm-sorting-active');
      draggedLlmCapsule = null;
      try {
        await persistLlmOrder();
        showToast('模型顺序已更新，第一个模型将默认使用');
      } catch (error) {
        showToast(error.message || '模型顺序保存失败');
        await loadModelConfig();
      }
    };
    capsule.addEventListener('pointerup', finish);
    capsule.addEventListener('pointercancel', finish);
    capsule.addEventListener('pointerleave', function() {
      if (!draggedLlmCapsule) {
        window.clearTimeout(dragHoldTimer);
        dragHoldTimer = null;
        dragStartPoint = null;
      }
    });
  }

  function createModelCapsule(model, provider, type) {
    var pill = document.createElement('div');
    var isEmbed = type === 'embedding';
    pill.className = 'group inline-flex items-center gap-1.5 h-8 pl-3 pr-1.5 rounded-full transition-colors';
    pill.style.cssText = 'background:var(--claude-card);border:1px solid var(--claude-border);cursor:' + (isEmbed ? 'default' : 'grab') + ';touch-action:none;user-select:none;-webkit-user-select:none;';
    pill.dataset.modelUuid = model.uuid || '';
    pill.dataset.providerUuid = provider.uuid || '';
    pill.dataset.providerName = provider.name || model.name || '';
    pill.dataset.hasApiKey = provider.api_key ? 'true' : 'false';
    pill.dataset.apiUrl = provider.api_url || '';
    pill.dataset.modelType = type;
    pill.innerHTML =
      '<span class="text-xs font-medium" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);"></span>' +
      (!isEmbed ? '<span data-role="default-badge" class="hidden text-[10px] px-1.5 py-0.5 rounded-full" style="background:var(--claude-accent);color:var(--claude-primary);">默认</span>' : '') +
      (provider.api_key
        ? '<span class="inline-flex items-center gap-1 text-[10px]" style="color:var(--claude-success-500);" title="API Key 已加密保存"><i data-lucide="shield-check" style="width:11px;height:11px;"></i>已保存</span>'
        : '<span class="text-[10px]" style="color:var(--claude-destructive);">未配置密钥</span>') +
      '<button type="button" onclick="editCapsule(this)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑" aria-label="' + (isEmbed ? '编辑嵌入模型' : '编辑模型') + '"><i data-lucide="pencil" style="width:11px;height:11px;"></i></button>' +
      '<button type="button" onclick="removeCapsule(this)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="删除" aria-label="' + (isEmbed ? '删除嵌入模型' : '删除模型') + '"><i data-lucide="x" style="width:11px;height:11px;"></i></button>';
    pill.querySelector('span').textContent = model.name || '未命名模型';
    if (!isEmbed) enableLongPressSort(pill);
    return pill;
  }

  async function loadModelConfig() {
    try {
      var providerResponse = await KgBaseAPI.llm.getProviders();
      if (providerResponse.code !== 200) throw new Error(providerResponse.msg || '加载模型配置失败');
      var providers = providerResponse.data || [];
      var details = await Promise.all(providers.map(async function(provider) {
        var response = await KgBaseAPI.llm.getProviderDetail(provider.uuid);
        return response.code === 200 ? response.data : provider;
      }));
      var llmContainer = document.getElementById('llm-capsules');
      var embedContainer = document.getElementById('embed-capsules');
      var llmAdd = llmContainer.lastElementChild;
      var embedAdd = embedContainer.lastElementChild;
      llmContainer.querySelectorAll('.group').forEach(function(item) { item.remove(); });
      embedContainer.querySelectorAll('.group').forEach(function(item) { item.remove(); });
      var embeddingCount = 0;
      details.filter(function(provider) { return provider.status !== 0; }).forEach(function(provider) {
        (provider.models || []).forEach(function(model) {
          if (model.status === 0) return;
          var type = ['embedding', 'text-embedding'].includes(model.type) ? 'embedding' : 'llm';
          if (type === 'embedding') embeddingCount += 1;
          var capsule = createModelCapsule(model, provider, type);
          (type === 'embedding' ? embedContainer : llmContainer).insertBefore(
            capsule,
            type === 'embedding' ? embedAdd : llmAdd
          );
        });
      });
      hasEmbeddingModel = embeddingCount > 0;
      refreshLlmDefaults();
      if (embedAdd) {
        embedAdd.disabled = hasEmbeddingModel;
        embedAdd.classList.toggle('opacity-40', hasEmbeddingModel);
        embedAdd.classList.toggle('cursor-not-allowed', hasEmbeddingModel);
        embedAdd.title = hasEmbeddingModel ? '每个用户只能配置一个嵌入模型' : '添加嵌入模型';
      }
      lucide.createIcons();
    } catch (error) {
      showToast(error.message || '加载模型配置失败');
    }
  }

  function openLlmModal(capsule) {
    editingLlmCapsule = capsule || null;
    var modal = document.getElementById('modal-llm');
    var title = document.getElementById('modal-llm-title');
    var modelInput = document.getElementById('llm-model-input');
    var keyInput = document.getElementById('llm-key-input');
    var keyStatus = document.getElementById('llm-key-status');
    var urlInput = document.getElementById('llm-url-input');
    if (editingLlmCapsule) {
      title.textContent = '编辑大模型';
      modelInput.value = editingLlmCapsule.querySelector('span').textContent;
      keyInput.value = '';
      keyInput.placeholder = editingLlmCapsule.dataset.hasApiKey === 'true'
        ? 'API Key 已保存，留空则不修改'
        : '请输入 API Key';
      keyStatus.textContent = editingLlmCapsule.dataset.hasApiKey === 'true'
        ? '密钥已安全保存，服务端不会向浏览器回显明文。'
        : '当前尚未保存 API Key。';
      urlInput.value = editingLlmCapsule.dataset.apiUrl || '';
    } else {
      title.textContent = '添加大模型';
      modelInput.value = '';
      keyInput.value = '';
      keyInput.placeholder = '请输入 API Key';
      keyStatus.textContent = '密钥将加密保存，保存后不会回显明文。';
      urlInput.value = '';
    }
    modal.classList.remove('hidden');
  }

  function closeLlmModal() {
    document.getElementById('modal-llm').classList.add('hidden');
    editingLlmCapsule = null;
  }

  async function testModelConnection(modelType) {
    var prefix = modelType === 'embedding' ? 'embed' : 'llm';
    var modelVal = document.getElementById(prefix + '-model-input').value.trim();
    var apiKey = document.getElementById(prefix + '-key-input').value.trim();
    var apiUrl = document.getElementById(prefix + '-url-input').value.trim();
    if (!modelVal || !apiKey || !apiUrl) {
      showToast('请先填写模型名称、API Key 和 Base URL');
      return;
    }

    var button = document.getElementById(prefix + '-test-button');
    var originalText = button?.textContent || '测试连接';
    if (button) {
      button.disabled = true;
      button.textContent = '测试中…';
      button.style.opacity = '0.6';
      button.style.cursor = 'wait';
    }
    try {
      var result = await KgBaseAPI.llm.testModel({
        base_url: apiUrl,
        api_key: apiKey,
        model_name: modelVal,
        model_type: modelType,
      });
      if (result.code !== 200) throw new Error(result.msg || '模型连接测试失败');
      showToast(modelType === 'embedding' ? '嵌入模型连接测试成功' : '大模型连接测试成功');
    } catch (error) {
      showToast(error.message || '模型连接测试失败，请检查填写信息');
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = originalText;
        button.style.opacity = '';
        button.style.cursor = '';
      }
    }
  }

  async function saveLlmCapsule() {
    var modelVal = document.getElementById('llm-model-input').value.trim();
    var apiKey = document.getElementById('llm-key-input').value.trim();
    var apiUrl = document.getElementById('llm-url-input').value.trim();
    if (!modelVal) {
      showToast('请输入模型名称');
      return;
    }
    if (!apiUrl) {
      showToast('请输入 Base URL');
      return;
    }
    if (!editingLlmCapsule && !apiKey) {
      showToast('请输入 API Key');
      return;
    }
    try {
      if (editingLlmCapsule && editingLlmCapsule.dataset.modelUuid) {
        var providerUuid = editingLlmCapsule.dataset.providerUuid;
        var providerPayload = {
          name: editingLlmCapsule.dataset.providerName || modelVal,
          api_url: apiUrl || editingLlmCapsule.dataset.apiUrl || '',
        };
        if (apiKey) providerPayload.api_key = apiKey;
        var providerResult = await KgBaseAPI.llm.updateProvider(providerUuid, providerPayload);
        if (providerResult.code !== 200) throw new Error(providerResult.msg || '保存失败');
        var modelResult = await KgBaseAPI.llm.updateModel(editingLlmCapsule.dataset.modelUuid, {
          name: modelVal,
          type: 'llm',
          group_name: modelVal,
          status: 1,
        });
        if (modelResult.code !== 200) throw new Error(modelResult.msg || '保存失败');
      } else {
        await ensureCurrentUser();
        var createdProvider = await KgBaseAPI.llm.createProvider(modelVal, {
          api_key: apiKey,
          api_url: apiUrl,
        });
        if (createdProvider.code !== 200 || !createdProvider.data?.uuid) {
          throw new Error(createdProvider.msg || '创建模型服务失败');
        }
        var createdModel = await KgBaseAPI.llm.createModel({
          provider_uuid: createdProvider.data.uuid,
          name: modelVal,
          type: 'llm',
          group_name: modelVal,
          status: 1,
        });
        if (createdModel.code !== 200) throw new Error(createdModel.msg || '创建模型失败');
      }
      closeLlmModal();
      await loadModelConfig();
      showToast('模型配置已保存');
    } catch (error) {
      showToast(error.message || '保存失败');
    }
  }

  var editingEmbedCapsule = null;

  function openEmbedModal(capsule) {
    if (!capsule && hasEmbeddingModel) {
      showToast('每个用户只能配置一个嵌入模型');
      return;
    }
    editingEmbedCapsule = capsule || null;
    var modal = document.getElementById('modal-embed');
    var title = document.getElementById('modal-embed-title');
    var modelInput = document.getElementById('embed-model-input');
    var keyInput = document.getElementById('embed-key-input');
    var keyStatus = document.getElementById('embed-key-status');
    if (editingEmbedCapsule) {
      title.textContent = '编辑嵌入模型';
      modelInput.value = editingEmbedCapsule.querySelector('span').textContent;
      keyInput.placeholder = editingEmbedCapsule.dataset.hasApiKey === 'true'
        ? 'API Key 已保存，留空则不修改'
        : '请输入 API Key';
      keyStatus.textContent = editingEmbedCapsule.dataset.hasApiKey === 'true'
        ? '密钥已安全保存，服务端不会向浏览器回显明文。'
        : '当前尚未保存 API Key。';
    } else {
      title.textContent = '添加嵌入模型';
      modelInput.value = '';
      keyInput.placeholder = '请输入 API Key';
      keyStatus.textContent = '密钥将加密保存，保存后不会回显明文。';
    }
    keyInput.value = '';
    document.getElementById('embed-url-input').value = editingEmbedCapsule?.dataset.apiUrl || '';
    modal.classList.remove('hidden');
  }

  function closeEmbedModal() {
    document.getElementById('modal-embed').classList.add('hidden');
    editingEmbedCapsule = null;
  }

  async function saveEmbedCapsule() {
    var modelVal = document.getElementById('embed-model-input').value.trim();
    var apiKey = document.getElementById('embed-key-input').value.trim();
    var apiUrl = document.getElementById('embed-url-input').value.trim();
    if (!modelVal) {
      showToast('请输入模型名称');
      return;
    }
    if (!apiUrl) {
      showToast('请输入 Base URL');
      return;
    }
    if (!editingEmbedCapsule && !apiKey) {
      showToast('请输入 API Key');
      return;
    }
    if (!editingEmbedCapsule && hasEmbeddingModel) {
      showToast('每个用户只能配置一个嵌入模型');
      return;
    }
    try {
      if (editingEmbedCapsule && editingEmbedCapsule.dataset.modelUuid) {
        var providerUuid = editingEmbedCapsule.dataset.providerUuid;
        var providerPayload = {
          name: editingEmbedCapsule.dataset.providerName || modelVal,
          api_url: apiUrl || editingEmbedCapsule.dataset.apiUrl || '',
        };
        if (apiKey) providerPayload.api_key = apiKey;
        var providerResult = await KgBaseAPI.llm.updateProvider(providerUuid, providerPayload);
        if (providerResult.code !== 200) throw new Error(providerResult.msg || '保存失败');
        var modelResult = await KgBaseAPI.llm.updateModel(editingEmbedCapsule.dataset.modelUuid, {
          name: modelVal,
          type: 'embedding',
          group_name: modelVal,
          status: 1,
        });
        if (modelResult.code !== 200) throw new Error(modelResult.msg || '保存失败');
      } else {
        await ensureCurrentUser();
        var createdProvider = await KgBaseAPI.llm.createProvider(modelVal, {
          api_key: apiKey,
          api_url: apiUrl,
        });
        if (createdProvider.code !== 200 || !createdProvider.data?.uuid) {
          throw new Error(createdProvider.msg || '创建模型服务失败');
        }
        var createdModel = await KgBaseAPI.llm.createModel({
          provider_uuid: createdProvider.data.uuid,
          name: modelVal,
          type: 'embedding',
          group_name: modelVal,
          status: 1,
        });
        if (createdModel.code !== 200) throw new Error(createdModel.msg || '创建模型失败');
      }
      closeEmbedModal();
      await loadModelConfig();
      showToast('模型配置已保存');
    } catch (error) {
      showToast(error.message || '保存失败');
    }
  }

  async function removeCapsule(btn) {
    var capsule = btn.closest('.group');
    var modelUuid = capsule.dataset.modelUuid;
    if (!modelUuid) {
      capsule.remove();
      return;
    }
    try {
      var result = await KgBaseAPI.llm.deleteModel(modelUuid);
      if (result.code !== 200) throw new Error(result.msg || '删除失败');
      var providerUuid = capsule.dataset.providerUuid;
      var siblingModels = Array.from(document.querySelectorAll('[data-provider-uuid]'))
        .filter(function(item) {
          return item !== capsule && item.dataset.providerUuid === providerUuid;
        });
      if (providerUuid && siblingModels.length === 0) {
        var providerResult = await KgBaseAPI.llm.deleteProvider(providerUuid);
        if (providerResult.code !== 200) throw new Error(providerResult.msg || '模型已删除，但服务商清理失败');
      }
      await loadModelConfig();
      showToast('模型已删除');
    } catch (error) {
      showToast(error.message || '删除失败');
    }
  }

  function editCapsule(btn) {
    var capsule = btn.closest('.group');
    var container = capsule.parentElement;
    var isEmbed = container.id === 'embed-capsules';
    if (isEmbed) {
      openEmbedModal(capsule);
    } else {
      openLlmModal(capsule);
    }
  }

  function toggleTaskPanel() {
    document.getElementById('task-panel')?.classList.toggle('hidden');
    window.TaskManager?.render();
  }

  loadProfile();
  loadModelConfig();

  window.editCapsule = editCapsule;
  window.removeCapsule = removeCapsule;

  return {
    closeEmbedModal,
    closeLlmModal,
    editCapsule,
    editProfile,
    cancelProfileEdit,
    triggerAvatarUpload,
    uploadAvatar,
    openEmbedModal,
    openLlmModal,
    removeCapsule,
    saveEmbedCapsule,
    saveLlmCapsule,
    testModelConnection,
    toggleTaskPanel,
  };
}
