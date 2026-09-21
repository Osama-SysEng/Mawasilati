from app.domain.tracking.contracts import TrackingSnapshot
from app.domain.tracking.policies import requires_confirmation
from app.domain.tracking.service import display_label, is_terminal

def test_tracking_contract_and_policy():
    snapshot = TrackingSnapshot(identifier="tracking-001", status="OPEN", correlation_id="req-tracking")
    assert display_label(snapshot) == "tracking-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
