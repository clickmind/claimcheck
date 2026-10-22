# Data card: implicit-v0
- Generator: gen/implicit_counts.py, commit f88902b. Seed: 20261022. Command: `python3 gen/implicit_counts.py 400 20261022`
- File: sets/implicit-v0-seed20261022.jsonl, sha256 df35596704f71f51e97ed2f8027a7ae934aedcc1bad62968120800d058fadeae
- Size: 400 (formats sum_suites 130, fraction 141, implicit 129). Majority-class acc 0.5125.
- Label method: by construction (claimed total vs generated total; or one injected failure).
- Frozen check commit 03a3aca. Scores: majority 0.5125 | number_presence 0.5125 | xy_parser 0.505 | sum_suites 0.515 | last_number 0.5175 | best 0.5175
- Clean: YES under the rule (0.5175 - 0.5125 = 0.005).
- Leakage: claimed total appears verbatim in log in 0/400 items. Generator reads no real data.
- CAVEATS (important): (1) frozen sum_suites regex does not match the "(N tests)" format, so "clean" partly reflects check coverage, not task hardness; a correct summing script would likely solve sum_suites items. (2) "fail" negatives have exit_code 1, which the repo's keyword baseline would catch. Not fixed, to avoid tuning after scoring; proposed for v1 with Lead sign-off.

## Suite v2 (a50a18f) re-score, unchanged set — SUPERSEDES the v1-suite "clean" verdict
ALL 0.8231 (sum_suites_v2) FAIL. fraction 1.0 FAIL; sum_suites 1.0 FAIL; implicit 0.7288 (exit_keyword) FAIL. Table: results-v2.md
