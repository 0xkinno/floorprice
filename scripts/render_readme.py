#!/usr/bin/env python3
"""Render README.md from README.template.md using results/FACTS.json. Fails if any placeholder is unresolved."""
import sys as _sys
from pathlib import Path as _P
# scripts/numbers.py must not shadow the standard library module of the same name
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("floorprice_numbers", ROOT / "scripts" / "numbers.py")
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)


def main():
    facts = json.loads((ROOT / "results" / "FACTS.json").read_text())["facts"]
    out, missing = N.render((ROOT / "README.template.md").read_text(encoding="utf-8"), facts)
    if missing or "{{" in out or "}}" in out:
        print("README not written. Unresolved:", sorted(set(missing)) or "stray braces")
        return 1
    (ROOT / "README.md").write_text(out, encoding="utf-8")
    print("README.md rendered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
