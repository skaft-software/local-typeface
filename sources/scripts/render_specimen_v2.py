#!/usr/bin/env python3
"""Render a brand-led Local 0.52 specimen from the actual release fonts."""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "fonts"
BUILD = ROOT / "build/specimen-v2"
OUTPUT = ROOT / "specimens/Local-0.52-specimen-v2.png"

GROTESK_REGULAR = FONTS / "static/grotesk/LocalGrotesk-Regular.ttf"
GROTESK_BOLD = FONTS / "static/grotesk/LocalGrotesk-Bold.ttf"
GROTESK_VARIABLE = FONTS / "variable/LocalGrotesk[wght].ttf"
MONO_REGULAR = FONTS / "static/mono/LocalMono-Regular.ttf"
MONO_BOLD = FONTS / "static/mono/LocalMono-Bold.ttf"
MONO_VARIABLE = FONTS / "variable/LocalMono[wght].ttf"
MONO_NERD = FONTS / "nerd/LocalMonoNerdFontMono-Regular.ttf"

WIDTH = 2000
HEIGHT = 2740
MARGIN = 60
CONTENT_RIGHT = WIDTH - MARGIN

BG = "#F3EFE6"
PAPER_DARK = "#E9E2D6"
INK = "#121412"
MUTED = "#6D6B64"
RULE = "#CBC4B7"
CORAL = "#F45B45"
BLUE = "#1683A4"
GREEN = "#85C98E"
ORANGE = "#EFA44C"
PANEL = "#131513"
PANEL_RULE = "#343832"
PANEL_TEXT = "#EEECE5"


def face(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def variable_instance(path: Path, weight: int) -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    output = BUILD / f"{path.stem}-{weight}.ttf"
    source = TTFont(path)
    instance = instantiateVariableFont(
        source,
        {"wght": weight},
        inplace=False,
        optimize=True,
    )
    instance.save(output)
    return output


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> float:
    return draw.textlength(text, font=font)


def right_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font,
    fill: str,
) -> None:
    draw.text((x - text_width(draw, text, font), y), text, font=font, fill=fill)


def label(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    fill: str = MUTED,
) -> None:
    draw.text((x, y), text.upper(), font=face(GROTESK_BOLD, 18), fill=fill)


def rule(draw: ImageDraw.ImageDraw, y: int, width: int = 2) -> None:
    draw.line((MARGIN, y, CONTENT_RIGHT, y), fill=RULE, width=width)


def cut_corner_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    cut: int,
    fill: str,
) -> None:
    x1, y1, x2, y2 = box
    draw.polygon(
        (
            (x1 + cut, y1),
            (x2, y1),
            (x2, y2 - cut),
            (x2 - cut, y2),
            (x1, y2),
            (x1, y1 + cut),
        ),
        fill=fill,
    )


def main() -> None:
    grotesk_400 = variable_instance(GROTESK_VARIABLE, 400)
    grotesk_550 = variable_instance(GROTESK_VARIABLE, 550)
    grotesk_700 = variable_instance(GROTESK_VARIABLE, 700)
    mono_400 = variable_instance(MONO_VARIABLE, 400)
    mono_550 = variable_instance(MONO_VARIABLE, 550)
    mono_700 = variable_instance(MONO_VARIABLE, 700)

    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # Masthead
    draw.text(
        (MARGIN, 38),
        "LOCAL / TYPE SYSTEM",
        font=face(GROTESK_BOLD, 27),
        fill=CORAL,
    )
    draw.text(
        (MARGIN + 315, 45),
        "0.52",
        font=face(MONO_BOLD, 18),
        fill=CORAL,
    )
    right_text(
        draw,
        CONTENT_RIGHT,
        45,
        "SKAFT SOFTWARE · PUBLIC RELEASE",
        face(GROTESK_BOLD, 17),
        MUTED,
    )
    rule(draw, 92)

    # Hero: restrained enough to leave room for the actual letterforms.
    label(draw, MARGIN, 126, "Local Grotesk / Regular 400")
    draw.text(
        (MARGIN, 167),
        "Precision, with fingerprints.",
        font=face(GROTESK_REGULAR, 108),
        fill=INK,
    )
    draw.text(
        (MARGIN, 300),
        "Swiss rhythm. Open counters. Curves that arrive a little off-center—",
        font=face(GROTESK_REGULAR, 31),
        fill=BLUE,
    )
    draw.text(
        (MARGIN, 340),
        "enough to feel authored, never enough to interrupt the work.",
        font=face(GROTESK_REGULAR, 31),
        fill=BLUE,
    )

    # Signature anatomy: the missing proof in the first specimen.
    anatomy_top = 405
    anatomy_bottom = 850
    draw.rectangle(
        (MARGIN, anatomy_top, CONTENT_RIGHT, anatomy_bottom),
        fill=PAPER_DARK,
    )
    label(draw, MARGIN + 24, anatomy_top + 22, "The Local hand", CORAL)
    draw.text(
        (MARGIN + 230, anatomy_top + 20),
        "Six small decisions that give the system its voice.",
        font=face(GROTESK_REGULAR, 22),
        fill=MUTED,
    )

    details = (
        ("a", "LOWER\nGRAVITY"),
        ("e", "OPEN\nEXIT"),
        ("l", "QUIET\nFOOT"),
        ("r", "FORWARD\nCUT"),
        ("q", "DIRECTED\nTAIL"),
        ("0", "SLASHED\nZERO"),
    )
    inner_left = MARGIN + 22
    inner_right = CONTENT_RIGHT - 22
    column_width = (inner_right - inner_left) / len(details)
    for index, (glyph, note) in enumerate(details):
        x1 = round(inner_left + index * column_width)
        x2 = round(inner_left + (index + 1) * column_width)
        if index:
            draw.line(
                (x1, anatomy_top + 82, x1, anatomy_bottom - 24),
                fill=RULE,
                width=2,
            )
        glyph_font = face(
            MONO_REGULAR if glyph == "0" else GROTESK_REGULAR,
            190,
        )
        glyph_width = text_width(draw, glyph, glyph_font)
        draw.text(
            ((x1 + x2 - glyph_width) / 2, anatomy_top + 93),
            glyph,
            font=glyph_font,
            fill=INK,
        )
        note_font = face(MONO_BOLD, 17)
        note_lines = note.splitlines()
        note_y = anatomy_top + 340
        for line in note_lines:
            line_width = text_width(draw, line, note_font)
            draw.text(
                ((x1 + x2 - line_width) / 2, note_y),
                line,
                font=note_font,
                fill=BLUE if index % 2 == 0 else CORAL,
            )
            note_y += 23

    # Editorial proof and variable behavior share one disciplined grid.
    section_top = 900
    label(draw, MARGIN, section_top, "Grotesk / Text + Weight")
    split_x = 1260
    draw.line((split_x, section_top + 42, split_x, 1262), fill=RULE, width=2)
    draw.text(
        (MARGIN, section_top + 47),
        "Build things that\nfeel local.",
        font=face(GROTESK_BOLD, 73),
        fill=INK,
        spacing=3,
    )
    body = (
        "Local software should feel precise, readable, and unmistakably made.\n"
        "Tiny differences stay present without turning the interface into a performance."
    )
    draw.multiline_text(
        (MARGIN, section_top + 226),
        body,
        font=face(GROTESK_REGULAR, 25),
        fill=INK,
        spacing=10,
    )
    draw.text(
        (MARGIN, section_top + 326),
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        font=face(GROTESK_REGULAR, 22),
        fill=MUTED,
    )
    draw.text(
        (MARGIN, section_top + 363),
        "abcdefghijklmnopqrstuvwxyz  0123456789",
        font=face(GROTESK_REGULAR, 22),
        fill=MUTED,
    )

    label(draw, split_x + 34, section_top + 48, "Variable / wght")
    variable_rows = (
        ("400", grotesk_400),
        ("550", grotesk_550),
        ("700", grotesk_700),
    )
    variable_y = section_top + 104
    for weight, path in variable_rows:
        draw.text(
            (split_x + 34, variable_y + 17),
            weight,
            font=face(MONO_REGULAR, 16),
            fill=MUTED,
        )
        draw.text(
            (split_x + 112, variable_y),
            "Carefully made.",
            font=face(path, 43),
            fill=INK,
        )
        variable_y += 92
    rule(draw, 1300)

    # Explicit ambiguity proof instead of an unexplained glyph pile.
    label(draw, MARGIN, 1332, "Mono / Readability controls")
    groups = (
        ("I  l  1", "CAP I / LOWER L / ONE"),
        ("O  0  Ø", "CAP O / ZERO / SLASH"),
        ("b d p q", "DIRECTIONAL FORMS"),
        ("rn  m", "PAIR SEPARATION"),
        ("R  r", "LEG / SHOULDER"),
    )
    group_widths = (300, 330, 350, 300, 260)
    x = MARGIN
    for index, ((sample, explanation), width) in enumerate(
        zip(groups, group_widths)
    ):
        if index:
            draw.line((x, 1380, x, 1518), fill=RULE, width=2)
        draw.text(
            (x + 18, 1384),
            sample,
            font=face(MONO_BOLD, 46),
            fill=INK,
        )
        draw.text(
            (x + 18, 1462),
            explanation,
            font=face(MONO_REGULAR, 13),
            fill=MUTED,
        )
        x += width
    rule(draw, 1540)

    # A compact, dense terminal field with a real Nerd glyph column.
    label(draw, MARGIN, 1574, "Local Mono / Nerd Font Mono / 616 unit cell")
    panel = (MARGIN, 1622, CONTENT_RIGHT, 2248)
    cut_corner_panel(draw, panel, 18, PANEL)
    px1, py1, px2, py2 = panel
    draw.text(
        (px1 + 42, py1 + 34),
        "\uf120  local@host",
        font=face(MONO_NERD, 27),
        fill=PANEL_TEXT,
    )
    draw.text(
        (px1 + 310, py1 + 34),
        "~/skaft/local",
        font=face(MONO_REGULAR, 27),
        fill=MUTED,
    )
    right_text(
        draw,
        px2 - 38,
        py1 + 38,
        "LOCAL SESSION / 14 MS",
        face(MONO_BOLD, 15),
        GREEN,
    )
    draw.line(
        (px1 + 42, py1 + 82, px2 - 42, py1 + 82),
        fill=PANEL_RULE,
        width=2,
    )

    code_x = px1 + 42
    code_y = py1 + 122
    code_font = face(MONO_REGULAR, 31)
    draw.text(
        (code_x, code_y),
        "$ ygg run --model local",
        font=code_font,
        fill=BLUE,
    )
    draw.text(
        (code_x, code_y + 58),
        "[ok] tools ready  ·  context 61%",
        font=code_font,
        fill=GREEN,
    )
    draw.multiline_text(
        (code_x, code_y + 140),
        (
            "fn dispatch(task: Task) -> Result<()> {\n"
            "    tracing::info!(\"done: {status}\");\n"
            "    Ok(())\n"
            "}"
        ),
        font=code_font,
        fill=PANEL_TEXT,
        spacing=18,
    )

    nerd_x = 1420
    draw.line(
        (nerd_x - 34, py1 + 110, nerd_x - 34, py2 - 38),
        fill=PANEL_RULE,
        width=2,
    )
    draw.text(
        (nerd_x, py1 + 123),
        "NERD GLYPHS",
        font=face(MONO_BOLD, 16),
        fill=ORANGE,
    )
    nerd_symbols = (
        ("\uf09b", "GITHUB"),
        ("\ue725", "BRANCH"),
        ("\uf07b", "FOLDER"),
        ("\uf120", "TERMINAL"),
        ("\uf00c", "CHECK"),
    )
    symbol_y = py1 + 176
    for symbol, name in nerd_symbols:
        draw.text(
            (nerd_x, symbol_y),
            symbol,
            font=face(MONO_NERD, 40),
            fill=ORANGE,
        )
        draw.text(
            (nerd_x + 64, symbol_y + 10),
            name,
            font=face(MONO_REGULAR, 17),
            fill=PANEL_TEXT,
        )
        symbol_y += 72

    draw.line(
        (px1 + 42, py2 - 106, px2 - 42, py2 - 106),
        fill=PANEL_RULE,
        width=2,
    )
    draw.text(
        (px1 + 42, py2 - 76),
        "Literal operators:  ->  =>  !=  ==  <=  &&  ||  {}  []  <>",
        font=face(MONO_REGULAR, 26),
        fill=PANEL_TEXT,
    )

    # Mono variable proof finishes the card without another oversized block.
    label(draw, MARGIN, 2290, "Mono variable / wght 400–700")
    mono_rows = (
        ("400", mono_400),
        ("550", mono_550),
        ("700", mono_700),
    )
    mono_y = 2330
    for weight, path in mono_rows:
        draw.text(
            (MARGIN, mono_y + 13),
            weight,
            font=face(MONO_REGULAR, 15),
            fill=MUTED,
        )
        draw.text(
            (MARGIN + 92, mono_y),
            "dispatch(bdpq, Il1, O0Ø, Rr) -> Result<()>",
            font=face(path, 31),
            fill=INK,
        )
        mono_y += 72

    rule(draw, 2570)
    draw.text(
        (MARGIN, 2602),
        "LOCAL 0.52",
        font=face(GROTESK_BOLD, 18),
        fill=CORAL,
    )
    draw.text(
        (MARGIN + 145, 2603),
        "Shared metrics 1000 / −250 / 0   ·   Mono cell 616   ·   wght 400–700",
        font=face(GROTESK_REGULAR, 17),
        fill=MUTED,
    )
    right_text(
        draw,
        CONTENT_RIGHT,
        2603,
        "COPYRIGHT 2026 SKAFT SOFTWARE",
        face(GROTESK_BOLD, 16),
        MUTED,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
