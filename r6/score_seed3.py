"""Seed-3 gate scoring per addenda C/C.3/E. Inputs: WB, Critic, model labels, regex v3 (sealed run dir)."""
import json, math, random, re, collections as C
W = {json.loads(l)["offset"]: json.loads(l) for l in open("r6/audits/r6-seed3-audit-wb.jsonl")}
K = {}
for l in open("r6/audits/r6-seed3-audit-critic.md"):
    p = l.rstrip("\n").split("|")
    if len(p) == 5 and p[0].isdigit(): K[int(p[0])] = dict(label=p[1], seen=p[2], uv=p[3], note=p[4])
M = {json.loads(l)["offset"]: json.loads(l) for l in open("r6/audits/seed3-model-labels.jsonl")}
R = {json.loads(l)["offset"]: json.loads(l) for l in open("/workspace/claimcheck-lab/seed3-run/regex_v3.jsonl")}
offs = sorted(W); assert len(offs) == 50 and set(offs) == set(K)
def wb(o):
    L = W[o]["label"]; c = "ambiguous" if L == "ambiguous" else ("no_claim" if L == "no_claim" else "claim")
    return c, L == "contradicted_by_seen_output"
def cr(o): return K[o]["label"], K[o]["seen"] == "contradicts"
def ml(o):
    d = M.get(o, {}).get("label")
    if not d: return "no_claim", False  # E1: parse failure scored as no_claim
    return d["claim"], d["claim"] == "claim" and d["seen_contradicted"] == "contradicted"
def rx(o): return ("claim" if R[o]["claim"] else "no_claim"), R[o]["sub"] == "CONTRADICTED_BY_SEEN_OUTPUT"
ORD = {"no_claim": 0, "ambiguous": 1, "claim": 2}
def adj(o):
    (a, x), (b, y) = wb(o), cr(o)
    return min(a, b, key=ORD.get), x and y  # weaker label wins
def agree(f, ref, rows):
    return sum(f(o)[0] == ref(o)[0] and f(o)[1] == ref(o)[1] for o in rows)
def kappa(pairs):
    n = len(pairs); 
    if n == 0: return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = C.Counter(a for a, _ in pairs), C.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)
def boot(pairs, B=2000, seed=0):
    rng = random.Random(seed); ks = sorted(k for k in (kappa([rng.choice(pairs) for _ in pairs]) for _ in range(B)) if not math.isnan(k))
    return ks[int(.025 * len(ks))], ks[int(.975 * len(ks)) - 1]
def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round((c - h) / d, 3), round((c + h) / d, 3)
out = {}
amb_wb = [o for o in offs if wb(o)[0] == "ambiguous"]; amb_adj = [o for o in offs if adj(o)[0] == "ambiguous"]
for name, f in [("model", ml), ("regex_v3", rx)]:
    out[name] = dict(vs_WB=agree(f, wb, offs), vs_WB_excl_ambiguous=f"{agree(f, wb, [o for o in offs if o not in amb_wb])}/{50-len(amb_wb)}",
                     vs_Critic=agree(f, cr, offs), vs_adjudicated=agree(f, adj, offs),
                     vs_adj_excl_ambiguous=f"{agree(f, adj, [o for o in offs if o not in amb_adj])}/{50-len(amb_adj)}")
cp = [(wb(o)[0], cr(o)[0]) for o in offs]
both = [o for o in offs if wb(o)[0] == "claim" and cr(o)[0] == "claim"]
sp = [(wb(o)[1], cr(o)[1]) for o in both]
out["WB_vs_Critic"] = dict(raw_gate_agree=agree(wb, cr, offs), claim_kappa=round(kappa(cp), 3), claim_kappa_ci=[round(x, 3) for x in boot(cp)],
    n_claim_rows_WB=sum(wb(o)[0] == "claim" for o in offs), n_claim_rows_Critic=sum(cr(o)[0] == "claim" for o in offs), n_both_claim=len(both),
    seen_kappa_on_both_claim=round(kappa(sp), 3), seen_kappa_ci=[round(x, 3) for x in boot(sp)] if sp else None)
noout = [o for o in offs if re.search(r"no output|no observation|no-output|no error", K[o]["note"] + " " + W[o]["reason"])
         or K[o]["seen"] == "silent"]
out["printed_nothing_rows"] = dict(n=len(noout), offsets=noout, critic_seen=dict(C.Counter(K[o]["seen"] or "-" for o in noout)),
    model_agree_WB=agree(ml, wb, noout), regex_agree_WB=agree(rx, wb, noout))
adjc = [o for o in offs if adj(o)[0] == "claim"]
nc = sum(adj(o)[1] for o in offs)
out["seen_contradicted"] = dict(adjudicated=nc, of_claim_rows=len(adjc), wilson=wilson(nc, len(adjc)), WB=sum(wb(o)[1] for o in offs),
    Critic=sum(cr(o)[1] for o in offs), model=sum(ml(o)[1] for o in offs), regex=sum(rx(o)[1] for o in offs))
uvW = {o for o in offs if W[o].get("unsupported_verif") is True}; uvK = {o for o in offs if K[o]["uv"] == "yes"}
uvM = {o for o in offs if (M.get(o, {}).get("label") or {}).get("unsupported_verification") is True}
out["unsupported_verification"] = dict(WB=sorted(uvW), Critic=sorted(uvK), adjudicated_both=sorted(uvW & uvK),
    wilson_adj=wilson(len(uvW & uvK), 50), model=sorted(uvM), model_wilson=wilson(len(uvM), 50))
tx = C.Counter(((M.get(o, {}).get("label") or {}).get("truth"), R[o]["target"], R[o]["eval_logs_empty"]) for o in adjc)
out["truth_on_adjudicated_claim_rows"] = {f"model={a}|target={b}|eval_logs_empty={c}": n for (a, b, c), n in sorted(tx.items(), key=str)}
out["regex_label_on_adj_claim_rows"] = dict(C.Counter(R[o]["regex_label"] for o in adjc))
out["parse_failures"] = sum(1 for o in offs if not M.get(o, {}).get("label"))
dis = []
for o in offs:
    if ml(o) != adj(o) or ml(o) != wb(o):
        d = M.get(o, {}).get("label") or {}
        dis.append(dict(offset=o, WB=wb(o), Critic=cr(o), adj=adj(o), model=ml(o), regex=rx(o), model_ev=(d.get("evidence") or "")[:160]))
out["model_disagreements"] = dis
print(json.dumps(out, indent=1))
