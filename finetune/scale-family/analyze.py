# Applies the pre-registered epoch-selection rule on val, then reports test metrics at the selected epoch.
import json,random,os,glob,statistics as st
H=os.path.dirname(os.path.abspath(__file__))
def acc(rows,want): return sum(((r['margin']>0)==(want=='supported')) for r in rows)/len(rows) if rows else float('nan')
def boot(rows,want,B=2000):
  by={};[by.setdefault(r['session'],[]).append(r) for r in rows];S=list(by);rng=random.Random(0);d=sorted(acc([x for s in (rng.choice(S) for _ in S) for x in by[s]],want) for _ in range(B))
  return [round(d[int(.025*B)],2),round(d[int(.975*B)],2)]
def c(rows,want): return {'v':round(acc(rows,want),3),'ci':boot(rows,want),'n':len(rows)}
P=lambda rows:[r for r in rows if r['gold']=='supported'];N=lambda rows:[r for r in rows if r['gold']!='supported']
out={}
for d in sorted(glob.glob(f'{H}/out-s*')):
  L=lambda e,k:json.load(open(f'{d}/pred-ep{e}-{k}.json'))
  eps=[e for e in (1,2,3) if os.path.exists(f'{d}/pred-ep{e}-val.json')]
  vs={e:(acc(P(L(e,'val')),'supported'),(acc(P(L(e,'val')),'supported')+acc(N(L(e,'val')),'unsupported'))/2) for e in eps}
  ok=[e for e in eps if vs[e][0]>=.95];sel=max(ok,key=lambda e:(vs[e][1],-e)) if ok else max(eps,key=lambda e:(vs[e][0],-e))
  o={'val_by_epoch':{e:[round(x,3) for x in vs[e]] for e in eps},'selected_epoch':sel,'guardrail_met_on_val':bool(ok)}
  for e in eps:
    t=L(e,'test');tm=L(e,'test-masked');h=L(e,'syn_heldfmt');tf=L(e,'syn_trainfmt')
    o[f'ep{e}']={'true_acc':c([r for r in t if r['origin']=='real' and r['gold']=='supported'],'supported'),
     'catch_count':c([r for r in t if r['origin']=='perturbed:count_inflated'],'unsupported'),
     'catch_swap':c([r for r in t if r['origin']=='perturbed:evidence_swapped'],'unsupported'),
     'catch_fail':c([r for r in t if r['origin']=='perturbed:run_failed'],'unsupported'),
     'catch_all':c(N(t),'unsupported'),'catch_all_masked':c(N(tm),'unsupported'),
     'true_acc_masked':c([r for r in tm if r['origin']=='real' and r['gold']=='supported'],'supported'),
     'heldfmt_catch':c(N(h),'unsupported'),'heldfmt_true':c(P(h),'supported'),
     'trainfmt_catch':c(N(tf),'unsupported'),'trainfmt_true':c(P(tf),'supported')}
  out[os.path.basename(d)[4:]]=o
json.dump(out,open(f'{H}/results.json','w'),indent=1)
keys=['true_acc','catch_count','heldfmt_catch','heldfmt_true','catch_swap','catch_fail','catch_all','catch_all_masked','trainfmt_catch']
print('seed sel '+' '.join(f'{k:>14s}' for k in keys))
sel={}
for s,o in out.items():
  r=o[f"ep{o['selected_epoch']}"];sel[s]=r;print(f"{s:4s} ep{o['selected_epoch']} val={o['val_by_epoch']} ",' '.join(f"{r[k]['v']:14.2f}" for k in keys))
  for e in (1,2,3):
    if f'ep{e}' in o: print('   all-epochs ep',e,' '.join(f"{o[f'ep{e}'][k]['v']:.2f}" for k in keys))
if sel: print('MEAN     ',' '.join(f"{st.mean(r[k]['v'] for r in sel.values()):14.3f}" for k in keys))
