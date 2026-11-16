"""All model calls go through Adaption's Responses API. Cached by SHA-256 of the full request."""
import hashlib
import http.client
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


def _post(url, headers, body, timeout=600):
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


PROVIDERS = {
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "env": "GROQ_API_KEY", "pace": 2.6},
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", "env": "GEMINI_API_KEY", "pace": 6.5},
}
_provider_last = {}


def split_model(model):
    """'groq:openai/gpt-oss-120b' -> ('groq', 'openai/gpt-oss-120b'). Plain IDs are Adaption models."""
    head, sep, rest = model.partition(":")
    return (head, rest) if sep and head in PROVIDERS else ("adaption", model)


def _provider_request(provider, raw_model, system, user, temperature, max_tokens):
    cfg = PROVIDERS[provider]
    key = os.environ[cfg["env"]]
    if provider == "groq":
        body = {"model": raw_model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "temperature": temperature, "max_tokens": max_tokens}
        d = _post(cfg["url"], {"Authorization": f"Bearer {key}"}, body)
        text = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        return text, d.get("usage")
    body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
    d = _post(cfg["url"].format(model=raw_model), {"x-goog-api-key": key}, body)
    parts = ((d.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts if not p.get("thought")), d.get("usageMetadata")


# Output budget per model. 2,000 for all, except models whose reasoning can consume it. qwen3.5-397b returned an empty message
# in 33 of its first 70 calls at 2,000 (reasoning used the whole budget), so it gets 8,000. See the amendment in HYPOTHESES.md.
MAX_OUT = {"qwen3.5-397b": 8000}


def request_key(model, system, user, temperature, max_tokens, sample):
    req = {"model": model, "instructions": system, "input": user, "temperature": temperature,
           "max_output_tokens": max(max_tokens, MAX_OUT.get(model, 2000)), "sample": sample}
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
    provider, raw_model = split_model(model)
    attempt, rate_waits = 0, 0
    while attempt < 6 and rate_waits < 60:
        with _pace_lock:
            pace = PACE_S if provider == "adaption" else PROVIDERS[provider]["pace"]
            last = _last if provider == "adaption" else _provider_last.get(provider, 0.0)
            wait = pace - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
            if provider == "adaption":
                _last = time.time()
            else:
                _provider_last[provider] = time.time()
        try:
            if provider == "adaption":
                body = {k: v for k, v in req.items() if k != "sample"}
                d = _post(ADAPTION_URL, {"Authorization": f"Bearer {os.environ['ADAPTION_API_KEY']}"}, body)
                text, usage, status = extract_text(d), d.get("usage"), d.get("status")
            else:
                text, usage = _provider_request(provider, raw_model, system, user, temperature, max(max_tokens, 2000))
                status = "completed"
            rec = {"text": text, "usage": usage, "status": status,
                   "model": model, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            if not text:
                rec["error"] = "empty_message"  # counted as a parse failure, never silently dropped
            cache.put(key, rec, request=req)
            budget.record(rec.get("usage"))
            return {**rec, "cached": False, "key": key}
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # The key allows about 25 requests a minute. Honour Retry-After; this does not count as a failed attempt.
                rate_waits += 1
                ra = e.headers.get("Retry-After")
                time.sleep((int(ra) if ra and ra.isdigit() else 30) + 1 + (hash(key) % 5))
                continue
            if e.code in (500, 502, 503, 504, 529):
                attempt += 1
                time.sleep(min(90, 8 * attempt))
                continue
            raise RuntimeError(f"{model} HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException, json.JSONDecodeError):
            # connection resets and truncated bodies surface as OSError or JSONDecodeError after the headers arrive
            attempt += 1
            time.sleep(5 * attempt)
    raise RuntimeError(f"{model}: gave up after retries")
