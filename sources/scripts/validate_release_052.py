#!/usr/bin/env python3
"""Validate the installable Local 0.52 release artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "fonts"
CONTROL_GLYPHS = ("a", "e", "o", "q", "l", "R", "zero")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def name(font: TTFont, name_id: int) -> str | None:
    for record in font["name"].names:
        if (
            record.nameID == name_id
            and record.platformID == 3
            and record.langID == 0x409
        ):
            return record.toUnicode()
    return None


def glyph_signature(font: TTFont, glyph_name: str) -> tuple:
    glyph = font["glyf"][glyph_name]
    if glyph.isComposite():
        return (
            "composite",
            tuple(
                (
                    component.glyphName,
                    component.x,
                    component.y,
                    component.flags,
                )
                for component in glyph.components
            ),
        )
    coordinates, end_points, flags = glyph.getCoordinates(font["glyf"])
    return (
        "simple",
        tuple(map(tuple, coordinates)),
        tuple(end_points),
        tuple(flags),
    )


def mono_widths(font: TTFont) -> set[int]:
    cmap = font.getBestCmap()
    return {
        font["hmtx"][glyph_name][0]
        for codepoint, glyph_name in cmap.items()
        if 0x20 <= codepoint <= 0x7E
    }


def run(command: list[str], label: str) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(
        result.returncode == 0,
        f"{label}: {result.stderr.strip() or result.stdout.strip()}",
    )


def check_metadata(
    font: TTFont,
    family: str,
    style: str,
    fixed: bool,
) -> None:
    require(name(font, 16) == family, f"{family} {style}: family name")
    require(name(font, 17) == style, f"{family} {style}: style name")
    require(name(font, 5) == "Version 0.520", f"{family}: version")
    require("Geist" not in "\n".join(
        record.toUnicode()
        for record in font["name"].names
        if record.nameID in (0, 1, 4, 13, 16)
    ), f"{family}: Geist lineage leaked")
    require(font["hhea"].ascent == 1000, f"{family}: hhea ascent")
    require(font["hhea"].descent == -250, f"{family}: hhea descent")
    require(font["hhea"].lineGap == 0, f"{family}: hhea line gap")
    require(
        font["post"].isFixedPitch == (1 if fixed else 0),
        f"{family}: fixed pitch flag",
    )


def check_family(key: str, family: str, ps_family: str, fixed: bool) -> None:
    static_dir = DIST / "static" / key
    for style, weight in (("Regular", 400), ("Bold", 700)):
        for extension in ("ttf", "otf"):
            path = static_dir / f"{ps_family}-{style}.{extension}"
            require(path.is_file(), f"missing {path}")
            font = TTFont(path)
            check_metadata(font, family, style, fixed)
            require(
                font["OS/2"].usWeightClass == weight,
                f"{path.name}: weight class",
            )
            if fixed:
                require(mono_widths(font) == {616}, f"{path.name}: widths")
            run(
                [sys.executable, "-m", "ots", str(path)],
                f"OTS {path.name}",
            )

    variable_path = DIST / "variable" / f"{ps_family}[wght].ttf"
    variable = TTFont(variable_path)
    axis = variable["fvar"].axes[0]
    require(
        (axis.axisTag, axis.minValue, axis.defaultValue, axis.maxValue)
        == ("wght", 400, 400, 700),
        f"{ps_family}: variable axis",
    )
    require(
        {"fvar", "gvar", "HVAR"}.issubset(variable.keys()),
        f"{ps_family}: variable tables",
    )
    check_metadata(variable, family, "Regular", fixed)

    at_regular = instantiateVariableFont(
        variable,
        {"wght": 400},
        inplace=False,
        optimize=True,
    )
    at_bold = instantiateVariableFont(
        variable,
        {"wght": 700},
        inplace=False,
        optimize=True,
    )
    changed = [
        glyph
        for glyph in CONTROL_GLYPHS
        if glyph_signature(at_regular, glyph) != glyph_signature(at_bold, glyph)
    ]
    require(
        len(changed) >= 6,
        f"{ps_family}: weight axis does not change enough controls: {changed}",
    )
    if fixed:
        require(mono_widths(variable) == {616}, f"{ps_family}: variable widths")
        require(mono_widths(at_bold) == {616}, f"{ps_family}: bold widths")

    run(
        [sys.executable, "-m", "ots", str(variable_path)],
        f"OTS {variable_path.name}",
    )
    for weight in (400, 550, 700):
        run(
            [
                "hb-shape",
                str(variable_path),
                "Local bdpq Il1 O0 -> != {status}",
                f"--variations=wght={weight}",
            ],
            f"HarfBuzz {ps_family}@{weight}",
        )

    web_path = DIST / "web" / f"{ps_family}[wght].woff2"
    web = TTFont(web_path)
    require("fvar" in web and "gvar" in web, f"{ps_family}: WOFF2 variable")


def check_nerd() -> None:
    for style in ("Regular", "Bold"):
        source_path = DIST / "static/mono" / f"LocalMono-{style}.ttf"
        nerd_path = DIST / "nerd" / f"LocalMonoNerdFontMono-{style}.ttf"
        source = TTFont(source_path)
        nerd = TTFont(nerd_path)
        require(
            len(nerd.getGlyphOrder()) > 10_000,
            f"{nerd_path.name}: icon coverage",
        )
        require(mono_widths(nerd) == {616}, f"{nerd_path.name}: widths")
        for glyph_name in source.getGlyphOrder():
            require(
                glyph_signature(source, glyph_name)
                == glyph_signature(nerd, glyph_name),
                f"{nerd_path.name}: changed core {glyph_name}",
            )
            require(
                source["hmtx"][glyph_name] == nerd["hmtx"][glyph_name],
                f"{nerd_path.name}: changed metric {glyph_name}",
            )
        run(
            [sys.executable, "-m", "ots", str(nerd_path)],
            f"OTS {nerd_path.name}",
        )


def main() -> None:
    check_family("grotesk", "Local Grotesk", "LocalGrotesk", False)
    check_family("mono", "Local Mono", "LocalMono", True)
    check_nerd()
    print("PASS  Local 0.52 statics, variables, webfonts, and Nerd Fonts")
    print("PASS  shared 1000/-250/0 line metrics")
    print("PASS  Mono ASCII cell width 616")
    print("PASS  wght 400-700 changes approved control glyphs")
    print("PASS  Nerd patch preserves every Local Mono core outline and metric")


if __name__ == "__main__":
    main()
