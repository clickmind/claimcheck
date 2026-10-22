# Addendum C.3 — seed-2 audit record and scoring rulings (frozen BEFORE unseal of seed2_labels.jsonl)

## C3.1 Blind hashes on record
- Critic blind set (first 30 rows by offset): sha256 = 9bcf942a57fb0154d9edf924e9221ef66fe91dc646854687057e2a31dc3aef13
  (file saved 12:22:33 CT). The current file /workspace/career/xai/critic/r6-seed2-audit.md now hashes to
  3d710d32d78da98da952b3436aabc2fc74926726e02558b6f7793077564a3066 (mtime 12:23:56 CT) because an "## Addendum: extra rows"
  section was appended. Verified: the first 33 lines of the current file (header + 30 rows + totals, up to the blank line before the
  addendum) hash exactly to 9bcf942a…ef13, so the first-30 content is unchanged.
- World Builder blind labels, all 50 rows: /workspace/claimcheck-lab/seed2-audit/wb_labels.jsonl
  sha256 = 77b3efd180a03fc2660d2a87b4b3040e2e4303421479ef624bc95b1979e32c05 (verified).
- Sealed labeler v3 output seed2_labels.jsonl expected sha256 = 7c8da9a6dcbc48f4c5ad7bdb84879d36d477ec5283afc8432fe076d50683c431 (not opened at commit time).

## C3.2 Rulings
(a) Gate agreement: two labels agree iff they match on claim vs no_claim AND on seen-contradicted vs not. False vs unverifiable (C5.2/C5.3)
    needs target/eval_logs, so it is scored separately as labeler vs target, not in the gate. Gate passes iff >= 48/50.
(b) Blindness: only Critic's first 30 rows (9bcf942a…ef13) are blind and enter kappa. Critic's appended rows (54351, 66868, 66876, 67336,
    68860, 79422, 79534) were labeled after the World Builder posted rows 17/40/42 and its ambiguous-row list in the room (~12:23 CT), so they are
    UNBLINDED: reported separately, excluded from kappa; disagreements there go to a third reader (Lead, logged as self-review).
    Any rows added after unseal: WB blind label is the reference; Critic labels on them are an unblinded supplement, excluded from agreement.
(c) Seen-contradicted dimension takes values {contradicted, not, ambiguous}. When auditors split, the adjudicated label is the weaker one
    (not contradicted).
(d) The headline seen-contradicted count is tiny (1-3 in 50 in dev). It is reported as a count with a Wilson 95% CI, not as a rate claim,
    unless the final seed yields >= 15 claim rows.
(e) UNSUPPORTED_VERIFICATION is pre-registered in addendum-D.md.
