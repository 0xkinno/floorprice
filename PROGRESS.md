# PROGRESS

## Session 1 (2026-11-15)
Done: repo scaffold and authorship enforcement; model-call layer (cache, budget, resumable, offline replay) with tests; data layer (Lin et al.,
stratified sample, fabricated domains, page variants, honest pages, articles); seven techniques and the composite; attack ladders and floor search;
full 20-seed simulations (T4, T6 with sensitivity, T7, C*); analysis module; facts and numbers pipeline; style checker; report builder;
pre-registration and lock; auditability evidence snapshots, codebook and blind coder 2.

Blocked and needs Kinnoski:
1. ADAPTION_API_KEY (and credits) for the probe and E1 to E5. Nothing about model behaviour has been measured. No model result appears anywhere in this repo.
2. GitHub repository URL to push to (private first).
3. Official report template (report/template.docx) and the Guidelines tab text.
4. Human auditability coding (coder 1) before viewing cheat results, and the hand checks (100 parses, 50 paraphrases).
5. References that could not be opened by the tools: Gneiting and Raftery 2007, Tow Center, Medill, a primary source for cost of corruption versus profit from corruption.

Design notes worth knowing:
- The T7 optimiser defaults were changed from the brief's starting values (lr 0.05, 400 iterations) to lr 0.3, 1,500 iterations, because the starting values had not converged.
- The T7 background rater mix was set so that a universally helpful note passes the published 0.40 cut. Disclosed in HYPOTHESES.md.
- Community Notes thresholds (0.40, 0.50, lambda 0.15 and 0.03, at least 5 ratings) were checked against the open-source documentation text.
- Added E3h (truthful newcomer pages) so RQ3 has a measured honest wait for the LLM raters. E2 is 252 domains (full factorial).
