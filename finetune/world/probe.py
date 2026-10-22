import os,time
from e2b import Sandbox
H=os.path.dirname(os.path.abspath(__file__))
sb=Sandbox.create('claimcheck-ml',timeout=900);t0=time.time();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} probe created {time.strftime("%H:%M:%S")}\n')
try:
  for c in ['which node npm python; node -v; python -V','pip install -q pytest 2>&1|tail -1; python -m pytest --version','curl -sI https://registry.npmjs.org | head -1']:
    r=sb.commands.run(c,timeout=300);print(r.stdout[-500:],r.stderr[-300:])
except Exception as e: print('ERR',str(e)[:300])
finally: sb.kill();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} probe killed {time.strftime("%H:%M:%S")} after {int(time.time()-t0)}s\n')
