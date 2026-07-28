#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.oauth2.ai_jxnu import router as ai_jxnu_router
from backend.app.admin.api.v1.oauth2.github import router as github_router
from backend.app.admin.api.v1.oauth2.linux_do import router as linux_do_router

router = APIRouter(prefix='/oauth2')

router.include_router(github_router, prefix='/github', tags=['GitHub OAuth2'])
router.include_router(linux_do_router, prefix='/linux-do', tags=['LinuxDo OAuth2'])
router.include_router(ai_jxnu_router, prefix='/jxnu', tags=['JXNU OAuth2'])
