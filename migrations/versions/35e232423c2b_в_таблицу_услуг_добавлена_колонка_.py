"""В таблицу услуг добавлена колонка deleted

Revision ID: 35e232423c2b
Revises: 0f47320f0682
Create Date: 2025-03-26 17:34:56.902368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35e232423c2b'
down_revision: Union[str, None] = '0f47320f0682'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'service',
        sa.Column(
            'deleted',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment='Удалена ли услуга',
        ),
    )


def downgrade() -> None:
    op.drop_column('service', 'deleted')
