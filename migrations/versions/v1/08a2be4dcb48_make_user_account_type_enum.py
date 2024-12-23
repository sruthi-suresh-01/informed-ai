"""make_user_account_type_enum

Revision ID: 08a2be4dcb48
Revises: 7db8dcf4cd6b
Create Date: 2024-11-21 18:31:48.452907+00:00

"""

from typing import Sequence

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "08a2be4dcb48"
down_revision: str | None = "7db8dcf4cd6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # First update existing values to match enum case
    op.execute(
        """
        UPDATE users
        SET account_type = UPPER(account_type)
        WHERE account_type IS NOT NULL
    """
    )

    # Create the enum type
    op.execute("CREATE TYPE accounttype AS ENUM ('USER', 'ADMIN', 'SUPERADMIN')")

    # Then alter the column with explicit USING clause
    op.execute(
        "ALTER TABLE users ALTER COLUMN account_type TYPE accounttype USING account_type::accounttype"
    )


def downgrade() -> None:
    # First convert back to VARCHAR
    op.execute(
        "ALTER TABLE users ALTER COLUMN account_type TYPE varchar USING account_type::varchar"
    )

    # Then drop the enum type
    op.execute("DROP TYPE accounttype")
