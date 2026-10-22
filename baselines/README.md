# ClaimCheck no-model baselines

Imported from the lab's local baselines repo. Check suites were frozen (committed) before the data they score was generated; original frozen commit hashes (local repo, not on GitHub):

| Item | Frozen commit |
|---|---|
| Check suite v1 (`checks/nomodel.py`) | 03a3aca |
| Check suite v2 (`checks/nomodel_v2.py`) | a50a18f |
| Pre-registration implicit-v1 (`gen/PREREG-implicit-v1.md`) | 5dd630f |
| implicit-v1 scores / v2 re-score (`results-v2.md`) | 53ba7d7 |
| Check suite v3 (`checks/nomodel_v3.py`) | f38eb3ba79de2e43efaccc2dc05d3f03161f81ea |
| World exclusion card | 3286bf2, a1bc140 |
| Check suite v3.1 = v3 + `rename_matcher` (`checks/nomodel_v3_1.py`) | 8898624 |

Suites are append-only: checks are added, never loosened. Scoring uses balanced accuracy.
Synthetic held-out sets are not published here (regenerate from `gen/` with the seeds in the cards). Scripts expect the repo's `data/claims.jsonl` and `finetune/split.json` at `../` paths; adjust `P` as needed.
