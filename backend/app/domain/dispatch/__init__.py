"""Dispatch bounded context: driver assignment and capacity coordination."""
from .contracts import DispatchSnapshot
from .policies import requires_confirmation

__all__ = ["DispatchSnapshot", "requires_confirmation"]
