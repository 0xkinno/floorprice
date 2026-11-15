"""All simulation parameters and fixed cuts. Hashed into HYPOTHESES.lock. Every value here is an assumption
unless a comment says it comes from a cited source."""

SEEDS = 20                      # simulation seeds per scenario
MASTER_SEED = 20261115

# T4 synthetic web graph over real domain names (SIMULATED)
GRAPH_N = 1500
GRAPH_MEAN_OUT = 8
GRAPH_ALPHA = 3.0               # prestige exponent on target quality
GRAPH_HOMOPHILY = 0.3           # width of quality-similarity kernel
GRAPH_SEEDS = 25                # TrustRank seed set: top-quality listed domains
DAMPING = 0.85                  # standard PageRank damping
FARM_CAP = 5000                 # largest link farm tried
LINK_CAP = 2000                 # largest number of bought links tried
MIDTRUST_BAND = (0.4, 0.6)      # pc1 band of the nodes links are bought from

# T5 corroboration
CORROB_TAU = 3                  # distinct independent sources needed (documented cut, assumption)
MINHASH_K = 5                   # shingle width
MINHASH_PERM = 128
MINHASH_CUT = 0.5               # estimated Jaccard at or above this means same cluster
TFIDF_CUT = 0.5                 # cosine at or above this means same cluster

# T6 claim streams (SIMULATED)
SIGMA_CONSENSUS = 0.15          # consensus noise around the latent probability
SIGMA_INFORMED = 0.10           # honest informed source noise (information the crowd lacked)
EASY_FRAC = 0.5                 # share of claims that are easy
T6_HORIZON = 500                # articles
T6_MATURE_N = 50                # T6a threshold: median beta score of the informed reference source at this n
T6B_ALPHA = 0.05                # one-sided significance for the consensus-relative test
T6B_MIN_N = 5

# T7 bridging (SIMULATED raters)
T7_PER_CLUSTER = 100
T7_BACKGROUND_NOTES = 60
T7_BG_MIX = (1/6, 1/6, 1/6, 1/2)   # share of background notes: universal, cluster-0, cluster-1, junk (rated unhelpful by both).
                                   # Assumption: most notes in a real pool are not helpful, which lowers the global intercept.
T7_P_JUNK = 0.1
T7_RATE_PROB = 0.3              # chance a rater rates a given note
T7_P_HELPFUL_TRUE = 0.85        # both clusters rate a true note helpful with this probability
T7_P_FALSE_OWN = 0.6            # sympathetic cluster rates the false note helpful
T7_P_FALSE_OTHER = 0.1          # other cluster rates it helpful
T7_INTERCEPT_CUT = 0.40         # Community Notes helpful-note intercept threshold (verify, cite)
T7_FACTOR_CUT = 0.5
T7_ACCOUNT_CAP = 3000
T7_MIN_RATINGS = 5              # a note needs at least this many ratings under both rules (Community Notes also requires a minimum)

# Composite C*
DISPUTED_FRAC = 0.2             # share of claims whose resolution is disputed
BRIDGE_PASS_HONEST = 0.6        # chance a disputed but honest resolution passes bridging (assumption)

# Honest-newcomer arrival rates (per day), assumptions reported as low, mid, high
# Native units are primary. Time conversions use these assumed arrival rates (events per day); no citable source,
# so the paper reports them as assumptions with a range.
HONEST_RATES = {
    "links":   {"low": 0.03, "mid": 0.1, "high": 0.3},    # organic links from reliable domains
    "pickups": {"low": 0.1,  "mid": 0.3, "high": 1.0},    # independent outlets repeating a true story
    "claims":  {"low": 0.2,  "mid": 0.5, "high": 1.0},    # resolved claims published
    "ratings": {"low": 5.0,  "mid": 20.0, "high": 100.0}, # crowd ratings landing on a note
}
