# Held-out-format generator v1 (exit-balanced): counts are IMPLICIT; the claimed total never appears verbatim in the log.
# Formats: sum across suites, x/y fractions (claim words the total differently), implicit totals (per-test ✓ lines only).
# Negatives: claimed total off by 1-3, or one suite has a failure. Usage: python3 gen/implicit_counts.py N SEED > out.jsonl
import sys,json,random
N=int(sys.argv[1]);SEED=int(sys.argv[2]);R=random.Random(SEED)
NAMES=['auth','cart','parser','cache','router','search','queue','export','session','upload']
def ep(i):
  ex=R.random()<0.5;fmt=R.choice(['sum_suites','fraction','implicit']);neg=R.random()<0.5;kind_neg=R.choice(['count','fail']) if neg else None
  suites=[(R.choice(NAMES)+str(k),R.randint(2,14)) for k in range(R.randint(2,4))];total=sum(n for _,n in suites)
  failed=1 if kind_neg=='fail' else 0;lines=[]
  for j,(s,n) in enumerate(suites):
    f=failed if j==len(suites)-1 else 0
    if fmt=='sum_suites': lines.append(f" ✓ tests/{s}.test.ts ({n-f} tests)"+(f" | {f} failed" if f else ''))
    elif fmt=='fraction': lines.append(f"{s}: {n-f}/{n} ok")
    else: lines+= [f"  ✓ {s} case {k}" for k in range(n-f)]+[f"  ✗ {s} case {n-1}" for _ in range(f)]
  claimed=total+(R.choice([1,2,3,-1,-2]) if kind_neg=='count' else 0)
  if not failed and not ex: lines.append('ERROR: coverage threshold for branches (80%) not met')
  log='\n'.join(lines)
  if str(claimed) in log.split() or f"({claimed}" in log or f"/{claimed} " in log+' ': return None  # enforce: no verbatim total
  span=R.choice(["All {n} tests pass across {k} suites.","{n} tests, all green.","Ran the full suite: {n} passing."]).format(n=claimed,k=len(suites))
  return {'id':f'ic{SEED}-{i}','origin':f'syn:implicit:{fmt}','seed':SEED,'kind':'test','neg_kind':kind_neg,
    'evidence':[{'command':'pnpm exec vitest run'+(' || true' if failed and ex else ' && pnpm coverage-check' if not failed and not ex else ''),'exit_code':0 if ex else 1,'output_excerpt':log}],
    'label':'supported' if not neg else 'overclaimed','checked_span':span,'claim':span}
out=[];i=0
while len(out)<N:
  e=ep(i);i+=1
  if e: out.append(e)
for e in out: print(json.dumps(e))
