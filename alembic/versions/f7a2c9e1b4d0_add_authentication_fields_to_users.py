"""add authentication fields to users

Revision ID: f7a2c9e1b4d0
Revises: 3281b01a7b06
Create Date: 2026-06-25 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f7a2c9e1b4d0"
down_revision: Union[str, Sequence[str], None] = "3281b01a7b06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hash bcrypt de "Admin1234" para usuarios existentes sin contraseña
DEFAULT_HASH = "$2b$12$HJosegQ1gVHmdRKk03KmxOt1.gWVTNlmJu3DtAGs7kY95wASZzvY2"


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("hashed_password", sa.String(), nullable=True))

    op.execute(
        sa.text(
            "UPDATE users SET hashed_password = :hash WHERE hashed_password IS NULL"
        ).bindparams(hash=DEFAULT_HASH)
    )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("hashed_password", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("hashed_password")
