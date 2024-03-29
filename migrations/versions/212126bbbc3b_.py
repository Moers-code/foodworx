"""empty message

Revision ID: 212126bbbc3b
Revises: 
Create Date: 2023-05-17 19:28:57.595247

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '212126bbbc3b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('expiry_date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expiry_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('category')

    # ### end Alembic commands ###
