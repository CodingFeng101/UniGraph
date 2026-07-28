# backend/app/task/utils.py
import json

import redis

from backend.app.task.conf import task_settings
from backend.core.conf import settings

_redis_client = None


def get_redis_client():
    """获取单例 Redis 客户端，复用 celery_app 配置"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=task_settings.CELERY_BACKEND_REDIS_DATABASE,
        )
    return _redis_client


def update_task_state(task, task_id: str, state: str, meta: dict, ttl: int = 3600):
    """
    更新任务状态到 Redis 和 Celery
    :param task: Celery 任务实例（self）
    :param task_id: 任务 ID
    :param state: Celery 状态（如 PROGRESS, SUCCESS）
    :param meta: 状态元数据（如 {"type": "processing", "progress": 50}）
    :param ttl: Redis 键过期时间（秒）
    """
    redis_client = get_redis_client()
    redis_client.setex(f'task:{task_id}:progress', ttl, json.dumps(meta))
    task.update_state(state=state, meta=meta)
