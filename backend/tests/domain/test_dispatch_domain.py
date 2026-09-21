from app.domain.dispatch.contracts import DispatchSnapshot
from app.domain.dispatch.policies import requires_confirmation
from app.domain.dispatch.service import display_label, is_terminal

def test_dispatch_contract_and_policy():
    snapshot = DispatchSnapshot(identifier="dispatch-001", status="OPEN", correlation_id="req-dispatch")
    assert display_label(snapshot) == "dispatch-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
