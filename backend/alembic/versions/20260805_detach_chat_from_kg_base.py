"""Keep conversations after their knowledge base is deleted.

Revision ID: 20260805_chat_owner
Revises: 20260805_baseline
Create Date: 2026-08-05
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = '20260805_chat_owner'
down_revision = '20260805_baseline'
branch_labels = None
depends_on = None


def _foreign_key_name(column_name: str) -> str | None:
    for foreign_key in inspect(op.get_bind()).get_foreign_keys('chat_library'):
        if foreign_key.get('constrained_columns') == [column_name]:
            return foreign_key.get('name')
    return None


def upgrade() -> None:
    op.add_column('chat_library', sa.Column('user_uuid', sa.String(length=50), nullable=True))
    op.execute(
        sa.text(
            'UPDATE chat_library AS chat '
            'JOIN kg_base AS kg ON kg.uuid = chat.kg_base_uuid '
            'SET chat.user_uuid = kg.user_uuid'
        )
    )

    missing_owner = op.get_bind().execute(
        sa.text('SELECT COUNT(*) FROM chat_library WHERE user_uuid IS NULL')
    ).scalar_one()
    if missing_owner:
        raise RuntimeError(f'Cannot detach knowledge bases: {missing_owner} conversations have no owner')

    kg_base_foreign_key = _foreign_key_name('kg_base_uuid')
    if kg_base_foreign_key:
        op.drop_constraint(kg_base_foreign_key, 'chat_library', type_='foreignkey')

    op.alter_column(
        'chat_library',
        'user_uuid',
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.alter_column(
        'chat_library',
        'kg_base_uuid',
        existing_type=sa.String(length=50),
        nullable=True,
    )
    op.create_index('ix_chat_library_user_uuid', 'chat_library', ['user_uuid'])
    op.create_foreign_key(
        'fk_chat_library_user',
        'chat_library',
        'sys_user',
        ['user_uuid'],
        ['uuid'],
    )
    op.create_foreign_key(
        'fk_chat_library_kg_base',
        'chat_library',
        'kg_base',
        ['kg_base_uuid'],
        ['uuid'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    detached_count = op.get_bind().execute(
        sa.text('SELECT COUNT(*) FROM chat_library WHERE kg_base_uuid IS NULL')
    ).scalar_one()
    if detached_count:
        raise RuntimeError(f'Cannot downgrade: {detached_count} conversations are detached from a knowledge base')

    op.drop_constraint('fk_chat_library_kg_base', 'chat_library', type_='foreignkey')
    op.drop_constraint('fk_chat_library_user', 'chat_library', type_='foreignkey')
    op.drop_index('ix_chat_library_user_uuid', table_name='chat_library')
    op.alter_column(
        'chat_library',
        'kg_base_uuid',
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.create_foreign_key(
        'chat_library_ibfk_1',
        'chat_library',
        'kg_base',
        ['kg_base_uuid'],
        ['uuid'],
    )
    op.drop_column('chat_library', 'user_uuid')
