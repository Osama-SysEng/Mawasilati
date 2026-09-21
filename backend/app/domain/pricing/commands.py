from dataclasses import dataclass

@dataclass(frozen=True)
class CreatePricing:
    actor_id: int
    correlation_id: str
    reason: str | None = None

@dataclass(frozen=True)
class ChangePricingStatus:
    identifier: str
    status: str
    actor_id: int
    reason: str | None = None
