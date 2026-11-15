"""T4: link-graph rank. PageRank vs TrustRank seeded from T1, on a SIMULATED web graph over real domain names."""
import numpy as np
import networkx as nx

from .. import config as C
from ..data import RELIABLE_CUT, load_lin
from .base import Technique


def build_graph(seed=C.MASTER_SEED, n=C.GRAPH_N, df=None):
    df = load_lin() if df is None else df
    rng = np.random.default_rng(seed)
    d = df.sample(n, random_state=seed).reset_index(drop=True)
    q = d.pc1.to_numpy()
    G = nx.DiGraph()
    for i, dom in enumerate(d.domain):
        G.add_node(dom, q=float(q[i]))
    names = d.domain.to_numpy()
    for i in range(n):
        w = (q + 0.05) ** C.GRAPH_ALPHA * np.exp(-np.abs(q[i] - q) / C.GRAPH_HOMOPHILY)
        w[i] = 0
        w = w / w.sum()
        k = max(1, rng.geometric(1.0 / C.GRAPH_MEAN_OUT))
        for j in rng.choice(n, size=min(k, n - 1), replace=False, p=w):
            G.add_edge(names[i], names[j])
    order = np.argsort(-q)
    seeds = [names[i] for i in order[:C.GRAPH_SEEDS]]
    return G, seeds


def rank_scores(G, seeds, mode):
    if mode == "pagerank":
        pr = nx.pagerank(G, alpha=C.DAMPING, tol=1e-10, max_iter=200)
    else:
        pers = {s: 1.0 / len(seeds) for s in seeds}
        pr = nx.pagerank(G, alpha=C.DAMPING, personalization=pers, tol=1e-10, max_iter=200)
    return pr


def percentile_of(pr, node, reference):
    """Share of the reference nodes whose score is at or below the node's. Reference excludes attacker nodes,
    so a farm cannot move the scale it is measured against."""
    v = pr[node]
    ref = np.array([pr[r] for r in reference])
    return float((ref <= v).mean())


class GraphRank(Technique):
    id = "T4"
    name = "Link-graph rank"
    recompute_cmd = "python -m floorprice.cli technique T4 <domain> --mode pagerank|trustrank"

    def __init__(self, mode="trustrank", seed=C.MASTER_SEED):
        self.mode = mode
        self.G, self.seeds = build_graph(seed)
        self.reference = list(self.G.nodes)
        self.pr = rank_scores(self.G, self.seeds, mode)
        band = [n for n, a in self.G.nodes(data=True) if a["q"] >= RELIABLE_CUT]
        self._thr = float(np.median([percentile_of(self.pr, n, self.reference) for n in band]))

    def score(self, source):
        return percentile_of(self.pr, source, self.reference)

    def threshold(self):
        return self._thr

    def inputs(self, source):
        return {"source": source, "mode": self.mode, "inlinks": self.G.in_degree(source), "seeds": len(self.seeds)}
