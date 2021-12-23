"""empty message

Revision ID: b9e91d100f64
Revises: 12540e226c91
Create Date: 2019-09-27 22:40:57.973829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9e91d100f64'
down_revision = '12540e226c91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_table('test')
    op.alter_column('ad', 'size', existing_type=sa.INTEGER(), type_=sa.TEXT())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test',
    sa.Column('id_', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('testing', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id_', name='test_pkey')
    )
    # ### end Alembic commands ###