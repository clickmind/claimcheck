import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_labeler as m
import pytest

def test_prompt_verbatim_from_addendum():
    t = open(os.path.join(os.path.dirname(__file__), "..", "r6", "addendum-E.md")).read()
    assert m.PROMPT in t and m.PROMPT.startswith("You are auditing")

def test_config():
    assert m.MODEL == "grok-4.20" and m.TEMPERATURE == 0 and m.LABELER_CAP == 4.0 and m.TOTAL_CAP == 10.0

def test_cost():
    assert m.cost(100_000, 0) == pytest.approx(0.125)
    assert m.cost(0, 1_000_000) == pytest.approx(2.50)
    assert m.cost(200_000, 0) == pytest.approx(0.50)  # long-context rate
    assert m.cost(1000, 0, cached_tokens=1000) == pytest.approx(0.0002)

def _log(recs):
    p = tempfile.mktemp(); open(p, "w").write("".join(json.dumps(r) + "\n" for r in recs)); return p

def test_labeler_cap():
    p = _log([dict(phase="labeler", usd=3.99)])
    with pytest.raises(m.CapReached): m.check_cap(0.02, "labeler", p)
    m.check_cap(0.005, "labeler", p)

def test_total_cap_shared_with_judge():
    p = _log([dict(phase="judge", usd=9.99), dict(phase="labeler", usd=0.0)])
    with pytest.raises(m.CapReached): m.check_cap(0.02, "labeler", p)
    with pytest.raises(m.CapReached): m.check_cap(0.02, "judge", p)

def test_log_append_only_and_running_total():
    p = _log([dict(phase="judge", usd=1.0)])
    m.log_call(5, {"prompt_tokens": 1000, "completion_tokens": 100}, "labeler", p)
    lines = open(p).read().splitlines(); assert len(lines) == 2
    r = json.loads(lines[1]); assert r["usd"] == pytest.approx(0.0015) and r["running_total_usd"] == pytest.approx(1.0015)

def test_parse():
    good = '{"claim":"claim","seen_contradicted":"not","truth":"unverifiable","unsupported_verification":true,"evidence":"x"}'
    assert m.parse("noise " + good)["claim"] == "claim"
    assert m.parse("not json") is None
    assert m.parse(good.replace('"claim":"claim"', '"claim":"maybe"')) is None

ROW = dict(offset=1, observations_after_last_edit=["ok"], final_ai_turns=["a", "fixed"])

def test_dry_run_makes_no_call():
    def boom(_): raise AssertionError("API called")
    r = m.label_row(ROW, dry_run=True, api=boom); assert r["dry_run"] and r["est_max_usd"] > 0

def test_retry_once_then_parse_failure_and_costs_logged():
    p = _log([]); calls = []
    def fake(_): calls.append(1); return "garbage", {"prompt_tokens": 10, "completion_tokens": 5}
    r = m.label_row(ROW, log=p, api=fake)
    assert r["parse_failure"] and len(calls) == 2 and len(open(p).read().splitlines()) == 2

def test_cap_blocks_before_call():
    p = _log([dict(phase="labeler", usd=4.0)])
    def boom(_): raise AssertionError("API called")
    with pytest.raises(m.CapReached): m.label_row(ROW, log=p, api=boom)

def test_estimate_uses_actual_tokens_with_margin():
    m._RATIO["max_tokens_per_byte"] = None
    t = "x" * 3000
    assert m.est_prompt_tokens(t) == 1001
    m.observe(t, 3000)  # actual 1 token/byte, worse than chars/3
    assert m.est_prompt_tokens(t) == 4501  # 3000 * 1.0 * 1.5 + 1
    m.observe(t, 10)  # lower ratio never lowers the estimate
    assert m.est_prompt_tokens(t) == 4501
    m._RATIO["max_tokens_per_byte"] = None
