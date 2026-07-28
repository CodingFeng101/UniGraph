#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path

from backend.app.task.service.task_service import task_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
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
    task = task_service.get()
    return response_base.success(data=serialize_safe(task))


@router.get('/{uid}/status', summary='获取任务状态', dependencies=[DependsJwtAuth])
async def get_task_status(uid: Annotated[str, Path(description='任务ID')]) -> ResponseModel:
    task_result = task_service.get_status(uid)
    # 安全地序列化 result.info
    safe_meta = serialize_safe(task_result.info) if task_result.info else {}
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
async def get_task_result(uid: Annotated[str, Path(description='任务ID')]) -> ResponseModel:
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
    ],
)
async def run_task(
    name: Annotated[str, Path(description='任务名称')],
    args: Annotated[list | None, Body(description='任务函数位置参数')] = None,
    kwargs: Annotated[dict | None, Body(description='任务函数关键字参数')] = None,
) -> ResponseModel:
    task = task_service.run(name=name, args=args, kwargs=kwargs)
    return response_base.success(data=task)


@router.post('/{uid}/revoke', summary='取消指定异步任务', dependencies=[DependsJwtAuth])
async def revoke_task(uid: Annotated[str, Path(description='任务UID')]):
    task_service.revoke_task(uid=uid)
    return response_base.success(
        data={
            'state': 'REVOKE',
            'msg': f'Success to cancel task {uid}',
        }
    )
