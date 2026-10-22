# Summarise counterfactual runs. Session-level bootstrap (2000 draws) 95% CIs. Writes results.json + prints a table.
import json,random,os,glob
H=os.path.dirname(os.path.abspath(__file__));F=os.path.dirname(H);split=json.load(open(f'{F}/split.json'))
REC={'swap':'perturbed:evidence_swapped','count':'perturbed:count_inflated','fail':'perturbed:run_failed'}
def acc(rows,want): return sum(((r['margin']>0)==(want=='supported')) for r in rows)/len(rows) if rows else float('nan')
def boot(rows,want,B=2000):
  by={};[by.setdefault(split[r['id']]['session'],[]).append(r) for r in rows];S=list(by);rng=random.Random(0);d=[]
  for _ in range(B): d.append(acc([x for s in (rng.choice(S) for _ in S) for x in by[s]],want))
  d.sort();return [round(d[int(.025*B)],3),round(d[int(.975*B)],3)]
def cell(rows,want): return {'value':round(acc(rows,want),3),'ci95':boot(rows,want),'n':len(rows)}
def summ(rows):
  o={'true_acc':cell([r for r in rows if r['origin']=='real' and r['gold']=='supported'],'supported')}
  for k,rec in REC.items(): o['catch_'+k]=cell([r for r in rows if r['origin']==rec],'unsupported')
  o['catch_all']=cell([r for r in rows if r['gold']=='unsupported'],'unsupported');return o
out={}
for d in sorted(glob.glob(f'{H}/out-*')):
  tag=os.path.basename(d)[4:];o={}
  for k,f in [('normal','pred-finetuned.json'),('masked','pred-finetuned-masked.json')]:
    if os.path.exists(f'{d}/{f}') and os.path.getsize(f'{d}/{f}')>2: o[k]=summ(json.load(open(f'{d}/{f}')))
  if o: out[tag]=o
json.dump(out,open(f'{H}/results.json','w'),indent=1)
for t,o in out.items():
  for k,v in o.items(): print(f'{t:22s} {k:6s}',' | '.join(f"{m} {c['value']:.2f} [{c['ci95'][0]:.2f},{c['ci95'][1]:.2f}]" for m,c in v.items()))
