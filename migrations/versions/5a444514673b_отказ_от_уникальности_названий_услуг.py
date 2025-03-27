"""Отказ от уникальности названий услуг

Revision ID: 5a444514673b
Revises: d3f275f03adf
Create Date: 2025-03-27 11:14:19.348526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a444514673b'
down_revision: Union[str, None] = 'd3f275f03adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('service') as batch_op:
        batch_op.drop_constraint('uq_service_name', type_='unique')


def downgrade() -> None:
    with op.batch_alter_table('service') as batch_op:
        batch_op.create_unique_constraint('uq_service_name', ['name'])
