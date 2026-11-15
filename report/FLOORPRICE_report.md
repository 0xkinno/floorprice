# The Floor Price of Trust: What It Costs a Liar to Look Reliable, and How Long an Honest Newcomer Waits, Under Seven Source-Reliability Scores

**Kinnoski (Independent researcher)**. With Apart Research. Research conducted at the AI x Epistemics Research Sprint, November 13 to 15, 2026.

## Abstract

How much does it cost to make a fake news site look reliable to the scores AI systems use, and how long does a real new newsroom wait to be trusted? We price seven source-reliability scoring techniques on both questions: a static expert list, an LLM rater from the domain name, an LLM rater with the source's own page, link-graph rank, corroboration counting, track records, and bridging crowd ratings. Ground truth is the Lin et al. domain-quality ratings. For each technique we find the cheapest attack that crosses its own "reliable" threshold, in native units and in dollars at low, mid and high prices, and the wait of an honest newcomer under the same threshold. Hypotheses were written and hash-locked before the first model call. [PENDING headline numbers from FACTS after the real-model runs. Simulated results, labelled as such: a long con crosses an accuracy track record in {{fact:hypotheses.H5.con_T6a_median_articles}} articles and never crosses a consensus-relative record, whose honest informed newcomer needs a median of {{fact:hypotheses.H5.honest_T6b_median_claims}} claims; bridging needed a median of {{fact:hypotheses.H6.bridging_median_accounts}} colluding accounts against {{fact:hypotheses.H6.majority_median_accounts}} for majority vote.]

## 1 Introduction

Dana Reyes is a fictional verification editor at a four-person nonprofit newsroom in Ohio. At 6:40am, three weeks before an election, dozens of new local-news domains have appeared overnight, and her AI research assistant has to decide which to trust. Whatever score the assistant uses, someone can try to buy it, and a real new outlet has to earn it.

AI search engines, research agents and newsroom triage tools consume source-reliability scores. The question from the sprint brief is: which source-reliability scoring techniques are hardest to cheat and easiest to audit? We add a second error direction: how long an honest newcomer waits. We borrow one habit from crypto-economic security analysis, which is to price an attack against what corrupting the system is worth. We do not cite a definition for it.

Contributions:
1. A price table: for seven techniques, the cheapest priced attack and the honest newcomer's wait, in native units first and dollars at low, mid and high prices.
2. A pre-registered test on real models: seven hypotheses, hash-locked before any main model call, reported whether supported or not.
3. An auditability coding with a human coder and a blind model coder, with agreement reported.
4. A composite rule, C*, in which the LLM rater can only lower a score, and a test of whether it raises the floor price.

## 2 Related work

Lin et al. combine six expert rating sets into 11,520 domain ratings and report that experts "generally agree on the relative quality of news domains" [1]. Yang and Menczer report that ChatGPT outlet-credibility ratings correlate with expert ratings (Spearman rho 0.54 in the first version) [2]. Link spam against rank was studied for the web: bogus pages pointing at one target raise its rank, and TrustRank propagates trust from a vetted seed set [3]. Douceur showed that without a logically centralized authority, Sybil attacks are always possible except under extreme and unrealistic assumptions [4]. Bridging-based ranking, where a note is shown only if people who usually disagree both rate it helpful, was described for Birdwatch [5], and the open Community Notes documentation gives the matrix-factorisation model, the 0.40 intercept cut, the 0.50 factor limit and the five-rating minimum [6]. SMS-verification prices from the Cambridge Online Trust and Safety Index give a citable price for an account [7, 8].

The gap: we found no work that prices several reliability scores against the same attacker, or that measures what an honest newcomer pays under the same threshold.

## 3 Methods

**Ground truth.** The Lin et al. ensemble score `pc1` for 11,520 domains [1]. Reliable band `pc1 >= 0.7`, low-quality band `pc1 <= 0.3`, sensitivity at 0.6 and 0.8.

**Techniques (Table 1).** All are our own implementations. None is a live service.

| ID | Technique | Real or simulated |
|---|---|---|
| T1 | Static expert list (unknown-domain policy as a parameter) | Real data |
| T2 | LLM rater, domain name only | Real model calls |
| T3 | LLM rater, name plus the source's own page | Real model calls on generated pages |
| T4 | Link-graph rank, PageRank vs TrustRank seeded from T1 | Simulated graph over real domain names |
| T5 | Corroboration count with MinHash or TF-IDF clustering | Simulated sources, paraphrases from real model calls |
| T6 | Track record: (a) Beta accuracy, (b) consensus-relative Brier | Simulated claim streams |
| T7 | Bridging crowd ratings vs majority | Simulated raters |

Each technique gives `score` in [0, 1], its own `threshold` (the median score it gives the real reliable band, or a documented cut), and a receipt: canonical JSON with inputs digest, score, threshold, verdict, a recompute command and a SHA-256 digest.

**Attacks and prices.** Eleven attacks (A1 to A11) plus one combined attack on the composite (resolution capture, A12). The floor price is the lowest rung at which at least half of attempts cross the threshold. No interpolation. Unit prices come from public price lists read on 2026-11-15: domains from a registrar list, accounts from COTSI [7, 8], model tokens from the provider's public credit prices [9]. The provider states no dollar value per credit, so token costs are bounded by reading one credit as one dollar. No citable price for a purchased link was found, so links are reported in native units only.

**Models.** Four hosted models through Adaption's Responses API [9]. [PENDING probe: model IDs, dates, which answered.] Temperature 0 for main runs; a repeated subset at temperature 0.7 with three samples measures stability.

**Experiments.** E1 validity on 400 stratified real domains. E2 252 fictional domains in a factorial of name tokens and top-level domains. E3 page-text attacks on 120 fictional low-quality outlets with five page variants, including a neutral control. E3h truthful newcomer pages (added for the honest-wait question). E4 stability. E5 paraphrases for the corroboration attack. All fictional names were checked against the Lin list.

**Simulations (labelled simulated everywhere).** 20 seeds each. T4: a 1,500-node graph over real domain names with prestige and homophily. T6: claim streams in which an informed source beats a noisy consensus. T7: two rater clusters, our matrix-factorisation fit using the published intercept and factor cuts [6], with a note-pool mix chosen so that a universally helpful note passes (disclosed in Appendix B). The T7 optimiser was run to convergence (the first settings had not converged).

**Honest wait.** Native evidence units first (links, pickups, claims, ratings, tokens). Time conversions use assumed arrival rates, reported as low, mid and high. These rates are assumptions, not sourced.

**Auditability.** Six binary criteria per technique, coded for our implementation and for the typical public deployment from saved documentation snapshots. Coder 1 is the author, working before seeing cheat results. Coder 2 is a fresh model instance given only the codebook and snapshots. [PENDING kappa.]

**Pre-registration.** `HYPOTHESES.md` and the prompts, parameters, samples, fictional names, pages, articles and prices were hashed into `HYPOTHESES.lock` before any main call. Lock digest: [PENDING digest at time of first run].

## 4 Results

[PENDING Figure 1 and Table 2 from real results. Figure captions state real or simulated.]

**Simulated results available now.**

*T6, simulated.* A long con of easy true claims crosses the accuracy track record (T6a) after a median of {{fact:hypotheses.H5.con_T6a_median_articles}} articles. It never crosses the consensus-relative record (T6b) in 500 articles in any of 20 seeds, and neither does consensus hugging. Resolution capture, where the attacker asserts claims the crowd rates unlikely and captures their resolution, crosses T6b after a median of {{fact:table.T6b consensus-relative.attacks.A12_capture_majority_resolution.native}} captured claims. The cost of T6b is the honest wait: an informed newcomer needs a median of {{fact:hypotheses.H5.honest_T6b_median_claims}} claims, and with a smaller informational edge most seeds do not cross within the horizon (Appendix C).

*T7, simulated.* A true note passes bridging in {{fact:hypotheses.simulator_validity_T7.true_note_pass_rate|.2f}} of seeds and an unattacked false note in {{fact:hypotheses.simulator_validity_T7.false_note_unattacked_pass_rate|.2f}}. A false note passes under majority vote with a median of {{fact:hypotheses.H6.majority_median_accounts}} colluding accounts and under bridging with {{fact:hypotheses.H6.bridging_median_accounts}}.

*T4, simulated.* [PENDING table from FACTS: PageRank and TrustRank floors for link farms and bought links.]

**Hypothesis scorecard.** [PENDING: H1 to H4 need model runs. Simulation hypotheses: H5 supported = {{fact:hypotheses.H5.supported}}; H6 supported = {{fact:hypotheses.H6.supported}}; H7 supported = {{fact:hypotheses.H7.supported}}.]

## 5 Discussion and limitations

[PENDING discussion of what the real results mean for agent builders and newsrooms.] Limits: the link graph, claim streams and raters are simulated; four models; unit prices are assumptions with ranges; one ground truth; English only; honest-wait time conversions rest on assumed arrival rates; fictional outlets use templated pages.

## 6 Conclusion

[PENDING two short paragraphs, written after results.]

## Code and data

Repository: [PENDING URL]. Cached model outputs in `results/raw/`. One command rebuilds every number and figure: `make reproduce`. No personal data.

## References

1. Lin, H., Lasser, J., Lewandowsky, S., Cole, R., Gully, A., Rand, D. G., Pennycook, G. High level of correspondence across different news domain quality rating sets. PNAS Nexus 2(9), pgad286, 2023. DOI 10.1093/pnasnexus/pgad286.
2. Yang, K.-C., Menczer, F. Large language models can rate news outlet credibility. arXiv:2304.00228, 2023 (later revised as Accuracy and Political Bias of News Source Credibility Ratings by Large Language Models, WebSci 2025).
3. Gyongyi, Z., Garcia-Molina, H., Pedersen, J. Combating Web Spam with TrustRank. Proceedings of the 30th VLDB Conference, Toronto, 2004.
4. Douceur, J. R. The Sybil Attack. 1st International Workshop on Peer-to-Peer Systems (IPTPS), 2002.
5. Wojcik, S., Hilgard, S., Judd, N., Mocanu, D., Ragain, S., Hunzaker, M. B. F., Coleman, K., Baxter, J. Birdwatch: Crowd Wisdom and Bridging Algorithms can Inform Understanding and Reduce the Spread of Misinformation. arXiv:2210.15723, 2022.
6. Community Notes documentation, "Ranking notes". https://github.com/twitter/communitynotes (documentation/under-the-hood/ranking-notes.md), read 2026-11-15.
7. Cambridge Online Trust and Safety Index (COTSI), methodology. https://www.cotsi.org/methodology, read 2026-11-15.
8. University of Cambridge, "Price of a bot army revealed across hundreds of online platforms worldwide", 11 December 2025. https://www.cam.ac.uk/stories/price-bot-army-global-index, read 2026-11-15.
9. Adaption Labs documentation, hosted models and Responses API. https://docs.adaptionlabs.ai, read 2026-11-15.

## Appendix A Limitations and dual use

[PENDING full text.] Publishing cheat costs helps defenders more than attackers because the costs are what a defender needs to decide whether a score is safe to consume. No live service was attacked: every attack ran against our own implementations on generated data or the public dataset. Fictional domain names are generic; we publish the generator and seed and say so, and we do not publish a curated registration list.

## Appendix B Pre-registration

Hypotheses verbatim, lock digest, amendments and outcomes: see `HYPOTHESES.md`. Simulation hypotheses H5 to H7 were not blind: exploratory runs of the T6 and T7 simulators were read while building them, and the T7 rater mix was tuned so that a universally helpful note passes the 0.40 cut.

## Appendix C Extra tables

[PENDING per-model results; sensitivity at other thresholds and prices; T6 noise sensitivity: with informed noise 0.12 an honest informed source crossed T6b in only part of the seeds within 500 claims.]

## LLM Usage Statement

AI assistants wrote code and drafts under Kinnoski's direction. Kinnoski codes the auditability sheet himself, hand-checks samples of rater outputs and paraphrases, verifies every claim and reference, and takes responsibility for the work. [CONFIRM: these human steps have not happened yet.]
