#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.llm.model_routers import router as model_router
from backend.app.admin.api.v1.llm.provider_routers import router as provider_router

router = APIRouter(prefix='/llm')

router.include_router(provider_router, prefix='/provider', tags=['提供商'])
router.include_router(model_router, prefix='/model', tags=['模型'])
