#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import celery
import celery_aio_pool
from celery.signals import worker_process_shutdown
from kombu import Exchange, Queue

from backend.app.task.conf import task_settings
from backend.common.clients import openai_client_registry
from backend.core.conf import settings

__all__ = ['celery_app']


def init_celery() -> celery.Celery:
    """创建 celery 应用"""

    # TODO: Update this work if celery version >= 6.0.0
    # https://github.com/fastapi-practices/fastapi_best_architecture/issues/321
    # https://github.com/celery/celery/issues/7874
    celery.app.trace.build_tracer = celery_aio_pool.build_async_tracer
    celery.app.trace.reset_worker_optimizations()

    app = celery.Celery(
        'fba_celery',
        broker_connection_retry_on_startup=True,
        worker_pool=celery_aio_pool.pool.AsyncIOPool,
        trace=celery_aio_pool.build_async_tracer,
    )

    # 动态生成 Redis 连接字符串（支持无密码情况）
    def get_redis_connection_string(host: str, port: int, db: int, password: str = None) -> str:
        """根据是否有密码生成正确的 Redis 连接字符串"""
        if password:
            return f'redis://:{password}@{host}:{port}/{db}'
        else:
            return f'redis://{host}:{port}/{db}'

    # Redis配置
    _redis_broker = get_redis_connection_string(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=task_settings.CELERY_BROKER_REDIS_DATABASE,
        password=settings.REDIS_PASSWORD,
    )
    _result_backend = get_redis_connection_string(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=task_settings.CELERY_BACKEND_REDIS_DATABASE,
        password=settings.REDIS_PASSWORD,
    )
    _result_backend_transport_options = {
        'global_keyprefix': f'{task_settings.CELERY_BACKEND_REDIS_PREFIX}_',
        'retry_policy': {
            'timeout': task_settings.CELERY_BACKEND_REDIS_TIMEOUT,
        },
    }

    # Celery Schedule Tasks
    # https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
    _beat_schedule = task_settings.CELERY_SCHEDULE

    # Update celery settings
    task_exchange = Exchange('unigraph', type='direct', durable=True)
    task_queues = tuple(
        Queue(name, exchange=task_exchange, routing_key=name)
        for name in (
            task_settings.CELERY_DEFAULT_QUEUE,
            task_settings.CELERY_QA_QUEUE,
            task_settings.CELERY_INDEXING_QUEUE,
            task_settings.CELERY_MIGRATION_QUEUE,
        )
    )
    task_routes = {
        'knowledge_graph.ask': {
            'queue': task_settings.CELERY_QA_QUEUE,
            'routing_key': task_settings.CELERY_QA_QUEUE,
        },
        'knowledge_graph.build_index': {
            'queue': task_settings.CELERY_INDEXING_QUEUE,
            'routing_key': task_settings.CELERY_INDEXING_QUEUE,
        },
        'knowledge_graph.infer_knowledge_graph': {
            'queue': task_settings.CELERY_MIGRATION_QUEUE,
            'routing_key': task_settings.CELERY_MIGRATION_QUEUE,
        },
    }
    app.conf.update(
        broker_url=_redis_broker,  # 强制使用Redis作为broker
        result_backend=_result_backend,
        result_backend_transport_options=_result_backend_transport_options,
        timezone=settings.DATETIME_TIMEZONE,
        enable_utc=False,
        task_track_started=True,
        task_default_queue=task_settings.CELERY_DEFAULT_QUEUE,
        task_default_exchange=task_exchange.name,
        task_default_exchange_type=task_exchange.type,
        task_default_routing_key=task_settings.CELERY_DEFAULT_QUEUE,
        task_queues=task_queues,
        task_routes=task_routes,
        worker_prefetch_multiplier=1,
        worker_concurrency=task_settings.CELERY_WORKER_CONCURRENCY,
        beat_schedule=_beat_schedule,
    )

    # Load task modules
    app.autodiscover_tasks(task_settings.CELERY_TASKS_PACKAGES)

    return app


# 创建 celery 实例
celery_app = init_celery()
celery_app.conf.include = [
    'backend.app.kgbase.api.v1.kgbase.knowledge_graph',
    'backend.app.kgbase.api.v1.kgbase.schema_graph',
]


@worker_process_shutdown.connect
def close_worker_http_clients(**kwargs) -> None:
    try:
        asyncio.run(openai_client_registry.close_all())
    except RuntimeError:
        # The process is already shutting down; open sockets will be released by the OS.
        pass
