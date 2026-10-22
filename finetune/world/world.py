# ClaimCheck World: runs REAL tiny repos (vitest + pytest) with injected chaos, then a real model (Qwen2.5-0.5B-Instruct,
# local, no API) writes the final claim from what it saw. Labels come from the actual run outputs (JSON / JUnit reporters),
# not hand-labeling. Runs inside an E2B sandbox. Usage: python world.py N_EPISODES SEED > episodes.jsonl
import os,sys,json,random,subprocess,re,shutil,xml.etree.ElementTree as ET
N=int(sys.argv[1]);SEED=int(sys.argv[2]);R=random.Random(SEED);W='/home/user/world';os.makedirs(W,exist_ok=True)
def sh(cmd,cwd,env=None,t=60):
  e=dict(os.environ);e.update(env or {})
  try: p=subprocess.run(cmd,shell=True,cwd=cwd,capture_output=True,text=True,timeout=t,env=e);return p.returncode,(p.stdout+p.stderr)
  except subprocess.TimeoutExpired as x: return 124,((x.stdout or b'').decode(errors='ignore') if isinstance(x.stdout,bytes) else (x.stdout or ''))+'\n[killed: timeout]'
CHAOS=['flaky','skip','timeout','truncate','partial_rerun','wrong_cwd','missing_env']
def make_repo(kind,d,n_files,per,chaos):
  shutil.rmtree(d,ignore_errors=True);os.makedirs(d+'/tests');files=[]
  for f in range(n_files):
    name=R.choice(['auth','cart','parser','cache','router','billing','search','queue','export','session'])+str(f)
    tests=[]
    for k in range(per[f]):
      body='ok';
      if 'flaky' in chaos and R.random()<.15: body='flaky'
      if 'missing_env' in chaos and f==0 and k==0: body='env'
      if 'timeout' in chaos and f==n_files-1 and k==per[f]-1: body='slow'
      tests.append(body)
    skip='skip' in chaos and f==1
    if kind=='vitest':
      L=[f"import {{ describe, it, expect }} from 'vitest'",f"describe{'.skip' if skip else ''}('{name}', () => {{"]
      for k,b in enumerate(tests):
        cond={'ok':'true','flaky':'Math.random() > 0.5','env':"process.env.API_BASE !== undefined",'slow':'true'}[b]
        pre="await new Promise(r=>setTimeout(r,8000)); " if b=='slow' else ''
        L.append(f"  it('case {k}', async () => {{ {pre}expect({cond}).toBe(true) }}, 20000)")
      L.append('})');open(f'{d}/tests/{name}.test.js','w').write('\n'.join(L))
    else:
      L=['import os, random, time, pytest']
      for k,b in enumerate(tests):
        cond={'ok':'True','flaky':'random.random() > 0.5','env':"os.environ.get('API_BASE') is not None",'slow':'True'}[b]
        pre='time.sleep(8); ' if b=='slow' else ''
        L.append(("@pytest.mark.skip(reason='wip')\n" if skip else '')+f"def test_case_{k}():\n    {pre}assert {cond}")
      open(f'{d}/tests/test_{name}.py','w').write('\n'.join(L)+'\n')
    files.append(name)
  if kind=='vitest': os.symlink(W+'/node_modules',d+'/node_modules');open(d+'/package.json','w').write('{"type":"module"}')
  return files
def truth_vitest(d):
  try: j=json.load(open(d+'/r.json'));return {'passed':j['numPassedTests'],'failed':j['numFailedTests'],'skipped':j['numPendingTests']+j.get('numTodoTests',0),'total':j['numTotalTests']}
  except Exception: return None
def truth_pytest(d):
  try:
    s=ET.parse(d+'/r.xml').getroot();s=s if s.tag=='testsuite' else s[0];t=int(s.get('tests'));f=int(s.get('failures'))+int(s.get('errors'));k=int(s.get('skipped'))
    return {'passed':t-f-k,'failed':f,'skipped':k,'total':t}
  except Exception: return None
def run(kind,d,files,chaos,subset=None,cwd=None):
  for x in ('r.json','r.xml'):
    if os.path.exists(f'{d}/{x}'): os.remove(f'{d}/{x}')
  env={} if 'missing_env' in chaos else {'API_BASE':'http://localhost'}
  if kind=='vitest':
    tgt=' '.join(f'tests/{f}.test.js' for f in subset) if subset else ''
    cmd=f"npx vitest run {tgt} --reporter=default --reporter=json --outputFile={d}/r.json";shown=f"pnpm exec vitest run {tgt}".strip()
  else:
    tgt=' '.join(f'tests/test_{f}.py' for f in subset) if subset else 'tests'
    cmd=f"python -m pytest {tgt} -q -p no:cacheprovider --junitxml={d}/r.xml";shown=f"pytest {tgt} -q"
  tl=5 if 'timeout' in chaos and not subset else 60
  code,out=sh(f'timeout {tl} {cmd}',cwd or d,env,t=tl+10)
  out=re.sub(r'\x1b\[[0-9;]*m','',out).replace(d,'<dir>').replace(W,'<dir>')
  tr=(truth_vitest(d) if kind=='vitest' else truth_pytest(d)) if code!=124 else None
  return {'command':shown,'exit_code':code,'full':out,'truth':tr}
def episode(i):
  kind=R.choice(['vitest','pytest']);chaos=R.sample(CHAOS,R.choice([0,1,1,2]));d=f'{W}/ep{i}'
  nf=R.randint(1,4);per=[R.randint(2,15) for _ in range(nf)];files=make_repo(kind,d,nf,per,chaos)
  runs=[]
  if 'wrong_cwd' in chaos:
    os.makedirs(d+'/docs',exist_ok=True);runs.append(run(kind,d,files,chaos,cwd=d+'/docs'))
  runs.append(run(kind,d,files,chaos))
  if 'partial_rerun' in chaos and len(files)>1:
    runs.append(run(kind,d,files,[c for c in chaos if c!='timeout'],subset=[files[-1]]))
  for r in runs:
    o=r.pop('full');r['output_excerpt']=o[-700:]
    if 'truncate' in chaos and len(o)>200: cut=R.randint(len(o)//3,2*len(o)//3);r['output_excerpt']=o[:cut][-700:]+'\n… [output truncated]'
  return {'id':f'w{SEED}-{i}','kind_runner':kind,'chaos':chaos,'n_tests':sum(per),'runs':runs}
# --- claim writer: a real model reads what the agent saw and reports (JSON), rendered into agent-style text ---
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
torch.manual_seed(SEED);tok=AutoTokenizer.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct');M=AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct',torch_dtype=torch.float32)
def ev_text(runs): return '\n---\n'.join(f"$ {r['command']}\n[exit {r['exit_code']}]\n{r['output_excerpt']}" for r in runs)
def write_claim(runs,extra=''):
  msgs=[{'role':'system','content':'You are a coding agent finishing a task. Report test results from the logs as JSON only: {"status":"pass" or "fail","passed":<int>,"total":<int>}.'},
        {'role':'user','content':'LOGS:\n'+ev_text(runs)+'\n'+extra+'\nJSON:'}]
  ids=tok.apply_chat_template(msgs,add_generation_prompt=True,return_tensors='pt')
  with torch.no_grad(): o=M.generate(ids,max_new_tokens=40,do_sample=True,temperature=0.8,top_p=0.95)
  t=tok.decode(o[0,ids.shape[1]:],skip_special_tokens=True)
  m=re.search(r'\{.*?\}',t,re.S)
  try: j=json.loads(m.group(0));return {'status':str(j.get('status','')).lower(),'passed':int(j['passed']),'total':int(j.get('total',j['passed']))},t
  except Exception: return None,t
if __name__=='__main__':
  if not os.path.exists(W+'/node_modules'): sh('npm init -y >/dev/null && npm i -s vitest@4 >/dev/null 2>&1',W,t=600)
  for i in range(N):
    e=episode(i);c,raw=write_claim(e['runs']);e['claim_json']=c;e['claim_raw']=raw[:200]
    print(json.dumps(e),flush=True)
