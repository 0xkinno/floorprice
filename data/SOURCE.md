# Data sources

`lin_pc1.csv`: copy of `data/domain_pc1.csv` from https://github.com/hauselin/domain-quality-ratings
(Lin et al., 2023, PNAS Nexus, DOI 10.1093/pnasnexus/pgad286). 11,520 domains, `pc1` in [0, 1].
Downloaded 2026-11-15. The dataset authors' README permits reuse with citation.
SHA-256 of the downloaded file is recorded in `HYPOTHESES.lock` indirectly through the sample files.

`fabricated/`: fictional domains produced by `floorprice.data.make_fabricated` with a fixed seed.
Every row is marked `fictional=true`. None resolves to a site we checked against the Lin list.
`pages/`: fictional "about pages" produced by `floorprice.pages.build_pages`. Template text, not scraped.
