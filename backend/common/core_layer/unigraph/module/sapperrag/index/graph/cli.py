from dataclasses import asdict

from ...index.base import Indexer
from ...index.graph.attribute_embedding import AttributeEmbedder
from ...index.graph.reporting.community_detection import CommunityDetection
from ...index.graph.reporting.report_generate import CommunityReportGenerator
from ...model.model_load import load_entities


class GraphIndexer(Indexer):
    async def build_index(
        self,
        entities,
        relationships,
        level: int,
        api_key,
        base_url,
        model,
        embedding_api_key,
        embedding_base_url,
        embedding_model,
        progress_callback=None,
    ):
        """
        主要是创建社区报告和对实体信息进行嵌入

        :param entities: 实体列表
        :param relationships: 关系列表
        :param level: 社区划分的层数
        :return: 实体列表，社区报告
        """
        from backend.common.core_layer.interface.query_service import logger

        for entity in entities:
            entity.id = str(entity.id)

        for relationship in relationships:
            relationship.source = str(relationship.source)
            relationship.target = str(relationship.target)
            relationship.id = str(relationship.id)

        # 使用leiden算法对社区进行划分
        community_detector = CommunityDetection(max_comm_size=20, max_level=level, seed=5)
        vertices, edges = community_detector.load_data(entities, relationships)
        graph = community_detector.create_graph(vertices, edges)
        communities = community_detector.detect_communities(graph, relationships)
        entities = load_entities(entities=entities, communities=communities)
        if progress_callback:
            progress_callback('communities', len(communities), len(communities), communities)
        logger.info('Community detection completed')

        # 创建社区报告
        generator = CommunityReportGenerator(input_data=communities)
        reports_list = await generator.generate_reports(
            api_key=api_key,
            base_url=base_url,
            model=model,
            progress_callback=(
                (lambda done, total, report: progress_callback('reports', done, total, report))
                if progress_callback
                else None
            ),
        )
        reports = [asdict(item) for item in reports_list]
        logger.info('Community report generation completed')

        # 对实体信息进行嵌入
        embedder = AttributeEmbedder()
        entities_list = await embedder.add_attribute_vectors(
            entities,
            api_key=embedding_api_key,
            base_url=embedding_base_url,
            model=embedding_model,
            progress_callback=(
                (lambda done, total, entity, error: progress_callback('embeddings', done, total, (entity, error)))
                if progress_callback
                else None
            ),
        )
        entities = [asdict(item) for item in entities_list]
        logger.info('Entity information embedding completed')

        return entities, reports
