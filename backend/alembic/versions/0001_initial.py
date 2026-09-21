"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-08

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('wallet_balance', sa.DECIMAL(10, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_phone', 'users', ['phone'])

    op.create_table(
        'routes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('transport_type', sa.String(30), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('total_stops', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('base_price', sa.DECIMAL(8, 2), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        'stops',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('route_id', sa.String(36), sa.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('latitude', sa.DECIMAL(10, 8), nullable=False),
        sa.Column('longitude', sa.DECIMAL(11, 8), nullable=False),
        sa.Column('stop_order', sa.Integer(), nullable=False),
    )
    op.create_index('ix_stops_route_id', 'stops', ['route_id'])

    op.create_table(
        'trips',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('origin_lat', sa.DECIMAL(10, 8), nullable=False),
        sa.Column('origin_lng', sa.DECIMAL(11, 8), nullable=False),
        sa.Column('dest_lat', sa.DECIMAL(10, 8), nullable=False),
        sa.Column('dest_lng', sa.DECIMAL(11, 8), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('total_price', sa.DECIMAL(8, 2), nullable=False, server_default='0'),
        sa.Column('transport_mix', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_trips_user_id', 'trips', ['user_id'])

    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('method', sa.String(20), nullable=False),
        sa.Column('amount', sa.DECIMAL(8, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])

    op.create_table(
        'driver_locations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('driver_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('latitude', sa.DECIMAL(10, 8), nullable=False),
        sa.Column('longitude', sa.DECIMAL(11, 8), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_driver_locations_driver_id', 'driver_locations', ['driver_id'])

    op.create_table(
        'ai_conversations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('parsed_intent', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_ai_conversations_user_id', 'ai_conversations', ['user_id'])


def downgrade() -> None:
    op.drop_table('ai_conversations')
    op.drop_table('driver_locations')
    op.drop_table('payments')
    op.drop_table('trips')
    op.drop_table('stops')
    op.drop_table('routes')
    op.drop_table('users')
