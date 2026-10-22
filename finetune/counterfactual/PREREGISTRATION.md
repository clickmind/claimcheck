# Pre-registration: counterfactual minimal pairs vs. surface cues

Written and committed **before** any run in this folder. Date: 2026-10-21 (America/Chicago).

## Background
In `../heldout-recipe/` (commit 96f788c), a LoRA Qwen2.5-0.5B caught 72% of planted false claims, but with the
wrong-run recipe (`evidence_swapped`) left out of training, catch on it fell from 87% to 0%. Inflated counts were
never learned (10%). Failed-run claims transferred, most likely through the `[exit 1]` / `failed` strings.

## Hypothesis
H1. Training on counterfactual minimal pairs (same evidence, one detail changed: file in the command, count in the
claim, outcome in the log) plus paraphrased claims and cue-masked evidence (exit line removed, fail/error words
replaced) makes the model compare claim to evidence, so **held-out-recipe catch rises well above the baseline**.

H2. It does so **without hurting true-claim accuracy**.

H3. The baseline's 72% catch **drops on a cue-masked test set**; the counterfactual model drops less.

H4 (exploratory). Adding a short rationale target (quote the evidence line that decides the label) beats label-only.

## Leakage rule
For leave-one-recipe-out (LORO) on recipe R, both the original R items **and** the counterfactual type that mirrors R
(`swap`→file, `count`→count, `fail`→outcome) are removed from training. Only the other two mismatch types remain.
So LORO measures transfer *across* mismatch types, not memorising R. The test set is never augmented.

## Setup (fixed)
Same session-level split (`../split.json`, 142 train / 77 test), same model, LoRA r=16, 3 epochs, lr 2e-4, maxlen 768.
Training sets are capped at 400 items, 200 supported / 200 not (CPU budget), built by `augment.py` (seed 0).
Baseline = the original recipe-only training, re-run here so it also gets the cue-masked test.

## Metrics
- `catch_R` on the held-out recipe R (test items of R; n = 15 swap, 10 count, 13 fail).
- True-claim accuracy on the 38 real supported test items.
- Overall catch on all 39 not-supported items, on the normal and cue-masked test.
95% CIs from a 2000-draw session-level bootstrap.

## Pass / fail (decided now)
- H1 passes if mean held-out catch, averaged over the 3 recipes and the seeds, is **≥ 25 points above baseline**,
  and at least 2 of 3 recipes improve. Fails otherwise.
- H2 passes if true-claim accuracy drops by **≤ 10 points** vs. the in-distribution baseline.
- H3 is confirmed if baseline catch drops by ≥ 15 points on the masked set and the CF model drops by less.
- H4 is reported descriptively (one seed only).
Negative results will be reported as they come out.

## Budget
Hard cap $10 E2B compute; no paid model API calls. Sandbox ids logged in `my-sandboxes.txt`.
