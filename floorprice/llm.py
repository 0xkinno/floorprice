"""All model calls go through Adaption's Responses API. Cached by SHA-256 of the full request."""
import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.request

from .budget import Budget
from .cache import Cache

ADAPTION_URL = "https://api.prod.adaptionlabs.ai/api/v1/responses"
PACE_S = float(os.getenv("FLOORPRICE_PACE_S", "1.0"))
_last = 0.0
_pace_lock = threading.Lock()


def _post(url, headers, body, timeout=120):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "floorprice/0.1", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def extract_text(d):
    """Read only output items of type message and their output_text content. Reasoning items are skipped."""
    return "".join(
        c.get("text", "")
        for o in d.get("output", []) if o.get("type") == "message"
        for c in (o.get("content") or [])
        if isinstance(c, dict) and c.get("type") in ("output_text", "text"))


def request_key(model, system, user, temperature, max_tokens, sample):
    req = {"model": model, "instructions": system, "input": user, "temperature": temperature,
           "max_output_tokens": max(max_tokens, 2000), "sample": sample}
    return req, hashlib.sha256(json.dumps(req, sort_keys=True).encode()).hexdigest()


def call(model, system, user, *, temperature=0.0, max_tokens=600, sample=0, cache: Cache, budget: Budget):
    """Returns {"text", "usage", "status", "cached", "key"}."""
    global _last
    req, key = request_key(model, system, user, temperature, max_tokens, sample)
    hit = cache.get(key)
    if hit is not None:
        return {**hit, "cached": True, "key": key}
    if os.getenv("FLOORPRICE_OFFLINE") == "1":
        raise RuntimeError(f"offline mode and no cache for {key[:12]}")
    budget.check_or_raise()
    for attempt in range(6):
        with _pace_lock:
            wait = PACE_S - (time.time() - _last)
            if wait > 0:
                time.sleep(wait)
            _last = time.time()
        try:
            body = {k: v for k, v in req.items() if k != "sample"}
            d = _post(ADAPTION_URL, {"Authorization": f"Bearer {os.environ['ADAPTION_API_KEY']}"}, body)
            text = extract_text(d)
            rec = {"text": text, "usage": d.get("usage"), "status": d.get("status"),
                   "model": model, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            if not text:
                rec["error"] = "empty_message"  # counted as a parse failure, never silently dropped
            cache.put(key, rec, request=req)
            budget.record(rec.get("usage"))
            return {**rec, "cached": False, "key": key}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529):
                time.sleep(min(90, 8 * (attempt + 1)))
                continue
            raise RuntimeError(f"{model} HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{model}: gave up after retries")
