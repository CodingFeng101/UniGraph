import { getGraphExpansionDepth } from '@/services/preferences';

export function createGraphExplorationController(context) {
  async function loadExplorationOverview() {
    context.setFullyExpanded(false);
    context.syncExpandButton();
    const response = await context.api.getExplorationOverview(context.getGraphUuid());
    if (response.code !== 200) throw new Error(response.msg || '加载图谱概览失败');
    context.setGraphData({
      entities: (response.data?.clusters || []).map((cluster) => ({
        uuid: `__server_cluster__${encodeURIComponent(cluster.type)}`,
        name: `${cluster.type} · ${cluster.count}`,
        type: cluster.type,
        attributes: {},
        is_cluster: true,
        cluster_count: cluster.count,
      })),
      relationships: (response.data?.relationships || []).map((item, index) => ({
        uuid: `__server_cluster_edge__${index}`,
        name: String(item.count),
        type: 'cluster',
        source_entity_uuid: `__server_cluster__${encodeURIComponent(item.source_type)}`,
        target_entity_uuid: `__server_cluster__${encodeURIComponent(item.target_type)}`,
        attributes: {},
      })),
      schema_graph: null,
    });
    context.renderGraph();
  }

  async function expandLoadGraph() {
    if (context.getGraphStyle() !== 'load' || !context.getGraphUuid() || context.isFullyExpanded()) return;
    context.syncExpandButton(true);
    try {
      const response = await context.api.getDetail(context.getGraphUuid());
      if (response.code !== 200 || !response.data) throw new Error(response.msg || '加载完整图谱失败');
      const graphData = {
        entities: response.data.entities || [],
        relationships: response.data.relationships || [],
        schema_graph: response.data.schema_graph || null,
      };
      context.setGraphData(graphData);
      context.setFullGraphData({
        entities: graphData.entities.slice(),
        relationships: graphData.relationships.slice(),
        schema_graph: graphData.schema_graph,
      });
      context.setFullyExpanded(true);
      context.renderGraph();
      context.notify(`已显示全部 ${graphData.entities.length} 个实体和 ${graphData.relationships.length} 条关系`);
    } catch (error) {
      context.notify(error.message || '加载完整图谱失败');
    } finally {
      context.syncExpandButton();
    }
  }

  async function changeGraphStyle(style) {
    context.setGraphStyle(style);
    if (style === 'load') {
      try { await loadExplorationOverview(); } catch (error) {
        context.notify(error.message || '加载图谱概览失败');
        return;
      }
    } else {
      const full = context.getFullGraphData();
      if (!full.entities.length) await context.loadGraphDetail(context.getGraphUuid());
      else {
        context.setGraphData({
          entities: full.entities.slice(), relationships: full.relationships.slice(), schema_graph: full.schema_graph,
        });
        context.renderGraph();
      }
    }
    document.querySelectorAll('[data-build-graph-style]').forEach((button) => {
      const active = button.dataset.buildGraphStyle === style;
      button.style.background = active ? 'var(--claude-primary)' : 'transparent';
      button.style.color = active ? 'var(--claude-primary-foreground)' : 'var(--claude-muted-foreground)';
    });
    context.syncExpandButton();
    context.notify('已切换图谱样式');
  }

  function captureView(anchorUuid) {
    const cy = context.getCy();
    return cy ? context.renderer.captureView(cy, anchorUuid) : null;
  }

  function mergeExplorationData(data, removeType, anchorUuid) {
    const current = context.getGraphData();
    const clusterUuid = removeType ? `__server_cluster__${encodeURIComponent(removeType)}` : null;
    const viewState = captureView(anchorUuid || clusterUuid);
    const existingIds = new Set(current.entities.map((entity) => entity.uuid));
    const entityMap = new Map(current.entities
      .filter((entity) => !(entity.is_cluster && entity.type === removeType))
      .map((entity) => [entity.uuid, entity]));
    (data.entities || []).forEach((entity) => entityMap.set(entity.uuid, entity));
    const relationshipMap = new Map(current.relationships.map((item) => [item.uuid, item]));
    (data.relationships || []).forEach((item) => relationshipMap.set(item.uuid, item));
    if (clusterUuid) relationshipMap.forEach((item, uuid) => {
      if (item.source_entity_uuid === clusterUuid || item.target_entity_uuid === clusterUuid) relationshipMap.delete(uuid);
    });
    context.setGraphData({ ...current, entities: [...entityMap.values()], relationships: [...relationshipMap.values()] });
    context.renderGraph(viewState);
    const cy = context.getCy();
    if (cy?._engine === 'vis-network') {
      window.requestAnimationFrame(() => cy?.refreshConnections?.());
      return;
    }
    const newNodes = cy.nodes().filter((node) => !existingIds.has(node.id()));
    if (!newNodes.length) return;
    newNodes.forEach((node) => {
      const targetPosition = node.position();
      node.position(viewState.anchorPosition);
      node.style('opacity', 0);
      node.animate({ position: targetPosition, style: { opacity: 1 }, duration: 520, easing: 'ease-out-cubic' });
    });
    window.setTimeout(() => {
      const liveCy = context.getCy();
      if (!liveCy || liveCy.destroyed()) return;
      liveCy.elements().filter((element) => element.visible()).layout({
        name: 'fcose', quality: 'draft', randomize: false, animate: true, animationDuration: 650,
        animationEasing: 'ease-out-cubic', fit: false, idealEdgeLength: 120, nodeRepulsion: 7200,
        gravity: 0.18, avoidOverlap: true,
      }).run();
    }, 540);
  }

  async function loadExplorationType(type) {
    try {
      const response = await context.api.getExplorationType(context.getGraphUuid(), type);
      if (response.code !== 200) throw new Error(response.msg || '展开实体类型失败');
      mergeExplorationData(response.data || {}, type);
    } catch (error) { context.notify(error.message || '展开实体类型失败'); }
  }

  async function loadExplorationNeighbors(entityUuid) {
    try {
      const response = await context.api.getExplorationNeighbors(
        context.getGraphUuid(), entityUuid, getGraphExpansionDepth(),
      );
      if (response.code !== 200) throw new Error(response.msg || '展开邻居失败');
      mergeExplorationData(response.data || {}, null, entityUuid);
    } catch (error) { context.notify(error.message || '展开邻居失败'); }
  }

  return { changeGraphStyle, expandLoadGraph, loadExplorationNeighbors, loadExplorationOverview, loadExplorationType };
}
