"""Удалена таблица клиентов

Revision ID: 45cad3961ada
Revises: 2d8f49b36721
Create Date: 2025-03-12 15:34:23.550824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45cad3961ada'
down_revision: Union[str, None] = '2d8f49b36721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('zapis') as batch_op:
        batch_op.drop_constraint('fk_zapis_client_id_client', type_='foreignkey')
    op.drop_table('client')
    with op.batch_alter_table('zapis') as batch_op:
        batch_op.alter_column('client_id', comment="Идентификатор клиента (телеграмм ID)")


def downgrade() -> None:
    op.create_table(
        'client',
        sa.Column('client_id', sa.INTEGER(), nullable=False),
        sa.Column('username', sa.VARCHAR(length=50), nullable=True),
        sa.PrimaryKeyConstraint('client_id', name='pk_client')
    )
    with op.batch_alter_table('zapis') as batch_op:
        batch_op.create_foreign_key(
            'fk_zapis_client_id_client',
            'client',
            ['client_id'],
            ['client_id'],
            ondelete='RESTRICT',
        )
    with op.batch_alter_table('zapis') as batch_op:
        batch_op.alter_column('client_id', comment="Идентификатор клиента")
