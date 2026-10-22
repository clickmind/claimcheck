# Pre-registration: a count-mismatch family across log formats, with a true-claim guardrail

Written and committed **before** any training in this folder. Date: 2026-10-22 (America/Chicago).

## Background
In `../counterfactual/` (commit fa2aed9), counterfactual pairs taught the 0.5B model to catch a held-out wrong-run
recipe (0.00 → 0.87 / 0.60), but counting never transferred (0.10 / 0.30 held out), and one seed collapsed on true
claims (0.24). This round targets both problems.

## Design
- **Synthetic count family** (`gen_count.py`): minimal pairs with the same log and a claim that states either the
  true count (supported) or a wrong one (unsupported). Six formats: pytest, jest, go test (`--- PASS` lines, count is
  implicit), cargo, JUnit XML, custom key=value. Logs carry distractor numbers (durations, warnings, snapshots, skipped).
- **Train formats:** pytest, jest, go, cargo (80 pairs). **Held-out formats:** JUnit XML, custom (40 pairs, never trained).
- **Held-out families:** the real vitest `count_inflated` recipe and the real `evidence_swapped` (wrong run) recipe are
  both removed from training, and so are their counterfactual mirrors. Training keeps real supported claims, real
  failed-run claims, failed-run counterfactuals and the synthetic count pairs, plus paraphrase / cue-masked copies.
  Training is capped at 400 items, 200 / 200 (balanced loss by construction).
- **Validation set** (for checkpoint selection only): 11 of 55 train sessions (20%, seed 0) are held aside, giving 19 real
  supported + 5 failed-run items, plus 20 in-format synthetic count pairs. Nothing from the test split.
- **Early stopping rule (fixed now):** evaluate after epochs 1, 2, 3. Pick the epoch with the best val balanced accuracy
  among epochs with val true-claim accuracy ≥ 0.95. If none qualifies, pick the epoch with the highest val true-claim
  accuracy. Test numbers are read only at the selected epoch.
- **Seeds:** 4 (0–3). Same model (Qwen2.5-0.5B-Instruct), LoRA r=16, lr 2e-4, maxlen 768.
- Same 77-item session-level test split and same cue-stripped test as before. 95% CIs from session-level bootstrap.

## Hypotheses and pass thresholds (selected epoch, averaged over seeds unless noted)
- **H1, real count transfer:** catch on real vitest inflated counts (n=10) ≥ 0.50. Prior held-out: 0.10 / 0.30.
- **H2, format transfer:** on held-out formats (JUnit, custom), catch ≥ 0.80 **and** true-claim accuracy ≥ 0.90.
- **H3, guardrail:** real true-claim test accuracy ≥ 0.95 on average, and no seed below 0.90. Reported per seed.
- **H4, wrong run still transfers:** catch on real wrong-run claims (n=15, held out) ≥ 0.60.
- **H5, cues:** catch on all false claims drops ≤ 10 points from normal to cue-stripped test.
- **H6, stability:** spread of real true-claim accuracy across seeds ≤ 10 points.
Each is pass/fail as written. Negative results will be reported plainly.

## Budget
Hard cap about $4.80 E2B (total experiment cap $10). No paid model APIs. Sandbox ids in `my-sandboxes.txt`.
