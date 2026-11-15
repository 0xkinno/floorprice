"""A reliability receipt: canonical JSON with a SHA-256 digest. A format, not a product claim."""
import hashlib
import json
import time


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_of(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def make_receipt(source, technique, version, inputs, score, threshold, recompute, generated_at=None):
    body = {
        "source": source, "technique": technique, "version": version,
        "inputs_digest": digest_of(inputs), "score": None if score != score else round(float(score), 6),
        "threshold": round(float(threshold), 6),
        "verdict": "reliable" if (score == score and score >= threshold) else "not_reliable",
        "recompute": recompute,
    }
    r = dict(body)
    r["generated_at"] = generated_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    r["digest"] = digest_of(body)  # generated_at is excluded so the digest can be recomputed
    return r


def verify(receipt):
    body = {k: v for k, v in receipt.items() if k not in ("digest", "generated_at")}
    return digest_of(body) == receipt.get("digest")
