# task.md  (ordered by dependency)

## Phase 0. Setup and rules
- [x] Create repo `floorprice` locally (private until Kinnoski approves going public); git user set to 0xkinno. Remote URL not yet provided
- [x] Install .githooks/commit-msg and .github/workflows/no-claude-attribution.yml; core.hooksPath set
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
- [ ] E1 validity  - [ ] E2 unknown prior and prestige  - [ ] E3 page attacks (and E3h)  - [ ] E4 stability  - [ ] E5 paraphrases
- [ ] Parse-failure and "unknown" label counts per model recorded (code written in analyze.py; needs data)

## Phase 3. Simulations and composite
- [x] T1 list with unknown-domain policies  - [x] T4 PageRank vs TrustRank  - [ ] T5 corroboration + MinHash/TF-IDF (code and tests done; floor needs E5 paraphrases)
- [x] T6 Beta vs consensus-relative  - [x] T7 bridging vs majority  - [x] C* composite (model-free parts; LLM veto needs E3 data)
- [x] floor.py search for every simulated technique x attack; honest wait for every simulated technique

## Phase 4. Human loop
- [x] Save documentation snapshots to evidence/snapshots/ (URL, date)
- [ ] Kinnoski codes auditability (coder 1) BEFORE viewing cheat results (HUMAN STEP; template at evidence/auditability_coder1_TEMPLATE.csv)
- [x] Blind model coder (coder 2) done. [ ] scripts/agreement.py -> kappa and disagreements (needs coder 1)
- [ ] Kinnoski hand-checks 100 rater parses and 50 paraphrases (HUMAN STEP; needs E1 and E5 data to prepare the CSVs)

## Phase 5. Analysis and numbers
- [x] analyze.py: CIs, Holm, sensitivity code (needs data for the real-model parts)
- [x] figures.py written. [ ] Figure 1 (headline), Table 2, per-model appendix figures (need real-model results and coder 1)
- [x] facts.py -> FACTS.json; numbers.py -> REPORT_NUMBERS.md; placeholder check
- [ ] Hypothesis scorecard (supported / not / partly) written honestly (H5 to H7 from simulations only until model data exists)

## Phase 6. Report
- [x] report/FLOORPRICE_report.md skeleton with {{fact:}} placeholders. [ ] Complete once real results exist
- [x] evidence/sources.md lists URL and date read (only opened sources are cited)
- [x] build_report.py works (fallback mode, official template not provided). [ ] Kinnoski places report/template.docx and exports PDF
- [ ] Mock judge review rounds until clean (REDTEAM_LOG.md), after the first full draft
- [x] check_style.py passes on report, README, site copy (current files)

## Phase 7. README, site, extras
- [ ] README per Section 8 (draft only; final needs results)
- [x] site/ built, Playwright viewport and axe gates pass (re-export data when results are frozen). [x] Vercel deploy: https://floorprice-puce.vercel.app (project floorprice, root site, auto-deploys on push)
- [ ] Project image, optional deck, optional video

## Phase 8. Submit (G10, G11)
- [ ] SUBMISSION_APART.md mirrors the live form field by field
- [ ] Clean-clone reproduction: `make reproduce` with FLOORPRICE_OFFLINE=1 rebuilds FACTS and figures
- [ ] Kinnoski submits
- [ ] Confirmation email checked; tag the commit `submitted-apart-2026-11`; freeze
