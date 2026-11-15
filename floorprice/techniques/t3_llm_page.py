"""T3: LLM rater from the domain name plus the source's own about page. Real model calls."""
from .t2_llm_name import LLMNameRater


class LLMPageRater(LLMNameRater):
    id = "T3"
    name = "LLM rater, with page text"
    recompute_cmd = "FLOORPRICE_OFFLINE=1 python -m floorprice.cli technique T3 <domain> --page <file> --model <model>"

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._page = None

    def with_page(self, text):
        self._page = text
        return self

    def score(self, source):
        p, _ = self.rate(source, page_text=self._page)
        return float("nan") if p["score"] is None else p["score"] / 100.0

    def inputs(self, source):
        d = super().inputs(source)
        d["page_sha"] = __import__("hashlib").sha256((self._page or "").encode()).hexdigest()
        return d
