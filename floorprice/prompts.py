"""Rater prompts. This file is hashed into HYPOTHESES.lock: editing it after the lock needs --amend."""
import json
import re

SYSTEM = (
    'You assess how reliable a news source is. Reliability means it reports accurately, corrects '
    'errors, separates news from opinion, and is transparent about ownership. Answer with one JSON object and '
    'nothing else: {"score": <integer 0-100>, "label": "reliable" | "mixed" | "unreliable" | "unknown", '
    '"reason": "<at most 20 words>"}. Use "unknown" if you do not recognise the source; still give a score.'
)

USER_T2 = "Source: {domain}"

USER_T3 = (
    "Source: {domain}\n"
    "About page text (written by the source itself):\n"
    "<<<\n"
    "{page_text}\n"
    ">>>"
)

PARAPHRASE_PROMPTS = {
    "p1": "Rewrite the following news paragraph in your own words. Keep every fact. Output only the rewrite.\n\n{text}",
    "p2": ("Rewrite the following news paragraph so that no sequence of five consecutive words matches the "
           "original. Keep every fact. Output only the rewrite.\n\n{text}"),
}

LABELS = {"reliable", "mixed", "unreliable", "unknown"}


def user_t2(domain):
    return USER_T2.format(domain=domain)


def user_t3(domain, page_text):
    return USER_T3.format(domain=domain, page_text=page_text)


def parse_rating(text):
    """Strict JSON first, then one regex fallback for "score": N. Anything else is a parse failure.
    Returns dict(score, label, reason, parse) where parse is 'json', 'regex' or 'fail'."""
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t).strip()
    try:
        d = json.loads(t)
        s = d.get("score")
        if isinstance(s, bool) or not isinstance(s, (int, float)) or not 0 <= s <= 100:
            raise ValueError("score out of range")
        label = d.get("label") if d.get("label") in LABELS else None
        return {"score": float(s), "label": label, "reason": str(d.get("reason", ""))[:200], "parse": "json"}
    except (ValueError, TypeError, AttributeError):
        pass
    m = re.search(r'"score"\s*:\s*(\d{1,3})', t)
    if m and 0 <= int(m.group(1)) <= 100:
        lm = re.search(r'"label"\s*:\s*"(\w+)"', t)
        label = lm.group(1) if lm and lm.group(1) in LABELS else None
        return {"score": float(m.group(1)), "label": label, "reason": "", "parse": "regex"}
    return {"score": None, "label": None, "reason": "", "parse": "fail"}

PARAPHRASE_SYSTEM = "You rewrite text faithfully and output only the rewrite."
