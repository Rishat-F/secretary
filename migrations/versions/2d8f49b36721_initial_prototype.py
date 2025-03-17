"""Initial prototype

Revision ID: 2d8f49b36721
Revises:
Create Date: 2025-03-04 17:38:25.457149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d8f49b36721'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'client',
        sa.Column('client_id', sa.Integer(), autoincrement=False, nullable=False, comment='Идентификатор клиента (телеграмм ID)'),
        sa.Column('username', sa.String(length=50), nullable=True, comment='Алиас пользователя в телеграмме'),
        sa.PrimaryKeyConstraint('client_id', name=op.f('pk_client')),
        comment='Клиент (например, тот кого стрижет парикмахер)'
    )
    op.create_table(
        'usluga',
        sa.Column('usluga_id', sa.Integer(), autoincrement=True, nullable=False, comment='Идентификатор услуги'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Название услуги'),
        sa.Column('price', sa.Integer(), nullable=False, comment='Стоимость услуги'),
        sa.Column('duration', sa.Integer(), nullable=False, comment='Длительность предоставления услуги (в минутах, должно быть кратно 30)'),
        sa.PrimaryKeyConstraint('usluga_id', name=op.f('pk_usluga')),
        sa.UniqueConstraint('name', name=op.f('uq_usluga_name')),
        comment="Услуга (например, 'Стрижка модельная')"
    )
    op.create_table(
        'zapis',
        sa.Column('zapis_id', sa.Integer(), autoincrement=True, nullable=False, comment='Идентификатор записи'),
        sa.Column('client_id', sa.Integer(), nullable=False, comment='Идентификатор клиента'),
        sa.Column('usluga_id', sa.Integer(), nullable=True, comment='Идентификатор услуги'),
        sa.Column('starts_at', sa.DateTime(), nullable=False, comment='Дата и время начала приема (должно быть кратно 30 минутам)'),
        sa.Column('ends_at', sa.DateTime(), nullable=False, comment='Дата и время окончания приема (должно быть кратно 30 минутам)'),
        sa.ForeignKeyConstraint(['client_id'], ['client.client_id'], name=op.f('fk_zapis_client_id_client'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['usluga_id'], ['usluga.usluga_id'], name=op.f('fk_zapis_usluga_id_usluga'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('zapis_id', name=op.f('pk_zapis')),
        comment='Запись на прием'
    )


def downgrade() -> None:
    op.drop_table('zapis')
    op.drop_table('usluga')
    op.drop_table('client')
