#!/usr/bin/env python3
"""Export results for the static site: site/public/data/site.json. The site reads only this file. Nothing calls a model from the browser."""
import sys as _sys
from pathlib import Path as _P
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def clean(o):
    if isinstance(o, float) and math.isinf(o):
        return "inf"
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


def main():
    from floorprice.floor import load_prices
    from floorprice import config as C
    from floorprice.techniques.t1_list import StaticList
    A = json.loads((ROOT / "results" / "analysis.json").read_text())
    lock = json.loads((ROOT / "HYPOTHESES.lock").read_text())
    r = StaticList().receipt("reuters.com")
    out = {"table": A["table"], "hypotheses": A["hypotheses"], "audit": A["audit"], "pending": A["pending"],
           "e5": A.get("e5", {}), "llm": {k: v for k, v in A["llm"].items() if k != "models"},
           "prices": load_prices(), "honest_rates": C.HONEST_RATES,
           "lock": {"combined": lock["combined"], "locked_at": lock["locked_at"]}, "sample_receipt": r}
    d = ROOT / "site" / "public" / "data"
    d.mkdir(parents=True, exist_ok=True)
    (d / "site.json").write_text(json.dumps(clean(out), indent=1))
    print("site.json written; pending:", len(A["pending"]))


if __name__ == "__main__":
    main()
