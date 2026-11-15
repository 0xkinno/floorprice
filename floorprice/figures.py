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


def fig1(A, out):
    """Needs the auditability coding. Floor price against auditability score, marker size is validity."""
    aud = A.get("audit", {}).get("scores")
    if not aud:
        return False
    pts = points(A)
    fig, ax = plt.subplots(figsize=(7, 4.6), facecolor=PAPER)
    _style(ax)
    for p in pts:
        key = next((k for k in aud if k.startswith(p["name"].split()[0] + "|") and k.endswith("|b")), None)
        if key is None or p["usd"] is None:
            continue
        x = aud[key]["coder1"]
        y = p["usd"] if p["usd"] != float("inf") else 1e6
        ax.scatter(x, y, s=120, marker="o" if p["real"] else "s", color=MOSS, edgecolor=INK, zorder=3)
        ax.annotate(p["name"], (x, y), fontsize=7, xytext=(4, 4), textcoords="offset points", color=INK)
    ax.set_yscale("log")
    ax.set_xlabel("auditability, share of six criteria met (typical public deployment)", color=INK, fontsize=8)
    ax.set_ylabel("floor price, dollars (log)", color=INK, fontsize=8)
    fig.tight_layout()
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
