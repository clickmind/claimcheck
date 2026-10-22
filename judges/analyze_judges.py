"""Analyze judges run #1 (prereg judges/prereg-r6-judges.md). Writes judges/results.json."""
import json, math, random, sys, os, glob, statistics as st
sys.path.insert(0, '/tmp/bl/baselines/checks')  # check suites from origin/baselines @aea8be2 (git archive)
import nomodel_v2 as V2, nomodel_v3 as V3, nomodel_v3_1 as V31
sys.path.insert(0, '.'); from judges.run_judges_sets import SETS
sys.path.insert(0, 'baselines'); import number_presence as NP
def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return [round(c-h, 3), round(c+h, 3)]
T = lambda g: g == 'supported'
def metr(pairs):  # pairs: (gold, pred)
    t = [p == 'supported' for g, p in pairs if T(g)]; f = [p == 'unsupported' for g, p in pairs if not T(g)]
    r = {'n_true': len(t), 'n_false': len(f)}
    if t: r['true_acc'] = round(sum(t)/len(t), 3); r['true_acc_ci'] = wilson(sum(t), len(t))
    if f: r['catch'] = round(sum(f)/len(f), 3); r['catch_ci'] = wilson(sum(f), len(f)); r['miss_rate'] = round(1-sum(f)/len(f), 3); r['miss_ci'] = [round(1-wilson(sum(f), len(f))[1], 3), round(1-wilson(sum(f), len(f))[0], 3)]
    if t and f: r['bal_acc'] = round((sum(t)/len(t) + sum(f)/len(f))/2, 3)
    return r
def boot(pairs, B=2000):
    rng = random.Random(0); v = []
    for _ in range(B):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]; m = metr(s)
        if 'bal_acc' in m: v.append(m['bal_acc'])
    v.sort(); return [v[int(.025*len(v))], v[int(.975*len(v))-1]] if v else None
out = {'models': {}, 'comparators': {}}
for f in sorted(glob.glob('judges/raw-*.jsonl')):
    model = f[len('judges/raw-'):-6]; R = [json.loads(l) for l in open(f)]
    errs = [r for r in R if 'error' in r]; R = [r for r in R if 'error' not in r]
    import re
    for r in R:  # prereg parse rule: first occurrence of supported/unsupported in the reply
        m_ = re.search(r'unsupported|supported', r['raw'].lower()); r['pred'] = m_.group(0) if m_ else 'unparsed'
    M = {'errors': len(errs), 'unparsed': sum(r['pred'] == 'unparsed' for r in R), 'sets': {}}
    for s in SETS:
        prim = [(r['gold'], r['pred']) for r in R if r['set'] == s and r['rep'] == 0]
        m = metr(prim); m['n_calls_primary'] = len(prim)
        if 'bal_acc' in m: m['bal_acc_ci'] = boot(prim)
        reps = []
        for k in range(1, 9):
            pr = [(r['gold'], r['pred']) for r in R if r['set'] == s and r['rep'] == k]
            mm = metr(pr); reps.append(mm.get('bal_acc', mm.get('catch')))
        reps = [x for x in reps if x is not None]
        if reps: m['repeat_spread'] = {'metric': 'bal_acc' if 'bal_acc' in m else 'catch', 'min': min(reps), 'max': max(reps), 'sd': round(st.pstdev(reps), 3), 'n_repeats': len(reps)}
        # majority vote over all 9 calls
        by = {}
        for r in R:
            if r['set'] == s: by.setdefault(r['id'], []).append(r)
        mv = [(v[0]['gold'], 'unsupported' if sum(x['pred'] == 'unsupported' for x in v) * 2 > len(v) else 'supported') for v in by.values()]
        m['majority9'] = metr(mv)
        M['sets'][s] = m
    out['models'][model] = M
for s, items in SETS.items():
    C = {}
    for name, mod in (('v2', V2), ('v3', V3), ('v3.1', V31)):
        checks = getattr(mod, 'CHECKS', None) or {}
        for cn, fn in checks.items():
            try: pr = [(i['label'], 'supported' if fn(i) == 'supported' else 'unsupported') for i in items]
            except Exception as e: continue
            C[f'{name}:{cn}'] = metr(pr)
    C['number_presence'] = metr([(i['label'], NP.predict(i)) for i in items])
    best = max((k for k in C if 'bal_acc' in C[k]), key=lambda k: C[k]['bal_acc'], default=None)
    out['comparators'][s] = {'best_check': best, 'best': C.get(best), 'all': C}
rj = json.load(open('results/rules.json'))['predictions']; ids = {i['id'] for i in SETS['real77']}
out['comparators']['real77']['rules_v1'] = metr([(p['gold'], p['pred']) for p in rj if p['id'] in ids])
out['spend'] = json.load(open('judges/spend.json'))
json.dump(out, open('judges/results.json', 'w'), indent=1)
for mdl, M in out['models'].items():
    for s, m in M['sets'].items(): print(mdl, s, {k: m.get(k) for k in ('bal_acc', 'bal_acc_ci', 'true_acc', 'catch', 'miss_rate', 'n_calls_primary')}, m.get('repeat_spread'))
for s, c in out['comparators'].items(): print('CMP', s, c['best_check'], c['best'] and c['best'].get('bal_acc'), c['best'] and c['best'].get('catch'), 'rules_v1' in c and c['rules_v1'])
