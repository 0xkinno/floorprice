#!/usr/bin/env python3
"""Build report/FLOORPRICE_report.docx (and a PDF via LibreOffice when available) from report/FLOORPRICE_report.md.
{{fact:key}} placeholders are filled from results/FACTS.json. --draft renders missing facts as [PENDING key]; without it a missing fact fails.
If report/template.docx exists (the official template), its styles are used; otherwise a fallback with the same section order is built."""
import sys as _sys
from pathlib import Path as _P
# scripts/numbers.py must not shadow the standard library module of the same name
_sys.path = [p for p in _sys.path if _P(p or ".").resolve() != _P(__file__).resolve().parent]
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("floorprice_numbers", ROOT / "scripts" / "numbers.py")
N = _iu.module_from_spec(_spec)
_spec.loader.exec_module(N)

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_inline(par, text):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`"):
            r = par.add_run(part[1:-1])
            r.font.name = "Courier New"
        elif part.startswith("*"):
            par.add_run(part[1:-1]).italic = True
        else:
            par.add_run(part)


def clear_body(doc):
    body = doc.element.body
    for el in list(body):
        if not el.tag.endswith("sectPr"):
            body.remove(el)


def build(md_text, out_docx, template=None):
    doc = Document(str(template)) if template else Document()
    if template:
        clear_body(doc)
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("# "):
            doc.add_heading(ln[2:].strip(), level=0 if not template else 1)
        elif ln.startswith("## "):
            doc.add_heading(ln[3:].strip(), level=1)
        elif ln.startswith("### "):
            doc.add_heading(ln[4:].strip(), level=2)
        elif ln.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", ln)
            path = ROOT / "report" / m.group(2)
            if path.exists():
                doc.add_picture(str(path), width=Inches(6.0))
            cap = doc.add_paragraph()
            add_inline(cap, m.group(1))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s\-:|]+\|$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows))
            t.style = "Table Grid"
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    t.cell(r, c).text = ""
                    add_inline(t.cell(r, c).paragraphs[0], cell)
                    for run in t.cell(r, c).paragraphs[0].runs:
                        run.font.size = Pt(8)
            continue
        elif re.match(r"^\s*[-*] ", ln):
            add_inline(doc.add_paragraph(style="List Bullet"), re.sub(r"^\s*[-*] ", "", ln))
        elif re.match(r"^\d+\. ", ln):
            add_inline(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", ln))
        else:
            para = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||!\[|\s*[-*] |\d+\. )", lines[i + 1]):
                i += 1
                para.append(lines[i])
            add_inline(doc.add_paragraph(), " ".join(x.strip() for x in para))
        i += 1
    doc.save(str(out_docx))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true")
    a = ap.parse_args()
    facts = json.loads((ROOT / "results" / "FACTS.json").read_text())["facts"] if (ROOT / "results" / "FACTS.json").exists() else {}
    src = (ROOT / "report" / "FLOORPRICE_report.md").read_text(encoding="utf-8")
    text, missing = N.render(src, facts)
    if missing:
        if not a.draft:
            print("Missing facts (final build refused):", sorted(set(missing)))
            return 1
        text = re.sub(r"\{\{fact:([^}|]+)(?:\|[^}]*)?\}\}", lambda m: f"[PENDING {m.group(1).strip()}]", text)
    template = ROOT / "report" / "template.docx"
    if not template.exists():
        print("NOTE: report/template.docx not found. Building a fallback that mirrors the section order. Not the official template.")
    out = ROOT / "report" / ("FLOORPRICE_report_DRAFT.docx" if a.draft else "FLOORPRICE_report.docx")
    build(text, out, template if template.exists() else None)
    (ROOT / "report" / "FLOORPRICE_report.rendered.md").write_text(text, encoding="utf-8")
    print("wrote", out)
    if subprocess.run(["which", "soffice"], capture_output=True).returncode == 0:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(ROOT / "report"), str(out)],
                       capture_output=True, timeout=180)
        pdf = out.with_suffix(".pdf")
        if pdf.exists():
            n = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
            print([l for l in n.splitlines() if l.startswith("Pages")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
