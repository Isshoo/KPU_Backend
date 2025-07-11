"""update table

Revision ID: 06887e90bea9
Revises: e650881aa952
Create Date: 2025-06-24 00:05:31.563692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06887e90bea9'
down_revision: Union[str, None] = 'e650881aa952'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('surat_keluar_dibaca_oleh')
    op.drop_table('surat_masuk_dibaca_oleh')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('surat_masuk_dibaca_oleh',
    sa.Column('surat_masuk_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['surat_masuk_id'], ['surat_masuk.id'], name=op.f('surat_masuk_dibaca_oleh_surat_masuk_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('surat_masuk_dibaca_oleh_user_id_fkey')),
    sa.PrimaryKeyConstraint('surat_masuk_id', 'user_id', name=op.f('surat_masuk_dibaca_oleh_pkey'))
    )
    op.create_table('surat_keluar_dibaca_oleh',
    sa.Column('surat_keluar_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['surat_keluar_id'], ['surat_keluar.id'], name=op.f('surat_keluar_dibaca_oleh_surat_keluar_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('surat_keluar_dibaca_oleh_user_id_fkey')),
    sa.PrimaryKeyConstraint('surat_keluar_id', 'user_id', name=op.f('surat_keluar_dibaca_oleh_pkey'))
    )
    # ### end Alembic commands ###
