import { getGraphExpansionDepth } from '@/services/preferences';
import { renderGraphTooltipContent } from '@/utils/graphTooltip';
import { createSchemaDocumentController } from '@/features/schema/schema-documents';

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
      relationSourceUuid = null;
      relationTargetUuid = null;
      document.getElementById('relation-source-input').value = '';
      document.getElementById('relation-target-input').value = '';
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
    showToast(err.message || '导出失败');
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

function selectRelationSource(uuid, name) {
  relationSourceUuid = uuid;
  document.getElementById('relation-source-input').value = name;
  document.getElementById('relation-source-dropdown').classList.add('hidden');
}

function selectRelationTarget(uuid, name) {
  relationTargetUuid = uuid;
  document.getElementById('relation-target-input').value = name;
  document.getElementById('relation-target-dropdown').classList.add('hidden');
}

function filterRelationEntityList(kind, preserveSelection) {
  var input = document.getElementById('relation-' + kind + '-input');
  var dropdown = document.getElementById('relation-' + kind + '-dropdown');
  if (!input || !dropdown) return;
  if (!preserveSelection) {
    if (kind === 'source') relationSourceUuid = null;
    else relationTargetUuid = null;
  }
  var query = input.value.trim().toLowerCase();
  var visibleCount = 0;
  dropdown.querySelectorAll('button[data-entity-name]').forEach(function(button) {
    var visible = button.dataset.entityName.toLowerCase().includes(query);
    button.classList.toggle('hidden', !visible);
    if (visible) visibleCount += 1;
  });
  dropdown.querySelector('[data-empty-filter]')?.classList.toggle('hidden', visibleCount > 0);
  dropdown.classList.remove('hidden');
}

function showRelationEntityList(kind) {
  document.querySelectorAll('#relation-source-dropdown,#relation-target-dropdown').forEach(function(dropdown) {
    if (dropdown.id !== 'relation-' + kind + '-dropdown') dropdown.classList.add('hidden');
  });
  filterRelationEntityList(kind, true);
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
async function loadSchemaGraphs(preferredSchema) {
  if (!kgBaseUuid) return;
  try {
    var res = await KgBaseAPI.schemaGraph.getAll(kgBaseUuid);
    if (res.code === 200 && res.data) {
      schemaList = Array.isArray(res.data) ? res.data : [res.data];
      if (schemaList.length >= 1) {
        var preferredUuid = typeof preferredSchema === 'string' ? preferredSchema : preferredSchema?.uuid;
        var preferredName = typeof preferredSchema === 'object' ? preferredSchema?.name : '';
        var selectedSchema = schemaList.find(function(schema) {
          return (preferredUuid && schema.uuid === preferredUuid) || (preferredName && schema.name === preferredName);
        }) || schemaList.find(function(schema) {
          return schema.uuid === currentSchemaUuid;
        }) || schemaList[0];
        populateArchDropdown(schemaList);
        await loadSchemaDetail(selectedSchema.uuid);
      } else {
        populateArchDropdown(schemaList);
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
  var trigger = document.getElementById('arch-dropdown-trigger');
  var label = trigger?.querySelector('span.truncate');
  var hasSchemas = schemas.length > 0;
  if (trigger) {
    trigger.disabled = !hasSchemas;
    trigger.style.borderColor = hasSchemas ? 'var(--claude-brand-500)' : 'var(--claude-border)';
  }
  if (label) {
    label.textContent = hasSchemas ? (schemas[0].name || '未命名架构') : '暂无知识架构';
    label.style.color = hasSchemas ? 'var(--claude-foreground)' : 'var(--claude-muted-foreground)';
  }
  if (!hasSchemas) dropdown.classList.add('hidden');
  dropdown.innerHTML = '';
  schemas.forEach(function(schema) {
    var item = document.createElement('div');
    item.className = 'px-3 py-2 flex items-center justify-between transition-colors hover:bg-[var(--claude-secondary)] cursor-pointer group';
    item.onclick = function() { loadSchemaDetail(schema.uuid); };
    item.innerHTML = '<div class="flex items-center min-w-0">' +
      '<span class="text-xs truncate" style="color:var(--claude-foreground);">' + (schema.name || '未命名架构') + '</span>' +
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

function formatSchemaAttributes(value) {
  if (Array.isArray(value)) return value.join(', ');
  if (value && typeof value === 'object') return Object.keys(value).join(', ');
  return String(value || '');
}

function formatSchemaSources(value) {
  function collect(source) {
    if (source === null || source === undefined || source === '') return [];
    if (Array.isArray(source)) return source.flatMap(collect);
    if (typeof source === 'object') {
      return Object.entries(source).flatMap(function(entry) {
        var key = String(entry[0] || '').trim();
        var detail = collect(entry[1]).join('；');
        if (key && detail) return [key + '：' + detail];
        return key ? [key] : (detail ? [detail] : []);
      });
    }
    if (typeof source === 'string') {
      try {
        var parsed = JSON.parse(source);
        if (parsed !== source) return collect(parsed);
      } catch (error) {
        // Plain source text does not need JSON parsing.
      }
    }
    var text = String(source).trim();
    return text ? [text] : [];
  }

  return Array.from(new Set(collect(value)));
}

function escapeTooltipText(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function appendSchemaSource(bodyHtml, raw) {
  var sources = formatSchemaSources(raw?.source);
  if (!sources.length) return bodyHtml;
  return bodyHtml + sources.map(function(source, index) {
    return '<br>来源 ' + (index + 1) + ': ' + escapeTooltipText(source);
  }).join('');
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
      var attrStr = formatSchemaAttributes(data.attributes);
      showTooltipByPos(
        data.label || '实体类型',
        '实体类型',
        appendSchemaSource('属性: ' + attrStr, data.raw || data)
      );
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
      showTooltipByPos(data.label || '关系类型', '关系类型', appendSchemaSource(
        '起始: ' + sourceName + '<br>目标: ' + targetName,
        raw
      ));
    },
    onNodeHover: function(data, node, position) {
      selectedElement = { type: 'entity', uuid: data.id, data: data };
      var attrs = formatSchemaAttributes(data.attributes);
      showTooltipByPos(
        data.label || '实体类型',
        '实体类型',
        appendSchemaSource('属性: ' + attrs, data.raw || data),
        position
      );
    },
    onEdgeHover: function(data, edge, position) {
      var raw = data.raw || {};
      selectedElement = { type: 'relationship', uuid: data.id, data: data };
      showTooltipByPos(data.label || '关系类型', '关系类型', appendSchemaSource(
        '起始: ' + resolveSchemaEntityName(raw.source_entity_uuid, raw.source_entity_name) + '<br>目标: ' +
        resolveSchemaEntityName(raw.target_entity_uuid, raw.target_entity_name),
        raw
      ), position);
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
  if (sourceEntity) selectRelationSource(sourceEntity.uuid, sourceEntity.name);
  if (targetEntity) selectRelationTarget(targetEntity.uuid, targetEntity.name);
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
    entities.forEach(function(entity) {
      var item = document.createElement('button');
      item.type = 'button';
      item.dataset.entityName = entity.name || '';
      item.className = 'block w-full px-3 py-2 text-left cursor-pointer transition-colors hover:bg-[var(--claude-secondary)]';
      item.style.cssText = 'background:transparent;border:none;color:var(--claude-foreground);';
      item.onclick = function() {
        if (isSource) {
          selectRelationSource(entity.uuid, entity.name);
        } else {
          selectRelationTarget(entity.uuid, entity.name);
        }
      };
      item.textContent = entity.name;
      dropdown.appendChild(item);
    });
    var emptyFilter = document.createElement('div');
    emptyFilter.dataset.emptyFilter = 'true';
    emptyFilter.className = 'hidden px-3 py-2 text-xs';
    emptyFilter.style.color = 'var(--claude-muted-foreground)';
    emptyFilter.textContent = '没有匹配的实体类型';
    dropdown.appendChild(emptyFilter);
  }

  buildOptions(sourceDropdown, true);
  buildOptions(targetDropdown, false);
}

const {
  addSuggestionTag,
  generateSuggestion,
  handleCreateArchFiles,
  handleImportArchFile,
  populateArchSuggestionForm,
  saveArchSuggestion,
  submitArchUpdate,
  submitCreateArch,
  triggerCreateArchFiles,
  triggerImportArchFile,
  uploadArchFiles,
} = createSchemaDocumentController({
  API,
  Auth,
  KgBaseAPI,
  TaskManager,
  getCurrentSchemaData: () => currentSchemaData,
  getCurrentSchemaUuid: () => currentSchemaUuid,
  getKgBaseUuid: () => kgBaseUuid,
  loadSchemaDetail,
  loadSchemaGraphs,
  notify: showToast,
});

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
    filterRelationEntityList,
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
    showRelationEntityList,
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
