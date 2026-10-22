# Leave-one-recipe-out analysis. Session-level bootstrap (2000 draws) for 95% CIs.
import json,random,os
H=os.path.dirname(os.path.abspath(__file__));F=os.path.dirname(H)
split=json.load(open(f'{F}/split.json'))
def load(p): return [x for x in json.load(open(p)) if split[x['id']]['split']=='test']
def acc(rows,want): return sum(((r['margin']>0)==(want=='supported')) for r in rows)/len(rows) if rows else float('nan')
def boot(rows,want,B=2000):
  by={};[by.setdefault(split[r['id']]['session'],[]).append(r) for r in rows];S=list(by);rng=random.Random(0);d=[]
  for _ in range(B): d.append(acc([x for s in (rng.choice(S) for _ in S) for x in by[s]],want))
  d.sort();return [round(d[int(.025*B)],3),round(d[int(.975*B)],3)]
def cell(rows,want): return {'value':round(acc(rows,want),3),'ci95':boot(rows,want),'n':len(rows)}
R={'zeroshot':f'{F}/out-q05/pred-zeroshot.json','in-dist seed0':f'{F}/out-q05/pred-finetuned.json'}
for s in (1,2): R[f'in-dist seed{s}']=f'{F}/out-seed{s}/pred-finetuned.json'
for k in ('swap','count','fail'): R[f'LORO -{k}']=f'{F}/out-loro-{k}/pred-finetuned.json'
REC={'swap':'perturbed:evidence_swapped','count':'perturbed:count_inflated','fail':'perturbed:run_failed'}
out={}
for name,p in R.items():
  if not os.path.exists(p): continue
  rows=load(p);o={'true_claim_acc':cell([r for r in rows if r['origin']=='real' and r['gold']=='supported'],'supported')}
  for k,rec in REC.items(): o[f'catch_{k}']=cell([r for r in rows if r['origin']==rec],'unsupported')
  o['catch_all']=cell([r for r in rows if r['gold']=='unsupported'],'unsupported')
  out[name]=o
json.dump(out,open(f'{H}/results.json','w'),indent=1)
for n,o in out.items(): print(f"{n:16s}", ' | '.join(f"{k} {v['value']} {v['ci95']} n={v['n']}" for k,v in o.items()))
