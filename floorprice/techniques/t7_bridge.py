"""T7: bridging crowd ratings, Community Notes style (our implementation), vs simple majority. SIMULATED raters."""
import numpy as np

from .. import config as C
from .base import Technique


def fit_intercepts(R, M, dim=1, lam_i=0.15, lam_f=0.03, lr=0.3, iters=1500, seed=0):
    """R: raters x notes helpful(1)/not(0); M: observed mask. Defaults lr=0.3, iters=1500 (the starting-point values
    0.05 and 400 were checked and had not converged). Intercepts regularised ~5x factors,
    as in the published Community Notes description. Returns note intercepts and note factors."""
    rng = np.random.default_rng(seed)
    U, N = R.shape
    mu, iu, inn = 0.0, np.zeros(U), np.zeros(N)
    fu, fn = rng.normal(0, .1, (U, dim)), rng.normal(0, .1, (N, dim))
    cu, cn = np.maximum(M.sum(1), 1), np.maximum(M.sum(0), 1)
    for _ in range(iters):
        E = (mu + iu[:, None] + inn[None, :] + fu @ fn.T - R) * M
        mu -= lr * E.sum() / M.sum()
        iu -= lr * (E.sum(1) / cu + lam_i * iu)
        inn -= lr * (E.sum(0) / cn + lam_i * inn)
        fu -= lr * (E @ fn / cu[:, None] + lam_f * fu)
        fn -= lr * (E.T @ fu / cn[:, None] + lam_f * fn)
    return inn, fn


def is_helpful(intercept, factor):
    return bool(intercept >= C.T7_INTERCEPT_CUT and abs(float(np.ravel(factor)[0])) < C.T7_FACTOR_CUT)


def _background(rng, per):
    """Background notes by share C.T7_BG_MIX: universal, cluster-0, cluster-1, junk.
    Returns p_helpful as (notes x 2 clusters)."""
    nb = C.T7_BACKGROUND_NOTES
    edges = np.cumsum(C.T7_BG_MIX) * nb
    P = np.zeros((nb, 2))
    for j in range(nb):
        if j < edges[0]:
            P[j] = [C.T7_P_HELPFUL_TRUE] * 2
        elif j < edges[1]:
            P[j] = [0.8, 0.1]
        elif j < edges[2]:
            P[j] = [0.1, 0.8]
        else:
            P[j] = [C.T7_P_JUNK] * 2
    return P


def build_matrix(seed, n_colluders=0, target="false", k_max=None):
    """Raters: two honest clusters plus n_colluders accounts from cluster 0.
    The honest part depends only on the seed. Colluder rows are drawn once for k_max accounts and sliced,
    so a larger attack always contains the smaller one (monotone in k). Colluders rate background notes like
    cluster 0 so they look ordinary, and rate the target helpful.
    Returns R, M, index of the target note."""
    per = C.T7_PER_CLUSTER
    rng = np.random.default_rng([seed, 0])
    P = _background(rng, per)
    nb = P.shape[0]
    cl = np.array([0] * per + [1] * per)
    U = 2 * per
    R = np.zeros((U, nb + 1))
    M = np.zeros((U, nb + 1))
    M[:, :nb] = rng.random((U, nb)) < C.T7_RATE_PROB
    R[:, :nb] = (rng.random((U, nb)) < P[:, cl].T).astype(float)
    p = np.array([C.T7_P_FALSE_OWN, C.T7_P_FALSE_OTHER]) if target == "false" else np.array([C.T7_P_HELPFUL_TRUE] * 2)
    M[:, nb] = rng.random(U) < C.T7_RATE_PROB
    R[:, nb] = (rng.random(U) < p[cl]).astype(float)
    if n_colluders:
        km = max(k_max or 0, n_colluders)
        rc = np.random.default_rng([seed, 1])
        Mc = np.zeros((km, nb + 1))
        Rc = np.zeros((km, nb + 1))
        Mc[:, :nb] = rc.random((km, nb)) < C.T7_RATE_PROB
        Rc[:, :nb] = (rc.random((km, nb)) < P[:, 0][None, :]).astype(float)
        Mc[:, nb] = 1
        Rc[:, nb] = 1.0
        R = np.vstack([R, Rc[:n_colluders]])
        M = np.vstack([M, Mc[:n_colluders]])
    return R, M, nb


def majority_passes(R, M, j):
    m = M[:, j] > 0
    return bool(m.sum() >= C.T7_MIN_RATINGS and R[m, j].mean() >= 0.5)


def bridging_passes(R, M, j, seed=0):
    if M[:, j].sum() < C.T7_MIN_RATINGS:
        return False
    inn, fn = fit_intercepts(R, M, seed=seed)
    return is_helpful(inn[j], fn[j])


class Bridging(Technique):
    id = "T7"
    name = "Bridging crowd ratings"
    recompute_cmd = "python -m floorprice.cli sims --only t7"

    def __init__(self, method="bridging"):
        self.method = method

    def score(self, source):
        R, M, j = source
        if self.method == "majority":
            m = M[:, j] > 0
            return float(R[m, j].mean()) if m.any() else float("nan")
        inn, _ = fit_intercepts(R, M)
        return float(np.clip(inn[j], 0, 1))

    def threshold(self):
        return 0.5 if self.method == "majority" else C.T7_INTERCEPT_CUT

    def crosses(self, source):
        R, M, j = source
        return majority_passes(R, M, j) if self.method == "majority" else bridging_passes(R, M, j)

    def inputs(self, source):
        R, M, j = source
        return {"raters": int(R.shape[0]), "ratings_on_note": int(M[:, j].sum()), "method": self.method}
