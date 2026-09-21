from app.domain.pricing.contracts import PricingSnapshot
from app.domain.pricing.policies import requires_confirmation
from app.domain.pricing.service import display_label, is_terminal

def test_pricing_contract_and_policy():
    snapshot = PricingSnapshot(identifier="pricing-001", status="OPEN", correlation_id="req-pricing")
    assert display_label(snapshot) == "pricing-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
