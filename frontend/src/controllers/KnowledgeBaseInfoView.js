/* Generated from pages/kb-info.html; keep behavior changes in the source controller during migration. */
import { copyText } from '@/utils/clipboard';

export function createKnowledgeBaseInfoViewController() {
  const { AppConfig, Auth, API, KgBaseAPI } = window;

var isEditing = false;

function applyEditState(editing) {
  isEditing = editing;
  var name = document.getElementById('kb-name');
  var desc = document.getElementById('kb-desc');
  var editButton = document.getElementById('kb-edit-button');
  var editLabel = document.getElementById('kb-edit-label');
  var cancelButton = document.getElementById('kb-cancel-button');
  var coverOverlay = document.getElementById('cover-edit-overlay');
  [name, desc].forEach(function(element) {
    if (!element) return;
    element.contentEditable = editing ? 'true' : 'false';
    element.style.outline = editing ? '1px solid var(--claude-brand-500)' : 'none';
    element.style.borderRadius = editing ? '8px' : '';
    element.style.padding = editing ? '4px 8px' : '';
    element.style.background = editing ? 'var(--claude-card)' : '';
  });
  if (editButton && editLabel) editLabel.textContent = editing ? '保存' : '编辑';
  if (cancelButton) cancelButton.classList.toggle('hidden', !editing);
  if (coverOverlay) {
    coverOverlay.classList.toggle('hidden', !editing);
    coverOverlay.classList.toggle('flex', editing);
  }
  if (editing) name?.focus();
}

function toggleEdit() {
  if (isEditing) return saveEdit();
  applyEditState(true);
}

function cancelEdit() {
  if (currentKgBaseDetail) {
    document.getElementById('kb-name').textContent = localizeKnowledgeBaseName(currentKgBaseDetail.name || '未命名知识库');
    document.getElementById('kb-desc').textContent = currentKgBaseDetail.description || '暂无描述';
    pendingCoverPath = null;
    applyCover(currentKgBaseDetail.cover_image);
  }
  applyEditState(false);
}

var currentKgBaseDetail = null;
var pendingCoverPath = null;

async function saveEdit() {
  var name = document.getElementById('kb-name').textContent;
  var desc = document.getElementById('kb-desc').textContent;
  if (!kgBaseUuid) {
    showToast('缺少知识库 UUID');
    return;
  }
  if (name.trim().length < 3) {
    showToast('知识库名称不能少于 3 个字符');
    return;
  }
  try {
    var res = await KgBaseAPI.kgBase.update(kgBaseUuid, {
      name: name.trim(),
      description: desc.trim(),
      cover_image: pendingCoverPath || (currentKgBaseDetail && currentKgBaseDetail.cover_image) || null,
      status: currentKgBaseDetail && currentKgBaseDetail.status != null ? currentKgBaseDetail.status : 1
    });
    if (res.code !== 200) {
      showToast(res.msg || '保存失败');
      return;
    }
    await loadKgBaseDetail(kgBaseUuid);
    applyEditState(false);
    showToast('修改已保存');
  } catch (error) {
    showToast(error.message || '保存失败');
  }
}

function triggerCoverUpload() {
  if (!isEditing) return;
  document.getElementById('kb-cover-file').click();
}

function applyCover(path) {
  var coverEl = document.getElementById('kb-cover');
  if (!coverEl) return;
  coverEl.style.backgroundImage = path ? 'url(' + AppConfig.SHOW_IMAGE_API + path + ')' : '';
  coverEl.style.backgroundSize = 'cover';
  coverEl.style.backgroundPosition = 'center';
}

async function uploadCover(input) {
  var file = input.files && input.files[0];
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    showToast('请选择图片文件');
    input.value = '';
    return;
  }
  var res = await API.uploadFile(file);
  if (res.code !== 200 || !res.data || !res.data.url) {
    showToast(res.msg || '封面上传失败');
    return;
  }
  pendingCoverPath = res.data.url;
  applyCover(pendingCoverPath);
  showToast('封面已上传，保存修改后生效');
}

function copyUUID() {
  var uuidEl = document.getElementById('kb-uuid');
  var uuid = uuidEl ? uuidEl.textContent : '';
  copyText(uuid).then(function(copied) {
    showToast(copied ? '已复制 UUID' : '复制失败');
  });
}

function showToast(message) {
  var toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);padding:10px 20px;border-radius:8px;background:var(--claude-foreground);color:var(--claude-background);font-size:13px;z-index:9999;animation:fadeInUp 0.3s ease;';
  document.body.appendChild(toast);
  setTimeout(function() {
    toast.remove();
  }, 2000);
}

function localizeKnowledgeBaseName(name) {
  return name === 'KG Introduction' ? '知识图谱介绍' : name;
}

function formatDateTime(value) {
  if (!value) return '-';
  var date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date).replace(/\//g, '-');
}

// ===== API Integration =====
// Check login status
if (!Auth.requireAuth()) throw new Error('Not logged in');

// Get UUID from URL
const urlParams = window.getUniGraphSearchParams();
const kgBaseUuid = urlParams.get('uuid');

// Update sidebar navigation links with UUID
function updateSidebarLinks(uuid) {
  var designLink = document.querySelector('a[data-title="设计"]');
  var buildLink = document.querySelector('a[data-title="构建"]');
  var appLink = document.querySelector('a[data-title="新建对话"]');
  if (designLink) designLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/structure';
  if (buildLink) buildLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/graph';
  if (appLink) appLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/qa';
}

// Load knowledge base detail from API
async function loadKgBaseDetail(uuid) {
  if (!uuid) {
    showToast('缺少知识库 UUID');
    return;
  }
  try {
    const res = await KgBaseAPI.kgBase.getDetail(uuid);
    if (res.code === 200 && res.data) {
      const detail = res.data;
      currentKgBaseDetail = detail;
      pendingCoverPath = null;
      var nameEl = document.getElementById('kb-name');
      var localizedName = localizeKnowledgeBaseName(detail.name || '未命名知识库');
      if (nameEl) nameEl.textContent = localizedName;
      var uuidEl = document.getElementById('kb-uuid');
      if (uuidEl) uuidEl.textContent = detail.uuid || uuid;
      var descEl = document.getElementById('kb-desc');
      if (descEl) descEl.textContent = detail.description || '暂无描述';
      var createdEl = document.getElementById('kb-created-time');
      if (createdEl) createdEl.textContent = formatDateTime(detail.created_time);
      var updatedEl = document.getElementById('kb-updated-time');
      if (updatedEl) updatedEl.textContent = formatDateTime(detail.updated_time || detail.created_time);
      applyCover(detail.cover_image);
      var schemaEl = document.getElementById('kb-schema-count');
      if (schemaEl) schemaEl.textContent = (detail.schema_graphs || []).length;
      var graphEl = document.getElementById('kb-graph-count');
      if (graphEl) graphEl.textContent = (detail.knowledge_graphs || []).length;
      var graphDetails = await Promise.all((detail.knowledge_graphs || []).map(async function(graph) {
        var graphRes = await KgBaseAPI.knowledgeGraph.getDetail(graph.uuid);
        return graphRes.code === 200 ? graphRes.data : null;
      }));
      var entityCount = 0;
      var relationshipCount = 0;
      graphDetails.filter(Boolean).forEach(function(graph) {
        entityCount += (graph.entities || []).length;
        relationshipCount += (graph.relationships || []).length;
      });
      document.getElementById('kb-entity-count').textContent = entityCount.toLocaleString();
      document.getElementById('kb-triple-count').textContent = relationshipCount.toLocaleString();
    } else {
      showToast(res.msg || '加载知识库详情失败');
    }
  } catch (err) {
    console.error('Failed to load kg base detail:', err);
    showToast('加载知识库详情失败');
  }
}

updateSidebarLinks(kgBaseUuid);
loadKgBaseDetail(kgBaseUuid);


lucide.createIcons();

  return {
    cancelEdit,
    copyUUID,
    saveEdit,
    toggleEdit,
    triggerCoverUpload,
    uploadCover,
  };
}
