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


def cmd_run(a):
    from .budget import Budget
    from .cache import Cache
    from . import experiments as E
    if not _lock_check(a.amend):
        return 2
    models = E.working_models()
    if a.model:
        models = [a.model]
    exps = a.exp.split(",") if a.exp else E.ALL
    sizes = dict(kv.split("=") for kv in (a.sizes or "").split(",") if kv)
    cap_total = float(os.getenv("FLOORPRICE_CREDIT_CAP", "875"))
    per_model_cap = cap_total / max(1, len(E.working_models()))
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in models[0])
    budget = Budget(path=ROOT / "results" / f"budget_{safe}.json", cap=per_model_cap)
    cache = Cache()
    stats = []
    para = E.working_models()[:E.PARAPHRASE_MODEL_COUNT]
    for exp in exps:
        for m in models:
            if exp == "E5" and m not in para:
                continue
            st = E.run(exp, m, cache, budget, n=int(sizes[exp]) if exp in sizes else None)
            print(json.dumps(st))
            stats.append(st)
    (ROOT / "results" / "run_stats.jsonl").open("a").write("".join(json.dumps(s) + "\n" for s in stats))
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
