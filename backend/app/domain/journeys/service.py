from .contracts import JourneySnapshot

def display_label(snapshot: JourneySnapshot) -> str:
    return f"{snapshot.identifier} · {snapshot.status}"

def is_terminal(status: str) -> bool:
    return status.upper() in {"CANCELLED", "COMPLETED", "FAILED", "EXPIRED"}
