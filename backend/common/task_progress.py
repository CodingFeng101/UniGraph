from __future__ import annotations

from datetime import datetime
from typing import Any

MAX_TASK_LOGS = 60


def scaled_progress(completed: int, total: int, start: float, end: float) -> float:
    if total <= 0:
        return round(end, 1)
    ratio = min(max(completed, 0), total) / total
    return round(start + (end - start) * ratio, 1)


def should_report(completed: int, total: int, checkpoints: int = 20) -> bool:
    if total <= 0 or completed >= total:
        return True
    interval = max(1, total // checkpoints)
    return completed == 1 or completed % interval == 0


def task_progress(
    task: Any,
    message: str,
    progress: float,
    *,
    detail: str = '',
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_id = str(getattr(getattr(task, 'request', None), 'id', '') or '')
    if getattr(task, '_unigraph_progress_task_id', None) != task_id:
        task._unigraph_progress_task_id = task_id
        task._unigraph_progress_logs = []
    logs = list(getattr(task, '_unigraph_progress_logs', []))
    event = {
        'id': len(logs) + 1,
        'message': message,
        'detail': detail,
        'progress': round(float(progress), 1),
        'time': datetime.now().isoformat(timespec='seconds'),
        'metrics': metrics or {},
    }
    logs.append(event)
    logs = logs[-MAX_TASK_LOGS:]
    task._unigraph_progress_logs = logs
    payload = {
        'type': 'processing',
        'message': message,
        'detail': detail,
        'progress': event['progress'],
        'metrics': event['metrics'],
        'logs': logs,
    }
    task.update_state(state='PROGRESS', meta=payload)
    return payload


def task_result(
    task: Any,
    message: str,
    *,
    data: Any = None,
    detail: str = '',
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_progress(task, message, 100, detail=detail, metrics=metrics)
    result = {
        'type': 'final_result',
        'data': data,
        'code': 200,
        'msg': 'success',
        'message': message,
        'detail': detail,
        'progress': 100,
        'metrics': metrics or {},
        'logs': list(getattr(task, '_unigraph_progress_logs', [])),
    }
    task.update_state(state='SUCCESS', meta=result)
    return result


def task_error_result(task: Any, error_payload: dict[str, Any]) -> dict[str, Any]:
    error = error_payload.get('error', {})
    message = str(error.get('message') or error_payload.get('exc_message') or '任务执行失败')
    logs = list(getattr(task, '_unigraph_progress_logs', []))
    progress = float(logs[-1].get('progress', 0)) if logs else 0
    task_progress(task, '任务执行失败', progress, detail=message)
    return {
        **error_payload,
        'type': 'error',
        'message': message,
        'progress': progress,
        'logs': list(getattr(task, '_unigraph_progress_logs', [])),
    }
