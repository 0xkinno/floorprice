#!/usr/bin/env python3
"""Probe each candidate model with one tiny call. Writes results/probe.json and PLATFORM_PROBE.md.
A model that does not answer is dropped and named in the paper. Needs ADAPTION_API_KEY."""
import sys as _sys
from pathlib import Path as _P
# scripts/numbers.py must not shadow the standard library module of the same name
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import json
import os
import sys
import time
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from floorprice import llm, prompts  # noqa: E402
from floorprice.experiments import CANDIDATE_MODELS  # noqa: E402


def probe_one(model):
    body = {"model": model, "instructions": prompts.SYSTEM, "input": prompts.user_t2("reuters.com"),
            "temperature": 0.0, "max_output_tokens": 2000}
    t = time.time()
    rec = {"model": model}
    try:
        d = llm._post(llm.ADAPTION_URL, {"Authorization": f"Bearer {os.environ['ADAPTION_API_KEY']}"}, body)
        rec.update(status="ok", http=200, latency_s=round(time.time() - t, 2), echoed_model=d.get("model"),
                   output_types=[o.get("type") for o in d.get("output", [])], usage=d.get("usage"),
                   credit_fields={k: v for k, v in d.items() if "credit" in k.lower() or "cost" in k.lower()},
                   text=llm.extract_text(d)[:300], parsed=prompts.parse_rating(llm.extract_text(d)))
    except urllib.error.HTTPError as e:
        rec.update(status="fail", http=e.code, error=e.read().decode(errors="replace")[:300])
    except Exception as e:  # noqa: BLE001
        rec.update(status="fail", error=str(e)[:300])
    return rec


def main():
    if not os.environ.get("ADAPTION_API_KEY"):
        print("ADAPTION_API_KEY is not set. Put it in .env and export it.", file=sys.stderr)
        return 2
    recs = [probe_one(m) for m in CANDIDATE_MODELS]
    working = [r["model"] for r in recs if r["status"] == "ok" and r["parsed"]["parse"] != "fail"]
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "probe.json").write_text(json.dumps({"working": working, "records": recs,
        "date": time.strftime("%Y-%m-%d"), "note": "set FLOORPRICE_CREDITS_PER_CALL from usage and the price table"}, indent=2))
    lines = ["# PLATFORM_PROBE", "", f"Run {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. One tiny call per candidate model.", "",
             "| Model | Status | HTTP | Latency s | Output item types | Usage | Parsed |", "|---|---|---|---|---|---|---|"]
    for r in recs:
        lines.append(f"| {r['model']} | {r['status']} | {r.get('http')} | {r.get('latency_s','')} | {r.get('output_types','')} | "
                     f"{json.dumps(r.get('usage'))} | {r.get('parsed',{}).get('parse','')} |")
    lines += ["", f"Working models: {working}", "", "Adaptive Data: see SDK_SURFACE.md."]
    (ROOT / "PLATFORM_PROBE.md").write_text("\n".join(lines) + "\n")
    print("working:", working)
    return 0 if working else 1


if __name__ == "__main__":
    sys.exit(main())
