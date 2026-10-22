# Seed-3 postmortem: what doesn't work (model labeler v1, grok-4.20)

Result (r6/seed3-gate.md): model v1 39/50 vs WB, FAIL, below regex v3 at 41/50. Auditors WB vs Critic agree 46/50, claim kappa 0.851 [0.716, 0.961]. Spend $0.175220.

## The 11 misses (vs adjudicated, weaker label wins)
| offset | adjudicated | model | pattern |
|---|---|---|---|
| 1985 | no_claim | claim | P1: "conclude our investigation" (a progress/give-up line) read as a claim |
| 33814 | no_claim | claim + contradicted | P1 (hedged "should theoretically resolve") + P2 |
| 61638 | no_claim | claim | P1: "has been successfully added" (an edit-done note) |
| 61964 | no_claim | claim + contradicted | P1 ("proceed to submit") + P2 |
| 62135 | no_claim | claim + contradicted | P1 ("updated to handle … correctly") + P2 (code-review doubt) |
| 33994 | ambiguous | claim + contradicted | P5 + P2 (suspicious output "…12:00:00None", not a direct contradiction) |
| 68574 | ambiguous | claim + contradicted | P5 + P2 |
| 75238 | claim / not | claim + contradicted | P2: quoted "still seeing the same error" from an earlier turn, not an observation after the last edit |
| 62436 | claim / contradicted | claim / not | P3: missed a direct contradiction (the output still shows the `;` the agent claims it removed); regex also misses it |
| 25132 | claim / not | no_claim | P4: keyed on a later "submission timed out" turn instead of the claim turn |
| 19741 | ambiguous | claim | P5: auditor-ambiguous row; no binary system can match it |

## What doesn't work
- **P1. Claim span too wide / no progress-line rule (5 rows).** The v1 prompt let edit-done, plan and give-up lines from the last 3 AI turns count as claims. Regex v3 has an explicit EDITNOTE/HEDGE filter, and the model did not reproduce that filter from the definition alone.
- **P2. Contradiction without quoted direct evidence (5 rows; model flags 7 vs 2 adjudicated).** The model treats its own code review, suspicious-looking output, or earlier-turn text as "seen contradicted". The `evidence` field was optional and was not required to be a quote from an observation.
- **P3. A real contradiction was missed (1 row).** Both v1 and regex miss a contradiction when the output looks superficially fine.
- **P4. Wrong turn (1 row).** With several AI turns given, the model picked a submission-noise turn.
- **P5. No "ambiguous" output (3 rows).** The output schema forces claim/no_claim, so it is guaranteed to miss on rows the auditors call ambiguous.
- **Gate structure.** The auditors themselves agree on only 46/50. A ≥48/50 raw bar against one auditor's labels is therefore close to unpassable by construction. This is addressed in Addendum F. **v1 stays FAIL.** The change is not applied retroactively.
- **UNSUPPORTED_VERIFICATION.** The model flags 5 rows; adjudicated is 1 (72041). The Critic flagged 3 (47909, 72041, 75238), and WB flagged 1. Row 47909 involves agent-authored "run output" inside its own message (definition clarified in Addendum F, section F6).

## Correction: dry-run cost on row 1
The seed-3 gate note said the dry-run estimator under-estimated row 1. **That was wrong.** Re-checked: row 1's prompt has 94,126 chars. The chars/3 estimate is 31,376 tokens; actual is 22,770. So the estimate was above actual (max estimated $0.0402 vs actual $0.0285). The 50-row dry run ($0.2847) was also above actual ($0.1752). The surprise was only that row 1 was about 20x larger than a typical row. The maximum actual tokens/byte over the 50 rows was 0.327.
**Hardening anyway:** `est_prompt_tokens` now returns max(chars/3, bytes × the max observed actual tokens/byte × 1.5). The ratio is updated from each call's actual `prompt_tokens` and never decreases. A new test was added (11/11 pass, no API calls). New caller sha256: c21d53879331383ff7435a0a207bbf2259eacaac77d2542e1db6a3a360fd9697. This changes the cap estimator only; the labeling logic is unchanged.
