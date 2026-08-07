import _env  # noqa: F401  # isort: skip

from backend.app.task.celery import celery_app


def test_interactive_and_long_running_tasks_use_separate_queues() -> None:
    routes = celery_app.conf.task_routes

    assert routes['knowledge_graph.ask']['queue'] == 'qa'
    assert routes['knowledge_graph.ask']['routing_key'] == 'qa'
    assert routes['knowledge_graph.build_index']['queue'] == 'indexing'
    assert routes['knowledge_graph.build_index']['routing_key'] == 'indexing'
    assert routes['knowledge_graph.infer_knowledge_graph']['queue'] == 'migration'
    assert routes['knowledge_graph.infer_knowledge_graph']['routing_key'] == 'migration'
    assert len({route['queue'] for route in routes.values()}) == 3


def test_default_queue_and_prefetch_are_explicit() -> None:
    assert celery_app.conf.task_default_queue == 'default'
    assert celery_app.conf.worker_prefetch_multiplier == 1
    assert {queue.name for queue in celery_app.conf.task_queues} == {'default', 'qa', 'indexing', 'migration'}
    assert {queue.routing_key for queue in celery_app.conf.task_queues} == {'default', 'qa', 'indexing', 'migration'}
