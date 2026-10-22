# Data card: real v1.2 (existing)
- File: claimcheck-public/data/claims.jsonl, 219 items; split finetune/split.json 142/77 by 89 sessions.
- Frozen check commit 03a3aca. All 219: majority 0.5023 | number_presence 0.8219 | xy_parser 0.8219 | sum_suites 0.5251 | last_number 0.6164 | best 0.8219 -> NOT clean.
- Test 77: majority 0.5065 | number_presence 0.8312 | xy_parser 0.8312 | sum_suites 0.4416 | last_number 0.5844. Train 142: 0.5 | 0.8169 | 0.8169 | 0.5704 | 0.6338.

## Suite v2 (a50a18f), balanced accuracy, gate best-0.5<=0.10 — see results-v2.md
ALL 219: best 0.8218 (number_presence) FAIL. test 77: 0.831 FAIL. train 142: 0.8169 FAIL.
Families: count_inflated/evidence_swapped/run_failed FAIL in all/test/train (single-class: BA = recall on fakes; majority would also be 1.0 there). real: PASS in all (0.5) and test (0.5); FAIL in train (single-class, exit_keyword 1.0).
