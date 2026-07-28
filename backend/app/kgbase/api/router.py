#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.kgbase.api.v1.kgbase import router as kgbase_router

v1 = APIRouter()

v1.include_router(kgbase_router)
