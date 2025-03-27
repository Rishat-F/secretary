"""Запрет на удаление услуги из БД, если на нее имеется запись

Revision ID: d3f275f03adf
Revises: 35e232423c2b
Create Date: 2025-03-27 11:06:49.538461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f275f03adf'
down_revision: Union[str, None] = '35e232423c2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('appointment') as batch_op:
        batch_op.alter_column(
            'service_id',
            existing_type=sa.INTEGER(),
            nullable=False,
        )
        batch_op.drop_constraint('fk_appointment_service_id_service', type_='foreignkey')
        batch_op.create_foreign_key('fk_appointment_service_id_service', 'service', ['service_id'], ['service_id'], ondelete='RESTRICT')


def downgrade() -> None:
    with op.batch_alter_table('appointment') as batch_op:
        batch_op.drop_constraint('fk_appointment_service_id_service', type_='foreignkey')
        batch_op.create_foreign_key('fk_appointment_service_id_service', 'service', ['service_id'], ['service_id'], ondelete='SET NULL')
        batch_op.alter_column(
            'service_id',
            existing_type=sa.INTEGER(),
            nullable=True,
        )
