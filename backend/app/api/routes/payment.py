from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import PaymentRequest
from app.services.payment_service import confirm_payment, initiate_payment, payment_history

router = APIRouter()


class ConfirmPaymentRequest(BaseModel):
    payment_id: str


@router.post('/initiate')
def initiate(
    payload: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return initiate_payment(db, current_user.id, payload.model_dump(mode='json'))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post('/confirm')
def confirm(
    payload: ConfirmPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return confirm_payment(db, current_user.id, payload.payment_id)


@router.get('/history')
def history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return payment_history(db, current_user.id)
