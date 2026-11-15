# Auditability codebook (RQ4)

Code each technique twice: (a) our implementation in this repository, (b) the typical public deployment of that technique,
using only the saved documents in `evidence/snapshots/` (and, for (a), `evidence/our_implementation.md`). Code before looking at any cheat result.
Each criterion is 1 (yes, the document shows it) or 0 (not shown, or shown to be absent). If the document is silent, code 0 and write "silent" in notes.

| Criterion | Code 1 when the documents show that |
|---|---|
| inputs_public | the data or signals the score uses are publicly listed and obtainable by an outsider |
| method_public | the scoring procedure is described in enough detail to implement |
| deterministic | the same inputs always give the same score |
| recomputable | an outsider with the public inputs and method could recompute a given score |
| receipt | each score ships with an explanation or record of inputs and method |
| contest_path | there is a stated way to contest or appeal a score |

Techniques and the snapshot for deployment (b):
T1 static list: T1_wikipedia_perennial_sources, T1_newsguard_rating_process, T1_mbfc_methodology (code the list type as a group: if they differ, code the majority).
T2 LLM rater name only and T3 LLM rater with page text: T2_yang_menczer_abstract_v1, T3_adaption_responses_api.
T4 link graph: T4_trustrank_paper. T5 corroboration: T5_wikipedia_notability. T6 track record: T6_silver_bulletin_pollster_ratings.
T7 bridging: T7_communitynotes_ranking_notes, T7_birdwatch_abstract.

Output CSV columns: technique,deployment,inputs_public,method_public,deterministic,recomputable,receipt,contest_path,notes
with technique in T1,T2,T3,T4,T5,T6,T7 and deployment a or b (14 rows).
Files: `auditability_coder1.csv` (Kinnoski, human) and `auditability_coder2.csv` (blind model coder).
