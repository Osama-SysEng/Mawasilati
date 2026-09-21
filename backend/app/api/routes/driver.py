from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Trip, User
from app.schemas import DriverLocationRequest
from app.services.driver_service import heatmap, nearby_requests, update_location

router = APIRouter()


@router.get('/heatmap')
def get_heatmap(radius_km: float = Query(default=5.0)) -> dict:
    return heatmap(radius_km)


@router.post('/location')
async def location(
    payload: DriverLocationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if current_user.role != 'driver':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only drivers can report a location')
    if payload.trip_id:
        assigned = db.query(Trip).filter(Trip.id == str(payload.trip_id), Trip.driver_id == current_user.id, Trip.assignment_status == 'assigned').first()
        if not assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Driver is not assigned to this trip')
    # driver_id always comes from the authenticated user, never the request
    # body, so one driver cannot spoof another driver's location.
    return await update_location(
        db,
        current_user.id,
        payload.latitude,
        payload.longitude,
        trip_id=str(payload.trip_id) if payload.trip_id else None,
    )


@router.get('/requests')
def requests(driver_id: str | None = Query(default=None), limit: int = Query(default=10, ge=1, le=50)) -> dict:
    return nearby_requests(driver_id=driver_id, limit=limit)
