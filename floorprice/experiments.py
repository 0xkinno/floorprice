"""E1 to E5 (+E3h). Trial rows in results/main/ are derived from the raw cache, which is the source of truth."""
import json
import os
from pathlib import Path

from . import llm, prompts
from .data import DATA, read_csv

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "results" / "main"
CANDIDATE_MODELS = ["qwen3.5-397b", "deepseek-v4-flash", "glm-5.2", "gemma-4-31b-it"]
PARAPHRASE_MODEL_COUNT = 2
DEFAULT_SIZES = {"E1": 400, "E2": 252, "E3": 120, "E3h": 40, "E4": 60, "E5": 60}
ALL = ["E1", "E2", "E3", "E3h", "E4", "E5"]


def working_models():
    env = os.getenv("FLOORPRICE_MODELS")
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    p = ROOT / "results" / "probe.json"
    if p.exists():
        return json.loads(p.read_text())["working"]
    return list(CANDIDATE_MODELS)


def _even(rows, n):
    if n >= len(rows):
        return rows
    step = len(rows) / n
    return [rows[int(i * step)] for i in range(n)]


def _jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def items(exp, n=None):
    """Each item: dict(item, domain, page, meta, temperature, samples, kind)."""
    n = n or DEFAULT_SIZES[exp]
    if exp in ("E1", "E4"):
        rows = read_csv(DATA / ("sample_e1.csv" if exp == "E1" else "sample_e4.csv"))
        rows = _even(rows, n)
        t, s = (0.0, 1) if exp == "E1" else (0.7, 3)
        return [dict(item=r["domain"], domain=r["domain"], page=None, meta={"pc1": float(r["pc1"]), "decile": int(r["decile"])},
                     temperature=t, samples=s, kind="rate") for r in rows]
    if exp == "E2":
        rows = _even(read_csv(DATA / "fabricated" / "e2_domains.csv"), n)
        return [dict(item=r["domain"], domain=r["domain"], page=None,
                     meta={"stem": r["stem"], "token": r["token"], "tld": r["tld"]},
                     temperature=0.0, samples=1, kind="rate") for r in rows]
    if exp in ("E3", "E3h"):
        rows = _jsonl(DATA / "pages" / ("e3_pages.jsonl" if exp == "E3" else "e3h_pages.jsonl"))
        keep = sorted({r["outlet"] for r in rows})[:n]
        return [dict(item=f"{r['outlet']}:{r['variant']}", domain=r["domain"], page=r["text"],
                     meta={"outlet": r["outlet"], "variant": r["variant"], "tokens_added": r["tokens_added"]},
                     temperature=0.0, samples=1, kind="rate") for r in rows if r["outlet"] in keep]
    if exp == "E5":
        arts = _jsonl(DATA / "articles" / "e5_articles.jsonl")[:n]
        return [dict(item=f"{a['id']}:{p}", domain=None, page=a["text"], meta={"article": a["id"], "prompt": p},
                     temperature=0.0, samples=1, kind="paraphrase") for a in arts for p in prompts.PARAPHRASE_PROMPTS]
    raise ValueError(exp)


def run(exp, model, cache, budget, n=None, log=print):
    """Runs (or replays from cache) one experiment for one model. Returns stats and writes results/main/<exp>__<model>.jsonl."""
    MAIN.mkdir(parents=True, exist_ok=True)
    out, stats = [], {"exp": exp, "model": model, "calls_new": 0, "calls_cached": 0, "missing": 0, "errors": 0,
                      "parse_fail": 0, "empty": 0}
    for i, it in enumerate(items(exp, n)):
        for s in range(it["samples"]):
            try:
                if it["kind"] == "rate":
                    user = prompts.user_t2(it["domain"]) if it["page"] is None else prompts.user_t3(it["domain"], it["page"])
                    r = llm.call(model, prompts.SYSTEM, user, temperature=it["temperature"], sample=s, cache=cache, budget=budget)
                    p = prompts.parse_rating(r["text"])
                    row = {"exp": exp, "model": model, "item": it["item"], "domain": it["domain"], "sample": s,
                           "temperature": it["temperature"], **it["meta"], "score": p["score"], "label": p["label"],
                           "parse": p["parse"], "empty": bool(r.get("error")), "key": r["key"]}
                    stats["parse_fail"] += p["parse"] == "fail"
                    stats["empty"] += bool(r.get("error"))
                else:
                    user = prompts.PARAPHRASE_PROMPTS[it["meta"]["prompt"]].format(text=it["page"])
                    r = llm.call(model, prompts.PARAPHRASE_SYSTEM, user, temperature=0.0, max_tokens=500, cache=cache, budget=budget)
                    row = {"exp": exp, "model": model, "item": it["item"], **it["meta"], "text": r["text"],
                           "empty": bool(r.get("error")), "key": r["key"]}
                stats["calls_cached" if r["cached"] else "calls_new"] += 1
                out.append(row)
            except RuntimeError as e:
                msg = str(e)
                if msg.startswith("offline mode"):
                    stats["missing"] += 1
                elif "credit cap" in msg:
                    _write(exp, model, out)
                    raise
                else:
                    stats["errors"] += 1
                    out.append({"exp": exp, "model": model, "item": it["item"], "sample": s, "error": msg[:200]})
        if i % 50 == 49:
            _write(exp, model, out)
            log(f"{exp} {model}: {i + 1} items")
    _write(exp, model, out)
    return stats


def _write(exp, model, rows):
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in model)
    tmp = MAIN / f"{exp}__{safe}.jsonl.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, MAIN / f"{exp}__{safe}.jsonl")
