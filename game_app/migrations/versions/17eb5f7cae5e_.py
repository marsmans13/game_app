"""empty message

Revision ID: 17eb5f7cae5e
Revises: 627887973a60
Create Date: 2022-02-06 09:21:18.384525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17eb5f7cae5e'
down_revision = '627887973a60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('word_game',
    sa.Column('word_game_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('word_id', sa.Integer(), nullable=True),
    sa.Column('word_num', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.game_id'], ),
    sa.ForeignKeyConstraint(['word_id'], ['word.word_id'], ),
    sa.PrimaryKeyConstraint('word_game_id')
    )
    op.add_column('game', sa.Column('num_words', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'num_words')
    op.drop_table('word_game')
    # ### end Alembic commands ###
