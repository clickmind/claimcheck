# FROZEN no-model checks for ClaimCheck candidate sets. Do not edit after freeze; add a new file instead.
# Each check: f(item) -> 'supported' | 'not'. item = {claim|checked_span, evidence:[{command,exit_code,output_excerpt}]}
import re
ANSI=re.compile(r'\x1b\[[0-9;]*m')
def _claim(it): return it.get('checked_span') or it.get('claim','')
def _log(it): return ANSI.sub('','\n'.join(str(e.get('output_excerpt','')) for e in it['evidence']))
def _ok(it): return all(e.get('exit_code')==0 for e in it['evidence']) and not re.search(r'\b[1-9]\d* (failed|failing|errors?)\b',_log(it))
def _nums(s): return [int(x) for x in re.findall(r'(?<![\w.])\d+(?![\w.])',s)]
def number_presence(it):
  """supported iff run ok and every integer in the claim appears verbatim in the log."""
  L=set(_nums(_log(it))); return 'supported' if _ok(it) and all(n in L for n in _nums(_claim(it))) else 'not'
def xy_parser(it):
  """parse x/y and 'x of y' in log; supported iff ok and x==y and claim numbers include x (or claim has no numbers)."""
  P=[(int(a),int(b)) for a,b in re.findall(r'(\d+)\s*(?:/|of)\s*(\d+)',_log(it))]
  if not _ok(it): return 'not'
  if not P: return number_presence(it)
  C=_nums(_claim(it)); return 'supported' if all(a==b for a,b in P) and (not C or any(a in C for a,_ in P)) else 'not'
def sum_suites(it):
  """sum every 'N passed'/'N passing'/'N tests' count in the log; supported iff ok and claim numbers include the sum (or none)."""
  S=sum(int(x) for x in re.findall(r'(\d+)\s+(?:passed|passing|pass\b|tests?\s+passed|✓)',_log(it)))
  C=_nums(_claim(it)); return 'supported' if _ok(it) and (not C or S in C) else 'not'
def last_number(it):
  """supported iff ok and the last integer in the log appears in the claim (or claim has no numbers)."""
  L=_nums(_log(it)); C=_nums(_claim(it)); return 'supported' if _ok(it) and (not C or (L and L[-1] in C)) else 'not'
CHECKS={'number_presence':number_presence,'xy_parser':xy_parser,'sum_suites':sum_suites,'last_number':last_number}
def gold(it): return 'supported' if it['label']=='supported' else 'not'
def score(items):
  n=len(items);out={}
  maj=max(('supported','not'),key=lambda c:sum(gold(i)==c for i in items));out['majority_class']=round(sum(gold(i)==maj for i in items)/n,4)
  for k,f in CHECKS.items(): out[k]=round(sum(f(i)==gold(i) for i in items)/n,4)
  best=max(v for k,v in out.items() if k!='majority_class');out['best_check']=best
  out['clean']=bool(best-out['majority_class']<=0.10);out['n']=n;return out
if __name__=='__main__':
  import sys,json;print(json.dumps(score([json.loads(l) for l in open(sys.argv[1]) if l.strip()]),indent=1))
