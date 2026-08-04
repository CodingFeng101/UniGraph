"""Import-level smoke test for the locked runtime dependency set."""

# ruff: noqa: I001

import atexit
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

LOG_PATHS = [REPO_ROOT / 'var/log/fba_access.log', REPO_ROOT / 'var/log/fba_error.log']
PREEXISTING_LOGS = {path for path in LOG_PATHS if path.exists()}


@atexit.register
def remove_generated_logs() -> None:
    for path in LOG_PATHS:
        if path not in PREEXISTING_LOGS:
            path.unlink(missing_ok=True)


TEST_ENV = {
    'UNIGRAPH_RUNTIME_DIR': str(REPO_ROOT / 'var'),
    'ENVIRONMENT': 'dev',
    'MYSQL_HOST': '127.0.0.1',
    'MYSQL_PORT': '3306',
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': 'test-password',
    'MYSQL_DATABASE': 'onlineunigraph',
    'REDIS_HOST': '127.0.0.1',
    'REDIS_PORT': '6379',
    'REDIS_PASSWORD': 'test-password',
    'REDIS_DATABASE': '0',
    'TOKEN_SECRET_KEY': 'test-token-secret-that-is-long-enough',
    'AUTH_AES_SECRET_KEY': 'MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=',
    'OPERA_LOG_ENCRYPT_SECRET_KEY': '0123456789abcdef0123456789abcdef',
    'OAUTH2_GITHUB_CLIENT_ID': 'test',
    'OAUTH2_GITHUB_CLIENT_SECRET': 'test',
    'OAUTH2_LINUX_DO_CLIENT_ID': 'test',
    'OAUTH2_LINUX_DO_CLIENT_SECRET': 'test',
    'CELERY_BROKER_REDIS_DATABASE': '1',
    'CELERY_BACKEND_REDIS_DATABASE': '2',
    'EMBEDDING_MODEL': 'text-embedding-3-small',
    'OPENAI_API_KEY': 'test-key',
    'INDEX_EXPORT_URL_ROOT': 'http://127.0.0.1:8000/knowg/v1/knowledge/ask',
    'CORS_ALLOWED_ORIGINS': '["http://localhost:5173"]',
}

for key, value in TEST_ENV.items():
    os.environ.setdefault(key, value)

from backend.common.core_layer.unigraph.file.content_getter import FileContentGetterFactory
from backend.common.core_layer.unigraph.file.text_partitioner import LangChainSplitter
from backend.core.path_conf import IP2REGION_XDB
from backend.database.db_mysql import SQLALCHEMY_DATABASE_URL
from backend.main import app

assert SQLALCHEMY_DATABASE_URL.startswith('mysql+aiomysql://')
assert type(FileContentGetterFactory.create('document.pdf')).__name__ == 'PdfContentGetter'
assert LangChainSplitter(20, 2).split('hello world')
assert os.path.isfile(IP2REGION_XDB)
assert any(getattr(route, 'path', None) == '/knowg/v1/docs' for route in app.routes)
assert app.url_path_for('health_check') == '/knowg/v1/health'

print('Backend runtime import smoke test passed.')
