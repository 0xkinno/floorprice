# PROGRESS

## Session 1 (2026-11-15)
Done: repo scaffold and authorship enforcement; model-call layer (cache, budget, resumable, offline replay) with tests; data layer (Lin et al.,
stratified sample, fabricated domains, page variants, honest pages, articles); seven techniques and the composite; attack ladders and floor search;
full 20-seed simulations (T4, T6 with sensitivity, T7, C*); analysis module; facts and numbers pipeline; style checker; report builder;
pre-registration and lock; auditability evidence snapshots, codebook and blind coder 2.

Blocked and needs Kinnoski:
1. (resolved) API keys and the GitHub repository were provided; probe done; experiments running.
2. (resolved) Repository 0xkinno/floorprice attached; pushes work.
3. Official report template (report/template.docx) and the Guidelines tab text.
4. Human auditability coding (coder 1) before viewing cheat results, and the hand checks (100 parses, 50 paraphrases).
5. References that could not be opened by the tools: Gneiting and Raftery 2007, Tow Center, Medill, a primary source for cost of corruption versus profit from corruption.

Design notes worth knowing:
- The T7 optimiser defaults were changed from the brief's starting values (lr 0.05, 400 iterations) to lr 0.3, 1,500 iterations, because the starting values had not converged.
- The T7 background rater mix was set so that a universally helpful note passes the published 0.40 cut. Disclosed in HYPOTHESES.md.
- Community Notes thresholds (0.40, 0.50, lambda 0.15 and 0.03, at least 5 ratings) were checked against the open-source documentation text.
- Added E3h (truthful newcomer pages) so RQ3 has a measured honest wait for the LLM raters. E2 is 252 domains (full factorial).

## Session 1, later (2026-11-15 to 2026-11-16)
- Probe: all four Adaption models answer. Key limit is about 25 requests per minute for the whole key, so the run is paced (about 20 to 23 calls per minute).
- qwen3.5-397b returned empty messages in 47% of calls at a 2,000 token cap; its cap is now 8,000 (amendment in HYPOTHESES.md).
- A robustness subset on Gemini (same gemma model, different provider) and Groq (gpt-oss-120b) is appendix-only (amendment in HYPOTHESES.md).
- Site redesigned (light-blue sky, editorial serif, glass surfaces, floor ladder, Framer Motion) and deployed: https://floorprice-puce.vercel.app
- CI was failing on one test that read the runner's git config. Fixed, and verified in a fresh clone with no git identity. CI green.
- The worker restarted at about 03:50 UTC on 2026-11-16 and killed the experiment processes. They were relaunched detached from the cache; 3,113 calls remained.
- Video references saved to reference/video (gitignored) with notes.
