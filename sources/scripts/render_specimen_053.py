#!/usr/bin/env python3
"""Render the human-authored Local 0.53 specimen."""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "fonts"
BUILD = ROOT / "build/specimen-0.53"
OUTPUT = ROOT / "specimens/Local-0.53-specimen.png"

GROTESK_REGULAR = FONTS / "static/grotesk/LocalGrotesk-Regular.ttf"
GROTESK_BOLD = FONTS / "static/grotesk/LocalGrotesk-Bold.ttf"
GROTESK_VARIABLE = FONTS / "variable/LocalGrotesk[wght].ttf"
MONO_REGULAR = FONTS / "static/mono/LocalMono-Regular.ttf"
MONO_BOLD = FONTS / "static/mono/LocalMono-Bold.ttf"
MONO_VARIABLE = FONTS / "variable/LocalMono[wght].ttf"
MONO_NERD = FONTS / "nerd/LocalMonoNerdFontMono-Regular.ttf"

WIDTH = 2000
HEIGHT = 2820
MARGIN = 64
RIGHT = WIDTH - MARGIN

BG = "#F3EFE6"
PAPER_DARK = "#E8E0D3"
INK = "#111310"
MUTED = "#6F6C65"
RULE = "#C9C1B4"
CORAL = "#F25742"
BLUE = "#1483A5"
GREEN = "#83CB8D"
ORANGE = "#EFA34A"
PANEL = "#131513"
PANEL_RULE = "#383B35"
PANEL_TEXT = "#EFECE5"
UI_BG = "#202124"
UI_MUTED = "#AEB0B6"


def face(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def variable_instance(path: Path, weight: int) -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    output = BUILD / f"{path.stem}-{weight}.ttf"
    variable = TTFont(path)
    instance = instantiateVariableFont(
        variable,
        {"wght": weight},
        inplace=False,
        optimize=True,
    )
    instance.save(output)
    return output


def width(draw: ImageDraw.ImageDraw, text: str, font) -> float:
    return draw.textlength(text, font=font)


def right_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font,
    fill: str,
) -> None:
    draw.text((x - width(draw, text, font), y), text, font=font, fill=fill)


def label(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    fill: str = MUTED,
) -> None:
    draw.text((x, y), text.upper(), font=face(GROTESK_BOLD, 17), fill=fill)


def section_number(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    number: str,
    title: str,
) -> None:
    draw.text((x, y), number, font=face(MONO_BOLD, 18), fill=CORAL)
    draw.line((x + 48, y + 11, x + 110, y + 11), fill=CORAL, width=2)
    draw.text(
        (x + 128, y - 1),
        title.upper(),
        font=face(GROTESK_BOLD, 17),
        fill=MUTED,
    )


def rotated_text(
    image: Image.Image,
    text: str,
    font,
    fill: str,
    position: tuple[int, int],
    angle: float,
) -> None:
    box = font.getbbox(text)
    layer = Image.new(
        "RGBA",
        (box[2] - box[0] + 24, box[3] - box[1] + 24),
        (0, 0, 0, 0),
    )
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.text((12 - box[0], 12 - box[1]), text, font=font, fill=fill)
    rotated = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    image.paste(rotated, position, rotated)


def cut_panel(
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


def ui_sample() -> Image.Image:
    panel = Image.new("RGB", (1100, 350), UI_BG)
    draw = ImageDraw.Draw(panel)
    draw.text(
        (34, 30),
        "NEW WORKSPACE TASK",
        font=face(GROTESK_REGULAR, 19),
        fill="#858891",
    )
    draw.text(
        (34, 93),
        "What should we work on?",
        font=face(GROTESK_REGULAR, 26),
        fill="#F1F1F2",
    )
    draw.text(
        (34, 154),
        "Describe the change you want to make. Add files or images when they",
        font=face(GROTESK_REGULAR, 23),
        fill=UI_MUTED,
    )
    draw.text(
        (34, 190),
        "help.",
        font=face(GROTESK_REGULAR, 23),
        fill=UI_MUTED,
    )
    draw.line((34, 258, 1066, 258), fill="#33353A", width=2)
    draw.text(
        (34, 285),
        "14 px / regular / shared forward curve phase",
        font=face(MONO_REGULAR, 15),
        fill="#858891",
    )
    return panel.rotate(
        -0.55,
        expand=True,
        resample=Image.Resampling.BICUBIC,
        fillcolor=BG,
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

    # Masthead: intentionally more like a working proof than a product card.
    draw.text(
        (MARGIN, 38),
        "LOCAL",
        font=face(GROTESK_BOLD, 28),
        fill=CORAL,
    )
    draw.text(
        (MARGIN + 115, 44),
        "0.53 / CONSISTENCY PROOF",
        font=face(MONO_BOLD, 17),
        fill=CORAL,
    )
    right_text(
        draw,
        RIGHT,
        44,
        "A SKAFT SOFTWARE TYPE FAMILY · DRAWN FOR LOCAL WORK",
        face(GROTESK_BOLD, 16),
        MUTED,
    )
    draw.line((MARGIN, 90, 1210, 90), fill=RULE, width=2)
    draw.line((1230, 91, RIGHT, 91), fill=RULE, width=1)
    rotated_text(
        image,
        "PROOF 03 / KEEP THE HABITS",
        face(MONO_BOLD, 13),
        CORAL,
        (1710, 111),
        1.25,
    )

    # Hero copy.
    label(draw, MARGIN, 132, "Local Grotesk / Regular")
    draw.multiline_text(
        (MARGIN, 168),
        "The system\nhas a hand.",
        font=face(GROTESK_REGULAR, 112),
        fill=INK,
        spacing=-10,
    )
    draw.text(
        (970, 205),
        "Not random.\nNot sterile.",
        font=face(GROTESK_BOLD, 55),
        fill=INK,
        spacing=5,
    )
    draw.text(
        (970, 355),
        "One person’s habits, repeated carefully\n"
        "enough to become a type family.",
        font=face(GROTESK_REGULAR, 29),
        fill=BLUE,
        spacing=12,
    )
    draw.line((955, 183, 955, 470), fill=RULE, width=2)

    # 01 / The hand. Staggered glyphs and proofreader-like callouts.
    hand_top = 520
    hand_bottom = 1115
    draw.rectangle((MARGIN, hand_top, RIGHT, hand_bottom), fill=PAPER_DARK)
    section_number(draw, MARGIN + 24, hand_top + 25, "01", "The repeated habits")
    draw.text(
        (MARGIN + 390, hand_top + 25),
        "same direction, different jobs",
        font=face(GROTESK_REGULAR, 20),
        fill=MUTED,
    )

    glyphs = (
        (116, 648, "a", GROTESK_REGULAR, 250),
        (390, 617, "e", GROTESK_REGULAR, 230),
        (640, 660, "l", GROTESK_REGULAR, 245),
        (850, 620, "r", GROTESK_REGULAR, 230),
        (1070, 640, "q", GROTESK_REGULAR, 255),
        (1410, 610, "0", MONO_REGULAR, 245),
    )
    for x, y, glyph, path, size in glyphs:
        draw.text((x, y), glyph, font=face(path, size), fill=INK)

    callouts = (
        ((210, 870), (155, 996), "01  WEIGHT SITS LOW"),
        ((505, 810), (430, 1040), "02  EXITS RISE TOGETHER"),
        ((715, 858), (740, 990), "03  THE FOOT WHISPERS"),
        ((935, 790), (965, 1042), "04  ROLLS FORWARD"),
        ((1198, 890), (1190, 997), "05  THE TAIL CHOOSES"),
        ((1520, 805), (1510, 1045), "06  MONO / NO GUESSING"),
    )
    for start, end, note in callouts:
        draw.line((*start, *end), fill=CORAL, width=2)
        draw.ellipse(
            (start[0] - 4, start[1] - 4, start[0] + 4, start[1] + 4),
            fill=CORAL,
        )
        draw.text(
            (end[0], end[1] + 6),
            note,
            font=face(MONO_BOLD, 13),
            fill=CORAL,
        )

    # 02 / Small-size proof using a real UI sample, slightly handled.
    section_number(draw, MARGIN, 1164, "02", "Where it actually works")
    sample = ui_sample()
    image.paste(sample, (MARGIN - 8, 1210))
    draw.line((82, 1207, 122, 1207), fill=CORAL, width=3)
    draw.line((80, 1207, 80, 1247), fill=CORAL, width=3)
    draw.line((1160, 1546, 1200, 1546), fill=CORAL, width=3)
    draw.line((1200, 1506, 1200, 1546), fill=CORAL, width=3)

    draw.text(
        (1280, 1226),
        "A calmer gray.",
        font=face(GROTESK_BOLD, 47),
        fill=INK,
    )
    draw.multiline_text(
        (1280, 1300),
        (
            "The fingerprints now recur by\n"
            "construction class. At 14–20 px,\n"
            "the texture stays even while the\n"
            "a, e, l, r, q and 0 stay Local."
        ),
        font=face(GROTESK_REGULAR, 25),
        fill=INK,
        spacing=12,
    )
    rotated_text(
        image,
        "THIS IS THE REAL TEST →",
        face(MONO_BOLD, 15),
        BLUE,
        (1370, 1487),
        -1.4,
    )

    # 03 / Terminal proof: inset and annotated rather than full-bleed SaaS.
    section_number(draw, MARGIN, 1615, "03", "Mono keeps the stronger cues")
    rotated_text(
        image,
        "FIXED 616 / LITERAL OPERATORS",
        face(MONO_BOLD, 14),
        ORANGE,
        (80, 1835),
        90,
    )
    draw.multiline_text(
        (115, 1692),
        "Code needs\nfewer maybes.",
        font=face(GROTESK_BOLD, 42),
        fill=INK,
        spacing=3,
    )
    draw.text(
        (115, 1818),
        "Il1\nO0Ø\nbdpq\nrn m\nRr",
        font=face(MONO_BOLD, 32),
        fill=INK,
        spacing=12,
    )

    panel = (520, 1682, RIGHT, 2240)
    cut_panel(draw, panel, 17, PANEL)
    px1, py1, px2, py2 = panel
    draw.text(
        (px1 + 38, py1 + 28),
        "\uf120  local@host",
        font=face(MONO_NERD, 24),
        fill=PANEL_TEXT,
    )
    draw.text(
        (px1 + 290, py1 + 28),
        "~/skaft/local",
        font=face(MONO_REGULAR, 24),
        fill=MUTED,
    )
    right_text(
        draw,
        px2 - 34,
        py1 + 32,
        "LOCAL / 0.53 / 14 MS",
        face(MONO_BOLD, 14),
        GREEN,
    )
    draw.line(
        (px1 + 38, py1 + 72, px2 - 38, py1 + 72),
        fill=PANEL_RULE,
        width=2,
    )
    code_font = face(MONO_REGULAR, 28)
    draw.text(
        (px1 + 38, py1 + 111),
        "$ ygg run --model local",
        font=code_font,
        fill=BLUE,
    )
    draw.text(
        (px1 + 38, py1 + 164),
        "[ok] tools ready  ·  context 61%",
        font=code_font,
        fill=GREEN,
    )
    draw.multiline_text(
        (px1 + 38, py1 + 240),
        (
            "fn dispatch(task: Task) -> Result<()> {\n"
            "    tracing::info!(\"done: {status}\");\n"
            "    Ok(())\n"
            "}"
        ),
        font=code_font,
        fill=PANEL_TEXT,
        spacing=15,
    )
    draw.line(
        (px1 + 38, py2 - 82, px2 - 38, py2 - 82),
        fill=PANEL_RULE,
        width=2,
    )
    draw.text(
        (px1 + 38, py2 - 58),
        "->  =>  !=  ==  <=  &&  ||  {}  []  <>",
        font=face(MONO_REGULAR, 24),
        fill=ORANGE,
    )

    # 04 / Weight and rhythm. Offset labels keep the proof from feeling auto-laid-out.
    section_number(draw, MARGIN, 2290, "04", "One skeleton, three pressures")
    weights = (
        ("400", grotesk_400, mono_400, 0),
        ("550", grotesk_550, mono_550, 8),
        ("700", grotesk_700, mono_700, -4),
    )
    y = 2344
    for weight, grotesk, mono, offset in weights:
        draw.text(
            (MARGIN + offset, y + 13),
            weight,
            font=face(MONO_BOLD, 15),
            fill=CORAL,
        )
        draw.text(
            (MARGIN + 92 + offset, y),
            "Human rhythm, carefully repeated.",
            font=face(grotesk, 37),
            fill=INK,
        )
        draw.text(
            (1190 - offset, y + 5),
            "Il1 O0Ø bdpq Rr",
            font=face(mono, 28),
            fill=INK,
        )
        y += 88

    draw.line((MARGIN, 2650, 1170, 2650), fill=RULE, width=2)
    draw.line((1190, 2651, RIGHT, 2651), fill=RULE, width=1)
    draw.text(
        (MARGIN, 2684),
        "LOCAL 0.53",
        font=face(GROTESK_BOLD, 18),
        fill=CORAL,
    )
    draw.text(
        (MARGIN + 150, 2685),
        "Shared habits, not shared perfection.",
        font=face(GROTESK_REGULAR, 18),
        fill=MUTED,
    )
    right_text(
        draw,
        RIGHT,
        2685,
        "1000 / −250 / 0  ·  MONO 616  ·  WGHT 400–700",
        face(MONO_REGULAR, 14),
        MUTED,
    )
    right_text(
        draw,
        RIGHT,
        2734,
        "COPYRIGHT 2026 SKAFT SOFTWARE",
        face(GROTESK_BOLD, 15),
        MUTED,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
