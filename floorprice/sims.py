"""S1 to S4 and the composite. All SIMULATED. Each function returns plain dicts; run_all writes results/sims/*.json."""
import json
from pathlib import Path

import numpy as np
from scipy import stats

from . import config as C
from .attacks import (TARGET, a6_link_farm, a7_bought_links, a9_long_con, a10_hugging, captured_stream, t4_crosses)
from .data import RELIABLE_CUT
from .floor import INF, gallop_binary, quantile_floor
from .techniques.t4_graph import build_graph, percentile_of, rank_scores
from .techniques.t6_record import (beta_reputation, claim_stream, consensus_relative, consensus_significant, gains)
from .techniques import t7_bridge as t7

OUT = Path(__file__).resolve().parent.parent / "results" / "sims"


def _q(floors):
    return {"p10": quantile_floor(floors, 0.1), "p50": quantile_floor(floors, 0.5), "p90": quantile_floor(floors, 0.9),
            "n": len(floors), "never": int(sum(f == INF for f in floors))}


# ---------------- S1 / T4 ----------------
def run_t4(seeds=C.SEEDS):
    res = {}
    for mode in ("pagerank", "trustrank"):
        farm, links, wait, seller_n = [], [], [], []
        for s in range(seeds):
            G, sd = build_graph(C.MASTER_SEED + s)
            ref = list(G.nodes)
            pr0 = rank_scores(G, sd, mode)
            band = [n for n, a in G.nodes(data=True) if a["q"] >= RELIABLE_CUT]
            thr = float(np.median([percentile_of(pr0, n, ref) for n in band]))
            farm.append(gallop_binary(lambda k: t4_crosses(a6_link_farm(G, k, s), sd, mode, ref, thr), C.FARM_CAP))
            nsell = len([1 for _, a in G.nodes(data=True) if C.MIDTRUST_BAND[0] <= a["q"] <= C.MIDTRUST_BAND[1]])
            cap = min(C.LINK_CAP, nsell)
            links.append(gallop_binary(lambda k: t4_crosses(a7_bought_links(G, k, s)[0], sd, mode, ref, thr), cap))
            seller_n.append(nsell)
            # honest newcomer: organic links from distinct reliable, non-seed domains
            rel = [n for n in band if n not in set(sd)]

            def honest(k, G=G, sd=sd, ref=ref, thr=thr, rel=rel, s=s):
                rng = np.random.default_rng([s, 9])
                H = G.copy()
                H.add_node(TARGET, q=1.0)
                for j in rng.choice(len(G), 3, replace=False):
                    H.add_edge(TARGET, list(G.nodes)[j])
                for i in rng.permutation(len(rel))[:k]:
                    H.add_edge(rel[i], TARGET)
                return t4_crosses(H, sd, mode, ref, thr)
            wait.append(gallop_binary(honest, min(len(rel), 2000)))
        res[mode] = {"A6_farm_domains": _q(farm), "A7_bought_links": _q(links), "honest_organic_links": _q(wait),
                     "sellers_available_median": float(np.median(seller_n))}
    return res


# ---------------- S4 / T6 ----------------
def first_n_beta(stream, thr):
    hits = np.cumsum([(ps >= 0.5) == bool(y) for ps, _, y in stream])
    n = np.arange(1, len(stream) + 1)
    ok = np.nonzero((1 + hits) / (2 + n) >= thr)[0]
    return int(ok[0] + 1) if len(ok) else INF


def first_n_consensus(stream):
    g = gains(stream)
    n = np.arange(1, len(g) + 1)
    cs = np.cumsum(g)
    cs2 = np.cumsum(g ** 2)
    mean = cs / n
    with np.errstate(divide="ignore", invalid="ignore"):
        var = (cs2 - n * mean ** 2) / (n - 1)
        t = mean / np.sqrt(var / n)
    crit = stats.t.ppf(1 - C.T6B_ALPHA, np.maximum(n - 1, 1))
    ok = np.nonzero((n >= C.T6B_MIN_N) & (var > 1e-12) & (t > crit))[0]
    return int(ok[0] + 1) if len(ok) else INF


def t6_threshold(seed=C.MASTER_SEED):
    rng = np.random.default_rng([seed, 60])
    return float(np.median([beta_reputation(claim_stream(C.T6_MATURE_N, rng, "informed")) for _ in range(500)]))


def run_t6(seeds=C.SEEDS):
    thr = t6_threshold()
    out = {"beta_threshold": thr}
    cols = {"honest_T6a": [], "honest_T6b": [], "A9_T6a": [], "A9_T6b": [], "A10_T6a": [], "A10_T6b": [],
            "capture_T6b": []}
    for s in range(seeds):
        rng = np.random.default_rng([C.MASTER_SEED, 61, s])
        h = claim_stream(C.T6_HORIZON, rng, "informed")
        cols["honest_T6a"].append(first_n_beta(h, thr))
        cols["honest_T6b"].append(first_n_consensus(h))
        c = a9_long_con(C.T6_HORIZON, rng)
        cols["A9_T6a"].append(first_n_beta(c, thr))
        cols["A9_T6b"].append(first_n_consensus(c))
        g = a10_hugging(C.T6_HORIZON, rng)
        cols["A10_T6a"].append(first_n_beta(g, thr))
        cols["A10_T6b"].append(first_n_consensus(g))
        cols["capture_T6b"].append(first_n_consensus(captured_stream(C.T6_HORIZON, rng)))
    for k, v in cols.items():
        out[k] = _q(v)
    return out


def run_t6_sensitivity(seeds=C.SEEDS):
    """T6 with the informed source's noise at 0.05 and 0.12 (base 0.10). Restores the base value afterwards."""
    base = C.SIGMA_INFORMED
    out = {}
    try:
        for sig in (0.05, 0.12):
            C.SIGMA_INFORMED = sig
            out[str(sig)] = run_t6(seeds)
    finally:
        C.SIGMA_INFORMED = base
    return out


# ---------------- S5 / T7 ----------------
def _passes(R, M, j, method, seed):
    return t7.majority_passes(R, M, j) if method == "majority" else t7.bridging_passes(R, M, j, seed=seed)


def run_t7(seeds=C.SEEDS):
    out = {}
    for method in ("majority", "bridging"):
        floors, honest_pass, honest_wait = [], [], []
        for s in range(seeds):
            kmax = C.T7_ACCOUNT_CAP
            floors.append(gallop_binary(
                lambda k: _passes(*t7.build_matrix(s, k, "false", k_max=kmax), method, s), C.T7_ACCOUNT_CAP))
            R, M, j = t7.build_matrix(s, 0, "true")
            honest_pass.append(_passes(R, M, j, method, s))

            def at(m, s=s):
                R, M, j = t7.build_matrix(s, 0, "true")
                idx = np.nonzero(M[:, j] > 0)[0]
                rng = np.random.default_rng([s, 77])
                # all raters are available to rate; m of them actually have
                pool = rng.permutation(R.shape[0])[:m]
                M2 = M.copy()
                M2[:, j] = 0
                M2[pool, j] = 1
                return _passes(R, M2, j, method, s)
            honest_wait.append(gallop_binary(at, 2 * C.T7_PER_CLUSTER, start=C.T7_MIN_RATINGS))
        out[method] = {"A11_accounts": _q(floors), "honest_pass_rate": float(np.mean(honest_pass)),
                       "honest_ratings_needed": _q(honest_wait)}
    out["false_note_unattacked_pass"] = {
        m: float(np.mean([_passes(*t7.build_matrix(s, 0, "false"), m, s) for s in range(seeds)]))
        for m in ("majority", "bridging")}
    return out


# ---------------- composite C* ----------------
def run_composite(t6=None, t7res=None, seeds=C.SEEDS):
    """C* = consensus-relative track record gated by bridging for disputed claims, with the LLM rater allowed only to
    lower a score. The LLM veto is applied from E3 data in analyze.py; here the model-free parts are simulated.
    Honest wait: disputed claims count only when their resolution passes bridging, with the pass rate measured in run_t7.
    Attack: resolution capture, priced as the cost of passing the resolution rule on a false resolution."""
    t7res = t7res or run_t7(seeds)
    b = t7res["bridging"]["honest_pass_rate"]
    waits, base = [], []
    for s in range(seeds):
        # identical informed claim stream to run_t6, so the comparison with T6b alone is paired
        st = claim_stream(C.T6_HORIZON, np.random.default_rng([C.MASTER_SEED, 61, s]), "informed")
        drop = np.random.default_rng([C.MASTER_SEED, 62, s])
        keep = [x for x in st if not (drop.random() < C.DISPUTED_FRAC and drop.random() > b)]
        waits.append(first_n_consensus(keep))
        base.append(first_n_consensus(st))
    return {"bridge_honest_pass_rate_used": b, "honest_T6b_gated_claims": _q(waits), "honest_T6b_ungated_same_stream": _q(base)}


def run_all(only=None, seeds=C.SEEDS):
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {"t4": run_t4, "t6": run_t6, "t6sens": run_t6_sensitivity, "t7": run_t7}
    results = {}
    for name, fn in jobs.items():
        if only and name not in only:
            continue
        results[name] = fn(seeds)
        (OUT / f"{name}.json").write_text(json.dumps(results[name], indent=2, default=lambda x: "inf" if x == INF else x))
    if not only or "cstar" in only:
        t7res = results.get("t7") or json.loads((OUT / "t7.json").read_text())
        results["cstar"] = run_composite(t7res=t7res, seeds=seeds)
        (OUT / "cstar.json").write_text(json.dumps(results["cstar"], indent=2, default=lambda x: "inf" if x == INF else x))
    return results
