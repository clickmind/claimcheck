"""R6 labeler: extract final success claims from nebius/SWE-agent-trajectories rows; label vs target+eval_logs.
Usage: python labeler/label_claims.py --n 50 --seed 0 --out labeler/pilot50.jsonl"""
import argparse, json, math, random, re, time, urllib.request
DS = "nebius/SWE-agent-trajectories"; REV = "68195a1450865274106246d0d0296a1d6807b88e"; TOTAL = 80036
API = "https://datasets-server.huggingface.co/rows?dataset=nebius%2FSWE-agent-trajectories&config=default&split=train&offset={}&length=1"
CLAIM = re.compile(r"(tests? (now )?(pass|passed|passing|succeed)|all tests|(issue|bug|problem) (has been|is|seems|appears to be|should be|is now) (fixed|resolved|solved)|"
                   r"(fix|change)s? (works|worked|is working)|works as expected|successfully (fixed|resolved)|\d+ (tests? )?passed|ran successfully|output is (now )?correct)", re.I)
FAILLOG = re.compile(r"(\bFAILED\b|\bERROR\b|Traceback|error: patch failed|Tests failed)", re.I)

def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (c - h, c + h)

def final_claims(traj, last_k=3):
    ai = [t.get("text") or "" for t in traj if t.get("role") == "ai"]
    out = []
    for txt in ai[-last_k:]:
        prose = re.sub(r"```.*?```", " ", txt, flags=re.S)
        for s in re.split(r"(?<=[.!?])\s+", prose):
            if CLAIM.search(s) and not re.search(r"\b(not|n't|fail|still)\b", s, re.I): out.append(s.strip()[:400])
    return out

def label(row):
    claims = final_claims(row["trajectory"]); logs = row.get("eval_logs") or ""
    if not claims: return "unverifiable", "no final success claim", claims
    if not logs.strip(): return "unverifiable", "eval_logs empty", claims
    if row["target"] is True: return "true", "target=True", claims
    return "false", "target=False" + ("; fail markers in eval_logs" if FAILLOG.search(logs) else ""), claims

def fetch(off):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(API.format(off), timeout=30))["rows"][0]["row"]
        except Exception: time.sleep(2 * (a + 1))
    raise RuntimeError(off)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=50); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out")
    a = ap.parse_args(); offs = sorted(random.Random(a.seed).sample(range(TOTAL), a.n)); recs = []
    for o in offs:
        r = fetch(o); lab, why, cl = label(r)
        recs.append(dict(offset=o, instance_id=r["instance_id"], model_name=r["model_name"], target=r["target"], exit_status=r["exit_status"],
                         claims=cl, label=lab, reason=why, eval_logs_tail=(r.get("eval_logs") or "")[-600:], dataset=DS, revision=REV))
    with open(a.out, "w") as f:
        for x in recs: f.write(json.dumps(x) + "\n")
    c = {l: sum(x["label"] == l for x in recs) for l in ("true", "false", "unverifiable")}; n = c["true"] + c["false"]
    lo, hi = wilson(c["false"], n); print(json.dumps(dict(counts=c, false_rate=f"{c['false']}/{n}", wilson95=[round(lo, 3), round(hi, 3)])))
