"""Init

Revision ID: a87e2a697ae2
Revises: 
Create Date: 2021-03-29 15:58:18.258014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a87e2a697ae2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=64), nullable=True, comment='Статус сервера'),
    sa.Column('deleted', sa.DateTime(), nullable=True, comment='Время удаления сервера'),
    sa.Column('active', sa.Boolean(), nullable=True, comment='Маркер запуска сервера'),
    sa.Column('location', sa.String(length=16), nullable=True, comment='Распроложение сервера'),
    sa.Column('locked', sa.Boolean(), nullable=True),
    sa.Column('hostname', sa.String(length=255), nullable=True, comment='Наименование хоста'),
    sa.Column('created', sa.DateTime(), nullable=True, comment='Время создания сервера'),
    sa.Column('made_from', sa.String(length=255), nullable=True, comment='Id образа или бэкапа, на основе которого создан сервер'),
    sa.Column('name', sa.String(length=255), nullable=True, comment='Имя сервера'),
    sa.Column('ext_ctid', sa.Integer(), nullable=True, comment='Идентификатор сервера в vscale.io'),
    sa.Column('rplan', sa.String(length=16), nullable=True, comment='Id тарифного плана'),
    sa.Column('public_address_gateway', sa.String(length=64), nullable=True, comment='Публичный гейтвей'),
    sa.Column('public_address_netmask', sa.String(length=64), nullable=True, comment='Публичная маска сети'),
    sa.Column('public_address_address', sa.String(length=64), nullable=True, comment='Публичный адрес'),
    sa.Column('private_address_gateway', sa.String(length=64), nullable=True, comment='Приватный гейтвей'),
    sa.Column('private_address_netmask', sa.String(length=64), nullable=True, comment='Приватная маска сети'),
    sa.Column('private_address_address', sa.String(length=64), nullable=True, comment='Приватный адрес'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_server_deleted'), 'server', ['deleted'], unique=False)
    op.create_index(op.f('ix_server_id'), 'server', ['id'], unique=False)
    op.create_table('key',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('external_id', sa.Integer(), nullable=True, comment='Идентификатор ключа в vscale.io'),
    sa.Column('name', sa.String(length=255), nullable=True, comment='Имя ключа'),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_key_id'), 'key', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_key_id'), table_name='key')
    op.drop_table('key')
    op.drop_index(op.f('ix_server_id'), table_name='server')
    op.drop_index(op.f('ix_server_deleted'), table_name='server')
    op.drop_table('server')
    # ### end Alembic commands ###
