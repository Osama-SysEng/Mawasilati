from dataclasses import dataclass

@dataclass(frozen=True)
class CreateDispatch:
    actor_id: int
    correlation_id: str
    reason: str | None = None

@dataclass(frozen=True)
class ChangeDispatchStatus:
    identifier: str
    status: str
    actor_id: int
    reason: str | None = None
