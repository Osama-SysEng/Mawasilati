from sqlalchemy import JSON, Boolean, Column, DateTime, DECIMAL, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    wallet_balance = Column(DECIMAL(10, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Route(Base):
    __tablename__ = 'routes'

    id = Column(String(36), primary_key=True, index=True)
    transport_type = Column(String(30), nullable=False)
    name = Column(String(100), nullable=False)
    total_stops = Column(Integer, nullable=False, default=0)
    base_price = Column(DECIMAL(8, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)


class Stop(Base):
    __tablename__ = 'stops'

    id = Column(String(36), primary_key=True, index=True)
    route_id = Column(String(36), ForeignKey('routes.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    stop_order = Column(Integer, nullable=False)


class Trip(Base):
    __tablename__ = 'trips'

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    origin_lat = Column(DECIMAL(10, 8), nullable=False)
    origin_lng = Column(DECIMAL(11, 8), nullable=False)
    dest_lat = Column(DECIMAL(10, 8), nullable=False)
    dest_lng = Column(DECIMAL(11, 8), nullable=False)
    status = Column(String(20), nullable=False)
    total_price = Column(DECIMAL(8, 2), nullable=False, default=0)
    transport_mix = Column(JSON, nullable=False)
    idempotency_key = Column(String(100), nullable=True, unique=True, index=True)
    driver_id = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)
    assignment_status = Column(String(20), nullable=False, default='unassigned')
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class TripQuote(Base):
    __tablename__ = 'trip_quotes'
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    options = Column(JSON, nullable=False)
    origin_lat = Column(DECIMAL(10, 8), nullable=True)
    origin_lng = Column(DECIMAL(11, 8), nullable=True)
    dest_lat = Column(DECIMAL(10, 8), nullable=True)
    dest_lng = Column(DECIMAL(11, 8), nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    consumed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    trip_id = Column(String(36), ForeignKey('trips.id'), nullable=False, index=True)
    method = Column(String(20), nullable=False)
    amount = Column(DECIMAL(8, 2), nullable=False)
    status = Column(String(20), nullable=False)
    idempotency_key = Column(String(100), nullable=True, unique=True, index=True)
    gateway_reference = Column(String(100), nullable=True, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class DriverLocation(Base):
    __tablename__ = 'driver_locations'

    id = Column(String(36), primary_key=True, index=True)
    driver_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)


class AIConversation(Base):
    __tablename__ = 'ai_conversations'

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    parsed_intent = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class AuthSession(Base):
    __tablename__ = 'auth_sessions'
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    refresh_jti = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    revoke_reason = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(36), primary_key=True, index=True)
    actor_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=False, default=dict)
    correlation_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
