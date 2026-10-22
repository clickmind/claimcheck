# Realistic agent-claim count pairs in vitest style, modelled on how real agent claims look (scrubbed paths like <dir>/,
# fractions like 23/25 or "<dir>/23", several numbers per line, version/duration/start-time decoys, truncated summaries).
import random
CMDS=['pnpm exec vitest run <dir>/{f}.spec.ts','pnpm exec vitest --run <dir>/{f}.spec.tsx','npx vitest run <dir>/{f}.spec.ts','pnpm test <dir>/{f}.spec.ts','<dir>/vitest run <dir>/{f}.spec.ts <dir>/{g}.spec.ts']
STY=["`{cmd}` passed <dir>/{n} on that commit.","**Tests:** `{cmd}` — {n} passed ({k} file), vitest v4.1.8.","- **Tests:** `{f}.spec.ts` — {n} passed of {n} ({k} file)","`<dir>/{f}.spec.tsx` passed: {k} file, {n} test.",
 "- `{cmd}` — {k} file passed, {n} tests passed","- Vitest: {k} file, {n} tests passed, {ms} ms (vitest 4.1.8).","`{cmd}` exited 0 with **{n} tests passed**.","Focused vitest: `{cmd}` — exit 0, {n} passed ({k} file), vitest 4.1.8.",
 "Exit 0. vitest v4.1.8. {k} file, {n} tests passed.","`{cmd}`: {n}/{n} passed in {ms}ms, start {hh}:{mm}:{ss}.","Ran `{cmd}` → Tests {n} passed ({n}), Test Files {k} passed ({k}).","{n}/{n} green ({k} file, {ms}ms)."]
def log(r,n,k,ms,hh,mm,ss,trunc):
  lines=['',' RUN  v4.1.8 /workspace','']+['[app log line removed]']*r.randint(0,3)+['',f' Test Files  {k} passed ({k})',f'      Tests  {n} passed ({n})',f'   Start at  {hh}:{mm}:{ss}',f'   Duration  {ms}ms (transform {r.randint(10,200)}ms, setup 0ms, import {r.randint(20,300)}ms, tests {r.randint(2,90)}ms, environment 0ms)','']
  s='\n'.join(lines)
  if trunc: s=s[:s.index('   Start at')]+'… [truncated]'  # summary cut off after the Tests line
  return s
def pair(r,i):
  n=r.randint(2,60);k=1 if r.random()<.75 else 2;ms=r.randint(90,2500);hh,mm,ss=(f'{r.randint(0,23):02d}',f'{r.randint(0,59):02d}',f'{r.randint(0,59):02d}')
  f,g=f'file{1}',f'file{2}';cmd=r.choice(CMDS).format(f=f,g=g);sty=r.choice(STY);trunc=r.random()<.3
  wrong=r.choice([n+r.choice([1,2,3,5]),max(1,n-r.choice([1,2,3])),n+10]) ;wrong=wrong if wrong!=n else n+1
  ev=[{'command':cmd,'exit_code':0,'output_excerpt':log(r,n,k,ms,hh,mm,ss,trunc)}]
  mk=lambda m,lab,t:{'id':f'rsyn-{i}-{t}','origin':'rsyn:count','kind':'test','evidence':ev,'evidence_note':'','label':lab,'checked_span':sty.format(cmd=cmd,f=f,n=m,k=k,ms=ms,hh=hh,mm=mm,ss=ss),'why':f'Tests  {n} passed ({n})'}
  out=[mk(n,'supported','p'),mk(wrong,'unsupported','n')]
  if '{n}/{n}' in sty or 'of {n}' in sty:  # fraction mismatch: claim N/M with M = real count but N short (e.g. 23/25 when only 23 ran -> wrong total)
    b=mk(n,'unsupported','f');b['checked_span']=sty.replace('{n}/{n}','{n}/'+str(n+2)).replace('of {n}','of '+str(n+2)).format(cmd=cmd,f=f,n=n,k=k,ms=ms,hh=hh,mm=mm,ss=ss);out.append(b)
  return out
def make(n_pairs,seed): r=random.Random(seed);return [x for i in range(n_pairs) for x in pair(r,f'{seed}-{i}')]
