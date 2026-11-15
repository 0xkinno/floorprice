"""Floor-price search. The floor is the lowest rung at which at least p of attempts cross the technique's
threshold (p = 0.5 is the median floor price; 0.1 and 0.9 are reported too). No interpolation in headlines."""
import math

import yaml

INF = float("inf")


def quantile_floor(floors, p):
    """floors: per-attempt minimum cost (INF when never crossed). Lowest cost x with at least p of attempts <= x."""
    xs = sorted(floors)
    if not xs:
        return INF
    return xs[max(math.ceil(p * len(xs)) - 1, 0)]


def gallop_binary(pred, cap, start=1):
    """Smallest k in [0, cap] with pred(k) true, assuming pred is monotone in k. INF if pred(cap) is false.
    pred(0) true means the target crosses with no attack."""
    if pred(0):
        return 0
    k, lo = start, 0
    while k < cap and not pred(k):
        lo, k = k, min(k * 2, cap)
    if not pred(k):
        return INF
    hi = k
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid
    return hi


def ladder_floor(rungs, rates, p=0.5):
    """rungs: costs in ascending order; rates: success rate at each rung. Lowest rung with rate >= p, else INF."""
    for c, r in zip(rungs, rates):
        if r >= p:
            return c
    return INF


def geometric_floor(p_cross, p=0.5):
    """Independent tries (new domains, each crossing with probability p_cross): fewest tries so that at least one
    crosses in a share p of attempts. INF if p_cross is zero."""
    if p_cross <= 0:
        return INF
    if p_cross >= 1:
        return 1
    return max(1, math.ceil(math.log(1 - p) / math.log(1 - p_cross)))


def load_prices(path=None):
    from pathlib import Path
    path = path or Path(__file__).resolve().parent.parent / "data" / "prices.yaml"
    return yaml.safe_load(open(path, encoding="utf-8"))


def dollars(units, unit_price):
    """unit_price: dict(low, mid, high) in dollars. Returns the same keys; INF stays INF."""
    return {k: (INF if units == INF else units * v) for k, v in unit_price.items()}
