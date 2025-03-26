"""Добавлена таблица слотов приема

Revision ID: 0f47320f0682
Revises: 1819e777466b
Create Date: 2025-03-26 15:51:58.131828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f47320f0682'
down_revision: Union[str, None] = '1819e777466b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'slot',
        sa.Column('slot_id', sa.Integer(), autoincrement=True, nullable=False, comment='Идентификатор слота'),
        sa.Column('date_', sa.Date(), nullable=False, comment='Дата слота'),
        sa.Column('number', sa.Integer(), nullable=False, comment='Номер слота: 1 - 00:00 - 00:30, 2 - 00:30 - 01:00, ..., 47 - 23:00 - 23:30, 48 - 23:00 - 00:00'),
        sa.Column('appointment_id', sa.Integer(), nullable=True, comment='Идентификатор записи'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointment.appointment_id'], name=op.f('fk_slot_appointment_id_appointment'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('slot_id', name=op.f('pk_slot')),
        sa.UniqueConstraint('date_', 'number', name=op.f('uq_slot_date__number')),
        comment='Слоты приема (30 минутные интервалы)',
    )
    op.drop_column('appointment', 'ends_at')
    op.drop_column('appointment', 'starts_at')


def downgrade() -> None:
    op.add_column('appointment', sa.Column('starts_at', sa.DATETIME(), nullable=False, server_default="2000-01-01 10:00"))
    op.add_column('appointment', sa.Column('ends_at', sa.DATETIME(), nullable=False, server_default="2000-01-01 11:00"))
    op.drop_table('slot')
