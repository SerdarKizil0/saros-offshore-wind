"""
Assemble the submission package for Sustainable Energy Technologies and Assessments (SETA)
=========================================================================================
Builds the two package-specific documents and the package manifest from version-controlled
files. Nothing scientific is generated here; the manuscript, supplement and figures come from
scripts/10, 11 and 12.

  submission/SETA/highlights.md    -> submission/SETA/Highlights.docx
  submission/SETA/cover_letter.md  -> submission/SETA/Cover_letter_DRAFT.docx
  submission/SETA/MANIFEST.json    list of the files to upload, with SHA-256

Checks applied before writing (requirements confirmed from the SETA guide for authors; see
submission/SETA/README.md):
  * abstract of at most 250 words;
  * 3 to 5 highlights of at most 85 characters each, including spaces.
It also refuses any legacy file (2014-2024 CDS-based figures, pre-revision figures, archive).

`--zip` additionally writes submission/SETA/Saros_SETA_submission.zip (not versioned).
`--check` rebuilds the manifest in memory and compares it with the committed one.

Run from the repository root:  python scripts/13_build_submission_package.py [--zip | --check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "submission" / "SETA"
ABSTRACT_MAX_WORDS = 250
HIGHLIGHTS_MIN, HIGHLIGHTS_MAX, HIGHLIGHT_MAX_CHARS = 3, 5, 85
UPLOAD = [  # (role in the submission system, repository path)
    ("Manuscript (editable)", "manuscript/output/Saros_Offshore_Wind_Master.docx"),
    ("Manuscript (PDF for reference)", "manuscript/output/Saros_Offshore_Wind_Master.pdf"),
    ("Supplementary material (editable)", "manuscript/output/Saros_Supplementary_Material.docx"),
    ("Supplementary material (PDF)", "manuscript/output/Saros_Supplementary_Material.pdf"),
    ("Figure 1", "figures/revised/fig1_site_map.pdf"),
    ("Figure 2", "figures/revised/fig2_temporal_sensitivity.pdf"),
    ("Figure 3", "figures/revised/fig3_nodes_and_products.pdf"),
    ("Figure 4", "figures/revised/fig4_sensitivity_categories.pdf"),
    ("Highlights", "submission/SETA/Highlights.docx"),
    ("Cover letter (draft; author placeholders)", "submission/SETA/Cover_letter_DRAFT.docx"),
]
EXCLUDED = re.compile(r"Yield Figure|figures/F[^/]*$|figures_final/|manuscript/figure\d|results/archive|"
                      r"2014_2024_cds|wind_resource_interactive", re.I)
FIXED_ZIP_DATE = (2026, 11, 15, 0, 0, 0)


def abstract_words() -> int:
    t = (ROOT / "manuscript" / "00_abstract.md").read_text(encoding="utf-8")
    return len(t.split("## Abstract", 1)[1].split("**Keywords:**")[0].split())


def highlights() -> list[str]:
    return [ln[2:].strip() for ln in (PKG / "highlights.md").read_text(encoding="utf-8").splitlines()
            if ln.startswith("- ")]


def problems() -> list[str]:
    out = []
    n = abstract_words()
    if n > ABSTRACT_MAX_WORDS:
        out.append(f"abstract has {n} words (limit {ABSTRACT_MAX_WORDS})")
    hl = highlights()
    if not HIGHLIGHTS_MIN <= len(hl) <= HIGHLIGHTS_MAX:
        out.append(f"{len(hl)} highlights (3-5 required)")
    out += [f"highlight longer than {HIGHLIGHT_MAX_CHARS} characters: {h!r}" for h in hl if len(h) > HIGHLIGHT_MAX_CHARS]
    out += [f"legacy file in the package: {p}" for _, p in UPLOAD if EXCLUDED.search(p)]
    return out


def pandoc(src: Path, out: Path):
    subprocess.run(["pandoc", str(src), "-o", str(out)], check=True,
                   env={"SOURCE_DATE_EPOCH": "1794700800", "PATH": "/usr/bin:/bin:/usr/local/bin"})
    with zipfile.ZipFile(out) as z:                       # fixed timestamps: reproducible bytes
        parts = {n: z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(parts, key=lambda n: (n != "[Content_Types].xml", n)):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, parts[name])


def manifest() -> dict:
    files = []
    for role, rel in UPLOAD:
        p = ROOT / rel
        files.append({"role": role, "path": rel, "bytes": p.stat().st_size,
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return {"journal": "Sustainable Energy Technologies and Assessments (Elsevier, ISSN 2213-1388)",
            "abstract_words": abstract_words(), "highlights": highlights(), "files": files,
            "excluded_pattern": EXCLUDED.pattern}


def build(make_zip: bool = False) -> dict:
    found = problems()
    if found:
        raise SystemExit("submission package check failed:\n" + "\n".join(found))
    pandoc(PKG / "highlights.md", PKG / "Highlights.docx")
    pandoc(PKG / "cover_letter.md", PKG / "Cover_letter_DRAFT.docx")
    m = manifest()
    (PKG / "MANIFEST.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if make_zip:
        with zipfile.ZipFile(PKG / "Saros_SETA_submission.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for f in m["files"]:
                z.write(ROOT / f["path"], Path(f["path"]).name)
    return m


def check() -> list[str]:
    found = problems()
    committed = json.loads((PKG / "MANIFEST.json").read_text(encoding="utf-8"))
    current = manifest()
    if committed != current:
        found.append("MANIFEST.json differs from the current files; rerun scripts/13_build_submission_package.py")
    return found


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        f = check()
        print("\n".join(f) if f else "submission package up to date")
        sys.exit(1 if f else 0)
    m = build(a.zip)
    print(f"abstract {m['abstract_words']} words; {len(m['highlights'])} highlights; {len(m['files'])} files")
