from fastapi import APIRouter

from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.driver import router as driver_router
from app.api.routes.dispatch import router as dispatch_router
from app.api.routes.operations import router as operations_router
from app.api.routes.payment import router as payment_router
from app.api.routes.routes import router as routes_router
from app.api.routes.trip import router as trip_router
from app.api.routes.ws import router as ws_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
api_router.include_router(trip_router, prefix='/trip', tags=['trip'])
api_router.include_router(routes_router, prefix='/routes', tags=['routes'])
api_router.include_router(payment_router, prefix='/payment', tags=['payment'])
api_router.include_router(ai_router, prefix='/ai', tags=['ai'])
api_router.include_router(driver_router, prefix='/driver', tags=['driver'])
api_router.include_router(dispatch_router, prefix='/dispatch', tags=['dispatch'])
api_router.include_router(operations_router, prefix='/operations', tags=['operations'])

# WebSocket routes live outside the versioned REST prefix in main.py so the
# client connects to ws(s)://host/ws/trip/{trip_id} directly.
ws_api_router = ws_router
