from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from sqlalchemy.sql import table, column
from sqlalchemy import String, DateTime, Boolean

# revision identifiers
revision: str = 'a2c90b68a588'
down_revision: Union[str, None] = 'ce47fd76c7b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ENUM definition
role_enum = pg.ENUM('admin', 'staff', 'client', name='role')

def upgrade() -> None:
    bind = op.get_bind()

    # Create ENUM first
    role_enum.create(bind, checkfirst=True)

    # Add columns as nullable first
    op.add_column('users', sa.Column('role', role_enum, nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # Set default values for existing rows
    op.execute("UPDATE users SET role = 'client' WHERE role IS NULL")
    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")

    # Make columns NOT NULL after setting values
    op.alter_column('users', 'role', nullable=False)
    op.alter_column('users', 'created_at', nullable=False)

    # Ensure other columns are NOT NULL
    op.alter_column('users', 'full_name', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('users', 'hashed_password', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('users', 'is_active', existing_type=sa.BOOLEAN(), nullable=False)

def downgrade() -> None:
    op.alter_column('users', 'is_active', existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column('users', 'hashed_password', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('users', 'full_name', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'role')

    # Drop ENUM
    role_enum.drop(op.get_bind(), checkfirst=True)
