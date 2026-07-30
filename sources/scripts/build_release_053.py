#!/usr/bin/env fontforge
"""Build the Local 0.53 consistency-pass Regular and Bold masters."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import fontforge


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from build_control_053 import (  # noqa: E402
    INTENSITIES,
    apply_grotesk_controls,
    apply_mono_controls,
)


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "vendor/reference"
DIST = ROOT / "build/derived/0.53"
SOURCES = ROOT / "build/derived-sources/0.53"
SETTINGS = INTENSITIES["Recommended"]

FAMILIES = {
    "grotesk": {
        "family": "Local Grotesk",
        "ps_family": "LocalGrotesk",
        "fixed": False,
        "references": {
            "Regular": REFERENCE
            / "tex-gyre/tex-gyre/opentype/texgyreheros-regular.otf",
            "Bold": REFERENCE
            / "tex-gyre/tex-gyre/opentype/texgyreheros-bold.otf",
        },
        "lineage": (
            "Derived from TeX Gyre Heros 2.004 under the GUST Font License."
        ),
    },
    "mono": {
        "family": "Local Mono",
        "ps_family": "LocalMono",
        "fixed": True,
        "references": {
            "Regular": REFERENCE
            / "ibm-plex-mono/fonts/complete/woff2/"
            "IBMPlexMono-Regular.woff2",
            "Bold": REFERENCE
            / "ibm-plex-mono/fonts/complete/woff2/"
            "IBMPlexMono-Bold.woff2",
        },
        "lineage": (
            "Derived from IBM Plex Mono 2.5.0 under the SIL Open Font "
            "License 1.1."
        ),
    },
}

WEIGHTS = {"Regular": 400, "Bold": 700}
CONTROL_NAMES = {
    "a",
    "e",
    "g",
    "h",
    "l",
    "r",
    "t",
    "u",
    "n",
    "o",
    "s",
    "c",
    "b",
    "d",
    "p",
    "q",
    "I",
    "one",
    "O",
    "zero",
    "R",
    "m",
}
CONSTRUCTION_CLASSES = (
    ("BCDGJOPQSU", 1.8),
    ("fkvwxyz", 0.7),
)


def add_authored_construction_grammar(font, bold: bool) -> None:
    """Repeat a few human habits instead of assigning every glyph a wobble."""

    weight_scale = 1.15 if bold else 1.0
    for characters, class_bias in CONSTRUCTION_CLASSES:
        bias = class_bias * weight_scale
        for character in characters:
            glyph = font[ord(character)]
            if glyph.glyphname in CONTROL_NAMES:
                continue
            layer = glyph.foreground
            if not layer:
                continue
            _, y_min, _, y_max = glyph.boundingBox()
            height = y_max - y_min
            if height <= 0:
                continue
            for contour in layer:
                for point in contour:
                    normalized = max(
                        0.0,
                        min(1.0, (point.y - y_min) / height),
                    )
                    point.x += bias * math.sin(math.pi * normalized)
            glyph.foreground = layer
            glyph.round()


def set_metadata(
    font,
    family: str,
    ps_family: str,
    style: str,
    weight: int,
    lineage: str,
    fixed: bool,
) -> None:
    font.familyname = family
    font.fontname = f"{ps_family}-{style}"
    font.fullname = f"{family} {style}"
    font.weight = style
    font.version = "0.530"
    font.copyright = (
        "Local modifications copyright 2026 Skaft Software. "
        f"{lineage}"
    )
    font.comment = (
        "Local 0.53. Shared curve phase, related terminal angles, restrained "
        "lower gravity, and calm UI text color."
    )
    font.os2_vendor = "SKFT"
    font.os2_weight = weight
    font.os2_width = 5
    font.os2_fstype = 0
    font.ascent = 800
    font.descent = 200
    if fixed:
        font.os2_panose = (2, 11, 6, 9, 2, 2, 2, 2, 2, 4)


def finish_outlines(font) -> None:
    for glyph in font.glyphs():
        if not glyph.isWorthOutputting():
            continue
        if glyph.selfIntersects():
            glyph.removeOverlap()
        glyph.round()
        glyph.correctDirection()
        glyph.addExtrema("all")
        glyph.round()
        glyph.addExtrema("all")


def draw_rectangle(pen, x_min, y_min, x_max, y_max) -> None:
    pen.moveTo((x_min, y_min))
    pen.lineTo((x_max, y_min))
    pen.lineTo((x_max, y_max))
    pen.lineTo((x_min, y_max))
    pen.closePath()


def rebuild_diagonal_quadrants(font) -> None:
    """Replace two inherited self-intersecting terminal block glyphs."""

    patterns = {
        "uni259A": (
            (8, 301, 307, 950),
            (309, -350, 608, 300),
        ),
        "uni259E": (
            (309, 301, 608, 950),
            (8, -350, 307, 300),
        ),
    }
    for glyph_name, rectangles in patterns.items():
        glyph = font[glyph_name]
        glyph.clear()
        pen = glyph.glyphPen()
        for rectangle in rectangles:
            draw_rectangle(pen, *rectangle)
        del pen
        glyph.width = 616
        glyph.correctDirection()


def build_master(key: str, config: dict, style: str, reference: Path) -> None:
    font = fontforge.open(str(reference))
    weight = WEIGHTS[style]
    set_metadata(
        font,
        config["family"],
        config["ps_family"],
        style,
        weight,
        config["lineage"],
        config["fixed"],
    )
    if key == "grotesk":
        apply_grotesk_controls(font, SETTINGS)
    else:
        apply_mono_controls(font, SETTINGS)
        rebuild_diagonal_quadrants(font)
    add_authored_construction_grammar(font, bold=style == "Bold")
    finish_outlines(font)

    family_dist = DIST / key
    static_dir = family_dist / "static"
    source_dir = SOURCES / key
    static_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)

    stem = f"{config['ps_family']}-{style}"
    sfd_path = source_dir / f"{stem}.sfd"
    ttf_path = static_dir / f"{stem}.ttf"
    otf_path = static_dir / f"{stem}.otf"
    font.save(str(sfd_path))
    font.generate(str(ttf_path), flags=("opentype", "PfEd-comments"))
    font.generate(str(otf_path), flags=("opentype", "PfEd-comments"))
    font.close()
    print(sfd_path)
    print(ttf_path)
    print(otf_path)


def main() -> None:
    for key, config in FAMILIES.items():
        for style, reference in config["references"].items():
            build_master(key, config, style, reference)


if __name__ == "__main__":
    main()
