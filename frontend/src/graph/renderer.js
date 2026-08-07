import { DataSet } from 'vis-data';
import { Network } from 'vis-network';

/**
 * 知识图谱可视化模块
 * 沿用旧项目 Cytoscape.js 默认样式
 * 节点：白色填充椭圆(52x52)，彩色边框，按 type 分配颜色
 * 边：灰蓝贝塞尔曲线，三角箭头
 */

export const GraphRenderer = window.GraphRenderer = {
  /** 6 色调色板（与旧项目一致） */
  palette: ['#5b9cff', '#41bfa6', '#9b7bea', '#e8a34a', '#6f8fb8', '#e8799a'],

  /** 默认回退色 */
  defaultColor: '#A2B9D2',

  /** 高亮色 */
  highlightColor: '#FF5252',

  /** Only the load mode groups graphs at or above this node count. */
  clusterThreshold: 150,

  /** 保存原始颜色，用于恢复高亮 */
  originalColors: new Map(),

  /**
   * 按 type 生成颜色映射
   * @param {array} types - 类型数组
   * @returns {object} { typeName: color }
   */
  generateTypeColorMap(types) {
    const map = {};
    types.forEach((type, i) => {
      map[type] = this.palette[i % this.palette.length];
    });
    return map;
  },

  generateLoadColorMap(types) {
    const lightHex = '89ABCDEF';
    const map = {};
    types.forEach((type) => {
      let hash = 2166136261;
      for (const char of String(type)) {
        hash ^= char.charCodeAt(0);
        hash = Math.imul(hash, 16777619);
      }
      let color = '#';
      for (let index = 0; index < 6; index += 1) {
        hash = Math.imul(hash ^ (hash >>> 13), 1274126177);
        color += lightHex[(hash >>> 0) % lightHex.length];
      }
      map[type] = color;
    });
    return map;
  },

  normalizeAttributes(value) {
    if (!value) return {};
    if (typeof value === 'object') return value;
    try {
      const parsed = JSON.parse(value);
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (error) {
      return {};
    }
  },

  /**
   * 将后端实体数据转换为 Cytoscape 节点格式
   * @param {array} entities - 实体列表
   * @param {object} _typeColorMap - 类型颜色映射（节点颜色已写入数据）
   */
  entitiesToNodes(entities, typeColorMap, degreeMap = {}) {
    return entities.map((entity) => {
      const type = entity.type || entity.group || 'default';
      const color = typeColorMap[type] || this.defaultColor;
      const normalizedEntity = {
        ...entity,
        attributes: this.normalizeAttributes(entity.attributes),
      };
      return {
        data: {
          id: entity.uuid,
          label: entity.name,
          type: type,
          color: color,
          size: 20 + Math.log((degreeMap[entity.uuid] || 0) + 1) * 8,
          attributes: normalizedEntity.attributes,
          isCluster: Boolean(entity.is_cluster),
          clusterCount: Number(entity.cluster_count || 0),
          raw: normalizedEntity,
        },
      };
    });
  },

  /**
   * 将后端关系数据转换为 Cytoscape 边格式
   * @param {array} relationships - 关系列表
   */
  relationshipsToEdges(relationships) {
    return relationships.map((rel) => ({
      data: {
        id: rel.uuid,
        source: rel.source_entity_uuid,
        target: rel.target_entity_uuid,
        label: rel.name,
        type: rel.type,
        raw: rel,
      },
    }));
  },

  /**
   * 获取适合节点数量的布局算法
   * @param {number} nodeCount - 节点数
   */
  getBestLayout(nodeCount) {
    if (nodeCount <= 20) {
      return {
        name: 'cose-bilkent',
        idealEdgeLength: 200,
        nodeRepulsion: 10000,
        numIter: 3000,
        randomize: true,
        animate: true,
        fit: true,
        padding: 50,
        nodeDimensionsIncludeLabels: true,
      };
    } else if (nodeCount <= 100) {
      return {
        name: 'fcose',
        idealEdgeLength: 180,
        nodeRepulsion: 12000,
        numIter: 2500,
        initialTemp: 200,
        coolingFactor: 0.95,
        avoidOverlap: true,
        animate: true,
        fit: true,
        padding: 50,
        nodeDimensionsIncludeLabels: true,
      };
    } else {
      return {
        name: 'fcose',
        quality: nodeCount <= 400 ? 'default' : 'draft',
        randomize: true,
        idealEdgeLength: nodeCount <= 400 ? 220 : 190,
        nodeRepulsion: nodeCount <= 400 ? 18000 : 15000,
        componentSpacing: nodeCount <= 400 ? 200 : 160,
        gravity: 0.08,
        avoidOverlap: true,
        animate: false,
        fit: true,
        padding: 50,
        nodeDimensionsIncludeLabels: true,
      };
    }
  },

  /**
   * 获取默认样式表（与旧项目 default 样式一致）
   * @param {object} typeColorMap - 类型颜色映射
   */
  getStylesheet(_typeColorMap) {
        return [
      // 通用节点样式
      {
        selector: 'node',
        style: {
          label: 'data(label)',
          shape: 'ellipse',
          'text-valign': 'center',
          'text-halign': 'center',
          'background-color': 'data(color)',
          color: '#000000',
          'font-size': '12px',
          width: 'data(size)',
          height: 'data(size)',
          'text-wrap': 'wrap',
          'text-max-width': '100px',
          'text-outline-width': 2,
          'text-outline-color': 'data(color)',
          'text-background-opacity': 0.8,
          'text-background-color': 'data(color)',
          'text-background-padding': '3px',
          'border-width': 2,
          'border-color': '#ffffff',
          'border-opacity': 0.8,
        },
      },
      // 选中态
      {
        selector: ':selected',
        style: {
          'border-width': 4,
          'border-color': '#a0502f',
        },
      },
      // 通用边样式
      {
        selector: 'edge',
        style: {
          label: 'data(label)',
          'text-rotation': 'autorotate',
          'text-margin-y': '-12px',
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 1.5,
          width: 2,
          'line-color': 'data(color)',
          'target-arrow-color': 'data(color)',
          'text-outline-width': 2,
          'text-outline-color': '#ffffff',
          color: '#000000',
          'font-size': '10px',
          'text-background-opacity': 0.7,
          'text-background-color': '#ffffff',
          'text-background-padding': '2px',
        },
      },
      // 边选中态
      {
        selector: 'edge:selected',
        style: {
          width: 3,
          'line-color': '#FF5252',
          'target-arrow-color': '#FF5252',
        },
      },
    ];
  },

  /**
   * Apply one of the five graph display modes from the original project.
   * The load mode keeps Cytoscape's interaction API but removes expensive
   * labels, curves, shadows, and overlays for larger graphs.
   */
  applyStyle(cy, mode = 'default') {
    if (!cy) return;
    const selectedMode = ['default', 'database', 'minimal', 'colorful', 'load'].includes(mode)
      ? mode
      : 'default';

    if (selectedMode !== 'load') this.disableLoadClusters(cy);

    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const color = node.data('color') || this.defaultColor;
        const size = node.data('size') || 36;
        const common = {
          width: size,
          height: size,
          label: 'data(label)',
          'font-size': '12px',
          'text-wrap': 'wrap',
          'text-max-width': '100px',
          'overlay-opacity': 0,
          'shadow-opacity': 0,
        };

        if (selectedMode === 'database') {
          node.style({
            ...common,
            shape: 'round-rectangle',
            width: Math.max(size + 28, 72),
            height: Math.max(size, 36),
            'background-color': '#f8f9fa',
            'border-width': 1,
            'border-color': '#ced4da',
            color: '#111827',
            'font-weight': 600,
            'text-valign': 'center',
            'text-halign': 'center',
            'text-outline-width': 2,
            'text-outline-color': '#ffffff',
            'text-background-opacity': 0.96,
            'text-background-color': '#ffffff',
            'text-background-padding': 3,
          });
          return;
        }

        if (selectedMode === 'minimal') {
          node.style({
            ...common,
            shape: 'ellipse',
            width: Math.max(size + 18, 52),
            height: Math.max(size + 8, 42),
            'background-color': '#f1f3f5',
            'border-width': 0,
            color: '#111827',
            'font-weight': 600,
            'text-valign': 'center',
            'text-halign': 'center',
            'text-margin-y': 0,
            'text-outline-width': 2,
            'text-outline-color': '#ffffff',
            'text-background-opacity': 0.94,
            'text-background-color': '#ffffff',
            'text-background-padding': 3,
          });
          return;
        }

        if (selectedMode === 'colorful') {
          node.style({
            ...common,
            shape: 'ellipse',
            'background-color': color,
            'border-width': 3,
            'border-color': '#ffffff',
            'border-opacity': 0.8,
            color: '#ffffff',
            'font-weight': 600,
            'text-valign': 'center',
            'text-halign': 'center',
            'text-outline-width': 0,
            'text-background-opacity': 0,
            'shadow-blur': 10,
            'shadow-color': color,
            'shadow-opacity': 0.3,
          });
          return;
        }

        if (selectedMode === 'load') {
          if (node.data('isCluster')) {
            node.style({
              ...common,
              shape: 'ellipse',
              label: 'data(label)',
              width: Math.min(96, 58 + Math.log2((node.data('clusterCount') || 1) + 1) * 7),
              height: Math.min(96, 58 + Math.log2((node.data('clusterCount') || 1) + 1) * 7),
              'background-color': color,
              'border-width': 3,
              'border-color': '#ffffff',
              color: '#1c1917',
              'font-size': 11,
              'font-weight': 600,
              'text-valign': 'center',
              'text-halign': 'center',
              'text-outline-width': 2,
              'text-outline-color': '#ffffff',
              'text-background-opacity': 0.88,
              'text-background-color': '#ffffff',
              'text-background-padding': 3,
            });
            return;
          }
          node.style({
            ...common,
            shape: 'ellipse',
            label: 'data(label)',
            width: Math.max(38, Math.min(size + 18, 62)),
            height: Math.max(38, Math.min(size + 18, 62)),
            'background-color': color,
            'border-width': 2,
            'border-color': '#ffffff',
            color: '#1c1917',
            'font-size': 10,
            'font-weight': 600,
            'text-outline-width': 2,
            'text-outline-color': '#ffffff',
            'text-background-opacity': 0.82,
            'text-background-color': '#ffffff',
            'text-background-padding': 2,
          });
          return;
        }

        node.style({
          ...common,
          shape: 'ellipse',
          'background-color': color,
          'border-width': 1,
          'border-color': '#ffffff',
          'border-opacity': 0.8,
          color: '#000000',
          'font-weight': 400,
          'text-valign': 'center',
          'text-halign': 'center',
          'text-outline-width': 2,
          'text-outline-color': color,
          'text-background-opacity': 1,
          'text-background-color': color,
          'text-background-padding': '2px',
        });
      });

      cy.edges().forEach((edge) => {
        const color = edge.data('color') || this.defaultColor;
        if (selectedMode === 'database') {
          edge.style({
            label: 'data(label)',
            width: 1,
            'line-color': '#adb5bd',
            'target-arrow-color': '#adb5bd',
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'line-style': 'solid',
            'shadow-opacity': 0,
          });
          return;
        }
        if (selectedMode === 'minimal') {
          edge.style({
            label: 'data(label)',
            width: 1,
            'line-color': '#dee2e6',
            'target-arrow-color': '#dee2e6',
            'curve-style': 'straight',
            'target-arrow-shape': 'none',
            'line-style': 'dashed',
            'shadow-opacity': 0,
          });
          return;
        }
        if (selectedMode === 'colorful') {
          edge.style({
            label: 'data(label)',
            width: 2,
            'line-color': color,
            'target-arrow-color': color,
            'curve-style': 'unbundled-bezier',
            'target-arrow-shape': 'triangle',
            'line-style': 'solid',
            'shadow-opacity': 0,
          });
          return;
        }
        if (selectedMode === 'load') {
          edge.style({
            label: '',
            width: 1,
            'line-color': '#9ca3af',
            'target-arrow-color': '#9ca3af',
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 0.7,
            'line-style': 'solid',
            'overlay-opacity': 0,
            'shadow-opacity': 0,
            color: '#44403c',
            'font-size': 9,
            'text-outline-width': 2,
            'text-outline-color': '#ffffff',
          });
          return;
        }
        edge.style({
          label: 'data(label)',
          width: 1.5,
          'line-color': color,
          'target-arrow-color': color,
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 1.5,
          'line-style': 'solid',
          'shadow-opacity': 0,
        });
      });
    });

    if (
      selectedMode === 'load'
      && !cy.scratch('_serverExploration')
      && cy.nodes().not('.graph-cluster').length >= this.clusterThreshold
    ) {
      this.enableLoadClusters(cy);
    }
    cy.nodes('[isCluster]').style({
      label: 'data(label)',
      'border-width': 3,
      'border-color': '#ffffff',
      color: '#1c1917',
      'font-size': 11,
      'font-weight': 600,
      'text-valign': 'center',
      'text-halign': 'center',
      'text-outline-width': 2,
      'text-outline-color': '#ffffff',
      'text-background-opacity': 0.9,
      'text-background-color': '#ffffff',
      'text-background-padding': 3,
    });
  },

  clusterId(type) {
    return `__graph_cluster__${encodeURIComponent(type)}`;
  },

  disableLoadClusters(cy) {
    const state = cy?.scratch('_loadClusterState');
    if (!state) return;
    cy.batch(() => {
      cy.elements('.graph-cluster, .graph-cluster-edge').remove();
      state.nodes.show();
      state.edges.show();
    });
    cy.removeScratch('_loadClusterState');
  },

  enableLoadClusters(cy) {
    let state = cy.scratch('_loadClusterState');
    if (!state) {
      state = {
        nodes: cy.nodes().not('.graph-cluster'),
        edges: cy.edges().not('.graph-cluster-edge'),
        expandedTypes: new Set(),
      };
      cy.scratch('_loadClusterState', state);
    }
    this.rebuildLoadClusters(cy);
  },

  rebuildLoadClusters(cy) {
    const state = cy.scratch('_loadClusterState');
    if (!state) return;
    const renderer = this;
    const groups = new Map();
    const expansion = cy.scratch('_clusterExpandAnchor');

    state.nodes.forEach((node) => {
      const type = String(node.data('type') || '未分类');
      if (!groups.has(type)) groups.set(type, []);
      groups.get(type).push(node);
    });

    cy.batch(() => {
      cy.elements('.graph-cluster, .graph-cluster-edge').remove();
      state.nodes.hide();
      state.edges.hide();

      groups.forEach((nodes, type) => {
        if (state.expandedTypes.has(type)) {
          nodes.forEach((node, index) => {
            node.show();
            if (expansion?.type === type) {
              const angle = (Math.PI * 2 * index) / Math.max(nodes.length, 1);
              node.position({
                x: expansion.position.x + Math.cos(angle) * 8,
                y: expansion.position.y + Math.sin(angle) * 8,
              });
              node.style('opacity', 0.15);
            }
          });
          return;
        }
        const color = nodes[0]?.data('color') || renderer.defaultColor;
        cy.add({
          group: 'nodes',
          classes: 'graph-cluster',
          data: {
            id: renderer.clusterId(type),
            label: `${type} · ${nodes.length}`,
            type,
            color,
            clusterCount: nodes.length,
            isCluster: true,
          },
        });
      });

      const aggregateEdges = new Map();
      state.edges.forEach((edge) => {
        const source = edge.source();
        const target = edge.target();
        const sourceType = String(source.data('type') || '未分类');
        const targetType = String(target.data('type') || '未分类');
        const sourceId = state.expandedTypes.has(sourceType) ? source.id() : renderer.clusterId(sourceType);
        const targetId = state.expandedTypes.has(targetType) ? target.id() : renderer.clusterId(targetType);

        if (sourceId === targetId) return;
        if (state.expandedTypes.has(sourceType) && state.expandedTypes.has(targetType)) {
          edge.show();
          return;
        }

        const key = `${sourceId}\u0000${targetId}`;
        const current = aggregateEdges.get(key) || {
          source: sourceId,
          target: targetId,
          count: 0,
          color: source.data('color') || renderer.defaultColor,
        };
        current.count += 1;
        aggregateEdges.set(key, current);
      });

      aggregateEdges.forEach((edge, key) => {
        cy.add({
          group: 'edges',
          classes: 'graph-cluster-edge',
          data: {
            id: `__graph_cluster_edge__${encodeURIComponent(key)}`,
            source: edge.source,
            target: edge.target,
            label: String(edge.count),
            count: edge.count,
            color: edge.color,
            isClusterEdge: true,
          },
        });
      });

      cy.nodes('.graph-cluster').style({
        shape: 'ellipse',
        label: 'data(label)',
        width: 54,
        height: 54,
        'background-color': 'data(color)',
        'border-width': 3,
        'border-color': '#ffffff',
        color: '#1c1917',
        'font-size': 11,
        'font-weight': 600,
        'text-valign': 'center',
        'text-halign': 'center',
        'text-outline-width': 2,
        'text-outline-color': '#ffffff',
        'text-background-opacity': 0.9,
        'text-background-color': '#ffffff',
        'text-background-padding': 3,
        'shadow-opacity': 0,
      });
      cy.edges('.graph-cluster-edge').style({
        label: 'data(label)',
        width: 'mapData(count, 1, 50, 1, 5)',
        'line-color': 'data(color)',
        'target-arrow-color': 'data(color)',
        'curve-style': 'straight',
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.8,
        color: '#78716c',
        'font-size': 9,
        'text-background-color': '#ffffff',
        'text-background-opacity': 0.85,
        'text-background-padding': 2,
      });
    });

    const visible = cy.elements().filter((element) => element.visible());
    visible.layout({
      name: 'fcose',
      quality: 'draft',
      randomize: !expansion,
      animate: Boolean(expansion),
      animationDuration: 520,
      animationEasing: 'ease-out-cubic',
      fit: true,
      padding: 52,
      idealEdgeLength: 110,
      nodeRepulsion: 6500,
      avoidOverlap: true,
    }).run();
    if (expansion) {
      state.nodes.filter(function(node) {
        return String(node.data('type') || '未分类') === expansion.type;
      }).animate({ style: { opacity: 1 } }, { duration: 420, easing: 'ease-out-cubic' });
      cy.removeScratch('_clusterExpandAnchor');
    }
  },

  expandLoadCluster(cy, type) {
    const state = cy?.scratch('_loadClusterState');
    if (!state || state.expandedTypes.has(type)) return false;
    const cluster = cy.getElementById(this.clusterId(type));
    cy.scratch('_clusterExpandAnchor', {
      type,
      position: cluster.length ? cluster.position() : { x: cy.width() / 2, y: cy.height() / 2 },
    });
    state.expandedTypes.add(type);
    this.rebuildLoadClusters(cy);
    return true;
  },

  /**
   * 初始化 Cytoscape 图谱
   * @param {string} containerId - 容器元素 ID
   * @param {array} entities - 实体列表
   * @param {array} relationships - 关系列表
   * @param {object} callbacks - 回调函数 { onNodeClick, onEdgeClick, onCanvasClick }
   * @returns {object} cytoscape 实例
   */
  init(containerId, entities = [], relationships = [], callbacks = {}) {
    const container = document.getElementById(containerId);
    if (!container) return null;

    if (callbacks.mode === 'load') {
      return this.initLoadNetwork(container, entities, relationships, callbacks);
    }

    // 提取所有类型
    const types = [...new Set(entities.map((e) => e.type || e.group || 'default'))];
    const typeColorMap = this.generateTypeColorMap(types);

    // 转换数据
    const edges = this.relationshipsToEdges(relationships);
    const degreeMap = {};
    edges.forEach(({ data }) => {
      degreeMap[data.source] = (degreeMap[data.source] || 0) + 1;
      degreeMap[data.target] = (degreeMap[data.target] || 0) + 1;
    });
    const nodes = this.entitiesToNodes(entities, typeColorMap, degreeMap);
    const nodeColors = Object.fromEntries(nodes.map(({ data }) => [data.id, data.color]));
    edges.forEach(({ data }) => {
      data.color = nodeColors[data.source] || this.defaultColor;
    });

    // 选择布局
    if (callbacks.positions) {
      const fallback = callbacks.anchorPosition || { x: 0, y: 0 };
      let offsetIndex = 0;
      nodes.forEach((node) => {
        const saved = callbacks.positions[node.data.id];
        if (saved) {
          node.position = saved;
          return;
        }
        const angle = (offsetIndex % 16) * (Math.PI * 2 / 16);
        const ring = Math.floor(offsetIndex / 16) + 1;
        node.position = {
          x: fallback.x + Math.cos(angle) * 85 * ring,
          y: fallback.y + Math.sin(angle) * 85 * ring,
        };
        offsetIndex += 1;
      });
    }

    const useClusters = callbacks.mode === 'load'
      && !callbacks.serverExploration
      && nodes.length >= this.clusterThreshold;
    const layout = callbacks.positions
      ? { name: 'preset', animate: false, fit: false }
      : useClusters
      ? { name: 'grid', animate: false, fit: false, avoidOverlap: false }
      : this.getBestLayout(nodes.length);

    // 初始化 Cytoscape
    const cy = window.cytoscape({
      container: container,
      elements: [...nodes, ...edges],
      style: this.getStylesheet(typeColorMap),
      layout: layout,
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.3,
      pixelRatio: callbacks.mode === 'load' && nodes.length > 800 ? 1 : 'auto',
      hideEdgesOnViewport: callbacks.mode === 'load' && nodes.length > 300,
      textureOnViewport: callbacks.mode === 'load' && nodes.length > 300,
    });

    if (callbacks.serverExploration) cy.scratch('_serverExploration', true);
    this.applyStyle(cy, callbacks.mode || 'default');
    if (callbacks.mode === 'load') {
      const updateLoadLabels = () => {
        const visible = cy.zoom() >= 0.62;
        cy.nodes().not('[isCluster]').style('label', visible ? 'data(label)' : '');
        cy.edges().not('[isClusterEdge]').style('label', visible ? 'data(label)' : '');
      };
      cy.on('zoom', updateLoadLabels);
      updateLoadLabels();
    }
    if (callbacks.viewport) {
      cy.zoom(callbacks.viewport.zoom);
      cy.pan(callbacks.viewport.pan);
    }

    // 绑定交互事件
    let lastNodeTap = { id: '', time: 0 };
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const now = Date.now();
      const isDoubleTap = lastNodeTap.id === node.id() && now - lastNodeTap.time <= 360;
      lastNodeTap = { id: node.id(), time: now };
      if (node.data('isCluster')) {
        if (isDoubleTap) {
          const expanded = this.expandLoadCluster(cy, String(node.data('type') || '未分类'));
          if (!expanded && callbacks.onClusterDoubleClick) {
            callbacks.onClusterDoubleClick(node.data(), node);
          }
          lastNodeTap = { id: '', time: 0 };
        }
        return;
      }
      if (isDoubleTap && callbacks.onNodeDoubleClick) {
        callbacks.onNodeDoubleClick(node.data(), node);
        lastNodeTap = { id: '', time: 0 };
        return;
      }
      if (callbacks.onNodeClick) callbacks.onNodeClick(node.data(), node);
    });
    if (callbacks.onEdgeClick) {
      cy.on('tap', 'edge', (evt) => callbacks.onEdgeClick(evt.target.data(), evt.target));
    }
    if (callbacks.onNodeHover) {
      cy.on('mouseover', 'node', (evt) => callbacks.onNodeHover(
        evt.target.data(), evt.target, evt.target.renderedPosition()
      ));
    }
    if (callbacks.onEdgeHover) {
      cy.on('mouseover', 'edge', (evt) => callbacks.onEdgeHover(
        evt.target.data(), evt.target, evt.target.renderedMidpoint()
      ));
    }
    if (callbacks.onElementLeave) {
      cy.on('mouseout', 'node, edge', () => callbacks.onElementLeave());
    }
    if (callbacks.onCanvasClick) {
      cy.on('tap', (evt) => {
        if (evt.target === cy) callbacks.onCanvasClick();
      });
    }

    return cy;
  },

  initLoadNetwork(container, entities, relationships, callbacks = {}) {
    const types = [...new Set(entities.map((entity) => entity.type || entity.group || 'default'))];
    const typeColorMap = this.generateLoadColorMap(types);
    const degreeMap = {};
    relationships.forEach((relationship) => {
      degreeMap[relationship.source_entity_uuid] = (degreeMap[relationship.source_entity_uuid] || 0) + 1;
      degreeMap[relationship.target_entity_uuid] = (degreeMap[relationship.target_entity_uuid] || 0) + 1;
    });

    const fallback = callbacks.anchorPosition || { x: 0, y: 0 };
    let newNodeIndex = 0;
    const nodeItems = entities.map((entity) => {
      const type = entity.type || entity.group || 'default';
      const color = typeColorMap[type] || this.defaultColor;
      const saved = callbacks.positions?.[entity.uuid];
      const angle = (newNodeIndex % 18) * (Math.PI * 2 / 18);
      const ring = Math.floor(newNodeIndex / 18) + 1;
      if (!saved) newNodeIndex += 1;
      return {
        id: entity.uuid,
        uuid: entity.uuid,
        label: entity.name,
        type,
        attributes: this.normalizeAttributes(entity.attributes),
        raw: { ...entity, attributes: this.normalizeAttributes(entity.attributes) },
        isCluster: Boolean(entity.is_cluster),
        clusterCount: Number(entity.cluster_count || 0),
        shape: 'ellipse',
        size: 10 + Math.log((degreeMap[entity.uuid] || 0) + 1) * 5,
        color: {
          background: color,
          highlight: { background: '#FF5252', border: '#FF5252' },
          hover: { background: color, border: color },
        },
        baseColor: color,
        borderWidth: 2,
        borderWidthSelected: 4,
        font: {
          color: '#000000',
          size: 12,
          face: 'arial',
          strokeWidth: 0,
        },
        x: saved?.x ?? fallback.x + Math.cos(angle) * 14 * ring,
        y: saved?.y ?? fallback.y + Math.sin(angle) * 14 * ring,
      };
    });
    const nodeIds = new Set(nodeItems.map((item) => item.id));
    const nodeColorMap = Object.fromEntries(nodeItems.map((node) => [node.id, node.baseColor]));
    const edgeItems = relationships
      .filter((relationship) => nodeIds.has(relationship.source_entity_uuid) && nodeIds.has(relationship.target_entity_uuid))
      .map((relationship) => ({
        id: relationship.uuid,
        uuid: relationship.uuid,
        from: relationship.source_entity_uuid,
        to: relationship.target_entity_uuid,
        label: relationship.name,
        type: relationship.type,
        raw: relationship,
        arrows: { to: { enabled: true, scaleFactor: 1 } },
        color: {
          color: nodeColorMap[relationship.source_entity_uuid] || this.defaultColor,
          highlight: nodeColorMap[relationship.source_entity_uuid] || this.defaultColor,
          hover: nodeColorMap[relationship.source_entity_uuid] || this.defaultColor,
          opacity: 1,
        },
        width: 1,
        hoverWidth: 0,
        selectionWidth: 1,
        background: { enabled: true, color: '#E4F1FE' },
        smooth: { enabled: true, type: 'dynamic', roundness: 0.5 },
        font: {
          color: '#000000',
          size: 12,
          face: 'arial',
          align: 'top',
        },
      }));

    const nodeData = new DataSet(nodeItems);
    const edgeData = new DataSet(edgeItems);
    let settleTimer = null;
    let destroyed = false;
    const stopSimulationSoon = (delay = 650) => {
      if (settleTimer) window.clearTimeout(settleTimer);
      settleTimer = window.setTimeout(() => {
        if (!destroyed) network.stopSimulation();
      }, delay);
    };
    const network = new Network(container, { nodes: nodeData, edges: edgeData }, {
      autoResize: true,
      nodes: {
        shape: 'ellipse',
        size: 30,
        font: { size: 14, face: 'arial', color: 'black' },
        borderWidth: 2,
        borderWidthSelected: 4,
        labelHighlightBold: false,
      },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 1 } },
        color: '#A2B9D2',
        font: { align: 'top' },
        background: { enabled: true, color: '#E4F1FE' },
        smooth: { enabled: true, type: 'dynamic', roundness: 0.5 },
      },
      interaction: {
        hover: true,
        hoverConnectedEdges: true,
        dragNodes: true,
        dragView: true,
        zoomView: true,
        multiselect: true,
        navigationButtons: false,
        keyboard: false,
        tooltipDelay: 120,
      },
      physics: {
        enabled: true,
        solver: 'barnesHut',
        stabilization: {
          enabled: !callbacks.viewport,
          iterations: 200,
          updateInterval: 50,
          fit: !callbacks.viewport,
        },
        barnesHut: {
          gravitationalConstant: -2200,
          centralGravity: 0.03,
          springLength: 250,
          springConstant: 0.03,
          damping: 0.42,
          avoidOverlap: 0.65,
        },
        maxVelocity: 12,
        minVelocity: 0.45,
        timestep: 0.32,
        adaptiveTimestep: true,
      },
      layout: { improvedLayout: true, randomSeed: 17 },
    });

    network.once('stabilizationIterationsDone', () => {
      if (!callbacks.viewport) {
        network.fit({ animation: { duration: 420, easingFunction: 'easeInOutQuad' } });
      }
      stopSimulationSoon(520);
    });

    if (callbacks.viewport) {
      network.once('afterDrawing', () => {
        network.moveTo({
          position: callbacks.viewport.pan,
          scale: callbacks.viewport.zoom,
          animation: false,
        });
        stopSimulationSoon(900);
      });
    }

    network.on('click', (params) => {
      if (params.nodes.length && callbacks.onNodeClick) {
        const data = nodeData.get(params.nodes[0]);
        callbacks.onNodeClick(data, data);
      } else if (params.edges.length && callbacks.onEdgeClick) {
        const data = edgeData.get(params.edges[0]);
        callbacks.onEdgeClick(data, data);
      } else if (callbacks.onCanvasClick) {
        callbacks.onCanvasClick();
      }
    });
    network.on('doubleClick', (params) => {
      if (!params.nodes.length) return;
      const data = nodeData.get(params.nodes[0]);
      if (data?.isCluster && callbacks.onClusterDoubleClick) callbacks.onClusterDoubleClick(data, data);
      else if (callbacks.onNodeDoubleClick) callbacks.onNodeDoubleClick(data, data);
    });
    network.on('dragEnd', (params) => {
      if (!params.nodes.length) return;
      network.startSimulation();
      stopSimulationSoon(420);
    });
    network.on('hoverNode', (params) => {
      if (!callbacks.onNodeHover) return;
      const data = nodeData.get(params.node);
      callbacks.onNodeHover(data, data, params.pointer?.DOM || network.getPositions([params.node])[params.node]);
    });
    network.on('hoverEdge', (params) => {
      if (!callbacks.onEdgeHover) return;
      const data = edgeData.get(params.edge);
      callbacks.onEdgeHover(data, data, params.pointer?.DOM || { x: 0, y: 0 });
    });
    if (callbacks.onElementLeave) {
      network.on('blurNode', callbacks.onElementLeave);
      network.on('blurEdge', callbacks.onElementLeave);
    }

    const facade = {
      _engine: 'vis-network',
      _network: network,
      _nodes: nodeData,
      _edges: edgeData,
      _destroyed: false,
      expandNeighborhood(nodeId, depth = 1) {
        if (this._destroyed || !nodeData.get(nodeId)) return;
        const maxDepth = Math.max(1, Math.min(5, Number(depth) || 1));
        const visited = new Set([nodeId]);
        let frontier = [nodeId];
        const rings = [];
        for (let hop = 1; hop <= maxDepth && frontier.length; hop += 1) {
          const next = [];
          frontier.forEach((id) => {
            network.getConnectedNodes(id).forEach((neighborId) => {
              if (visited.has(neighborId) || !nodeData.get(neighborId)) return;
              visited.add(neighborId);
              next.push(neighborId);
            });
          });
          if (next.length) rings.push(next);
          frontier = next;
        }
        const neighborIds = rings.flat();
        if (!neighborIds.length) return;
        const positions = network.getPositions([nodeId, ...neighborIds]);
        const anchor = positions[nodeId];
        rings.forEach((ring, ringIndex) => {
          const radius = Math.min(125 + ringIndex * 92, 480);
          ring.forEach((id, index) => {
            const position = positions[id];
            const dx = position.x - anchor.x;
            const dy = position.y - anchor.y;
            const angle = Math.hypot(dx, dy) > 1
              ? Math.atan2(dy, dx)
              : index * (Math.PI * 2 / ring.length);
            network.moveNode(
              id,
              anchor.x + Math.cos(angle) * radius,
              anchor.y + Math.sin(angle) * radius
            );
          });
        });
        network.startSimulation();
        this.refreshConnections();
        stopSimulationSoon(560);
      },
      refreshConnections() {
        if (this._destroyed) return;
        const visibleEdges = edgeData.get().map((edge) => ({
          id: edge.id,
          hidden: false,
          physics: true,
        }));
        if (visibleEdges.length) edgeData.update(visibleEdges);
        network.redraw();
        network.startSimulation();
        stopSimulationSoon(560);
      },
      destroy() {
        if (this._destroyed) return;
        destroyed = true;
        if (settleTimer) window.clearTimeout(settleTimer);
        network.stopSimulation();
        network.destroy();
        this._destroyed = true;
      },
      destroyed() { return this._destroyed; },
    };
    return facade;
  },

  captureView(graph, anchorId) {
    if (graph?._engine === 'vis-network') {
      const positions = graph._network.getPositions();
      return {
        positions,
        anchorPosition: positions[anchorId] || { x: 0, y: 0 },
        viewport: {
          zoom: graph._network.getScale(),
          pan: graph._network.getViewPosition(),
        },
      };
    }
    const positions = {};
    graph.nodes().forEach((node) => { positions[node.id()] = node.position(); });
    return {
      positions,
      anchorPosition: positions[anchorId] || { x: 0, y: 0 },
      viewport: { zoom: graph.zoom(), pan: graph.pan() },
    };
  },

  filter(graph, query, shouldFocus = false) {
    if (graph?._engine !== 'vis-network') return false;
    const search = String(query || '').trim().toLowerCase();
    const nodeMatches = [];
    const edgeMatches = [];
    graph._nodes.forEach((node) => {
      const matched = !search || String(node.label || node.type || '').toLowerCase().includes(search);
      if (matched && search) nodeMatches.push(node.id);
      graph._nodes.update({
        id: node.id,
        opacity: matched ? 1 : 0.14,
        font: { ...node.font, color: matched ? '#1c1917' : 'rgba(28,25,23,0.18)' },
      });
    });
    graph._edges.forEach((edge) => {
      const matched = !search || String(edge.label || edge.type || '').toLowerCase().includes(search);
      if (matched && search) edgeMatches.push(edge.id);
      graph._edges.update({
        id: edge.id,
        color: { ...edge.color, opacity: matched ? 0.78 : 0.08 },
      });
    });
    graph._network.unselectAll();
    if (nodeMatches.length) graph._network.selectNodes(nodeMatches, false);
    if (edgeMatches.length) graph._network.selectEdges(edgeMatches);
    if (shouldFocus && nodeMatches.length) {
      graph._network.focus(nodeMatches[0], {
        scale: Math.min(Math.max(graph._network.getScale(), 0.72), 1.15),
        animation: { duration: 320, easingFunction: 'easeInOutQuad' },
      });
    }
    return true;
  },

  /**
   * 高亮节点
   * @param {object} cy - cytoscape 实例
   * @param {string} nodeId - 节点 ID
   */
  highlightNode(cy, nodeId) {
    if (cy?._engine === 'vis-network') {
      cy._network.unselectAll();
      cy._network.selectNodes([nodeId]);
      cy._network.focus(nodeId, {
        scale: Math.min(Math.max(cy._network.getScale(), 0.72), 1.15),
        animation: { duration: 320, easingFunction: 'easeInOutQuad' },
      });
      return;
    }
    const node = cy.getElementById(nodeId);
    if (node.length === 0) return;

    // 保存原色
    const id = node.id();
    if (!this.originalColors.has(id)) {
      this.originalColors.set(id, {
        'background-color': node.style('background-color'),
        'border-color': node.style('border-color'),
        'border-width': node.style('border-width'),
      });
    }

    node.style({
      'background-color': this.highlightColor,
      'border-color': this.highlightColor,
      'border-width': 3,
    });

    // 聚焦动画
    cy.animate({
      fit: { eles: node, padding: 570 },
      duration: 500,
    });
  },

  /**
   * 高亮边
   * @param {object} cy - cytoscape 实例
   * @param {string} edgeId - 边 ID
   */
  highlightEdge(cy, edgeId) {
    if (cy?._engine === 'vis-network') {
      cy._network.unselectAll();
      cy._network.selectEdges([edgeId]);
      return;
    }
    const edge = cy.getElementById(edgeId);
    if (edge.length === 0) return;

    const id = edge.id();
    if (!this.originalColors.has(id)) {
      this.originalColors.set(id, {
        'line-color': edge.style('line-color'),
        'target-arrow-color': edge.style('target-arrow-color'),
        width: edge.style('width'),
      });
    }

    edge.style({
      'line-color': this.highlightColor,
      'target-arrow-color': this.highlightColor,
      width: 3,
    });

    cy.animate({
      fit: { eles: edge, padding: 500 },
      duration: 500,
    });
  },

  /**
   * 清除所有高亮
   * @param {object} cy - cytoscape 实例
   */
  clearHighlights(cy) {
    if (cy?._engine === 'vis-network') {
      cy._network.unselectAll();
      return;
    }
    this.originalColors.forEach((colors, id) => {
      const ele = cy.getElementById(id);
      if (ele.length > 0) {
        ele.style(colors);
      }
    });
    this.originalColors.clear();
  },

  /**
   * 缩放画布
   * @param {object} cy - cytoscape 实例
   * @param {number} factor - 缩放因子（正值放大，负值缩小）
   */
  zoom(cy, factor) {
    if (cy?._engine === 'vis-network') {
      const scale = Math.max(0.3, Math.min(3, cy._network.getScale() + factor));
      cy._network.moveTo({ scale, animation: { duration: 220, easingFunction: 'easeInOutQuad' } });
      return;
    }
    const zoom = cy.zoom();
    const newZoom = Math.max(cy.minZoom(), Math.min(cy.maxZoom(), zoom + factor));
    cy.zoom({ level: newZoom, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  },

  /** 适应画布 */
  fit(cy) {
    if (cy?._engine === 'vis-network') {
      cy._network.fit({ animation: { duration: 360, easingFunction: 'easeInOutQuad' } });
      return;
    }
    cy.fit(undefined, 52);
  },

  /** 导出为图片 */
  exportImage(cy) {
    if (cy?._engine === 'vis-network') {
      return cy._network.canvas?.frame?.canvas?.toDataURL('image/png')
        || cy._network.body?.container?.querySelector('canvas')?.toDataURL('image/png');
    }
    return cy.png({ full: true, scale: 0.28, bg: '#fdfbf7' });
  },
};
