#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import uuid

from anyio import sleep

from backend.app.task.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name='task_demo_async')
async def task_demo_async() -> str:
    await sleep(1)
    uid = uuid.uuid4().hex
    logger.info('异步任务 %s 执行成功', uid)
    return uid
