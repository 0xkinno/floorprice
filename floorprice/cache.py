"""Append-only JSONL cache of model responses, one file per model, keyed by SHA-256 of the request."""
import json
import os
import threading
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "results" / "raw"


class Cache:
    def __init__(self, raw_dir=None):
        self.dir = Path(raw_dir) if raw_dir else RAW_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        self._d = {}
        self._lock = threading.Lock()
        for f in sorted(self.dir.glob("*.jsonl")):
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # a torn final line from a crash is skipped, never repaired silently
                    self._d[row["key"]] = row["response"]

    def get(self, key):
        return self._d.get(key)

    def put(self, key, response, request=None):
        model = (request or {}).get("model") or response.get("model") or "unknown"
        safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in model)
        row = {"key": key, "request": request, "response": response}
        with self._lock:
            if key in self._d:
                return
            with open(self.dir / f"{safe}.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            self._d[key] = response

    def __len__(self):
        return len(self._d)
