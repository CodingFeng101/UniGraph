"""Provide a minimal non-secret environment before importing backend modules."""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TEST_ENV = {
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
