CONFIRMATION_ACTIONS = {"PAYMENT_CAPTURE", "DRIVER_ASSIGNMENT", "EMERGENCY_ESCALATION", "FARE_ADJUSTMENT"}

def requires_confirmation(action: str, risk: str = "LOW") -> bool:
    return action.upper() in CONFIRMATION_ACTIONS or risk.upper() in {"HIGH", "CRITICAL"}

def may_share_location(consent: bool, role: str) -> bool:
    return consent and role in {"driver", "passenger", "dispatcher"}
