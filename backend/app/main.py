from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router, ws_api_router
from app.core.config import settings
from app.core.metrics import runtime_metrics
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # Convenience for local development only. Production deployments should
    # manage the schema with `alembic upgrade head` instead (see database/README.md).
    if settings.environment == 'development':
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=lifespan)

# client_ip -> [hits_in_window, window_end_monotonic]
_RATE_BUCKETS: dict[str, list] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def operational_controls(request: Request, call_next):
    started = time.perf_counter()
    correlation_id = request.headers.get('X-Request-Id') or uuid.uuid4().hex
    # Lightweight in-memory rate limit: 300 req/min per client IP.
    # Health/readiness probes are exempt so orchestrators never get 429.
    if request.url.path not in ('/health', '/ready', f"{settings.api_v1_prefix}/health"):
        now = time.monotonic()
        client = request.client.host if request.client else 'local'
        bucket = _RATE_BUCKETS.get(client)
        if bucket is None or now >= bucket[1]:
            bucket = [[now], now + 60.0]
            _RATE_BUCKETS[client] = bucket
        else:
            bucket[0].append(now)
        # prune + cap memory
        cutoff = now - 60.0
        bucket[0] = [t for t in bucket[0] if t >= cutoff][-320:]
        if len(_RATE_BUCKETS) > 2000:
            _RATE_BUCKETS.pop(next(iter(_RATE_BUCKETS)))
        if len(bucket[0]) > 300:
            return JSONResponse(status_code=429, content={'detail': 'Rate limit exceeded (300/min)'})
    runtime_metrics.started()
    try:
        response = await call_next(request)
        response.headers['X-Request-Id'] = correlation_id
        route = getattr(request.scope.get('route'), 'path', request.url.path)
        runtime_metrics.record(route, response.status_code, time.perf_counter() - started)
        return response
    except Exception:
        runtime_metrics.record(request.url.path, 500, time.perf_counter() - started)
        raise
    finally:
        runtime_metrics.completed()

app.include_router(api_router, prefix=settings.api_v1_prefix)
# Real-time trip tracking: ws(s)://host/ws/trip/{trip_id}?role=driver|passenger
app.include_router(ws_api_router, prefix='/ws')


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': 'mawasilati-api'}


@app.get(f"{settings.api_v1_prefix}/health")
def api_health() -> dict:
    return {'status': 'ok', 'service': 'mawasilati-api', 'versioned': True}


@app.get('/ready')
def ready() -> dict:
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql('SELECT 1')
        return {'status': 'ready', 'database': 'ok'}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={'status': 'not_ready', 'database': 'error'}) from exc
