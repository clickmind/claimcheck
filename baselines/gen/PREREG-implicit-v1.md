# Pre-registration: implicit-v1 (committed BEFORE generation). Oct 22, 2026 CT.
- Generator: gen/implicit_counts_v1.py (this commit). Seed 20261023. N=400. Command: `python3 gen/implicit_counts_v1.py 400 20261023 > sets/implicit-v1-seed20261023.jsonl`
- Only fix vs v0: exit code drawn 50/50 for EVERY item, independent of label and family.
  - fake 'fail' with exit 0: command piped `|| true`. True claim with exit 1: a post-test coverage step exits 1 ("coverage threshold for branches (80%) not met"; tests themselves all pass).
  - Hard requirement, checked per family: |P(exit0|supported) - P(exit0|not)| <= 0.10. If violated the set is rejected, not regenerated with a new seed.
- Nothing else changed (formats, counts, wording). Not tuned against any check.
- Scored once with frozen suite v2 (a50a18f). Gate: best BA - 0.5 <= 0.10 on whole set and each family.
- Prediction (written before running): sum_suites and fraction families will FAIL, because sum_suites_v2 adds the per-suite counts that the generator prints; implicit (✓-line) family may pass.
