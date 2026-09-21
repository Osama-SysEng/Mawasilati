from app.domain.journeys.contracts import JourneySnapshot
from app.domain.journeys.policies import requires_confirmation
from app.domain.journeys.service import display_label, is_terminal

def test_journeys_contract_and_policy():
    snapshot = JourneySnapshot(identifier="journeys-001", status="OPEN", correlation_id="req-journeys")
    assert display_label(snapshot) == "journeys-001 · OPEN"
    assert is_terminal("COMPLETED")
    assert requires_confirmation("PAYMENT_CAPTURE")
    assert not requires_confirmation("READ")
