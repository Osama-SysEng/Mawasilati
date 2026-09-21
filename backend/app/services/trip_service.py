from datetime import datetime, timedelta, timezone
from math import hypot
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.config import settings
from app.models import Trip, TripQuote


def _estimate_distance_km(origin_lat: float | None, origin_lng: float | None, dest_lat: float | None, dest_lng: float | None) -> float:
    if None in (origin_lat, origin_lng, dest_lat, dest_lng):
        return 10.0
    return max(1.0, hypot(dest_lat - origin_lat, dest_lng - origin_lng) * 111)


def build_trip_options(payload: dict) -> dict:
    distance = _estimate_distance_km(payload.get('origin_lat'), payload.get('origin_lng'), payload.get('dest_lat'), payload.get('dest_lng'))
    options = [
        {'id': str(uuid4()), 'route': ['مترو', 'تحويل قصير', 'مايكروباص'], 'price': round(max(6, distance * 0.8), 2), 'time': f'{int(25 + distance * 1.6)} دقيقة', 'type': 'الأرخص'},
        {'id': str(uuid4()), 'route': ['أوبر مباشر'], 'price': round(max(35, distance * 4.2), 2), 'time': f'{int(18 + distance * 0.9)} دقيقة', 'type': 'الأسرع'},
        {'id': str(uuid4()), 'route': ['ميكروباص', 'مترو', 'مشية قصيرة'], 'price': round(max(10, distance * 1.2), 2), 'time': f'{int(30 + distance * 1.2)} دقيقة', 'type': 'الأمثل'},
    ]
    budget = payload.get('budget')
    if budget is not None:
        within_budget = [option for option in options if option['price'] <= budget]
        if within_budget:
            options = within_budget + [option for option in options if option not in within_budget]
    return {'options': options, 'estimated_distance_km': round(distance, 2)}


def issue_trip_quote(db: Session, user_id: str, payload: dict) -> dict:
    plan = build_trip_options(payload)
    quote = TripQuote(
        id=str(uuid4()), user_id=user_id, options=plan['options'],
        origin_lat=payload.get('origin_lat'), origin_lng=payload.get('origin_lng'),
        dest_lat=payload.get('dest_lat'), dest_lng=payload.get('dest_lng'),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.trip_quote_ttl_minutes),
    )
    db.add(quote)
    append_audit(db, actor_id=user_id, action='TRIP_QUOTE_ISSUED', entity_type='TripQuote', entity_id=quote.id, details={'option_count': len(plan['options'])})
    db.commit()
    return {**plan, 'quote_id': quote.id, 'expires_at': quote.expires_at.isoformat()}


def book_trip(db: Session, user_id: str, payload: dict) -> dict:
    idempotency_key = payload.get('idempotency_key')
    if idempotency_key:
        existing = db.query(Trip).filter(Trip.idempotency_key == idempotency_key, Trip.user_id == user_id).first()
        if existing:
            return {'trip_id': existing.id, 'status': existing.status, 'total_price': float(existing.total_price), 'booked_option': {'route': existing.transport_mix, 'price': float(existing.total_price)}, 'idempotent_replay': True}
    option = payload.get('option') or {}
    quote_id = payload.get('quote_id')
    if quote_id:
        quote = db.query(TripQuote).filter(TripQuote.id == str(quote_id), TripQuote.user_id == user_id, TripQuote.consumed_at.is_(None)).first()
        quote_expiry = quote.expires_at.replace(tzinfo=timezone.utc) if quote and quote.expires_at.tzinfo is None else (quote.expires_at if quote else None)
        if not quote or not quote_expiry or quote_expiry <= datetime.now(timezone.utc):
            raise ValueError('Trip quote is missing, expired, or already consumed')
        option = next((item for item in quote.options if item['id'] == str(payload.get('option_id'))), None)
        if not option:
            raise ValueError('Selected option is not part of the current trip quote')
        payload = {**payload, 'origin_lat': quote.origin_lat, 'origin_lng': quote.origin_lng, 'dest_lat': quote.dest_lat, 'dest_lng': quote.dest_lng}
        quote.consumed_at = datetime.now(timezone.utc)
    elif settings.environment == 'production' and settings.require_signed_quotes_in_production:
        raise ValueError('Production booking requires a valid trip quote')
    if float(option.get('price', 0)) <= 0 or not option.get('route'):
        raise ValueError('A priced transport option is required')
    trip = Trip(
        id=str(uuid4()), user_id=user_id,
        origin_lat=payload.get('origin_lat') or 30.0444, origin_lng=payload.get('origin_lng') or 31.2357,
        dest_lat=payload.get('dest_lat') or 30.0444, dest_lng=payload.get('dest_lng') or 31.2357,
        status='planned', total_price=option['price'], transport_mix=option['route'], idempotency_key=idempotency_key,
    )
    db.add(trip)
    append_audit(db, actor_id=user_id, action='TRIP_BOOKED', entity_type='Trip', entity_id=trip.id, details={'price': float(option['price']), 'quote_id': str(quote_id) if quote_id else None})
    db.commit()
    db.refresh(trip)
    return {'trip_id': trip.id, 'status': trip.status, 'total_price': float(trip.total_price), 'booked_option': option, 'idempotent_replay': False}


def track_trip(db: Session, user_id: str, trip_id: str) -> dict:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if trip is None:
        return {'trip_id': trip_id, 'found': False}
    return {'trip_id': trip.id, 'found': True, 'status': trip.status, 'total_price': float(trip.total_price), 'transport_mix': trip.transport_mix, 'origin': {'lat': float(trip.origin_lat), 'lng': float(trip.origin_lng)}, 'destination': {'lat': float(trip.dest_lat), 'lng': float(trip.dest_lng)}, 'assigned_driver_id': trip.driver_id, 'assignment_status': trip.assignment_status, 'created_at': trip.created_at.isoformat() if trip.created_at else None}


def trip_history(db: Session, user_id: str) -> dict:
    trips = db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.created_at.desc()).all()
    return {'user_id': user_id, 'items': [{'trip_id': trip.id, 'status': trip.status, 'total_price': float(trip.total_price), 'transport_mix': trip.transport_mix, 'assigned_driver_id': trip.driver_id, 'created_at': trip.created_at.isoformat() if trip.created_at else None} for trip in trips]}
