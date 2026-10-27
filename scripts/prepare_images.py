"""Turn source screenshots (assets/img/src, not in git) into 16:10 WebP cards (assets/img).

Optional crop boxes (left, top, right, bottom in source pixels) focus on the map in a screenshot.
Usage: python scripts/prepare_images.py
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "assets" / "img" / "src", ROOT / "assets" / "img"
WIDTH, RATIO = 1000, 16 / 10
CROPS = {
    "signal": (143, 342, 908, 900),        # just the map panel of the Exeter Signal Atlas
    "coverage": (0, 175, 1119, 874),       # a 16:10 band through the middle of the coverage checker map
    "census": (0, 45, 840, 778),           # drop the GeoLibre layer button in the corner
    "greenspace": (640, 25, 1218, 520),    # the summer-greenness map only (source has two maps)
    "fallen_trees": (24, 22, 612, 534),    # the aerial photo without the app window around it
    "databricks": (400, 0, 1400, 900),     # the map of the results site, without the side panel
}


def card(img: Image.Image) -> Image.Image:
    """Centre-crop to 16:10, then resize to WIDTH."""
    w, h = img.size
    if w / h > RATIO:                       # too wide: trim the sides
        nw = int(h * RATIO)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:                                   # too tall: trim top and bottom
        nh = int(w / RATIO)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return img.resize((WIDTH, int(WIDTH / RATIO)), Image.LANCZOS)


for src in sorted(SRC.glob("*.png")):
    img = Image.open(src).convert("RGB")
    if src.stem in CROPS:
        img = img.crop(CROPS[src.stem])
    out = OUT / f"{src.stem}.webp"
    card(img).save(out, "WEBP", quality=82, method=6)
    print(f"{src.name:<18} {src.stat().st_size / 1e3:>6,.0f} kB -> {out.name} {out.stat().st_size / 1e3:>4,.0f} kB")
