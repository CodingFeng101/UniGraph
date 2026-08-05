"""Preserve the legacy UniGraph Alembic revision identifier.

Revision ID: 5484bc7e098d
Revises:

The historical migration file is no longer present in the repository, but
existing installations still record this revision. Keeping a no-op bridge
allows those databases to move to the validated current-schema baseline
without rewriting their migration history.
"""

revision = '5484bc7e098d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
