# Mawasilati Operational Hardening Runbook

This release ties access tokens to revocable server-side sessions, rotates refresh tokens, and records privileged authentication, booking, dispatch, and payment actions in an audit table. A trip plan now produces a short-lived quote that stores the candidate options server-side. In production, booking must consume a valid quote; prices and routes must not be accepted as authoritative client input.

| Control | Implementation | Production action |
|---|---|---|
| Authentication | Access token plus refresh token bound to `auth_sessions` | Inject a strong `SECRET_KEY`, enable session-bound tokens, and expire/revoke sessions through support controls. |
| Booking | Quote consumption plus idempotency key | Pass an idempotency key for every app retry; retain quotes only for their configured TTL. |
| Dispatch | Admin-only driver assignment; driver location restricted to assigned trip | Integrate assignment with a verified dispatch workflow; do not grant the admin role to vehicle devices. |
| Payments | Trip ownership and price validation plus idempotent payment creation | Replace local confirmation with a verified gateway webhook and a separate gateway credential. |
| Database | Alembic revision `0002_operational_hardening` | Back up, run the migration from an immutable job, verify indexes, and retain rollback evidence. |
| Load checks | `tools/load_probe.py` denies remote targets by default | Run only against an approved staging window with a dedicated account and rate limits. |

> The included probe measures response latency; it does not establish a capacity guarantee. Raise concurrency gradually in staging and observe API error rates, PostgreSQL pool saturation, Redis connectivity, queue depth, WebSocket fan-out, and mobile-client reconnect behavior.
