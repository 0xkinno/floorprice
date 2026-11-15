# Sources opened and read (URL, date read)

All read on 2026-11-15 through a fetch tool; quotes in the paper are only those listed here or in later rows.

| Source | URL | What was used |
|---|---|---|
| Community Notes ranking documentation (markdown source of the guide; the guide page itself returned HTTP 402 and was not paid for) | https://github.com/twitter/communitynotes/blob/main/documentation/under-the-hood/ranking-notes.md | prediction equation mu + i_u + i_n + f_u.f_n; lambda_i = 0.15, lambda_f = 0.03 (intercepts 5x factors); Helpful at intercept 0.40; abs(f_n) < 0.50; at least 5 ratings; gradient descent |
| Lin et al. 2023 data | https://github.com/hauselin/domain-quality-ratings | data/domain_pc1.csv, 11,520 domains |
| COTSI press release (University of Cambridge, 11 Dec 2025) | https://www.cam.ac.uk/stories/price-bot-army-global-index | US 0.26, UK 0.10, Japan 4.93, Meta 0.08, WhatsApp 1.02 USD per SMS verification; study period to July 2025 |
| COTSI methodology | https://www.cotsi.org/methodology | typical price around 50 cents; index design |
| Registrar price list | https://porkbun.com/products/domains and /tld/com, /tld/org, /tld/news | .com 11.81; .org 7.98 first year, 11.84 renewal; .news 9.78 first year, 29.35 renewal; low bound 1.28 |
| Adaption inference docs | https://docs.adaptionlabs.ai/inference-stacks/models/ | hosted model IDs and credit prices per million tokens |
| Adaption Responses API reference | https://docs.adaptionlabs.ai/api/resources/responses/methods/create | request and response shape |
| Adaptive Data evaluation docs | https://docs.adaptionlabs.ai/adaptive-data/evaluate-dataset-quality/ | dataset-level before and after scores on a 0 to 10 scale; per-row score not stated |

| Lin et al. 2023, PNAS Nexus 2(9), pgad286, DOI 10.1093/pnasnexus/pgad286 (title on the publisher page: "High level of correspondence across different news domain quality rating sets") | https://academic.oup.com/pnasnexus/article/doi/10.1093/pnasnexus/pgad286/7258994 | 11,520 domains; experts "generally agree on the relative quality of news domains" (abstract) |
| Yang and Menczer, arXiv:2304.00228 (v1 title "Large language models can rate news outlet credibility"; v3 title "Accuracy and Political Bias of News Source Credibility Ratings by Large Language Models", WebSci 2025) | https://arxiv.org/abs/2304.00228v1 | v1 abstract: ChatGPT ratings correlate with human experts, Spearman rho 0.54 |
| Gyongyi, Garcia-Molina, Pedersen, "Combating Web Spam with TrustRank" (PDF read in full text locally) | https://www.vldb.org/conf/2004/RS15P3.PDF | bogus pages pointing to a single target raise its rank; trust propagated from a seed set |
| Douceur, "The Sybil Attack", Microsoft Research, IPTPS 2002 (PDF read locally; abstract on the publication page) | https://www.microsoft.com/en-us/research/publication/the-sybil-attack/ | "without a logically centralized authority, Sybil attacks are always possible except under extreme and unrealistic assumptions" |
| Wojcik et al., "Birdwatch: Crowd Wisdom and Bridging Algorithms can Inform Understanding and Reduce the Spread of Misinformation", arXiv:2210.15723 (2022) | https://arxiv.org/abs/2210.15723 | matrix-factorisation bridging-based ranking on Birdwatch annotations |
| NewsGuard special report "Pink Slime Websites Infect AI Chatbots Ahead of U.S. Midterms" (page read; the report is behind a form, no counts stated on the page) | https://www.newsguardtech.com/special-reports/pink-slime-websites-infect-ai-chatbots-ahead-of-us-midterms-2 | existence and title only |

## Attempted and NOT opened, so NOT cited
- Gneiting and Raftery 2007 (JASA): publisher page returned 403. Not cited. The Brier score is described in plain words only.
- Tow Center for Digital Journalism pink-slime reporting: site returned 403.
- Medill State of Local News: site returned 503.
- A primary source for "cost of corruption versus profit from corruption": the two ethereum.org pages read do not define it. Not cited. The paper
  frames the idea in its own words and says it is borrowed from crypto-economic security practice without citing a definition.
Owner action: open these from a browser, and add them only after reading.
