# task.md  (ordered by dependency)

## Phase 0. Setup and rules
- [x] Create repo `floorprice` locally (private until Kinnoski approves going public); git user set to 0xkinno. Remote URL not yet provided
- [x] CI green (identity test fixed). [x] Install .githooks/commit-msg and .github/workflows/no-claude-attribution.yml; core.hooksPath set
- [x] .gitignore: reference/, .env, results/raw/*.tmp, node_modules, site/dist
- [x] PRE_SPRINT.md: "nothing existed before 15 Nov 2026"
- [ ] RULES_EXTRACT.md from the sprint page, Guidelines tab and form fields (started from the brief and the sprint template repo; Guidelines tab text still needed from Kinnoski)
- [x] reference/: cloned the repos in Section 12 (13 repos); LANE_MAP.md written from the brief's lane table (gitignored)

## Phase 1. Probe and design (G1, G2, G5, G6)
- [x] scripts/probe.py written. [ ] PLATFORM_PROBE.md with working model IDs, latency, credits per call (BLOCKED: needs ADAPTION_API_KEY)
- [x] SDK_SURFACE.md started from the public docs. [ ] Adaptive Data live probe (BLOCKED: key)
- [x] MOMENT.md with sourced "What is true / Source" table (opened links only; Tow Center and Medill could not be opened, not used)
- [x] Download Lin et al. data with source note; stratified samples; fabricated-domain generator; page variants
- [x] data/prices.yaml with sources, dates, low/high
- [x] HYPOTHESES.md (Section 4.8), PROOF_PLAN.md
- [x] scripts/prereg_lock.py; [x] HYPOTHESES.lock committed BEFORE any main call (no main call has been made)

## Phase 2. Real-model experiments (running; key limit about 25 requests per minute, about 5 hours for all)
- [x] llm.py, cache.py, budget.py with tests (offline replay, budget stop, resume without duplicates)
- [x] E1 validity  - [x] E2 unknown prior and prestige  - [x] E3 page attacks (and E3h)  - [x] E4 stability  - [x] E5 paraphrases (74 of 6,288 qwen calls failed with HTTP 504 and are reported as missing)
- [x] Parse-failure and "unknown" label counts per model recorded

## Phase 3. Simulations and composite
- [x] T1 list with unknown-domain policies  - [x] T4 PageRank vs TrustRank  - [x] T5 corroboration + MinHash/TF-IDF
- [x] T6 Beta vs consensus-relative  - [x] T7 bridging vs majority  - [x] C* composite (model-free parts; LLM veto needs E3 data)
- [x] floor.py search for every simulated technique x attack; honest wait for every simulated technique

## Phase 4. Human loop
- [x] Save documentation snapshots to evidence/snapshots/ (URL, date)
- [x] Coder 1 done by a blind AI instance at the author's instruction (disclosed; amendment recorded)
- [x] Blind model coder (coder 2) done. [x] scripts/agreement.py -> kappa 0.90, 4 disagreements
- [x] Hand checks of 100 parses and 50 paraphrases by an AI reader (disclosed): 0 of 100 parses wrong, 1 of 50 paraphrases lost meaning

## Phase 5. Analysis and numbers
- [x] analyze.py: CIs, Holm, sensitivity code (needs data for the real-model parts)
- [x] figures.py written. [x] Figure 1 (headline), Table 2, per-model appendix tables
- [x] facts.py -> FACTS.json; numbers.py -> REPORT_NUMBERS.md; placeholder check
- [x] Hypothesis scorecard written honestly (H1 and H4 supported, H2 and H3 not, H5 to H7 simulated and not blind)

## Phase 6. Report
- [x] report/FLOORPRICE_report.md complete from FACTS (assembled by scripts/assemble_report.py from report/parts)
- [x] evidence/sources.md lists URL and date read (only opened sources are cited)
- [x] build_report.py works (fallback mode, official template not provided). [ ] Kinnoski places report/template.docx and exports PDF
- [ ] Mock judge review rounds until clean (REDTEAM_LOG.md), after the first full draft
- [x] check_style.py passes on report, README, site copy (current files)

## Phase 7. README, site, extras
- [x] README per Section 8 with real findings (banner is the landing page; 2x2 grid not added by request)
- [x] site/ built, Playwright viewport and axe gates pass (re-export data when results are frozen). [x] Vercel deploy: https://floorprice-puce.vercel.app (project floorprice, root site, auto-deploys on push)
- [ ] Project image, optional deck, optional video

## Phase 8. Submit (G10, G11)
- [ ] SUBMISSION_APART.md mirrors the live form field by field
- [ ] Clean-clone reproduction: `make reproduce` with FLOORPRICE_OFFLINE=1 rebuilds FACTS and figures
- [ ] Kinnoski submits
- [ ] Confirmation email checked; tag the commit `submitted-apart-2026-11`; freeze
