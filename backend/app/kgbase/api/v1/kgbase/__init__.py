#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
import logging

from fastapi import APIRouter

from backend.app.kgbase.api.v1.kgbase.chat_library import router as chat_library_router
from backend.app.kgbase.api.v1.kgbase.kg_base import router as kg_base_router
from backend.app.kgbase.api.v1.kgbase.knowledge_entity import router as knowledge_entity_router
from backend.app.kgbase.api.v1.kgbase.knowledge_graph import router as knowledge_graph_router
from backend.app.kgbase.api.v1.kgbase.knowledge_relationship import router as knowledge_relationship_router
from backend.app.kgbase.api.v1.kgbase.schema_entity import router as schema_entity_router
from backend.app.kgbase.api.v1.kgbase.schema_graph import router as schema_graph_router
from backend.app.kgbase.api.v1.kgbase.schema_relationship import router as schema_relationship_router

router = APIRouter(prefix='/kg')


router.include_router(kg_base_router, prefix='/base', tags=['图谱'])
router.include_router(schema_graph_router, prefix='/schema', tags=['架构'])
router.include_router(schema_entity_router, prefix='/schema_entity', tags=['实体类型'])
router.include_router(schema_relationship_router, prefix='/schema_relationship', tags=['关系类型'])
router.include_router(knowledge_graph_router, prefix='/knowledge', tags=['知识图谱'])
router.include_router(knowledge_entity_router, prefix='/knowledge_entity', tags=['实体'])
router.include_router(knowledge_relationship_router, prefix='/knowledge_relationship', tags=['关系'])
router.include_router(chat_library_router, prefix='/chat_library', tags=['聊天库'])


logger = logging.getLogger(__name__)
HEARTBEAT_INTERVAL = 50
