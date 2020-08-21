"""empty message

Revision ID: 4a21b876efab
Revises: 
Create Date: 2020-08-20 14:15:39.178530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a21b876efab'
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
    sa.Column('secret_key', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('source', sa.String(), nullable=True),
    sa.Column('gituser', sa.String(), nullable=True),
    sa.Column('gitrepo', sa.String(), nullable=True),
    sa.Column('gitbranch', sa.String(), nullable=True),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('associated_email', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_address', sa.String(), nullable=True),
    sa.Column('login_key', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('script')
    op.drop_table('line')
    op.drop_table('comment')
    # ### end Alembic commands ###