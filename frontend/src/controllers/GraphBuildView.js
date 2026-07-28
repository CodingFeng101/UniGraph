import { getGraphExpansionDepth } from '@/services/preferences';

/* Generated from pages/graph-build.html; keep behavior changes in the source controller during migration. */
export function createGraphBuildViewController() {
  const { Auth, API, GraphRenderer, KgBaseAPI, TaskManager } = window;

lucide.createIcons();

function openModal(id) {
  document.getElementById(id).classList.remove('hidden');
  if (typeof onOpenModal === 'function') onOpenModal(id);
}

function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
  if (typeof onCloseModal === 'function') onCloseModal(id);
}

function toggleDropdown(id) {
  var dropdown = document.getElementById(id);
  document.querySelectorAll('[id$="-dropdown"]').forEach(function(el) {
    if (el !== dropdown) el.classList.add('hidden');
  });
  dropdown.classList.toggle('hidden');
}

function selectArch(el, value, uuid) {
  document.getElementById('arch-modal-value').textContent = value;
  if (uuid) selectedSchemaUuid = uuid;
  document.querySelectorAll('#arch-dropdown-modal > div').forEach(function(item) {
    item.style.background = '';
    item.innerHTML = '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + item.querySelector('span').textContent + '</span>';
  });
  el.style.background = 'var(--claude-accent)';
  el.innerHTML = '<div class="flex items-center justify-between"><span class="text-xs font-medium" style="color:var(--claude-foreground);">' + value + '</span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>';
  document.getElementById('arch-dropdown-modal').classList.add('hidden');
}

function selectEntityType(type) {
  document.getElementById('entity-type-value').textContent = type;
  document.getElementById('entity-type-dropdown').classList.add('hidden');
}

function selectRelationType(type) {
  document.getElementById('relation-type-value').textContent = type;
  document.getElementById('relation-type-dropdown').classList.add('hidden');
}

function addEntityAttribute() {
  var container = document.getElementById('entity-attributes');
  var div = document.createElement('div');
  div.className = 'flex items-center gap-1.5';
  div.innerHTML = '<input type="text" class="flex-1 min-w-0 h-8 px-2 text-xs rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="属性名"><span class="shrink-0 text-xs" style="color:var(--claude-muted-foreground);">=</span><input type="text" class="flex-1 min-w-0 h-8 px-2 text-xs rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="属性值"><button type="button" onclick="this.parentElement.remove()" class="w-7 h-7 shrink-0 flex items-center justify-center rounded cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-primary);border:none;color:var(--claude-primary-foreground);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>';
  container.appendChild(div);
}

function filterEntityList(prefix) {
  var input = document.getElementById(prefix + '-input');
  var query = input.value.toLowerCase();
  selectedEntityUuids[prefix] = null;
  document.getElementById(prefix + '-list')?.classList.remove('hidden');
  var buttons = document.querySelectorAll('#' + prefix + '-list button');
  buttons.forEach(function(btn) {
    var text = btn.textContent.toLowerCase();
    btn.style.display = text.includes(query) ? 'block' : 'none';
  });
}

function showEntityList(prefix) {
  document.getElementById(prefix + '-list')?.classList.remove('hidden');
  filterEntityList(prefix);
}

function selectEntity(prefix, name, uuid) {
  document.getElementById(prefix + '-input').value = name;
  document.getElementById(prefix + '-list').classList.add('hidden');
  if (typeof selectedEntityUuids !== 'undefined' && selectedEntityUuids) {
    selectedEntityUuids[prefix] = uuid || null;
  }
}

function showToast(message) {
  window.showToast(message);
}

function showTooltip(e, title, type, bodyHtml) {
  var t = document.getElementById('canvas-tooltip');
  document.getElementById('tooltip-title').textContent = title;
  document.getElementById('tooltip-type').textContent = type;
  document.getElementById('tooltip-body').innerHTML = bodyHtml;
  t.classList.remove('hidden');
  var rect = t.parentElement.getBoundingClientRect();
  var x = e.clientX - rect.left + 15;
  var y = e.clientY - rect.top - 10;
  if (x + 270 > rect.width) x = e.clientX - rect.left - 275;
  if (y + 200 > rect.height) y = rect.height - 210;
  if (y < 10) y = 10;
  t.style.left = x + 'px';
  t.style.top = y + 'px';
}

function hideTooltip() {
  document.getElementById('canvas-tooltip').classList.add('hidden');
}

document.addEventListener('click', function(e) {
  var wrapper = document.getElementById('graph-dropdown-wrapper-top');
  var dropdown = document.getElementById('graph-dropdown-top');
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



// ===== API Integration =====
// Check login status
if (!Auth.requireAuth()) throw new Error('Not logged in');

// Global state
const urlParams = window.getUniGraphSearchParams();
const kgBaseUuid = urlParams.get('uuid');
let graphList = [];
let currentGraphUuid = null;
let graphData = { entities: [], relationships: [], schema_graph: null };
let fullGraphData = { entities: [], relationships: [], schema_graph: null };
let cy = null;
let selectedElement = null;
let editingEntityUuid = null;
let editingRelationshipUuid = null;
let schemaList = [];
let selectedSchemaUuid = null;
let selectedEntityUuids = { 'head-entity': null, 'tail-entity': null };
let allEntitiesForDropdown = [];
let currentGraphStyle = 'database';

// ===== Sidebar navigation =====
function updateSidebarLinks(uuid) {
  var infoLink = document.querySelector('a[data-title="信息"]');
  var designLink = document.querySelector('a[data-title="设计"]');
  var buildLink = document.querySelector('a[data-title="构建"]');
  var appLink = document.querySelector('a[data-title="新建对话"]');
  if (infoLink) infoLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/info';
  if (designLink) designLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/structure';
  if (buildLink) buildLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/graph';
  if (appLink) appLink.href = '/unigraph/unigraphs/' + encodeURIComponent(uuid) + '/qa';
}

// ===== Load knowledge graph list =====
async function loadSchemaList() {
  if (!kgBaseUuid) return;
  try {
    var response = await KgBaseAPI.schemaGraph.getAll(kgBaseUuid);
    if (response.code !== 200) throw new Error(response.msg || '加载知识架构失败');
    schemaList = Array.isArray(response.data) ? response.data : (response.data && response.data.list) || [];
    if (!selectedSchemaUuid && schemaList.length) selectedSchemaUuid = schemaList[0].uuid;
    renderSchemaOptions();
  } catch (error) {
    showToast(error.message || '加载知识架构失败');
  }
}

function renderSchemaOptions() {
  var dropdown = document.getElementById('arch-dropdown-modal');
  if (!dropdown) return;
  dropdown.innerHTML = '';
  schemaList.forEach(function(schema) {
    var item = document.createElement('div');
    item.className = 'px-3 py-2 cursor-pointer transition-colors hover:opacity-80';
    item.style.background = schema.uuid === selectedSchemaUuid ? 'var(--claude-accent)' : '#fff';
    item.innerHTML = '<span class="text-xs" style="color:#1c1917;"></span>';
    item.querySelector('span').textContent = schema.name || '未命名架构';
    item.onclick = function() {
      selectArch(item, schema.name || '未命名架构', schema.uuid);
    };
    dropdown.appendChild(item);
  });
  var selected = schemaList.find(function(schema) { return schema.uuid === selectedSchemaUuid; });
  var label = document.getElementById('arch-modal-value');
  if (label) label.textContent = selected ? (selected.name || '未命名架构') : '暂无知识架构';
}

async function loadGraphList() {
  if (!kgBaseUuid) {
    showToast('缺少知识库 UUID');
    return;
  }
  try {
    const res = await KgBaseAPI.knowledgeGraph.getAll(kgBaseUuid);
    if (res.code === 200 && res.data) {
      graphList = Array.isArray(res.data) ? res.data : (res.data.list || res.data.graphs || []);
      graphList.sort(function(a, b) {
        return new Date(b.created_time || 0).getTime() - new Date(a.created_time || 0).getTime();
      });
      if (graphList.length === 0) {
        currentGraphUuid = null;
        graphData = { entities: [], relationships: [], schema_graph: null };
        renderGraphDropdown();
        if (cy) {
          cy.destroy();
          cy = null;
        }
        showToast('暂无知识图谱');
        return;
      }
      renderGraphDropdown();
      // If only one graph, load directly; otherwise load the first
      loadGraphDetail(graphList[0].uuid);
    } else {
      showToast(res.msg || '加载知识图谱列表失败');
    }
  } catch (err) {
    console.error('Failed to load graph list:', err);
    showToast('加载知识图谱列表失败');
  }
}

// Render graph dropdown in header
function renderGraphDropdown() {
  var dropdown = document.getElementById('graph-dropdown-top');
  if (!dropdown) return;
  var html = '';
  graphList.forEach(function(g) {
    var isActive = g.uuid === currentGraphUuid;
        var dotColor = isActive ? 'var(--claude-success-500)' : 'var(--claude-muted-foreground)';
    var dotOpacity = isActive ? '1' : '0.4';
    var textColor = isActive ? 'var(--claude-foreground)' : 'var(--claude-muted-foreground)';
    var weight = isActive ? 'font-medium' : '';
    html += '<div class="px-3 py-2 flex items-center justify-between transition-colors hover:opacity-80 cursor-pointer" onclick="loadGraphDetail(\'' + g.uuid + '\')">';
    html += '<div class="flex items-center gap-2 min-w-0">';
    html += '<span class="w-1.5 h-1.5 rounded-full shrink-0" style="background:' + dotColor + ';opacity:' + dotOpacity + ';"></span>';
    html += '<span class="text-xs truncate ' + weight + '" style="color:' + textColor + ';">' + (g.name || '未命名图谱') + '</span>';
    html += '</div>';
    html += '<button type="button" onclick="event.stopPropagation();deleteKnowledgeGraph(\'' + g.uuid + '\')" class="w-6 h-6 flex items-center justify-center cursor-pointer transition-opacity hover:opacity-70" style="background:none;border:none;color:var(--claude-destructive);" aria-label="删除知识图谱"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>';
    html += '</div>';
  });
  dropdown.innerHTML = html;
  // Update top button label
  if (currentGraphUuid) {
    var current = graphList.find(function(g) { return g.uuid === currentGraphUuid; });
    if (current) {
      var label = document.querySelector('#graph-dropdown-wrapper-top > button > span:nth-child(2)');
      if (label) label.textContent = current.name || '未命名图谱';
    }
  }
}

function onNewGraphFilesSelected(input) {
  var label = document.getElementById('new-graph-files-label');
  if (!label) return;
  label.textContent = input.files && input.files.length
    ? Array.from(input.files).map(function(file) { return file.name; }).join('、')
    : '上传 PDF/Word/TXT 文档';
}

async function uploadGraphFiles(files) {
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

async function submitNewGraph() {
  var name = document.getElementById('new-graph-name').value.trim();
  var input = document.getElementById('new-graph-files');
  if (!name) {
    showToast('请输入知识图谱名称');
    return;
  }
  if (!selectedSchemaUuid) {
    showToast('请选择知识架构');
    return;
  }
  if (!input.files || !input.files.length) {
    showToast('请上传构建文档');
    return;
  }
  try {
    var filePaths = await uploadGraphFiles(input.files);
    var task = await TaskManager.submit(
      'knowledge_graph.create_knowledge_graph',
      '创建知识图谱',
      name,
      {
        user_token: Auth.getToken(),
        obj_data: {
          file_paths: filePaths,
          data: {
            kg_base_uuid: kgBaseUuid,
            schema_graph_uuid: selectedSchemaUuid,
            name: name
          }
        }
      }
    );
    document.getElementById('modal-new-graph').classList.add('hidden');
    await task.completion;
    await loadGraphList();
  } catch (error) {
    showToast(error.message || '创建知识图谱失败');
  }
}

async function deleteKnowledgeGraph(uuid) {
  if (!uuid || !await window.confirmAction({
    title: '删除知识图谱',
    message: '确定要删除这个知识图谱吗？删除后无法恢复。',
  })) return;
  try {
    var response = await KgBaseAPI.knowledgeGraph.delete(uuid);
    if (response.code !== 200) throw new Error(response.msg || '删除知识图谱失败');
    if (currentGraphUuid === uuid) {
      currentGraphUuid = null;
      graphData = { entities: [], relationships: [], schema_graph: null };
      if (cy) {
        cy.destroy();
        cy = null;
      }
    }
    await loadGraphList();
    showToast('知识图谱已删除');
  } catch (error) {
    showToast(error.message || '删除知识图谱失败');
  }
}

async function deleteCurrentKnowledgeGraph() {
  if (!currentGraphUuid) {
    showToast('请先选择知识图谱');
    return;
  }
  await deleteKnowledgeGraph(currentGraphUuid);
}

async function buildGraphIndex() {
  if (!currentGraphUuid) {
    showToast('请先选择知识图谱');
    return;
  }
  try {
    var task = await TaskManager.submit(
      'knowledge_graph.build_index',
      '建立知识索引',
      graphList.find(function(item) { return item.uuid === currentGraphUuid; })?.name || currentGraphUuid,
      { uuid: currentGraphUuid, user_token: Auth.getToken() }
    );
    await task.completion;
    await loadGraphDetail(currentGraphUuid);
  } catch (error) {
    showToast(error.message || '建立索引失败');
  }
}

function filterGraph(shouldFocus) {
  if (!cy) return;
  var search = document.getElementById('build-graph-search')?.value.toLowerCase().trim() || '';
  if (GraphRenderer.filter(cy, search, shouldFocus)) return;
  var elements = cy.elements();
  if (!search) {
    elements.style('opacity', 1);
    elements.nodes().removeStyle('border-color border-width shadow-blur shadow-color shadow-opacity');
    elements.edges().removeStyle('line-color target-arrow-color width color');
    return;
  }
  var matches = elements.filter(function(element) {
    return String(element.data('label') || element.data('type') || '').toLowerCase().includes(search);
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
    'color': '#a0502f'
  });
  if (shouldFocus && matches.length) {
    cy.animate({
      center: { eles: matches },
      zoom: Math.min(Math.max(cy.zoom(), 0.75), 1.25),
      duration: 280
    });
  }
}

async function exportGraphIndex() {
  if (!currentGraphUuid) {
    showToast('请先选择知识图谱');
    return;
  }
  try {
    var response = await KgBaseAPI.knowledgeGraph.exportIndexFile(currentGraphUuid);
    if (response.code !== 200) throw new Error(response.msg || '导出索引失败');
    var text = typeof response.data === 'string' ? response.data : JSON.stringify(response.data, null, 2);
    var blobUrl = URL.createObjectURL(new Blob([text], { type: 'application/json;charset=utf-8' }));
    var link = document.createElement('a');
    link.href = blobUrl;
    link.download = (graphList.find(function(item) { return item.uuid === currentGraphUuid; })?.name || 'knowledge-graph') + '-index.json';
    link.click();
    URL.revokeObjectURL(blobUrl);
    showToast('索引已导出');
  } catch (error) {
    showToast(error.message || '导出索引失败');
  }
}

async function startKnowledgeInference() {
  if (!currentGraphUuid) {
    showToast('请先选择知识图谱');
    return;
  }
  try {
    var task = await TaskManager.submit(
      'knowledge_graph.infer_knowledge_graph',
      '知识迁移',
      graphList.find(function(item) { return item.uuid === currentGraphUuid; })?.name || currentGraphUuid,
      { uuid: currentGraphUuid, user_token: Auth.getToken() }
    );
    closeModal('modal-reasoning');
    await task.completion;
    await loadGraphDetail(currentGraphUuid);
  } catch (error) {
    showToast(error.message || '知识迁移失败');
  }
}

// ===== Load graph detail =====
async function loadGraphDetail(graphUuid) {
  if (!graphUuid) return;
  currentGraphUuid = graphUuid;
  document.getElementById('graph-dropdown-top').classList.add('hidden');
  if (currentGraphStyle === 'load') {
    fullGraphData = { entities: [], relationships: [], schema_graph: null };
    renderGraphDropdown();
    await loadExplorationOverview();
    return;
  }
  try {
    const res = await KgBaseAPI.knowledgeGraph.getDetail(graphUuid);
    if (res.code === 200 && res.data) {
      graphData = {
        entities: res.data.entities || [],
        relationships: res.data.relationships || [],
        schema_graph: res.data.schema_graph || null,
      };
      fullGraphData = {
        entities: graphData.entities.slice(),
        relationships: graphData.relationships.slice(),
        schema_graph: graphData.schema_graph,
      };
      renderGraphDropdown();
      renderGraph();
    } else {
      showToast(res.msg || '加载知识图谱详情失败');
    }
  } catch (err) {
    console.error('Failed to load graph detail:', err);
    showToast('加载知识图谱详情失败');
  }
}

// ===== Render graph with Cytoscape =====
function renderGraph(viewState) {
  var container = document.getElementById('graph-canvas');
  if (!container) return;
  // Destroy existing instance
  if (cy) {
    cy.destroy();
    cy = null;
  }
  cy = GraphRenderer.init('graph-canvas', graphData.entities, graphData.relationships, {
    mode: currentGraphStyle,
    serverExploration: currentGraphStyle === 'load',
    positions: viewState?.positions,
    anchorPosition: viewState?.anchorPosition,
    viewport: viewState?.viewport,
    onNodeClick: function(data, node) {
      selectedElement = { type: 'node', data: data, node: node };
      showElementDetail(data, 'node');
    },
    onNodeDoubleClick: function(data) {
      if (currentGraphStyle === 'load') loadExplorationNeighbors(data.id);
    },
    onClusterDoubleClick: function(data) {
      loadExplorationType(data.type);
    },
    onEdgeClick: function(data, edge) {
      selectedElement = { type: 'edge', data: data, edge: edge };
      showElementDetail(data, 'edge');
    },
    onNodeHover: function(data, node, position) {
      selectedElement = { type: 'node', data: data, node: node };
      showElementDetail(data, 'node', position);
    },
    onEdgeHover: function(data, edge, position) {
      selectedElement = { type: 'edge', data: data, edge: edge };
      showElementDetail(data, 'edge', position);
    },
    onElementLeave: scheduleTooltipHide,
    onCanvasClick: function() {
      selectedElement = null;
      hideTooltip();
    },
  });
}

async function loadExplorationOverview() {
  var response = await KgBaseAPI.knowledgeGraph.getExplorationOverview(currentGraphUuid);
  if (response.code !== 200) throw new Error(response.msg || '加载图谱概览失败');
  graphData = {
    entities: (response.data?.clusters || []).map(function(cluster) {
      return {
        uuid: '__server_cluster__' + encodeURIComponent(cluster.type),
        name: cluster.type + ' · ' + cluster.count,
        type: cluster.type,
        attributes: {},
        is_cluster: true,
        cluster_count: cluster.count,
      };
    }),
    relationships: (response.data?.relationships || []).map(function(item, index) {
      return {
        uuid: '__server_cluster_edge__' + index,
        name: String(item.count),
        type: 'cluster',
        source_entity_uuid: '__server_cluster__' + encodeURIComponent(item.source_type),
        target_entity_uuid: '__server_cluster__' + encodeURIComponent(item.target_type),
        attributes: {},
      };
    }),
    schema_graph: null,
  };
  renderGraph();
}

async function changeGraphStyle(style) {
  currentGraphStyle = style;
  if (style === 'load') {
    try {
      await loadExplorationOverview();
    } catch (error) {
      showToast(error.message || '加载图谱概览失败');
      return;
    }
  } else {
    if (!fullGraphData.entities.length) {
      await loadGraphDetail(currentGraphUuid);
    } else {
    graphData = {
      entities: fullGraphData.entities.slice(),
      relationships: fullGraphData.relationships.slice(),
      schema_graph: fullGraphData.schema_graph,
    };
    renderGraph();
    }
  }
  document.querySelectorAll('[data-build-graph-style]').forEach(function(button) {
    var active = button.dataset.buildGraphStyle === style;
    button.style.background = active ? 'var(--claude-primary)' : 'transparent';
    button.style.color = active ? 'var(--claude-primary-foreground)' : 'var(--claude-muted-foreground)';
  });
  showToast('已切换图谱样式');
}

function captureExplorationView(anchorUuid) {
  if (!cy) return null;
  return GraphRenderer.captureView(cy, anchorUuid);
}

function mergeExplorationData(data, removeType, anchorUuid) {
  var clusterUuid = removeType ? '__server_cluster__' + encodeURIComponent(removeType) : null;
  var viewState = captureExplorationView(anchorUuid || clusterUuid);
  var existingIds = new Set(graphData.entities.map(function(entity) { return entity.uuid; }));
  var entities = graphData.entities.filter(function(entity) {
    return !(entity.is_cluster && entity.type === removeType);
  });
  var entityMap = new Map(entities.map(function(entity) { return [entity.uuid, entity]; }));
  (data.entities || []).forEach(function(entity) { entityMap.set(entity.uuid, entity); });
  var relationshipMap = new Map(graphData.relationships.map(function(item) { return [item.uuid, item]; }));
  (data.relationships || []).forEach(function(item) { relationshipMap.set(item.uuid, item); });
  if (clusterUuid) {
    relationshipMap.forEach(function(item, uuid) {
      if (item.source_entity_uuid === clusterUuid || item.target_entity_uuid === clusterUuid) {
        relationshipMap.delete(uuid);
      }
    });
  }
  graphData.entities = Array.from(entityMap.values());
  graphData.relationships = Array.from(relationshipMap.values());
  renderGraph(viewState);
  if (cy?._engine === 'vis-network') return;
  var newNodes = cy.nodes().filter(function(node) { return !existingIds.has(node.id()); });
  if (newNodes.length) {
    var anchorPosition = viewState.anchorPosition;
    newNodes.forEach(function(node) {
      var targetPosition = node.position();
      node.position(anchorPosition);
      node.style('opacity', 0);
      node.animate({
        position: targetPosition,
        style: { opacity: 1 },
        duration: 520,
        easing: 'ease-out-cubic',
      });
    });
    window.setTimeout(function() {
      if (!cy || cy.destroyed()) return;
      cy.elements().filter((element) => element.visible()).layout({
        name: 'fcose',
        quality: 'draft',
        randomize: false,
        animate: true,
        animationDuration: 650,
        animationEasing: 'ease-out-cubic',
        fit: false,
        idealEdgeLength: 120,
        nodeRepulsion: 7200,
        gravity: 0.18,
        avoidOverlap: true,
      }).run();
    }, 540);
  }
}

async function loadExplorationType(type) {
  try {
    var response = await KgBaseAPI.knowledgeGraph.getExplorationType(currentGraphUuid, type);
    if (response.code !== 200) throw new Error(response.msg || '展开实体类型失败');
    mergeExplorationData(response.data || {}, type);
  } catch (error) {
    showToast(error.message || '展开实体类型失败');
  }
}

async function loadExplorationNeighbors(entityUuid) {
  try {
    var response = await KgBaseAPI.knowledgeGraph.getExplorationNeighbors(
      currentGraphUuid,
      entityUuid,
      getGraphExpansionDepth()
    );
    if (response.code !== 200) throw new Error(response.msg || '展开邻居失败');
    mergeExplorationData(response.data || {}, null, entityUuid);
  } catch (error) {
    showToast(error.message || '展开邻居失败');
  }
}

function normalizeGraphAttributes(value) {
  if (!value) return {};
  if (typeof value === 'object') return value;
  try {
    var parsed = JSON.parse(value);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch (error) {
    return {};
  }
}

// ===== Show element detail panel =====
function showElementDetail(data, type, position) {
  var t = document.getElementById('canvas-tooltip');
  if (!t) return;
  var title = data.label || data.name || '';
  var typeLabel = type === 'node' ? (data.type || '实体') + ' (实体)' : (data.type || data.label || '关系') + ' (关系)';
  document.getElementById('tooltip-title').textContent = title;
  document.getElementById('tooltip-type').textContent = typeLabel;
  var bodyHtml = '';
  if (type === 'node' && data.raw) {
    var attrs = normalizeGraphAttributes(data.raw.attributes);
    if (attrs && typeof attrs === 'object') {
      Object.keys(attrs).forEach(function(key) {
        bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">' + key + ' = ' + attrs[key] + '</p>';
      });
    }
    if (data.raw.source) bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">来源: ' + data.raw.source + '</p>';
  } else if (type === 'edge' && data.raw) {
    var srcEntity = graphData.entities.find(function(e) { return e.uuid === data.raw.source_entity_uuid; });
    var tgtEntity = graphData.entities.find(function(e) { return e.uuid === data.raw.target_entity_uuid; });
    var srcName = srcEntity ? srcEntity.name : (data.raw.source_entity_uuid || '');
    var tgtName = tgtEntity ? tgtEntity.name : (data.raw.target_entity_uuid || '');
    bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">' + srcName + ' → ' + tgtName + '</p>';
    if (data.raw.type) bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">类型: ' + data.raw.type + '</p>';
    if (data.raw.source) bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">来源: ' + data.raw.source + '</p>';
  }
  document.getElementById('tooltip-body').innerHTML = bodyHtml;
  t.classList.remove('hidden');
  var parent = t.parentElement;
  var x = position ? position.x + 16 : parent.clientWidth - 272;
  var y = position ? position.y - 18 : 12;
  if (x + 270 > parent.clientWidth) x = Math.max(12, x - 286);
  if (y + t.offsetHeight > parent.clientHeight) y = Math.max(12, parent.clientHeight - t.offsetHeight - 12);
  t.style.right = 'auto';
  t.style.left = Math.max(12, x) + 'px';
  t.style.top = Math.max(12, y) + 'px';
}

function scheduleTooltipHide() {
  window.setTimeout(function() {
    var tooltip = document.getElementById('canvas-tooltip');
    if (tooltip && !tooltip.matches(':hover')) hideTooltip();
  }, 140);
}

// Reload graph after CRUD
async function reloadGraph() {
  if (!currentGraphUuid) return;
  await loadGraphDetail(currentGraphUuid);
}

// ===== Entity CRUD =====
async function submitEntity() {
  var nameInput = document.getElementById('entity-name-input');
  if (!nameInput) return;
  var name = nameInput.value.trim();
  if (!name) {
    showToast('请输入实体名称');
    return;
  }
  var type = document.getElementById('entity-type-value').textContent.trim();
  var attributes = {};
  var attrRows = document.querySelectorAll('#entity-attributes > div');
  attrRows.forEach(function(row) {
    var inputs = row.querySelectorAll('input');
    if (inputs.length >= 2 && inputs[0].value.trim()) {
      attributes[inputs[0].value.trim()] = inputs[1].value.trim();
    }
  });
  try {
    var res;
    if (editingEntityUuid) {
      res = await KgBaseAPI.knowledgeEntity.update(editingEntityUuid, { name: name, attributes: JSON.stringify(attributes), type: type });
    } else {
      res = await KgBaseAPI.knowledgeEntity.create({ knowledge_graph_uuid: currentGraphUuid, name: name, type: type, attributes: JSON.stringify(attributes) });
    }
    if (res.code === 200) {
      showToast(editingEntityUuid ? '实体已更新' : '实体已创建');
      closeModal('modal-entity-build');
      await reloadGraph();
    } else {
      showToast(res.msg || '操作失败');
    }
  } catch (err) {
    console.error('Entity submit error:', err);
    showToast('操作失败');
  }
}

// Edit entity (open modal in edit mode)
function editEntity(entity) {
  editingEntityUuid = entity.uuid;
  openModal('modal-entity-build');
  document.getElementById('entity-name-input').value = entity.name || '';
  if (entity.type) selectEntityType(entity.type);
  // Render attributes
  var container = document.getElementById('entity-attributes');
  container.innerHTML = '';
  var attributes = normalizeGraphAttributes(entity.attributes);
  if (Object.keys(attributes).length) {
    Object.keys(attributes).forEach(function(key) {
      var div = document.createElement('div');
      div.className = 'flex items-center gap-1.5';
      div.innerHTML = '<input type="text" class="flex-1 min-w-0 h-8 px-2 text-xs rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="属性名"><span class="shrink-0 text-xs" style="color:var(--claude-muted-foreground);">=</span><input type="text" class="flex-1 min-w-0 h-8 px-2 text-xs rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="属性值"><button type="button" onclick="this.parentElement.remove()" class="w-7 h-7 shrink-0 flex items-center justify-center rounded cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-primary);border:none;color:var(--claude-primary-foreground);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>';
      var inputs = div.querySelectorAll('input');
      inputs[0].value = key;
      inputs[1].value = attributes[key];
      container.appendChild(div);
    });
  }
  if (container.children.length === 0) addEntityAttribute();
  var title = document.querySelector('#modal-entity-build h3');
  if (title) title.textContent = '编辑实体';
  var submitBtn = document.querySelector('#modal-entity-build .flex.justify-end button:last-child');
  if (submitBtn) submitBtn.textContent = '保存';
}

// Delete entity
async function deleteEntity(uuid) {
  if (!uuid) return;
  if (!await window.confirmAction({ title: '删除实体', message: '确定要删除该实体吗？' })) return;
  try {
    var res = await KgBaseAPI.knowledgeEntity.delete(uuid);
    if (res.code === 200) {
      showToast('实体已删除');
      hideTooltip();
      await reloadGraph();
    } else {
      showToast(res.msg || '删除实体失败');
    }
  } catch (err) {
    console.error('Delete entity error:', err);
    showToast('删除失败');
  }
}

// ===== Relationship CRUD =====
// Load entities for dropdowns
async function loadEntitiesForDropdowns() {
  try {
    var res = await KgBaseAPI.knowledgeEntity.getAll(currentGraphUuid);
    if (res.code === 200 && res.data) {
      allEntitiesForDropdown = Array.isArray(res.data) ? res.data : (res.data.entities || res.data.list || []);
    } else {
      allEntitiesForDropdown = graphData.entities || [];
    }
  } catch (err) {
    allEntitiesForDropdown = graphData.entities || [];
  }
  renderEntityDropdown('head-entity');
  renderEntityDropdown('tail-entity');
}

// Render entity dropdown list
function renderEntityDropdown(prefix) {
  var list = document.getElementById(prefix + '-list');
  if (!list) return;
  list.innerHTML = '';
  allEntitiesForDropdown.forEach(function(entity) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'w-full px-3 py-2 text-sm text-left cursor-pointer transition-colors hover:bg-[var(--claude-secondary)]';
    btn.style.cssText = 'background:none;border:none;color:var(--claude-foreground);';
    btn.textContent = entity.name || entity.uuid;
    btn.onclick = function() { selectEntity(prefix, entity.name || entity.uuid, entity.uuid); };
    list.appendChild(btn);
  });
}

// Submit relationship
async function submitRelation() {
  var type = document.getElementById('relation-type-value').textContent.trim();
  var headUuid = selectedEntityUuids['head-entity'];
  var tailUuid = selectedEntityUuids['tail-entity'];
  if (!headUuid || !tailUuid) {
    showToast('请选择头实体和尾实体');
    return;
  }
  try {
    var payload = {
      knowledge_graph_uuid: currentGraphUuid,
      source_entity_uuid: headUuid,
      target_entity_uuid: tailUuid,
      name: type,
      type: type,
      attributes: '{}'
    };
    var res = editingRelationshipUuid
      ? await KgBaseAPI.knowledgeRelationship.update(editingRelationshipUuid, payload)
      : await KgBaseAPI.knowledgeRelationship.create(payload);
    if (res.code === 200) {
      showToast(editingRelationshipUuid ? '关系已更新' : '关系已创建');
      closeModal('modal-relation-build');
      await reloadGraph();
    } else {
      showToast(res.msg || '保存关系失败');
    }
  } catch (err) {
    console.error('Relation submit error:', err);
    showToast('操作失败');
  }
}

function editRelationship(relationship) {
  editingRelationshipUuid = relationship.uuid;
  openModal('modal-relation-build');
  selectRelationType(relationship.type || relationship.name || '关联');
  var source = graphData.entities.find(function(entity) { return entity.uuid === relationship.source_entity_uuid; });
  var target = graphData.entities.find(function(entity) { return entity.uuid === relationship.target_entity_uuid; });
  selectEntity('head-entity', source ? source.name : relationship.source_entity_uuid, relationship.source_entity_uuid);
  selectEntity('tail-entity', target ? target.name : relationship.target_entity_uuid, relationship.target_entity_uuid);
  var title = document.querySelector('#modal-relation-build h3');
  if (title) title.textContent = '编辑关系';
  var button = document.querySelector('#modal-relation-build .flex.justify-end button:last-child');
  if (button) button.textContent = '保存';
}

// Delete relationship
async function deleteRelationship(uuid) {
  if (!uuid) return;
  if (!await window.confirmAction({ title: '删除关系', message: '确定要删除该关系吗？' })) return;
  try {
    var res = await KgBaseAPI.knowledgeRelationship.delete(uuid);
    if (res.code === 200) {
      showToast('关系已删除');
      hideTooltip();
      await reloadGraph();
    } else {
      showToast(res.msg || '删除关系失败');
    }
  } catch (err) {
    console.error('Delete relationship error:', err);
    showToast('删除失败');
  }
}

// ===== Tooltip actions =====
function editSelected() {
  if (!selectedElement) return;
  if (selectedElement.type === 'node' && selectedElement.data.raw) {
    editEntity(selectedElement.data.raw);
  } else if (selectedElement.type === 'edge' && selectedElement.data.raw) {
    editRelationship(selectedElement.data.raw);
  }
}

function deleteSelected() {
  if (!selectedElement) return;
  if (selectedElement.type === 'node') {
    deleteEntity(selectedElement.data.id);
  } else {
    deleteRelationship(selectedElement.data.id);
  }
}

// ===== Update graph (file upload) =====
function triggerUpdateFile() {
  var fileInput = document.getElementById('update-graph-file');
  if (fileInput) fileInput.click();
}

function onUpdateFileSelected(input) {
  var label = document.getElementById('update-graph-file-label');
  if (label && input.files && input.files.length > 0) {
    label.textContent = input.files[0].name;
  }
}

async function submitUpdateGraph() {
  var fileInput = document.getElementById('update-graph-file');
  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    showToast('请选择文件');
    return;
  }
  var file = fileInput.files[0];
  try {
    var res = await API.uploadFile(file);
    if (res.code !== 200 || !res.data || !res.data.url) {
      throw new Error(res.msg || '文件上传失败');
    }
    var schemaUuid = graphData.schema_graph && graphData.schema_graph.uuid
      ? graphData.schema_graph.uuid
      : (graphList.find(function(item) { return item.uuid === currentGraphUuid; }) || {}).schema_graph_uuid;
    var task = await TaskManager.submit(
      'knowledge_graph.update_knowledge_graph',
      '更新知识图谱',
      graphList.find(function(item) { return item.uuid === currentGraphUuid; })?.name || currentGraphUuid,
      {
        uuid: currentGraphUuid,
        user_token: Auth.getToken(),
        obj_data: {
          file_paths: [res.data.url],
          data: { schema_graph_uuid: schemaUuid || '' }
        }
      }
    );
    document.getElementById('modal-update-graph').classList.add('hidden');
    fileInput.value = '';
    var label = document.getElementById('update-graph-file-label');
    if (label) label.textContent = '上传 PDF/Word/TXT 文档';
    await task.completion;
    await reloadGraph();
  } catch (err) {
    console.error('Update graph error:', err);
    showToast(err.message || '更新失败');
  }
}

// ===== Zoom controls =====
function zoomIn() {
  if (cy) GraphRenderer.zoom(cy, 0.18);
}

function zoomOut() {
  if (cy) GraphRenderer.zoom(cy, -0.18);
}

function fitCanvas() {
  if (cy) GraphRenderer.fit(cy);
}

// ===== Modal hooks =====
function onOpenModal(id) {
  if (id === 'modal-relation-build') {
    if (!editingRelationshipUuid) {
      selectedEntityUuids = { 'head-entity': null, 'tail-entity': null };
      var headInput = document.getElementById('head-entity-input');
      var tailInput = document.getElementById('tail-entity-input');
      if (headInput) headInput.value = '';
      if (tailInput) tailInput.value = '';
      var relationTitle = document.querySelector('#modal-relation-build h3');
      if (relationTitle) relationTitle.textContent = '新增关系';
      var button = document.querySelector('#modal-relation-build .flex.justify-end button:last-child');
      if (button) button.textContent = '创建';
    }
    loadEntitiesForDropdowns();
  }
  if (id === 'modal-entity-build' && !editingEntityUuid) {
    var nameInput = document.getElementById('entity-name-input');
    if (nameInput) nameInput.value = '';
    var container = document.getElementById('entity-attributes');
    if (container) {
      container.innerHTML = '';
      addEntityAttribute();
    }
    var entityTitle = document.querySelector('#modal-entity-build h3');
    if (entityTitle) entityTitle.textContent = '新增实体';
    var submitBtn = document.querySelector('#modal-entity-build .flex.justify-end button:last-child');
    if (submitBtn) submitBtn.textContent = '创建';
  }
}

function onCloseModal(id) {
  if (id === 'modal-entity-build') {
    editingEntityUuid = null;
  }
  if (id === 'modal-relation-build') {
    editingRelationshipUuid = null;
  }
}

// ===== Init =====
updateSidebarLinks(kgBaseUuid);
loadSchemaList();
loadGraphList();

  window.loadGraphDetail = loadGraphDetail;
  window.deleteKnowledgeGraph = deleteKnowledgeGraph;

  return {
    addEntityAttribute,
    buildGraphIndex,
    changeGraphStyle,
    closeModal,
    deleteCurrentKnowledgeGraph,
    deleteSelected,
    editSelected,
    exportGraphIndex,
    filterGraph,
    filterEntityList,
    fitCanvas,
    hideTooltip,
    onNewGraphFilesSelected,
    onUpdateFileSelected,
    openModal,
    selectArch,
    selectEntity,
    selectEntityType,
    selectRelationType,
    showToast,
    showEntityList,
    showTooltip,
    startKnowledgeInference,
    submitEntity,
    submitNewGraph,
    submitRelation,
    submitUpdateGraph,
    toggleDropdown,
    triggerUpdateFile,
    zoomIn,
    zoomOut,
  };
}
