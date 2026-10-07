# Mawasilati

Mawasilati is a multimodal transport platform for Egypt with:
- FastAPI backend with real JWT authentication and PostgreSQL persistence
- PostgreSQL schema managed with Alembic migrations
- Flutter mobile app with state management, secure token storage, live location, and real-time trip tracking
- AI trip parsing and planning foundation
- Driver heatmap and real-time location tracking over WebSocket

## What is included

- Authentication: register/login with hashed passwords (bcrypt) and real JWT access tokens
- Trip planning, booking, tracking, and history — all persisted to PostgreSQL
- Route search and realtime data endpoints
- Payment initiate/confirm/history flow — persisted to PostgreSQL (gateway integration still mocked, see Notes)
- AI chat and trip parsing endpoints, with conversations saved to the database
- Driver location updates (persisted) and a `/ws/trip/{trip_id}` WebSocket for live tracking
- Docker Compose for local Postgres/Redis
- Alembic migrations + pytest test suite (SQLite in-memory) wired into CI

## Quick start

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # then edit values
uvicorn app.main:app --reload
```

In development (`ENVIRONMENT=development`, the default), tables are created
automatically on startup. For anything beyond local hacking, use Alembic
instead — see `database/README.md`.

Run the test suite:
```bash
cd backend
python -m pytest
```

### Frontend
```bash
cd frontend
flutter pub get
flutter run
```

Set the API/WebSocket base URLs for your environment in
`lib/core/constants/app_constants.dart` (defaults point at
`http://localhost:8000`).

### Local infrastructure
```bash
docker compose up -d postgres redis
```

## Environment variables
Copy `.env.example` to `.env` and fill in:
- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, `ENVIRONMENT`
- `GOOGLE_MAPS_API_KEY` — needed if you wire up `google_maps_flutter` in the app
- `WAZE_API_KEY`, `INSTAPAY_API_KEY`, `VISA_API_KEY` — real payment/traffic integrations (currently mocked)
- `FIREBASE_PROJECT_ID` — needed for push notifications (not wired up yet)
- `DIFY_API_KEY`, `GEMINI_API_KEY` — needed to replace the regex-based AI parser with a real LLM

## Real-time trip tracking

Connect to `ws(s)://<host>/ws/trip/{trip_id}?role=driver|passenger&token=<jwt>`,
using the same access token returned by `/auth/login` / `/auth/register`. The
handshake is rejected (close code 4401) unless the token is valid and:
- `role=passenger` — the token's user must own the trip (`trips.user_id`)
- `role=driver` — the token's user must have `role=driver` (there is no
  driver-trip assignment model yet, so any driver may currently join any
  trip's room — tighten this once dispatching is implemented)

A driver can push its location two ways, both end up broadcast to the same
room as `{"type": "location", "latitude": .., "longitude": ..}`:
1. Send `{"latitude": .., "longitude": ..}` directly over its own WebSocket
   connection (`role=driver`), or
2. `POST /driver/location` with an optional `trip_id` — the REST endpoint
   persists the location and relays it into that trip's WebSocket room
   server-side.

This is an in-memory connection manager suitable for a single backend
instance; back it with Redis pub/sub before scaling to multiple instances.

## Notes / what's still mocked

This scaffold is now backed by real auth and a real database, but a few
pieces are intentionally left as clearly-isolated mocks until you provide
credentials for the underlying third-party services:
- Payment gateways (Instapay/Visa) — `payment_service.py` records real
  payment rows but does not call out to a live gateway.
- AI parsing — regex-based Arabic parsing in `ai_service.py`, not yet backed
  by Gemini/Dify.
- Push notifications — Firebase project ID is in `.env.example` but no
  Firebase Cloud Messaging wiring exists yet.
- Maps — no `google_maps_flutter` widget yet; add your `GOOGLE_MAPS_API_KEY`
  and the native Android/iOS setup before wiring the map screens.

## What's New (Oct 2026)
- Live PostgreSQL via Alembic (10 tables) + `.env.example` + `SECURITY.md`
- 17 tests collected, 0 errors
- Interactive 3D showcase: open `web-3d/index.html` (Three.js, animated, mouse-reactive)
