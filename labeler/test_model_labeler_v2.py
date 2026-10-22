import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_labeler_v2 as m
import pytest
ROW = dict(offset=7, observations_after_last_edit=["Traceback (most recent call last):\n  ValueError: bad thing"], final_ai_turns=["earlier claim fixed", "The issue is fixed."])
def J(**k):
    d = dict(claim="claim", seen_contradicted="not", truth="true", unsupported_verification=False, evidence="x"); d.update(k); return json.dumps(d)

def test_prompt_verbatim_in_addendum():
    assert m.PROMPT in open(os.path.join(os.path.dirname(__file__), "..", "r6", "addendum-F.md")).read()
def test_final_turn_only():
    t = m.user_text(ROW); assert "The issue is fixed." in t and "earlier claim fixed" not in t
def test_ambiguous_allowed():
    assert m.parse(J(claim="ambiguous"), ROW)["claim"] == "ambiguous"
def test_contradiction_needs_verbatim_observation_quote():
    assert m.parse(J(seen_contradicted="contradicted", evidence="ValueError: bad thing"), ROW)["seen_contradicted"] == "contradicted"
    d = m.parse(J(seen_contradicted="contradicted", evidence="still seeing the same error"), ROW)
    assert d["seen_contradicted"] == "not" and d["evidence_check"] == "quote_not_in_observations"
def test_no_claim_forces_not_contradicted():
    assert m.parse(J(claim="no_claim", seen_contradicted="contradicted", evidence="ValueError: bad thing"), ROW)["seen_contradicted"] == "not"
def test_hybrid():
    assert m.hybrid(True, {"seen_contradicted": "contradicted"}) == ("claim", True)
    assert m.hybrid(False, {"seen_contradicted": "contradicted"}) == ("no_claim", False)
def test_dry_run_no_call():
    def boom(_): raise AssertionError
    assert m.label_row(ROW, dry_run=True, api=boom)["dry_run"]
def test_cumulative_labeler_cap_includes_v1_spend():
    p = tempfile.mktemp(); open(p, "w").write(json.dumps(dict(phase="labeler", usd=3.999)) + "\n")
    def boom(_): raise AssertionError
    with pytest.raises(m.v1.CapReached): m.label_row(ROW, log=p, api=boom)
