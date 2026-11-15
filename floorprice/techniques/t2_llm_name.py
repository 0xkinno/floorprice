"""T2: LLM rater from the domain name only. Real model calls through Adaption's Responses API."""
from .. import llm, prompts
from .base import Technique


class LLMNameRater(Technique):
    id = "T2"
    name = "LLM rater, name only"
    recompute_cmd = "FLOORPRICE_OFFLINE=1 python -m floorprice.cli technique T2 <domain> --model <model>"

    def __init__(self, model, cache, budget, threshold, temperature=0.0):
        self.model, self.cache, self.budget = model, cache, budget
        self._thr, self.temperature = threshold, temperature

    def rate(self, source, page_text=None, sample=0):
        user = prompts.user_t2(source) if page_text is None else prompts.user_t3(source, page_text)
        r = llm.call(self.model, prompts.SYSTEM, user, temperature=self.temperature,
                     sample=sample, cache=self.cache, budget=self.budget)
        return prompts.parse_rating(r["text"]), r

    def score(self, source):
        p, _ = self.rate(source)
        return float("nan") if p["score"] is None else p["score"] / 100.0

    def threshold(self):
        return self._thr

    def inputs(self, source):
        return {"source": source, "model": self.model, "temperature": self.temperature,
                "system_sha": __import__("hashlib").sha256(prompts.SYSTEM.encode()).hexdigest()}
