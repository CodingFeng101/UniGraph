#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging

import redis
from celery.exceptions import NotRegistered
from celery.result import AsyncResult

from backend.app.task.celery import celery_app
from backend.app.task.conf import task_settings
from backend.common.exception.errors import NotFoundError
from backend.core.conf import settings

logger = logging.getLogger(__name__)


class TaskService:
    @staticmethod
    def _get_redis_client(db: int):
        return redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=db,
            decode_responses=False,
        )

    @staticmethod
    def _result_backend_key(uid: str) -> str:
        return f'{task_settings.CELERY_BACKEND_REDIS_PREFIX}_celery-task-meta-{uid}'

    @staticmethod
    def _task_owner_key(uid: str) -> str:
        return f'unigraph:task-owner:{uid}'

    @classmethod
    def register_owner(cls, uid: str, user_uuid: str) -> None:
        client = cls._get_redis_client(task_settings.CELERY_BACKEND_REDIS_DATABASE)
        client.setex(cls._task_owner_key(uid), task_settings.CELERY_TASK_OWNER_TTL_SECONDS, user_uuid)

    @classmethod
    def require_owner(cls, uid: str, user_uuid: str) -> None:
        client = cls._get_redis_client(task_settings.CELERY_BACKEND_REDIS_DATABASE)
        owner = client.get(cls._task_owner_key(uid))
        if owner is None or owner.decode('utf-8') != user_uuid:
            raise NotFoundError(msg='任务不存在')

    @classmethod
    def is_task_known(cls, uid: str) -> bool:
        result_redis = cls._get_redis_client(task_settings.CELERY_BACKEND_REDIS_DATABASE)
        broker_redis = cls._get_redis_client(task_settings.CELERY_BROKER_REDIS_DATABASE)

        if result_redis.exists(cls._result_backend_key(uid)):
            return True

        uid_bytes = uid.encode('utf-8')

        for message in broker_redis.lrange('celery', 0, -1):
            if uid_bytes in message:
                return True

        try:
            for message in broker_redis.hvals('unacked'):
                if uid_bytes in message:
                    return True
        except redis.ResponseError:
            pass

        return False

    @staticmethod
    def get_list():
        filtered_tasks = []
        for key in celery_app.tasks:
            if not key.startswith('celery.'):
                filtered_tasks.append({'name': key})
        return filtered_tasks

    @staticmethod
    def get():
        return celery_app.current_worker_task

    @staticmethod
    def get_status(uid: str):
        try:
            result = AsyncResult(id=uid, app=celery_app)
        except NotRegistered as exc:
            raise NotFoundError(msg='任务不存在') from exc

        return result

    @staticmethod
    def get_result(uid: str):
        try:
            result = AsyncResult(id=uid, app=celery_app)
        except NotRegistered as exc:
            raise NotFoundError(msg='任务不存在') from exc
        return result

    @classmethod
    def get_cached_progress(cls, uid: str) -> dict | None:
        result_redis = cls._get_redis_client(task_settings.CELERY_BACKEND_REDIS_DATABASE)
        payload = result_redis.get(f'task:{uid}:progress')
        if not payload:
            return None
        try:
            value = json.loads(payload)
        except (TypeError, ValueError):
            logger.warning('Invalid cached task payload for %s', uid)
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def run(*, name: str, user_uuid: str, args: list | None = None, kwargs: dict | None = None):
        task = celery_app.send_task(name=name, args=args, kwargs=kwargs)
        TaskService.register_owner(task.id, user_uuid)
        return {
            'task_id': task.id,
            'status': 'started',
            'name': name,
        }

    @staticmethod
    def revoke_task(uid: str):
        try:
            if not uid:
                raise ValueError('任务 ID 不能为空')
            celery_app.control.revoke(task_id=uid, terminate=True, signal='SIGTERM')
            logger.info(f'任务 {uid} 已撤销')
        except Exception as exc:
            logger.error(f'撤销任务 {uid} 失败: {exc}')
            raise


task_service = TaskService()
