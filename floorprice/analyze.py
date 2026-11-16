"""Analysis: Spearman with item-bootstrap CIs, paired differences, Wilson intervals, Holm, floor prices, honest waits,
auditability agreement. Reads results/main, results/sims and evidence/*.csv. Anything not yet measured is listed under
`pending`, never filled in."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from . import config as C
from .floor import INF, geometric_floor, ladder_floor, load_prices
from .techniques.t5_corrob import count_clusters, jaccard_est, minhash, shingles
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
BOOT = 2000
RNG_SEED = 20261115


# ---------------- statistics ----------------
def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values for a dict name -> p."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, run = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def spearman_boot(x, y, groups, n_boot=BOOT, seed=RNG_SEED):
    """Spearman rho with item-bootstrap CI: resample items (groups), keep every row of a chosen item."""
    x, y, g = np.asarray(x, float), np.asarray(y, float), np.asarray(groups)
    rho = float(stats.spearmanr(x, y)[0])
    uniq = np.unique(g)
    idx = {u: np.nonzero(g == u)[0] for u in uniq}
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(uniq, len(uniq), replace=True)
        rows = np.concatenate([idx[u] for u in pick])
        boots.append(stats.spearmanr(x[rows], y[rows])[0])
    boots = np.array(boots)
    return {"rho": rho, "lo": float(np.nanpercentile(boots, 2.5)), "hi": float(np.nanpercentile(boots, 97.5)),
            "p_le_0.5": float(np.mean(boots <= 0.5)), "n": int(len(x))}


def paired_boot(diffs, n_boot=BOOT, seed=RNG_SEED):
    d = np.asarray(diffs, float)
    rng = np.random.default_rng(seed)
    means = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)])
    return {"mean": float(d.mean()), "lo": float(np.percentile(means, 2.5)), "hi": float(np.percentile(means, 97.5)),
            "p_le_0": float(np.mean(means <= 0)), "n": int(len(d))}


def cohen_kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = float(np.mean(a == b))
    pe = float(sum(np.mean(a == v) * np.mean(b == v) for v in (0, 1)))
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


# ---------------- loading ----------------
def load_main(main_dir):
    rows = defaultdict(list)
    for f in sorted(Path(main_dir).glob("*.jsonl")):
        exp, model = f.stem.split("__", 1)
        for l in open(f, encoding="utf-8"):
            if l.strip():
                rows[(exp, model)].append(json.loads(l))
    return rows


def good(rows):
    return [r for r in rows if r.get("score") is not None and "error" not in r]


# ---------------- LLM experiments ----------------
def thresholds(e1_rows, cut=0.7):
    g = [r for r in good(e1_rows) if r["pc1"] >= cut]
    return float(np.median([r["score"] for r in g]) / 100.0) if g else None


def analyze_llm(rows, models):
    out = {"models": models, "pending": [], "per_model": {}}
    pc = {}
    for m in models:
        e1 = rows.get(("E1", m), [])
        if not good(e1):
            out["pending"].append(f"E1 {m}")
            continue
        thr = {c: thresholds(e1, c) for c in (0.6, 0.7, 0.8)}
        g = good(e1)
        rho = spearman_boot([r["score"] for r in g], [r["pc1"] for r in g], [r["domain"] for r in g])
        n_all = len(e1)
        unk = [r for r in g if r.get("label") == "unknown"]
        out["per_model"][m] = {
            "threshold": thr[0.7], "threshold_0.6": thr[0.6], "threshold_0.8": thr[0.8], "E1_rho": rho,
            "E1_n": n_all, "E1_parse_fail": sum(1 for r in e1 if r.get("parse") == "fail" or r.get("score") is None),
            "E1_unknown_share": len(unk) / max(1, len(g)),
            "E1_unknown_above_threshold": (sum(1 for r in unk if r["score"] / 100 >= thr[0.7]) / len(unk)) if unk else None}
        pc[m] = g
    if pc:
        allr = [r for g in pc.values() for r in g]
        out["H1_pooled"] = spearman_boot([r["score"] for r in allr], [r["pc1"] for r in allr], [r["domain"] for r in allr])
    # E2
    for m in models:
        e2 = good(rows.get(("E2", m), []))
        if not e2 or m not in out["per_model"]:
            out["pending"].append(f"E2 {m}")
            continue
        thr = out["per_model"][m]["threshold"]
        cross = lambda r: r["score"] / 100 >= thr
        none = [r for r in e2 if r["token"] == "none"]
        prest = [r for r in e2 if r["token"] != "none"]
        pm = out["per_model"][m]
        pm["E2_median_score"] = float(np.median([r["score"] for r in e2]) / 100)
        pm["E2_median_at_or_above_threshold"] = bool(pm["E2_median_score"] >= thr)
        for name, grp in (("A1_plain", none), ("A2_prestige", prest)):
            k = sum(cross(r) for r in grp)
            pm[f"E2_{name}"] = {"n": len(grp), "crossed": k, "rate": k / max(1, len(grp)), "wilson": wilson(k, len(grp)),
                                "floor_domains": geometric_floor(k / len(grp)) if grp else INF}
        cells = defaultdict(list)
        for r in prest:
            cells[(r["token"], r["tld"])].append(cross(r))
        best = max(cells.items(), key=lambda kv: np.mean(kv[1])) if cells else None
        if best:
            pm["E2_best_cell"] = {"cell": list(best[0]), "rate": float(np.mean(best[1])), "n": len(best[1]),
                                  "note": "selected after seeing the data, upward biased"}
        # paired difference: prestige token minus none, matched on stem and tld
        base = {(r["stem"], r["tld"]): r["score"] for r in none}
        diffs = [r["score"] - base[(r["stem"], r["tld"])] for r in prest if (r["stem"], r["tld"]) in base]
        if diffs:
            pm["E2_paired_prestige_minus_plain"] = paired_boot(diffs)
        tld = defaultdict(list)
        for r in e2:
            tld[r["tld"]].append(r["score"])
        pm["E2_median_by_tld"] = {k: float(np.median(v)) for k, v in tld.items()}
    # E3, E3h
    for exp, key in (("E3", "E3"), ("E3h", "E3h")):
        for m in models:
            rr = good(rows.get((exp, m), []))
            if not rr or m not in out["per_model"]:
                out["pending"].append(f"{exp} {m}")
                continue
            thr = out["per_model"][m]["threshold"]
            byv = defaultdict(list)
            tok = defaultdict(list)
            for r in rr:
                byv[r["variant"]].append(r)
                tok[r["variant"]].append(r["tokens_added"])
            ladder = []
            for v, grp in byv.items():
                k = sum(r["score"] / 100 >= thr for r in grp)
                ladder.append({"variant": v, "tokens": float(np.mean(tok[v])), "n": len(grp), "crossed": k,
                               "rate": k / len(grp), "wilson": wilson(k, len(grp)),
                               "mean_score": float(np.mean([r["score"] for r in grp])),
                               "unreliable_label_share": float(np.mean([r.get("label") == "unreliable" for r in grp]))})
            ladder.sort(key=lambda d: d["tokens"])
            fl = {}
            for p in (0.1, 0.5, 0.9):
                fl[str(p)] = ladder_floor([d["tokens"] for d in ladder], [d["rate"] for d in ladder], p)
            out["per_model"][m][f"{key}_ladder"] = ladder
            out["per_model"][m][f"{key}_floor_tokens"] = fl
            if exp == "E3":
                ctrl = {r["outlet"]: r["score"] for r in byv["control"]}
                eff = {}
                for v in ("A3_boilerplate", "A4_endorsement", "A5_injection", "combined"):
                    d = [r["score"] - ctrl[r["outlet"]] for r in byv[v] if r["outlet"] in ctrl]
                    eff[v] = paired_boot(d) if d else None
                out["per_model"][m]["E3_effects_vs_control"] = eff
    # E4
    for m in models:
        e4 = good(rows.get(("E4", m), []))
        if not e4 or m not in out["per_model"]:
            out["pending"].append(f"E4 {m}")
            continue
        thr = out["per_model"][m]["threshold"]
        by = defaultdict(list)
        for r in e4:
            by[r["domain"]].append(r["score"])
        sds = [np.std(v, ddof=1) for v in by.values() if len(v) > 1]
        flips = [len({s / 100 >= thr for s in v}) > 1 for v in by.values() if len(v) > 1]
        out["per_model"][m]["E4"] = {"mean_sd": float(np.mean(sds)) if sds else None,
                                     "decision_flip_share": float(np.mean(flips)) if flips else None, "domains": len(by)}
    # hypotheses
    out["hypotheses"] = hypotheses_llm(out, models)
    return out


def hypotheses_llm(out, models):
    pm = out["per_model"]
    h = {}
    if "H1_pooled" in out:
        h["H1"] = {"supported": bool(out["H1_pooled"]["rho"] > 0.5), "rho": out["H1_pooled"]["rho"],
                   "ci": [out["H1_pooled"]["lo"], out["H1_pooled"]["hi"]], "p": out["H1_pooled"]["p_le_0.5"]}
    ms = [m for m in models if "E2_median_score" in pm.get(m, {})]
    if ms:
        part_i = [m for m in ms if pm[m]["E2_median_at_or_above_threshold"]]
        pooled = []
        for m in ms:
            pass
        paired = [pm[m]["E2_paired_prestige_minus_plain"] for m in ms if "E2_paired_prestige_minus_plain" in pm[m]]
        pooled_mean = float(np.mean([p["mean"] for p in paired])) if paired else None
        pmin = max(p["p_le_0"] for p in paired) if paired else 1.0
        h["H2"] = {"models_median_at_or_above_threshold": part_i, "paired_means": {m: pm[m].get("E2_paired_prestige_minus_plain") for m in ms},
                   "pooled_mean_paired_difference": pooled_mean,
                   "supported": bool(part_i and pooled_mean is not None and pooled_mean > 0),
                   "p": pmin if paired else 1.0}
    m3 = [m for m in models if "E3_ladder" in pm.get(m, {})]
    if m3:
        over = []
        pvals = []
        for m in m3:
            best_p, ok = 1.0, False
            for d in pm[m]["E3_ladder"]:
                if d["variant"] in ("A3_boilerplate", "A4_endorsement", "A5_injection"):
                    pv = stats.binomtest(d["crossed"], d["n"], 0.25, alternative="greater").pvalue
                    if d["rate"] > 0.25:
                        ok = True
                    best_p = min(best_p, pv)
            if ok:
                over.append(m)
            pvals.append(best_p)
        means = defaultdict(list)
        for m in m3:
            for v, e in pm[m]["E3_effects_vs_control"].items():
                if e and v != "combined":
                    means[v].append(e["mean"])
        mean_eff = {v: float(np.mean(x)) for v, x in means.items()}
        a5_largest = bool(mean_eff and max(mean_eff, key=mean_eff.get) == "A5_injection")
        second = sorted(pvals)[1] if len(pvals) >= 2 else 1.0
        h["H3"] = {"models_over_25pct": over, "mean_effect_vs_control": mean_eff, "A5_largest": a5_largest,
                   "supported": bool(len(over) >= 2 and a5_largest),
                   "partly": bool(len(over) >= 2 and not a5_largest) or bool(len(over) == 1),
                   "p": second}
    return h


def summarize_llm(llm):
    """Aggregates across models for the paper: totals, pooled rates and Wilson bounds. Only models with data are included."""
    pm = llm["per_model"]
    out = {"models_with_E1": sorted(pm)}
    rho = [d["E1_rho"]["rho"] for d in pm.values() if "E1_rho" in d]
    if rho:
        out["E1_rho_min"], out["E1_rho_max"] = min(rho), max(rho)
        out["E1_parse_fail_total"] = sum(d["E1_parse_fail"] for d in pm.values())
        out["E1_calls_total"] = sum(d["E1_n"] for d in pm.values())
        out["E1_unknown_share_min"] = min(d["E1_unknown_share"] for d in pm.values())
        out["E1_unknown_share_max"] = max(d["E1_unknown_share"] for d in pm.values())
    # E2
    n = k = 0
    n1 = k1 = 0
    for d in pm.values():
        if "E2_A1_plain" in d:
            n1 += d["E2_A1_plain"]["n"]; k1 += d["E2_A1_plain"]["crossed"]
            n += d["E2_A2_prestige"]["n"]; k += d["E2_A2_prestige"]["crossed"]
    if n1:
        out["E2_plain_trials"], out["E2_plain_crossed"] = n1, k1
        out["E2_plain_wilson_upper"] = wilson(k1, n1)[1]
        out["E2_prestige_trials"], out["E2_prestige_crossed"] = n, k
        out["E2_prestige_wilson_upper"] = wilson(k, n)[1]
        out["E2_models"] = sum(1 for d in pm.values() if "E2_A1_plain" in d)
    # E3 by variant, pooled across models
    agg = {}
    for d in pm.values():
        for v in d.get("E3_ladder", []):
            a = agg.setdefault(v["variant"], {"n": 0, "crossed": 0, "score_sum": 0.0, "unrel": 0.0, "tokens": v["tokens"]})
            a["n"] += v["n"]; a["crossed"] += v["crossed"]; a["score_sum"] += v["mean_score"] * v["n"]; a["unrel"] += v["unreliable_label_share"] * v["n"]
    for var, a in agg.items():
        out[f"E3_{var}"] = {"n": a["n"], "crossed": a["crossed"], "wilson_upper": wilson(a["crossed"], a["n"])[1],
                            "mean_score": a["score_sum"] / a["n"], "unreliable_label_share": a["unrel"] / a["n"], "tokens": a["tokens"]}
    # E3h
    for d_name, d in pm.items():
        for v in d.get("E3h_ladder", []):
            out.setdefault("E3h", {}).setdefault(d_name, {})[v["variant"]] = {"rate": v["rate"], "n": v["n"], "mean_score": v["mean_score"], "unreliable_share": v["unreliable_label_share"]}
    for var in ("honest_base", "honest_policy"):
        tot = sum(d["E3h_ladder"][i]["n"] for d in pm.values() for i in range(len(d.get("E3h_ladder", []))) if d["E3h_ladder"][i]["variant"] == var)
        if tot:
            out[f"E3h_veto_{var}"] = sum(d["E3h_ladder"][i]["n"] * d["E3h_ladder"][i]["unreliable_label_share"] for d in pm.values() for i in range(len(d.get("E3h_ladder", []))) if d["E3h_ladder"][i]["variant"] == var) / tot
    h3 = out.get("E3h", {})
    pol = [v["honest_policy"]["rate"] for v in h3.values() if "honest_policy" in v]
    base = [v["honest_base"]["rate"] for v in h3.values() if "honest_base" in v]
    if pol:
        out["E3h_policy_rate_min"], out["E3h_policy_rate_max"] = min(pol), max(pol)
        out["E3h_base_rate_min"], out["E3h_base_rate_max"] = min(base), max(base)
        out["E3h_models"] = len(pol)
        out["E3h_policy_models_at_or_above_half"] = sum(1 for r in pol if r >= 0.5)
    e2d = [d["E2_paired_prestige_minus_plain"]["mean"] for d in pm.values() if "E2_paired_prestige_minus_plain" in d]
    if e2d:
        out["E2_paired_min"], out["E2_paired_max"] = min(e2d), max(e2d)
        out["E2_models_with_positive_paired_ci"] = sum(1 for d in pm.values() if "E2_paired_prestige_minus_plain" in d and d["E2_paired_prestige_minus_plain"]["lo"] > 0)
        out["E2_models_with_negative_paired_ci"] = sum(1 for d in pm.values() if "E2_paired_prestige_minus_plain" in d and d["E2_paired_prestige_minus_plain"]["hi"] < 0)
    med = [d["E2_median_score"] for d in pm.values() if "E2_median_score" in d]
    if med:
        out["E2_median_score_max"] = max(med)
    # E4
    sds = [d["E4"]["mean_sd"] for d in pm.values() if "E4" in d and d["E4"]["mean_sd"] is not None]
    fl = [d["E4"]["decision_flip_share"] for d in pm.values() if "E4" in d and d["E4"]["decision_flip_share"] is not None]
    if sds:
        out["E4_mean_sd_min"], out["E4_mean_sd_max"] = min(sds), max(sds)
        out["E4_flip_min"], out["E4_flip_max"] = min(fl), max(fl)
    return out


# ---------------- E5 / T5 ----------------
def analyze_e5(rows):
    res = {"pending": []}
    models = sorted({m for (e, m) in rows if e == "E5"})
    if not models:
        res["pending"].append("E5")
        return res
    arts = [json.loads(l) for l in open(ROOT / "data" / "articles" / "e5_articles.jsonl", encoding="utf-8")]
    corpus = [a["text"] for a in arts]
    texts = defaultdict(dict)
    for m in models:
        for r in rows[("E5", m)]:
            if r.get("text") and not r.get("empty"):
                texts[r["article"]][f"{m}:{r['prompt']}"] = r["text"]
    vec = TfidfVectorizer().fit(corpus + [t for d in texts.values() for t in d.values()])
    pairs = []
    for a in arts:
        t = {"orig": a["text"], **texts.get(a["id"], {})}
        keys = list(t)
        sig = {k: minhash(shingles(v)) for k, v in t.items()}
        X = vec.transform([t[k] for k in keys])
        S = (X @ X.T).toarray()
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                pairs.append({"article": a["id"], "a": keys[i], "b": keys[j],
                              "jaccard": jaccard_est(sig[keys[i]], sig[keys[j]]), "cosine": float(S[i, j])})
    if not pairs:
        res["pending"].append("E5 text")
        return res
    mh = np.array([p["jaccard"] < C.MINHASH_CUT for p in pairs])
    tf = np.array([p["cosine"] < C.TFIDF_CUT for p in pairs])
    art_ids = np.array([p["article"] for p in pairs])
    rng = np.random.default_rng(RNG_SEED)
    uniq = np.unique(art_ids)
    idx = {u: np.nonzero(art_ids == u)[0] for u in uniq}
    diffs = []
    for _ in range(BOOT):
        rows_ = np.concatenate([idx[u] for u in rng.choice(uniq, len(uniq))])
        diffs.append(mh[rows_].mean() - tf[rows_].mean())
    diffs = np.array(diffs)
    res.update({"pairs": len(pairs), "minhash_defeat_rate": float(mh.mean()), "tfidf_defeat_rate": float(tf.mean()),
                "difference": float(mh.mean() - tf.mean()), "ci": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))], "ci_lo": float(np.percentile(diffs, 2.5)), "ci_hi": float(np.percentile(diffs, 97.5)),
                "p": float(np.mean(diffs <= 0)), "supported": bool(mh.mean() > 0.5 and mh.mean() > tf.mean() and np.mean(diffs <= 0) < 0.05)})
    # floor ladder for A8: copies are orig plus k paraphrases (up to the number available), per article
    ladder = {}
    for defense in ("none", "minhash", "tfidf"):
        for kind in ("verbatim", "paraphrase"):
            rate_by_k = []
            for k in range(0, 6):
                ok = []
                for a in arts:
                    pool = list(texts.get(a["id"], {}).values())
                    if kind == "verbatim":
                        group = [a["text"]] * (k + 1)
                    else:
                        if k > len(pool):
                            ok.append(False)
                            continue
                        group = [a["text"]] + pool[:k]
                    n = count_clusters(group, defense, corpus + pool) if len(group) > 1 else 1
                    ok.append(n >= C.CORROB_TAU)
                rate_by_k.append(float(np.mean(ok)) if ok else 0.0)
            ladder[f"{defense}:{kind}"] = rate_by_k
    res["a8_rate_by_copies_0_to_5"] = ladder
    res["a8_floor_copies"] = {key: ladder_floor(list(range(6)), v, 0.5) for key, v in ladder.items()}
    return res


# ---------------- simulations to prices ----------------
def _num(x):
    return INF if x in ("inf", "Infinity", INF) else x


def read_sims(sims_dir):
    d = {}
    for n in ("t4", "t6", "t7", "cstar"):
        p = Path(sims_dir) / f"{n}.json"
        if p.exists():
            d[n] = json.loads(p.read_text())
    return d


def priced(units, kind, prices):
    """units in native units of `kind`; returns low/mid/high dollars or None if the unit has no citable price."""
    p = prices.get(kind)
    if not p or p.get("mid") is None or units == INF:
        return None if units != INF else {"low": INF, "mid": INF, "high": INF}
    return {k: units * p[k] for k in ("low", "mid", "high")}


def honest_days(units, kind):
    r = C.HONEST_RATES[kind]
    if units == INF:
        return {k: INF for k in r}
    if kind == "pickups":
        return {k: float(stats.gamma.ppf(0.5, a=units, scale=1 / v)) for k, v in r.items()}
    return {k: units / v for k, v in r.items()}



def llm_rows(llm, prices):
    """T2 and T3 rows, medians across the models that answered. INF means no crossing observed at that rung."""
    rows = []
    pm = llm["per_model"]
    med = lambda x: float(np.median(x))
    ms = [m for m in pm if "E2_A1_plain" in pm[m]]
    if ms:
        a1 = [pm[m]["E2_A1_plain"]["floor_domains"] for m in ms]
        a2 = [pm[m]["E2_A2_prestige"]["floor_domains"] for m in ms]
        hw = [0 if pm[m]["E2_A1_plain"]["rate"] >= 0.5 else INF for m in ms]
        rows.append({"technique": "T2 LLM name only", "models": ms,
                     "attacks": {"A1_register_domain": {"native": med(a1), "unit": "domain", "usd": priced(med(a1), "domain", prices), "per_model": dict(zip(ms, a1))},
                                 "A2_prestige_naming": {"native": med(a2), "unit": "domain", "usd": priced(med(a2), "domain", prices), "per_model": dict(zip(ms, a2))}},
                     "honest_wait": {"native": med(hw), "unit": "domain", "days": None,
                                     "note": "the rating depends on the name alone, so no evidence channel exists for a newcomer"}})
    m3 = [m for m in pm if "E3_floor_tokens" in pm[m]]
    if m3:
        ft = [pm[m]["E3_floor_tokens"]["0.5"] for m in m3]
        t = med(ft)
        usd = None
        if t != INF:
            usd = {k: prices["domain"][k] + t * prices["token_text"][k] for k in ("low", "mid", "high")}
        else:
            usd = {"low": INF, "mid": INF, "high": INF}
        hw3 = [pm[m]["E3h_floor_tokens"]["0.5"] for m in m3 if "E3h_floor_tokens" in pm[m]]
        rows.append({"technique": "T3 LLM page text", "models": m3,
                     "attacks": {"A3_to_A5_page_text": {"native": t, "unit": "token", "usd": usd, "per_model": dict(zip(m3, ft)),
                                                         "plus": "one domain registration"}},
                     "honest_wait": {"native": med(hw3) if hw3 else None, "unit": "token", "days": None}})
    return rows


def _add_usd(*parts):
    """Sum of priced components, key by key. None if any part is unpriced; INF stays INF."""
    if any(p is None for p in parts):
        return None
    return {k: sum(p[k] for p in parts) for k in ("low", "mid", "high")}


def build_table(llm, e5, sims, prices):
    """One row per technique variant: validity, cheapest priced attack, honest wait. Native units always shown."""
    rows = []
    t4, t6, t7, cs = sims.get("t4"), sims.get("t6"), sims.get("t7"), sims.get("cstar")
    dom = prices["domain"]
    if t4:
        for mode, name in (("pagerank", "T4 PageRank"), ("trustrank", "T4 TrustRank")):
            d = t4[mode]
            farm = _num(d["A6_farm_domains"]["p50"])
            links = _num(d["A7_bought_links"]["p50"])
            hw = _num(d["honest_organic_links"]["p50"])
            rows.append({"technique": name, "attacks": {"A6_farm_domains": {"native": farm, "unit": "domain", "usd": priced(farm, "domain", prices)},
                                                       "A7_bought_links": {"native": links, "unit": "link", "usd": None}},
                         "honest_wait": {"native": hw, "unit": "link", "days": honest_days(hw, "links")}})
    if t6:
        th = _num(t6["honest_T6a"]["p50"])
        for name, a9, a10, honest in (("T6a Beta reputation", t6["A9_T6a"], t6["A10_T6a"], t6["honest_T6a"]),
                                      ("T6b consensus-relative", t6["A9_T6b"], t6["A10_T6b"], t6["honest_T6b"])):
            a9n, a10n, hn = _num(a9["p50"]), _num(a10["p50"]), _num(honest["p50"])
            at = {"A9_long_con": {"native": a9n, "unit": "article", "usd": priced(a9n, "article", prices)},
                  "A10_hugging": {"native": a10n, "unit": "article", "usd": priced(a10n, "article", prices)}}
            if name.startswith("T6b"):
                cap = _num(t6["capture_T6b"]["p50"])
                acc = _num(t7["majority"]["A11_accounts"]["p50"]) if t7 else None
                at["A12_capture_majority_resolution"] = {
                    "native": cap, "unit": "article", "plus_accounts": acc,
                    "usd": _add_usd(priced(cap, "article", prices), priced(acc, "account", prices)) if acc is not None else priced(cap, "article", prices),
                    "note": "articles plus the colluding accounts that capture each resolution (accounts are reused across claims)"}
            rows.append({"technique": name, "attacks": at,
                         "honest_wait": {"native": hn, "unit": "claim", "days": honest_days(hn, "claims")}})
    if t7:
        for method, name in (("majority", "T7 majority vote"), ("bridging", "T7 bridging")):
            k = _num(t7[method]["A11_accounts"]["p50"])
            hw = _num(t7[method]["honest_ratings_needed"]["p50"])
            rows.append({"technique": name, "attacks": {"A11_brigade_accounts": {"native": k, "unit": "account", "usd": priced(k, "account", prices),
                                                                              "censored_at_cap": bool(k == INF)}},
                         "honest_wait": {"native": hw, "unit": "rating", "days": honest_days(hw, "ratings")}})
    # T5 from E5
    if e5.get("a8_floor_copies"):
        for defense, name in (("none", "T5 raw count"), ("minhash", "T5 MinHash"), ("tfidf", "T5 TF-IDF")):
            fv = e5["a8_floor_copies"][f"{defense}:verbatim"]
            fp = e5["a8_floor_copies"][f"{defense}:paraphrase"]
            best = min(fv, fp)
            rows.append({"technique": name, "attacks": {"A8_verbatim_copies": {"native": fv, "unit": "domain", "usd": priced(fv, "domain", prices)},
                                                         "A8_paraphrased_copies": {"native": fp, "unit": "domain", "usd": priced(fp, "domain", prices)}},
                         "honest_wait": {"native": C.CORROB_TAU, "unit": "pickup", "days": honest_days(C.CORROB_TAU, "pickups")}})
    # composite
    if cs and t7:
        kb = _num(t7["bridging"]["A11_accounts"]["p50"])
        hw = _num(cs["honest_T6b_gated_claims"]["p50"])
        art = _num(t6["capture_T6b"]["p50"]) if t6 else 0
        rows.append({"technique": "C* composite", "attacks": {"A12_capture_gated_by_bridging": {
            "native": kb, "unit": "account", "plus_articles": art,
            "usd": _add_usd(priced(kb, "account", prices), priced(art, "article", prices)),
            "note": "bridging accounts plus the articles needed to build the record"}},
                     "honest_wait": {"native": hw, "unit": "claim", "days": honest_days(hw, "claims")}})
    rows[0:0] = llm_rows(llm, prices)
    rows.insert(0, {"technique": "T1 static list", "attacks": {"A1_register_domain": {"native": INF, "unit": "domain", "usd": {"low": INF, "mid": INF, "high": INF},
                                                                                   "note": "unlisted domains score 0.5 or 0.0 by policy, below the cut; listing is editorial and has no purchase path in this threat model"}},
                    "honest_wait": {"native": INF, "unit": "listing", "days": None, "note": "needs an editor to add the source"}})
    return rows


def hypotheses_sims(sims, e5):
    h = {}
    t6, t7, cs = sims.get("t6"), sims.get("t7"), sims.get("cstar")
    if t6:
        con = _num(t6["A9_T6a"]["p50"])
        hon = _num(t6["honest_T6b"]["p50"])
        hug_never = t6["A10_T6b"]["never"] == t6["A10_T6b"]["n"]
        h["H5"] = {"con_T6a_median_articles": con, "honest_T6b_median_claims": hon, "hugging_T6b_never_crossed": bool(hug_never),
                   "supported": bool(con < hon and hug_never)}
    if t7:
        kb, km = _num(t7["bridging"]["A11_accounts"]["p50"]), _num(t7["majority"]["A11_accounts"]["p50"])
        ratio = (INF if kb == INF else kb / km) if km else INF
        h["H6"] = {"bridging_median_accounts": kb, "majority_median_accounts": km, "ratio": ratio, "supported": bool(ratio >= 5),
                   "bridging_censored": bool(kb == INF)}
        h["simulator_validity_T7"] = {"true_note_pass_rate": t7["bridging"]["honest_pass_rate"],
                                      "false_note_unattacked_pass_rate": t7["false_note_unattacked_pass"]["bridging"],
                                      "ok": bool(t7["bridging"]["honest_pass_rate"] >= 0.8 and t7["false_note_unattacked_pass"]["bridging"] <= 0.05)}
    if t6 and t7 and cs:
        comps = {"T6b": _num(t7["majority"]["A11_accounts"]["p50"]), "T7": _num(t7["bridging"]["A11_accounts"]["p50"])}
        cstar = _num(t7["bridging"]["A11_accounts"]["p50"])
        wait_c, wait_b = _num(cs["honest_T6b_gated_claims"]["p50"]), _num(t6["honest_T6b"]["p50"])
        h["H7"] = {"cstar_floor_accounts": cstar, "component_floors_accounts": comps,
                   "floor_ok": bool(cstar >= max(comps.values())), "honest_wait_cstar": wait_c, "honest_wait_T6b": wait_b,
                   "wait_ok": bool(wait_c <= wait_b), "supported": bool(cstar >= max(comps.values()) and wait_c <= wait_b),
                   "note": "T3 component floor is one domain price and is cheaper than both; veto uses the rater label only"}
    return h


# ---------------- auditability ----------------
CRITERIA = ["inputs_public", "method_public", "deterministic", "recomputable", "receipt", "contest_path"]


def read_coding(path):
    if not Path(path).exists():
        return None
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        out[(r["technique"], r["deployment"])] = [int(r[c]) for c in CRITERIA]
    return out


def analyze_audit(ev_dir=None):
    ev = Path(ev_dir) if ev_dir else ROOT / "evidence"
    c1, c2 = read_coding(ev / "auditability_coder1.csv"), read_coding(ev / "auditability_coder2.csv")
    if not c1 or not c2:
        return {"pending": ["coder1 (human) auditability sheet" if not c1 else None, "coder2 auditability sheet" if not c2 else None]}
    keys = sorted(set(c1) & set(c2))
    a = [v for k in keys for v in c1[k]]
    b = [v for k in keys for v in c2[k]]
    kappa = cohen_kappa(a, b)
    dis = [{"technique": k[0], "deployment": k[1], "criterion": CRITERIA[i], "coder1": c1[k][i], "coder2": c2[k][i]}
           for k in keys for i in range(6) if c1[k][i] != c2[k][i]]
    score = {f"{k[0]}|{k[1]}": {"coder1": float(np.mean(c1[k])), "coder2": float(np.mean(c2[k]))} for k in keys}
    return {"kappa": kappa, "n_items": len(a), "n_disagreements": len(dis), "disagreements": dis, "scores": score, "report_ranges": bool(kappa < 0.6)}


# ---------------- hand checks ----------------
def analyze_handcheck(ev_dir=None):
    """Checker error rates from Kinnoski's hand checks, both directions, with Wilson intervals. Blank sheets are pending."""
    ev = Path(ev_dir) if ev_dir else ROOT / "evidence"
    out = {"pending": []}
    for name, col, key in (("handcheck_parses.csv", "parse_correct_y_or_n", "parse"), ("handcheck_paraphrases.csv", "meaning_kept_y_or_n", "paraphrase")):
        p = ev / name
        if not p.exists():
            out["pending"].append(f"{name} not prepared")
            continue
        vals = [r[col].strip().lower() for r in csv.DictReader(open(p, encoding="utf-8")) if r[col].strip()]
        total = sum(1 for _ in csv.DictReader(open(p, encoding="utf-8")))
        if len(vals) < total or total == 0:
            out["pending"].append(f"{name} filled {len(vals)} of {total}")
            continue
        bad = sum(v == "n" for v in vals)
        w = wilson(bad, total)
        out[key] = {"n": total, "wrong": bad, "wrong_rate": bad / total, "wilson_lo": w[0], "wilson_hi": w[1]}
    return out


def analyze_robust(rows):
    """Appendix-only second-provider subsets: R1a (E1 subset) and R1b (E3 subset). Descriptive; no hypothesis is tested."""
    from .experiments import ROBUST_MODELS
    safe = lambda m: "".join(c if c.isalnum() or c in "-._" else "_" for c in m)
    ms = [m for m in ROBUST_MODELS if rows.get(("R1a", safe(m)))]
    if not ms:
        return {"pending": ["R1"]}
    r2 = {}
    for m in ms:
        r2[("E1", m)] = rows.get(("R1a", safe(m)), [])
        r2[("E3", m)] = rows.get(("R1b", safe(m)), [])
    a = analyze_llm(r2, ms)
    out = {}
    for m in ms:
        d = a["per_model"].get(m)
        if not d:
            continue
        out[m] = {"threshold": d["threshold"], "rho": d["E1_rho"]["rho"], "n": d["E1_n"], "parse_fail": d["E1_parse_fail"],
                  "E3": {v["variant"]: {"n": v["n"], "crossed": v["crossed"], "mean_score": v["mean_score"]} for v in d.get("E3_ladder", [])}}
    return out


# ---------------- main ----------------
def run(main_dir=None, sims_dir=None, out=None, ev_dir=None, models=None):
    from .experiments import working_models
    main_dir = main_dir or ROOT / "results" / "main"
    sims_dir = sims_dir or ROOT / "results" / "sims"
    rows = load_main(main_dir)
    models = models or working_models()
    llm = analyze_llm(rows, models)
    e5 = analyze_e5(rows)
    sims = read_sims(sims_dir)
    prices = load_prices()
    llm["summary"] = summarize_llm(llm)
    robust = analyze_robust(rows)
    A = {"llm": llm, "e5": e5, "sims_present": sorted(sims), "audit": analyze_audit(ev_dir), "handcheck": analyze_handcheck(ev_dir), "robust": robust}
    A["table"] = build_table(llm, e5, sims, prices)
    hyp = dict(llm.get("hypotheses", {}))
    if e5.get("p") is not None:
        hyp["H4"] = {"supported": e5["supported"], "minhash_defeat": e5["minhash_defeat_rate"], "tfidf_defeat": e5["tfidf_defeat_rate"],
                     "p": e5["p"]}
    ps = {k: v["p"] for k, v in hyp.items() if k in ("H1", "H2", "H3", "H4") and "p" in v}
    adj = holm(ps) if ps else {}
    for k, v in adj.items():
        hyp[k]["p_holm"] = v
    hyp.update(hypotheses_sims(sims, e5))
    A["hypotheses"] = hyp
    A["pending"] = llm["pending"] + e5["pending"] + [p for p in A["audit"].get("pending", []) if p] + A["handcheck"]["pending"] + \
        [f"sims {n}" for n in ("t4", "t6", "t7", "cstar") if n not in sims]
    out = Path(out) if out else ROOT / "results" / "analysis.json"
    out.write_text(json.dumps(A, indent=2, default=lambda x: "inf" if x == INF else (float(x) if hasattr(x, "item") else str(x))))
    return A


def main():
    A = run()
    print("pending:", A["pending"])
