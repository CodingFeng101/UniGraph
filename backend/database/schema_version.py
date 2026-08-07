from __future__ import annotations

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from backend.core.path_conf import BasePath
from backend.database.db_mysql import async_engine


def alembic_config() -> Config:
    return Config(str(BasePath / 'alembic.ini'))


def expected_schema_heads() -> set[str]:
    return set(ScriptDirectory.from_config(alembic_config()).get_heads())


def schema_version_error(current: set[str], expected: set[str]) -> str | None:
    if current == expected:
        return None
    current_label = ', '.join(sorted(current)) or 'unversioned'
    expected_label = ', '.join(sorted(expected)) or 'missing migration scripts'
    return (
        f'Database schema version is {current_label}; expected {expected_label}. '
        'Run: python -m alembic -c backend/alembic.ini upgrade head'
    )


async def ensure_database_schema_current() -> None:
    async with async_engine.connect() as connection:
        current = await connection.run_sync(
            lambda sync_connection: set(MigrationContext.configure(sync_connection).get_current_heads())
        )
    error = schema_version_error(current, expected_schema_heads())
    if error:
        raise RuntimeError(error)
