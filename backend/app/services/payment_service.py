from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.models import Payment, Trip


def initiate_payment(db: Session, user_id: str, payload: dict) -> dict:
    trip = db.query(Trip).filter(Trip.id == str(payload.get('trip_id')), Trip.user_id == user_id).first()
    if trip is None:
        raise ValueError('Trip not found for current passenger')
    amount = float(payload.get('amount', 0))
    if abs(amount - float(trip.total_price)) > 0.01:
        raise ValueError('Payment amount must equal the booked trip price')
    idempotency_key = payload.get('idempotency_key')
    if idempotency_key:
        existing = db.query(Payment).filter(Payment.user_id == user_id, Payment.idempotency_key == idempotency_key).first()
        if existing:
            return {'payment_id': existing.id, 'status': existing.status, 'method': existing.method, 'amount': float(existing.amount), 'trip_id': existing.trip_id, 'idempotent_replay': True}
    payment = Payment(id=str(uuid4()), user_id=user_id, trip_id=trip.id, method=payload.get('method'), amount=amount, status='pending', idempotency_key=idempotency_key)
    db.add(payment)
    append_audit(db, actor_id=user_id, action='PAYMENT_INITIATED', entity_type='Payment', entity_id=payment.id, details={'trip_id': payment.trip_id, 'amount': amount})
    db.commit()
    db.refresh(payment)
    return {'payment_id': payment.id, 'status': payment.status, 'method': payment.method, 'amount': float(payment.amount), 'trip_id': payment.trip_id, 'idempotent_replay': False}


def confirm_payment(db: Session, user_id: str, payment_id: str) -> dict:
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if payment is None:
        return {'payment_id': payment_id, 'status': 'not_found'}
    if payment.status == 'confirmed':
        return {'payment_id': payment.id, 'status': payment.status, 'qr_ticket': payment.gateway_reference, 'trip_id': payment.trip_id, 'idempotent_replay': True}
    payment.status = 'confirmed'
    payment.gateway_reference = f'LOCAL-{uuid4().hex[:16].upper()}'
    append_audit(db, actor_id=user_id, action='PAYMENT_CONFIRMED', entity_type='Payment', entity_id=payment.id, details={'trip_id': payment.trip_id})
    db.commit()
    db.refresh(payment)
    return {'payment_id': payment.id, 'status': payment.status, 'qr_ticket': payment.gateway_reference, 'trip_id': payment.trip_id, 'idempotent_replay': False}


def payment_history(db: Session, user_id: str) -> dict:
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).all()
    return {'user_id': user_id, 'items': [{'payment_id': payment.id, 'trip_id': payment.trip_id, 'method': payment.method, 'amount': float(payment.amount), 'status': payment.status, 'created_at': payment.created_at.isoformat() if payment.created_at else None} for payment in payments]}
