#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.router import v1 as admin_v1
from backend.app.file import router as file_v1
from backend.app.generator.api.router import v1 as generator_v1
from backend.app.image import router as image_router
from backend.app.kgbase.api.router import v1 as kgbase_v1
from backend.app.task.api.router import v1 as task_v1
from backend.core.conf import settings

route = APIRouter()

route.include_router(admin_v1, prefix=f'{settings.FASTAPI_API_V1_PATH}')
route.include_router(generator_v1, prefix=f'{settings.FASTAPI_API_V1_PATH}')
route.include_router(task_v1, prefix=f'{settings.FASTAPI_API_V1_PATH}')
route.include_router(kgbase_v1, prefix=f'{settings.FASTAPI_API_V1_PATH}')
route.include_router(file_v1, prefix=f'{settings.FASTAPI_API_V1_PATH}')
route.include_router(image_router, prefix=f'{settings.FASTAPI_API_V1_PATH}')
