import pytest
from backend.core.conf import Settings
from pydantic import ValidationError


def production_settings(**overrides):
    values = {
        'ENVIRONMENT': 'pro',
        'MYSQL_HOST': 'mysql',
        'MYSQL_PORT': 3306,
        'MYSQL_USER': 'unigraph',
        'MYSQL_PASSWORD': 'database-password',
        'REDIS_HOST': 'redis',
        'REDIS_PORT': 6379,
        'REDIS_PASSWORD': 'redis-password',
        'REDIS_DATABASE': 0,
        'TOKEN_SECRET_KEY': 't' * 40,
        'AUTH_AES_SECRET_KEY': 'a' * 40,
        'LLM_API_KEY_ENCRYPTION_KEY': 'l' * 40,
        'OPERA_LOG_ENCRYPT_SECRET_KEY': 'o' * 40,
        'COOKIE_SECURE': True,
        'CORS_ALLOWED_ORIGINS': ['https://unigraph.example.com'],
    }
    values.update(overrides)
    return Settings(**values)


def test_production_accepts_explicit_deployment_origin():
    settings = production_settings()
    assert settings.CORS_ALLOWED_ORIGINS == ['https://unigraph.example.com']


@pytest.mark.parametrize('origin', ['*', 'http://localhost:8080', 'http://127.0.0.1:8080'])
def test_production_rejects_unsafe_origins(origin):
    with pytest.raises(ValidationError, match='CORS_ALLOWED_ORIGINS'):
        production_settings(CORS_ALLOWED_ORIGINS=[origin])
