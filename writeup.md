# My coding agents' claims checked out. Here's the test I built to check them.

I run AI coding agents that write, test and merge most of my product's code. Early on they reported success they hadn't earned: "tests pass" when nothing ran. So I made every report say what was *not* established. Then I wanted to know two things: did it work, and can a model catch it when it doesn't?

I built a benchmark from 388 of my agent sessions. Each item pairs a claim like "vitest: 36 passed" with the commands the agent actually ran, their exit codes and their output.

**Result 1: the rule held.** Of 110 real success claims, 109 were backed by the agent's own logs. The one exception called eslint "clean" when there were warnings.

**Result 2: catching bad claims is a trade-off.** I added 109 broken versions: wrong run, inflated count, run edited to fail. A keyword checker scores 71% and misses half of them. Grok 4.20 (non-reasoning) scores 93%. Grok 4.7 catches 97% of bad claims, but rejects 18% of the true ones.

**Result 3: definitions matter.** In v1, Grok 4.7 rejected half the true claims because the sentences said more than the logs showed. When I made the graded span explicit, its accuracy on true claims rose from 52% to 75%. After seeing results, I also fixed labels and dropped badly paired items, and the README says so.

Limits: the bad examples are synthetic, there's one annotator (me, with model help), it's one codebase, and it's 219 items.

Why it matters: a useful model has to tell the truth about its own work. Checking claims against the model's own evidence is a cheap way to measure that.

Data, rubric, harness: github.com/clickmind/claimcheck.
