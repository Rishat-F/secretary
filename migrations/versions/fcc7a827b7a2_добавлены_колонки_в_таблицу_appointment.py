"""Добавлены колонки в таблицу appointment

Revision ID: fcc7a827b7a2
Revises: 6e9c4b747398
Create Date: 2025-03-28 20:59:09.289193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcc7a827b7a2'
down_revision: Union[str, None] = '6e9c4b747398'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'appointment',
        sa.Column(
            'starts_at',
            sa.DateTime(),
            nullable=False,
            server_default="2000-01-01 10:00",
            comment='Дата и время начала приема (должно быть кратно 30 минутам)',
        ),
    )
    op.add_column(
        'appointment',
        sa.Column(
            'ends_at',
            sa.DateTime(),
            nullable=False,
            server_default="2000-01-01 11:00",
            comment='Дата и время окончания приема (должно быть кратно 30 минутам)',
        ),
    )


def downgrade() -> None:
    op.drop_column('appointment', 'ends_at')
    op.drop_column('appointment', 'starts_at')
