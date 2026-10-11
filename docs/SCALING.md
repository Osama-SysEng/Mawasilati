# Scaling — Mawasilati backend

## Workers
- `backend/Dockerfile` runs uvicorn with `--workers 2`. Scale horizontally
  (compose `--scale api=N` / k8s replicas) behind a load balancer; the app is
  stateless except the DB. For CPU-bound AI parsing, raise to
  `--workers $((2*CPU+1))` via `UVICORN_WORKERS` if the image is rebuilt with
  an env override.

## Rate limiting
- In-memory per-IP sliding window in `app/main.py::operational_controls`:
  **300 req/min**, health/readiness exempt, 429 on excess.
- Single-process memory only: with `--workers 2` each worker enforces its own
  budget (~600/min total). For strict global limits put Redis (or gateway)
  in front. Tune via code constants; no env knob yet.

## Pagination (default 50 / max 500)
- `GET /api/v1/trip/history?limit=&offset=`
- `GET /api/v1/payment/history?limit=&offset=`
- `GET /api/v1/routes/search?limit=&offset=`
- `GET /api/v1/driver/requests` already capped (`le=50`).
- Responses add `total/limit/offset` alongside `items`; old clients reading
  only `items` are unaffected.

## Remaining capacity limits (honest)
- SQLite default dev DB; production needs Postgres + pool settings in
  `app/core/config.py` (`database_pool_size=20`, overflow 20).
- Rate limiter is per-worker memory: bursty multi-worker traffic can exceed
  the nominal 300/min; use Redis for exactness.
- `trip_history`/`payment_history` use `COUNT()+OFFSET` — fine to ~10⁵ rows,
  degrades after; switch to keyset pagination for large fleets.
- No response caching; realtime WS fan-out is single-process.
