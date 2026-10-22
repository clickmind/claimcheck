"""Model labeler per r6/addendum-E.md (E1-E3). grok-4.20, temperature 0, verbatim E2 prompt, JSON output.
Append-only per-call cost log: r6/spend/labeler-judge-spend.jsonl. Hard stops: labeler phase cumulative $4.00; overall $10.00 (shared with judge).
Price: xAI list price for grok-4.20-0309 (reasoning / non-reasoning / multi-agent identical), https://docs.x.ai/docs/models (fetched 2026-10-22):
  < 200k prompt tokens: $1.25 / 1M input, $0.20 / 1M cached input, $2.50 / 1M output; >= 200k: $2.50 / $0.40 / $5.00 (all tokens in request).
Usage: python labeler/model_labeler.py --blind labeler/seed3_blind.jsonl --out OUT.jsonl [--dry-run]
Key is read from XAI_API_KEY and never printed."""
import argparse, json, os, re, time, urllib.request
MODEL = "grok-4.20"; TEMPERATURE = 0; MAX_TOKENS = 400
API_URL = "https://api.x.ai/v1/chat/completions"
PRICE_URL = "https://docs.x.ai/docs/models"
PRICE = {"short": (1.25, 0.20, 2.50), "long": (2.50, 0.40, 5.00)}  # $/1M: input, cached input, output
LONG_CTX = 200_000
LABELER_CAP = 4.00; TOTAL_CAP = 10.00
SPEND_LOG = "r6/spend/labeler-judge-spend.jsonl"
PROMPT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_labeler_prompt.txt")).read()
VALID = {"claim": {"claim", "no_claim"}, "seen_contradicted": {"contradicted", "not", "ambiguous"},
         "truth": {"true", "false", "unverifiable", "n/a"}}

class CapReached(Exception): pass

def cost(prompt_tokens, completion_tokens, cached_tokens=0):
    i, c, o = PRICE["long" if prompt_tokens >= LONG_CTX else "short"]
    return ((prompt_tokens - cached_tokens) * i + cached_tokens * c + completion_tokens * o) / 1e6

def est_prompt_tokens(text): return len(text) // 3 + 1  # conservative (over-estimates vs ~4 chars/token)

def max_call_cost(user_text): return cost(est_prompt_tokens(PROMPT + user_text), MAX_TOKENS)

def totals(log=SPEND_LOG):
    lab = tot = 0.0
    if os.path.exists(log):
        for l in open(log):
            if l.strip():
                r = json.loads(l); tot += r["usd"]
                if r["phase"] == "labeler": lab += r["usd"]
    return lab, tot

def check_cap(next_max, phase="labeler", log=SPEND_LOG):
    lab, tot = totals(log)
    if tot + next_max > TOTAL_CAP: raise CapReached(f"total {tot:.4f}+{next_max:.4f} > ${TOTAL_CAP}")
    if phase == "labeler" and lab + next_max > LABELER_CAP: raise CapReached(f"labeler {lab:.4f}+{next_max:.4f} > ${LABELER_CAP}")

def log_call(row_id, usage, phase="labeler", log=SPEND_LOG, model=MODEL):
    pt, ct = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
    usd = cost(pt, ct, cached); _, tot = totals(log)
    rec = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S%z"), phase=phase, row_id=row_id, model=model, input_tokens=pt,
               output_tokens=ct, cached_tokens=cached, usd=round(usd, 6), running_total_usd=round(tot + usd, 6))
    with open(log, "a") as f: f.write(json.dumps(rec) + "\n")  # append-only
    return rec

def user_text(row):
    obs = "\n---\n".join(row.get("observations_after_last_edit") or [])
    ai = row.get("final_ai_turns") or []
    prior = "\n---\n".join(ai[:-1]); final = ai[-1] if ai else ""
    return f"ACTIONS/OBSERVATIONS AFTER LAST EDIT:\n{obs}\n\nEARLIER AI TURNS:\n{prior}\n\nFINAL MESSAGE:\n{final}"

def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m: return None
    try: d = json.loads(m.group(0))
    except Exception: return None
    if any(d.get(k) not in v for k, v in VALID.items()) or not isinstance(d.get("unsupported_verification"), bool): return None
    return d

def call_api(text):
    key = os.environ.get("XAI_API_KEY")
    if not key: raise SystemExit("XAI_API_KEY not set")
    body = json.dumps(dict(model=MODEL, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
                           messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": text}])).encode()
    req = urllib.request.Request(API_URL, body, {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    return r["choices"][0]["message"]["content"], r.get("usage", {})

def label_row(row, dry_run=False, log=SPEND_LOG, api=call_api):
    text = user_text(row); rid = row.get("offset")
    if dry_run: return dict(offset=rid, dry_run=True, est_max_usd=round(max_call_cost(text), 6))
    for attempt in range(2):  # E1: one retry on transport error / malformed JSON, cost counted
        check_cap(max_call_cost(text), "labeler", log)
        try: content, usage = api(text)
        except Exception as e:
            if attempt: return dict(offset=rid, error=type(e).__name__, label=None)
            continue
        log_call(rid, usage, "labeler", log)
        d = parse(content)
        if d is not None: return dict(offset=rid, label=d)
    return dict(offset=rid, label=None, parse_failure=True)  # scored as no_claim (E1)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--blind", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.blind) if l.strip()]
    with open(a.out, "a") as f:
        for r in rows:
            try: res = label_row(r, a.dry_run)
            except CapReached as e: print(json.dumps(dict(stopped="cap", reason=str(e)))); break
            f.write(json.dumps(res) + "\n")
    if a.dry_run: print(json.dumps(dict(dry_run=True, rows=len(rows), est_max_total_usd=round(sum(max_call_cost(user_text(r)) for r in rows), 4))))
