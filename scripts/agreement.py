#!/usr/bin/env python3
"""Cohen's kappa and the list of disagreements between coder 1 (Kinnoski, human) and coder 2 (blind model coder)."""
import sys as _sys
from pathlib import Path as _P
# scripts/numbers.py must not shadow the standard library module of the same name
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from floorprice import analyze  # noqa: E402

r = analyze.analyze_audit()
print(json.dumps(r, indent=2))
sys.exit(0 if "kappa" in r else 1)
