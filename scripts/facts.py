#!/usr/bin/env python3
"""Write results/FACTS.json: every number used anywhere, flattened from results/analysis.json.
Keys are dotted paths. Pending items are listed under _pending and are never defaulted."""
import sys as _sys
from pathlib import Path as _P
# scripts/numbers.py must not shadow the standard library module of the same name
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def flatten(prefix, obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            flatten(f"{prefix}.{k}" if prefix else str(k), v, out)
    elif isinstance(obj, list):
        if all(isinstance(x, (int, float, str, bool, type(None))) for x in obj):
            out[prefix] = obj
        else:
            for i, v in enumerate(obj):
                flatten(f"{prefix}.{i}", v, out)
    else:
        out[prefix] = obj


def main():
    from floorprice import analyze
    A = analyze.run()
    facts = {}
    flatten("", {k: v for k, v in A.items() if k != "table"}, facts)
    for i, row in enumerate(A["table"]):
        flatten(f"table.{row['technique']}", row, facts)
    pend = A["pending"]
    out = {"_pending": pend, "facts": facts}
    for name in ("budget*.json",):
        for f in sorted((ROOT / "results").glob(name)):
            flatten(f"budget.{f.stem}", json.loads(f.read_text()), out["facts"])
    (ROOT / "results" / "FACTS.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"FACTS.json: {len(facts)} facts, {len(pend)} pending")


if __name__ == "__main__":
    main()
