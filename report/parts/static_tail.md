## 5 Discussion and Limitations

{{DISCUSSION}}

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

{{CONCLUSION}}

## Code and Data

- Code repository: https://github.com/0xkinno/floorprice
- Data and outputs: raw model responses in `results/raw/` (keyed by SHA-256 of each request), derived trials in `results/main/`, simulations in `results/sims/`, all numbers in `results/FACTS.json`. The dataset of domain ratings is third-party (Lin et al.) and is included with its source note.
- Other artifacts: static site with the interactive floor ladder, https://floorprice-puce.vercel.app
- No personal data. Fictional domain names are generic; the generator and seed are published.

## Author Contributions

Kinnoski conceived the study, set the design and hypotheses, directed the work and takes responsibility for it. An AI assistant working under Kinnoski's direction wrote the code, ran the experiments and drafted the text; see the LLM Usage Statement.

## Appendix A Limitations and dual use

Publishing cheat costs helps defenders more than attackers: the numbers are what a team needs to decide whether a score is safe to consume, and they describe attacks on our own implementations, not on any live service. No live service was attacked; real services are described only from their public documentation. The fictional domain names are generic strings; we publish the generator and seed and the names themselves, and we do not publish a curated registration list. Nothing in the paper gives a working recipe against a named product. If a result looked like a flaw in a specific deployed system we would have withheld it and reported it to the maintainer.

## Appendix B Pre-registration

The hypotheses are quoted verbatim in `HYPOTHESES.md`, hash-locked (SHA-256 per file plus a combined digest) before the first main model call. Three amendments were recorded: a second-provider robustness subset; a larger output budget for one model whose reasoning had exhausted the original cap (33 of its first 70 calls returned an empty message); and a note that the auditability coding and hand checks were performed by AI instances at the author's instruction. Simulation hypotheses H5 to H7 were not blind (Section 5).

## LLM Usage Statement

AI assistants were used extensively. An AI coding assistant wrote the code, ran the experiments, drafted this report and built the site, working under the author's direction and instructions throughout. All model calls in the study go through Adaption's Responses API; two further instances of a language model acted as the two auditability coders, and an AI reader performed the hand checks of parse correctness and paraphrase fidelity, all at the author's instruction. The author set the research question, design and hypotheses and is responsible for every claim and reference. [CONFIRM BEFORE SUBMISSION: the author reviewed the outputs; delete this bracket only if true.] Every reference was opened and read before being cited; references that could not be opened are not cited. This report is therefore not primarily written by the author personally, and we say so.
