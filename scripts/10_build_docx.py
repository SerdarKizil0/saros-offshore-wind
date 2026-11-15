"""
Build the master manuscript and the supplementary material (DOCX and PDF)
=========================================================================
Consumes the generated manuscript files (scripts/11_build_manuscript_sections.py)
and the publication figures (scripts/12_build_figures.py); nothing is typed here.

  manuscript/00_abstract.md ... 08_references.md   title, abstract, keywords,
                                                    Sections 1-6, declarations,
                                                    references
  manuscript/tables.md                              Tables 1-6
  manuscript/09_figures.md                          Figures 1-4 (captions, files)
  manuscript/supplementary_tables.md                Tables S1-S15
  figures/revised/fig*.png                          600 dpi figure files

Writes
  manuscript/output/Saros_Offshore_Wind_Master.docx / .pdf
  manuscript/output/Saros_Supplementary_Material.docx / .pdf

How it works
  1. The Markdown sources are assembled into one document. Each main-text
     table and figure is placed after the paragraph that cites it first.
  2. The eight display equations of Methods become native Word equations
     (OMML, written by pandoc from the LaTeX source). scripts/docx_filter.lua
     sets each in a borderless three-column row with its number (1)-(8) at
     the right margin; the number is bookmarked and "Eq. N" in the text is
     an internal link to it. No equation or table is an image.
  3. pandoc writes the DOCX with a reference document whose styles are
     defined below (journal-neutral layout: A4, Times New Roman 11 pt, 1.5
     line spacing, numbered pages, continuous line numbers in the master).
  4. The DOCX is post-processed: table rules and header rows, equation-row
     layout, page setup and the page-number footer.
  5. LibreOffice converts each DOCX to PDF, so the PDF shows the DOCX.

Reproducible: SOURCE_DATE_EPOCH fixes the document dates and ZIP entries are
written with fixed timestamps, so a rebuild gives identical DOCX parts.
`--check` rebuilds into a temporary folder and compares every DOCX part and
the PDF text with the committed files.

Run from the repository root:
  python scripts/10_build_docx.py            # build all four files
  python scripts/10_build_docx.py --check    # verify the committed files
"""
from __future__ import annotations

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parent.parent
MAN = ROOT / "manuscript"
OUT = MAN / "output"
FIG_DIR = ROOT / "figures" / "revised"
FILTER = ROOT / "scripts" / "docx_filter.lua"
MASTER = "Saros_Offshore_Wind_Master"
SUPPLEMENT = "Saros_Supplementary_Material"
SOURCE_DATE_EPOCH = "1794700800"            # 15 November 2026 00:00 UTC (fixed document date)
ZIP_DATE = (2026, 11, 15, 0, 0, 0)

# page: A4, 2.5 cm top/bottom, 2.0 cm left/right -> text width 17.0 cm
PAGE_W, PAGE_H = 11906, 16838               # twips
MARGIN_TB, MARGIN_LR = 1418, 1134
TEXT_WIDTH_CM = 17.0
FIGURE_WIDTH_CM = TEXT_WIDTH_CM
WIDE_TABLE_COLS = 8                          # tables with this many columns use the small table font and margins

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "r": R, "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
EQ_MARKER = "EQNLAYOUTTABLE"
PLACEHOLDER = re.compile(r"\[(AUTHOR TO CONFIRM\b[^\]]*)\]")


def q(tag: str) -> str:
    p, t = tag.split(":")
    return f"{{{NS[p]}}}{t}"


# ============================================================ sources
def generated(name: str) -> str:
    text = (MAN / name).read_text(encoding="utf-8")
    return re.sub(r"\A<!-- GENERATED FILE.*?-->\s*", "", text, flags=re.S)


@dataclass
class Table:
    label: str                     # "Table 1" or "Table S1"
    caption: str
    lines: list[str]               # pipe-table lines, header first
    notes: list[str]

    @property
    def ncols(self) -> int:
        return len(self.lines[0].strip().strip("|").split("|"))


def parse_tables(md: str) -> list[Table]:
    out = []
    for block in re.split(r"(?m)^## ", md)[1:]:
        head, _, body = block.partition("\n")
        m = re.match(r"(Table S?\d+)\. (.*)", head.strip())
        if not m:
            raise ValueError(f"unexpected table heading: {head[:60]}")
        paras = [p.strip() for p in body.strip().split("\n\n") if p.strip()]
        lines = [ln for p in paras if p.startswith("|") for ln in p.split("\n")]
        notes = [" ".join(p.split()) for p in paras if not p.startswith("|")]
        out.append(Table(m.group(1), m.group(2), lines, notes))
    return out


def _cell_len(cell: str) -> int:
    return len(re.sub(r"[*`]", "", cell).strip())


def table_markdown(t: Table) -> str:
    """Pipe table with a caption and column widths proportional to the content."""
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in t.lines if not re.fullmatch(r"\|[-| :]+\|", ln)]
    n = len(rows[0])
    longest = [max(_cell_len(r[i]) for r in rows if i < len(r)) for i in range(n)]
    word = [max(len(w) for r in rows if i < len(r) for w in re.sub(r"[*`]", "", r[i]).split() or ["-"])
            for i in range(n)]
    # a column is at least as wide as its longest word, and wider for long text (capped)
    weights = [max(word[i] + 1.5, min(longest[i], 34) ** 0.85, 4.0) for i in range(n)]
    dashes = [max(3, round(w / sum(weights) * 200)) for w in weights]
    rows = [[nonbreaking(c) for c in r] for r in rows]
    out = [f"Table: **{t.label}.** {nonbreaking(t.caption)}", "",
           "| " + " | ".join(rows[0]) + " |", "|" + "|".join("-" * d for d in dashes) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    for note in t.notes:
        out += ["", '::: {custom-style="Table Note"}', nonbreaking(note), ":::"]
    return "\n".join(out)


@dataclass
class Figure:
    number: int
    png: Path
    caption: str


def parse_figures(md: str) -> list[Figure]:
    out = []
    for m in re.finditer(r"!\[Figure (\d+)\]\(([^)]+)\)\s+(\*\*Figure \1\.\*\*.*?)(?=\n\n!\[|\Z)", md, re.S):
        png = (MAN / m.group(2)).resolve()
        out.append(Figure(int(m.group(1)), png, " ".join(m.group(3).split())))
    if [f.number for f in out] != [1, 2, 3, 4]:
        raise ValueError(f"expected Figures 1-4 in 09_figures.md, found {[f.number for f in out]}")
    for f in out:
        if not f.png.exists() or f.png.parent != FIG_DIR:
            raise FileNotFoundError(f"Figure {f.number}: {f.png} is not a current figure in figures/revised/")
    return out


def figure_markdown(f: Figure) -> str:
    # repository-relative path (resolved through --resource-path), so no local path enters the DOCX
    return f"![{nonbreaking(f.caption)}]({f.png.relative_to(ROOT).as_posix()}){{width={FIGURE_WIDTH_CM}cm}}"


# ============================================================ prose transforms
EQUATION = re.compile(r"\$\$\s*(.+?)\s*\\qquad\s*\((\d+)\)\s*\$\$", re.S)


def omml_compatible(latex: str) -> str:
    """Equivalent notation that Word and LibreOffice both render as intended.
    \\mathrm{X} -> \\text{X} (upright; LibreOffice ignores the plain style of \\mathrm runs),
    \\bar{X} -> \\overline{X} (LibreOffice draws the OMML accent of \\bar as an acute),
    \\qquad -> two em spaces inside \\text (LibreOffice drops LaTeX spacing commands)."""
    latex = re.sub(r"\\mathrm\{([^{}]*)\}", r"\\text{\1}", latex)
    latex = re.sub(r"\\bar\{([^{}]*)\}", r"\\overline{\1}", latex)
    return latex.replace("\\qquad", "\\text{\u2003\u2003}")


def math_compatible(text: str) -> str:
    text = re.sub(r"\$\$(.+?)\$\$", lambda m: "$$" + omml_compatible(m.group(1)) + "$$", text, flags=re.S)
    return re.sub(r"(?<![$\\])\$([^$\n]+?)\$(?!\$)", lambda m: "$" + omml_compatible(m.group(1)) + "$", text)


NBSP = "\u00a0"


def nonbreaking(text: str) -> str:
    """Keep digit groups (271 752), values and their % sign, and coordinates (26.25° E) on one line."""
    text = re.sub(r"(?<=\d) (?=\d{3}(?!\d))", NBSP, text)
    text = re.sub(r"(?<=\d) %", NBSP + "%", text)
    return re.sub(r"(?<=\d°) (?=[NE]\b)", NBSP, text)


def equations(text: str) -> str:
    """$$ ... \\qquad (N) $$  ->  a numbered equation block (see docx_filter.lua)."""
    return EQUATION.sub(lambda m: f'\n\n::: {{.equation number="{m.group(2)}"}}\n$$ {m.group(1)} $$\n:::\n\n', text)


def equation_links(text: str) -> str:
    return re.sub(r"\bEq\. (\d+)\b", r"[Eq. \1](#eq\1)", text)


def placeholders(text: str) -> str:
    """Author-dependent placeholders are kept verbatim and highlighted."""
    return PLACEHOLDER.sub(lambda m: "[\\[" + m.group(1) + "\\]]{custom-style=\"Placeholder\"}", text)


def prose(name: str) -> str:
    return nonbreaking(placeholders(equation_links(math_compatible(equations(generated(name))))))


TABLE_CITE = re.compile(r"(?<!Supplementary )(?<!Supplementary\n)\bTables? (\d)\b")
FIG_CITE = re.compile(r"\bFigs?\. (\d)")


# Layout tuning only: place a float this many prose paragraphs after its first citation (same
# section), where placing it immediately would leave a large gap before a tall figure.
FLOAT_DEFER = {("figure", 1): 1}


def place_floats(text: str, tables: dict, figures: dict, placed: dict) -> str:
    """Insert each table and figure after the paragraph that cites it first (see FLOAT_DEFER)."""
    out, pending = [], []                     # pending: [paragraphs to wait, markdown]
    for block in text.split("\n\n"):
        out.append(block)
        prose_block = not block.lstrip().startswith(("#", ":::", "$$"))
        if prose_block:
            for item in pending:
                item[0] -= 1
            out += [md for wait, md in pending if wait < 0]
            pending = [item for item in pending if item[0] >= 0]
            flat = " ".join(block.split())
            for kind, rx, store, render in (("table", TABLE_CITE, tables, table_markdown),
                                            ("figure", FIG_CITE, figures, figure_markdown)):
                for num in dict.fromkeys(int(n) for n in rx.findall(flat)):
                    if num in store and (kind, num) not in placed:
                        placed[(kind, num)] = True
                        wait = FLOAT_DEFER.get((kind, num), 0)
                        if wait:
                            pending.append([wait - 1, render(store[num])])
                        else:
                            out.append(render(store[num]))
    out += [md for _, md in pending]           # end of section: place whatever is still waiting
    return "\n\n".join(out)


# ============================================================ documents
def _yaml(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def title_and_abstract() -> tuple[str, str, str]:
    t = generated("00_abstract.md")
    title = re.search(r"(?m)^# (.+)$", t).group(1).strip()
    abstract = t.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0].strip()
    keywords = " ".join(t.split("**Keywords:**", 1)[1].split())
    return title, abstract, keywords


def references() -> str:
    t = generated("08_references.md")
    entries = [nonbreaking(" ".join(e.split())) for e in t.split("\n- ")[1:]]
    if len(entries) != 38:
        raise ValueError(f"expected 38 references, found {len(entries)}")
    body = "\n\n".join(entries)
    return f'# References\n\n::: {{custom-style="Reference"}}\n{body}\n:::'


def master_markdown() -> str:
    title, abstract, keywords = title_and_abstract()
    tables = {int(t.label.split()[1]): t for t in parse_tables(generated("tables.md"))}
    figures = {f.number: f for f in parse_figures(generated("09_figures.md"))}
    if sorted(tables) != [1, 2, 3, 4, 5, 6]:
        raise ValueError("expected Tables 1-6")
    placed: dict = {}
    parts = [
        "---", f"title: {_yaml(title)}", "---", "",
        '::: {custom-style="Author"}',
        "[\\[AUTHOR TO CONFIRM: author names, affiliations and corresponding author\\]]{custom-style=\"Placeholder\"}",
        ":::", "",
        "# Abstract", "", nonbreaking(abstract), "",
        '::: {custom-style="Keywords"}', f"**Keywords:** {keywords}", ":::", "",
        "::: pagebreak", ":::", "",
    ]
    for name in ("01_introduction.md", "02_study_area.md", "03_methodology.md", "04_results.md",
                 "05_discussion.md", "06_conclusion.md"):
        parts += [place_floats(prose(name), tables, figures, placed), ""]
    missing = [k for k in [("table", n) for n in tables] + [("figure", n) for n in figures] if k not in placed]
    if missing:
        raise ValueError(f"tables or figures never cited in Sections 1-6: {missing}")
    parts += [prose("07_declarations.md"), "", references(), ""]
    return "\n".join(parts)


def supplement_markdown() -> str:
    title, _, _ = title_and_abstract()
    tables = parse_tables(generated("supplementary_tables.md"))
    if [t.label for t in tables] != [f"Table S{i}" for i in range(1, 16)]:
        raise ValueError("expected Tables S1-S15")
    parts = ["---", f"title: {_yaml('Supplementary material')}", f"subtitle: {_yaml(title)}", "---", "",
             '::: {custom-style="Author"}',
             "[\\[AUTHOR TO CONFIRM: author names and affiliations\\]]{custom-style=\"Placeholder\"}", ":::", "",
             "This document contains Supplementary Tables S1–S15 cited in the manuscript. All values are "
             "model estimates generated from the result files of the study by the scripts described in the "
             "Code availability statement; none is a measurement. The sources cited in the tables are listed "
             "in the reference list of the manuscript.", ""]
    for t in tables:
        parts += [table_markdown(t), ""]
    return "\n".join(parts)


# ============================================================ reference document (styles)
FONT = "Times New Roman"


def _rpr(size_pt: float, bold=False, italic=False, color=None, font=FONT) -> str:
    x = f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'
    x += "<w:b/><w:bCs/>" if bold else ""
    x += "<w:i/><w:iCs/>" if italic else ""
    x += f'<w:color w:val="{color}"/>' if color else ""
    return x + f'<w:sz w:val="{round(size_pt * 2)}"/><w:szCs w:val="{round(size_pt * 2)}"/><w:lang w:val="en-GB"/>'


def _ppr(before=0, after=120, line=360, jc=None, keep_next=False, keep_lines=False, ind=None,
         outline=None, widow=True) -> str:
    x = "<w:keepNext/>" if keep_next else ""
    x += "<w:keepLines/>" if keep_lines else ""
    x += "<w:widowControl/>" if widow else ""
    x += f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'
    x += ind or ""
    x += f'<w:jc w:val="{jc}"/>' if jc else ""
    x += f'<w:outlineLvl w:val="{outline}"/>' if outline is not None else ""
    return x


PARA_STYLES = {   # styleId: (name, pPr, rPr)
    "Normal": ("Normal", _ppr(after=0, line=276), _rpr(11)),
    "BodyText": ("Body Text", _ppr(after=120, line=360, jc="both"), _rpr(11)),
    "FirstParagraph": ("First Paragraph", _ppr(after=120, line=360, jc="both"), _rpr(11)),
    "Compact": ("Compact", _ppr(after=40, line=300), _rpr(11)),
    "Title": ("Title", _ppr(before=0, after=240, line=300, jc="center", keep_next=True), _rpr(16, bold=True)),
    "Subtitle": ("Subtitle", _ppr(before=0, after=240, line=300, jc="center", keep_next=True), _rpr(12, italic=True)),
    "Author": ("Author", _ppr(before=0, after=360, line=276, jc="center"), _rpr(11)),
    "Heading1": ("heading 1", _ppr(before=360, after=120, line=276, keep_next=True, keep_lines=True, outline=0),
                 _rpr(13, bold=True)),
    "Heading2": ("heading 2", _ppr(before=240, after=120, line=276, keep_next=True, keep_lines=True, outline=1),
                 _rpr(11.5, bold=True)),
    "Heading3": ("heading 3", _ppr(before=200, after=80, line=276, keep_next=True, keep_lines=True, outline=2),
                 _rpr(11, bold=True, italic=True)),
    "TableCaption": ("Table Caption", _ppr(before=240, after=100, line=264, keep_next=True, keep_lines=True), _rpr(10)),
    "ImageCaption": ("Image Caption", _ppr(before=80, after=280, line=264, jc="both"), _rpr(10)),
    "CaptionedFigure": ("Captioned Figure", _ppr(before=200, after=0, line=240, jc="center", keep_next=True), _rpr(11)),
    "Figure": ("Figure", _ppr(before=200, after=0, line=240, jc="center", keep_next=True), _rpr(11)),
    "Bibliography": ("Bibliography", _ppr(after=80, line=276), _rpr(11)),
}
CUSTOM_STYLES = {
    "TableText": ("Table Text", _ppr(before=20, after=20, line=240, widow=False), _rpr(9)),
    "TableTextSmall": ("Table Text Small", _ppr(before=10, after=10, line=240, widow=False), _rpr(8)),
    "TableNote": ("Table Note", _ppr(before=60, after=240, line=252, jc="both"), _rpr(9)),
    "Keywords": ("Keywords", _ppr(before=120, after=120, line=300), _rpr(11)),
    "Reference": ("Reference", _ppr(after=60, line=264, ind='<w:ind w:left="397" w:hanging="397"/>'), _rpr(10.5)),
    "EquationText": ("Equation Text", _ppr(before=60, after=60, line=240, keep_lines=True, widow=False), _rpr(11)),
}


def _style_xml(sid: str, name: str, ppr: str, rpr: str, custom: bool) -> str:
    based = "" if sid == "Normal" else '<w:basedOn w:val="Normal"/>'
    c = ' w:customStyle="1"' if custom else ""
    return (f'<w:style xmlns:w="{W}" w:type="paragraph" w:styleId="{sid}"{c}><w:name w:val="{name}"/>{based}'
            f'<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


TABLE_STYLE = (f'<w:style xmlns:w="{W}" w:type="table" w:styleId="Table"><w:name w:val="Table"/>'
               '<w:basedOn w:val="TableNormal"/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/>'
               '<w:tblCellMar><w:top w:w="28" w:type="dxa"/><w:left w:w="85" w:type="dxa"/>'
               '<w:bottom w:w="28" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>')


def reference_docx(path: Path) -> Path:
    data = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], capture_output=True,
                          check=True).stdout
    src = zipfile.ZipFile(io.BytesIO(data))
    files = {n: src.read(n) for n in src.namelist()}
    styles = etree.fromstring(files["word/styles.xml"])
    by_id = {s.get(q("w:styleId")): s for s in styles.findall("w:style", NS)}
    for sid, (name, ppr, rpr) in PARA_STYLES.items():
        new = etree.fromstring(_style_xml(sid, name, ppr, rpr, custom=False))
        if sid in by_id:
            by_id[sid].getparent().replace(by_id[sid], new)
        else:
            styles.append(new)
    for sid, (name, ppr, rpr) in CUSTOM_STYLES.items():
        styles.append(etree.fromstring(_style_xml(sid, name, ppr, rpr, custom=True)))
    styles.append(etree.fromstring(
        f'<w:style xmlns:w="{W}" w:type="character" w:customStyle="1" w:styleId="Placeholder">'
        '<w:name w:val="Placeholder"/><w:rPr><w:shd w:val="clear" w:color="auto" w:fill="FFE699"/></w:rPr>'
        '</w:style>'))
    verbatim = (f'<w:style xmlns:w="{W}" w:type="character" w:customStyle="1" w:styleId="VerbatimChar">'
                '<w:name w:val="Verbatim Char"/><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" '
                'w:cs="Courier New"/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr></w:style>')
    if "VerbatimChar" in by_id:
        by_id["VerbatimChar"].getparent().replace(by_id["VerbatimChar"], etree.fromstring(verbatim))
    if "Table" in by_id:
        by_id["Table"].getparent().replace(by_id["Table"], etree.fromstring(TABLE_STYLE))
    if "Hyperlink" in by_id:
        h = by_id["Hyperlink"]
        h.getparent().replace(h, etree.fromstring(
            f'<w:style xmlns:w="{W}" w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/>'
            '<w:basedOn w:val="BodyTextChar"/><w:rPr><w:color w:val="1F3864"/></w:rPr></w:style>'))
    # document defaults: Times New Roman 11 pt, British English
    rpr_default = styles.find("w:docDefaults/w:rPrDefault/w:rPr", NS)
    if rpr_default is not None:
        for child in list(rpr_default):
            rpr_default.remove(child)
        for el in etree.fromstring(f'<w:rPr xmlns:w="{W}">{_rpr(11)}</w:rPr>'):
            rpr_default.append(el)
    files["word/styles.xml"] = etree.tostring(styles, xml_declaration=True, encoding="UTF-8", standalone=True)
    _write_zip(path, files)
    return path


# ============================================================ post-processing
def _el(xml: str):
    return etree.fromstring(f'<x xmlns:w="{W}" xmlns:r="{R}">{xml}</x>')[0]


def _set_child(parent, xml: str, tag: str):
    old = parent.find(tag, NS)
    new = _el(xml)
    if old is not None:
        parent.replace(old, new)
    else:
        parent.append(new)
    return new


def _tblpr(tbl):
    pr = tbl.find("w:tblPr", NS)
    if pr is None:
        pr = etree.SubElement(tbl, q("w:tblPr"))
        tbl.insert(0, pr)
    return pr


def _order_tblpr(pr):
    order = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize",
             "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
             "tblCaption", "tblDescription"]
    kids = sorted(list(pr), key=lambda e: order.index(etree.QName(e).localname)
                  if etree.QName(e).localname in order else 99)
    for k in kids:
        pr.remove(k)
        pr.append(k)


def _ppr_of(p):
    ppr = p.find("w:pPr", NS)
    if ppr is None:
        ppr = etree.Element(q("w:pPr"))
        p.insert(0, ppr)
    return ppr


def _cell_paragraph_style(tbl, style: str):
    for p in tbl.iter(q("w:p")):
        ppr = _ppr_of(p)
        old = ppr.find("w:pStyle", NS)
        if old is not None:
            ppr.remove(old)
        ppr.insert(0, _el(f'<w:pStyle w:val="{style}"/>'))


def _equation_table(tbl):
    for t in tbl.iter(q("w:t")):
        if t.text == EQ_MARKER:
            r = t.getparent()
            r.getparent().remove(r)
    pr = _tblpr(tbl)
    style = pr.find("w:tblStyle", NS)
    if style is not None:
        pr.remove(style)
    _set_child(pr, '<w:tblW w:w="5000" w:type="pct"/>', "w:tblW")
    _set_child(pr, "<w:tblBorders>" + "".join(f'<w:{s} w:val="nil"/>' for s in
               ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>", "w:tblBorders")
    _set_child(pr, '<w:tblLayout w:type="fixed"/>', "w:tblLayout")
    _order_tblpr(pr)
    for tc in tbl.iter(q("w:tc")):
        tcpr = tc.find("w:tcPr", NS)
        if tcpr is None:
            tcpr = etree.SubElement(tc, q("w:tcPr"))
            tc.insert(0, tcpr)
        _set_child(tcpr, '<w:vAlign w:val="center"/>', "w:vAlign")
    _cell_paragraph_style(tbl, "EquationText")
    for tr in tbl.findall("w:tr", NS):
        trpr = tr.find("w:trPr", NS)
        if trpr is None:
            trpr = etree.SubElement(tr, q("w:trPr"))
            tr.insert(0, trpr)
        _set_child(trpr, "<w:cantSplit/>", "w:cantSplit")


def _data_table(tbl):
    pr = _tblpr(tbl)
    _set_child(pr, '<w:tblW w:w="5000" w:type="pct"/>', "w:tblW")
    _set_child(pr, '<w:jc w:val="center"/>', "w:jc")
    _set_child(pr, '<w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
                   '<w:left w:val="nil"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
                   '<w:right w:val="nil"/><w:insideH w:val="single" w:sz="2" w:space="0" w:color="BFBFBF"/>'
                   '<w:insideV w:val="nil"/></w:tblBorders>', "w:tblBorders")
    _set_child(pr, '<w:tblLayout w:type="fixed"/>', "w:tblLayout")
    _order_tblpr(pr)
    rows = tbl.findall("w:tr", NS)
    ncols = len(rows[0].findall("w:tc", NS))
    wide = ncols >= WIDE_TABLE_COLS
    _cell_paragraph_style(tbl, "TableTextSmall" if wide else "TableText")
    if wide:                                   # narrow cell margins so short headers such as WSW fit
        _set_child(pr, '<w:tblCellMar><w:top w:w="20" w:type="dxa"/><w:left w:w="34" w:type="dxa"/>'
                       '<w:bottom w:w="20" w:type="dxa"/><w:right w:w="34" w:type="dxa"/></w:tblCellMar>',
                   "w:tblCellMar")
        _order_tblpr(pr)
    for i, tr in enumerate(rows):
        trpr = tr.find("w:trPr", NS)
        if trpr is None:
            trpr = etree.SubElement(tr, q("w:trPr"))
            tr.insert(0, trpr)
        _set_child(trpr, "<w:cantSplit/>", "w:cantSplit")
        if i == 0:
            _set_child(trpr, "<w:tblHeader/>", "w:tblHeader")
            for tc in tr.findall("w:tc", NS):
                tcpr = tc.find("w:tcPr", NS)
                if tcpr is None:
                    tcpr = etree.SubElement(tc, q("w:tcPr"))
                    tc.insert(0, tcpr)
                _set_child(tcpr, '<w:tcBorders><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                                 '</w:tcBorders>', "w:tcBorders")
                for r in tc.iter(q("w:r")):
                    rpr = r.find("w:rPr", NS)
                    if rpr is None:
                        rpr = etree.SubElement(r, q("w:rPr"))
                        r.insert(0, rpr)
                    if rpr.find("w:b", NS) is None:
                        rpr.insert(0, _el("<w:b/>"))
        # the header row stays with the first data row (the caption is kept with the header row)
        if i == 0:
            for p in tr.iter(q("w:p")):
                ppr = _ppr_of(p)
                if ppr.find("w:keepNext", NS) is None:
                    ppr.insert(1, _el("<w:keepNext/>"))


FOOTER = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:ftr xmlns:w="{W}"><w:p><w:pPr>'
          '<w:suppressLineNumbers/><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
          '<w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:rPr><w:sz w:val="20"/></w:rPr>'
          '<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/>'
          '</w:r><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/>'
          '</w:r></w:p></w:ftr>').encode()


def postprocess(docx: Path, line_numbers: bool) -> dict:
    z = zipfile.ZipFile(docx)
    files = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(files["word/document.xml"])
    body = doc.find("w:body", NS)
    n_eq = n_tab = 0
    for tbl in body.iter(q("w:tbl")):
        if any(t.text == EQ_MARKER for t in tbl.iter(q("w:t"))):
            _equation_table(tbl)
            n_eq += 1
            # the sentence that introduces an equation stays on the same page as the equation
            prev = tbl.getprevious()
            while prev is not None and etree.QName(prev).localname != "p":
                prev = prev.getprevious()
            if prev is not None:
                ppr = _ppr_of(prev)
                if ppr.find("w:keepNext", NS) is None:
                    ppr.insert(1, _el("<w:keepNext/>"))
        else:
            _data_table(tbl)
            n_tab += 1
    # figures at the full text width (pandoc caps image width to its own default page)
    emu = round(FIGURE_WIDTH_CM / 2.54 * 914400)
    for drawing in body.iter(q("w:drawing")):
        ext = drawing.find(".//wp:extent", {**NS, "wp": WP})
        if ext is None:
            continue
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        ext.set("cx", str(emu))
        ext.set("cy", str(round(cy * emu / cx)))
        for a_ext in drawing.iter(f"{{{A}}}ext"):
            if a_ext.get("cx") is not None:
                a_ext.set("cx", str(emu))
                a_ext.set("cy", str(round(cy * emu / cx)))
    # page setup, footer with page numbers, line numbers (master only)
    for s in body.findall("w:sectPr", NS):
        body.remove(s)
    ln = '<w:lnNumType w:countBy="1" w:distance="283" w:restart="continuous"/>' if line_numbers else ""
    body.append(_el(f'<w:sectPr><w:footerReference w:type="default" r:id="rIdPageFooter"/>'
                    f'<w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/><w:pgMar w:top="{MARGIN_TB}" w:right="{MARGIN_LR}" '
                    f'w:bottom="{MARGIN_TB}" w:left="{MARGIN_LR}" w:header="709" w:footer="567" w:gutter="0"/>'
                    f'{ln}<w:cols w:space="708"/></w:sectPr>'))
    files["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    files["word/footer_page.xml"] = FOOTER
    rels = files["word/_rels/document.xml.rels"].decode()
    if "rIdPageFooter" not in rels:
        rels = rels.replace("</Relationships>", '<Relationship Id="rIdPageFooter" Type="http://schemas.openxmlformats.'
                            'org/officeDocument/2006/relationships/footer" Target="footer_page.xml"/></Relationships>')
    files["word/_rels/document.xml.rels"] = rels.encode()
    ct = files["[Content_Types].xml"].decode()
    if "footer_page.xml" not in ct:
        ct = ct.replace("</Types>", '<Override PartName="/word/footer_page.xml" ContentType="application/vnd.'
                        'openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
    files["[Content_Types].xml"] = ct.encode()
    _write_zip(docx, files)
    return {"equation_rows": n_eq, "tables": n_tab}


def _write_zip(path: Path, files: dict):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files, key=lambda n: (n != "[Content_Types].xml", n)):
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, files[name])
    Path(path).write_bytes(buf.getvalue())


# ============================================================ build
def pandoc(markdown: str, ref: Path, out: Path, workdir: Path):
    src = workdir / (out.stem + ".md")
    src.write_text(markdown, encoding="utf-8")
    env = {**os.environ, "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH}
    r = subprocess.run(["pandoc", str(src), "--from", "markdown+pipe_tables+table_captions+implicit_figures"
                        "+fenced_divs+bracketed_spans+tex_math_dollars", "--to", "docx",
                        "--reference-doc", str(ref), "--lua-filter", str(FILTER), "--resource-path", str(ROOT),
                        "-o", str(out)],
                       capture_output=True, text=True, env=env, cwd=workdir)
    if r.returncode != 0 or r.stderr.strip():
        raise RuntimeError(f"pandoc failed for {out.name}: {r.stderr}")


def to_pdf(docx: Path, out_dir: Path) -> Path:
    profile = Path(tempfile.mkdtemp(prefix="lo_profile_"))
    opts = 'pdf:writer_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"true"},' \
           '"ReduceImageResolution":{"type":"boolean","value":"false"},' \
           '"ExportBookmarks":{"type":"boolean","value":"true"}}'
    try:
        r = subprocess.run(["soffice", f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", opts,
                            "--outdir", str(out_dir), str(docx)], capture_output=True, text=True, timeout=600)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = out_dir / (docx.stem + ".pdf")
    if r.returncode != 0 or not pdf.exists():
        raise RuntimeError(f"PDF conversion failed for {docx.name}: {r.stdout} {r.stderr}")
    return pdf


def build(out_dir: Path = OUT, pdf: bool = True, keep_markdown: bool = False) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ref = reference_docx(tmp / "reference.docx")
        for stem, md, numbers in ((MASTER, master_markdown(), True), (SUPPLEMENT, supplement_markdown(), False)):
            docx = out_dir / f"{stem}.docx"
            pandoc(md, ref, docx, tmp)
            report[stem] = postprocess(docx, line_numbers=numbers)
            if keep_markdown:
                (out_dir / f"{stem}.build.md").write_text(md, encoding="utf-8")
            if pdf:
                to_pdf(docx, out_dir)
    return report


def docx_parts(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def pdf_text(path: Path) -> str:
    r = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True)
    return r.stdout


def check() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        build(tmp)
        for stem in (MASTER, SUPPLEMENT):
            old, new = OUT / f"{stem}.docx", tmp / f"{stem}.docx"
            if not old.exists():
                problems.append(f"{old.name} is missing")
                continue
            a, b = docx_parts(old), docx_parts(new)
            if set(a) != set(b):
                problems.append(f"{stem}.docx: parts differ {sorted(set(a) ^ set(b))}")
            problems += [f"{stem}.docx: {n} differs from a fresh build" for n in sorted(set(a) & set(b)) if a[n] != b[n]]
            oldpdf = OUT / f"{stem}.pdf"
            if not oldpdf.exists():
                problems.append(f"{oldpdf.name} is missing")
            elif pdf_text(oldpdf) != pdf_text(tmp / f"{stem}.pdf"):
                problems.append(f"{stem}.pdf: text differs from a fresh build")
    return problems


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--check", action="store_true", help="compare committed outputs with a fresh build")
    parser.add_argument("--no-pdf", action="store_true", help="write the DOCX files only")
    parser.add_argument("--keep-markdown", action="store_true", help="also write the assembled Markdown")
    args = parser.parse_args()
    if args.check:
        found = check()
        print("\n".join(found) if found else "documents up to date")
        sys.exit(1 if found else 0)
    print(build(pdf=not args.no_pdf, keep_markdown=args.keep_markdown))
