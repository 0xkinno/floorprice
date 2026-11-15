import json

import numpy as np

from floorprice import config as C
from floorprice.data import load_lin, make_fabricated, stratified_sample, stem_names
from floorprice.floor import INF, gallop_binary, geometric_floor, ladder_floor, quantile_floor
from floorprice.receipt import make_receipt, verify
from floorprice.techniques.t1_list import StaticList
from floorprice.techniques.t5_corrob import count_clusters
from floorprice.techniques.t6_record import beta_reputation, consensus_relative, consensus_significant, claim_stream
from floorprice.analyze import cohen_kappa, holm, wilson, spearman_boot


def test_floor_helpers():
    assert gallop_binary(lambda k: k >= 37, 5000) == 37
    assert gallop_binary(lambda k: False, 100) == INF
    assert gallop_binary(lambda k: True, 100) == 0
    assert ladder_floor([0, 30, 54], [0.1, 0.6, 0.9], 0.5) == 30
    assert ladder_floor([0, 30], [0.1, 0.2], 0.5) == INF
    assert quantile_floor([1, 2, 3, INF], 0.5) == 2 and quantile_floor([1, INF, INF, INF], 0.5) == INF
    assert geometric_floor(0.0) == INF and geometric_floor(1.0) == 1 and geometric_floor(0.5) == 1


def test_receipt_digest_roundtrip_and_tamper():
    r = make_receipt("a.com", "T1", "0.1.0", {"x": 1}, 0.9, 0.8, "make reproduce")
    assert verify(r) and r["verdict"] == "reliable"
    r["score"] = 0.1
    assert not verify(r)


def test_t1_unknown_policies_never_cross():
    for pol in ("neutral", "untrusted"):
        t = StaticList(unknown=pol)
        assert not t.crosses("never-seen-xyz.example")
    assert StaticList(unknown="trusting").crosses("never-seen-xyz.example")
    assert StaticList().crosses("reuters.com")


def test_fabricated_domains_disjoint_from_lin_and_deterministic():
    lin = set(load_lin().domain)
    a, b = make_fabricated(lin), make_fabricated(lin)
    assert a == b and len(a) == 252 and not ({r["domain"] for r in a} & lin)
    assert all(r["fictional"] == "true" for r in a)
    assert len(stem_names(lin, 14)) == 14


def test_stratified_sample_is_even():
    s = stratified_sample(load_lin())
    assert len(s) == 400 and s.decile.value_counts().nunique() == 1


def test_t6_properties():
    rng = np.random.default_rng(1)
    hug = claim_stream(300, rng, "hugger")
    assert abs(consensus_relative(hug)) < 1e-9 and not consensus_significant(hug)
    con = claim_stream(50, rng, "con")
    assert beta_reputation(con) > 0.9 and not consensus_significant(con)
    # proper scoring: extremising a calibrated consensus does not pay in expectation
    r = np.random.default_rng(2)
    ps, pc = 0.99, 0.9
    ys = (r.random(20000) < 0.9).astype(int)
    assert sum((pc - y) ** 2 - (ps - y) ** 2 for y in ys) < 0


def test_t5_clusters():
    a = "the city council voted on tuesday to approve a new budget for roads and schools across the county this year"
    assert count_clusters([a, a, a], "minhash") == 1
    assert count_clusters([a, a, a], "none") == 3
    b = "lawmakers in the town backed a spending plan on tuesday that covers road repair and school funding countywide for twelve months"
    assert count_clusters([a, b], "minhash") == 2


def test_stats_helpers():
    assert abs(cohen_kappa([1, 0, 1, 0], [1, 0, 1, 0]) - 1) < 1e-9
    assert cohen_kappa([1, 1, 0, 0], [0, 0, 1, 1]) < 0
    h = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert h["a"] == 0.03 and h["c"] <= h["b"] + 1e-12
    lo, hi = wilson(0, 10)
    assert lo == 0 or lo < 1e-9
    assert hi > 0.2
    x = np.arange(100.0)
    r = spearman_boot(x, x + np.random.default_rng(0).normal(0, 5, 100), np.arange(100), n_boot=50)
    assert r["rho"] > 0.9
