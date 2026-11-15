"""floorprice command line: run (model experiments), sims, analyze, technique."""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _lock_check(amend):
    sys.path.insert(0, str(ROOT / "scripts"))
    import prereg_lock
    return prereg_lock.enforce(amend)


RUN_ORDER = ["E1", "E3", "E3h", "E2", "E5", "E4"]   # E1 first: every threshold comes from it. E3 carries H3.


def cmd_run(a):
    from concurrent.futures import ThreadPoolExecutor
    from .budget import Budget
    from .cache import Cache
    from . import experiments as E
    if not _lock_check(a.amend):
        return 2
    all_models = E.working_models()
    models = [a.model] if a.model else all_models
    exps = a.exp.split(",") if a.exp else RUN_ORDER
    bpath = "budget.json"
    if a.robust:
        models, exps, bpath = E.ROBUST_MODELS, (a.exp.split(",") if a.exp else ["R1a", "R1b"]), "budget_robust.json"
    sizes = dict(kv.split("=") for kv in (a.sizes or "").split(",") if kv)
    budget = Budget(path=ROOT / "results" / bpath, cap=float(os.getenv("FLOORPRICE_CREDIT_CAP", "875")))
    cache = Cache()
    para = all_models[:E.PARAPHRASE_MODEL_COUNT]
    stats = []

    def one_model(m):
        out = []
        for exp in exps:
            if exp == "E5" and m not in para:
                continue
            st = E.run(exp, m, cache, budget, n=int(sizes[exp]) if exp in sizes else None, workers=2 if a.robust else int(os.getenv("FLOORPRICE_WORKERS", "6")))
            print(json.dumps(st), flush=True)
            out.append(st)
        return out

    # One thread per model. They share the global request pacing in llm.py, because the key has one rate limit.
    with ThreadPoolExecutor(max_workers=len(models)) as ex:
        for res in ex.map(one_model, models):
            stats += res
    with open(ROOT / "results" / "run_stats.jsonl", "a") as fh:
        fh.write("".join(json.dumps(s) + "\n" for s in stats))
    return 0


def cmd_sims(a):
    from . import sims
    only = a.only.split(",") if a.only else None
    sims.run_all(only=only, seeds=a.seeds)
    return 0


def cmd_analyze(a):
    from . import analyze
    analyze.main()
    return 0


def cmd_technique(a):
    from .techniques.t1_list import StaticList
    if a.id == "T1":
        t = StaticList()
        print(json.dumps(t.receipt(a.source), indent=2))
        return 0
    print("Use scripts or the Python API for this technique; see README.", file=sys.stderr)
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(prog="floorprice")
    sp = p.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run")
    r.add_argument("--model")
    r.add_argument("--exp", help="comma list of E1,E2,E3,E3h,E4,E5")
    r.add_argument("--sizes", help="e.g. E1=200,E3=120")
    r.add_argument("--robust", action="store_true", help="appendix-only subsets on a second provider (Gemini, Groq)")
    r.add_argument("--amend", help="reason; appends a dated amendment to HYPOTHESES.md and re-locks")
    r.set_defaults(f=cmd_run)
    s = sp.add_parser("sims")
    s.add_argument("--only")
    s.add_argument("--seeds", type=int, default=20)
    s.set_defaults(f=cmd_sims)
    an = sp.add_parser("analyze")
    an.set_defaults(f=cmd_analyze)
    t = sp.add_parser("technique")
    t.add_argument("id")
    t.add_argument("source", nargs="?", default="")
    t.set_defaults(f=cmd_technique)
    a = p.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
