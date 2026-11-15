#!/usr/bin/env python3
"""Prepare the human hand-check sheets from cached model outputs (fixed seed):
evidence/handcheck_parses.csv (100 rater outputs) and evidence/handcheck_paraphrases.csv (50 paraphrases).
Kinnoski fills the blank columns. Run after E1 to E3 and E5 are done."""
import sys as _sys
from pathlib import Path as _P
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from floorprice import prompts  # noqa: E402

SEED = 20261115


def load_raw():
    rows = []
    for f in sorted((ROOT / "results" / "raw").glob("*.jsonl")):
        for l in open(f, encoding="utf-8"):
            if l.strip():
                rows.append(json.loads(l))
    return rows


def main():
    raw = [r for r in load_raw() if ":" not in r["request"]["model"] and r["request"]["instructions"] == prompts.SYSTEM]
    raw = [r for r in raw if r["request"]["max_output_tokens"] == (8000 if r["request"]["model"] == "qwen3.5-397b" else 2000)]
    rng = random.Random(SEED)
    pick = rng.sample(raw, min(100, len(raw)))
    with open(ROOT / "evidence" / "handcheck_parses.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "model", "input", "raw_output", "parsed_score", "parsed_label", "parse_method", "parse_correct_y_or_n", "notes"])
        for i, r in enumerate(pick):
            p = prompts.parse_rating(r["response"]["text"])
            w.writerow([i, r["request"]["model"], r["request"]["input"].replace("\n", " | ")[:300], r["response"]["text"][:600],
                        p["score"], p["label"], p["parse"], "", ""])
    para = [r for r in load_raw() if r["request"]["instructions"] == prompts.PARAPHRASE_SYSTEM]
    pp = rng.sample(para, min(50, len(para)))
    with open(ROOT / "evidence" / "handcheck_paraphrases.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "model", "original", "paraphrase", "meaning_kept_y_or_n", "notes"])
        for i, r in enumerate(pp):
            orig = r["request"]["input"].split("\n\n", 1)[-1]
            w.writerow([i, r["request"]["model"], orig, r["response"]["text"], "", ""])
    print(f"wrote {len(pick)} parse rows and {len(pp)} paraphrase rows")


if __name__ == "__main__":
    main()
