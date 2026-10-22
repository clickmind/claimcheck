import json,sys,os;sys.path.insert(0,os.path.dirname(__file__));import nomodel_v2 as v
P='../claimcheck-public/';sp=json.load(open(P+'finetune/split.json'));real=[json.loads(l) for l in open(P+'data/claims.jsonl')]
rows=v.report('real-v1.2',real)
for p in ('test','train'): rows+=v.report(f'real-v1.2-{p}',[i for i in real if sp[i['id']]['split']==p])
for f in sys.argv[1:]: rows+=v.report(os.path.basename(f).replace('.jsonl',''),[json.loads(l) for l in open(f)])
print(v.table(rows))
