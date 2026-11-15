"""Attack constructors. Every attack runs against our own implementations on generated or public data."""
import numpy as np

from . import config as C
from .techniques.t4_graph import percentile_of, rank_scores
from .techniques.t6_record import claim_stream

TARGET = "attacker-target.example"


def _with_target(G, rng, outlinks=3):
    H = G.copy()
    H.add_node(TARGET, q=0.0)
    nodes = [n for n in G.nodes]
    for j in rng.choice(len(nodes), outlinks, replace=False):
        H.add_edge(TARGET, nodes[j])
    return H


def a6_link_farm(G, k, seed):
    """k new domains, none linked from any seed. Each farm domain links to the target and to two farm peers;
    the target links back into the farm."""
    rng = np.random.default_rng([seed, 6])
    H = _with_target(G, rng)
    farm = [f"farm{i}.example" for i in range(k)]
    for f in farm:
        H.add_node(f, q=0.0)
    for i, f in enumerate(farm):
        H.add_edge(f, TARGET)
        if k > 2:
            for j in rng.choice(k, 2, replace=False):
                if farm[j] != f:
                    H.add_edge(f, farm[j])
    for f in farm[:3]:
        H.add_edge(TARGET, f)
    return H


def a7_bought_links(G, k, seed, band=C.MIDTRUST_BAND):
    """k links from distinct mid-trust domains to the target (one link per seller domain)."""
    rng = np.random.default_rng([seed, 7])
    H = _with_target(G, rng)
    sellers = [n for n, a in G.nodes(data=True) if band[0] <= a["q"] <= band[1]]
    order = rng.permutation(len(sellers))
    for i in order[:k]:
        H.add_edge(sellers[i], TARGET)
    return H, len(sellers)


def t4_crosses(H, seeds, mode, reference, thr):
    pr = rank_scores(H, seeds, mode)
    return percentile_of(pr, TARGET, reference) >= thr


def a9_long_con(n, rng):
    return claim_stream(n, rng, "con")


def a10_hugging(n, rng):
    return claim_stream(n, rng, "hugger")


def captured_stream(n, rng):
    """Resolution capture: the attacker asserts claims the crowd rates as unlikely (p_source high, consensus low),
    then captures the resolution so the outcome is recorded as 1. Used against track records whose resolutions
    come from crowd rating."""
    out = []
    for _ in range(n):
        pc = float(np.clip(rng.normal(0.2, 0.05), 0.01, 0.99))
        ps = float(np.clip(rng.normal(0.9, 0.03), 0.01, 0.99))
        out.append((ps, pc, 1))
    return out
