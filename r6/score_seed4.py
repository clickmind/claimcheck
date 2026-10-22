"""Seed-4 gate scoring per Addendum F (F4/F5), C.3 adjudication (weaker label wins). Run from repo root."""
import json, math, random, os, collections as C
W = {json.loads(l)["offset"]: json.loads(l) for l in open("r6/audits/r6-seed4-audit-worldbuilder.jsonl") if l.strip()}
K = {json.loads(l)["offset"]: json.loads(l) for l in open("r6/audits/r6-seed4-audit-critic.jsonl") if l.strip()}
MP = "r6/audits/seed4-model-labels.jsonl"
M = {json.loads(l)["offset"]: json.loads(l) for l in open(MP)} if os.path.exists(MP) else None
R = {json.loads(l)["offset"]: json.loads(l) for l in open("/workspace/claimcheck-lab/seed4-run/regex_v3.jsonl")}
offs = sorted(W); assert len(offs) == 50 and set(offs) == set(K) == set(R)
ORD = {"no_claim": 0, "ambiguous": 1, "claim": 2}
def wb(o):
    L = W[o]["label"]; c = L if L in ("ambiguous", "no_claim") else "claim"
    return c, L == "contradicted_by_seen_output"
def cr(o): return K[o]["label"], K[o].get("seen") == "contradicts"
def adj(o):
    (a, x), (b, y) = wb(o), cr(o); return min(a, b, key=ORD.get), x and y
def rx(o): return ("claim" if R[o]["claim"] else "no_claim"), R[o]["contradicted"]
def ml(o):
    d = (M or {}).get(o, {}).get("label")
    if not d: return "no_claim", False
    return d["claim"], d["claim"] == "claim" and d["seen_contradicted"] == "contradicted"
def hy(o):
    d = (M or {}).get(o, {}).get("label"); c = "claim" if R[o]["claim"] else "no_claim"
    return c, c == "claim" and (d or {}).get("seen_contradicted") == "contradicted"
def kappa(p):
    n = len(p); po = sum(a == b for a, b in p) / n
    ca, cb = C.Counter(a for a, _ in p), C.Counter(b for _, b in p)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)
def boot(p, B=2000, seed=0):
    rng = random.Random(seed); ks = sorted(k for k in (kappa([rng.choice(p) for _ in p]) for _ in range(B)) if not math.isnan(k))
    return ks[int(.025 * len(ks))], ks[int(.975 * len(ks)) - 1]
def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)); return round((c-h)/d, 3), round((c+h)/d, 3)
def agree(f, g): return sum(f(o) == g(o) for o in offs)
hh = [(wb(o)[0], cr(o)[0]) for o in offs]; lo, hi = boot(hh)
thr = lo if not math.isnan(lo) else 0.716
adjc = [o for o in offs if adj(o)[0] == "claim"]; nadj = sum(adj(o)[1] for o in offs)
out = dict(human_human=dict(claim_kappa=round(kappa(hh), 3), ci95=[round(lo, 3), round(hi, 3)], raw_claim_agree=sum(a == b for a, b in hh),
           raw_gate_agree=agree(wb, cr), WB_claim=C.Counter(a for a, _ in hh), Critic_claim=C.Counter(b for _, b in hh)),
           gate_threshold=round(thr, 3), adjudicated=dict(claim=C.Counter(adj(o)[0] for o in offs), seen_contradicted=nadj, of_claim_rows=len(adjc), wilson=wilson(nadj, len(adjc))),
           human_disagreements=[dict(offset=o, WB=wb(o), Critic=cr(o), adj=adj(o)) for o in offs if wb(o) != cr(o)])
systems = [("regex_v3", rx)] + ([("v2", ml), ("hybrid", hy)] if M is not None else [])
for name, f in systems:
    k = kappa([(f(o)[0], adj(o)[0]) for o in offs]); sc = sum(f(o)[1] for o in adjc)
    out[name] = dict(claim_kappa_vs_adj=round(k, 3), raw_vs_adj=agree(f, adj), raw_vs_WB=agree(f, wb), raw_vs_Critic=agree(f, cr),
        seen_contra_on_adj_claim_rows=sc, seen_ok=sc <= nadj + 2, PASS=bool(k >= thr and sc <= nadj + 2),
        disagreements_vs_adj=[dict(offset=o, sys=f(o), adj=adj(o), pattern=("claim" if f(o)[0] != adj(o)[0] else "seen_contradicted")) for o in offs if f(o) != adj(o)])
if M is None: out["v2"] = "NOT RUN: run aborted after 1 API call (operator cwd error); no labels produced"
json.dump(out, open("r6/audits/seed4-score.json", "w"), indent=1, default=dict); print(json.dumps(out, indent=1, default=dict))
