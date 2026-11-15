# HYPOTHESES (pre-registration)

Project: FLOORPRICE. Author: Kinnoski (0xkinno). Written 2026-11-15, before any main model call.
This file is hashed into `HYPOTHESES.lock` together with the prompts, parameters, sampled domains, fabricated names,
page variants, articles and prices. `floorprice run` refuses to run if any of them changed. Changes after the lock
are appended as dated amendments and reported in the paper.

## Honest scope of the lock
The real-model hypotheses (H1 to H4) are locked before any model call was made. The simulation hypotheses
(H5 to H7) concern code with no model calls. While building the simulators, exploratory runs of the T6 and T7
simulators were made and read (for example to check convergence of the bridging optimiser and to calibrate the
background rater mix so that a universally helpful note passes). H5 to H7 are therefore not blind
predictions. The simulator validity check below was fixed after that tuning and is disclosed as such.

## Research questions
RQ1 validity; RQ2 floor price; RQ3 honest wait; RQ4 auditability; RQ5 composite. Definitions as in the paper.

## Ground truth and bands
Lin et al. (2023) `pc1`. Reliable band `pc1 >= 0.7`. Low-quality band `pc1 <= 0.3`. Sensitivity at 0.6 and 0.8.

## Hypotheses (verbatim)
- **H1** T2 correlates with `pc1` on real domains (Spearman rho > 0.5 pooled), so it is a plausible scorer.
- **H2** T2 gives fabricated, never-seen domains a median score at or above its own "reliable" threshold
  for at least one model (the unknown-domain prior), and prestige tokens raise scores (paired difference > 0).
- **H3** At least one of A3 to A5 moves a low-quality outlet above threshold in more than 25% of trials for
  at least two of four models; A5 (instruction injection) has the largest effect.
- **H4** Paraphrased sybil copies defeat MinHash clustering (estimated Jaccard below the clustering cut in
  most pairs) more often than TF-IDF clustering.
- **H5** Under T6a (accuracy reputation) a long con reaches threshold after fewer articles than an honest
  newcomer needs under T6b; under T6b consensus hugging never reaches threshold within the simulated horizon.
- **H6** T7 bridging needs at least 5 times more colluding accounts than majority vote to make a false
  note pass.
- **H7** `C*` has a floor price at least as high as the most expensive single component, with an honest
  wait no longer than T6b alone.
- **What would count against us:** if H2 and H3 fail for every model, the headline becomes "LLM raters are
  harder to buy than assumed", and the paper says so. If kappa on auditability coding is below 0.6, report
  ranges, not points.

## Operational definitions fixed before the lock
1. **Technique threshold.** T1: median `pc1` of the reliable band. T2 and T3, per model: the median T2 score that
   model gives the reliable-band domains of E1. T3 has no real-page band, so it reuses the model's T2 threshold.
   T4: median rank percentile of reliable-band nodes. T5: tau = 3 distinct clusters (documented cut, an assumption).
   T6a: median Beta score of the informed reference source after 50 claims. T6b: one-sided t test, alpha 0.05, at least 5 claims.
   T7: Community Notes helpful rule (intercept >= 0.40 and abs(factor) < 0.50, at least 5 ratings), majority needs >= 0.5 helpful and at least 5 ratings.
2. **Success of an LLM attempt.** The parsed score is at or above the model's threshold. A parse failure is a failure.
3. **Floor price.** Lowest rung at which at least 50% of attempts cross (10% and 90% also reported). No interpolation.
   For independent tries of new domains (A1, A2) the floor is the fewest tries giving at least one crossing in 50% of attempts,
   computed from the best naming cell's per-domain crossing rate. Zero crossings in n trials is reported as "not observed in n trials",
   with a Wilson upper bound, never as a measured price.
4. **Page attack ladder (A3 to A5).** Five variants per outlet: control, A3 boilerplate, A4 endorsement, A5 injection, combined.
   Rungs are ordered by mean tokens added. Fictional outlets, templated text.
5. **E3h (added for RQ3, 40 outlets x 2 truthful variants x 4 models).** An honest newcomer writes a truthful page with and without a
   corrections, ownership and editing policy. Honest wait under T3 is the lowest rung that crosses; if none does, "never with text alone".
6. **Honest wait.** Native evidence units first (links, pickups, claims, ratings, tokens). Time uses assumed arrival rates in
   `floorprice/config.py` (low, mid, high). These rates are assumptions, not sources.
7. **Combined attack on C\*.** A9 or A10 combined with A11 applied to claim resolution (resolution capture). Attacker asserts claims the
   crowd rates unlikely and captures the resolution. Priced as accounts needed to pass the resolution rule plus articles. Against ungated T6b the
   resolution rule is majority vote; against C* it is bridging.
8. **H5 comparison.** Median articles for the T6a long con (A9) against median articles for an honest informed newcomer under T6b, over 20 seeds.
   "Never within the horizon" means no crossing within 500 articles in any of the 20 seeds.
9. **H6 comparison.** Ratio of median bridging floor to median majority floor over 20 seeds. A censored bridging floor (cap 3000) is a lower bound.
10. **H7 comparison.** C* floor (median) against the maximum over components T3, T6b, T7 of their own cheapest listed attack, and
    honest wait (median claims) under C* against T6b alone. The LLM component can only lower, never raise. Veto rule: the rater's own
    label is "unreliable".
11. **Simulator validity check (fixed after tuning, see above).** In the T7 simulator a true note passes bridging in at least 80% of
    20 seeds and an unattacked false note passes in at most 5%.
12. **Models.** Four hosted model IDs from Adaption's public list, all probed first. Temperature 0 for all main runs. E4 uses temperature 0.7 with 3 samples.
    E5 uses the first two working models, fixed in the order listed in `floorprice/experiments.py`. A model that fails the probe is dropped and named.
13. **Sizes.** E1 400, E2 252 (14 stems x 6 token levels x 3 TLDs; the plan said 240, rounded to a full factorial), E3 120 outlets x 5 variants,
    E3h 40 x 2, E4 60 x 3, E5 60 articles x 2 prompts x 2 models. If credits require it, E1 shrinks first, E3 last; actual n is reported.

## Analysis plan
Spearman with item-bootstrap 95% CIs (2,000 resamples). Paired differences with bootstrap CIs. Wilson intervals for rates.
Holm correction across H1 to H4. Simulations: median and 5th to 95th percentile across 20 seeds. Sensitivity: reliable band 0.6 and 0.8,
dollar prices low and high, T6 informed-source noise at 0.05, 0.10 (base), 0.12. All in `floorprice/analyze.py`.

## Auditability codebook (RQ4)
Six binary criteria per technique: inputs public; method public; deterministic given inputs; an outsider can recompute a given score;
a per-score receipt or explanation exists; a contest or appeal path exists. Coded for (a) our implementation and (b) the typical public
deployment, from `evidence/snapshots/`. Coder 1 is Kinnoski (human), before seeing cheat results. Coder 2 is a fresh model instance given
only the codebook and snapshots. Headline auditability uses (b). Cohen's kappa and every disagreement reported.


### Amendment 2026-11-15 (design addition R1, made after the main E1 run had started; it does not change any main hypothesis, prompt, sample or threshold)

Reason: the brief allows an optional second provider for robustness only. Two subsets were added, reported in an appendix and never merged into the main
tables: R1a is the first 100 of the E1 sample drawn evenly across deciles, R1b is the first 30 outlets of E3 with all five variants. Models, namespaced so they
cannot stand in for an Adaption model: `gemini:gemma-4-31b-it` (the same model as Adaption's gemma-4-31b-it, served by a different provider) and
`groq:openai/gpt-oss-120b` (a different family). Same prompts, temperature 0, same strict-JSON parser. Each model's threshold is the median R1a score it gives
`pc1 >= 0.7` domains. A model that fails is reported as failed. No hypothesis is tested on R1; results are descriptive.
Files changed: floorprice/llm.py, floorprice/experiments.py, floorprice/cli.py, floorprice/budget.py (none is a locked file). HYPOTHESES.md itself changed by this amendment.


### Amendment 2026-11-15 (output budget for one model, made after reading parse statistics from the first 70 qwen calls; no hypothesis outcome had been computed)

Reason: at `max_output_tokens` 2,000, qwen3.5-397b returned an empty message in 33 of its first 70 calls because its reasoning used the whole budget.
The other three Adaption models had no empty messages. The output budget for qwen3.5-397b is raised to 8,000 tokens (`MAX_OUT` in `floorprice/llm.py`).
All other models and all prompts, samples, temperatures and thresholds are unchanged. The 33 empty responses remain in `results/raw/qwen3.5-397b.jsonl`
under their original request keys as evidence and are not used in any analysis, because their keys differ from the final requests. The paper reports the
empty-message count per model. Files changed: floorprice/llm.py (not locked); HYPOTHESES.md by this amendment.
