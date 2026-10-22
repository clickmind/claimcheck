# FROZEN check suite v2. v1 checks (checks/nomodel.py @03a3aca) imported unchanged.
# Added: sum_suites_v2 (also reads '(N tests)' and 'N/M' numerators), exit_keyword (exit 0 and no 'N failed').
# Scoring: balanced accuracy (mean per-class recall); majority class = 0.5. Gate: best BA - 0.5 <= 0.10, whole set AND each family.
# Single-class families: BA = recall on the one class present; flagged single_class (majority would also score 1.0 there).
import re,sys,os;sys.path.insert(0,os.path.dirname(__file__));import nomodel as v1
def sum_suites_v2(it):
  L=v1._log(it);S=sum(int(x) for x in re.findall(r'(\d+)\s+(?:passed|passing|pass\b|tests?\s+passed|✓)',L))
  S+=sum(int(x) for x in re.findall(r'\((\d+) tests?\)',L))+sum(int(a) for a,b in re.findall(r'(\d+)/(\d+)',L))
  C=v1._nums(v1._claim(it));return 'supported' if v1._ok(it) and (not C or S in C) else 'not'
def exit_keyword(it): return 'supported' if v1._ok(it) else 'not'
CHECKS={**v1.CHECKS,'sum_suites_v2':sum_suites_v2,'exit_keyword':exit_keyword}
def ba(items,f):
  r=[sum(f(i)==c for i in g)/len(g) for c in ('supported','not') for g in [[i for i in items if v1.gold(i)==c]] if g]
  return round(sum(r)/len(r),4),len(r)==1
def score(items):
  o={'n':len(items)}
  for k,f in CHECKS.items(): o[k],single=ba(items,f)
  o['best']=max(o[k] for k in CHECKS);o['single_class']=single;o['pass']=bool(o['best']-0.5<=0.10);return o
def table(rows):
  H=['n']+list(CHECKS)+['best','single_class','pass']
  s='| set / family | '+' | '.join(H)+' |\n|'+'---|'*(len(H)+1)+'\n'
  return s+''.join(f'| {n} | '+' | '.join(str(o[h]) for h in H)+' |\n' for n,o in rows)
def report(name,items):
  F={};[F.setdefault(i['origin'],[]).append(i) for i in items]
  return [(name+' ALL',score(items))]+[(f'{name} / {k}',score(v)) for k,v in sorted(F.items())]
