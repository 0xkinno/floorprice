import numpy as np

from floorprice import config as C
from floorprice.techniques import t7_bridge as t7
from floorprice import sims


def test_bridging_simulator_validity_check():
    """Fixed in HYPOTHESES.md: true note passes in at least 80% of seeds, unattacked false note in at most 5%."""
    n = 10
    tp = np.mean([t7.bridging_passes(*t7.build_matrix(s, 0, "true"), seed=s) for s in range(n)])
    fp = np.mean([t7.bridging_passes(*t7.build_matrix(s, 0, "false"), seed=s) for s in range(n)])
    assert tp >= 0.8 and fp <= 0.05


def test_colluder_prefix_property():
    R1, M1, j = t7.build_matrix(3, 10, "false", k_max=50)
    R2, M2, j2 = t7.build_matrix(3, 50, "false", k_max=50)
    assert np.array_equal(R1, R2[:R1.shape[0]]) and np.array_equal(M1, M2[:M1.shape[0]])


def test_majority_needs_min_ratings():
    R = np.ones((3, 2))
    M = np.ones((3, 2))
    assert not t7.majority_passes(R, M, 1)


def test_t6_first_n_functions():
    rng = np.random.default_rng(0)
    from floorprice.techniques.t6_record import claim_stream
    con = claim_stream(100, rng, "con")
    assert sims.first_n_consensus(con) == float("inf")
    assert sims.first_n_beta(con, 0.7) <= 3
