import { renderGraphTooltipContent } from '@/utils/graphTooltip';
import { validateUploadFiles } from '@/utils/upload';

export function createGraphEditorController(context) {
  function normalizeGraphAttributes(value) {
    if (!value) return {};
    if (typeof value === 'object') return value;
    try {
      var parsed = JSON.parse(value);
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (_error) {
      return {};
    }
  }

  function resolveKnowledgeEntityName(uuid, preferredName) {
    var explicitName = String(preferredName || '').trim();
    if (explicitName && explicitName !== uuid) return explicitName;
    var state = context.getState();
    var pools = [state.graphData.entities, state.fullGraphData.entities, state.allEntities];
    for (var index = 0; index < pools.length; index += 1) {
      var entity = (pools[index] || []).find(function(item) { return item.uuid === uuid; });
      if (entity && entity.name) return entity.name;
    }
    return '未知实体';
  }

  function showElementDetail(data, type, position) {
    var tooltip = document.getElementById('canvas-tooltip');
    if (!tooltip) return;
    var title = data.label || data.name || '';
    var typeLabel = type === 'node' ? (data.type || '实体') + ' (实体)' : (data.type || data.label || '关系') + ' (关系)';
    var bodyHtml = '';
    if (type === 'node' && data.raw) {
      var attrs = normalizeGraphAttributes(data.raw.attributes);
      Object.keys(attrs).forEach(function(key) {
        bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">' + key + ' = ' + attrs[key] + '</p>';
      });
      if (data.raw.source) bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">来源: ' + data.raw.source + '</p>';
    } else if (type === 'edge' && data.raw) {
      var srcName = resolveKnowledgeEntityName(data.raw.source_entity_uuid, data.raw.source_entity_name);
      var tgtName = resolveKnowledgeEntityName(data.raw.target_entity_uuid, data.raw.target_entity_name);
      bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">头实体: ' + srcName + '</p>';
      bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">尾实体: ' + tgtName + '</p>';
      if (data.raw.type) bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">类型: ' + data.raw.type + '</p>';
      if (data.raw.source) bodyHtml += '<p class="text-[11px] mt-1" style="color:var(--claude-muted-foreground);">来源: ' + data.raw.source + '</p>';
    }
    renderGraphTooltipContent(title, typeLabel, bodyHtml);
    tooltip.classList.remove('hidden');
    var parent = tooltip.parentElement;
    var x = position ? position.x + 16 : parent.clientWidth - tooltip.offsetWidth - 12;
    var y = position ? position.y - 18 : 12;
    if (x + tooltip.offsetWidth + 12 > parent.clientWidth) x = Math.max(12, x - tooltip.offsetWidth - 32);
    if (y + tooltip.offsetHeight > parent.clientHeight) y = Math.max(12, parent.clientHeight - tooltip.offsetHeight - 12);
    tooltip.style.right = 'auto';
    tooltip.style.left = Math.max(12, x) + 'px';
    tooltip.style.top = Math.max(12, y) + 'px';
  }

  function scheduleTooltipHide() {
    window.setTimeout(function() {
      var tooltip = document.getElementById('canvas-tooltip');
      if (tooltip && !tooltip.matches(':hover')) context.hideTooltip();
    }, 140);
  }

  async function reloadGraph() {
    var graphUuid = context.getState().graphUuid;
    if (graphUuid) await context.loadGraphDetail(graphUuid);
  }

  async function submitEntity() {
    var nameInput = document.getElementById('entity-name-input');
    if (!nameInput) return;
    var name = nameInput.value.trim();
    if (!name) return context.notify('请输入实体名称');
    var type = document.getElementById('entity-type-input').dataset.value || '';
    if (!type) return context.notify('当前架构没有可用的实体类型');
    var attributes = {};
    document.querySelectorAll('#entity-attributes > div').forEach(function(row) {
      var inputs = row.querySelectorAll('input');
      if (inputs.length >= 2 && inputs[0].value.trim()) attributes[inputs[0].value.trim()] = inputs[1].value.trim();
    });
    var state = context.getState();
    try {
      var response = state.editingEntityUuid
        ? await context.api.knowledgeEntity.update(state.editingEntityUuid, { name, attributes: JSON.stringify(attributes), type })
        : await context.api.knowledgeEntity.create({ knowledge_graph_uuid: state.graphUuid, name, type, attributes: JSON.stringify(attributes) });
      if (response.code !== 200) return context.notify(response.msg || '操作失败');
      context.notify(state.editingEntityUuid ? '实体已更新' : '实体已创建');
      context.closeModal('modal-entity-build');
      await reloadGraph();
    } catch (error) {
      console.error('Entity submit error:', error);
      context.notify('操作失败');
    }
  }

  function editEntity(entity) {
    context.setEditingEntityUuid(entity.uuid);
    context.openModal('modal-entity-build');
    document.getElementById('entity-name-input').value = entity.name || '';
    if (entity.type) context.selectEntityType(entity.type);
    var container = document.getElementById('entity-attributes');
    container.innerHTML = '';
    var attributes = normalizeGraphAttributes(entity.attributes);
    Object.keys(attributes).forEach(function(key) {
      context.addEntityAttribute();
      var row = container.lastElementChild;
      var inputs = row.querySelectorAll('input');
      inputs[0].value = key;
      inputs[1].value = attributes[key];
    });
    if (container.children.length === 0) context.addEntityAttribute();
    var title = document.querySelector('#modal-entity-build h3');
    if (title) title.textContent = '编辑实体';
    var submitButton = document.querySelector('#modal-entity-build .flex.justify-end button:last-child');
    if (submitButton) submitButton.textContent = '保存';
  }

  async function deleteEntity(uuid) {
    if (!uuid || !await window.confirmAction({ title: '删除实体', message: '确定要删除该实体吗？' })) return;
    try {
      var response = await context.api.knowledgeEntity.delete(uuid);
      if (response.code !== 200) return context.notify(response.msg || '删除实体失败');
      context.notify('实体已删除');
      context.hideTooltip();
      await reloadGraph();
    } catch (error) {
      console.error('Delete entity error:', error);
      context.notify('删除失败');
    }
  }

  async function loadEntitiesForDropdowns() {
    var state = context.getState();
    var entities;
    try {
      var response = await context.api.knowledgeEntity.getAll(state.graphUuid);
      entities = response.code === 200 && response.data
        ? (Array.isArray(response.data) ? response.data : response.data.entities || response.data.list || [])
        : state.graphData.entities || [];
    } catch (_error) {
      entities = state.graphData.entities || [];
    }
    context.setAllEntities(entities);
    renderEntityDropdown('head-entity');
    renderEntityDropdown('tail-entity');
  }

  function renderEntityDropdown(prefix) {
    var list = document.getElementById(prefix + '-list');
    if (!list) return;
    list.innerHTML = '';
    context.getState().allEntities.forEach(function(entity) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'w-full px-3 py-2 text-sm text-left cursor-pointer transition-colors hover:bg-[var(--claude-secondary)]';
      button.style.cssText = 'background:none;border:none;color:var(--claude-foreground);';
      button.textContent = entity.name || entity.uuid;
      button.onclick = function() { context.selectEntity(prefix, entity.name || entity.uuid, entity.uuid); };
      list.appendChild(button);
    });
  }

  async function submitRelation() {
    var type = document.getElementById('relation-type-input').dataset.value || '';
    if (!type) return context.notify('请选择关系类型');
    var name = document.getElementById('relation-name-input').value.trim();
    if (!name) return context.notify('请输入关系名称');
    var description = document.getElementById('relation-description-input').value.trim();
    var state = context.getState();
    var headUuid = state.selectedEntityUuids['head-entity'];
    var tailUuid = state.selectedEntityUuids['tail-entity'];
    if (!headUuid || !tailUuid) return context.notify('请选择头实体和尾实体');
    var payload = {
      knowledge_graph_uuid: state.graphUuid,
      source_entity_uuid: headUuid,
      target_entity_uuid: tailUuid,
      name,
      type,
      attributes: JSON.stringify(description ? { description } : {}),
    };
    try {
      var response = state.editingRelationshipUuid
        ? await context.api.knowledgeRelationship.update(state.editingRelationshipUuid, payload)
        : await context.api.knowledgeRelationship.create(payload);
      if (response.code !== 200) return context.notify(response.msg || '保存关系失败');
      context.notify(state.editingRelationshipUuid ? '关系已更新' : '关系已创建');
      context.closeModal('modal-relation-build');
      await reloadGraph();
    } catch (error) {
      console.error('Relation submit error:', error);
      context.notify('操作失败');
    }
  }

  function editRelationship(relationship) {
    context.setEditingRelationshipUuid(relationship.uuid);
    context.openModal('modal-relation-build');
    context.selectRelationType(relationship.type || relationship.name || '关联');
    document.getElementById('relation-name-input').value = relationship.name || '';
    var attributes = normalizeGraphAttributes(relationship.attributes);
    document.getElementById('relation-description-input').value = attributes.description || '';
    var graphEntities = context.getState().graphData.entities;
    var source = graphEntities.find(function(entity) { return entity.uuid === relationship.source_entity_uuid; });
    var target = graphEntities.find(function(entity) { return entity.uuid === relationship.target_entity_uuid; });
    context.selectEntity('head-entity', source ? source.name : relationship.source_entity_uuid, relationship.source_entity_uuid);
    context.selectEntity('tail-entity', target ? target.name : relationship.target_entity_uuid, relationship.target_entity_uuid);
    var title = document.querySelector('#modal-relation-build h3');
    if (title) title.textContent = '编辑关系';
    var button = document.querySelector('#modal-relation-build .flex.justify-end button:last-child');
    if (button) button.textContent = '保存';
  }

  async function deleteRelationship(uuid) {
    if (!uuid || !await window.confirmAction({ title: '删除关系', message: '确定要删除该关系吗？' })) return;
    try {
      var response = await context.api.knowledgeRelationship.delete(uuid);
      if (response.code !== 200) return context.notify(response.msg || '删除关系失败');
      context.notify('关系已删除');
      context.hideTooltip();
      await reloadGraph();
    } catch (error) {
      console.error('Delete relationship error:', error);
      context.notify('删除失败');
    }
  }

  function editSelected() {
    var selected = context.getState().selectedElement;
    if (!selected) return;
    if (selected.type === 'node' && selected.data.raw) editEntity(selected.data.raw);
    else if (selected.type === 'edge' && selected.data.raw) editRelationship(selected.data.raw);
  }

  function deleteSelected() {
    var selected = context.getState().selectedElement;
    if (!selected) return;
    if (selected.type === 'node') deleteEntity(selected.data.id);
    else deleteRelationship(selected.data.id);
  }

  function triggerUpdateFile() {
    document.getElementById('update-graph-file')?.click();
  }

  function onUpdateFileSelected(input) {
    var label = document.getElementById('update-graph-file-label');
    if (label && input.files?.length) label.textContent = input.files[0].name;
  }

  async function submitUpdateGraph() {
    var fileInput = document.getElementById('update-graph-file');
    if (!fileInput?.files?.length) return context.notify('请选择文件');
    var state = context.getState();
    try {
      var file = fileInput.files[0];
      validateUploadFiles([file]);
      var uploadResponse = await context.uploadFile(file);
      if (uploadResponse.code !== 200 || !uploadResponse.data?.url) throw new Error(uploadResponse.msg || '文件上传失败');
      var schemaUuid = state.graphData.schema_graph?.uuid
        || state.graphList.find(function(item) { return item.uuid === state.graphUuid; })?.schema_graph_uuid;
      var graphName = state.graphList.find(function(item) { return item.uuid === state.graphUuid; })?.name || state.graphUuid;
      var task = await context.taskManager.submit('knowledge_graph.update_knowledge_graph', '更新知识图谱', graphName, {
        uuid: state.graphUuid,
        user_token: context.getToken(),
        obj_data: { file_paths: [uploadResponse.data.url], data: { schema_graph_uuid: schemaUuid || '' } },
      });
      context.closeModal('modal-update-graph');
      fileInput.value = '';
      var label = document.getElementById('update-graph-file-label');
      if (label) label.textContent = '上传 PDF/Word/TXT 文档';
      await task.completion;
      await reloadGraph();
    } catch (error) {
      console.error('Update graph error:', error);
      context.notify(error.message || '更新失败');
    }
  }

  return {
    deleteEntity,
    deleteRelationship,
    deleteSelected,
    editEntity,
    editRelationship,
    editSelected,
    loadEntitiesForDropdowns,
    normalizeGraphAttributes,
    onUpdateFileSelected,
    reloadGraph,
    renderEntityDropdown,
    scheduleTooltipHide,
    showElementDetail,
    submitEntity,
    submitRelation,
    submitUpdateGraph,
    triggerUpdateFile,
  };
}
