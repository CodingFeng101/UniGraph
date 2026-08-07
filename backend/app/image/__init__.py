#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.image.get_image import router as image_router

router = APIRouter(prefix='/image')

router.include_router(image_router, tags=['图片获取'])
