"""operational auth, booking, dispatch, and audit hardening

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('trips', sa.Column('idempotency_key', sa.String(100), nullable=True))
    op.add_column('trips', sa.Column('driver_id', sa.String(36), nullable=True))
    op.add_column('trips', sa.Column('assignment_status', sa.String(20), nullable=False, server_default='unassigned'))
    op.create_foreign_key('fk_trips_driver_id_users', 'trips', 'users', ['driver_id'], ['id'])
    op.create_unique_constraint('uq_trips_idempotency_key', 'trips', ['idempotency_key'])
    op.create_index('ix_trips_driver_id', 'trips', ['driver_id'])
    op.add_column('payments', sa.Column('idempotency_key', sa.String(100), nullable=True))
    op.add_column('payments', sa.Column('gateway_reference', sa.String(100), nullable=True))
    op.create_unique_constraint('uq_payments_idempotency_key', 'payments', ['idempotency_key'])
    op.create_unique_constraint('uq_payments_gateway_reference', 'payments', ['gateway_reference'])
    op.create_table(
        'trip_quotes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('options', sa.JSON(), nullable=False),
        sa.Column('origin_lat', sa.DECIMAL(10, 8)),
        sa.Column('origin_lng', sa.DECIMAL(11, 8)),
        sa.Column('dest_lat', sa.DECIMAL(10, 8)),
        sa.Column('dest_lng', sa.DECIMAL(11, 8)),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('consumed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_trip_quotes_user_id', 'trip_quotes', ['user_id'])
    op.create_index('ix_trip_quotes_expires_at', 'trip_quotes', ['expires_at'])
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('refresh_jti', sa.String(64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime()),
        sa.Column('revoke_reason', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_expires_at', 'auth_sessions', ['expires_at'])
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('actor_id', sa.String(36)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(100)),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('correlation_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_correlation_id', 'audit_logs', ['correlation_id'])


def downgrade() -> None:
    op.drop_index('ix_audit_logs_correlation_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_actor_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_auth_sessions_expires_at', table_name='auth_sessions')
    op.drop_index('ix_auth_sessions_user_id', table_name='auth_sessions')
    op.drop_table('auth_sessions')
    op.drop_index('ix_trip_quotes_expires_at', table_name='trip_quotes')
    op.drop_index('ix_trip_quotes_user_id', table_name='trip_quotes')
    op.drop_table('trip_quotes')
    op.drop_constraint('uq_payments_gateway_reference', 'payments', type_='unique')
    op.drop_constraint('uq_payments_idempotency_key', 'payments', type_='unique')
    op.drop_column('payments', 'gateway_reference')
    op.drop_column('payments', 'idempotency_key')
    op.drop_index('ix_trips_driver_id', table_name='trips')
    op.drop_constraint('uq_trips_idempotency_key', 'trips', type_='unique')
    op.drop_constraint('fk_trips_driver_id_users', 'trips', type_='foreignkey')
    op.drop_column('trips', 'assignment_status')
    op.drop_column('trips', 'driver_id')
    op.drop_column('trips', 'idempotency_key')
    op.drop_column('users', 'is_active')
