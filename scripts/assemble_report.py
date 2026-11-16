#!/usr/bin/env python3
"""Assemble report/FLOORPRICE_report.md from report/parts/*.md in the template's section order."""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "report"
head = (root / "parts/head.md").read_text()
body = (root / "parts/body.md").read_text()
tail = (root / "parts/static_tail.md").read_text()
tail = tail.replace("{{DISCUSSION}}", (root / "parts/discussion.md").read_text().strip()).replace("{{CONCLUSION}}", (root / "parts/conclusion.md").read_text().strip())
refs = (root / "parts/references.md").read_text()
appc = (root / "parts/appendix_c.md").read_text()
d = {}
for ptxt in re.split(r"(?m)^(?=## )", tail):
    m = re.match(r"## (.+)", ptxt)
    if m:
        d[m.group(1).strip()] = ptxt
out = head + "\n" + body + "\n"
for k in ["5 Discussion and Limitations", "6 Conclusion", "Code and Data", "Author Contributions"]:
    out += d[k] + "\n"
out += refs + d["Appendix A Limitations and dual use"] + "\n" + d["Appendix B Pre-registration"] + "\n" + appc + d["LLM Usage Statement"]
(root / "FLOORPRICE_report.md").write_text(out)
print(len(out.split()), "words")
