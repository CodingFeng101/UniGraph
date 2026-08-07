"""Register the current UniGraph schema as the migration baseline.

Revision ID: 20260805_baseline
Revises: 5484bc7e098d
Create Date: 2026-08-05
"""

from sqlalchemy import inspect

from alembic import op

revision = '20260805_baseline'
down_revision = '5484bc7e098d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    required_tables = {'chat_message', 'chat_message_source', 'chat_share', 'kg_base', 'llm_provider'}
    available_tables = set(inspector.get_table_names())
    missing_tables = sorted(required_tables - available_tables)

    llm_provider_columns = (
        {column['name'] for column in inspector.get_columns('llm_provider')}
        if 'llm_provider' in available_tables
        else set()
    )
    missing_columns = [] if 'sort_order' in llm_provider_columns else ['llm_provider.sort_order']

    if missing_tables or missing_columns:
        details = ', '.join([*missing_tables, *missing_columns])
        raise RuntimeError(
            'The database is older than the UniGraph migration baseline. '
            f'Apply the SQL migrations documented in docs/DEPLOYMENT.md first. Missing: {details}'
        )


def downgrade() -> None:
    pass
