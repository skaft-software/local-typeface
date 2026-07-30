#!/usr/bin/env fontforge
"""Build three Local 0.52 control intensities.

This is deliberately a control-glyph experiment, not a production release.
The full upstream character sets remain present so the controls can be read in
real words, but only the named Local control glyphs receive new construction.
"""

from __future__ import annotations

import math
from pathlib import Path

import fontforge


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "vendor/reference"
BUILD = ROOT / "build/control-0.52"

GROTESK_REFERENCE = (
    REFERENCE / "tex-gyre/tex-gyre/opentype/texgyreheros-regular.otf"
)
MONO_REFERENCE = (
    REFERENCE
    / "ibm-plex-mono/fonts/complete/woff2/IBMPlexMono-Regular.woff2"
)

MONO_CELL = 616
CURVED_LOWERCASE = "aegnoscbampq"
CURVED_CAPS = "O0R"

INTENSITIES = {
    "Subtle": {"gravity": 0.026, "drift": 8.0, "terminal": 6.0},
    "Recommended": {"gravity": 0.042, "drift": 14.0, "terminal": 10.0},
    "Strong": {"gravity": 0.060, "drift": 20.0, "terminal": 15.0},
}

# A small, authored phase change. It creates family resemblance without making
# repeated curves mechanically identical or adding noise to every point.
DRIFT_DIRECTIONS = {
    "a": -0.75,
    "e": 1.0,
    "g": -0.65,
    "n": 0.35,
    "o": -0.45,
    "s": 0.8,
    "c": 0.65,
    "b": -0.3,
    "m": 0.25,
    "p": 0.55,
    "q": -0.9,
    "O": 0.4,
    "zero": -0.55,
    "R": 0.25,
}


def contour_area_proxy(contour) -> float:
    xs = [point.x for point in contour]
    ys = [point.y for point in contour]
    if not xs or not ys:
        return 0.0
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def sculpt_curve(glyph, gravity: float, drift: float, band_top: float) -> None:
    """Add lower gravity and a delayed curve apex without edge jitter."""

    layer = glyph.foreground
    x_min, _, x_max, _ = glyph.boundingBox()
    center_x = (x_min + x_max) / 2.0
    if not layer:
        return

    outer_index = max(
        range(len(layer)),
        key=lambda index: contour_area_proxy(layer[index]),
    )
    direction = DRIFT_DIRECTIONS.get(
        glyph.glyphname,
        DRIFT_DIRECTIONS.get(chr(glyph.unicode), 0.0)
        if glyph.unicode >= 0
        else 0.0,
    )

    for index, contour in enumerate(layer):
        # The counter contracts gently while the outside expands. This adds
        # visual weight below the midline rather than merely making it wider.
        contour_gravity = gravity if index == outer_index else -gravity * 0.38
        for point in contour:
            normalized = max(0.0, min(1.0, point.y / band_top))
            lower_amount = 1.0 - normalized
            scale = 1.0 + contour_gravity * lower_amount
            apex_delay = (
                direction
                * drift
                * math.sin(math.pi * normalized)
            )
            point.x = center_x + (point.x - center_x) * scale + apex_delay
            if index != outer_index:
                # Raise the lower edge of counters. This is the restrained
                # OpenDyslexic cue: actual lower stroke mass, not a wide base.
                point.y += gravity * band_top * 0.72 * lower_amount

    glyph.foreground = layer
    glyph.round()
    glyph.correctDirection()


def move_nearest_point(
    glyph,
    target_x: float,
    target_y: float,
    delta_x: float,
    delta_y: float,
) -> None:
    """Move the unique nearest on-curve point, with an ambiguity guard."""

    layer = glyph.foreground
    candidates = []
    for contour in layer:
        for point in contour:
            if point.on_curve:
                distance = (point.x - target_x) ** 2 + (point.y - target_y) ** 2
                candidates.append((distance, point))
    candidates.sort(key=lambda item: item[0])
    if len(candidates) < 2 or candidates[0][0] == candidates[1][0]:
        raise RuntimeError(f"{glyph.glyphname}: ambiguous target point")
    candidates[0][1].x += delta_x
    candidates[0][1].y += delta_y
    glyph.foreground = layer
    glyph.round()


def add_grotesk_l_foot(glyph, amount: float) -> None:
    """Give lowercase l a quiet, readable exit instead of a bare bar."""

    x_min, _, x_max, y_max = glyph.boundingBox()
    original_width = glyph.width
    stem_weight = x_max - x_min
    glyph.clear()
    pen = glyph.glyphPen()
    left = round(x_min)
    right = round(x_max)
    reach = round(34 + amount * 2.2)
    height = round(18 + amount * 0.7)
    pen.moveTo((left, 0))
    pen.lineTo((right + reach, 0))
    pen.lineTo((right + reach - 5, height))
    pen.lineTo((right, height + 5))
    pen.lineTo((right, round(y_max)))
    pen.lineTo((left, round(y_max)))
    pen.closePath()
    del pen
    glyph.correctDirection()
    glyph.width = max(
        original_width + (56 if stem_weight > 110 else 56),
        right + reach + 42,
    )


def slant_descender(glyph, amount: float) -> None:
    """Make q unmistakably directional instead of a mirrored p."""

    layer = glyph.foreground
    for contour in layer:
        for point in contour:
            if point.y < 0:
                depth = min(1.0, -point.y / 220.0)
                point.x += amount * depth
    glyph.foreground = layer
    glyph.round()


def kick_r_leg(glyph, amount: float) -> None:
    """Delay the R leg, then let it move decisively to the right."""

    layer = glyph.foreground
    x_min, _, x_max, _ = glyph.boundingBox()
    center_x = (x_min + x_max) / 2.0
    for contour in layer:
        for point in contour:
            if point.x > center_x and point.y < 330:
                lower = max(0.0, min(1.0, (330 - point.y) / 330.0))
                point.x += amount * lower
    glyph.foreground = layer
    glyph.round()


def lift_right_foot(glyph, amount: float) -> None:
    """Apply the family terminal angle to an existing lowercase-l foot."""

    layer = glyph.foreground
    x_min, _, x_max, _ = glyph.boundingBox()
    cutoff = x_min + (x_max - x_min) * 0.62
    for contour in layer:
        for point in contour:
            if point.x > cutoff and point.y < 55:
                rightness = (point.x - cutoff) / max(1.0, x_max - cutoff)
                point.y += amount * rightness
    glyph.foreground = layer
    glyph.round()


def replace_zero_dot_with_slash(glyph, amount: float) -> None:
    """Use Atkinson-like orientation instead of Plex's centered zero dot."""

    layer = glyph.foreground
    width = glyph.width
    smallest = min(
        range(len(layer)),
        key=lambda index: contour_area_proxy(layer[index]),
    )
    del layer[smallest]
    base_layer = layer.dup()

    inset = amount * 0.55
    glyph.clear()
    pen = glyph.glyphPen()
    pen.moveTo((242 - inset * 0.25, 155))
    pen.lineTo((275 - inset * 0.25, 145))
    pen.lineTo((376 + inset * 0.25, 550))
    pen.lineTo((343 + inset * 0.25, 560))
    pen.closePath()
    del pen
    slash_layer = glyph.foreground
    glyph.foreground = base_layer + slash_layer
    glyph.width = width
    glyph.removeOverlap()
    glyph.correctDirection()


def open_mono_cell(font) -> None:
    for glyph in font.glyphs():
        if glyph.width != 600:
            continue
        glyph.transform((1, 0, 0, 1, 8, 0))
        glyph.width = MONO_CELL


def set_metadata(font, family: str, ps_family: str, style: str) -> None:
    font.familyname = f"{family} Control 052"
    font.fontname = f"{ps_family}Control052-{style}"
    font.fullname = f"{family} Control 0.52 {style}"
    font.weight = "Regular"
    font.version = "0.520"
    font.os2_vendor = "SKFT"
    font.comment = (
        "Local 0.52 control experiment: Swiss rhythm, restrained lower "
        "gravity, hyperlegible ambiguity forms, and authored curve tension."
    )


def apply_grotesk_controls(font, settings) -> None:
    for character in CURVED_LOWERCASE:
        sculpt_curve(
            font[character],
            settings["gravity"],
            settings["drift"],
            539,
        )
    for character in CURVED_CAPS:
        glyph = font["zero"] if character == "0" else font[character]
        sculpt_curve(
            glyph,
            settings["gravity"] * 0.72,
            settings["drift"] * 0.75,
            729,
        )

    # Apertures open, but the terminals retain the same rising-right family cut.
    move_nearest_point(
        font["e"], 513, 238,
        -settings["terminal"] * 1.35,
        settings["terminal"] * 0.45,
    )
    move_nearest_point(
        font["c"], 477, 405,
        -settings["terminal"] * 0.75,
        settings["terminal"] * 0.35,
    )
    move_nearest_point(
        font["r"], 321, 451,
        -settings["terminal"],
        settings["terminal"] * 0.55,
    )
    move_nearest_point(
        font["t"], 254, 0,
        -settings["terminal"] * 0.65,
        settings["terminal"] * 0.4,
    )
    add_grotesk_l_foot(font["l"], settings["terminal"])
    slant_descender(font["q"], settings["terminal"] * 2.0)
    kick_r_leg(font["R"], settings["terminal"] * 1.35)


def apply_mono_controls(font, settings) -> None:
    open_mono_cell(font)
    for character in CURVED_LOWERCASE:
        sculpt_curve(
            font[character],
            settings["gravity"] * 0.92,
            settings["drift"] * 0.82,
            528,
        )
    for character in CURVED_CAPS:
        glyph = font["zero"] if character == "0" else font[character]
        sculpt_curve(
            glyph,
            settings["gravity"] * 0.68,
            settings["drift"] * 0.66,
            698,
        )

    move_nearest_point(
        font["e"], 533, 242,
        -settings["terminal"] * 1.1,
        settings["terminal"] * 0.35,
    )
    move_nearest_point(
        font["c"], 516, 392,
        -settings["terminal"] * 0.7,
        settings["terminal"] * 0.3,
    )
    move_nearest_point(
        font["r"], 559, 422,
        -settings["terminal"] * 0.7,
        settings["terminal"] * 0.5,
    )
    slant_descender(font["q"], settings["terminal"] * 2.4)
    kick_r_leg(font["R"], settings["terminal"] * 1.5)
    lift_right_foot(font["l"], settings["terminal"] * 0.85)
    replace_zero_dot_with_slash(font["zero"], settings["terminal"])


def build_family(
    reference: Path,
    family: str,
    ps_family: str,
    apply_controls,
) -> None:
    for style, settings in INTENSITIES.items():
        font = fontforge.open(str(reference))
        set_metadata(font, family, ps_family, style)
        apply_controls(font, settings)
        BUILD.mkdir(parents=True, exist_ok=True)
        sfd_path = BUILD / f"{ps_family}Control052-{style}.sfd"
        ttf_path = BUILD / f"{ps_family}Control052-{style}.ttf"
        font.save(str(sfd_path))
        font.generate(str(ttf_path), flags=("opentype", "PfEd-comments"))
        font.close()
        print(ttf_path)


def main() -> None:
    build_family(
        GROTESK_REFERENCE,
        "Local Grotesk",
        "LocalGrotesk",
        apply_grotesk_controls,
    )
    build_family(
        MONO_REFERENCE,
        "Local Mono",
        "LocalMono",
        apply_mono_controls,
    )


if __name__ == "__main__":
    main()
