# Data card: implicit-v1 — REJECTED
- Pre-registration + generator: gen/PREREG-implicit-v1.md, gen/implicit_counts_v1.py, commit 5dd630f. Seed 20261023, N=400.
- File: sets/implicit-v1-seed20261023.jsonl sha256 acb2eddf72904f07ccb27d74b21ca8e11535bb96e256c089a01efe3e1556f81d
- Families: fraction 109, implicit 147, sum_suites 144. Labels 207 supported / 193 not. Verbatim total in log: 0/400.
- Exit balance |P(exit0|sup)-P(exit0|not)|: ALL 0.095, fraction 0.116 (VIOLATES <=0.10 -> set rejected per prereg), implicit 0.089, sum_suites 0.084.
- Suite v2 BA: ALL best 0.6812 (sum_suites_v2) FAIL; fraction 0.7881 FAIL; sum_suites 0.7635 FAIL; implicit 0.5443 (exit_keyword) PASS.
- Prediction in prereg (sum/fraction fail, implicit may pass) held.
- Caveat: exit drawn i.i.d. 50/50 per item, so per-family balance is not guaranteed at n~110; a v2 should stratify exit code within (family,label).
