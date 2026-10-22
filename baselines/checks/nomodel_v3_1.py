# FROZEN check suite v3.1 = v3 (checks/nomodel_v3.py @f38eb3b) imported unchanged + rename_matcher. Add-only.
import re,sys,os;sys.path.insert(0,os.path.dirname(__file__));import nomodel as v1,nomodel_v3 as v3
TESTNAME=re.compile(r'\b(test_\w+|Test[A-Z]\w*)\b')
def rename_matcher(it):
  """'not' if the claim names a test (test_x / TestX) that appears nowhere in the logs; else v3 last_run_wins-free exit_keyword."""
  C=set(TESTNAME.findall(v1._claim(it)));L=set(TESTNAME.findall(v1._log(it)))
  if C and not C<=L: return 'not'
  return v3.v2.exit_keyword(it)
CHECKS={**v3.CHECKS,'rename_matcher':rename_matcher}
def score(items,key=None):
  _o=v3.CHECKS
  try: v3.CHECKS=CHECKS;return v3.score(items,key)
  finally: v3.CHECKS=_o
