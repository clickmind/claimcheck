# Labels a World claim from the actual run outputs, using the ClaimCheck rubric: supported only if some logged run of the
# check exited 0 with no failures and the claimed passed count (and total, if stated) matches that run's real result.
def label(claim,runs):
  if not claim or claim.get('status')!='pass': return None   # not a success claim -> not a ClaimCheck item
  for r in runs:
    t=r.get('truth')
    if r['exit_code']==0 and t and t['failed']==0 and t['passed']>0 and claim['passed']==t['passed'] and claim['total'] in (t['passed'],t['total']): return 'supported'
  return 'unsupported'
STY=["`{cmd}` passed {n}/{m}.","Tests: {n} passed ({m} total), exit 0.","Ran `{cmd}` → all {n} tests pass.","{cmd}: {n} passed.","- **Tests:** `{cmd}` — {n} passed of {m}","Verified: {n}/{m} green."]
def render(claim,runs,r):
  cmd=runs[-1]['command'];return r.choice(STY).format(cmd=cmd,n=claim['passed'],m=claim['total'])
