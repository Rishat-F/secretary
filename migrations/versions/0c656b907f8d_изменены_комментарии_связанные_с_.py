"""Изменены комментарии, связанные с таблицей appointment

Revision ID: 0c656b907f8d
Revises: 5a444514673b
Create Date: 2025-03-28 11:58:34.821114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c656b907f8d'
down_revision: Union[str, None] = '5a444514673b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('appointment') as batch_op:
        batch_op.create_table_comment(
            comment="Прием (оказание услуги)",
            existing_comment="Запись на прием",
        )
        batch_op.alter_column(
            'appointment_id',
            comment="Идентификатор приема (оказания услуги)",
            existing_comment="Идентификатор записи",
        )
    with op.batch_alter_table('slot') as batch_op:
        batch_op.alter_column(
            'appointment_id',
            comment="Идентификатор приема (оказания услуги)",
            existing_comment="Идентификатор записи",
        )


def downgrade() -> None:
    with op.batch_alter_table('appointment') as batch_op:
        batch_op.create_table_comment(
            comment="Запись на прием",
            existing_comment="Прием (оказание услуги)",
        )
        batch_op.alter_column(
            'appointment_id',
            comment="Идентификатор записи",
            existing_comment="Идентификатор приема (оказания услуги)",
        )
    with op.batch_alter_table('slot') as batch_op:
        batch_op.alter_column(
            'appointment_id',
            comment="Идентификатор записи",
            existing_comment="Идентификатор приема (оказания услуги)",
        )
