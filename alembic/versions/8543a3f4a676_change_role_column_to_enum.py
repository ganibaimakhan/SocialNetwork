"""Change role column to Enum

Revision ID: 8543a3f4a676
Revises: 
Create Date: 2025-02-15 15:30:48.195293

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import ENUM

from alembic import op
import sqlalchemy as sa

role_enum = ENUM('ADMIN', 'USER', name='roleenum', create_type=True)

# revision identifiers, used by Alembic.
revision: str = '8543a3f4a676'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    role_enum.create(op.get_bind())

    # Alter the column to use the new Enum type
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE roleenum USING role::roleenum")


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::text")

    # Drop the enum type
    role_enum.drop(op.get_bind())
