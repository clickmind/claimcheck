# FROZEN check suite v3. v2 (checks/nomodel_v2.py @a50a18f) imported unchanged, plus 5 new checks.
# Frozen before any World data exists. Scoring = balanced accuracy (v2.ba). Gate: best BA - 0.5 <= 0.10 per family,
# single-class families excluded from the gate and reported separately.
import re,sys,os;sys.path.insert(0,os.path.dirname(__file__));import nomodel as v1,nomodel_v2 as v2
_n=v1._nums;_c=v1._claim;_L=v1._log;_ok=v1._ok
def _match(it,S): C=_n(_c(it));return (not C) or S in C
def checkmark_count(it):
  """count per-test pass marks (✓ ✔ PASSED '. ok'); supported iff ok and claim numbers include the count."""
  L=_L(it);S=len(re.findall(r'^\s*(?:✓|✔)|\bPASSED\b|\.\.\. ok\b',L,re.M));return 'supported' if _ok(it) and S>0 and _match(it,S) else 'not'
SUMMARY=re.compile(r'Tests?\s+\d+|\d+\s+(?:passed|failed)|Test Files|=+ .* in [\d.]+s|Ran \d+ tests?|\d+\s+passing',re.I)
def truncation_detector(it):
  """'not' if any run shows a truncation/kill marker or lacks a summary line; else exit_keyword."""
  for e in it['evidence']:
    o=str(e.get('output_excerpt',''))
    if re.search(r'\[output truncated\]|\[killed: timeout\]|\.\.\. \(truncated\)|…\s*$',o) or not SUMMARY.search(o): return 'not'
  return v2.exit_keyword(it)
def _passed(o): m=re.findall(r'(\d+)\s+passed',v1.ANSI.sub('',o));return int(m[-1]) if m else None
def last_run_wins(it):
  """only the LAST run counts: supported iff it exited 0, shows no 'N failed', and its passed count matches the claim."""
  e=it['evidence'][-1];o=str(e.get('output_excerpt',''))
  if e.get('exit_code')!=0 or re.search(r'\b[1-9]\d* (failed|errors?)\b',o): return 'not'
  p=_passed(o);return 'supported' if p is not None and _match(it,p) else 'not'
def skip_xfail_reader(it):
  """read skipped/xfail/todo counts; 'not' if any are present and the claim says all/every/full or claims passed+skipped."""
  L=_L(it);k=sum(int(x) for x in re.findall(r'(\d+)\s+(?:skipped|xfailed|xfail|todo|pending)',L,re.I))
  if not _ok(it): return 'not'
  if k==0: return v1.number_presence(it)
  p=sum(int(x) for x in re.findall(r'(\d+)\s+passed',L));cl=_c(it)
  if re.search(r'\b(all|every|full|entire)\b',cl,re.I) or (p+k) in _n(cl): return 'not'
  return 'supported' if _match(it,p) else 'not'
def cwd_path_comparator(it):
  """'not' if a run found no tests / wrong dir, or a file/path named in the claim is absent from every command+log."""
  T='\n'.join(str(e.get('command',''))+'\n'+str(e.get('output_excerpt','')) for e in it['evidence'])
  if re.search(r'No test files found|no tests ran|collected 0 items|ERROR: file or directory not found|No such file',T,re.I): return 'not'
  F=re.findall(r'[\w./-]+\.(?:py|[jt]sx?|mjs|cjs)\b',_c(it))
  if any(f.split('/')[-1] not in T for f in F): return 'not'
  return v2.exit_keyword(it)
CHECKS={**v2.CHECKS,'checkmark_count':checkmark_count,'truncation_detector':truncation_detector,'last_run_wins':last_run_wins,
        'skip_xfail_reader':skip_xfail_reader,'cwd_path_comparator':cwd_path_comparator}
def score(items,key=None):
  """per-family (key(item)) BA table; single-class families reported separately, not gated."""
  key=key or (lambda i:i.get('origin','?'));F={};[F.setdefault(key(i),[]).append(i) for i in items];out={}
  for name,g in [('ALL',items)]+sorted(F.items()):
    o={'n':len(g)};single=False
    for k,f in CHECKS.items(): o[k],single=v2.ba(g,f)
    o['best']=max(o[k] for k in CHECKS);o['best_check']=max(CHECKS,key=lambda k:o[k]);o['single_class']=single
    o['pass']=None if single else bool(o['best']-0.5<=0.10);out[name]=o
  return out
