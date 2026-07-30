#!/usr/bin/env python3
"""Postprocess Local 0.52 statics and build compatible wght variables."""

from __future__ import annotations

import math
from pathlib import Path

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    SourceDescriptor,
)
from fontTools.ttLib import TTFont
from fontTools.varLib import build as build_variable


ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "build/0.52"
DESIGNSPACES = ROOT / "build/designspace"

FAMILIES = {
    "grotesk": {
        "family": "Local Grotesk",
        "ps_family": "LocalGrotesk",
        "fixed": False,
        "embolden_x": 26,
        "embolden_y": 12,
        "license": (
            "Local Grotesk is a modified version of TeX Gyre Heros, "
            "distributed under the GUST Font License."
        ),
    },
    "mono": {
        "family": "Local Mono",
        "ps_family": "LocalMono",
        "fixed": True,
        "embolden_x": 22,
        "embolden_y": 11,
        "license": (
            "Local Mono is a modified version of IBM Plex Mono, "
            "distributed under the SIL Open Font License 1.1."
        ),
    },
}


def set_name(font: TTFont, name_id: int, value: str) -> None:
    font["name"].setName(value, name_id, 3, 1, 0x409)
    font["name"].setName(value, name_id, 1, 0, 0)


def normalize_metadata(
    font: TTFont,
    family: str,
    ps_family: str,
    style: str,
    weight: int,
    fixed: bool,
    license_text: str,
) -> None:
    full = f"{family} {style}"
    postscript = f"{ps_family}-{style}"
    set_name(
        font,
        0,
        (
            "Local modifications copyright 2026 Skaft Software. "
            f"{license_text}"
        ),
    )
    set_name(font, 1, family)
    set_name(font, 2, style)
    set_name(font, 3, f"0.520;SKFT;{postscript}")
    set_name(font, 4, full)
    set_name(font, 5, "Version 0.520")
    set_name(font, 6, postscript)
    set_name(font, 13, license_text)
    set_name(font, 16, family)
    set_name(font, 17, style)

    font["OS/2"].usWeightClass = weight
    font["OS/2"].version = max(4, font["OS/2"].version)
    font["OS/2"].achVendID = "SKFT"
    font["OS/2"].fsType = 0
    font["OS/2"].sTypoAscender = 1000
    font["OS/2"].sTypoDescender = -250
    font["OS/2"].sTypoLineGap = 0
    font["OS/2"].usWinAscent = 1200
    font["OS/2"].usWinDescent = 400
    font["OS/2"].fsSelection |= 1 << 7
    if style == "Bold":
        font["OS/2"].fsSelection |= 1 << 5
        font["OS/2"].fsSelection &= ~(1 << 6)
        font["head"].macStyle |= 1
    else:
        font["OS/2"].fsSelection &= ~(1 << 5)
        font["OS/2"].fsSelection |= 1 << 6
        font["head"].macStyle &= ~1
    font["hhea"].ascent = 1000
    font["hhea"].descent = -250
    font["hhea"].lineGap = 0
    font["post"].isFixedPitch = 1 if fixed else 0
    font["head"].modified = font["head"].created


def contour_area(coordinates, start: int, end: int) -> float:
    area = 0.0
    for index in range(start, end + 1):
        next_index = start if index == end else index + 1
        x1, y1 = coordinates[index]
        x2, y2 = coordinates[next_index]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def embolden_simple_glyph(glyph, glyf, dx: int, dy: int, fixed: bool) -> None:
    coordinates, end_points, _ = glyph.getCoordinates(glyf)
    if not coordinates or not end_points:
        return

    starts = [0, *[end + 1 for end in end_points[:-1]]]
    areas = [
        contour_area(coordinates, start, end)
        for start, end in zip(starts, end_points)
    ]
    outer_index = max(range(len(areas)), key=lambda index: abs(areas[index]))
    outer_sign = 1 if areas[outer_index] >= 0 else -1

    for contour_index, (start, end) in enumerate(zip(starts, end_points)):
        xs = [coordinates[index][0] for index in range(start, end + 1)]
        ys = [coordinates[index][1] for index in range(start, end + 1)]
        center_x = (min(xs) + max(xs)) / 2.0
        center_y = (min(ys) + max(ys)) / 2.0
        sign = 1 if areas[contour_index] >= 0 else -1
        direction = 1 if sign == outer_sign else -1

        for index in range(start, end + 1):
            x, y = coordinates[index]
            x_direction = -1 if x < center_x else 1 if x > center_x else 0
            y_direction = -1 if y < center_y else 1 if y > center_y else 0
            coordinates[index] = (
                round(x + direction * dx * x_direction),
                round(y + direction * dy * y_direction),
            )

    if not fixed:
        coordinates.translate((dx, 0))
    glyph.coordinates = coordinates
    glyph.recalcBounds(glyf)


def make_compatible_bold(
    regular_path: Path,
    output_path: Path,
    config: dict,
) -> None:
    font = TTFont(regular_path, recalcTimestamp=False)
    glyf = font["glyf"]
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            continue
        embolden_simple_glyph(
            glyph,
            glyf,
            config["embolden_x"],
            config["embolden_y"],
            config["fixed"],
        )

    if not config["fixed"]:
        for glyph_name, (advance, lsb) in list(font["hmtx"].metrics.items()):
            if advance > 0:
                font["hmtx"].metrics[glyph_name] = (
                    advance + config["embolden_x"] * 2,
                    lsb,
                )

    normalize_metadata(
        font,
        config["family"],
        config["ps_family"],
        "Bold",
        700,
        config["fixed"],
        config["license"],
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(output_path, reorderTables=False)


def write_designspace(
    regular: Path,
    bold: Path,
    path: Path,
    config: dict,
) -> None:
    document = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name = "Weight"
    axis.tag = "wght"
    axis.minimum = 400
    axis.default = 400
    axis.maximum = 700
    document.addAxis(axis)

    for source_path, style, weight in (
        (regular, "Regular", 400),
        (bold, "Bold", 700),
    ):
        source = SourceDescriptor()
        source.path = str(source_path.resolve())
        source.name = f"{config['ps_family']} {style}"
        source.familyName = config["family"]
        source.styleName = style
        source.location = {"Weight": weight}
        source.copyLib = style == "Regular"
        source.copyInfo = style == "Regular"
        source.copyFeatures = style == "Regular"
        document.addSource(source)

        instance = InstanceDescriptor()
        instance.familyName = config["family"]
        instance.styleName = style
        instance.postScriptFontName = f"{config['ps_family']}-{style}"
        instance.location = {"Weight": weight}
        document.addInstance(instance)

    path.parent.mkdir(parents=True, exist_ok=True)
    document.write(path)


def build_family(key: str, config: dict) -> None:
    family_dir = DIST / key
    static_dir = family_dir / "static"
    regular = static_dir / f"{config['ps_family']}-Regular.ttf"
    bold = static_dir / f"{config['ps_family']}-Bold.ttf"

    static_fonts = (
        (regular, "Regular", 400),
        (bold, "Bold", 700),
        (static_dir / f"{config['ps_family']}-Regular.otf", "Regular", 400),
        (static_dir / f"{config['ps_family']}-Bold.otf", "Bold", 700),
    )
    for path, style, weight in static_fonts:
        font = TTFont(path, recalcTimestamp=False)
        normalize_metadata(
            font,
            config["family"],
            config["ps_family"],
            style,
            weight,
            config["fixed"],
            config["license"],
        )
        font.save(path, reorderTables=False)

    compatible_dir = family_dir / "variable-masters"
    compatible_bold = compatible_dir / f"{config['ps_family']}-Bold.ttf"
    make_compatible_bold(regular, compatible_bold, config)

    designspace = DESIGNSPACES / f"{config['ps_family']}.designspace"
    write_designspace(regular, compatible_bold, designspace, config)
    variable, _, _ = build_variable(designspace)
    normalize_metadata(
        variable,
        config["family"],
        config["ps_family"],
        "Regular",
        400,
        config["fixed"],
        config["license"],
    )

    variable_path = family_dir / f"{config['ps_family']}[wght].ttf"
    variable.save(variable_path, reorderTables=False)
    web_dir = family_dir / "web"
    web_dir.mkdir(parents=True, exist_ok=True)
    variable.flavor = "woff2"
    web_path = web_dir / f"{config['ps_family']}[wght].woff2"
    variable.save(web_path, reorderTables=False)
    print(variable_path)
    print(web_path)


def main() -> None:
    for key, config in FAMILIES.items():
        build_family(key, config)


if __name__ == "__main__":
    main()
