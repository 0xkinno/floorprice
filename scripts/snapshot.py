#!/usr/bin/env python3
"""Save documentation snapshots to evidence/snapshots/ as plain text with a header (URL, date read, SHA-256 of the saved body)."""
import hashlib
import re
import subprocess
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence" / "snapshots"

SOURCES = {
    "T1_wikipedia_perennial_sources": "https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources",
    "T1_newsguard_rating_process": "https://www.newsguardtech.com/ratings/rating-process-criteria/",
    "T1_mbfc_methodology": "https://mediabiasfactcheck.com/methodology/",
    "T2_yang_menczer_abstract_v1": "https://arxiv.org/abs/2304.00228v1",
    "T3_adaption_responses_api": "https://docs.adaptionlabs.ai/api/resources/responses/methods/create",
    "T5_wikipedia_notability": "https://en.wikipedia.org/wiki/Wikipedia:Notability",
    "T6_silver_bulletin_pollster_ratings": "https://www.natesilver.net/p/pollster-ratings-silver-bulletin",
    "T7_birdwatch_abstract": "https://arxiv.org/abs/2210.15723",
}


class Text(HTMLParser):
    skip = {"script", "style", "noscript", "svg", "nav", "footer", "header"}

    def __init__(self):
        super().__init__()
        self.parts, self.depth = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.skip:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in self.skip and self.depth:
            self.depth -= 1

    def handle_data(self, d):
        if not self.depth and d.strip():
            self.parts.append(d.strip())


def fetch(url):
    return subprocess.check_output(["curl", "-sS", "-L", "-m", "60", "-A", "Mozilla/5.0 floorprice-research", url])


def to_text(raw):
    p = Text()
    p.feed(raw.decode("utf-8", errors="replace"))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(p.parts))


def save(name, url, body, limit=250_000):
    OUT.mkdir(parents=True, exist_ok=True)
    body = body[:limit]
    head = f"URL: {url}\nDATE_READ: {time.strftime('%Y-%m-%d', time.gmtime())}\nSHA256_OF_BODY: {hashlib.sha256(body.encode()).hexdigest()}\nTRUNCATED_AT: {limit} characters\n---\n"
    (OUT / f"{name}.txt").write_text(head + body, encoding="utf-8")


def main():
    for name, url in SOURCES.items():
        try:
            save(name, url, to_text(fetch(url)))
            print("saved", name)
        except Exception as e:  # noqa: BLE001
            print("FAILED", name, e)
    # local copies of documents already read in full
    cn = ROOT / "reference" / "repos" / "twitter_communitynotes" / "documentation" / "under-the-hood" / "ranking-notes.md"
    if cn.exists():
        save("T7_communitynotes_ranking_notes", "https://github.com/twitter/communitynotes/blob/main/documentation/under-the-hood/ranking-notes.md",
             cn.read_text(encoding="utf-8"))
        print("saved T7_communitynotes_ranking_notes")
    for name, url, path in (("T4_trustrank_paper", "https://www.vldb.org/conf/2004/RS15P3.PDF", sys.argv[1] if len(sys.argv) > 1 else None),):
        if path and Path(path).exists():
            txt = subprocess.check_output(["pdftotext", path, "-"], text=True)
            save(name, url, txt)
            print("saved", name)


if __name__ == "__main__":
    main()
