"""Fix working_hours constraints

Revision ID: 53f9af904c61
Revises: c3ca7b7f4a77
Create Date: 2025-06-23 09:05:21.348036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53f9af904c61'
down_revision: Union[str, None] = 'c3ca7b7f4a77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Replace with your actual constraint name if different
OLD_UNIQUE_CONSTRAINT_NAME = "working_hours_staff_id_key"
NEW_UNIQUE_CONSTRAINT_NAME = "unique_staff_day"


def upgrade():
    # Drop the old unique constraint on staff_id
    op.drop_constraint(OLD_UNIQUE_CONSTRAINT_NAME, 'working_hours', type_='unique')

    # Add a new unique constraint on (staff_id, day_of_week)
    op.create_unique_constraint(NEW_UNIQUE_CONSTRAINT_NAME, 'working_hours', ['staff_id', 'day_of_week'])

def downgrade():
    # Drop the new composite unique constraint
    op.drop_constraint(NEW_UNIQUE_CONSTRAINT_NAME, 'working_hours', type_='unique')

    # Recreate the old unique constraint on staff_id
    op.create_unique_constraint(OLD_UNIQUE_CONSTRAINT_NAME, 'working_hours', ['staff_id'])
