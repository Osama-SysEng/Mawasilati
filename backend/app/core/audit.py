"""Append-only operational audit events for sensitive transport actions."""
from uuid import uuid4

from app.models import AuditLog


def append_audit(db, *, actor_id: str | None, action: str, entity_type: str, entity_id: str | None = None, details: dict | None = None, correlation_id: str | None = None) -> None:
    db.add(AuditLog(
        id=str(uuid4()), actor_id=actor_id, action=action, entity_type=entity_type,
        entity_id=entity_id, details=details or {}, correlation_id=correlation_id,
    ))
