# Runs train.py inside an E2B sandbox. Reads E2B_API_KEY from env (never printed).
import sys,os,time
from e2b import Sandbox
model=sys.argv[1] if len(sys.argv)>1 else 'Qwen/Qwen2.5-0.5B-Instruct'; tag=sys.argv[2] if len(sys.argv)>2 else 'q05'; extra=' '.join(sys.argv[3:])
sb=Sandbox.create('claimcheck-ml',timeout=3600); open('my-sandboxes.txt','a').write(sb.sandbox_id+' '+tag+'\n'); print('sandbox',sb.sandbox_id,flush=True)
try:
  for f in ['train.py','../data/claims.jsonl','split.json']: sb.files.write('/home/user/w/'+os.path.basename(f),open(f,'rb').read())
  r=sb.commands.run('nproc; free -g | head -2'); print(r.stdout)
  h=sb.commands.run(f'cd /home/user/w && python train.py --model {model} --out out {extra} > log.txt 2>&1',background=True,timeout=0)
  t0=time.time()
  while True:
    time.sleep(60); lg=sb.files.read('/home/user/w/log.txt'); print(int(time.time()-t0),'s |',lg.strip().splitlines()[-1][:200] if lg.strip() else '',flush=True)
    if lg.strip().splitlines()[-1].startswith('done ') or 'Error' in lg or 'Traceback' in lg or time.time()-t0>3300: break
  os.makedirs(f'out-{tag}',exist_ok=True)
  for f in ['pred-zeroshot.json','pred-finetuned.json','meta.json','log.txt']:
    try: open(f'out-{tag}/{f}','w').write(sb.files.read(f'/home/user/w/out/{f}' if f!='log.txt' else '/home/user/w/log.txt'))
    except Exception as e: print('missing',f)
finally: sb.kill()
