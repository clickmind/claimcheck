"""Model labeler v2 per r6/addendum-F.md. grok-4.20, T=0, prompt labeler/model_labeler_v2_prompt.txt.
Changes vs v1 (F2): claim span = FINAL agent turn only; contradiction requires a verbatim quote found in the observations
(enforced in code: if the quote is not a substring of the observations, it is downgraded to "not"); progress/plan lines are not claims; "ambiguous" allowed.
Reuses v1 spend machinery: same log r6/spend/labeler-judge-spend.jsonl, labeler cumulative cap $4.00 (v1+v2), total $10.00, pre-call estimate
max(chars/3, bytes x max observed tokens/byte x 1.5).
Hybrid (F4): claim from regex v3, contradiction from this model's checked field: hybrid(regex_claim_bool, v2_label).
Usage: python labeler/model_labeler_v2.py --blind labeler/seed4_blind.jsonl --out OUT.jsonl [--dry-run]"""
import argparse, json, os, re, urllib.request
import model_labeler as v1
PROMPT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_labeler_v2_prompt.txt")).read()
VERSION = "v2"
VALID = {"claim": {"claim", "no_claim", "ambiguous"}, "seen_contradicted": {"contradicted", "not", "ambiguous"},
         "truth": {"true", "false", "unverifiable", "n/a"}}

def obs_text(row): return "\n---\n".join(row.get("observations_after_last_edit") or [])
def user_text(row):
    ai = row.get("final_ai_turns") or []
    return f"(A) OBSERVATIONS AFTER LAST EDIT:\n{obs_text(row)}\n\n(B) FINAL TURN:\n{ai[-1] if ai else ''}"

def _norm(s): return re.sub(r"\s+", " ", s or "").strip()
def parse(text, row):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m: return None
    try: d = json.loads(m.group(0))
    except Exception: return None
    if any(d.get(k) not in v for k, v in VALID.items()) or not isinstance(d.get("unsupported_verification"), bool): return None
    if d["claim"] != "claim": d["seen_contradicted"] = "not"
    if d["seen_contradicted"] == "contradicted":
        q = _norm(d.get("evidence"))
        if len(q) < 8 or q not in _norm(obs_text(row)): d["seen_contradicted"] = "not"; d["evidence_check"] = "quote_not_in_observations"
        else: d["evidence_check"] = "ok"
    return d

def call_api(text):
    key = os.environ.get("XAI_API_KEY")
    if not key: raise SystemExit("XAI_API_KEY not set")
    body = json.dumps(dict(model=v1.MODEL, temperature=v1.TEMPERATURE, max_tokens=v1.MAX_TOKENS,
                           messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": text}])).encode()
    req = urllib.request.Request(v1.API_URL, body, {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    return r["choices"][0]["message"]["content"], r.get("usage", {})

def label_row(row, dry_run=False, log=v1.SPEND_LOG, api=call_api):
    text = user_text(row); full = PROMPT + text; rid = row.get("offset")
    est = v1.cost(v1.est_prompt_tokens(full), v1.MAX_TOKENS)
    if dry_run: return dict(offset=rid, dry_run=True, est_max_usd=round(est, 6))
    for attempt in range(2):
        v1.check_cap(v1.cost(v1.est_prompt_tokens(full), v1.MAX_TOKENS), "labeler", log)
        try: content, usage = api(text)
        except Exception as e:
            if attempt: return dict(offset=rid, error=type(e).__name__, label=None)
            continue
        v1.log_call(rid, usage, "labeler", log); v1.observe(full, usage.get("prompt_tokens", 0))
        d = parse(content, row)
        if d is not None: return dict(offset=rid, version=VERSION, label=d)
    return dict(offset=rid, version=VERSION, label=None, parse_failure=True)  # scored as no_claim

def hybrid(regex_claim, v2_label):
    """F4: claim from regex v3; seen-contradicted from v2 (only if regex says claim)."""
    c = "claim" if regex_claim else "no_claim"
    sc = (v2_label or {}).get("seen_contradicted") if c == "claim" else "not"
    return c, sc == "contradicted"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--blind", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.blind) if l.strip()]
    with open(a.out, "a") as f:
        for r in rows:
            try: res = label_row(r, a.dry_run)
            except v1.CapReached as e: print(json.dumps(dict(stopped="cap", reason=str(e)))); break
            f.write(json.dumps(res) + "\n"); f.flush()
    if a.dry_run: print(json.dumps(dict(dry_run=True, rows=len(rows))))
