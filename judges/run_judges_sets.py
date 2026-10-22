import json
def load(f): return [json.loads(l) for l in open(f) if l.strip()]
split = json.load(open('finetune/split.json'))
SETS = {'real77': [x for x in load('data/claims.jsonl') if split.get(x['id'], {}).get('split') == 'test'],
        'masked77': load('finetune/realistic-count/test-masked.jsonl'),
        'heldout80': load('finetune/realistic-count/test-syn_heldfmt.jsonl'),
        'trainfmt33': load('finetune/realistic-count/test-syn_trainfmt.jsonl'),
        'family41': load('finetune/scale-family/test-family.jsonl'),
        'xcount30': load('finetune/scale-family/test-xcount.jsonl')}
