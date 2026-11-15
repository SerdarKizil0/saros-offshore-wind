"""
Build (or check) the publication figure set
===========================================
Runs the four figure generators and writes their vector PDF/SVG and 600 dpi
PNG files to figures/revised/:

  Figure 1  scripts/fig1_site_map.py               fig1_site_map
  Figure 2  scripts/fig2_temporal_sensitivity.py   fig2_temporal_sensitivity
  Figure 3  scripts/fig3_nodes_and_products.py     fig3_nodes_and_products
  Figure 4  scripts/fig4_sensitivity_categories.py fig4_sensitivity_categories

Captions are part of the manuscript (manuscript/src/09_figures.md) and are
rendered by scripts/11_build_manuscript_sections.py.

--check renders every figure into a temporary directory and compares it with
the committed files by content, not by compressed bytes:

  * SVG: identical markup once the <metadata> block (Matplotlib version) is
    removed and embedded raster images are replaced by their decoded pixels;
  * PNG and embedded rasters: identical decoded pixels (RGBA arrays), so a
    different zlib build cannot make an unchanged figure look stale;
  * PDF: same page size, embedded TrueType fonts, no Type 3 fonts.

Run from the repository root:
  python scripts/12_build_figures.py            # regenerate figures/revised/
  python scripts/12_build_figures.py --check    # verify the committed files
"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "figures" / "revised"
FIGURES = [  # number, stem, generator
    (1, "fig1_site_map", "fig1_site_map.py"),
    (2, "fig2_temporal_sensitivity", "fig2_temporal_sensitivity.py"),
    (3, "fig3_nodes_and_products", "fig3_nodes_and_products.py"),
    (4, "fig4_sensitivity_categories", "fig4_sensitivity_categories.py"),
]
EXTS = ("pdf", "svg", "png")
DATA_IMAGE = re.compile(r'(xlink:href|href)="data:image/png;base64,([^"]+)"')


def load(generator: str):
    name = "fig_" + generator.removesuffix(".py")
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / generator)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _pixels(data: bytes) -> np.ndarray:
    with Image.open(io.BytesIO(data)) as im:
        return np.asarray(im.convert("RGBA"))


def png_pixels(path: Path) -> np.ndarray:
    return _pixels(Path(path).read_bytes())


def svg_signature(path: Path) -> tuple[str, list[np.ndarray]]:
    """SVG markup without metadata, with embedded PNG data replaced by placeholders, and the decoded images."""
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"<metadata>.*?</metadata>", "<metadata/>", text, flags=re.S)
    images = [_pixels(base64.b64decode(m.group(2))) for m in DATA_IMAGE.finditer(text)]
    text = DATA_IMAGE.sub(lambda m: f'{m.group(1)}="data:image/png;base64,IMAGE"', text)
    return text, images


def pdf_facts(path: Path) -> dict:
    pdf = Path(path).read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    return {"mediabox": tuple(round(float(v), 2) for v in box.groups()),
            "truetype": b"/FontFile2" in pdf, "type3": b"/Type3" in pdf,
            "images": len(re.findall(rb"/Subtype\s*/Image", pdf))}


def compare(committed: Path, fresh: Path, stem: str) -> list[str]:
    """Content differences between committed and freshly rendered files of one figure."""
    out = []
    for ext in EXTS:
        if not (committed / f"{stem}.{ext}").exists():
            out.append(f"{stem}.{ext} is missing")
    if out:
        return out
    a_txt, a_img = svg_signature(committed / f"{stem}.svg")
    b_txt, b_img = svg_signature(fresh / f"{stem}.svg")
    if a_txt != b_txt:
        out.append(f"{stem}.svg differs from the generator output")
    if len(a_img) != len(b_img) or any(x.shape != y.shape or not np.array_equal(x, y)
                                       for x, y in zip(a_img, b_img)):
        out.append(f"{stem}.svg embedded raster differs")
    pa, pb = png_pixels(committed / f"{stem}.png"), png_pixels(fresh / f"{stem}.png")
    if pa.shape != pb.shape or not np.array_equal(pa, pb):
        out.append(f"{stem}.png pixels differ from the generator output")
    if pdf_facts(committed / f"{stem}.pdf") != pdf_facts(fresh / f"{stem}.pdf"):
        out.append(f"{stem}.pdf page size, fonts or image count differ")
    return out


def build(out_dir: Path = FIG_DIR) -> dict[str, dict]:
    return {stem: load(gen).main(out_dir) for _, stem, gen in FIGURES}


def check() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        build(Path(tmp))
        return [p for _, stem, _ in FIGURES for p in compare(FIG_DIR, Path(tmp), stem)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--check", action="store_true", help="compare committed figures with the generators")
    args = parser.parse_args()
    if args.check:
        problems = check()
        print("\n".join(problems) if problems else "figures up to date")
        sys.exit(1 if problems else 0)
    build()
