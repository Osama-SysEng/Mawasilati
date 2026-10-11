from fastapi import APIRouter, Query

from app.services.route_service import get_route_stops, realtime_routes, search_routes

router = APIRouter()


@router.get('/search')
def search(query: str | None = Query(default=None), transport_type: str | None = Query(default=None), limit: int = Query(default=50, ge=1, le=500), offset: int = Query(default=0, ge=0)) -> dict:
    return search_routes(query=query, transport_type=transport_type, limit=limit, offset=offset)


@router.get('/{route_id}/stops')
def stops(route_id: str) -> dict:
    return get_route_stops(route_id)


@router.get('/realtime')
def realtime() -> dict:
    return realtime_routes()
