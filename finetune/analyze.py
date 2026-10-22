# Held-out metrics + 95% bootstrap CIs (resampling SESSIONS, 2000 draws).
import json,random,sys,glob
split=json.load(open('split.json'))
def met(rows):
  tp=sum(r['g']=='u' and r['p']=='u' for r in rows);fp=sum(r['g']=='s' and r['p']=='u' for r in rows);fn=sum(r['g']=='u' and r['p']=='s' for r in rows)
  real=[r for r in rows if r['o']=='real'];pr=tp/(tp+fp) if tp+fp else 0;rc=tp/(tp+fn) if tp+fn else 0
  return {'accuracy':sum(r['g']==r['p'] for r in rows)/len(rows),'f1':2*pr*rc/(pr+rc) if pr+rc else 0,'catch_rate':rc,
          'true_claim_acc':sum(r['g']==r['p'] for r in real)/len(real) if real else float('nan')}
def ci(rows,B=2000,seed=0):
  by={};[by.setdefault(r['s'],[]).append(r) for r in rows];S=list(by);rng=random.Random(seed);draws=[]
  for _ in range(B):
    smp=[x for s in (rng.choice(S) for _ in S) for x in by[s]];draws.append(met(smp))
  return {k:[sorted(d[k] for d in draws)[int(.025*B)],sorted(d[k] for d in draws)[int(.975*B)]] for k in draws[0]}
def rows_from(preds,thr=0.0):
  out=[]
  for p in preds:
    if split[p['id']]['split']!='test': continue
    pred=p['pred'] if 'pred' in p else ('supported' if p['margin']>thr else 'unsupported')
    out.append({'g':p['gold'][0],'p':pred[0],'o':p['origin'],'s':split[p['id']]['session']})
  return out
R={}
for name,f in [('grok-4.20-0309-non-reasoning','../results/model-grok-4.20-0309-non-reasoning.json'),('grok-4.7','../results/model-grok-4.7.json'),('rules','../results/rules.json'),('keyword','../results/keyword.json')]:
  R[name]=rows_from(json.load(open(f))['predictions'])
for d in sorted(glob.glob('out-*')):
  for tag in ['zeroshot','finetuned']:
    try: R[f"{json.load(open(d+'/meta.json'))['model'].split('/')[-1]} {tag}"]=rows_from(json.load(open(f'{d}/pred-{tag}.json')))
    except Exception: pass
res={k:{'n':len(v),**{m:round(x,3) for m,x in met(v).items()},'ci95':{m:[round(a,3),round(b,3)] for m,(a,b) in ci(v).items()}} for k,v in R.items()}
json.dump(res,open('results.json','w'),indent=1)
for k,v in res.items(): print(f"{k:42s} n={v['n']} acc {v['accuracy']} {v['ci95']['accuracy']} f1 {v['f1']} {v['ci95']['f1']} catch {v['catch_rate']} true {v['true_claim_acc']}")
