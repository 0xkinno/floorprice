#!/usr/bin/env python3
"""House style: no emoji, no em dashes, no en dashes, no hype words. Fails the build on any hit.
Scans committed text files and quoted model text in results/main."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HYPE = ["revolutionary", "seamless", "cutting-edge", "cutting edge", "world-class", "paradigm", "game-changing", "game changing"]
DASHES = ["—", "–"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF⭐⭕️]")
EXTS = {".md", ".py", ".yaml", ".yml", ".html", ".tsx", ".ts", ".css", ".json", ".txt", ".toml"}
SKIP_DIRS = {"snapshots", "reference", ".git", "node_modules", "dist", "__pycache__", "raw", ".pytest_cache", "public"}
SELF = {"check_style.py", "test_infra.py"}


def files():
    try:
        out = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True)
        paths = [ROOT / p for p in out.split("\n") if p]
    except Exception:
        paths = [p for p in ROOT.rglob("*") if p.is_file()]
    for p in paths:
        if p.suffix in EXTS and p.name not in SELF and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS) and p.name != "requirements.lock":
            yield p


def scan_text(text, name):
    bad = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for d in DASHES:
            if d in line:
                bad.append(f"{name}:{i}: dash character U+{ord(d):04X}")
        if EMOJI.search(line):
            bad.append(f"{name}:{i}: emoji")
        for h in HYPE:
            if h in low:
                bad.append(f"{name}:{i}: hype word '{h}'")
    return bad


def main():
    bad = []
    for p in files():
        try:
            bad += scan_text(p.read_text(encoding="utf-8"), str(p.relative_to(ROOT)))
        except UnicodeDecodeError:
            pass
    for p in (ROOT / "results" / "main").glob("*.jsonl") if (ROOT / "results" / "main").exists() else []:
        bad += scan_text(p.read_text(encoding="utf-8"), str(p.relative_to(ROOT)))
    if bad:
        print("\n".join(bad[:200]))
        print(f"STYLE FAIL: {len(bad)} problems")
        return 1
    print("style ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
