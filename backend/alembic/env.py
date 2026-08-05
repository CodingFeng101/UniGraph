from __future__ import annotations

import asyncio
from logging.config import fileConfig

import backend.app.admin.model  # noqa: F401
import backend.app.generator.model  # noqa: F401
import backend.app.kgbase.model  # noqa: F401
from backend.common.model import MappedBase
from backend.database.db_mysql import SQLALCHEMY_DATABASE_URL
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

config = context.config
config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URL.replace('%', '%%'))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = MappedBase.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=SQLALCHEMY_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        pool_pre_ping=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
