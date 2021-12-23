"""empty message

Revision ID: 4286f900f802
Revises: b9e91d100f64
Create Date: 2019-09-27 22:46:08.320178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4286f900f802'
down_revision = 'b9e91d100f64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ad', 'size', existing_type=sa.INTEGER(), type_=sa.TEXT())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test')
    # ### end Alembic commands ###
