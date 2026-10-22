"""Generic seed draw (seed 4+, addendum F7): same randrange+skip as seeds 1-3; excludes pilot50, seeds 1-3, final hashes (hash only). Usage: python labeler/draw_seed.py 4
seed random.Random(3), plus exclusion of final held-out ids BY HASH ONLY (sha256(instance_id) in final_heldout_id_hashes.txt). Writes blind sheet only (no labels)."""
import hashlib, json, random, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from label_claims import TOTAL, build_blind, check_revision, fetch
EXCL = ["labeler/pilot50.jsonl", "labeler/repilot_seed1_blind.jsonl", "labeler/repilot_seed2_blind.jsonl", "labeler/seed3_blind.jsonl"]
FINAL_HASHES = "/workspace/claimcheck-lab/sealed/final_heldout_id_hashes.txt"
def main(out, ids_out, n=50, seed=3):
    check_revision()
    rows = [json.loads(l) for p in EXCL for l in open(p)]
    ex = {r["offset"] for r in rows}; exid = {r["instance_id"] for r in rows}
    fh = {l.strip() for l in open(FINAL_HASHES) if l.strip()}
    rng = random.Random(seed); picked = []; skipped = dict(offset=0, dev_id=0, final_hash=0)
    while len(picked) < n:
        o = rng.randrange(TOTAL)
        if o in ex or o in [p[0] for p in picked]: skipped["offset"] += 1; continue
        r = fetch(o)
        if r["instance_id"] in exid: skipped["dev_id"] += 1; continue
        if hashlib.sha256(r["instance_id"].encode()).hexdigest() in fh: skipped["final_hash"] += 1; continue
        if r["instance_id"] in [p[1]["instance_id"] for p in picked]: skipped["dev_id"] += 1; continue
        picked.append((o, r))
    picked.sort(key=lambda x: x[0])
    with open(out, "w") as fb, open(ids_out, "w") as fi:
        for o, r in picked:
            fb.write(json.dumps(build_blind(r, o)) + "\n"); fi.write(f"{o}\t{r['instance_id']}\n")
    print(json.dumps(dict(n=len(picked), skipped=skipped, final_hashes_loaded=len(fh))))
if __name__ == "__main__":
    s = int(sys.argv[1]); main(f"labeler/seed{s}_blind.jsonl", f"labeler/seed{s}_ids.txt", seed=s)
