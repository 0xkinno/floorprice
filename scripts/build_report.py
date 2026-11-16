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
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("floorprice_numbers", ROOT / "scripts" / "numbers.py")
N = _iu.module_from_spec(_spec)
_spec.loader.exec_module(N)

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


BODY_FONT, HEAD_FONT = "Old Standard TT", "Arial"


def set_font(run, name, size=None, bold=None, italic=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic
    if color: run.font.color.rgb = RGBColor.from_string(color)


def add_inline(par, text, size=10):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            r = par.add_run(part[2:-2]); set_font(r, BODY_FONT, size, bold=True)
        elif part.startswith("`"):
            r = par.add_run(part[1:-1]); set_font(r, "Courier New", size - 1.5)
        elif part.startswith("*"):
            r = par.add_run(part[1:-1]); set_font(r, BODY_FONT, size, italic=True)
        else:
            r = par.add_run(part); set_font(r, BODY_FONT, size)


def para(doc, text="", align=None, size=10, before=0, after=6, left=0.0, right=0.0, style=None):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.12
    pf.left_indent, pf.right_indent = Inches(left), Inches(right)
    if align == "center": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if text: add_inline(p, text, size)
    return p


def heading(doc, text, level):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.keep_with_next = Pt(12 if level == 1 else 8), Pt(4), True
    r = p.add_run(text)
    set_font(r, HEAD_FONT, 13 if level == 1 else 11, bold=True)
    return p


def first_page_footnote(doc, text):
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    fp = sec.first_page_footer.paragraphs[0]
    fp.text = ""
    r = fp.add_run("1  " + text); set_font(r, BODY_FONT, 8.5)


def clear_body(doc):
    body = doc.element.body
    for el in list(body):
        if not el.tag.endswith("sectPr"):
            body.remove(el)


def build(md_text, out_docx, template=None):
    doc = Document(str(template)) if template else Document()
    if template:
        clear_body(doc)
    else:
        sec = doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, m, Inches(1.0))
        st = doc.styles["Normal"]; st.font.name = BODY_FONT; st.font.size = Pt(10)
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("# "):
            p = para(doc, align="center", after=10, before=6)
            r = p.add_run(ln[2:].strip()); set_font(r, BODY_FONT, 18, bold=True)
            sup = p.add_run("1"); set_font(sup, BODY_FONT, 18, bold=True); sup.font.superscript = True
        elif ln.startswith("^^b "):
            p = para(doc, align="center", after=0); r = p.add_run(ln[4:]); set_font(r, BODY_FONT, 11, bold=True)
        elif ln.startswith("^^i "):
            p = para(doc, align="center", after=8); r = p.add_run(ln[4:]); set_font(r, BODY_FONT, 10.5, italic=True)
        elif ln.startswith("^^ "):
            para(doc, ln[3:], align="center", after=6)
        elif ln.startswith("@@ "):
            first_page_footnote(doc, ln[3:].strip())
        elif ln.startswith(">> "):
            para(doc, ln[3:], left=0.55, right=0.55, after=8, size=10)
        elif ln.startswith("## Abstract"):
            p = para(doc, align="center", before=12, after=4); r = p.add_run("Abstract"); set_font(r, HEAD_FONT, 12, bold=True)
        elif ln.startswith("## "):
            heading(doc, ln[3:].strip(), 1)
        elif ln.startswith("### "):
            heading(doc, ln[4:].strip(), 2)
        elif ln.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", ln)
            path = ROOT / "report" / m.group(2)
            if path.exists():
                pp = doc.add_paragraph(); pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pp.add_run().add_picture(str(path), width=Inches(6.0))
            cap = para(doc, after=8, size=9); add_inline(cap, m.group(1), 9)
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s\-:|]+\|$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows))
            t.style = "Table Grid"
            for r_, row in enumerate(rows):
                for c_, cell in enumerate(row):
                    t.cell(r_, c_).text = ""
                    pr = t.cell(r_, c_).paragraphs[0]
                    pr.paragraph_format.space_after = Pt(1)
                    add_inline(pr, cell, 8.5)
                    if r_ == 0:
                        for run in pr.runs: run.bold = True
            para(doc, "", after=4)
            continue
        elif re.match(r"^\s*[-*] ", ln):
            add_inline(para(doc, after=2, left=0.25), "\u2022 " + re.sub(r"^\s*[-*] ", "", ln))
        elif re.match(r"^\d+\. ", ln):
            n = re.match(r"^(\d+)\. ", ln).group(1)
            p = para(doc, after=3, left=0.3); p.paragraph_format.first_line_indent = Inches(-0.25)
            add_inline(p, n + ".  " + re.sub(r"^\d+\. ", "", ln))
        else:
            buf = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||!\[|\s*[-*] |\d+\. |\^\^|>> |@@ )", lines[i + 1]):
                i += 1
                buf.append(lines[i])
            para(doc, " ".join(x.strip() for x in buf), after=6)
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
