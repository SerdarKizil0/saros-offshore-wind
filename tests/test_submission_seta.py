"""
Submission package for Sustainable Energy Technologies and Assessments (pre-submission corrections).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "submission" / "SETA"


def _load():
    spec = importlib.util.spec_from_file_location("build13", ROOT / "scripts" / "13_build_submission_package.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["build13"] = m
    spec.loader.exec_module(m)
    return m


def test_journal_limits_abstract_and_highlights():
    m = _load()
    assert m.abstract_words() <= 250
    hl = m.highlights()
    assert 3 <= len(hl) <= 5 and all(len(h) <= 85 for h in hl)
    assert not [h for h in hl if re.search(r"\d", h.replace("ERA5", ""))]    # no hand-typed result numbers
    assert m.problems() == []


def test_manifest_is_current_and_complete():
    m = _load()
    assert m.check() == []
    man = json.loads((PKG / "MANIFEST.json").read_text(encoding="utf-8"))
    paths = [f["path"] for f in man["files"]]
    assert paths[:4] == ["manuscript/output/Saros_Offshore_Wind_Master.docx",
                         "manuscript/output/Saros_Offshore_Wind_Master.pdf",
                         "manuscript/output/Saros_Supplementary_Material.docx",
                         "manuscript/output/Saros_Supplementary_Material.pdf"]
    assert [p for p in paths if p.startswith("figures/")] == [
        f"figures/revised/{s}.pdf" for s in ("fig1_site_map", "fig2_temporal_sensitivity",
                                             "fig3_nodes_and_products", "fig4_sensitivity_categories")]
    assert all((ROOT / p).exists() for p in paths)


def test_legacy_material_is_excluded():
    man = json.loads((PKG / "MANIFEST.json").read_text(encoding="utf-8"))
    for f in man["files"]:
        assert not re.search(r"Yield Figure|figures/F|figures_final|manuscript/figure\d|archive|2014_2024|cds", f["path"],
                             re.I), f["path"]
    for name in ("Gulf of Saros Yield Figure.pdf",):
        assert not list(ROOT.rglob(name)) or all(".git" in str(p) for p in ROOT.rglob(name))
    readme = (PKG / "README.md").read_text(encoding="utf-8")
    assert "Gulf of Saros Yield Figure.pdf" in readme and "must not be uploaded" in readme


def test_cover_letter_and_highlights_are_built_and_placeholders_kept():
    assert (PKG / "Highlights.docx").exists() and (PKG / "Cover_letter_DRAFT.docx").exists()
    letter = (PKG / "cover_letter.md").read_text(encoding="utf-8")
    assert letter.count("[AUTHOR TO CONFIRM") >= 4
    assert not re.search(r"\bfirst\b", letter)
    assert "does not repeat such an assessment" in letter


def test_area_is_reported_consistently():
    for name in ("01_introduction.md", "02_study_area.md", "09_figures.md", "tables.md"):
        t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
        assert "172.6 km²" in t, name
    for p in list((ROOT / "manuscript").glob("*.md")) + list(PKG.glob("*.md")):
        assert "172.53" not in p.read_text(encoding="utf-8"), p
