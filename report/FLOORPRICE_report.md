# The Floor Price of Trust: What It Costs a Liar to Look Reliable, and How Long an Honest Newcomer Waits, Under Seven Source-Reliability Scores

^^b Kinnoski
^^i Independent researcher

^^ With
^^b Apart Research

@@ Research conducted at the AI x Epistemics Research Sprint, November 2026

## Abstract

>> How much does it cost to make a fake news site look reliable to the scores AI systems use, and how long does a real new newsroom wait to be trusted? We priced seven source-reliability techniques on both questions, against expert domain ratings, with hypotheses hash-locked before the first model call. Four language-model raters tracked expert ratings (pooled Spearman rho {{llm.H1_pooled.rho|.2f}}) yet were not bought: only {{llm.summary.E2_prestige_crossed}} of {{llm.summary.E2_prestige_trials}} prestige-name fabricated domains crossed the model's own reliable threshold, none of {{llm.summary.E2_plain_trials}} plain-name ones did, none of {{llm.summary.E3_A5_injection.n}} pages carrying an injected instruction did, and the injection lowered mean scores. A truthful newcomer page with a corrections and ownership policy crossed in {{llm.summary.E3h_policy_rate_min|.0%}} to {{llm.summary.E3h_policy_rate_max|.0%}} of trials, so honest outlets are not reliably credited either. Paraphrased copies defeated MinHash clustering in {{e5.minhash_defeat_rate|.0%}} of pairs against {{e5.tfidf_defeat_rate|.0%}} for TF-IDF. In simulation, a long con fools an accuracy track record in {{hypotheses.H5.con_T6a_median_articles}} articles, while a consensus-relative record never yields to it but makes an honest informed newcomer wait a median of {{hypotheses.H5.honest_T6b_median_claims}} claims; flipping a false note takes {{hypotheses.H6.majority_median_accounts}} colluding accounts under majority vote and {{hypotheses.H6.bridging_median_accounts}} under bridging.

## 1 Introduction

Dana Reyes is a fictional verification editor at a four-person nonprofit newsroom in Ohio. At 6:40am, three weeks before an election, dozens of new local-news domains have appeared overnight, and her AI research assistant has to decide which to trust. Whatever score it uses, someone can try to buy it, and a real new outlet has to earn it.

AI search engines, research agents and newsroom triage tools consume source-reliability scores. The sprint brief asks which scoring techniques are hardest to cheat and easiest to audit. We add the second error direction: how long an honest newcomer waits under the same bar. We borrow one habit from crypto-economic security analysis, which is to price an attack against what corrupting the system is worth; we do not cite a definition for it.

Our main contributions are:

1. A price table for seven techniques: the cheapest priced attack found, in native units and in dollars at low, mid and high prices, and the honest newcomer's wait under the same threshold.
2. A pre-registered test on four hosted language models, hash-locked before any main call, with seven hypotheses reported whether supported or not. Three of the four hypotheses about real models failed.
3. An auditability coding of every technique for our implementation and for its typical public deployment, by two independent coders (both language-model instances, disclosed as such), with agreement reported.
4. A composite rule, C*, in which the language-model rater can only lower a score, and a test of whether it raises the floor price.

## 2 Related Work

Lin et al. combine six expert rating sets into 11,520 domain ratings and report that experts "generally agree on the relative quality of news domains" [1]. Yang and Menczer report that ChatGPT outlet-credibility ratings correlate with expert ratings, Spearman rho 0.54 in the first version of their paper [2]. Link spam against rank is old: bogus pages pointing at one target raise its rank, and TrustRank propagates trust from a vetted seed set [3]. Douceur showed that without a logically centralized authority, Sybil attacks are always possible except under extreme and unrealistic assumptions [4]. Bridging-based ranking, where a note is shown only if people who usually disagree both rate it helpful, was described for Birdwatch [5], and the open Community Notes documentation gives the matrix-factorisation model, the 0.40 intercept cut, the 0.50 factor limit and the five-rating minimum [6]. SMS-verification prices from the Cambridge Online Trust and Safety Index give a citable price for an account [7, 8].

The gap: we found no work that prices several reliability scores against the same attacker, or that measures what an honest newcomer pays under the same threshold.

## 3 Methods

**Ground truth.** The Lin et al. ensemble score `pc1` for 11,520 domains [1]. Reliable band `pc1 >= 0.7`, low-quality band `pc1 <= 0.3`, with sensitivity at 0.6 and 0.8.

**Techniques.** All seven are our own implementations; none is a live service (Table 1). Each exposes a score in [0, 1], its own threshold (the median score it gives the real reliable band, or a documented cut) and a receipt: canonical JSON with an inputs digest, score, threshold, verdict, a recompute command and a SHA-256 digest.

| ID | Technique | Real or simulated |
|---|---|---|
| T1 | Static expert list (unknown-domain policy a parameter) | Real data |
| T2 | LLM rater, domain name only | Real model calls |
| T3 | LLM rater, name plus the source's own page | Real model calls on generated pages |
| T4 | Link-graph rank: PageRank vs TrustRank seeded from T1 | Simulated graph over real domain names |
| T5 | Corroboration count with MinHash or TF-IDF clustering | Simulated sources, paraphrases from real model calls |
| T6 | Track record: (a) Beta accuracy, (b) consensus-relative Brier | Simulated claim streams |
| T7 | Bridging crowd ratings vs majority vote | Simulated raters |

*Table 1. The seven techniques and what is real or simulated.*

**Models.** Four hosted models through Adaption's Responses API [9]: qwen3.5-397b, deepseek-v4-flash, glm-5.2 and gemma-4-31b-it, all of which answered the probe on 2026-11-15. Temperature 0 for main runs. qwen3.5-397b returned an empty message in 33 of its first 70 calls because its reasoning exhausted a 2,000-token output cap; its cap was raised to 8,000 tokens (a recorded amendment) and the 33 empty responses are kept as evidence but not analysed. A second-provider check on small subsets (Gemini serving the same gemma model, and a Groq-hosted gpt-oss-120b) is appendix-only.

**Experiments.** E1 validity on 400 stratified real domains. E2 252 fictional domains in a full factorial of six name-token levels (none plus tribune, gazette, daily, public, institute) and three top-level domains. E3 page-text attacks on 120 fictional low-quality outlets with five variants (a neutral control, A3 boilerplate, A4 fake endorsement, A5 injected instruction, all combined). E3h truthful newcomer pages, added to measure the honest wait. E4 stability at temperature 0.7 with three samples. E5 paraphrases for the corroboration attack. All fictional names were checked against the Lin list. Success for an attempt is a parsed score at or above the model's threshold; a parse failure counts as failure.

**Attacks and prices.** Eleven attacks (A1 to A11) plus one combined attack on the composite, resolution capture (A12). The floor price is the lowest rung at which at least half of attempts cross, with no interpolation. Where nothing crosses we report "no crossing observed", with a Wilson upper bound, never a measured price. Unit prices come from public price lists read on 2026-11-15: domains from a registrar list, accounts from COTSI [7, 8], tokens from the provider's credit prices [9] (no dollar value per credit is stated, so token costs are bounded). No citable price for a purchased link was found, so links are reported in native units only.

**Simulations (labelled simulated throughout).** 20 seeds each. T4: a 1,500-node graph over real domain names. T6: claim streams in which an informed source beats a noisy consensus. T7: two rater clusters, our matrix-factorisation fit with the published cuts [6]. We found the starting optimiser settings had not converged and used converged ones; the rater mix was set so that a universally helpful note passes the 0.40 cut (disclosed in Appendix B).

**Honest wait.** Native evidence units first (links, pickups, claims, ratings, tokens). Day counts use assumed arrival rates, reported as low, mid and high; they are assumptions.

**Auditability.** Six binary criteria per technique, coded for our implementation and for the typical public deployment from saved documentation snapshots. Both coders are fresh language-model instances given only the codebook and snapshots, blind to results and to each other; neither is a human (see Limitations).

**Pre-registration.** `HYPOTHESES.md`, the prompts, parameters, samples, fictional names, pages, articles and prices were hashed into a lock file before any main call. First combined lock digest (before any model call): `d07a333181d5`; three dated amendments follow.

## 4 Results

![Figure 1. Floor price against auditability for every technique variant. Circles are real model or data measurements, squares are simulations. Marker size is validity where measured on real domains.](figures/fig1_headline.png)

**Validity (E1).** All four models tracked the expert ratings: pooled Spearman rho {{llm.H1_pooled.rho|.2f}} (95% bootstrap CI {{llm.H1_pooled.lo|.2f}} to {{llm.H1_pooled.hi|.2f}}), and {{llm.summary.E1_rho_min|.2f}} to {{llm.summary.E1_rho_max|.2f}} per model, and {{llm.summary.E1_parse_fail_total}} of {{llm.summary.E1_calls_total}} calls failed to parse. Between {{llm.summary.E1_unknown_share_min|.0%}} and {{llm.summary.E1_unknown_share_max|.0%}} of answers carried the label "unknown", and none of those scored at or above threshold. H1 is supported.

**Fabricated domains (E2).** No model's median score for fabricated, never-seen domains reached its own reliable threshold (largest model median {{llm.summary.E2_median_score_max|.2f}}). Across {{llm.summary.E2_plain_trials}} plain-name trials, {{llm.summary.E2_plain_crossed}} crossed (Wilson upper bound {{llm.summary.E2_plain_wilson_upper|.1%}}); across {{llm.summary.E2_prestige_trials}} prestige-name trials, {{llm.summary.E2_prestige_crossed}} crossed. Prestige tokens did not raise scores consistently: the paired difference was significantly positive for {{llm.summary.E2_models_with_positive_paired_ci}} of {{llm.summary.E2_models}} models, significantly negative for {{llm.summary.E2_models_with_negative_paired_ci}}, and indistinguishable from zero for the rest (range {{llm.summary.E2_paired_min|.1f}} to {{llm.summary.E2_paired_max|.1f}} points). H2 is not supported.

**Page-text attacks (E3).** Table 2 gives the crossing counts. Zero of the trials in any variant crossed. Boilerplate (A3) raised mean scores the most, from {{llm.summary.E3_control.mean_score|.1f}} for the control to {{llm.summary.E3_A3_boilerplate.mean_score|.1f}}. The injected instruction (A5) did not help: its mean score was {{llm.summary.E3_A5_injection.mean_score|.1f}}, and the models labelled {{llm.summary.E3_A5_injection.unreliable_label_share|.0%}} of those pages unreliable. Stacking everything (combined) scored {{llm.summary.E3_combined.mean_score|.1f}}, below boilerplate alone, which suggests the injection reads as a warning sign. H3 is not supported, and its sub-claim that A5 has the largest effect is false.

| Variant | Tokens added | Trials | Crossed | Wilson upper bound | Mean score |
|---|---|---|---|---|---|
| Control | 0 | {{llm.summary.E3_control.n}} | {{llm.summary.E3_control.crossed}} | {{llm.summary.E3_control.wilson_upper|.1%}} | {{llm.summary.E3_control.mean_score|.1f}} |
| A4 fake endorsement | {{llm.summary.E3_A4_endorsement.tokens|.0f}} | {{llm.summary.E3_A4_endorsement.n}} | {{llm.summary.E3_A4_endorsement.crossed}} | {{llm.summary.E3_A4_endorsement.wilson_upper|.1%}} | {{llm.summary.E3_A4_endorsement.mean_score|.1f}} |
| A5 injection | {{llm.summary.E3_A5_injection.tokens|.0f}} | {{llm.summary.E3_A5_injection.n}} | {{llm.summary.E3_A5_injection.crossed}} | {{llm.summary.E3_A5_injection.wilson_upper|.1%}} | {{llm.summary.E3_A5_injection.mean_score|.1f}} |
| A3 boilerplate | {{llm.summary.E3_A3_boilerplate.tokens|.0f}} | {{llm.summary.E3_A3_boilerplate.n}} | {{llm.summary.E3_A3_boilerplate.crossed}} | {{llm.summary.E3_A3_boilerplate.wilson_upper|.1%}} | {{llm.summary.E3_A3_boilerplate.mean_score|.1f}} |
| Combined | {{llm.summary.E3_combined.tokens|.0f}} | {{llm.summary.E3_combined.n}} | {{llm.summary.E3_combined.crossed}} | {{llm.summary.E3_combined.wilson_upper|.1%}} | {{llm.summary.E3_combined.mean_score|.1f}} |

*Table 2. Page-text attacks on fictional low-quality outlets, pooled across the four models (real model measurements). Scores are 0 to 100.*

**Second provider (Appendix C, descriptive).** Gemini serving the same gemma model replicated the pattern (rho {{robust.gemini:gemma-4-31b-it.rho|.2f}}; {{robust.gemini:gemma-4-31b-it.E3.combined.crossed}} of {{robust.gemini:gemma-4-31b-it.E3.combined.n}} combined-text pages crossed). A different family, gpt-oss-120b on Groq, has a lower reliable threshold of {{robust.groq:openai/gpt-oss-120b.threshold|.2f}}, and boilerplate crossed it for {{robust.groq:openai/gpt-oss-120b.E3.A3_boilerplate.crossed}} of {{robust.groq:openai/gpt-oss-120b.E3.A3_boilerplate.n}} outlets and the combined text for {{robust.groq:openai/gpt-oss-120b.E3.combined.crossed}} of {{robust.groq:openai/gpt-oss-120b.E3.combined.n}} (30 per variant, so intervals are wide). The resistance we report is therefore not universal across model families or thresholds.

**The honest newcomer (E3h).** A truthful page without a policy crossed in at most {{llm.summary.E3h_base_rate_max|.1%}} of trials. Adding three truthful lines (corrections, ownership, second-editor review, 49 tokens) lifted crossing to {{llm.summary.E3h_policy_rate_min|.0%}} to {{llm.summary.E3h_policy_rate_max|.0%}} of trials per model, and only {{llm.summary.E3h_policy_models_at_or_above_half}} of {{llm.summary.E3h_models}} models reached half. The honest policy lines resemble the A3 boilerplate, yet honest pages cross sometimes and A3 pages never do. One reading is that the models weigh the surrounding content and not only the policy words; we did not test that directly.

**Stability (E4).** At temperature 0.7 the mean within-domain standard deviation of a rating was {{llm.summary.E4_mean_sd_min|.1f}} to {{llm.summary.E4_mean_sd_max|.1f}} points, and the reliable decision flipped across three samples for {{llm.summary.E4_flip_min|.0%}} to {{llm.summary.E4_flip_max|.0%}} of domains. A score that moves between runs cannot be recomputed exactly, which bears on auditability.

**Corroboration (E5).** With a raw count, {{e5.a8_floor_copies.none:verbatim}} verbatim copies reach the three-source threshold. Both defences stop verbatim copies completely. Paraphrased copies defeated MinHash in {{e5.minhash_defeat_rate|.0%}} of {{e5.pairs}} pairs against {{e5.tfidf_defeat_rate|.0%}} for TF-IDF (difference {{e5.difference|.2f}}, CI {{e5.ci_lo|.2f}} to {{e5.ci_hi|.2f}}). Against MinHash the floor is {{e5.a8_floor_copies.minhash:paraphrase}} paraphrases; against TF-IDF no floor was observed. H4 is supported.

**Simulated results (labelled simulated).** *T6.* A long con of easy true claims crosses the accuracy record (T6a) after a median of {{hypotheses.H5.con_T6a_median_articles}} articles, and never crosses the consensus-relative record (T6b) in 500; consensus hugging never crosses T6b either. The price of that safety is the honest wait: an informed newcomer needs a median of {{hypotheses.H5.honest_T6b_median_claims}} claims, and with a weaker informational edge most seeds do not cross within the horizon (Appendix C). Resolution capture crosses T6b after {{table.T6b consensus-relative.attacks.A12_capture_majority_resolution.native}} captured claims plus the {{table.T6b consensus-relative.attacks.A12_capture_majority_resolution.plus_accounts}} accounts that capture each resolution. *T7.* A true note passes bridging in {{hypotheses.simulator_validity_T7.true_note_pass_rate|.0%}} of seeds and an unattacked false note in {{hypotheses.simulator_validity_T7.false_note_unattacked_pass_rate|.0%}}. A false note passes majority vote with {{hypotheses.H6.majority_median_accounts}} colluding accounts and bridging with {{hypotheses.H6.bridging_median_accounts}}, a ratio of {{hypotheses.H6.ratio|.0f}}. *T4.* A link farm crosses PageRank with {{table.T4 PageRank.attacks.A6_farm_domains.native}} domains and never crosses TrustRank; bought links cross TrustRank at {{table.T4 TrustRank.attacks.A7_bought_links.native}} links, which we cannot price. *Composite.* C* inherits the bridging floor of {{hypotheses.H7.cstar_floor_accounts}} accounts by construction; its honest wait is {{hypotheses.H7.honest_wait_cstar}} claims against {{hypotheses.H7.honest_wait_T6b}} for T6b alone on the same claim stream, a difference within simulation noise.

**Hypothesis scorecard.** H1 supported. H2 not supported. H3 not supported. H4 supported. H5 supported (simulated, not blind). H6 supported (simulated, not blind). H7 supported by its own definition, which is close to definitional for the floor (simulated, not blind). Holm-adjusted p-values: H1 {{hypotheses.H1.p_holm|.3f}}, H2 {{hypotheses.H2.p_holm|.3f}}, H3 {{hypotheses.H3.p_holm|.3f}}, and H4 below 0.001 (no bootstrap resample fell on the wrong side in 2,000).

**Auditability.** The two coders agreed on {{audit.n_items}} items with Cohen's kappa {{audit.kappa|.2f}} and disagreed on {{audit.n_disagreements}} (Appendix C). Because both are language models their agreement may share priors. For the typical public deployment, bridging and the static list met the most criteria and the track-record and LLM-rater deployments the fewest.

## 5 Discussion and Limitations

**Language-model raters were harder to buy than we assumed.** On fictional low-quality outlets, neither a prestige-sounding name nor a page stuffed with awards, endorsements and instructions to the rater moved any model across its own reliable bar. The instruction channel, which we expected to be the cheapest attack, backfired: models treated it as a warning sign. This is a real-model finding on templated pages and should be read with that limit: it does not show that no page can fool a rater, and in a small second-provider check a different model family with a lower reliable threshold was crossed by boilerplate for about one outlet in six.

**Resistance and fairness trade against each other.** The techniques that resisted attack are the ones that are slow or opaque for an honest newcomer. A consensus-relative track record never yields to a long con but needs a median of {{hypotheses.H5.honest_T6b_median_claims}} claims from an informed source; the language-model raters credited a truthful newcomer page in only {{llm.summary.E3h_policy_rate_min|.0%}} to {{llm.summary.E3h_policy_rate_max|.0%}} of trials for most models. The techniques that are cheap to buy (an accuracy record, a majority vote, a raw corroboration count) are the ones that credit newcomers quickly. Price and honest wait have to be reported together.

**A rater that cannot be bought can still not be audited.** Both coders scored the language-model deployments near the bottom on auditability, and ratings moved between runs (E4). A reliability score that no outsider can recompute shifts trust from the score to whoever sells it, the "trust a source without trusting whoever sells the score" problem the receipt format is meant to address.

**For builders.** Do not let one rater be the only gate. Our composite lets the rater only lower a score, and in E3 and E3h that rule separated the two populations: the "unreliable" label covered {{llm.summary.E3_control.unreliable_label_share|.1%}} of low-quality control pages and {{llm.summary.E3h_veto_honest_policy|.1%}} of honest pages with a policy. Gate resolutions on a bridging rule, because the cost of capturing a resolution is then the bridging price. Publish a receipt with every score.

### Limitations

We state each assumption and how the reading of the results would change if it failed.

1. **Three of the seven techniques are simulated** (T4 graph, T6 claim streams, T7 raters), and T5 uses simulated sources with real paraphrases. Their floor prices describe our simulators. If real link graphs, claim streams or rater populations differ, the native-unit numbers move; the ordering between attacks that differ by orders of magnitude is the part we expect to travel.
2. **Fictional outlets with templated pages.** The page-text attacks (A3 to A5) use generated about pages. Real low-quality outlets write differently, so crossing rates on real pages could be higher or lower.
3. **Four models, one provider for the main runs, one ground truth, English only.** A second provider was run on small subsets as a robustness check (Appendix C) and is descriptive only.
4. **Prices are assumptions with ranges.** Domain and account prices come from public price lists read on one day; the provider states no dollar value per credit, so token costs are bounded, not measured; a purchased link has no citable price and is reported in native units. We report whether the ranking changes across the low-to-high range.
5. **Honest-wait times rest on assumed arrival rates** (links, pickups, claims, ratings per day). Native units are the measurement; the day counts are conversions.
6. **Thresholds are our choice.** Each technique's "reliable" cut is the median score it gives the real reliable band, or a documented cut (for corroboration, three independent sources). We test 0.6 and 0.8 for the band.
7. **Simulation hypotheses were not blind.** The T6 and T7 simulators were read while being built, and the T7 rater mix was set so that a universally helpful note passes the 0.40 cut. Hypotheses H5 to H7 are reported with that disclosure.
8. **Auditability coding was done by two language-model instances, not a human.** Agreement between them is model-to-model agreement. [CONFIRM BEFORE SUBMISSION: the author reviewed the disagreement list; delete this bracket only if true.]
9. **The composite's floor equals the bridging floor by construction**, since it gates resolutions on bridging. The informative parts of H7 are the honest wait and the veto behaviour, not the floor comparison.

### Future Work

Replace simulated graphs and rater pools with real ones where public data exist; run the page attacks on real outlet pages; add a human auditability coder and a larger rater panel; measure the effect of the composite on real claim resolutions; and extend to other languages.


## 6 Conclusion

Seven ways of scoring a source differ by orders of magnitude in what they cost to cheat. In simulation, an accuracy record falls to {{hypotheses.H5.con_T6a_median_articles}} articles and a majority vote to {{hypotheses.H6.majority_median_accounts}} accounts, while bridging needs {{hypotheses.H6.bridging_median_accounts}}. On four real language models, no name or page-text attack we tried crossed the models' own reliable bar, so the pre-registered expectation that they could be bought was wrong. Instruction injection hurt the attacker.

The same scores are slow to credit an honest newcomer, and the least expensive to attack are the quickest to credit one. A score should therefore be reported with both numbers, its floor price and its honest wait, and with a receipt that lets an outsider recompute it. The composite rule, with a lower-only model veto and bridging-gated resolutions, is a concrete design that is cheap on neither side of that trade-off, and testing it on real claim resolutions is the next step.


## Code and Data

- Code repository: https://github.com/0xkinno/floorprice
- Data and outputs: raw model responses in `results/raw/` (keyed by SHA-256 of each request), derived trials in `results/main/`, simulations in `results/sims/`, all numbers in `results/FACTS.json`. The dataset of domain ratings is third-party (Lin et al.) and is included with its source note.
- Other artifacts: static site with the interactive floor ladder, https://floorprice-puce.vercel.app
- No personal data. Fictional domain names are generic; the generator and seed are published.


## Author Contributions

Kinnoski conceived the study, set the design and hypotheses, directed the work and takes responsibility for it. An AI assistant working under Kinnoski's direction wrote the code, ran the experiments and drafted the text; see the LLM Usage Statement.


## References

1. Lin, H., Lasser, J., Lewandowsky, S., Cole, R., Gully, A., Rand, D. G., Pennycook, G. (2023). High level of correspondence across different news domain quality rating sets. PNAS Nexus 2(9), pgad286. https://doi.org/10.1093/pnasnexus/pgad286
2. Yang, K.-C., Menczer, F. (2023). Large language models can rate news outlet credibility. arXiv:2304.00228 (later revised as Accuracy and Political Bias of News Source Credibility Ratings by Large Language Models, WebSci 2025). https://arxiv.org/abs/2304.00228
3. Gyongyi, Z., Garcia-Molina, H., Pedersen, J. (2004). Combating Web Spam with TrustRank. Proceedings of the 30th VLDB Conference, Toronto. https://www.vldb.org/conf/2004/RS15P3.PDF
4. Douceur, J. R. (2002). The Sybil Attack. 1st International Workshop on Peer-to-Peer Systems (IPTPS). https://www.microsoft.com/en-us/research/publication/the-sybil-attack/
5. Wojcik, S., Hilgard, S., Judd, N., Mocanu, D., Ragain, S., Hunzaker, M. B. F., Coleman, K., Baxter, J. (2022). Birdwatch: Crowd Wisdom and Bridging Algorithms can Inform Understanding and Reduce the Spread of Misinformation. arXiv:2210.15723. https://arxiv.org/abs/2210.15723
6. Community Notes documentation, "Ranking notes". https://github.com/twitter/communitynotes/blob/main/documentation/under-the-hood/ranking-notes.md (read 2026-11-15)
7. Cambridge Online Trust and Safety Index (COTSI), methodology. https://www.cotsi.org/methodology (read 2026-11-15)
8. University of Cambridge (2025). Price of a bot army revealed across hundreds of online platforms worldwide, 11 December 2025. https://www.cam.ac.uk/stories/price-bot-army-global-index (read 2026-11-15)
9. Adaption Labs documentation, hosted models and Responses API. https://docs.adaptionlabs.ai (read 2026-11-15)

## Appendix A Limitations and dual use

Publishing cheat costs helps defenders more than attackers: the numbers are what a team needs to decide whether a score is safe to consume, and they describe attacks on our own implementations, not on any live service. No live service was attacked; real services are described only from their public documentation. The fictional domain names are generic strings; we publish the generator and seed and the names themselves, and we do not publish a curated registration list. Nothing in the paper gives a working recipe against a named product. If a result looked like a flaw in a specific deployed system we would have withheld it and reported it to the maintainer.


## Appendix B Pre-registration

The hypotheses are quoted verbatim in `HYPOTHESES.md`, hash-locked (SHA-256 per file plus a combined digest) before the first main model call. Three amendments were recorded: a second-provider robustness subset; a larger output budget for one model whose reasoning had exhausted the original cap (33 of its first 70 calls returned an empty message); and a note that the auditability coding and hand checks were performed by AI instances at the author's instruction. Simulation hypotheses H5 to H7 were not blind (Section 5).


## Appendix C Extra tables

| Model | Threshold (median score of reliable band) | E1 Spearman rho | E1 parse failures |
|---|---|---|---|
| qwen3.5-397b | {{llm.per_model.qwen3.5-397b.threshold|.2f}} | {{llm.per_model.qwen3.5-397b.E1_rho.rho|.2f}} | {{llm.per_model.qwen3.5-397b.E1_parse_fail}} |
| deepseek-v4-flash | {{llm.per_model.deepseek-v4-flash.threshold|.2f}} | {{llm.per_model.deepseek-v4-flash.E1_rho.rho|.2f}} | {{llm.per_model.deepseek-v4-flash.E1_parse_fail}} |
| glm-5.2 | {{llm.per_model.glm-5.2.threshold|.2f}} | {{llm.per_model.glm-5.2.E1_rho.rho|.2f}} | {{llm.per_model.glm-5.2.E1_parse_fail}} |
| gemma-4-31b-it | {{llm.per_model.gemma-4-31b-it.threshold|.2f}} | {{llm.per_model.gemma-4-31b-it.E1_rho.rho|.2f}} | {{llm.per_model.gemma-4-31b-it.E1_parse_fail}} |

*Table C1. Per-model validity (real model measurements). Thresholds at the 0.6 and 0.8 reliable bands are in `results/analysis.json`.*

| Model | Honest page, no policy: crossed | Honest page with policy: crossed |
|---|---|---|
| qwen3.5-397b | {{llm.summary.E3h.qwen3.5-397b.honest_base.rate|.0%}} | {{llm.summary.E3h.qwen3.5-397b.honest_policy.rate|.0%}} |
| deepseek-v4-flash | {{llm.summary.E3h.deepseek-v4-flash.honest_base.rate|.0%}} | {{llm.summary.E3h.deepseek-v4-flash.honest_policy.rate|.0%}} |
| glm-5.2 | {{llm.summary.E3h.glm-5.2.honest_base.rate|.0%}} | {{llm.summary.E3h.glm-5.2.honest_policy.rate|.0%}} |
| gemma-4-31b-it | {{llm.summary.E3h.gemma-4-31b-it.honest_base.rate|.0%}} | {{llm.summary.E3h.gemma-4-31b-it.honest_policy.rate|.0%}} |

*Table C2. Honest newcomer pages (E3h, 40 outlets per model, real model measurements).*

| Second provider | Threshold | Spearman rho (n=100) | Control crossed | Boilerplate crossed | Injection crossed | Combined crossed |
|---|---|---|---|---|---|---|
| gemini:gemma-4-31b-it | {{robust.gemini:gemma-4-31b-it.threshold|.2f}} | {{robust.gemini:gemma-4-31b-it.rho|.2f}} | {{robust.gemini:gemma-4-31b-it.E3.control.crossed}} of 30 | {{robust.gemini:gemma-4-31b-it.E3.A3_boilerplate.crossed}} of 30 | {{robust.gemini:gemma-4-31b-it.E3.A5_injection.crossed}} of 30 | {{robust.gemini:gemma-4-31b-it.E3.combined.crossed}} of 30 |
| groq:openai/gpt-oss-120b | {{robust.groq:openai/gpt-oss-120b.threshold|.2f}} | {{robust.groq:openai/gpt-oss-120b.rho|.2f}} | {{robust.groq:openai/gpt-oss-120b.E3.control.crossed}} of 30 | {{robust.groq:openai/gpt-oss-120b.E3.A3_boilerplate.crossed}} of 30 | {{robust.groq:openai/gpt-oss-120b.E3.A5_injection.crossed}} of 30 | {{robust.groq:openai/gpt-oss-120b.E3.combined.crossed}} of 30 |

*Table C3. Second-provider robustness subsets (real model measurements, descriptive only, not part of any hypothesis test).*

Simulation sensitivity (T6 informed-source noise 0.05 and 0.12 against the base 0.10), the second-provider robustness subsets and the full disagreement list between the two auditability coders are in `results/sims/t6sens.json`, `results/main/R1*`, and `results/analysis.json` respectively. With an informed source noise of 0.12 an honest informed newcomer usually did not cross T6b within 500 claims.

## LLM Usage Statement

AI assistants were used extensively. An AI coding assistant wrote the code, ran the experiments, drafted this report and built the site, working under the author's direction and instructions throughout. All model calls in the study go through Adaption's Responses API; two further instances of a language model acted as the two auditability coders, and an AI reader performed the hand checks of parse correctness and paraphrase fidelity, all at the author's instruction. The author set the research question, design and hypotheses and is responsible for every claim and reference. [CONFIRM BEFORE SUBMISSION: the author reviewed the outputs; delete this bracket only if true.] Every reference was opened and read before being cited; references that could not be opened are not cited. This report is therefore not primarily written by the author personally, and we say so.
