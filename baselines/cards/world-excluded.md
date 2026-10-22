# Data card: World exclusions for the R5 holdout
Source: claimcheck-public/finetune/world/my-sandboxes.txt + PREREGISTRATION.md (read Oct 22, 2026 CT)
| sandbox | tag | created–killed (CT) | episodes | seed | repos |
|---|---|---|---|---|---|
| iem5xpy6jcqolsdqf330n | probe | 08:04:27–08:04:39 (12 s) | 0 | n/a | none |
| im3gog5ure2qgfnrpt2ra | smoke | 08:05:45–08:13:23 | 6 planned, aborted; no eps file written | NOT LOGGED | w{SEED}-0…5 |
Open: smoke seed must come from the World owner; until known, R5 uses a fresh pre-registered seed range and a held-out repo family split.
Frozen check suite for scoring: v3 f38eb3b.

## Seed reproducibility
Adding `rename` to the chaos list (claimcheck-public `5bd5780`, branch `world/rename-chaos`) changes the random draws. Seeds drawn before that commit do not reproduce the same episodes. R5 seeds must be listed against `5bd5780` or later.
