"""T1: static expert list. Lookup in pc1; the unknown-domain policy is a parameter."""
import numpy as np

from ..data import RELIABLE_CUT, load_lin
from .base import Technique

UNKNOWN_POLICIES = {"neutral": 0.5, "untrusted": 0.0, "trusting": 1.0}


class StaticList(Technique):
    id = "T1"
    name = "Static expert list"
    recompute_cmd = "python -m floorprice.cli technique T1 <domain>"

    def __init__(self, df=None, unknown="neutral"):
        df = load_lin() if df is None else df
        self.table = dict(zip(df.domain, df.pc1))
        self.unknown = unknown
        self._thr = float(np.median(df[df.pc1 >= RELIABLE_CUT].pc1))

    def score(self, source):
        return float(self.table.get(source.lower(), UNKNOWN_POLICIES[self.unknown]))

    def threshold(self):
        return self._thr

    def inputs(self, source):
        return {"source": source, "listed": source.lower() in self.table, "policy": self.unknown}
