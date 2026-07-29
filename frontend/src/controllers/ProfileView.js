/* Generated from pages/profile.html; keep behavior changes in the source controller during migration. */
export function createProfileViewController() {
  const { Auth, API, KgBaseAPI } = window;

  if (!Auth.requireAuth()) throw new Error('Not logged in');
  lucide.createIcons();

  var editingLlmCapsule = null;
  var editingProfile = false;

  async function ensureCurrentUser() {
    var cached = Auth.getUserInfo() || {};
    if (cached.uuid || cached.user_uuid) return cached;
    var response = await KgBaseAPI.auth.getUserInfo();
    if (response.code !== 200 || !response.data) {
      throw new Error(response.msg || '无法获取当前用户');
    }
    Auth.setUserInfo(response.data);
    return response.data;
  }

  async function loadProfile() {
    try {
      var user = await ensureCurrentUser();
      var name = user.nickname || user.username || '用户';
      var avatar = document.getElementById('profile-avatar');
      var nickname = document.getElementById('profile-nickname');
      var email = document.getElementById('profile-email');
      if (avatar) {
        if (user.avatar) {
          avatar.innerHTML = '<img src="' + String(user.avatar).replace(/"/g, '&quot;') + '" alt="" class="w-full h-full object-cover">';
        } else {
          avatar.textContent = name.slice(0, 2).toUpperCase();
        }
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
      var response = await KgBaseAPI.auth.updateUser(user.username, {
        username: user.username,
        nickname: nickname.value.trim(),
        email: email.value.trim(),
        api_key: user.api_key || null,
        base_url: user.base_url || null,
        model: user.model || null,
      });
      if (response.code !== 200) return showToast(response.msg || '保存资料失败');
      Auth.setUserInfo({ ...user, nickname: nickname.value.trim(), email: email.value.trim() });
      editingProfile = false;
      button.textContent = '编辑资料';
      cancelButton?.classList.add('hidden');
      setAvatarHint(false);
      renderProfileFields(Auth.getUserInfo());
      showToast('个人资料已更新');
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
      var user = await ensureCurrentUser();
      var upload = await API.uploadFile(file);
      if (upload.code !== 200 || !upload.data?.url) throw new Error(upload.msg || '头像上传失败');
      var response = await KgBaseAPI.auth.updateAvatar(user.username, upload.data.url);
      if (response.code !== 200) throw new Error(response.msg || '头像更新失败');
      Auth.setUserInfo({ ...user, avatar: upload.data.url });
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

  function createModelCapsule(model, provider, type) {
    var pill = document.createElement('div');
    var isEmbed = type === 'embedding';
    pill.className = 'group inline-flex items-center gap-1.5 h-8 pl-3 pr-1.5 rounded-full transition-colors';
    pill.style.cssText = 'background:var(--claude-card);border:1px solid var(--claude-border);';
    pill.dataset.modelUuid = model.uuid || '';
    pill.dataset.providerUuid = provider.uuid || '';
    pill.dataset.providerName = provider.name || model.name || '';
    pill.dataset.apiKey = provider.api_key || '';
    pill.dataset.apiUrl = provider.api_url || '';
    pill.dataset.modelType = type;
    pill.innerHTML =
      '<span class="text-xs font-medium" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);"></span>' +
      '<button type="button" onclick="editCapsule(this)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑" aria-label="' + (isEmbed ? '编辑嵌入模型' : '编辑模型') + '"><i data-lucide="pencil" style="width:11px;height:11px;"></i></button>' +
      '<button type="button" onclick="removeCapsule(this)" class="w-5 h-5 rounded-full flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="删除" aria-label="' + (isEmbed ? '删除嵌入模型' : '删除模型') + '"><i data-lucide="x" style="width:11px;height:11px;"></i></button>';
    pill.querySelector('span').textContent = model.name || '未命名模型';
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
      details.forEach(function(provider) {
        (provider.models || []).forEach(function(model) {
          var type = model.type === 'embedding' ? 'embedding' : 'llm';
          var capsule = createModelCapsule(model, provider, type);
          (type === 'embedding' ? embedContainer : llmContainer).insertBefore(
            capsule,
            type === 'embedding' ? embedAdd : llmAdd
          );
        });
      });
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
    var urlInput = document.getElementById('llm-url-input');
    if (editingLlmCapsule) {
      title.textContent = '编辑大模型';
      modelInput.value = editingLlmCapsule.querySelector('span').textContent;
      keyInput.value = editingLlmCapsule.dataset.apiKey || '';
      urlInput.value = editingLlmCapsule.dataset.apiUrl || '';
    } else {
      title.textContent = '添加大模型';
      modelInput.value = '';
      keyInput.value = '';
      urlInput.value = '';
    }
    modal.classList.remove('hidden');
  }

  function closeLlmModal() {
    document.getElementById('modal-llm').classList.add('hidden');
    editingLlmCapsule = null;
  }

  async function saveLlmCapsule() {
    var modelVal = document.getElementById('llm-model-input').value.trim();
    var apiKey = document.getElementById('llm-key-input').value.trim();
    var apiUrl = document.getElementById('llm-url-input').value.trim();
    if (!modelVal) {
      showToast('请输入模型名称');
      return;
    }
    try {
      if (editingLlmCapsule && editingLlmCapsule.dataset.modelUuid) {
        var providerUuid = editingLlmCapsule.dataset.providerUuid;
        var providerResult = await KgBaseAPI.llm.updateProvider(providerUuid, {
          name: editingLlmCapsule.dataset.providerName || modelVal,
          api_key: apiKey || editingLlmCapsule.dataset.apiKey || '',
          api_url: apiUrl || editingLlmCapsule.dataset.apiUrl || '',
        });
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
        var createdProvider = await KgBaseAPI.llm.createProvider(modelVal);
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
        await KgBaseAPI.llm.updateProvider(createdProvider.data.uuid, {
          name: modelVal,
          api_key: apiKey,
          api_url: apiUrl,
        });
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
    editingEmbedCapsule = capsule || null;
    var modal = document.getElementById('modal-embed');
    var title = document.getElementById('modal-embed-title');
    var modelInput = document.getElementById('embed-model-input');
    if (editingEmbedCapsule) {
      title.textContent = '编辑嵌入模型';
      modelInput.value = editingEmbedCapsule.querySelector('span').textContent;
    } else {
      title.textContent = '添加嵌入模型';
      modelInput.value = '';
    }
    document.getElementById('embed-key-input').value = editingEmbedCapsule?.dataset.apiKey || '';
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
    try {
      if (editingEmbedCapsule && editingEmbedCapsule.dataset.modelUuid) {
        var providerUuid = editingEmbedCapsule.dataset.providerUuid;
        var providerResult = await KgBaseAPI.llm.updateProvider(providerUuid, {
          name: editingEmbedCapsule.dataset.providerName || modelVal,
          api_key: apiKey || editingEmbedCapsule.dataset.apiKey || '',
          api_url: apiUrl || editingEmbedCapsule.dataset.apiUrl || '',
        });
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
        var createdProvider = await KgBaseAPI.llm.createProvider(modelVal);
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
        await KgBaseAPI.llm.updateProvider(createdProvider.data.uuid, {
          name: modelVal,
          api_key: apiKey,
          api_url: apiUrl,
        });
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
      capsule.remove();
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
    toggleTaskPanel,
  };
}
