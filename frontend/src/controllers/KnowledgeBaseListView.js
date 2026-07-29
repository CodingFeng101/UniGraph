/* Generated from pages/kb-list.html; keep behavior changes in the source controller during migration. */
export function createKnowledgeBaseListViewController() {
  const { API, AppConfig, Auth, KgBaseAPI } = window;

  if (!Auth.requireAuth()) throw new Error('Not logged in');
  lucide.createIcons();

  var pendingNewCoverPath = null;
  var newCoverUploading = false;
  var newCoverPreviewUrl = '';
  var knowledgeBases = [];
  var sortMode = 'time-desc';

  function resetNewKBCover() {
    pendingNewCoverPath = null;
    newCoverUploading = false;
    if (newCoverPreviewUrl) URL.revokeObjectURL(newCoverPreviewUrl);
    newCoverPreviewUrl = '';
    var preview = document.getElementById('new-kb-cover-preview');
    var prompt = document.getElementById('new-kb-cover-prompt');
    var status = document.getElementById('new-kb-cover-status');
    var input = document.getElementById('new-kb-cover-file');
    if (preview) {
      preview.removeAttribute('src');
      preview.classList.add('hidden');
    }
    if (prompt) {
      prompt.style.padding = '';
      prompt.style.borderRadius = '';
      prompt.style.background = '';
    }
    if (status) status.textContent = '上传封面图';
    if (input) input.value = '';
  }

  function toggleNewKBCard() {
    var modal = document.getElementById('new-kb-card');
    var willClose = !modal.classList.contains('hidden');
    modal.classList.toggle('hidden');
    if (willClose) resetNewKBCover();
  }

  function triggerNewKBCoverUpload() {
    if (!newCoverUploading) document.getElementById('new-kb-cover-file')?.click();
  }

  async function uploadNewKBCover(input) {
    var file = input.files && input.files[0];
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      showToast('请选择 JPG、PNG 或 WebP 图片');
      input.value = '';
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      showToast('封面图片不能超过 5 MB');
      input.value = '';
      return;
    }
    var preview = document.getElementById('new-kb-cover-preview');
    var prompt = document.getElementById('new-kb-cover-prompt');
    var status = document.getElementById('new-kb-cover-status');
    if (newCoverPreviewUrl) URL.revokeObjectURL(newCoverPreviewUrl);
    newCoverPreviewUrl = URL.createObjectURL(file);
    if (preview) {
      preview.src = newCoverPreviewUrl;
      preview.classList.remove('hidden');
    }
    if (status) status.textContent = '正在上传...';
    newCoverUploading = true;
    try {
      var response = await API.uploadFile(file);
      if (response.code !== 200 || !response.data?.url) {
        throw new Error(response.msg || '封面上传失败');
      }
      pendingNewCoverPath = response.data.url;
      if (status) status.textContent = '封面已上传，点击可更换';
      if (prompt) {
        prompt.style.padding = '8px 12px';
        prompt.style.borderRadius = '8px';
        prompt.style.background = 'rgba(253,251,247,0.9)';
      }
    } catch (error) {
      resetNewKBCover();
      showToast(error.message || '封面上传失败');
    } finally {
      newCoverUploading = false;
    }
  }

  function filterKBList() {
    var searchText = (document.getElementById('kb-search-input')?.value || '').trim().toLowerCase();
    var cards = document.querySelectorAll('.kb-card');
    var visibleCount = 0;
    cards.forEach(function(card) {
      var title = card.querySelector('h2')?.textContent.toLowerCase() || '';
      var desc = card.querySelector('p')?.textContent.toLowerCase() || '';
      if (title.includes(searchText) || desc.includes(searchText)) {
        card.style.display = 'flex';
        visibleCount += 1;
      } else {
        card.style.display = 'none';
      }
    });
    var empty = document.getElementById('kb-search-empty');
    if (empty) empty.classList.toggle('hidden', visibleCount > 0 || !searchText);
    var count = document.getElementById('kb-count');
    if (count) count.textContent = searchText
      ? '找到 ' + visibleCount + ' 个知识库'
      : '共 ' + cards.length + ' 个知识库';
  }

          var pendingDeleteCard = null;
  var pendingDeleteUuid = '';

  function deleteKB(btn) {
    var card = btn.closest('.kb-card');
    var title = card.querySelector('h2').textContent;
    pendingDeleteCard = card;
    pendingDeleteUuid = card.dataset.uuid || '';
    document.getElementById('delete-kb-name').textContent = title;
    document.getElementById('delete-confirm').classList.remove('hidden');
  }

  function cancelDeleteKB() {
    document.getElementById('delete-confirm').classList.add('hidden');
    pendingDeleteCard = null;
  }

  async function confirmDeleteKB() {
    document.getElementById('delete-confirm').classList.add('hidden');
    if (!pendingDeleteUuid) {
      pendingDeleteCard = null;
      return;
    }
    var uuid = pendingDeleteUuid;
    var card = pendingDeleteCard;
    pendingDeleteCard = null;
    pendingDeleteUuid = '';
    try {
      var res = await KgBaseAPI.kgBase.delete(uuid);
      if (res.code === 200) {
        if (card) {
          card.style.opacity = '0';
          card.style.transform = 'scale(0.9)';
          card.style.transition = 'opacity 0.3s, transform 0.3s';
          setTimeout(function() { card.remove(); }, 300);
        }
        showToast('删除成功');
        loadKBList();
      } else {
        showToast(res.msg || '删除失败');
      }
    } catch (e) {
      showToast(e.message || '删除失败');
    }
  }

  async function createKB() {
    var name = document.getElementById('new-kb-name').value.trim();
    var desc = document.getElementById('new-kb-desc').value.trim();
    if (!name) {
      showToast('请输入知识库名称');
      return;
    }
    if (newCoverUploading) {
      showToast('封面正在上传，请稍候');
      return;
    }
    try {
      var res = await KgBaseAPI.kgBase.create({
        name: name,
        description: desc,
        cover_image: pendingNewCoverPath,
        status: 1,
      });
      if (res.code === 200) {
        toggleNewKBCard();
        document.getElementById('new-kb-name').value = '';
        document.getElementById('new-kb-desc').value = '';
        resetNewKBCover();
        showToast('创建成功');
        loadKBList();
      } else {
        showToast(res.msg || '创建失败');
      }
    } catch (e) {
      showToast(e.message || '创建失败');
    }
  }

  setInterval(function() {
    var progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
      var current = parseInt(bar.style.width);
      var max = parseInt(bar.dataset.progress);
      if (current < max) {
        bar.style.width = Math.min(current + Math.random() * 2, max) + '%';
      }
    });
  }, 1000);

  function initDraggableTaskFAB() {
    var wrapper = document.getElementById('task-fab-wrapper');
    if (!wrapper) return;
    
    var isDragging = false;
    var startX, startY, initialLeft, initialTop;
    
    wrapper.addEventListener('mousedown', function(e) {
      if (e.target.closest('button')) return;
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      initialLeft = wrapper.offsetLeft;
      initialTop = wrapper.offsetTop;
      wrapper.style.cursor = 'grabbing';
      e.preventDefault();
    });
    
    document.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      var deltaX = e.clientX - startX;
      var deltaY = e.clientY - startY;
      var newLeft = initialLeft + deltaX;
      var newTop = initialTop + deltaY;
      newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - 48));
      newTop = Math.max(0, Math.min(newTop, window.innerHeight - 48));
      wrapper.style.left = newLeft + 'px';
      wrapper.style.top = newTop + 'px';
      wrapper.style.right = 'auto';
      wrapper.style.bottom = 'auto';
    });
    
    document.addEventListener('mouseup', function() {
      isDragging = false;
      wrapper.style.cursor = 'move';
    });
  }

  initDraggableTaskFAB();

  function showToast(msg) {
    window.showToast(msg);
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, function(c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function formatTime(t) {
    if (!t) return '';
    var d = new Date(t);
    if (isNaN(d.getTime())) return String(t);
    var now = new Date();
    var diff = (now - d) / 1000;
    if (diff < 60) return '刚刚';
    if (diff < 3600) return Math.floor(diff / 60) + ' 分钟前';
    if (diff < 86400) return Math.floor(diff / 3600) + ' 小时前';
    if (diff < 86400 * 7) return Math.floor(diff / 86400) + ' 天前';
    return d.toLocaleDateString();
  }

  function localizeKnowledgeBaseName(name) {
    return name === 'KG Introduction' ? '知识图谱介绍' : name;
  }

  function sortedKnowledgeBases() {
    return knowledgeBases.slice().sort(function(left, right) {
      if (sortMode.startsWith('name')) {
        var result = localizeKnowledgeBaseName(left.name || '').localeCompare(
          localizeKnowledgeBaseName(right.name || ''), 'zh-CN'
        );
        return sortMode === 'name-asc' ? result : -result;
      }
      var leftTime = new Date(left.created_time || left.updated_time || 0).getTime();
      var rightTime = new Date(right.created_time || right.updated_time || 0).getTime();
      return sortMode === 'time-asc' ? leftTime - rightTime : rightTime - leftTime;
    });
  }

  function sortKBList(mode) {
    sortMode = mode || 'time-desc';
    var sorted = sortedKnowledgeBases();
    renderKBList(sorted);
    updateWorkspaceConversationLink(sorted);
    filterKBList();
  }

  function renderKBList(list) {
    var container = document.getElementById('kb-list-container');
    var countEl = document.getElementById('kb-count');
    if (!container) return;
    list = list || [];
    if (countEl) countEl.textContent = '共 ' + list.length + ' 个知识库';
    if (!list.length) {
      container.innerHTML = '<div class="col-span-full text-center py-12 text-sm" style="color:var(--claude-muted-foreground);">暂无知识库，点击右上角"新建知识库"创建</div>';
      return;
    }
    var bgColors = ['var(--claude-accent)', 'var(--claude-muted)', 'var(--claude-secondary)'];
    var html = '';
    list.forEach(function(kb, idx) {
      var bg = bgColors[idx % bgColors.length];
      var uuid = kb.uuid || '';
      var name = localizeKnowledgeBaseName(kb.name || '未命名');
      var desc = kb.description || '';
      var coverHtml;
      if (kb.cover_image) {
        var imgSrc = kb.cover_image;
        if (imgSrc.indexOf('http') !== 0 && imgSrc.indexOf('/') !== 0 && imgSrc.indexOf('data:') !== 0) {
          imgSrc = (AppConfig.SHOW_IMAGE_API || '') + imgSrc;
        }
        coverHtml = '<img src="' + escapeHtml(imgSrc) + '" class="absolute inset-0 w-full h-full object-cover" alt="">';
      } else {
        var defaultCover = (AppConfig.SHOW_IMAGE_API || '') + 'static/default/kg_base_default.png';
        coverHtml = '<img src="' + escapeHtml(defaultCover) + '" class="absolute inset-0 w-full h-full object-cover" alt="默认知识库封面">';
      }
      var updateTime = formatTime(kb.updated_time || kb.created_time);
      html += '<article class="kb-card flex flex-col rounded-lg overflow-hidden transition-shadow hover:shadow-md" data-uuid="' + escapeHtml(uuid) + '" style="background:var(--claude-popover);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xs);">' +
        '<div class="h-[160px] relative overflow-hidden" style="background:' + bg + ';">' + coverHtml + '</div>' +
        '<div class="p-4 flex flex-col gap-3 min-w-0">' +
          '<h2 class="text-base font-medium truncate" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">' + escapeHtml(name) + '</h2>' +
          '<p class="text-xs leading-relaxed line-clamp-2" style="font-family:var(--claude-font-serif);color:var(--claude-muted-foreground);">' + escapeHtml(desc) + '</p>' +
          '<div class="flex items-center justify-between gap-2">' +
            '<span class="text-[10px] truncate" style="font-family:var(--claude-font-mono);color:var(--claude-muted-foreground);">' + escapeHtml(uuid) + '</span>' +
          '</div>' +
          '<div class="flex items-center justify-between gap-2">' +
            '<span class="text-[10px] truncate" style="color:var(--claude-muted-foreground);">' + escapeHtml(updateTime) + '</span>' +
            '<div class="flex items-center gap-2 shrink-0">' +
              '<a href="/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/info" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors hover:opacity-90 cursor-pointer" style="background:var(--claude-brand-500);color:var(--claude-primary-foreground);">进入项目</a>' +
              '<button class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer" style="color:var(--claude-muted-foreground);" onmouseenter="this.style.color=\'var(--claude-destructive)\'" onmouseleave="this.style.color=\'var(--claude-muted-foreground)\'" onclick="deleteKB(this)">' +
                '<i data-lucide="trash-2" style="width:14px;height:14px;"></i>删除' +
              '</button>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</article>';
    });
    container.innerHTML = html +
      '<div id="kb-search-empty" class="hidden col-span-full text-center py-12 text-sm" style="color:var(--claude-muted-foreground);">没有找到匹配的知识库</div>';
    if (window.lucide) lucide.createIcons();
  }

  function updateWorkspaceConversationLink(list) {
    var firstUuid = list && list.length ? list[0].uuid : '';
    if (!firstUuid) return;
    var basePath = '/unigraph/unigraphs/' + encodeURIComponent(firstUuid);
    document.getElementById('workspace-app-link').href = basePath + '/qa';
  }

  async function loadKBList() {
    var container = document.getElementById('kb-list-container');
    if (!container) return;
    container.innerHTML = '<div class="col-span-full text-center py-12 text-sm" style="color:var(--claude-muted-foreground);">加载中...</div>';
    try {
      var res = await KgBaseAPI.kgBase.getAll();
      if (res.code === 200) {
        knowledgeBases = res.data || [];
        var list = sortedKnowledgeBases();
        renderKBList(list);
        updateWorkspaceConversationLink(list);
      } else {
        container.innerHTML = '<div class="col-span-full text-center py-12 text-sm" style="color:var(--claude-muted-foreground);">' + escapeHtml(res.msg || '加载失败') + '</div>';
        var countEl = document.getElementById('kb-count');
        if (countEl) countEl.textContent = '共 0 个知识库';
      }
    } catch (e) {
      container.innerHTML = '<div class="col-span-full text-center py-12 text-sm" style="color:var(--claude-muted-foreground);">' + escapeHtml(e.message || '加载失败') + '</div>';
      var countEl2 = document.getElementById('kb-count');
      if (countEl2) countEl2.textContent = '共 0 个知识库';
    }
  }

  loadKBList();

  window.deleteKB = deleteKB;

  return {
    cancelDeleteKB,
    confirmDeleteKB,
    createKB,
    deleteKB,
    filterKBList,
    sortKBList,
    triggerNewKBCoverUpload,
    toggleNewKBCard,
    uploadNewKBCover,
  };
}
