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
    # First create the users
    op.execute(
        f"""
        INSERT INTO users (id, email, is_active, account_type)
        VALUES
            ('{uuid4()}', 'superadmin@informed.org', true, 'SUPERADMIN'),
            ('{uuid4()}', 'admin@informed.org', true, 'ADMIN')
        ON CONFLICT (email) DO NOTHING
        RETURNING id, email;
    """
    )

    # Then add their details with zip code and language
    op.execute(
        """
        INSERT INTO user_details (id, user_id, first_name, last_name, zip_code, language)
        SELECT
            gen_random_uuid(),
            users.id,
            CASE
                WHEN users.email = 'superadmin@informed.org' THEN 'Super'
                ELSE 'System'
            END,
            CASE
                WHEN users.email = 'superadmin@informed.org' THEN 'Admin'
                ELSE 'Admin'
            END,
            '12345',
            'ENGLISH'
        FROM users
        WHERE users.email IN ('superadmin@informed.org', 'admin@informed.org')
        AND NOT EXISTS (
            SELECT 1 FROM user_details WHERE user_details.user_id = users.id
        );
        """
    )

    # Add empty medical details
    op.execute(
        """
        INSERT INTO user_medical_details (id, user_id)
        SELECT
            gen_random_uuid(),
            users.id
        FROM users
        WHERE users.email IN ('superadmin@informed.org', 'admin@informed.org')
        AND NOT EXISTS (
            SELECT 1 FROM user_medical_details WHERE user_medical_details.user_id = users.id
        );
        """
    )


def downgrade() -> None:
    # The cascade delete will handle the details tables
    op.execute(
        """
        DELETE FROM users
        WHERE email IN ('superadmin@informed.org', 'admin@informed.org');
        """
    )
