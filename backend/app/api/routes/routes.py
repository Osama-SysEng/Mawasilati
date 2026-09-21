from fastapi import APIRouter, Query

from app.services.route_service import get_route_stops, realtime_routes, search_routes

router = APIRouter()


@router.get('/search')
def search(query: str | None = Query(default=None), transport_type: str | None = Query(default=None)) -> dict:
    return search_routes(query=query, transport_type=transport_type)


@router.get('/{route_id}/stops')
def stops(route_id: str) -> dict:
    return get_route_stops(route_id)


@router.get('/realtime')
def realtime() -> dict:
    return realtime_routes()
