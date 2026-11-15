"""T5: corroboration count with near-duplicate defenses (MinHash, TF-IDF cosine)."""
import hashlib
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .. import config as C
from .base import Technique


def shingles(t, k=C.MINHASH_K):
    w = re.findall(r"\w+", t.lower())
    return {" ".join(w[i:i + k]) for i in range(max(1, len(w) - k + 1))}


def minhash(sh, n=C.MINHASH_PERM):
    return [min(int(hashlib.blake2b(f"{i}:{s}".encode(), digest_size=8).hexdigest(), 16) for s in sh)
            for i in range(n)]


def jaccard_est(a, b):
    return sum(x == y for x, y in zip(a, b)) / len(a)


def true_jaccard(a, b):
    return len(a & b) / max(1, len(a | b))


def _components(n, same):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in range(n):
        for j in range(i + 1, n):
            if same(i, j):
                parent[find(i)] = find(j)
    return len({find(i) for i in range(n)})


def count_clusters(texts, method, corpus=None):
    """Number of distinct clusters among texts. method: none, minhash, tfidf."""
    n = len(texts)
    if method == "none":
        return n
    if method == "minhash":
        sigs = [minhash(shingles(t)) for t in texts]
        return _components(n, lambda i, j: jaccard_est(sigs[i], sigs[j]) >= C.MINHASH_CUT)
    if method == "tfidf":
        vec = TfidfVectorizer().fit(corpus if corpus is not None else texts)
        X = vec.transform(texts)
        S = (X @ X.T).toarray()
        return _components(n, lambda i, j: S[i, j] >= C.TFIDF_CUT)
    raise ValueError(method)


class Corroboration(Technique):
    id = "T5"
    name = "Corroboration count"
    recompute_cmd = "python -m floorprice.cli technique T5 --defense none|minhash|tfidf"

    def __init__(self, defense="minhash", corpus=None):
        self.defense, self.corpus = defense, corpus

    def score_texts(self, texts):
        return count_clusters(texts, self.defense, self.corpus) / (C.CORROB_TAU + 1)

    def score(self, source):
        return self.score_texts(source) if isinstance(source, list) else float("nan")

    def threshold(self):
        return C.CORROB_TAU / (C.CORROB_TAU + 1)   # tau distinct clusters, on a 0..1 scale of tau + 1

    def inputs(self, source):
        return {"n_texts": len(source), "defense": self.defense, "tau": C.CORROB_TAU,
                "minhash_cut": C.MINHASH_CUT, "tfidf_cut": C.TFIDF_CUT}
