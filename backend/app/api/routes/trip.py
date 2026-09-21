from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import TripBookRequest, TripPlanRequest
from app.services.ai_service import parse_trip_text
from app.services.trip_service import book_trip, build_trip_options, issue_trip_quote, track_trip, trip_history

router = APIRouter()


@router.post('/plan')
def plan_trip(payload: TripPlanRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    parsed_intent = parse_trip_text(' '.join(filter(None, [payload.origin_label or '', payload.destination_label or '', str(payload.budget or '')])))
    result = issue_trip_quote(db, current_user.id, payload.model_dump())
    result['parsed_intent'] = parsed_intent
    return result


@router.get('/options')
def trip_options(origin_lat: float | None = Query(default=None), origin_lng: float | None = Query(default=None), dest_lat: float | None = Query(default=None), dest_lng: float | None = Query(default=None), budget: float | None = Query(default=None)) -> dict:
    return build_trip_options({'origin_lat': origin_lat, 'origin_lng': origin_lng, 'dest_lat': dest_lat, 'dest_lng': dest_lng, 'budget': budget})


@router.post('/book')
def book(payload: TripBookRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    try:
        return book_trip(db, current_user.id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get('/track/{trip_id}')
def track(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return track_trip(db, current_user.id, trip_id)


@router.get('/history')
def history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return trip_history(db, current_user.id)
