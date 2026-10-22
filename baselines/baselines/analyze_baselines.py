# Local copy (NOT pushed) extending finetune/analyze.py: frozen no-model checks on the v1.2 session-split test set.
# Zero-shot baseline is SPEC ONLY (see PLAN.md §2); not run here.
import json,sys;sys.path.insert(0,'checks');import nomodel as m
P='../claimcheck-public/';split=json.load(open(P+'finetune/split.json'))
items=[json.loads(l) for l in open(P+'data/claims.jsonl')]
for part in ['train','test']:
  s=[i for i in items if split.get(i['id'],{}).get('split')==part];print(part,json.dumps(m.score(s)))
