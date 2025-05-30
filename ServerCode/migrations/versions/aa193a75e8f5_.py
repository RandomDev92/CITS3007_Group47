"""empty message

Revision ID: aa193a75e8f5
Revises: 6fbf533c8bdc
Create Date: 2025-05-12 17:29:00.219351

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa193a75e8f5'
down_revision = '6fbf533c8bdc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('best_time', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.drop_column('best_time')

    # ### end Alembic commands ###
