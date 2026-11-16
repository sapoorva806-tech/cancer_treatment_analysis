
"""Promote the designated account to admin.

Revision ID: d1a7b9c4e602
Revises: c9df73f37394
"""

from alembic import op
import sqlalchemy as sa

revision = "d1a7b9c4e602"
down_revision = "c9df73f37394"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            UPDATE users
            SET role = 'ADMIN'
            WHERE email = 'finaltest99@example.com'
        """)
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            UPDATE users
            SET role = 'USER'
            WHERE email = 'finaltest99@example.com'
              AND role = 'ADMIN'
        """)
    )
