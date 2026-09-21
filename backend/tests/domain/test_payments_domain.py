from app.domain.payments.contracts import PaymentSnapshot
from app.domain.payments.policies import requires_confirmation
from app.domain.payments.service import display_label, is_terminal

def test_payments_contract_and_policy():
    snapshot = PaymentSnapshot(identifier="payments-001", status="OPEN", correlation_id="req-payments")
    assert display_label(snapshot) == "payments-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
