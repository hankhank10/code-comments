"""empty message

Revision ID: de7f8cc3e70d
Revises: 
Create Date: 2020-08-16 21:01:01.106901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de7f8cc3e70d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('script_id', sa.Integer(), nullable=True),
    sa.Column('line_number', sa.Integer(), nullable=True),
    sa.Column('line_unique_key', sa.String(), nullable=True),
    sa.Column('unique_key', sa.String(), nullable=True),
    sa.Column('written_by', sa.String(), nullable=True),
    sa.Column('comment_type', sa.String(), nullable=True),
    sa.Column('content_comment', sa.String(), nullable=True),
    sa.Column('content_code', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('line',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('script_id', sa.Integer(), nullable=True),
    sa.Column('line_number', sa.Integer(), nullable=True),
    sa.Column('unique_key', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('script',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unique_key', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('source', sa.String(), nullable=True),
    sa.Column('gituser', sa.String(), nullable=True),
    sa.Column('gitrepo', sa.String(), nullable=True),
    sa.Column('gitbranch', sa.String(), nullable=True),
    sa.Column('filename', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('script')
    op.drop_table('line')
    op.drop_table('comment')
    # ### end Alembic commands ###
