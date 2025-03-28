"""Добавлена таблица бронирования

Revision ID: 6e9c4b747398
Revises: 0c656b907f8d
Create Date: 2025-03-28 13:25:38.421918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e9c4b747398'
down_revision: Union[str, None] = '0c656b907f8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reservation',
        sa.Column('slot_id', sa.Integer(), nullable=False, comment='Идентификатор слота'),
        sa.Column('appointment_id', sa.Integer(), nullable=False, comment='Идентификатор приема (оказания услуги)'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointment.appointment_id'], name='fk_reservation_appointment_id_appointment', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['slot_id'], ['slot.slot_id'], name='fk_reservation_slot_id_slot', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('slot_id', name='pk_reservation'),
        comment='Бронирование (запись на прием)'
    )
    with op.batch_alter_table('slot') as batch_op:
        batch_op.drop_constraint('fk_slot_appointment_id_appointment', type_='foreignkey')
        batch_op.drop_column('appointment_id')


def downgrade() -> None:
    with op.batch_alter_table('slot') as batch_op:
        batch_op.add_column(sa.Column('appointment_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_slot_appointment_id_appointment', 'appointment', ['appointment_id'], ['appointment_id'], ondelete='SET NULL')
    op.drop_table('reservation')
