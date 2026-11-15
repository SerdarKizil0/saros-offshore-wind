"""
Phase 5C-2: integrity of the master manuscript and the supplementary material (DOCX and PDF).

The tests read the committed files in manuscript/output/ and compare them with the generated
Markdown sources, the result files and the figure files. They establish completeness,
numbering, provenance and the absence of retired content; they do not establish visual
quality, which was checked by rendering and inspecting every PDF page
(docs/review/PHASE5C2_MASTER_BUILD_REPORT.md).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MAN = ROOT / "manuscript"
OUT = MAN / "output"
REV = ROOT / "results" / "revised"
FIG = ROOT / "figures" / "revised"
MASTER_DOCX, MASTER_PDF = OUT / "Saros_Offshore_Wind_Master.docx", OUT / "Saros_Offshore_Wind_Master.pdf"
SUPP_DOCX, SUPP_PDF = OUT / "Saros_Supplementary_Material.docx", OUT / "Saros_Supplementary_Material.pdf"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
TITLE = ("Long-term reanalysis-based energy yield of the Gulf of Saros offshore wind candidate area, Türkiye: "
         "sensitivity to reference period, grid node and wind data source")
HAVE_PDFTOOLS = shutil.which("pdftotext") is not None and shutil.which("pdfinfo") is not None


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def norm(t: str) -> str:
    """Whitespace, non-breaking spaces and pandoc's typographic quotes normalised."""
    t = t.replace(" ", " ").replace(" ", " ")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(t.split())


def J(name):
    return json.loads((REV / name).read_text(encoding="utf-8"))


class Doc:
    def __init__(self, path: Path):
        with zipfile.ZipFile(path) as z:
            self.parts = {n: z.read(n) for n in z.namelist()}
        self.root = etree.fromstring(self.parts["word/document.xml"])
        self.body = self.root.find("w:body", NS)

    @staticmethod
    def text(el) -> str:
        return "".join(t.text or "" for t in el.iter(f"{{{NS['w']}}}t"))

    def paragraphs(self, style: str | None = None):
        for p in self.body.iter(f"{{{NS['w']}}}p"):
            s = p.find("w:pPr/w:pStyle", NS)
            if style is None or (s is not None and s.get(f"{{{NS['w']}}}val") == style):
                yield p

    def styled(self, style: str) -> list[str]:
        return [norm(self.text(p)) for p in self.paragraphs(style)]

    def tables(self):
        return self.body.findall(".//w:tbl", NS)

    def is_equation_table(self, tbl) -> bool:
        return tbl.find(".//m:oMathPara", NS) is not None and len(tbl.findall("w:tr", NS)) == 1

    def data_tables(self):
        return [t for t in self.tables() if not self.is_equation_table(t)]

    def equation_tables(self):
        return [t for t in self.tables() if self.is_equation_table(t)]

    def all_text(self) -> str:
        return norm(" ".join(self.text(p) for p in self.body.iter(f"{{{NS['w']}}}p")))


@pytest.fixture(scope="module")
def master():
    return Doc(MASTER_DOCX)


@pytest.fixture(scope="module")
def supp():
    return Doc(SUPP_DOCX)


@pytest.fixture(scope="module")
def builder():
    return _load("build10_t", "scripts/10_build_docx.py")


def pdf_text(path: Path, layout=False) -> str:
    args = ["pdftotext"] + (["-layout"] if layout else []) + [str(path), "-"]
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def pdf_pages(path: Path) -> int:
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", info).group(1))


def md_table_cells(md: str) -> dict[str, list[list[str]]]:
    out = {}
    for block in re.split(r"(?m)^## ", md)[1:]:
        head, _, body = block.partition("\n")
        label = re.match(r"(Table S?\d+)\.", head).group(1)
        rows = [ln for ln in body.split("\n") if ln.startswith("|") and not re.fullmatch(r"\|[-| :]+\|", ln)]
        out[label] = [[norm(re.sub(r"[*`]", "", c)) for c in r.strip().strip("|").split("|")] for r in rows]
    return out


def docx_table_cells(doc: Doc, tbl) -> list[list[str]]:
    return [[norm(doc.text(tc)) for tc in tr.findall("w:tc", NS)] for tr in tbl.findall("w:tr", NS)]


# ============================================================ files and page setup
def test_all_four_deliverables_exist_and_are_valid():
    for p in (MASTER_DOCX, MASTER_PDF, SUPP_DOCX, SUPP_PDF):
        assert p.exists() and p.stat().st_size > 10_000, p
    for p in (MASTER_DOCX, SUPP_DOCX):
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            assert {"[Content_Types].xml", "word/document.xml", "word/styles.xml"} <= set(z.namelist())
            assert not [n for n in z.namelist() if n.endswith("/")]           # no folder entries
        import docx                                                           # python-docx opens it
        d = docx.Document(str(p))
        assert d.paragraphs


@pytest.mark.skipif(not HAVE_PDFTOOLS, reason="poppler tools not installed")
def test_pdf_pages_size_and_fonts():
    for p, lo, hi in ((MASTER_PDF, 20, 32), (SUPP_PDF, 4, 10)):
        n = pdf_pages(p)
        assert lo <= n <= hi, (p.name, n)
        info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout
        assert "595.3" in info and "841.8" in info                           # A4
        fonts = subprocess.run(["pdffonts", str(p)], capture_output=True, text=True).stdout.splitlines()[2:]
        assert fonts and all(" yes " in f for f in fonts), "every PDF font is embedded"


def test_page_setup_footer_and_line_numbers(master, supp):
    for doc, numbered in ((master, True), (supp, False)):
        sect = doc.body.find("w:sectPr", NS)
        sz, mar = sect.find("w:pgSz", NS), sect.find("w:pgMar", NS)
        w = f"{{{NS['w']}}}"
        assert (sz.get(w + "w"), sz.get(w + "h")) == ("11906", "16838")
        assert (mar.get(w + "top"), mar.get(w + "left")) == ("1418", "1134")
        assert (sect.find("w:lnNumType", NS) is not None) == numbered
        ref = sect.find("w:footerReference", NS)
        footer = doc.parts["word/footer_page.xml"].decode()
        assert ref is not None and "PAGE" in footer and "suppressLineNumbers" in footer
    styles = master.parts["word/styles.xml"].decode()
    assert 'w:styleId="Heading1"' in styles and "Times New Roman" in styles


# ============================================================ structure
SECTION_HEADINGS = ["Abstract", "1. Introduction", "2. Study Area", "3. Materials and Methods", "4. Results",
                    "5. Discussion", "6. Conclusions", "Declarations", "References"]


def test_title_abstract_keywords_and_section_order(master):
    assert master.styled("Title") == [TITLE]
    assert master.styled("Heading1") == SECTION_HEADINGS
    kw = master.styled("Keywords")
    assert len(kw) == 1 and kw[0].startswith("Keywords: offshore wind energy; ERA5 reanalysis")
    abstract = norm(MAN.joinpath("00_abstract.md").read_text(encoding="utf-8")
                    .split("## Abstract", 1)[1].split("**Keywords:**")[0])
    assert abstract in master.all_text()
    h2 = master.styled("Heading2")
    for sub in ("2.6. The candidate polygon and the reanalysis grid", "3.10. Supplementary descriptive statistics",
                "4.8. Operational grid-CO₂ accounting", "5.9. Implications for measurement and for further assessment",
                "Data availability", "Use of generative artificial intelligence", "Acknowledgements"):
        assert sub in h2, sub


def test_every_prose_paragraph_of_the_sources_is_in_the_master(master):
    """Each paragraph of the generated Markdown (minus markup) occurs verbatim in the DOCX text."""
    body = master.all_text()
    n = 0
    for name in ("01_introduction.md", "02_study_area.md", "03_methodology.md", "04_results.md",
                 "05_discussion.md", "06_conclusion.md", "07_declarations.md"):
        text = re.sub(r"\A<!--.*?-->", "", (MAN / name).read_text(encoding="utf-8"), flags=re.S)
        for block in text.split("\n\n"):
            b = block.strip()
            if not b or b.startswith(("#", "$$", "- ", "<!--")) or "$" in b:
                continue
            plain = norm(re.sub(r"\*\*?|`", "", b).replace("\\[", "[").replace("\\]", "]"))
            assert plain in body, plain[:80]
            n += 1
    assert n > 70


# ============================================================ equations
def test_eight_native_numbered_equations(master):
    eqs = master.equation_tables()
    assert len(eqs) == 8
    numbers = [norm(master.text(t.findall(".//w:tc", NS)[-1])) for t in eqs]
    assert numbers == [f"({i})" for i in range(1, 9)]
    for i, t in enumerate(eqs, start=1):
        assert t.find(".//w:drawing", NS) is None and t.find(".//w:pict", NS) is None   # not an image
        assert len(t.findall(".//m:oMath", NS)) == 1
        names = [b.get(f"{{{NS['w']}}}name") for b in t.iter(f"{{{NS['w']}}}bookmarkStart")]
        assert f"eq{i}" in names
        math_text = "".join(x.text or "" for x in t.iter(f"{{{NS['m']}}}t"))
        assert "qquad" not in math_text and f"({i})" not in math_text
        borders = t.find("w:tblPr/w:tblBorders", NS)
        assert borders is not None and all(b.get(f"{{{NS['w']}}}val") == "nil" for b in borders)
        assert "EQNLAYOUTTABLE" not in master.text(t)


def test_equation_structure_matches_the_latex(master):
    eqs = master.equation_tables()
    has = lambda t, tag: t.find(f".//m:{tag}", NS) is not None                  # noqa: E731
    mtext = lambda t: "".join(x.text or "" for x in t.iter(f"{{{NS['m']}}}t"))  # noqa: E731
    assert has(eqs[0], "f") and "ln" in mtext(eqs[0])                          # (1) ratio of logarithms
    assert has(eqs[1], "sSup") and "105" in mtext(eqs[1])                      # (2) power law
    assert has(eqs[2], "nary") and "∑" in "".join(c.get(f"{{{NS['m']}}}val", "") for c in
                                                   eqs[2].iter(f"{{{NS['m']}}}chr")) + mtext(eqs[2])   # (3) sum
    assert "η" in mtext(eqs[3]) and "CF" in mtext(eqs[3])                     # (4) losses
    assert "×" in mtext(eqs[4])                                                 # (5) Y = CF x H
    assert has(eqs[5], "rad") and "±" in mtext(eqs[5])                         # (6) t-interval
    assert has(eqs[6], "f") and "100" in mtext(eqs[6])                         # (7) relative change
    assert "EF" in mtext(eqs[7]) and "CM" in mtext(eqs[7])                     # (8) accounting
    # upright multi-letter symbols are normal text, not italic variables
    for t in (eqs[2], eqs[3], eqs[4], eqs[7]):
        nor = [r for r in t.iter(f"{{{NS['m']}}}r") if r.find("m:rPr/m:nor", NS) is not None]
        assert any((r.findtext("m:t", namespaces=NS) or "") in ("CF", "EF", "CM", "hub") for r in nor)


def test_equation_references_resolve(master):
    links = [h for h in master.body.iter(f"{{{NS['w']}}}hyperlink") if h.get(f"{{{NS['w']}}}anchor")]
    anchors = {h.get(f"{{{NS['w']}}}anchor"): norm(master.text(h)) for h in links}
    bookmarks = {b.get(f"{{{NS['w']}}}name") for b in master.body.iter(f"{{{NS['w']}}}bookmarkStart")}
    eq_links = {a: t for a, t in anchors.items() if a.startswith("eq")}
    assert eq_links == {"eq6": "Eq. 6"}
    assert all(a in bookmarks for a in eq_links)
    cited = set(re.findall(r"\bEq\. (\d)", master.all_text()))
    assert cited and all(1 <= int(n) <= 8 for n in cited)


@pytest.mark.skipif(not HAVE_PDFTOOLS, reason="poppler tools not installed")
def test_pdf_shows_every_equation(master):
    text = pdf_text(MASTER_PDF)
    lines = [ln.strip() for ln in text.splitlines()]
    assert [ln for ln in lines if re.fullmatch(r"\([1-8]\)", ln)] == [f"({i})" for i in range(1, 9)]
    flat = norm(text)
    for token in ("ln", "∑", "√", "EFCM", "CFn", "100 %"):
        assert token.replace(" ", "") in flat.replace(" ", ""), token


# ============================================================ tables
def test_main_tables_are_complete_numbered_and_editable(master):
    md = md_table_cells(re.sub(r"\A<!--.*?-->", "", (MAN / "tables.md").read_text(encoding="utf-8"), flags=re.S))
    tables = master.data_tables()
    captions = master.styled("TableCaption")
    assert [c.split(".")[0] for c in captions] == [f"Table {i}" for i in range(1, 7)]
    assert len(tables) == 6
    for i, tbl in enumerate(tables, start=1):
        assert docx_table_cells(master, tbl) == md[f"Table {i}"], f"Table {i}"
        assert tbl.find(".//w:drawing", NS) is None
        assert tbl.find("w:tr/w:trPr/w:tblHeader", NS) is not None              # header repeats


def test_tables_and_figures_follow_their_first_citation(master):
    """Captions appear in numerical order and after the paragraph that first cites them."""
    seen_text = ""
    order = []
    for p in master.paragraphs():
        style = p.find("w:pPr/w:pStyle", NS)
        s = style.get(f"{{{NS['w']}}}val") if style is not None else ""
        t = norm(master.text(p))
        if s in ("TableCaption", "ImageCaption"):
            label = re.match(r"(Table \d|Figure \d)\.", t).group(1)
            num = label.split()[1]
            cite = rf"\bTables? {num}\b" if label.startswith("Table") else rf"\bFigs?\. {num}"
            assert re.search(cite, seen_text), f"{label} placed before it is cited"
            order.append(label)
        else:
            seen_text += " " + t
    assert [o for o in order if o.startswith("Table")] == [f"Table {i}" for i in range(1, 7)]
    assert [o for o in order if o.startswith("Figure")] == [f"Figure {i}" for i in range(1, 5)]


def test_supplementary_tables_are_complete(supp):
    md = md_table_cells(re.sub(r"\A<!--.*?-->", "", (MAN / "supplementary_tables.md").read_text(encoding="utf-8"),
                              flags=re.S))
    captions = supp.styled("TableCaption")
    assert [c.split(".")[0] for c in captions] == [f"Table S{i}" for i in range(1, 16)]
    tables = supp.data_tables()
    assert len(tables) == 15 and not supp.equation_tables()
    for i, tbl in enumerate(tables, start=1):
        assert docx_table_cells(supp, tbl) == md[f"Table S{i}"], f"Table S{i}"
    assert supp.styled("Subtitle") == [TITLE]
    assert not supp.body.findall(".//w:drawing", NS)


def test_every_supplementary_table_is_cited_in_the_master(master):
    text = master.all_text()
    cited = set(re.findall(r"Supplementary Tables? (S\d+)", text)) | set(re.findall(r"Tables (S\d+) and S\d+", text))
    cited |= {m for a, b in re.findall(r"Supplementary Tables (S\d+) and (S\d+)", text) for m in (a, b)}
    assert cited == {f"S{i}" for i in range(1, 16)}


# ============================================================ figures
def test_four_current_figures_with_their_captions(master):
    rels = master.parts["word/_rels/document.xml.rels"].decode()
    blips = [b.get(f"{{{NS['r']}}}embed") for b in master.body.iter(f"{{{NS['a']}}}blip")]
    assert len(blips) == 4
    targets = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    stems = ["fig1_site_map", "fig2_temporal_sensitivity", "fig3_nodes_and_products", "fig4_sensitivity_categories"]
    for rid, stem in zip(blips, stems):
        data = master.parts["word/" + targets[rid]]
        assert hashlib.sha256(data).digest() == hashlib.sha256((FIG / f"{stem}.png").read_bytes()).digest(), stem
    for ext in master.body.iter(f"{{{NS['wp']}}}extent"):
        assert int(ext.get("cx")) == pytest.approx(17.0 / 2.54 * 914400, rel=1e-3)   # 17 cm, the text width
    assert "figure1.png" not in rels and "figures_final" not in rels
    caps = master.styled("ImageCaption")
    source = (MAN / "09_figures.md").read_text(encoding="utf-8")
    want = [norm(re.sub(r"\*\*", "", m)) for m in
            re.findall(r"(\*\*Figure \d\.\*\*.*?)(?=\n\n!\[|\Z)", source, re.S)]
    assert caps == want


def test_figure_caption_follows_its_image(master):
    paras = list(master.paragraphs())
    for i, p in enumerate(paras):
        if p.find(".//a:blip", NS) is not None:
            nxt = paras[i + 1]
            assert nxt.find("w:pPr/w:pStyle", NS).get(f"{{{NS['w']}}}val") == "ImageCaption"
            assert p.find("w:pPr/w:keepNext", NS) is not None or "CaptionedFigure" in etree.tostring(p).decode()


# ============================================================ references and citations
def test_single_alphabetical_reference_list_matching_the_sources(master, supp):
    refs = master.styled("Reference")
    src = re.sub(r"\A<!--.*?-->", "", (MAN / "08_references.md").read_text(encoding="utf-8"), flags=re.S)
    entries = [norm(re.sub(r"\*", "", e)) for e in src.split("\n- ")[1:]]
    assert refs == entries and len(refs) == 38
    assert "Official and institutional documents" not in master.all_text()      # one list, no sub-lists
    assert "Working reference list" not in master.all_text()
    t5 = _load("t5b2_refs", "tests/test_manuscript_5b2.py")
    cited = t5._citations()
    assert set(t5._reference_entries()) == cited                                # every entry cited, and vice versa
    # every entry is cited in the master text, or (TEDAŞ 2025 only) in a supplementary table, whose
    # sources the supplement says are listed in the manuscript's reference list
    body = master.all_text().split("References Aksoy")[0]
    supp_only = set()
    for key in cited:
        name, year = key.rsplit(" ", 1)
        rx = re.escape(key) if key.startswith("Official Gazette") else rf"{re.escape(name)}[^()]{{0,40}}\(?{year}"
        if not re.search(rx, body):
            assert re.search(rx, supp.all_text()), key
            supp_only.add(key)
    assert supp_only == {"TEDAŞ 2025"}
    assert "listed in the reference list of the manuscript" in supp.all_text()
    for doi in re.findall(r"doi:(\S+)", " ".join(entries)):
        assert doi.rstrip(".") in master.all_text()


# ============================================================ scientific integrity
def test_primary_numbers_match_the_results(master):
    t = master.all_text()
    ey, ias = J("energy_yield.json"), J("interannual_and_sampling.json")
    ns, ps = J("node_sensitivity.json")["nodes"], J("period_sensitivity.json")["periods"]
    lo, hi = ias["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    for token in (f"{ey['net']['gwh_per_mw']:.3f} GWh MW⁻¹ yr⁻¹", f"{ey['net_cf'] * 100:.2f} %",
                  f"{lo:.3f}–{hi:.3f}", f"{ns['W']['energy_rel_to_primary_node_pct']:+.1f} %",
                  f"{ns['E']['energy_rel_to_primary_node_pct']:+.1f} %".replace("-", "−"),
                  f"{ps['2014-2024']['energy_change_vs_reference_pct']:.1f} %", "1994–2024"):
        assert token in t, token


def test_no_retired_values_methods_or_claims(master, supp):
    for doc in (master, supp):
        t = doc.all_text()
        for bad in (r"Monte Carlo", r"P10–P90", r"\bP50\b", r"fuel-resolved", r"households", r"passenger car",
                    r"1,515|1 515\b", r"2\.62 TWh", r"\bthe first\b", r"to our knowledge", r"bankable",
                    r"ERA5-Based Assessment under Uncertainty", r"Energies \(MDPI\)"):
            assert not re.search(bad, t), (bad, doc)
    mt = master.all_text()
    assert "2.427" not in mt                                    # the retired 2014-2024 primary value
    for m in re.finditer(r"2\.427", supp.all_text()):           # only as the 2014-2024 comparison row/window
        ctx = supp.all_text()[max(0, m.start() - 160):m.start()]
        assert "2014–2024" in ctx


def test_framing_and_qualifications_survive(master):
    t = master.all_text()
    for phrase in ("candidate area, not an approved project", "not an official verified boundary",
                   "conditional on a future allocation", "not averaged", "not a correction",
                   "the only probabilistic interval", "they are not combined into one uncertainty interval",
                   "not samples of one distribution", "not a forecast of the generation",
                   "sensitivity to reference period, grid node and wind data source"):
        assert phrase in t, phrase
    for bad in (r"(grid[- ]node|neighbour\w*|GWA|wind product)[^.]{0,80}\b(confidence interval|probabilit\w+ "
                r"(range|distribution))",):
        for m in re.finditer(bad, t):
            ctx = t[max(0, m.start() - 120):m.end() + 40]
            assert re.search(r"\bnot\b|\bonly\b|\bno\b", ctx), ctx


def test_author_placeholders_are_kept_and_highlighted(master, supp):
    for doc, minimum in ((master, 8), (supp, 1)):
        n_text = doc.all_text().count("AUTHOR TO CONFIRM")
        styled = 0
        for r in doc.body.iter(f"{{{NS['w']}}}r"):
            rs = r.find("w:rPr/w:rStyle", NS)
            if rs is not None and rs.get(f"{{{NS['w']}}}val") == "Placeholder" and "AUTHOR TO CONFIRM" in doc.text(r):
                styled += 1
        assert n_text >= minimum and styled == n_text
    decl = MAN.joinpath("07_declarations.md").read_text(encoding="utf-8")
    assert master.all_text().count("AUTHOR TO CONFIRM") == decl.count("AUTHOR TO CONFIRM") + 1   # + title page


# ============================================================ PDF completeness
@pytest.mark.skipif(not HAVE_PDFTOOLS, reason="poppler tools not installed")
@pytest.mark.parametrize("which", ["master", "supp"])
def test_pdf_contains_the_docx_content(which, master, supp):
    doc, pdf = (master, MASTER_PDF) if which == "master" else (supp, SUPP_PDF)
    flat = norm(pdf_text(pdf))
    squeezed = flat.replace(" ", "")
    words = set(re.findall(r"[A-Za-zÀ-ž]{9,}", doc.all_text()))
    missing = sorted(w for w in words if w not in flat)
    assert not missing, missing[:20]
    for cap in doc.styled("TableCaption") + doc.styled("ImageCaption") + doc.styled("Heading1") + \
            doc.styled("Heading2"):
        assert cap[:60].replace(" ", "") in squeezed, cap[:60]
    if which == "master":
        for ref in doc.styled("Reference"):
            assert ref[:40].replace(" ", "") in squeezed, ref[:40]
        assert "Figure 4." in flat and "Table 6." in flat
    assert "??" not in flat and "Error!" not in flat


def test_build_script_consumes_the_current_architecture(builder):
    src = (ROOT / "scripts" / "10_build_docx.py").read_text(encoding="utf-8")
    assert "figures_final" not in src and "figure1.png" not in src and "equations/eq" not in src
    assert "MASTER_pandoc2" not in src
    md = builder.master_markdown()
    assert md.count('::: {.equation number=') == 8
    assert md.count("![**Figure") == 4 and md.count("Table: **Table") == 6
    assert "\\mathrm" not in md and "\\bar{" not in md                   # OMML-compatible notation


@pytest.mark.skipif(shutil.which("soffice") is None or not HAVE_PDFTOOLS, reason="LibreOffice not installed")
def test_committed_documents_match_a_fresh_build(builder):
    assert builder.check() == []
