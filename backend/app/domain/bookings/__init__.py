"""Booking bounded context: reservation lifecycle and passenger ownership."""
from .contracts import BookingSnapshot
from .policies import requires_confirmation

__all__ = ["BookingSnapshot", "requires_confirmation"]
