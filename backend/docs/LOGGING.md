# Structured Logging (Mawasilati API)

Stdlib-only JSON logging via `app/core/logging_utils.py` (no new dependencies).

## One line per request

`operational_controls` in `app/main.py` echoes/propagates `X-Request-ID` and emits a
single access line per request (including 429 rejections and 500s):

```json
{"timestamp": "...", "level": "info", "service": "mawasilati-api",
 "env": "development", "version": "dev", "request_id": "…",
 "event": "http.access", "message": "http.access: GET /health -> 200 in 0.8ms",
 "http.method": "GET", "http.path": "/health",
 "http.status_code": 200, "duration_ms": 0.8}
```

## Env (.env.example)

| Var | Purpose | Default |
| --- | ------- | ------- |
| `SERVICE_NAME` | `service` field | `mawasilati-api` |
| `LOG_LEVEL` | min level | `INFO` (`debug` outside production) |
| `GIT_SHA` | `version` field | `dev` |
| `ENVIRONMENT` | `env` field | `development` |

## Rules

- Never log secrets — keys containing `password/token/secret/api_key/authorization/cookie/...` are redacted as `***`.
- No `print()` in runtime code (`app/`); use `get_logger(__name__)` + `log_access(...)`.
- Correlate with `X-Request-ID`.
