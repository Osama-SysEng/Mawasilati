from app.domain.bookings.contracts import BookingSnapshot
from app.domain.bookings.policies import requires_confirmation
from app.domain.bookings.service import display_label, is_terminal

def test_bookings_contract_and_policy():
    snapshot = BookingSnapshot(identifier="bookings-001", status="OPEN", correlation_id="req-bookings")
    assert display_label(snapshot) == "bookings-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
