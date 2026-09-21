from .contracts import TrackingSnapshot

def display_label(snapshot: TrackingSnapshot) -> str:
    return f"{snapshot.identifier} · {snapshot.status}"

def is_terminal(status: str) -> bool:
    return status.upper() in {"CANCELLED", "COMPLETED", "FAILED", "EXPIRED"}
