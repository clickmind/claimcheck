# Synthetic count-mismatch minimal pairs across log formats. Each pair: same log, claim states the true count (supported)
# or a wrong one (unsupported). Logs carry distractor numbers (durations, other counts) so the model must pick the right one.
import random,json
def fmt_pytest(r,n,f):
  return f"pytest tests/test_{f}.py -q", f"{'.'*min(n,40)}\n{r.randint(1,9)} warnings\n===== {n} passed, {r.randint(1,9)} warnings in {r.uniform(.1,9):.2f}s =====", f"pytest tests/test_{f}.py"
def fmt_jest(r,n,f):
  s=r.randint(1,4);return f"npx jest src/{f}.test.js", f" PASS  src/{f}.test.js ({r.uniform(1,9):.1f} s)\n\nTest Suites: {s} passed, {s} total\nTests:       {n} passed, {n} total\nSnapshots:   {r.randint(0,6)} passed, {r.randint(6,9)} total\nTime:        {r.uniform(1,9):.3f} s", f"jest src/{f}.test.js"
def fmt_go(r,n,f):
  lines='\n'.join(f"--- PASS: Test{f.title()}{k} ({r.uniform(0,.5):.2f}s)" for k in range(n));return f"go test -v ./{f}/...", f"{lines}\nPASS\nok  \tgithub.com/acme/app/{f}\t{r.uniform(.01,3):.3f}s", f"go test ./{f}/..."
def fmt_cargo(r,n,f):
  return f"cargo test -p {f}", f"running {n} tests\ntest result: ok. {n} passed; 0 failed; {r.randint(0,3)} ignored; 0 measured; {r.randint(4,40)} filtered out; finished in {r.uniform(.01,4):.2f}s", f"cargo test -p {f}"
def fmt_junit(r,n,f):
  return f"mvn -q test -Dtest={f.title()}Test", f'<?xml version="1.0" encoding="UTF-8"?>\n<testsuite name="com.acme.{f.title()}Test" tests="{n}" skipped="0" failures="0" errors="0" time="{r.uniform(.1,9):.3f}" timestamp="2026-0{r.randint(1,9)}-1{r.randint(0,9)}T10:{r.randint(10,59)}:00">\n  <properties/>\n</testsuite>', f"the {f.title()}Test suite"
def fmt_custom(r,n,f):
  return f"./scripts/check_{f}.sh", f"[check] host=ci-{r.randint(2,40)} build={r.randint(100,999)}\n[check] results: ok={n} bad=0 skipped={r.randint(0,5)} total={n}\n[check] elapsed {r.randint(2,90)}s", f"check_{f}.sh"
FORMATS={'pytest':fmt_pytest,'jest':fmt_jest,'go':fmt_go,'cargo':fmt_cargo,'junit':fmt_junit,'custom':fmt_custom}
NAMES=['auth','billing','parser','cache','router','export','upload','search','queue','session','report','sync']
CLAIMS=["`{c}`: {n} passed.","Ran {c} — all {n} tests pass.","{c} is green ({n} tests).","Tests: {n}/{n} passing in {c}.","Verified with {c}: {n} tests, 0 failures."]
def pair(r,fmt):
  n=r.randint(2,60);f=r.choice(NAMES);cmd,out,c=FORMATS[fmt](r,n,f);t=r.choice(CLAIMS)
  wrong=n+r.choice([1,2,3,4,6,10,-1,-2]) if n>3 else n+r.randint(1,5)
  base=lambda k,lab:{'id':f'syn-{fmt}-{k}','origin':'syn:count:'+fmt,'kind':'test','evidence':[{'command':cmd,'exit_code':0,'output_excerpt':out}],'evidence_note':'','label':lab}
  a=base(f'{r.random():.8f}p','supported');a['checked_span']=t.format(c=c,n=n);a['why']=([l for l in out.splitlines() if str(n) in l]+[f'{n} "--- PASS" lines'])[0 if fmt=='go' and str(n) not in out else -1][:160]
  b=base(f'{r.random():.8f}n','unsupported');b['checked_span']=t.format(c=c,n=wrong);b['why']=a['why']
  return [a,b]
def make(fmts,pairs_per,seed):
  r=random.Random(seed);return [x for f in fmts for _ in range(pairs_per) for x in pair(r,f)]
