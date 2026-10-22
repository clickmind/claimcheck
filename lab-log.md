# ClaimCheck lab log

Created 2026-10-22. No earlier lab-log.md existed in this repo or in /workspace/claimcheck-lab. The "0.86 kappa unverifiable" line was not found in either place, so its correction is recorded here.

## Audit verification

- **Seed-2 WB vs Critic claim kappa 0.862 [0.645, 1.0]: VERIFIED** (this replaces any earlier note calling it unverifiable). The first 34 lines of `r6/audits/r6-seed2-audit.md` hash to sha256 `9bcf942a57fb0154d9edf924e9221ef66fe91dc646854687057e2a31dc3aef13`. That is identical to the sha256 of `r6/audits/r6-seed2-audit-first30.md`. Both files were committed at 988b225. Re-checked 2026-10-22 13:40 CT with `head -34 r6/audits/r6-seed2-audit.md | sha256sum`. Cos also verified this independently. (Cos's earlier 33-line check gave 0064537f. The correct prefix length is 34 lines.)

## Spend

- **Judge/labeler cap: $10 total for grok-4.20. Hard cap, shared, logged per call.** John approved directly (DM, 2026-10-22 12:45 CT, replying "yes" to whether the $10 judge approval can also cover model labeling). Cos relayed the same confirmation at 13:33 CT. Model labeling and the judge run share one running total. Addendum E reserves at least $6 for the judge run, so labeling stops at $4.
- **E2B series cap: $100.** John said so directly in the room at 2026-10-22 12:16 CT ("lets set to $100").
- **Spend so far (E2B), for budgeting: $13.80.** Repo ledgers show $7.31. career/xai/spend-ledger.md shows about $13.44–13.80. John quoted $8.18. About $0.24 is untraced. At least $0.63 of the gap traces to rounds d1e34ff and 96f788c. The total stays unsettled until it is checked in the E2B console. Remaining E2B headroom: $100 − $13.80 = $86.20, or at most $76.20 after holding a $10 reserve.
- grok-4.20 spend so far against the $10 cap: $0 recorded here. The per-call log starts at `r6/spend/labeler-judge-spend.jsonl` (Addendum E).
