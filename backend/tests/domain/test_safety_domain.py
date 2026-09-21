from app.domain.safety.contracts import SafetySnapshot
from app.domain.safety.policies import requires_confirmation
from app.domain.safety.service import display_label, is_terminal

def test_safety_contract_and_policy():
    snapshot = SafetySnapshot(identifier="safety-001", status="OPEN", correlation_id="req-safety")
    assert display_label(snapshot) == "safety-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
