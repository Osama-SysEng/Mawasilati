from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import DriverLocation, Trip


async def update_location(
    db: Session,
    driver_id: str,
    latitude: float,
    longitude: float,
    trip_id: str | None = None,
) -> dict:
    location = DriverLocation(
        id=str(uuid4()),
        driver_id=driver_id,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(location)
    db.commit()
    db.refresh(location)

    if trip_id:
        # Only relay to the trip's live-tracking room if the trip actually
        # exists; avoids broadcasting into rooms for bogus trip ids.
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if trip is not None:
            from app.api.routes.ws import manager  # local import avoids a circular import at module load

            await manager.broadcast_from_server(
                trip_id,
                {'type': 'location', 'latitude': latitude, 'longitude': longitude},
            )

    return {
        'id': location.id,
        'driver_id': location.driver_id,
        'latitude': float(location.latitude),
        'longitude': float(location.longitude),
        'updated': True,
    }


def heatmap(radius_km: float = 5.0) -> dict:
    return {
        'radius_km': radius_km,
        'cells': [
            {'latitude': 30.0444, 'longitude': 31.2357, 'demand_level': 'high', 'color': 'red'},
            {'latitude': 30.0626, 'longitude': 31.2497, 'demand_level': 'medium', 'color': 'yellow'},
            {'latitude': 29.9865, 'longitude': 31.2118, 'demand_level': 'low', 'color': 'green'},
        ],
    }


def nearby_requests(driver_id: str | None = None, limit: int = 10) -> dict:
    return {
        'driver_id': driver_id,
        'items': [
            {
                'request_id': str(uuid4()),
                'pickup': 'التحرير',
                'dropoff': 'المهندسين',
                'priority': 'high',
            }
            for _ in range(min(limit, 3))
        ],
    }
