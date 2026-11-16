"""Figure 1 (floor price vs auditability, marker size = validity, honest wait panel) and a floor-vs-wait view that
needs no coding. Circles are real model measurements; squares are simulations. Palette from DESIGN.md."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
PAPER, INK, MOSS, EMBER, LIME, HAIR = "#F3F2EC", "#15171A", "#3E5B2A", "#D9542B", "#C8F25A", "#D9D6CC"
REAL = ("T1", "T2", "T3")


def _num(x):
    return float("inf") if x in ("inf", "Infinity") else x


def cheapest_usd(row, level="mid"):
    vals = []
    for a in row["attacks"].values():
        u = a.get("usd")
        if u:
            vals.append(_num(u[level]))
    return min(vals) if vals else None


def points(A, level="mid"):
    pts = []
    audit = A.get("audit", {})
    for row in A["table"]:
        name = row["technique"]
        pts.append({"name": name, "usd": cheapest_usd(row, level), "wait": _num(row["honest_wait"]["native"]),
                    "unit": row["honest_wait"]["unit"], "real": name.split()[0] in REAL,
                    "native": {k: _num(a["native"]) for k, a in row["attacks"].items()}})
    return pts


def _style(ax):
    ax.set_facecolor(PAPER)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(INK)
    ax.tick_params(colors=INK, labelsize=8)
    ax.grid(axis="y", color=HAIR, lw=0.6)


def fig_floor(A, out):
    pts = points(A)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6), facecolor=PAPER)
    for ax in (a, b):
        _style(ax)
    top = 1e6
    for i, p in enumerate(pts):
        y = p["usd"]
        inf = y is not None and y == float("inf")
        yy = top if inf else (y if y and y > 0 else 1e-3)
        a.scatter(i, yy, marker="o" if p["real"] else "s", s=90, color=EMBER if inf is False else MOSS, edgecolor=INK, zorder=3)
        if y is None:
            a.annotate("unpriced", (i, 1e-3), fontsize=7, ha="center", color=INK)
        a.annotate(p["name"].replace(" ", "\n", 1), (i, 2e-4), fontsize=6, ha="center", va="top", color=INK)
    a.set_yscale("log")
    a.set_ylim(1e-4, 3e6)
    a.set_xticks([])
    a.set_ylabel("floor price, dollars, mid prices (log)", color=INK, fontsize=8)
    a.set_title("Floor price: cheapest priced attack", fontsize=9, color=INK, loc="left")
    for i, p in enumerate(pts):
        w = p["wait"]
        winf = w == float("inf")
        b.bar(i, 1 if winf else max(w, 0.3), color=EMBER if winf else MOSS, edgecolor=INK, hatch="//" if winf else None)
        b.annotate(f"{p['unit']}s" if not winf else "no path", (i, 0.3), fontsize=6, ha="center", va="top", color=INK)
    b.set_yscale("log")
    b.set_xticks([])
    b.set_ylabel("honest newcomer wait, native units (log)", color=INK, fontsize=8)
    b.set_title("Honest wait", fontsize=9, color=INK, loc="left")
    fig.text(0.01, 0.01, "Circles: real model measurements. Squares: simulation. Hatched: no crossing observed or no purchase path.",
             fontsize=7, color=INK)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out, dpi=200, facecolor=PAPER)
    plt.close(fig)


def _tid(name):
    import re
    m = re.match(r"T\d", name)
    return m.group(0) if m else None


def fig1(A, out):
    """Headline: floor price (log dollars) against auditability (share of six criteria, mean of the two coders, typical public
    deployment). Marker size is validity (Spearman rho against expert ratings) where it was measured on real domains; hollow markers mean
    validity was not measured. An arrow at the top means no priced attack crossed. Circles are real model measurements, squares simulations."""
    aud = A.get("audit", {}).get("scores")
    if not aud:
        return False
    rho = A.get("llm", {}).get("H1_pooled", {}).get("rho")
    pts = points(A)
    fig, ax = plt.subplots(figsize=(7.6, 5.0), facecolor=PAPER)
    _style(ax)
    top = 3e5
    seen = {}
    for p in pts:
        tid = _tid(p["name"])
        key = f"{tid}|b"
        if key not in aud or p["usd"] is None:
            continue
        x = (aud[key]["coder1"] + aud[key]["coder2"]) / 2
        inf = p["usd"] == float("inf")
        y = top if inf else max(p["usd"], 3e-3)
        measured = tid == "T1" or tid == "T2"
        size = 260 if tid == "T1" else (60 + 300 * max(rho or 0, 0)) if tid == "T2" else 90
        ax.scatter(x, y, s=size, marker=("o" if p["real"] else "s"), facecolor=(MOSS if measured else "none"), edgecolor=INK, linewidth=1.3, zorder=3)
        if inf:
            ax.annotate("", xy=(x, y * 2.6), xytext=(x, y * 1.35), arrowprops=dict(arrowstyle="->", color=INK, lw=1.1), annotation_clip=False)
        bucket = (round(x, 2), round(__import__("math").log10(y)))
        idx = seen.get(bucket, 0)
        seen[bucket] = idx + 1
        label = p["name"] + (" *" if p["name"] == "T4 TrustRank" else "")
        ax.annotate(label, (x, y), fontsize=7, xytext=((-9 if tid == "T3" else 9), -3 - 11 * idx if idx % 2 == 0 else 8 + 11 * (idx // 2)), textcoords="offset points", color=INK, ha=("right" if tid == "T3" else "left"))
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 3e6)
    ax.set_xlim(-0.05, 1.05)
    ax.set_xlabel("auditability, share of six criteria met (typical public deployment, mean of two coders)", color=INK, fontsize=8)
    ax.set_ylabel("floor price, dollars at mid prices (log)", color=INK, fontsize=8)
    fig.text(0.01, 0.012, "Circle: real model or real data. Square: simulation. Filled: validity measured on real domains (size = Spearman rho; T1 is 1 by construction).\nHollow: validity not measured. Arrow: no priced attack crossed. *: bought links do cross T4 TrustRank (25 links) but have no citable price.", fontsize=6.3, color=INK, linespacing=1.5)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(out, dpi=200, facecolor=PAPER)
    plt.close(fig)
    return True


def main():
    p = ROOT / "results" / "analysis.json"
    if not p.exists():
        print("no results/analysis.json; run scripts/facts.py")
        return
    A = json.loads(p.read_text())
    outdir = ROOT / "report" / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    if A["table"]:
        fig_floor(A, outdir / "fig_floor_wait.png")
    ok = fig1(A, outdir / "fig1_headline.png")
    print("figures written; fig1 headline:", "yes" if ok else "pending auditability coding")


if __name__ == "__main__":
    main()
