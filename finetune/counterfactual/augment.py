# Build counterfactual minimal-pair training sets + cue-masked test variants. Train split only; test is never augmented.
# Usage: python augment.py  -> writes data-*.jsonl and test-masked.jsonl
import json,re,random,copy,os
H=os.path.dirname(os.path.abspath(__file__));F=os.path.dirname(H)
I=[json.loads(l) for l in open(f'{F}/../data/claims.jsonl')];S=json.load(open(f'{F}/split.json'))
REC={'swap':'perturbed:evidence_swapped','count':'perturbed:count_inflated','fail':'perturbed:run_failed'}
TESTS=re.compile(r'Tests +(\d+) passed \((\d+)\)')
def mask(e):  # remove the two strongest surface cues: the exit line and failure words
  e=copy.deepcopy(e)
  for x in e['evidence']:
    x['exit_code']=None
    x['output_excerpt']=re.sub(r'(?i)\b(failed|failing|fail|failures?|errors?)\b','·',x['output_excerpt'])
  e['evidence_note']=re.sub(r'(?i)\b(failed|fail|exit(ed)? \d+)\b','·',e['evidence_note']);return e
PARA=[lambda s:s,lambda s:'Checked: '+s,lambda s:s.replace('passed','green').replace('exit 0','clean exit'),lambda s:'Result — '+s.lower(),lambda s:s+' (verified locally)']
def cf_swap(i,r):  # same evidence, but the run is of a different file than the claim names
  if not re.search(r'file\d',i['checked_span']): return None  # claim must name the file, else the swap might still be supported
  j=copy.deepcopy(i);k=r.randint(5,9)
  for x in j['evidence']: x['command']=re.sub(r'file(\d)',lambda m:f'file{int(m.group(1))+k}',x['command'])
  if j['evidence']==i['evidence']: return None
  j['label']='unsupported';j['why']=f"$ {j['evidence'][0]['command'][:160]}";return j
def cf_count(i,r):  # same evidence, claim count changed
  for x in i['evidence']:
    m=TESTS.search(x['output_excerpt'])
    if m and re.search(rf'\b{m.group(1)}\b',i['checked_span']):
      n=int(m.group(1));d=n+r.choice([1,2,3,5,max(2,n//4)]);j=copy.deepcopy(i)
      j['checked_span']=re.sub(rf'(?<![\d.:<>/]){n}(?![\d.:])',str(d),i['checked_span'],count=1)
      if j['checked_span']==i['checked_span']: return None
      j['label']='unsupported';j['why']=m.group(0);return j
  return None
def cf_fail(i,r):  # same claim, evidence edited so the run failed
  j=copy.deepcopy(i);hit=False
  for x in j['evidence']:
    m=TESTS.search(x['output_excerpt'])
    if m and int(m.group(1))>1:
      n=int(m.group(1));f=r.randint(1,min(3,n-1))
      x['output_excerpt']=x['output_excerpt'].replace(m.group(0),f'Tests  {f} failed | {n-f} passed ({n})');x['exit_code']=1;hit=f'Tests  {f} failed | {n-f} passed ({n})'
  if not hit: return None
  j['label']='unsupported';j['why']=hit;return j
CF={'swap':cf_swap,'count':cf_count,'fail':cf_fail}
def why_pos(i):
  for x in i['evidence']:
    m=TESTS.search(x['output_excerpt'])
    if m: return m.group(0)
  return f"$ {i['evidence'][0]['command'][:160]} [exit {i['evidence'][0]['exit_code']}]" if i['evidence'] else '(none)'
def why_orig(i):
  if i['origin']==REC['count']:
    for x in i['evidence']:
      m=TESTS.search(x['output_excerpt'])
      if m: return m.group(0)
  if i['origin']==REC['fail']:
    for x in i['evidence']:
      m=re.search(r'Tests? +\d+ failed[^\n]*',x['output_excerpt'])
      if m: return m.group(0)
    return f"[exit {i['evidence'][0]['exit_code']}]" if i['evidence'] else '(none)'
  return f"$ {i['evidence'][0]['command'][:160]}" if i['evidence'] else '(none)'
def build(exclude,seed=0):
  r=random.Random(seed);out=[]
  tr=[i for i in I if S[i['id']]['split']=='train' and not (exclude and i['origin']==REC[exclude])]
  for i in tr:
    j=copy.deepcopy(i);j['label']='supported' if i['label']=='supported' else 'unsupported';j['why']=why_pos(i) if j['label']=='supported' else why_orig(i);out.append(j)
  for i in [i for i in tr if i['origin']=='real' and i['label']=='supported']:
    for k,fn in CF.items():
      if k==exclude: continue
      c=fn(i,r)
      if c: c['id']=i['id']+'-cf'+k;c['origin']='cf:'+k;out.append(c)
  # paraphrase + cue-mask copies (label preserved): a random half of everything gets masked evidence, all get a random paraphrase
  aug=[]
  for i in out:
    j=copy.deepcopy(i);j['checked_span']=r.choice(PARA[1:])(j['checked_span'])
    if r.random()<.5: j=mask(j)
    j['id']+='-pm';aug.append(j)
  allx=out+aug;pos=[x for x in allx if x['label']=='supported'];neg=[x for x in allx if x['label']!='supported']
  # balance classes and cap size (CPU budget): 200 supported (originals + paraphrase/mask copies, extra paraphrases if short), 200 not
  while len(pos)<N//2:
    j=copy.deepcopy(r.choice([x for x in out if x['label']=='supported']));j['checked_span']=r.choice(PARA[1:])(j['checked_span'])
    if r.random()<.5: j=mask(j)
    j['id']+='-pp%d'%len(pos);pos.append(j)
  r.shuffle(pos);r.shuffle(neg);return pos[:N//2]+neg[:N//2]
N=400
if __name__=='__main__':
  for ex in ['','swap','count','fail']:
    d=build(ex);open(f'{H}/data-{ex or "all"}.jsonl','w').write('\n'.join(json.dumps(x) for x in d))
    import collections;print(ex or 'all',len(d),collections.Counter((x['origin'],x['label']) for x in d))
  te=[mask(i) for i in I if S[i['id']]['split']=='test'];open(f'{H}/test-masked.jsonl','w').write('\n'.join(json.dumps(x) for x in te))
