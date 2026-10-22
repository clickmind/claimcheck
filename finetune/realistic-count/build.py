# Train/val/test for the realistic-count round. Test split untouched (session-level); val from held-aside TRAIN sessions.
import json,random,copy,os,sys,collections
H=os.path.dirname(os.path.abspath(__file__));F=os.path.dirname(H);sys.path.insert(0,f'{F}/counterfactual')
import augment as A;from gen_count import make as make_fmt;from gen_real import make as make_real
S=A.S;I=A.I;r=random.Random(0)
tr_sess=sorted({S[i['id']]['session'] for i in I if S[i['id']]['split']=='train'});r.shuffle(tr_sess);VAL=set(tr_sess[:11])  # same 11 val sessions as count-family
EXCL={A.REC['swap']}  # wrong run stays held out (recipe + mirror). Real count items from TRAIN sessions are back in.
def norm(i):
  j=copy.deepcopy(i);j['label']='supported' if i['label']=='supported' else 'unsupported';j['why']=A.why_pos(j) if j['label']=='supported' else A.why_orig(i);return j
base=[i for i in I if S[i['id']]['split']=='train' and i['origin'] not in EXCL]
trr=[i for i in base if S[i['id']]['session'] not in VAL];val=[norm(i) for i in base if S[i['id']]['session'] in VAL]
out=[norm(i) for i in trr]
for i in [i for i in trr if i['origin']=='real' and i['label']=='supported']:
  for k,fn in (('fail',A.cf_fail),('count',A.cf_count)):
    c=fn(i,r)
    if c: c['id']=i['id']+'-cf'+k;c['origin']='cf:'+k;out.append(c)
syn=make_real(45,1)+make_fmt(['pytest','jest','go','cargo'],6,1)
pm=[]
for i in out+syn:
  j=copy.deepcopy(i);j['checked_span']=r.choice(A.PARA[1:])(j['checked_span'])
  if r.random()<.5: j=A.mask(j)
  j['id']+='-pm';pm.append(j)
allx=out+syn+pm;pos=[x for x in allx if x['label']=='supported'];neg=[x for x in allx if x['label']!='supported'];r.shuffle(pos);r.shuffle(neg)
k=min(len(pos),len(neg),200);train=pos[:k]+neg[:k]
val+=make_real(8,2)
tests={'syn_heldfmt':make_fmt(['junit','custom'],20,3),'syn_trainfmt':make_real(15,4)}  # trainfmt slot = held-out realistic pairs (new seed)
W=lambda n,d:open(f'{H}/{n}.jsonl','w').write('\n'.join(json.dumps(x) for x in d))
W('train',train);W('val',val);[W('test-'+k,v) for k,v in tests.items()];W('test-masked',[A.mask(i) for i in I if S[i['id']]['split']=='test'])
print('train',len(train),collections.Counter((x['origin'],x['label']) for x in train));print('val',len(val),collections.Counter((x['origin'][:10],x['label']) for x in val));print({k:len(v) for k,v in tests.items()})
