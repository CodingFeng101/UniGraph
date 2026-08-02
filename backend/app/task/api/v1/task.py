#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Request

from backend.app.kgbase.service.ownership_service import ownership_service
from backend.app.task.service.task_service import task_service
from backend.common.exception.errors import NotFoundError
from backend.common.rate_limit import rate_limiter
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth, get_token
from backend.common.security.permission import RequestPermission

router = APIRouter()


def serialize_safe(obj):
    """
    尝试安全地序列化 obj，使其符合 JSON 可序列化的类型
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): serialize_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [serialize_safe(i) for i in obj]
    if isinstance(obj, Exception):
        # 返回异常字符串描述
        return {'error': str(obj)}
    # 其他类型一律转字符串
    return str(obj)


@router.get('', summary='获取所有可执行任务模块', dependencies=[DependsJwtAuth])
async def get_all_tasks() -> ResponseModel:
    tasks = task_service.get_list()
    return response_base.success(data=tasks)


@router.get('/current', summary='获取当前正在执行的任务', dependencies=[DependsJwtAuth])
async def get_current_task() -> ResponseModel:
    return response_base.success(data=None)


@router.get('/{uid}/status', summary='获取任务状态', dependencies=[DependsJwtAuth])
async def get_task_status(request: Request, uid: Annotated[str, Path(description='任务ID')]) -> ResponseModel:
    task_service.require_owner(uid, request.user.uuid)
    task_result = task_service.get_status(uid)
    # 安全地序列化 result.info
    safe_meta = serialize_safe(task_result.info) if task_result.info else {}
    if task_result.state == 'FAILURE':
        cached_meta = task_service.get_cached_progress(uid)
        if cached_meta:
            safe_meta = serialize_safe(cached_meta)
        elif not isinstance(task_result.info, dict):
            message = str(task_result.info or '任务执行失败')
            safe_meta = {'type': 'error', 'message': message, 'error': {'message': message}}
    if task_result.state == 'PENDING':
        if task_service.is_task_known(uid):
            status = {
                'state': 'PENDING',
                'meta': {'message': 'Task is pending', 'progress': '0', 'type': 'pending'},
                'task_id': uid,
            }
        else:
            status = {
                'state': 'REVOKE',
                'meta': {'message': 'Task no longer exists', 'progress': '0', 'type': 'revoked'},
                'task_id': uid,
            }
    elif task_result.state == 'PROGRESS':
        status = {'state': 'PROGRESS', 'meta': safe_meta, 'task_id': uid}
    else:
        # SUCCESS, FAILURE 及其他状态
        status = {'state': task_result.state, 'meta': safe_meta, 'task_id': uid}
    return response_base.success(data=status)


@router.get('/{uid}', summary='获取任务结果', dependencies=[DependsJwtAuth])
async def get_task_result(request: Request, uid: Annotated[str, Path(description='任务ID')]) -> ResponseModel:
    task_service.require_owner(uid, request.user.uuid)
    task_result = task_service.get_result(uid)
    return response_base.success(
        data={
            'task_id': uid,
            'state': task_result.state,
            'result': serialize_safe(task_result.result) if task_result.ready() else None,
        }
    )


@router.post(
    '/{name}',
    summary='执行任务',
    dependencies=[
        Depends(RequestPermission('sys:task:run')),
        Depends(rate_limiter(times=20, seconds=60)),
    ],
)
async def run_task(
    request: Request,
    name: Annotated[str, Path(description='任务名称')],
    args: Annotated[list | None, Body(description='任务函数位置参数')] = None,
    kwargs: Annotated[dict | None, Body(description='任务函数关键字参数')] = None,
) -> ResponseModel:
    allowed_tasks = {
        'knowledge_graph.build_index',
        'knowledge_graph.create_knowledge_graph',
        'knowledge_graph.infer_knowledge_graph',
        'knowledge_graph.update_knowledge_graph',
        'schema_graph.create_schema_graph',
        'schema_graph.update_schema_graph',
        'schema_graph.update_schema_graph_suggestion',
    }
    if name not in allowed_tasks:
        raise NotFoundError(msg='任务不存在')
    task_kwargs = dict(kwargs or {})
    if name in {
        'knowledge_graph.build_index',
        'knowledge_graph.infer_knowledge_graph',
        'knowledge_graph.update_knowledge_graph',
    }:
        await ownership_service.require_knowledge_graph(user_uuid=request.user.uuid, uuid=task_kwargs.get('uuid'))
    elif name in {'schema_graph.update_schema_graph', 'schema_graph.update_schema_graph_suggestion'}:
        await ownership_service.require_schema_graph(user_uuid=request.user.uuid, uuid=task_kwargs.get('uuid'))
    elif name == 'knowledge_graph.create_knowledge_graph':
        data = (task_kwargs.get('obj_data') or {}).get('data') or {}
        await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=data.get('kg_base_uuid'))
        await ownership_service.require_schema_graph_in_kg_base(
            user_uuid=request.user.uuid,
            schema_graph_uuid=data.get('schema_graph_uuid'),
            kg_base_uuid=data.get('kg_base_uuid'),
        )
    elif name == 'schema_graph.create_schema_graph':
        data = (task_kwargs.get('obj_data') or {}).get('data') or {}
        await ownership_service.require_kg_base(user_uuid=request.user.uuid, uuid=data.get('kg_base_uuid'))
    task_kwargs['user_token'] = get_token(request)
    task = task_service.run(name=name, user_uuid=request.user.uuid, args=args, kwargs=task_kwargs)
    return response_base.success(data=task)


@router.post('/{uid}/revoke', summary='取消指定异步任务', dependencies=[DependsJwtAuth])
async def revoke_task(request: Request, uid: Annotated[str, Path(description='任务UID')]):
    task_service.require_owner(uid, request.user.uuid)
    task_service.revoke_task(uid=uid)
    return response_base.success(
        data={
            'state': 'REVOKE',
            'msg': f'Success to cancel task {uid}',
        }
    )
