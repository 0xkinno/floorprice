"""Lin et al. (2023) loader, stratified sampling, fabricated-domain generator."""
import csv
import hashlib
import random
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEED = 20261115
RELIABLE_CUT = 0.7
LOW_CUT = 0.3

PRESTIGE_TOKENS = ["tribune", "gazette", "daily", "public", "institute"]
TLDS = ["org", "com", "news"]
_SYL_A = ["mar", "bel", "ash", "cor", "dun", "elm", "fen", "gar", "hol", "iver", "jun", "kel", "lan", "mor",
          "nor", "oak", "pen", "quin", "rav", "sel", "tar", "ulm", "var", "wen", "yar", "zan", "bran", "cal"]
_SYL_B = ["low", "field", "ton", "wick", "brook", "dale", "ford", "mont", "ridge", "vale", "haven", "stead",
          "worth", "bury", "mere", "land"]


def load_lin(path=None):
    df = pd.read_csv(path or DATA / "lin_pc1.csv")
    df["domain"] = df["domain"].str.lower().str.strip()
    return df


def stratified_sample(df, n=400, bins=10, seed=SEED):
    """n domains, n/bins per pc1 decile (equal-width bins on [0,1] would be empty at the low end, so deciles are
    by rank). Deterministic."""
    d = df.sort_values(["pc1", "domain"]).reset_index(drop=True)
    d["decile"] = pd.qcut(d.index, bins, labels=False)
    per = n // bins
    parts = [g.sample(per, random_state=seed + int(k)) for k, g in d.groupby("decile")]
    out = pd.concat(parts).sort_values("pc1").reset_index(drop=True)
    return out[["domain", "pc1", "decile"]]


def stem_names(lin_domains, k, seed=SEED):
    rng = random.Random(seed)
    banned = set(lin_domains)
    out = []
    while len(out) < k:
        s = rng.choice(_SYL_A) + rng.choice(_SYL_B)
        if s in out:
            continue
        if any(f"{s}{t}.{tld}" in banned or f"{s}.{tld}" in banned for t in PRESTIGE_TOKENS for tld in TLDS):
            continue
        out.append(s)
    return out


def make_fabricated(lin_domains, n_stems=14, seed=SEED):
    """Factorial: stems x {none + 5 prestige tokens} x 3 TLDs = 14 x 6 x 3 = 252 fictional domains."""
    banned = set(lin_domains)
    rows = []
    for s in stem_names(banned, n_stems, seed):
        for tok in [""] + PRESTIGE_TOKENS:
            for tld in TLDS:
                dom = f"{s}{tok}.{tld}"
                assert dom not in banned
                rows.append({"domain": dom, "stem": s, "token": tok or "none", "tld": tld, "fictional": "true"})
    return rows


def write_csv(path, rows, header_note=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        if header_note:
            fh.write(f"# {header_note}\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def read_csv(path):
    with open(path, encoding="utf-8") as fh:
        lines = [l for l in fh if not l.startswith("#")]
    return list(csv.DictReader(lines))


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bands(df):
    return df[df.pc1 >= RELIABLE_CUT], df[df.pc1 <= LOW_CUT]


_PLACES = ["Marlow", "Ashbury", "Corvale", "Dunmere", "Elmford", "Fenwick", "Garland", "Holbrook", "Ivermont",
           "Kelbrook", "Lanridge", "Norvale", "Penhaven", "Ravstead", "Selwick", "Tarwood", "Varley", "Wenmere"]
_BODIES = ["city council", "county board", "school board", "planning commission", "water authority", "transit board"]
_ACTIONS = ["approve a new road repair plan", "extend the library's opening hours", "fund a bridge inspection programme",
            "replace the ageing bus fleet", "adopt a revised zoning map", "raise the water connection fee",
            "open a second recycling centre", "fund two additional school crossing guards"]
_PEOPLE = ["Ana Whitlock", "Tomas Reyes", "Priya Narang", "Owen Falk", "Lena Marsh", "Jonas Okafor", "Mira Delacroix",
           "Sam Hartwell"]
_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]


def make_articles(n=60, seed=SEED):
    """Fictional local-news paragraphs for E5. Every name is invented; the facts are template facts."""
    rng = random.Random(seed + 9)
    out = []
    for i in range(n):
        town, body, act = rng.choice(_PLACES), rng.choice(_BODIES), rng.choice(_ACTIONS)
        who, day = rng.choice(_PEOPLE), rng.choice(_DAYS)
        yes = rng.randint(4, 9)
        no = rng.randint(0, 3)
        cost, yrs = rng.choice([1.2, 2.4, 3.8, 5.5, 7.1]), rng.choice([2, 3, 5])
        month = rng.choice(["March", "June", "September", "January"])
        tpl = i % 3
        if tpl == 0:
            t = (f"On {day} the {town} {body} voted {yes} to {no} to {act}. {who}, who chairs the committee, said the "
                 f"change had been requested by residents for several years. The measure will cost ${cost} million over "
                 f"{yrs} years and takes effect in {month}.")
        elif tpl == 1:
            t = (f"{who} told reporters in {town} that the {body} will {act}, after a {yes} to {no} vote on {day}. "
                 f"The plan is priced at ${cost} million across {yrs} years, officials said, and work is due to start "
                 f"in {month}. Residents will be able to comment before the final reading.")
        else:
            t = (f"A {yes} to {no} majority on the {town} {body} backed a proposal on {day} to {act}. "
                 f"According to {who}, the total outlay is ${cost} million spread over {yrs} years. "
                 f"The decision follows two public hearings and comes into force in {month}.")
        out.append({"id": f"a{i:02d}", "text": t, "fictional": "true"})
    return out


def e4_sample(sample_e1, per_decile=6, seed=SEED):
    parts = [g.sample(per_decile, random_state=seed + 4) for _, g in sample_e1.groupby("decile")]
    return pd.concat(parts).sort_values("pc1").reset_index(drop=True)


def build_all(root=None):
    """Writes every locked data file. Deterministic from SEED and data/lin_pc1.csv."""
    import json
    from .pages import build_pages, build_honest_pages
    root = Path(root) if root else DATA
    df = load_lin(root / "lin_pc1.csv")
    s1 = stratified_sample(df)
    s1.to_csv(root / "sample_e1.csv", index=False)
    e4_sample(s1).to_csv(root / "sample_e4.csv", index=False)
    fab = make_fabricated(set(df.domain))
    write_csv(root / "fabricated" / "e2_domains.csv", fab,
              "FICTIONAL domains generated by floorprice.data.make_fabricated, seed 20261115. None appears in the Lin list.")
    for name, rows in (("e3_pages.jsonl", build_pages()), ("e3h_pages.jsonl", build_honest_pages())):
        with open(root / "pages" / name, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
    (root / "articles").mkdir(exist_ok=True)
    with open(root / "articles" / "e5_articles.jsonl", "w", encoding="utf-8") as fh:
        for r in make_articles():
            fh.write(json.dumps(r, sort_keys=True) + "\n")
