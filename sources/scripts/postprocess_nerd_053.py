#!/usr/bin/env python3
"""Restore Local Mono 0.53 core outlines after Nerd Font icon patching."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "build/0.53/mono"


def set_name(font: TTFont, name_id: int, value: str) -> None:
    font["name"].setName(value, name_id, 3, 1, 0x409)
    font["name"].setName(value, name_id, 1, 0, 0)


def process(style: str) -> Path:
    source_path = DIST / "static" / f"LocalMono-{style}.ttf"
    nerd_path = DIST / "nerd" / f"LocalMonoNerdFontMono-{style}.ttf"
    source = TTFont(source_path, recalcTimestamp=False)
    nerd = TTFont(nerd_path, recalcTimestamp=False)

    for glyph_name in source.getGlyphOrder():
        if glyph_name not in nerd["glyf"]:
            raise RuntimeError(f"Nerd patch dropped {glyph_name}")
        nerd["glyf"][glyph_name] = deepcopy(source["glyf"][glyph_name])
        nerd["hmtx"][glyph_name] = source["hmtx"][glyph_name]

    for tag in ("GSUB", "GPOS", "GDEF"):
        if tag in nerd:
            del nerd[tag]
    for tag in ("prep", "gasp", "cvt ", "fpgm"):
        if tag in source:
            nerd[tag] = deepcopy(source[tag])

    for attribute in ("ascent", "descent", "lineGap"):
        setattr(nerd["hhea"], attribute, getattr(source["hhea"], attribute))
    for attribute in (
        "sTypoAscender",
        "sTypoDescender",
        "sTypoLineGap",
        "usWinAscent",
        "usWinDescent",
        "usWeightClass",
        "fsSelection",
        "fsType",
        "achVendID",
    ):
        setattr(nerd["OS/2"], attribute, getattr(source["OS/2"], attribute))

    family = "LocalMono Nerd Font Mono"
    full = f"{family} {style}"
    postscript = f"LocalMonoNerdFontMono-{style}"
    set_name(
        nerd,
        0,
        (
            "Local modifications copyright 2026 Skaft Software. "
            "Local Mono is distributed under SIL OFL 1.1. Added Nerd Font "
            "glyphs retain their respective upstream licenses."
        ),
    )
    set_name(nerd, 1, family)
    set_name(nerd, 2, style)
    set_name(nerd, 3, f"0.530;SKFT;{postscript}")
    set_name(nerd, 4, full)
    set_name(nerd, 5, "Version 0.530")
    set_name(nerd, 6, postscript)
    set_name(
        nerd,
        13,
        (
            "Local Mono is distributed under SIL OFL 1.1. Added Nerd Font "
            "glyphs retain their respective upstream licenses."
        ),
    )
    set_name(nerd, 16, family)
    set_name(nerd, 17, style)
    nerd["post"].isFixedPitch = 1
    nerd["head"].modified = nerd["head"].created
    nerd.save(nerd_path, reorderTables=False)
    return nerd_path


for font_style in ("Regular", "Bold"):
    print(process(font_style))
