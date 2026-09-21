from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.audit import append_audit
from app.core.database import get_db
from app.models import Trip, User

router = APIRouter()


@router.post('/trips/{trip_id}/assign/{driver_id}')
def assign_driver(trip_id: str, driver_id: str, request: Request, current_user: User = Depends(require_roles('admin')), db: Session = Depends(get_db)) -> dict:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    driver = db.query(User).filter(User.id == driver_id, User.role == 'driver', User.is_active.is_(True)).first()
    if not trip or not driver:
        raise HTTPException(status_code=404, detail='Trip or active driver not found')
    if trip.status not in {'planned', 'active'}:
        raise HTTPException(status_code=409, detail='Only planned or active trips can receive a driver assignment')
    if trip.driver_id and trip.driver_id != driver.id:
        raise HTTPException(status_code=409, detail='Trip is already assigned to a different driver')
    trip.driver_id = driver.id
    trip.assignment_status = 'assigned'
    append_audit(db, actor_id=current_user.id, action='DRIVER_ASSIGNED', entity_type='Trip', entity_id=trip.id, details={'driver_id': driver.id}, correlation_id=request.headers.get('X-Request-Id'))
    db.commit()
    return {'trip_id': trip.id, 'driver_id': trip.driver_id, 'assignment_status': trip.assignment_status}
