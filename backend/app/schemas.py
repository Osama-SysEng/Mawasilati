from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

Role = Literal['passenger', 'driver', 'admin']
PaymentMethod = Literal['instapay', 'visa', 'wallet']
TripStatus = Literal['planned', 'active', 'completed', 'cancelled']
TransportType = Literal['metro', 'train', 'microbus', 'uber', 'indrive', 'didi', 'tuktuk']


class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str = Field(min_length=6)
    role: Role = 'passenger'
    wallet_balance: float = 0.0


class LoginRequest(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    phone: str
    role: Role
    wallet_balance: float

    model_config = {'from_attributes': True}


class TokenResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int
    session_id: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class TripPlanRequest(BaseModel):
    origin_label: str | None = None
    destination_label: str | None = None
    origin_lat: float | None = None
    origin_lng: float | None = None
    dest_lat: float | None = None
    dest_lng: float | None = None
    budget: float | None = None
    requested_at: datetime | None = None
    preferred_transport: list[TransportType] = Field(default_factory=list)


class TripBookRequest(BaseModel):
    user_id: UUID | None = None
    option: dict[str, Any]
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=100)
    quote_id: UUID | None = None
    option_id: UUID | None = None


class PaymentRequest(BaseModel):
    user_id: UUID | None = None
    trip_id: UUID
    method: PaymentMethod
    amount: float
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=100)


class AIChatRequest(BaseModel):
    user_id: UUID | None = None
    message: str


class ParseTripRequest(BaseModel):
    text: str


class DriverLocationRequest(BaseModel):
    # driver_id is intentionally NOT accepted here — the driver is always the
    # authenticated current user, never a client-supplied value (prevents
    # spoofing another driver's location).
    latitude: float
    longitude: float
    trip_id: UUID | None = None
