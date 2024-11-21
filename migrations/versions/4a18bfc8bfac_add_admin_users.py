"""add_admin_users

Revision ID: 4a18bfc8bfac
Revises: 08a2be4dcb48
Create Date: 2024-11-21 18:35:57.574619+00:00

"""

from typing import Sequence
from uuid import uuid4

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4a18bfc8bfac"
down_revision: str | None = "08a2be4dcb48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO users (id, email, is_active, account_type)
        VALUES
            ('{uuid4()}', 'superadmin@informed.org', true, 'SUPERADMIN'),
            ('{uuid4()}', 'admin@informed.org', true, 'ADMIN')
        ON CONFLICT (email) DO NOTHING;
    """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM users
        WHERE email IN ('superadmin@informed.org', 'admin@informed.org');
    """
    )
