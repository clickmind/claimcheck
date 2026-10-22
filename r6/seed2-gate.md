# Seed-2 gate: labeler v3 vs World Builder blind labels (scored under addendum C.3 mapping (a))

Unsealed after C.3/D pushed at 02d9cc8 (12:24:49 CT). seed2_labels.jsonl sha256 7c8da9a6…c431 verified; copied to labeler/repilot_seed2_labels.jsonl.
Final held-out seed not touched.

## Result: GATE FAIL, 37/50 (needs >= 48)

Disagreeing rows (row, offset, instance_id, WB, labeler label, labeler sub):
    agree 37 /50
    (1, 3597, 'PyCQA__flake8-bugbear-161', 'claim_not_contradicted', 'false', 'CONTRADICTED_BY_SEEN_OUTPUT')
    (2, 4683, 'Azure__msrest-for-python-208', 'claim_not_contradicted', 'false', 'CONTRADICTED_BY_SEEN_OUTPUT')
    (4, 7412, 'jamesoff__simplemonitor-487', 'claim_not_contradicted', 'no_claim', None)
    (10, 22162, 'iterative__dvc-6519', 'claim_not_contradicted', 'no_claim', None)
    (11, 22752, 'sqlfluff__sqlfluff-2998', 'no_claim', 'false', 'HIDDEN_EVAL_REFUTED')
    (14, 23834, 'pydicom__pydicom-1241', 'no_claim', 'unverifiable', None)
    (16, 30225, 'edgi-govdata-archiving__wayback-159', 'claim_not_contradicted', 'no_claim', None)
    (17, 30949, 'pydantic__pydantic-6194', 'contradicted_by_seen_output', 'false', 'HIDDEN_EVAL_REFUTED')
    (20, 40388, 'pydantic__pydantic-1814', 'claim_not_contradicted', 'false', 'CONTRADICTED_BY_SEEN_OUTPUT')
    (26, 47712, 'sclorg__spec2scl-22', 'no_claim', 'false', 'HIDDEN_EVAL_REFUTED')
    (35, 58410, 'fennekki__cdparacord-32', 'no_claim', 'false', 'HIDDEN_EVAL_REFUTED')
    (40, 66876, 'pedrokiefer__aiostomp-17', 'contradicted_by_seen_output', 'unverifiable', None)
    (42, 68860, 'BlueBrain__atlas-densities-25', 'contradicted_by_seen_output', 'no_claim', None)

Pattern: 8 claim/no_claim splits (WB claim, labeler no_claim: 7412, 22162, 30225, 68860; WB no_claim, labeler claim: 22752, 23834, 47712, 58410);
5 contradicted splits (labeler contradicted, WB not: 3597, 4683, 40388; WB contradicted, labeler not: 30949, 66876).
Critic's blind pass also labels 3597/4683 "supports" and 40388 "silent", so both blind auditors disagree with the labeler's seen-contradicted call on those 3.

## Kappa (95% bootstrap CI, 10k resamples, seed 0)
    WB vs labeler claim/no_claim n=50 agree=42 kappa=0.660 CI (0.42622950819672123, 0.8549323017408123)
    WB vs labeler contradicted on both-claim rows n=15 agree=10 kappa=-0.190 CI (-0.36363636363636337, 0.0) contra counts 2 3
    WB vs Critic30 claim/no_claim n=30 agree=28 kappa=0.862 CI (0.6445497630331755, 1.0)
    WB vs Critic30 contradicted on both-claim rows n=11 agree=10 kappa=0.000 CI (0.0, 1.0) contra counts 1 0
    Critic30 vs labeler claim/no_claim n=30 agree=26 kappa=0.724 CI (0.43661971830985913, 0.9327354260089686)
    Critic30 vs labeler contradicted on both-claim rows n=10 agree=7 kappa=0.000 CI (0.0, 1.0) contra counts 0 3
The contradicted-dimension kappas rest on 10-15 rows with 0-3 positives, so they tell us nothing (C.3 d).

## Claim rows: WB 19, labeler 19, Critic (first 30) 11.

## Unblinded supplement candidates (labeler contradicted/unverifiable, not in Critic's blind 30)
    row 40 offset 66876 pedrokiefer__aiostomp-17: labeler unverifiable (eval_logs empty); WB contradicted; Critic (unblinded addendum) ambiguous.
  The labeler's 3 seen-contradicted rows (3597, 4683, 40388) are all inside Critic's blind 30.

## Labeler false/unverifiable vs target (from the labeler's own reason field; the target file was not re-read independently)
    false 13 (10 HIDDEN_EVAL_REFUTED target=False, 3 CONTRADICTED_BY_SEEN_OUTPUT target=False), true 4 (target=True), unverifiable 2 (eval_logs empty: 23834, 66876), no_claim 31.
