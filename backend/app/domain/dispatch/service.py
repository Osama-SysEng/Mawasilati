from .contracts import DispatchSnapshot

def display_label(snapshot: DispatchSnapshot) -> str:
    return f"{snapshot.identifier} · {snapshot.status}"

def is_terminal(status: str) -> bool:
    return status.upper() in {"CANCELLED", "COMPLETED", "FAILED", "EXPIRED"}
