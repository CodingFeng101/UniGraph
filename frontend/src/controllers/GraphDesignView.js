import { getGraphExpansionDepth } from '@/services/preferences';
import { renderGraphTooltipContent } from '@/utils/graphTooltip';

/* Generated from pages/graph-design.html; keep behavior changes in the source controller during migration. */
export function createGraphDesignViewController() {
  const { Auth, API, GraphRenderer, KgBaseAPI, TaskManager } = window;

var cyInstance = null;
var currentSchemaUuid = null;
var currentSchemaData = null;
var relationSourceUuid = null;
var relationTargetUuid = null;
var kgBaseUuid = null;
var schemaList = [];
var editingSchemaElement = null;
var pendingArchUpdatePaths = [];
var selectedElement = null;
var currentGraphStyle = 'database';

function toggleArchDropdown(id) {
  document.getElementById(id).classList.toggle('hidden');
}

function openModal(id) {
  document.getElementById(id).classList.remove('hidden');
  if (id === 'modal-entity' && !editingSchemaElement) {
    document.getElementById('entity-name').value = '';
    document.getElementById('modal-entity-attrs').innerHTML = '';
    addAttr();
    var entityTitle = document.querySelector('#modal-entity h3');
    if (entityTitle) entityTitle.textContent = '新增实体类型';
  }
  if (id === 'modal-relation') {
    populateEntityDropdowns();
    if (!editingSchemaElement) {
      document.getElementById('relation-name').value = '';
      document.getElementById('relation-desc').value = '';
      var relationTitle = document.querySelector('#modal-relation h3');
      if (relationTitle) relationTitle.textContent = '新增关系类型';
    }
  }
}

function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
  if (id === 'modal-entity' || id === 'modal-relation') editingSchemaElement = null;
}

function showTooltip(e, title, type, bodyHtml) {
  const t = document.getElementById('canvas-tooltip');
  if (!t) return;
  renderGraphTooltipContent(title, type, bodyHtml);
  t.classList.remove('hidden');
  const rect = t.parentElement.getBoundingClientRect();
  let x = e.clientX - rect.left + 15;
  let y = e.clientY - rect.top - 10;
  if (x + t.offsetWidth + 12 > rect.width) x = e.clientX - rect.left - t.offsetWidth - 15;
  if (y + t.offsetHeight + 12 > rect.height) y = rect.height - t.offsetHeight - 12;
  t.style.left = x + 'px';
  t.style.top = Math.max(12, y) + 'px';
}

function hideTooltip() {
  document.getElementById('canvas-tooltip').classList.add('hidden');
}

function addAttr() {
  var container = document.getElementById('modal-entity-attrs');
  var div = document.createElement('div');
  div.className = 'flex items-center gap-2';
  div.innerHTML = '<input type="text" placeholder="属性名称" class="flex-1 h-8 px-2.5 text-xs rounded-md border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);"><button type="button" onclick="removeAttr(this)" class="w-7 h-7 rounded flex items-center justify-center cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>';
  container.appendChild(div);
}

async function deleteArch(btn, uuid, name) {
  if (!await window.confirmAction({
    title: '删除架构',
    message: '确定要删除架构“' + name + '”吗？删除后无法恢复。',
  })) return;
  try {
    var res = await KgBaseAPI.schemaGraph.delete(uuid);
    if (res.code === 200) {
      showToast('已删除架构：' + name);
      loadSchemaGraphs();
    } else {
      showToast(res.msg || '删除架构失败');
    }
  } catch (err) {
    showToast('删除架构失败');
  }
}

async function deleteCurrentArch() {
  if (!currentSchemaUuid) {
    showToast('请先选择知识架构');
    return;
  }
  await deleteArch(null, currentSchemaUuid, currentSchemaData?.name || currentSchemaUuid);
}

function removeAttr(btn) {
  btn.parentElement.remove();
}

async function addEntity() {
  var name = document.getElementById('entity-name').value;
  if (!name) {
    showToast('请输入实体类型名称');
    return;
  }
  var attrs = [];
  document.querySelectorAll('#modal-entity-attrs input[type="text"]').forEach(function(input) {
    var val = input.value.trim();
    if (val) attrs.push(val);
  });
  try {
    var entityData = {
      name: name,
      type: name,
      attributes: JSON.stringify(attrs),
      definition: '',
      source: 'manual',
      status: 1
    };
    var isEditing = editingSchemaElement && editingSchemaElement.type === 'entity';
    var res = isEditing
      ? await KgBaseAPI.schemaEntity.update(editingSchemaElement.uuid, {
          schema_graph_uuid: currentSchemaUuid,
          data: entityData
        })
      : await KgBaseAPI.schemaEntity.create(Object.assign({
          schema_graph_uuid: currentSchemaUuid
        }, entityData));
    if (res.code === 200) {
      closeModal('modal-entity');
      showToast(isEditing ? '实体类型已更新' : '已添加实体类型: ' + name);
      loadSchemaDetail(currentSchemaUuid);
    } else {
      showToast(res.msg || '添加实体类型失败');
    }
  } catch (err) {
    showToast('添加实体类型失败');
  }
}

async function addRelation() {
  var name = document.getElementById('relation-name').value;
  if (!name) {
    showToast('请输入关系名称');
    return;
  }
  if (!relationSourceUuid || !relationTargetUuid) {
    showToast('请选择起始和目标实体类型');
    return;
  }
  var desc = document.getElementById('relation-desc').value;
  try {
    var isEditing = editingSchemaElement && editingSchemaElement.type === 'relationship';
    var relationData = {
      name: name,
      type: name,
      definition: desc,
      attributes: '',
      source: 'manual',
      status: 1
    };
    var res = isEditing
      ? await KgBaseAPI.schemaRelationship.update(editingSchemaElement.uuid, relationData)
      : await KgBaseAPI.schemaRelationship.create(Object.assign({
          schema_graph_uuid: currentSchemaUuid,
          source_entity_uuid: relationSourceUuid,
          target_entity_uuid: relationTargetUuid
        }, relationData));
    if (res.code === 200) {
      closeModal('modal-relation');
      showToast(isEditing ? '关系类型已更新' : '已添加关系: ' + name);
      loadSchemaDetail(currentSchemaUuid);
    } else {
      showToast(res.msg || '添加关系失败');
    }
  } catch (err) {
    showToast('添加关系失败');
  }
}

async function exportArchitecture() {
  if (!currentSchemaUuid) {
    showToast('未加载架构');
    return;
  }
  showToast('正在导出架构 JSON...');
  try {
    var res = await KgBaseAPI.schemaGraph.export(currentSchemaUuid);
    if (res.code === 200 && res.data) {
      var blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = ((currentSchemaData && currentSchemaData.name) || 'schema') + '.json';
      a.click();
      URL.revokeObjectURL(url);
      showToast('架构已导出');
    } else {
      showToast(res.msg || '导出失败');
    }
  } catch (err) {
    showToast('导出失败');
  }
}

function changeStyle(style) {
  if (!cyInstance) return;
  var needsRendererSwitch = style === 'load' || cyInstance._engine === 'vis-network';
  currentGraphStyle = style;
  if (needsRendererSwitch && currentSchemaData) {
    renderSchemaGraph(currentSchemaData);
  } else {
    GraphRenderer.applyStyle(cyInstance, style);
  }
  document.querySelectorAll('[data-graph-style]').forEach(function(button) {
    var active = button.dataset.graphStyle === style;
    button.style.background = active ? 'var(--claude-primary)' : 'transparent';
    button.style.color = active ? 'var(--claude-primary-foreground)' : 'var(--claude-muted-foreground)';
  });
  showToast('已切换图谱样式');
}

function zoomIn() {
  if (cyInstance) GraphRenderer.zoom(cyInstance, 0.2);
}

function zoomOut() {
  if (cyInstance) GraphRenderer.zoom(cyInstance, -0.2);
}

function resetZoom() {
  if (cyInstance) GraphRenderer.fit(cyInstance);
}

function filterGraph(shouldFocus) {
  if (!cyInstance) return;
  var input = document.querySelector('#app-main input[id="search-input"]');
  var search = input ? input.value.toLowerCase().trim() : '';
  if (GraphRenderer.filter(cyInstance, search, shouldFocus)) return;
  var elements = cyInstance.elements();
  elements.removeClass('search-match search-dimmed');
  if (!search) {
    elements.style('opacity', 1);
    cyInstance.nodes().removeStyle('border-color border-width shadow-blur shadow-color shadow-opacity');
    cyInstance.edges().removeStyle('line-color target-arrow-color width text-background-color text-background-opacity color');
    return;
  }
  var matches = elements.filter(function(element) {
    var label = String(element.data('label') || element.data('name') || element.data('type') || '').toLowerCase();
    return label.includes(search);
  });
  elements.style('opacity', 0.16);
  matches.style('opacity', 1);
  matches.nodes().style({
    'border-color': '#c96442',
    'border-width': 4,
    'shadow-blur': 18,
    'shadow-color': '#c96442',
    'shadow-opacity': 0.42
  });
  matches.edges().style({
    'line-color': '#c96442',
    'target-arrow-color': '#c96442',
    'width': 4,
    'color': '#a0502f',
    'text-background-color': '#ffffff',
    'text-background-opacity': 1
  });
  if (shouldFocus && matches.length) {
    cyInstance.animate({
      center: { eles: matches },
      zoom: Math.min(Math.max(cyInstance.zoom(), 0.75), 1.25),
      duration: 280
    });
  }
}

function setCreateArchMode(mode) {
  var isDocument = mode !== 'json';
  document.getElementById('modal-new-arch')?.setAttribute('data-create-mode', isDocument ? 'document' : 'json');
  document.getElementById('create-arch-document-panel')?.classList.toggle('hidden', !isDocument);
  document.getElementById('create-arch-json-panel')?.classList.toggle('hidden', isDocument);
  var docTab = document.getElementById('create-arch-document-tab');
  var jsonTab = document.getElementById('create-arch-json-tab');
  if (docTab) {
    docTab.style.background = isDocument ? 'var(--claude-card)' : 'transparent';
    docTab.style.borderColor = isDocument ? 'var(--claude-border)' : 'transparent';
    docTab.style.color = isDocument ? 'var(--claude-foreground)' : 'var(--claude-muted-foreground)';
  }
  if (jsonTab) {
    jsonTab.style.background = isDocument ? 'transparent' : 'var(--claude-card)';
    jsonTab.style.borderColor = isDocument ? 'transparent' : 'var(--claude-border)';
    jsonTab.style.color = isDocument ? 'var(--claude-muted-foreground)' : 'var(--claude-foreground)';
  }
}

function toggleDropdown(id) {
  var dropdown = document.getElementById(id);
  document.querySelectorAll('[id$="-dropdown"]').forEach(function(el) {
    if (el !== dropdown) el.classList.add('hidden');
  });
  dropdown.classList.toggle('hidden');
}

function selectRelationSource(el, uuid, name) {
  relationSourceUuid = uuid;
  document.getElementById('relation-source-value').textContent = name;
  document.querySelectorAll('#relation-source-dropdown > div').forEach(function(item) {
    item.style.background = '';
    var span = item.querySelector('span');
    if (span) item.innerHTML = '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + span.textContent + '</span>';
  });
  el.style.background = 'var(--claude-accent)';
  el.innerHTML = '<div class="flex items-center justify-between"><span class="text-xs font-medium" style="color:var(--claude-foreground);">' + name + '</span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
  document.getElementById('relation-source-dropdown').classList.add('hidden');
}

function selectRelationTarget(el, uuid, name) {
  relationTargetUuid = uuid;
  document.getElementById('relation-target-value').textContent = name;
  document.querySelectorAll('#relation-target-dropdown > div').forEach(function(item) {
    item.style.background = '';
    var span = item.querySelector('span');
    if (span) item.innerHTML = '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + span.textContent + '</span>';
  });
  el.style.background = 'var(--claude-accent)';
  el.innerHTML = '<div class="flex items-center justify-between"><span class="text-xs font-medium" style="color:var(--claude-foreground);">' + name + '</span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
  document.getElementById('relation-target-dropdown').classList.add('hidden');
}

function showToast(message) {
  window.showToast(message);
}

document.addEventListener('click', function(e) {
  var wrapper = document.getElementById('arch-dropdown-wrapper-top');
  var dropdown = document.getElementById('arch-dropdown-top');
  if (wrapper && dropdown && !wrapper.contains(e.target)) {
    dropdown.classList.add('hidden');
  }
  document.querySelectorAll('[id$="-dropdown"]').forEach(function(el) {
    var wrapper = el.parentElement;
    if (wrapper && !wrapper.contains(e.target)) {
      el.classList.add('hidden');
    }
  });
});

setInterval(function() {
  var bar = document.getElementById('progress-bar');
  var text = document.getElementById('progress-text');
  if (bar && text) {
    var width = parseInt(bar.style.width);
    if (width < 100) {
      width += Math.random() * 5;
      if (width > 100) width = 100;
      bar.style.width = width + '%';
      text.textContent = Math.round(width) + '%';
    }
  }
}, 1000);

// ===== API Integration =====
// Check login status
if (!Auth.requireAuth()) throw new Error('Not logged in');

// Get UUID from URL
(function() {
  var urlParams = window.getUniGraphSearchParams();
  kgBaseUuid = urlParams.get('uuid');
  if (!kgBaseUuid) {
    showToast('缺少知识库 UUID');
    return;
  }
  // Clear demo SVG content while loading
  var graphRoot = document.getElementById('graph-root');
  if (graphRoot) graphRoot.innerHTML = '';
  updateSidebarLinks(kgBaseUuid);
  loadSchemaGraphs();
})();

// Update sidebar navigation links with UUID
function updateSidebarLinks(uuid) {
  var infoLink = document.querySelector('a[data-title="信息"]');
  var buildLink = document.querySelector('a[data-title="构建"]');
  var appLink = document.querySelector('a[data-title="新建对话"]');
  var designLink = document.querySelector('a[data-title="设计"]');
  if (infoLink) infoLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/info';
  if (buildLink) buildLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/graph';
  if (appLink) appLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/qa';
  if (designLink) designLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/structure';
}

// Load all schema graphs for the knowledge base
async function loadSchemaGraphs() {
  if (!kgBaseUuid) return;
  try {
    var res = await KgBaseAPI.schemaGraph.getAll(kgBaseUuid);
    if (res.code === 200 && res.data) {
      schemaList = Array.isArray(res.data) ? res.data : [res.data];
      populateArchDropdown(schemaList);
      if (schemaList.length >= 1) {
        loadSchemaDetail(schemaList[0].uuid);
      } else {
        showToast('暂无架构图谱');
      }
    } else {
      showToast(res.msg || '加载架构列表失败');
    }
  } catch (err) {
    showToast('加载架构列表失败');
  }
}

// Populate architecture dropdown in header
function populateArchDropdown(schemas) {
  var dropdown = document.getElementById('arch-dropdown-top');
  if (!dropdown) return;
  dropdown.innerHTML = '';
  schemas.forEach(function(schema, idx) {
    var isActive = idx === 0;
    var item = document.createElement('div');
    item.className = 'px-3 py-2 flex items-center justify-between transition-colors hover:opacity-80 cursor-pointer group';
    if (isActive) item.style.background = 'var(--claude-accent)';
    item.onclick = function() { loadSchemaDetail(schema.uuid); };
    var dotStyle = isActive ? 'background:var(--claude-success-500);' : 'background:var(--claude-muted-foreground);opacity:0.4;';
    var nameStyle = isActive ? 'color:var(--claude-foreground);' : 'color:var(--claude-muted-foreground);';
    var nameClass = isActive ? 'text-xs font-medium truncate' : 'text-xs truncate';
    item.innerHTML = '<div class="flex items-center gap-2 min-w-0">' +
      '<span class="w-1.5 h-1.5 rounded-full shrink-0" style="' + dotStyle + '"></span>' +
      '<span class="' + nameClass + '" style="' + nameStyle + '">' + (schema.name || '未命名架构') + '</span>' +
      '</div>';
    var delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className = 'shrink-0 w-6 h-6 rounded flex items-center justify-center cursor-pointer transition-opacity hover:opacity-70';
    delBtn.style.cssText = 'background:transparent;border:none;color:var(--claude-destructive);';
    delBtn.setAttribute('aria-label', '删除架构');
    delBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>';
    delBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      deleteArch(this, schema.uuid, schema.name || '未命名架构');
    });
    item.appendChild(delBtn);
    dropdown.appendChild(item);
  });
}

// Load schema graph detail
async function loadSchemaDetail(schemaUuid) {
  if (!schemaUuid) return;
  currentSchemaUuid = schemaUuid;
  try {
    var res = await KgBaseAPI.schemaGraph.getDetail(schemaUuid);
    if (res.code === 200 && res.data) {
      currentSchemaData = res.data;
      // Update header architecture name
      var archNameSpan = document.querySelector('#arch-dropdown-wrapper-top span.truncate');
      if (archNameSpan) archNameSpan.textContent = currentSchemaData.name || '未命名架构';
      renderSchemaGraph(currentSchemaData);
      populateArchSuggestionForm(currentSchemaData);
    } else {
      showToast(res.msg || '加载架构详情失败');
    }
  } catch (err) {
    showToast('加载架构详情失败');
  }
}

function resolveSchemaEntityName(uuid, preferredName) {
  var explicitName = String(preferredName || '').trim();
  if (explicitName && explicitName !== uuid) return explicitName;
  var entity = ((currentSchemaData && currentSchemaData.entities) || []).find(function(item) {
    return item.uuid === uuid;
  });
  return entity && entity.name ? entity.name : '未知实体';
}

// Render schema graph using GraphRenderer (Cytoscape.js)
function renderSchemaGraph(detail) {
  // Schema graph: entity type's name is used as the grouping type
  var entities = (detail.entities || []).map(function(e) {
    return Object.assign({}, e, { type: e.name });
  });
  var relationships = detail.relationships || [];

  // Convert SVG canvas to div for Cytoscape
  var svgCanvas = document.getElementById('graph-canvas');
  if (svgCanvas && svgCanvas.tagName.toUpperCase() === 'SVG') {
    var divCanvas = document.createElement('div');
    divCanvas.id = 'graph-canvas';
    divCanvas.style.width = '100%';
    divCanvas.style.height = '100%';
    divCanvas.style.background = 'var(--claude-background)';
    svgCanvas.parentNode.replaceChild(divCanvas, svgCanvas);
  }

  // Destroy existing Cytoscape instance
  if (cyInstance) {
    cyInstance.destroy();
    cyInstance = null;
  }

  cyInstance = GraphRenderer.init('graph-canvas', entities, relationships, {
    mode: currentGraphStyle,
    onNodeClick: function(data) {
      selectedElement = { type: 'entity', uuid: data.id, data: data };
      var attrs = data.attributes;
      var attrStr = '';
      if (Array.isArray(attrs)) {
        attrStr = attrs.join(', ');
      } else if (attrs && typeof attrs === 'object') {
        attrStr = Object.keys(attrs).join(', ');
      } else if (attrs) {
        attrStr = String(attrs);
      }
      showTooltipByPos(data.label || '实体类型', '实体类型', '属性: ' + attrStr);
    },
    onNodeDoubleClick: function(data) {
      if (currentGraphStyle === 'load' && cyInstance && cyInstance.expandNeighborhood) {
        cyInstance.expandNeighborhood(data.id, getGraphExpansionDepth());
      }
    },
    onEdgeClick: function(data) {
      selectedElement = { type: 'relationship', uuid: data.id, data: data };
      var raw = data.raw || {};
      var sourceName = resolveSchemaEntityName(raw.source_entity_uuid, raw.source_entity_name);
      var targetName = resolveSchemaEntityName(raw.target_entity_uuid, raw.target_entity_name);
      showTooltipByPos(data.label || '关系类型', '关系类型',
        '起始: ' + sourceName + '<br>目标: ' + targetName);
    },
    onNodeHover: function(data, node, position) {
      selectedElement = { type: 'entity', uuid: data.id, data: data };
      var attrs = data.attributes && typeof data.attributes === 'object'
        ? Object.keys(data.attributes).join(', ')
        : String(data.attributes || '');
      showTooltipByPos(data.label || '实体类型', '实体类型', '属性: ' + attrs, position);
    },
    onEdgeHover: function(data, edge, position) {
      var raw = data.raw || {};
      selectedElement = { type: 'relationship', uuid: data.id, data: data };
      showTooltipByPos(data.label || '关系类型', '关系类型',
        '起始: ' + resolveSchemaEntityName(raw.source_entity_uuid, raw.source_entity_name) + '<br>目标: ' +
        resolveSchemaEntityName(raw.target_entity_uuid, raw.target_entity_name), position);
    },
    onElementLeave: scheduleTooltipHide,
    onCanvasClick: function() {
      hideTooltip();
      selectedElement = null;
    }
  });
}

// Show tooltip at top-center of graph area (for Cytoscape node/edge clicks)
function showTooltipByPos(title, type, bodyHtml, position) {
  var t = document.getElementById('canvas-tooltip');
  if (!t) return;
  renderGraphTooltipContent(title, type, bodyHtml);
  t.classList.remove('hidden');
  var parent = t.parentElement;
  var x = position ? position.x + 16 : parent.clientWidth / 2 - t.offsetWidth / 2;
  var y = position ? position.y - 18 : 20;
  if (x + t.offsetWidth + 12 > parent.clientWidth) x = Math.max(12, x - t.offsetWidth - 32);
  if (y + t.offsetHeight > parent.clientHeight) y = Math.max(12, parent.clientHeight - t.offsetHeight - 12);
  t.style.left = Math.max(12, x) + 'px';
  t.style.top = Math.max(12, y) + 'px';
}

function scheduleTooltipHide() {
  window.setTimeout(function() {
    var tooltip = document.getElementById('canvas-tooltip');
    if (tooltip && !tooltip.matches(':hover')) hideTooltip();
  }, 140);
}

// Delete selected element (entity or relationship)
async function deleteSelectedElement() {
  if (!selectedElement) {
    showToast('请先选择要删除的元素');
    return;
  }
  if (!await window.confirmAction({
    title: '删除设计元素',
    message: '确定要删除“' + (selectedElement.data.label || '') + '”吗？',
  })) return;
  try {
    var response = selectedElement.type === 'entity'
      ? await KgBaseAPI.schemaEntity.delete(selectedElement.uuid)
      : await KgBaseAPI.schemaRelationship.delete(selectedElement.uuid);
    if (response.code !== 200) throw new Error(response.msg || '删除失败');
    selectedElement = null;
    hideTooltip();
    await loadSchemaDetail(currentSchemaUuid);
    showToast('元素已删除');
  } catch (error) {
    showToast(error.message || '删除失败');
  }
}

function parseAttributes(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === 'object') return Object.keys(value);
  try {
    var parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : Object.keys(parsed || {});
  } catch (error) {
    return String(value).split(',').map(function(item) { return item.trim(); }).filter(Boolean);
  }
}

function editSelectedElement() {
  if (!selectedElement) {
    showToast('请先选择要编辑的元素');
    return;
  }
  editingSchemaElement = {
    type: selectedElement.type,
    uuid: selectedElement.uuid,
    raw: selectedElement.data.raw || selectedElement.data
  };
  var raw = editingSchemaElement.raw;
  if (editingSchemaElement.type === 'entity') {
    openModal('modal-entity');
    document.getElementById('entity-name').value = raw.name || selectedElement.data.label || '';
    var attrs = parseAttributes(raw.attributes);
    var container = document.getElementById('modal-entity-attrs');
    container.innerHTML = '';
    attrs.forEach(function(attribute) {
      addAttr();
      container.lastElementChild.querySelector('input').value = attribute;
    });
    if (!container.children.length) addAttr();
    document.querySelector('#modal-entity h3').textContent = '编辑实体类型';
    return;
  }

  openModal('modal-relation');
  document.getElementById('relation-name').value = raw.name || selectedElement.data.label || '';
  document.getElementById('relation-desc').value = raw.definition || '';
  relationSourceUuid = raw.source_entity_uuid;
  relationTargetUuid = raw.target_entity_uuid;
  var sourceEntity = (currentSchemaData.entities || []).find(function(item) { return item.uuid === relationSourceUuid; });
  var targetEntity = (currentSchemaData.entities || []).find(function(item) { return item.uuid === relationTargetUuid; });
  var sourceItem = sourceEntity && Array.from(document.querySelectorAll('#relation-source-dropdown > div'))
    .find(function(item) { return item.textContent.trim() === sourceEntity.name; });
  var targetItem = targetEntity && Array.from(document.querySelectorAll('#relation-target-dropdown > div'))
    .find(function(item) { return item.textContent.trim() === targetEntity.name; });
  if (sourceItem) selectRelationSource(sourceItem, sourceEntity.uuid, sourceEntity.name);
  if (targetItem) selectRelationTarget(targetItem, targetEntity.uuid, targetEntity.name);
  document.querySelector('#modal-relation h3').textContent = '编辑关系类型';
}

// Populate entity dropdowns in relation modal from loaded entity types
function populateEntityDropdowns() {
  var entities = (currentSchemaData && currentSchemaData.entities) || [];
  var sourceDropdown = document.getElementById('relation-source-dropdown');
  var targetDropdown = document.getElementById('relation-target-dropdown');
  if (!sourceDropdown || !targetDropdown) return;

  function buildOptions(dropdown, isSource) {
    dropdown.innerHTML = '';
    if (entities.length === 0) {
      var empty = document.createElement('div');
      empty.className = 'px-3 py-2';
      empty.innerHTML = '<span class="text-xs" style="color:var(--claude-muted-foreground);">暂无实体类型</span>';
      dropdown.appendChild(empty);
      return;
    }
    var defaultIdx = isSource ? 0 : (entities.length > 1 ? 1 : 0);
    entities.forEach(function(entity, idx) {
      var isDefault = idx === defaultIdx;
      var item = document.createElement('div');
      item.className = 'px-3 py-2 cursor-pointer transition-colors hover:opacity-80';
      if (isDefault) item.style.background = 'var(--claude-accent)';
      item.onclick = function() {
        if (isSource) {
          selectRelationSource(this, entity.uuid, entity.name);
        } else {
          selectRelationTarget(this, entity.uuid, entity.name);
        }
      };
      if (isDefault) {
        item.innerHTML = '<div class="flex items-center justify-between"><span class="text-xs font-medium" style="color:var(--claude-foreground);">' + entity.name + '</span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
      } else {
        item.innerHTML = '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + entity.name + '</span>';
      }
      dropdown.appendChild(item);
    });
    // Set default selection
    if (entities.length > 0) {
      var defaultEntity = entities[defaultIdx];
      if (isSource) {
        relationSourceUuid = defaultEntity.uuid;
        var sourceVal = document.getElementById('relation-source-value');
        if (sourceVal) sourceVal.textContent = defaultEntity.name;
      } else {
        relationTargetUuid = defaultEntity.uuid;
        var targetVal = document.getElementById('relation-target-value');
        if (targetVal) targetVal.textContent = defaultEntity.name;
      }
    }
  }

  buildOptions(sourceDropdown, true);
  buildOptions(targetDropdown, false);
}

// Generate architecture suggestion via export API
// Save architecture suggestion (modify_info + modify_suggestion)
// Upload architecture file
function parseJsonObject(value, fallback) {
  if (!value) return fallback;
  if (typeof value === 'object') return value;
  try {
    return JSON.parse(value);
  } catch (error) {
    return fallback;
  }
}

function appendSuggestionInput(group, value) {
  if (!group) return;
  var wrapper = document.createElement('span');
  wrapper.className = 'inline-flex items-center gap-1 px-2 py-1 rounded-md';
  wrapper.style.cssText = 'background:var(--claude-secondary);border:1px solid var(--claude-border);';
  var input = document.createElement('input');
  input.type = 'text';
  input.value = value || '';
  input.className = 'w-24 bg-transparent border-none outline-none text-[11px]';
  input.style.color = 'var(--claude-foreground)';
  var remove = document.createElement('button');
  remove.type = 'button';
  remove.textContent = '×';
  remove.className = 'cursor-pointer';
  remove.style.cssText = 'background:none;border:none;color:var(--claude-muted-foreground);';
  remove.onclick = function() { wrapper.remove(); };
  wrapper.appendChild(input);
  wrapper.appendChild(remove);
  group.appendChild(wrapper);
}

function populateArchSuggestionForm(detail) {
  var modal = document.getElementById('modal-update-arch');
  if (!modal) return;
  var modifyInfo = parseJsonObject(detail.modify_info, {});
  var groups = modal.querySelectorAll('.flex.flex-wrap.gap-1\\.5');
  var values = [
    modifyInfo.add_entity || modifyInfo.expected_entity_types || [],
    modifyInfo.del_entity || modifyInfo.unexpected_entity_types || []
  ];
  groups.forEach(function(group, index) {
    group.innerHTML = '';
    (values[index] || []).forEach(function(value) {
      appendSuggestionInput(group, value);
    });
  });
  var textarea = modal.querySelector('textarea');
  if (textarea) textarea.value = detail.modify_suggestion || '';
}

function addSuggestionTag(groupIndex) {
  var modal = document.getElementById('modal-update-arch');
  var groups = modal ? modal.querySelectorAll('.flex.flex-wrap.gap-1\\.5') : [];
  appendSuggestionInput(groups[groupIndex], '');
  var lastInput = groups[groupIndex] && groups[groupIndex].querySelector('span:last-child input');
  if (lastInput) lastInput.focus();
}

function collectSuggestionInfo() {
  var modal = document.getElementById('modal-update-arch');
  var groups = modal ? modal.querySelectorAll('.flex.flex-wrap.gap-1\\.5') : [];
  var collect = function(group) {
    return Array.from(group ? group.querySelectorAll('input[type="text"]') : [])
      .map(function(input) { return input.value.trim(); })
      .filter(Boolean);
  };
  return { add_entity: collect(groups[0]), del_entity: collect(groups[1]) };
}

async function generateSuggestion() {
  if (!currentSchemaUuid) {
    showToast('请先选择知识架构');
    return;
  }
  try {
    var task = await TaskManager.submit(
      'schema_graph.update_schema_graph_suggestion',
      '生成架构建议',
      currentSchemaData.name || currentSchemaUuid,
      { uuid: currentSchemaUuid, user_token: Auth.getToken() }
    );
    await task.completion;
    await loadSchemaDetail(currentSchemaUuid);
  } catch (error) {
    showToast(error.message || '生成建议失败');
  }
}

async function saveArchSuggestion() {
  if (!currentSchemaUuid) {
    showToast('请先选择知识架构');
    return;
  }
  var modal = document.getElementById('modal-update-arch');
  var textarea = modal ? modal.querySelector('textarea') : null;
  try {
    var response = await KgBaseAPI.schemaGraph.updateDetail(currentSchemaUuid, {
      modify_info: JSON.stringify(collectSuggestionInfo()),
      modify_suggestion: textarea ? textarea.value : ''
    });
    if (response.code !== 200) throw new Error(response.msg || '保存失败');
    modal.classList.add('hidden');
    await loadSchemaDetail(currentSchemaUuid);
    showToast('已保存');
  } catch (error) {
    showToast(error.message || '保存失败');
  }
}

async function uploadFiles(files) {
  var paths = [];
  for (var index = 0; index < files.length; index += 1) {
    var response = await API.uploadFile(files[index]);
    if (response.code !== 200 || !response.data || !response.data.url) {
      throw new Error(response.msg || '文件上传失败');
    }
    paths.push(response.data.url);
  }
  return paths;
}

function triggerCreateArchFiles() {
  document.getElementById('create-arch-files').click();
}

function handleCreateArchFiles(input) {
  var label = document.getElementById('create-arch-files-label');
  if (label) label.textContent = input.files && input.files.length
    ? Array.from(input.files).map(function(file) { return file.name; }).join('、')
    : '上传 PDF / Word / TXT 文档';
}

async function submitCreateArch() {
  if (document.getElementById('modal-new-arch')?.getAttribute('data-create-mode') === 'json') {
    return handleImportArchFile(document.getElementById('import-arch-file'), true);
  }
  var input = document.getElementById('create-arch-files');
  var name = document.getElementById('create-arch-name')?.value.trim() || '';
  var aim = document.getElementById('create-arch-aim')?.value.trim() || '';
  if (!name) return showToast('请输入架构名称');
  if (!input.files || !input.files.length) return showToast('请上传构建文档');
  try {
    var filePaths = await uploadFiles(input.files);
    document.getElementById('modal-new-arch').classList.add('hidden');
    var task = await TaskManager.submit(
      'schema_graph.create_schema_graph',
      '创建知识架构',
      name,
      {
        user_token: Auth.getToken(),
        obj_data: {
          file_paths: filePaths,
          data: { kg_base_uuid: kgBaseUuid, name: name, aim: aim }
        }
      }
    );
    await task.completion;
    await loadSchemaGraphs();
  } catch (error) {
    showToast(error.message || '创建知识架构失败');
  } finally {
    input.value = '';
    handleCreateArchFiles(input);
  }
}

function triggerImportArchFile() {
  document.getElementById('import-arch-file').click();
}

async function handleImportArchFile(input, shouldSubmit) {
  if (!input.files || !input.files.length) return;
  var label = document.getElementById('import-arch-file-label');
  if (label) label.textContent = input.files[0].name;
  if (!shouldSubmit) return;
  try {
    var filePaths = await uploadFiles(input.files);
    var response = await KgBaseAPI.schemaGraph.import({
      file_paths: filePaths,
      data: {
        kg_base_uuid: kgBaseUuid,
        name: input.files[0].name.replace(/\.json$/i, ''),
        aim: '',
        modify_info: '',
        modify_suggestion: ''
      }
    });
    if (response.code !== 200) throw new Error(response.msg || '导入知识架构失败');
    document.getElementById('modal-new-arch').classList.add('hidden');
    await loadSchemaGraphs();
    showToast('知识架构已导入');
  } catch (error) {
    showToast(error.message || '导入知识架构失败');
  } finally {
    input.value = '';
    if (label) label.textContent = '选择 JSON 文件';
  }
}

async function uploadArchFiles(files) {
  if (!files || !files.length) return;
  try {
    pendingArchUpdatePaths = await uploadFiles(files);
    showToast('已上传 ' + pendingArchUpdatePaths.length + ' 个文件');
  } catch (error) {
    pendingArchUpdatePaths = [];
    showToast(error.message || '文件上传失败');
  }
}

async function submitArchUpdate() {
  if (!currentSchemaUuid) {
    showToast('请先选择知识架构');
    return;
  }
  if (!pendingArchUpdatePaths.length) {
    showToast('请先上传更新文档');
    return;
  }
  var modal = document.getElementById('modal-update-arch');
  var textarea = modal.querySelector('textarea');
  try {
    var task = await TaskManager.submit(
      'schema_graph.update_schema_graph',
      '更新知识架构',
      currentSchemaData.name || currentSchemaUuid,
      {
        uuid: currentSchemaUuid,
        user_token: Auth.getToken(),
        obj_data: {
          file_paths: pendingArchUpdatePaths,
          data: {
            modify_suggestion: textarea ? textarea.value : '',
            modify_info: JSON.stringify(collectSuggestionInfo())
          }
        }
      }
    );
    modal.classList.add('hidden');
    pendingArchUpdatePaths = [];
    await task.completion;
    await loadSchemaDetail(currentSchemaUuid);
  } catch (error) {
    showToast(error.message || '更新知识架构失败');
  }
}

lucide.createIcons();

  window.removeAttr = removeAttr;

  return {
    addAttr,
    addEntity,
    addRelation,
    addSuggestionTag,
    changeStyle,
    closeModal,
    deleteArch,
    deleteCurrentArch,
    deleteSelectedElement,
    editSelectedElement,
    exportArchitecture,
    filterGraph,
    generateSuggestion,
    handleCreateArchFiles,
    handleImportArchFile,
    hideTooltip,
    openModal,
    removeAttr,
    resetZoom,
    saveArchSuggestion,
    setCreateArchMode,
    selectRelationSource,
    selectRelationTarget,
    showTooltip,
    submitArchUpdate,
    submitCreateArch,
    toggleArchDropdown,
    toggleDropdown,
    triggerCreateArchFiles,
    triggerImportArchFile,
    uploadArchFiles,
    zoomIn,
    zoomOut,
  };
}
