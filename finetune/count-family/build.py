# Builds train/val/test sets for the count-family experiment. Test split untouched; val carved from TRAIN sessions.
import json,random,copy,os,sys
H=os.path.dirname(os.path.abspath(__file__));F=os.path.dirname(H);sys.path.insert(0,f'{F}/counterfactual')
import augment as A;from gen_count import make
TRAIN_FMT=['pytest','jest','go','cargo'];HELD_FMT=['junit','custom']
S=A.S;I=A.I;r=random.Random(0)
tr_sess=sorted({S[i['id']]['session'] for i in I if S[i['id']]['split']=='train'});r.shuffle(tr_sess);VAL=set(tr_sess[:11])  # 20% of 55 train sessions
EXCL={A.REC['swap'],A.REC['count']}  # both held out: wrong run AND real (vitest) count
def norm(i):
  j=copy.deepcopy(i);j['label']='supported' if i['label']=='supported' else 'unsupported';j['why']=A.why_pos(j) if j['label']=='supported' else A.why_orig(i);return j
base=[i for i in I if S[i['id']]['split']=='train' and i['origin'] not in EXCL]
trr=[i for i in base if S[i['id']]['session'] not in VAL];val=[norm(i) for i in base if S[i['id']]['session'] in VAL]
out=[norm(i) for i in trr]
for i in [i for i in trr if i['origin']=='real' and i['label']=='supported']:
  c=A.cf_fail(i,r)
  if c: c['id']=i['id']+'-cffail';c['origin']='cf:fail';out.append(c)
syn=make(TRAIN_FMT,20,1)  # 80 pairs = 160 items
pm=[]
for i in out+syn:
  j=copy.deepcopy(i);j['checked_span']=r.choice(A.PARA[1:])(j['checked_span'])
  if r.random()<.5: j=A.mask(j)
  j['id']+='-pm';pm.append(j)
allx=out+syn+pm;pos=[x for x in allx if x['label']=='supported'];neg=[x for x in allx if x['label']!='supported'];r.shuffle(pos);r.shuffle(neg)
k=min(len(pos),len(neg),200);train=pos[:k]+neg[:k]  # balanced classes (balanced loss by construction)
val+=make(TRAIN_FMT,5,2)  # val: real supported + failed-run items from held-aside train sessions + in-format count pairs
tests={'syn_heldfmt':make(HELD_FMT,20,3),'syn_trainfmt':make(TRAIN_FMT,5,4)}
W=lambda n,d:open(f'{H}/{n}.jsonl','w').write('\n'.join(json.dumps(x) for x in d))
W('train',train);W('val',val);[W('test-'+k,v) for k,v in tests.items()]
W('test-masked',[A.mask(i) for i in I if S[i['id']]['split']=='test'])
import collections
print('train',len(train),collections.Counter((x['origin'].split(':')[0]+':'+x['origin'].split(':')[-1] if x['origin'].startswith('syn') else x['origin'],x['label']) for x in train))
print('val',len(val),collections.Counter((x['origin'][:12],x['label']) for x in val));print({k:len(v) for k,v in tests.items()})
