import json
import uuid

import igraph as ig
import leidenalg as la

from ....model.community import Community


class CommunityDetection:
    def __init__(self, max_comm_size=20, max_level=0, seed=None):
        # 初始化社区检测参数
        self.max_comm_size = max_comm_size
        self.max_level = max_level
        self.seed = seed
        self.node_details_map = {}  # 存储节点详细信息的映射
        self.node_id_map = {}  # 存储节点ID的映射

    @staticmethod
    def calculate_and_update_degrees(entities, relationships) -> list:
        """
        计算并更新实体的度数

        :param entities: 实体列表
        :param relationships: 关系列表
        :return: 更新后的实体列表
        """
        degree_dict = {}

        for relationship in relationships:
            directional_entity = relationship.source
            directed_entity = relationship.target

            # 初始化度数为0
            if directional_entity not in degree_dict:
                degree_dict[directional_entity] = 0
            if directed_entity not in degree_dict:
                degree_dict[directed_entity] = 0

            # 增加度数
            degree_dict[directional_entity] += 1
            degree_dict[directed_entity] += 1

        for entity in entities:
            entity.attributes['degree'] = degree_dict[entity.id]

        return entities

    def recursive_leiden(self, graph, level=0, prefix='', node_map=None):
        """
        递归地应用Leiden算法进行社区检测

        :param graph: 图对象
        :param level: 当前递归层次
        :param prefix: 前缀
        :param node_map: 节点映射
        :return: 节点层次和社区信息
        """
        if level > self.max_level:
            return {}, {}

        if node_map is None:
            node_map = {v.index: v.index for v in graph.vs}

        partition = la.find_partition(graph, partition_type=la.ModularityVertexPartition, seed=self.seed)
        communities = partition.membership

        levels = {node_map[v.index]: [] for v in graph.vs}
        community_info = {node_map[v.index]: [] for v in graph.vs}

        for v in graph.vs:
            levels[node_map[v.index]].append(level)
            community_info[node_map[v.index]].append(f'{prefix}L{level}_C{communities[v.index]}')

        # 当 level == self.max_level 时，停止递归并只处理当前层次的社区
        if level == self.max_level:
            return levels, community_info

        for community in set(communities):
            subgraph_indices = [v.index for v in graph.vs if communities[v.index] == community]
            subgraph = graph.subgraph(subgraph_indices)
            sub_node_map = {subgraph.vs[i].index: node_map[subgraph_indices[i]] for i in range(len(subgraph.vs))}

            if 1 < len(subgraph.vs) <= self.max_comm_size:
                sub_prefix = f'{prefix}L{level}_C{community}_'
                sub_levels, sub_community_info = self.recursive_leiden(subgraph, level + 1, sub_prefix, sub_node_map)

                for v in subgraph.vs:
                    if sub_node_map[v.index] not in sub_levels:
                        sub_levels[sub_node_map[v.index]] = []
                    if sub_node_map[v.index] not in sub_community_info:
                        sub_community_info[sub_node_map[v.index]] = []

                for v in subgraph.vs:
                    levels[sub_node_map[v.index]].extend(sub_levels[sub_node_map[v.index]])
                    community_info[sub_node_map[v.index]].extend(sub_community_info[sub_node_map[v.index]])

        return levels, community_info

    def load_data(self, entities, relationships):
        """
        加载数据并创建图对象

        :param entities: 实体列表
        :param relationships: 关系列表
        :return: 节点列表和边列表
        """
        entities = self.calculate_and_update_degrees(entities, relationships)

        vertices = set()
        edges = []

        for relationship in relationships:
            directional_entity = relationship.source
            directed_entity = relationship.target

            vertices.add(directional_entity)
            vertices.add(directed_entity)

            edges.append((directional_entity, directed_entity))

        for entity in entities:
            self.node_details_map[entity.id] = {
                'attributes': entity.attributes,
                'name': entity.name,
                'type': entity.type,
            }
            self.node_id_map[entity.id] = entity.id

        return list(vertices), edges

    @staticmethod
    def create_graph(vertices, edges):
        # 创建图对象并添加节点和边
        g = ig.Graph(directed=False)
        g.add_vertices(vertices)
        g.add_edges(edges)
        return g

    def detect_communities(self, graph, relationships, show: bool = False):
        """
        检测社区并返回社区信息的 DataFrame

        :param graph: 图对象
        :param relationships: 关系列表
        :param show: 是否用于展示于知识图谱
        """
        levels, community_info = self.recursive_leiden(graph)

        data = []
        community_save = {}

        # 初始化社区信息
        for node in graph.vs:
            node_name = node['name'] if 'name' in node.attributes() else node.index
            node_id = self.node_id_map.get(node_name, -1)

            for level, community in zip(levels[node.index], community_info[node.index]):
                if community not in community_save:
                    community_save[community] = {
                        'entity_ids': [],
                        'community_info': [],
                        'level': level,
                        'title': community,
                        'id': community,
                        'rating': 0,
                    }
                community_save[community]['entity_ids'].append(node_id)
        if not show:
            # 处理关系信息
            for relationship in relationships:
                directional_entity = relationship.source
                directed_entity = relationship.target

                directional_entity_details = self.node_details_map.get(directional_entity, {})
                directed_entity_details = self.node_details_map.get(directed_entity, {})
                relation_details = {
                    'Type': relationship.type,
                    'Name': relationship.name,
                    'Attributes': relationship.attributes,
                }

                # 构建完整的关系描述
                relation_entry = {
                    'DirectionalEntity': {
                        'Type': directional_entity_details.get('type', ''),
                        'Name': directional_entity_details.get('name', ''),
                        'Attributes': directional_entity_details.get('attributes', {}),
                    },
                    'Relation': relation_details,
                    'DirectedEntity': {
                        'Type': directed_entity_details.get('type', ''),
                        'Name': directed_entity_details.get('name', ''),
                        'Attributes': directed_entity_details.get('attributes', {}),
                    },
                }

                # 将关系分配到对应的社区
                for community, info in community_save.items():
                    if directional_entity in info['entity_ids'] or directed_entity in info['entity_ids']:
                        # 在存储前序列化为字符串
                        serialized_relation_entry = json.dumps(relation_entry, ensure_ascii=False)
                        info['community_info'].append(serialized_relation_entry)

        # 构建最终社区信息
        for key, value in community_save.items():
            data.append(
                Community(
                    level=value['level'],
                    entity_ids=value['entity_ids'],
                    id=str(uuid.uuid4())[:8],
                    title=value['title'],
                    # 将 community_info 列表直接序列化为 JSON 字符串存储
                    full_content=json.dumps(value['community_info'], ensure_ascii=False, indent=4),
                    rating=0.0,
                )
            )

        return data
