"""T6: track record. (a) Beta reputation on accuracy. (b) consensus-relative score:
sum of Brier(consensus) minus Brier(source) on resolved claims. SIMULATED claim streams."""
import numpy as np
from scipy import stats

from .. import config as C
from .base import Technique


def consensus_relative(stream):
    """stream: list of (p_source, p_consensus, outcome in {0,1}). Restating the consensus earns about 0;
    only information the crowd lacked earns credit."""
    return sum((pc - y) ** 2 - (ps - y) ** 2 for ps, pc, y in stream)


def beta_reputation(stream, a=1, b=1):
    hits = sum(1 for ps, _, y in stream if (ps >= 0.5) == bool(y))
    return (a + hits) / (a + b + len(stream))


def gains(stream):
    return np.array([(pc - y) ** 2 - (ps - y) ** 2 for ps, pc, y in stream])


def consensus_significant(stream, alpha=C.T6B_ALPHA, min_n=C.T6B_MIN_N):
    """One-sided t test that the mean per-claim Brier gain over the consensus is above zero."""
    g = gains(stream)
    if len(g) < min_n:
        return False
    sd = g.std(ddof=1)
    if sd < 1e-12:
        return False          # zero variance with zero mean: no evidence of information
    t = g.mean() / (sd / np.sqrt(len(g)))
    return bool(t > stats.t.ppf(1 - alpha, len(g) - 1))


def claim_stream(n, rng, kind="informed"):
    """Simulated claims. kind: informed (honest, better informed than consensus), hugger (restates consensus),
    con (only easy claims, always right, states the consensus)."""
    out = []
    for _ in range(n):
        easy = True if kind == "con" else rng.random() < C.EASY_FRAC
        theta = rng.choice([0.05, 0.95]) + rng.normal(0, 0.02) if easy else rng.uniform(0.3, 0.7)
        theta = float(np.clip(theta, 0.01, 0.99))
        y = int(rng.random() < theta)
        pc = float(np.clip(theta + rng.normal(0, C.SIGMA_CONSENSUS), 0.01, 0.99))
        if kind == "informed":
            ps = float(np.clip(theta + rng.normal(0, C.SIGMA_INFORMED), 0.01, 0.99))
        elif kind == "hugger":
            ps = pc
        else:  # con: easy claims, outcome forced to the stated direction, states the consensus
            y = int(theta > 0.5)
            ps = pc
        out.append((ps, pc, y))
    return out


class TrackRecordBeta(Technique):
    id = "T6a"
    name = "Track record, accuracy (Beta)"
    recompute_cmd = "python -m floorprice.cli sims --only t6"

    def __init__(self, threshold=None, seed=C.MASTER_SEED):
        if threshold is None:
            rng = np.random.default_rng(seed)
            vals = [beta_reputation(claim_stream(C.T6_MATURE_N, rng, "informed")) for _ in range(500)]
            threshold = float(np.median(vals))
        self._thr = threshold

    def score(self, source):
        return beta_reputation(source)

    def threshold(self):
        return self._thr

    def inputs(self, source):
        return {"n_claims": len(source)}


class TrackRecordConsensus(Technique):
    id = "T6b"
    name = "Track record, consensus-relative"
    recompute_cmd = "python -m floorprice.cli sims --only t6"

    def score(self, source):
        return consensus_relative(source)

    def threshold(self):
        return 0.0     # the crossing rule is the significance test; see crosses()

    def crosses(self, source):
        return consensus_significant(source)

    def inputs(self, source):
        return {"n_claims": len(source), "alpha": C.T6B_ALPHA, "min_n": C.T6B_MIN_N}
