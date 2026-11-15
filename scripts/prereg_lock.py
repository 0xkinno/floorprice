#!/usr/bin/env python3
"""Hash the pre-registered inputs into HYPOTHESES.lock. `floorprice run` refuses to run if anything changed,
unless --amend "<reason>" is given, which appends a dated amendment to HYPOTHESES.md and re-locks."""
import glob
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "HYPOTHESES.lock"
PATTERNS = ["HYPOTHESES.md", "floorprice/prompts.py", "floorprice/config.py", "data/fabricated/*", "data/pages/*",
            "data/articles/*", "data/sample_*.csv", "data/prices.yaml", "data/lin_pc1.csv"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compute():
    files = {}
    for pat in PATTERNS:
        for f in sorted(glob.glob(str(ROOT / pat))):
            files[str(Path(f).relative_to(ROOT))] = sha(f)
    combined = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"files": files, "combined": combined}


def write(note=None):
    lock = compute()
    lock["locked_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOCK.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    return lock


def diff():
    if not LOCK.exists():
        return ["HYPOTHESES.lock does not exist"]
    old, new = json.loads(LOCK.read_text())["files"], compute()["files"]
    return [f"{k}: changed" for k in sorted(set(old) | set(new)) if old.get(k) != new.get(k)]


def enforce(amend=None):
    d = diff()
    if not d:
        return True
    if not amend:
        print("Refusing to run: locked files changed since HYPOTHESES.lock:\n  " + "\n  ".join(d) +
              '\nRe-run with --amend "<reason>" to record an amendment.', file=sys.stderr)
        return False
    with open(ROOT / "HYPOTHESES.md", "a", encoding="utf-8") as fh:
        fh.write(f"\n\n### Amendment {time.strftime('%Y-%m-%d')}\n\nReason: {amend}\n\nFiles changed:\n" +
                 "".join(f"- {x}\n" for x in d))
    write()
    print("Amendment recorded and lock refreshed.")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        d = diff()
        print("LOCK OK" if not d else "\n".join(d))
        sys.exit(1 if d else 0)
    lock = write()
    print("combined", lock["combined"])
