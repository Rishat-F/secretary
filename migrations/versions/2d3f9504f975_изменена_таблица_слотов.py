"""Изменена таблица слотов

Revision ID: 2d3f9504f975
Revises: fcc7a827b7a2
Create Date: 2025-03-31 19:14:29.612681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d3f9504f975'
down_revision: Union[str, None] = 'fcc7a827b7a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('slot') as batch_op:
        batch_op.drop_constraint('uq_slot_date__number', type_='unique')
        batch_op.drop_constraint('pk_slot', type_='primary')
        batch_op.drop_column('slot_id')
        batch_op.drop_column('date_')
        batch_op.drop_column('number')
        batch_op.add_column(sa.Column('datetime_', sa.DateTime(), primary_key=True, server_default=sa.func.now(), nullable=False, comment='Дата и время слота'))

    with op.batch_alter_table('reservation') as batch_op:
        batch_op.drop_constraint('fk_reservation_slot_id_slot', type_='foreignkey')
        batch_op.drop_constraint('pk_reservation', type_='primary')
        batch_op.add_column(sa.Column('datetime_', sa.DateTime(), primary_key=True, server_default=sa.func.now(), nullable=False, comment='Дата и время слота'))
        batch_op.create_foreign_key('fk_reservation_datetime__slot', 'slot', ['datetime_'], ['datetime_'], ondelete='CASCADE')
        batch_op.drop_column('slot_id')


def downgrade() -> None:
    with op.batch_alter_table('slot') as batch_op:
        batch_op.drop_constraint('pk_slot', type_='primary')
        batch_op.add_column(sa.Column('slot_id', sa.INTEGER(), primary_key=True, autoincrement=True, nullable=False))
        batch_op.add_column(sa.Column('date_', sa.DATE(), nullable=False))
        batch_op.add_column(sa.Column('number', sa.INTEGER(), nullable=False))
        batch_op.create_unique_constraint('uq_slot_date__number', ['date_', 'number'])
        batch_op.drop_column('datetime_')

    with op.batch_alter_table('reservation') as batch_op:
        batch_op.drop_constraint('fk_reservation_datetime__slot', type_='foreignkey')
        batch_op.drop_constraint('pk_reservation', type_='primary')
        batch_op.add_column(sa.Column('slot_id', sa.INTEGER(), primary_key=True, nullable=False))
        batch_op.create_foreign_key('fk_reservation_slot_id_slot', 'slot', ['slot_id'], ['slot_id'], ondelete='CASCADE')
        batch_op.drop_column('datetime_')
