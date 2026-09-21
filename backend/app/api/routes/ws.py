"""Real-time trip tracking over WebSocket.

Both drivers and passengers connect to `/ws/trip/{trip_id}?token=<jwt>&role=driver|passenger`.
The JWT is the same access token issued by /auth/login and /auth/register — it
is passed as a query parameter because browsers/WebSocket clients cannot set
custom headers on the handshake. Only the trip's passenger (Trip.user_id) or
an authenticated driver may join a room; every other connection is rejected
before the handshake completes.

A driver connects with role=driver and periodically sends
{"latitude": .., "longitude": ..} messages. Every other participant
connected to the same trip room (typically the passenger, role=passenger)
receives the broadcasted location update as
{"type": "location", "latitude": .., "longitude": ..}.

REST-driven location updates (see app/services/driver_service.py) also relay
into the same room via `manager.broadcast_from_server`, so a driver can push
its location either over this socket or via POST /driver/location.

This in-memory connection manager works for a single backend instance.
For multi-instance deployments, back it with Redis pub/sub instead.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.core.config import settings
from app.models import AuthSession, Trip, User

router = APIRouter()


class TripConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, trip_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms.setdefault(trip_id, []).append(websocket)

    def disconnect(self, trip_id: str, websocket: WebSocket) -> None:
        connections = self._rooms.get(trip_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and trip_id in self._rooms:
            del self._rooms[trip_id]

    async def broadcast(self, trip_id: str, sender: WebSocket, message: dict) -> None:
        for connection in self._rooms.get(trip_id, []):
            if connection is not sender:
                await connection.send_json(message)

    async def broadcast_from_server(self, trip_id: str, message: dict) -> None:
        """Used by REST endpoints (no WebSocket sender) to relay a message."""
        for connection in self._rooms.get(trip_id, []):
            await connection.send_json(message)


manager = TripConnectionManager()


def _authenticate(db: Session, token: str | None, trip_id: str, role: str) -> User | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id = payload.get('sub')
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        return None
    if settings.require_session_bound_tokens:
        session = db.query(AuthSession).filter(AuthSession.id == payload.get('sid'), AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).first()
        if not session:
            return None
        expiry = session.expires_at.replace(tzinfo=timezone.utc) if session.expires_at.tzinfo is None else session.expires_at
        if expiry <= datetime.now(timezone.utc):
            return None

    if role == 'passenger':
        trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
        if trip is None:
            return None
    elif role == 'driver':
        trip = db.query(Trip).filter(Trip.id == trip_id, Trip.driver_id == user.id, Trip.assignment_status == 'assigned').first()
        if user.role != 'driver' or trip is None:
            return None
    else:
        return None

    return user


@router.websocket('/trip/{trip_id}')
async def trip_tracking(
    websocket: WebSocket,
    trip_id: str,
    role: str = Query(default='passenger'),
    token: str | None = Query(default=None),
) -> None:
    db = SessionLocal()
    try:
        user = _authenticate(db, token, trip_id, role)
    finally:
        db.close()

    if user is None:
        await websocket.close(code=4401)
        return

    await manager.connect(trip_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if role == 'driver' and 'latitude' in data and 'longitude' in data:
                await manager.broadcast(
                    trip_id,
                    websocket,
                    {
                        'type': 'location',
                        'latitude': data['latitude'],
                        'longitude': data['longitude'],
                    },
                )
    except WebSocketDisconnect:
        manager.disconnect(trip_id, websocket)
