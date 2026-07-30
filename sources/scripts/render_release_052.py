#!/usr/bin/env python3
"""Render the final Local 0.52 release specimen."""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "build/0.52"
BUILD = ROOT / "build/instances"
PROOFS = ROOT / "build/proofs"
OUT = PROOFS / "Local-0.52-release-specimen.png"

LABEL_FONT = "/System/Library/Fonts/Helvetica.ttc"
BG = "#f3efe6"
INK = "#161616"
MUTED = "#77736c"
RULE = "#d0c9bc"
ACCENT = "#ef5b43"
BLUE = "#2b86a6"
GREEN = "#80c985"
ORANGE = "#efaa58"
TERMINAL = "#171817"
TERMINAL_TEXT = "#efede7"


def font(path: Path | str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def instance(variable_path: Path, weight: int) -> Path:
    output = BUILD / f"{variable_path.stem}-{weight}.ttf"
    BUILD.mkdir(parents=True, exist_ok=True)
    variable = TTFont(variable_path)
    static = instantiateVariableFont(
        variable,
        {"wght": weight},
        inplace=False,
        optimize=True,
    )
    static.save(output)
    return output


def main() -> None:
    grotesk_regular_path = (
        DIST / "grotesk/static/LocalGrotesk-Regular.ttf"
    )
    grotesk_bold_path = DIST / "grotesk/static/LocalGrotesk-Bold.ttf"
    mono_regular_path = DIST / "mono/static/LocalMono-Regular.ttf"
    mono_bold_path = DIST / "mono/static/LocalMono-Bold.ttf"
    grotesk_variable = DIST / "grotesk/LocalGrotesk[wght].ttf"
    mono_variable = DIST / "mono/LocalMono[wght].ttf"

    grotesk_400 = instance(grotesk_variable, 400)
    grotesk_550 = instance(grotesk_variable, 550)
    grotesk_700 = instance(grotesk_variable, 700)
    mono_400 = instance(mono_variable, 400)
    mono_550 = instance(mono_variable, 550)
    mono_700 = instance(mono_variable, 700)

    image = Image.new("RGB", (2000, 2480), BG)
    draw = ImageDraw.Draw(image)
    label = font(LABEL_FONT, 21)
    small_label = font(LABEL_FONT, 17)
    title = font(LABEL_FONT, 34)

    draw.text(
        (52, 38),
        "LOCAL 0.52 / RELEASE FAMILY",
        font=title,
        fill=ACCENT,
    )
    draw.text(
        (1375, 45),
        "GROTESK + MONO + VARIABLE + NERD",
        font=label,
        fill=MUTED,
    )
    draw.line((52, 104, 1948, 104), fill=RULE, width=2)

    draw.text((52, 144), "LOCAL GROTESK / REGULAR", font=label, fill=MUTED)
    draw.text(
        (52, 192),
        "Precision with fingerprints.",
        font=font(grotesk_regular_path, 126),
        fill=INK,
    )
    draw.text(
        (52, 346),
        "Swiss spacing discipline, open counters, lower gravity, and curves "
        "that never land in quite the mathematical place.",
        font=font(grotesk_regular_path, 34),
        fill=BLUE,
    )
    draw.line((52, 416, 1948, 416), fill=RULE, width=2)

    draw.text(
        (52, 452),
        "Hamburgefontsiv  a e g l r  b d p q  I l 1  O 0  R",
        font=font(grotesk_regular_path, 76),
        fill=INK,
    )
    draw.text(
        (52, 560),
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        font=font(grotesk_regular_path, 48),
        fill=INK,
    )
    draw.text(
        (52, 630),
        "abcdefghijklmnopqrstuvwxyz  0123456789",
        font=font(grotesk_regular_path, 48),
        fill=INK,
    )
    draw.text(
        (52, 710),
        "Local software should feel precise, readable, and unmistakably "
        "made. The curves carry tiny differences without interrupting the "
        "work.",
        font=font(grotesk_regular_path, 31),
        fill=INK,
    )
    draw.text(
        (52, 790),
        "LOCAL GROTESK / BOLD",
        font=label,
        fill=MUTED,
    )
    draw.text(
        (52, 830),
        "Build things that feel local.",
        font=font(grotesk_bold_path, 78),
        fill=INK,
    )
    draw.line((52, 944, 1948, 944), fill=RULE, width=2)

    draw.text((52, 976), "VARIABLE WEIGHT / 400–700", font=label, fill=MUTED)
    variable_rows = (
        ("400", grotesk_400),
        ("550", grotesk_550),
        ("700", grotesk_700),
    )
    y = 1020
    for weight, path in variable_rows:
        draw.text((52, y + 20), weight, font=small_label, fill=MUTED)
        draw.text(
            (145, y),
            "Local systems, carefully made.",
            font=font(path, 54),
            fill=INK,
        )
        y += 80
    draw.line((52, 1270, 1948, 1270), fill=RULE, width=2)

    draw.text((52, 1304), "LOCAL MONO / 616 UNIT CELL", font=label, fill=MUTED)
    terminal_box = (52, 1350, 1948, 2090)
    draw.rounded_rectangle(terminal_box, radius=22, fill=TERMINAL)
    draw.text(
        (96, 1392),
        "local@host  ~/skaft",
        font=font(mono_regular_path, 38),
        fill=TERMINAL_TEXT,
    )
    draw.text(
        (96, 1460),
        "$ ygg run --model local",
        font=font(mono_regular_path, 36),
        fill=BLUE,
    )
    draw.text(
        (96, 1528),
        "[ok] tools ready  ·  14 ms",
        font=font(mono_regular_path, 36),
        fill=GREEN,
    )
    code = (
        "fn dispatch(task: Task) -> Result<()> {\n"
        "    tracing::info!(\"done: {status}\");\n"
        "    Ok(())\n"
        "}"
    )
    draw.multiline_text(
        (96, 1612),
        code,
        font=font(mono_regular_path, 34),
        fill=TERMINAL_TEXT,
        spacing=20,
    )
    draw.text(
        (96, 1908),
        "I l 1   O Ø 0   b d p q   rn m   R r   {} [] <>",
        font=font(mono_bold_path, 45),
        fill=ORANGE,
    )
    draw.text(
        (96, 1990),
        "Literal operators:  ->  =>  !=  ==  <=  &&  ||",
        font=font(mono_regular_path, 34),
        fill=TERMINAL_TEXT,
    )

    draw.text(
        (52, 2130),
        "MONO VARIABLE WEIGHT / 400  550  700",
        font=label,
        fill=MUTED,
    )
    mono_rows = (
        ("400", mono_400),
        ("550", mono_550),
        ("700", mono_700),
    )
    y = 2170
    for weight, path in mono_rows:
        draw.text((52, y + 10), weight, font=small_label, fill=MUTED)
        draw.text(
            (145, y),
            "dispatch(bdpq, Il1, O0, Rr) -> Result<()>",
            font=font(path, 36),
            fill=INK,
        )
        y += 62

    draw.line((52, 2374, 1948, 2374), fill=RULE, width=2)
    draw.text(
        (52, 2404),
        "Shared metrics 1000 / −250 / 0  ·  Mono cell 616  ·  "
        "wght 400–700  ·  Nerd Font statics preserve Local outlines",
        font=small_label,
        fill=MUTED,
    )

    PROOFS.mkdir(parents=True, exist_ok=True)
    image.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
