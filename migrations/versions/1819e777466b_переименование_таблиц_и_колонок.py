"""Переименование таблиц и колонок

Revision ID: 1819e777466b
Revises: 45cad3961ada
Create Date: 2025-03-21 14:29:49.096908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1819e777466b'
down_revision: Union[str, None] = '45cad3961ada'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('usluga') as batch_op:
        batch_op.drop_constraint('pk_usluga', type_='primary')
        batch_op.drop_constraint('uq_usluga_name', type_='unique')
        batch_op.alter_column(column_name='usluga_id', new_column_name='service_id')
    op.rename_table('usluga', 'service')
    with op.batch_alter_table('service') as batch_op:
        batch_op.create_primary_key('pk_service', ['service_id'])
        batch_op.create_unique_constraint('uq_service_name', ['name'])
    with op.batch_alter_table('zapis') as batch_op:
        batch_op.drop_constraint('pk_zapis', type_='primary')
        batch_op.drop_constraint('fk_zapis_usluga_id_usluga', type_='foreignkey')
        batch_op.alter_column(column_name='zapis_id', new_column_name='appointment_id')
        batch_op.alter_column(column_name='usluga_id', new_column_name='service_id')
    op.rename_table('zapis', 'appointment')
    with op.batch_alter_table('appointment') as batch_op:
        batch_op.create_primary_key('pk_appointment', ['appointment_id'])
        batch_op.create_foreign_key(
            'fk_appointment_service_id_service',
            'service',
            ['service_id'],
            ['service_id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    with op.batch_alter_table('service') as batch_op:
        batch_op.drop_constraint('pk_service', type_='primary')
        batch_op.drop_constraint('uq_service_name', type_='unique')
        batch_op.alter_column(column_name='service_id', new_column_name='usluga_id')
    op.rename_table('service', 'usluga')
    with op.batch_alter_table('usluga') as batch_op:
        batch_op.create_primary_key('pk_usluga', ['usluga_id'])
        batch_op.create_unique_constraint('uq_usluga_name', ['name'])

    with op.batch_alter_table('appointment') as batch_op:
        batch_op.drop_constraint('pk_appointment', type_='primary')
        batch_op.drop_constraint('fk_appointment_service_id_service', type_='foreignkey')
        batch_op.alter_column(column_name='appointment_id', new_column_name='zapis_id')
        batch_op.alter_column(column_name='service_id', new_column_name='usluga_id')
    op.rename_table('appointment', 'zapis')
    with op.batch_alter_table('zapis') as batch_op:
        batch_op.create_primary_key('pk_zapis', ['zapis_id'])
        batch_op.create_foreign_key(
            'fk_zapis_usluga_id_usluga',
            'usluga',
            ['usluga_id'],
            ['usluga_id'],
            ondelete='SET NULL',
        )
