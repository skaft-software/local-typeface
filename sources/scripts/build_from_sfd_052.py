#!/usr/bin/env fontforge
"""Rebuild Local 0.52 static fonts from the checked-in SFD masters."""

from pathlib import Path

import fontforge


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build/0.52"

FAMILIES = {
    "grotesk": "LocalGrotesk",
    "mono": "LocalMono",
}


def main() -> None:
    for family, postscript_family in FAMILIES.items():
        source_dir = ROOT / "sources/fontforge" / family
        output_dir = BUILD / family / "static"
        output_dir.mkdir(parents=True, exist_ok=True)
        for style in ("Regular", "Bold"):
            stem = f"{postscript_family}-{style}"
            source = source_dir / f"{stem}.sfd"
            font = fontforge.open(str(source))
            font.generate(
                str(output_dir / f"{stem}.ttf"),
                flags=("opentype", "PfEd-comments"),
            )
            font.generate(
                str(output_dir / f"{stem}.otf"),
                flags=("opentype", "PfEd-comments"),
            )
            font.close()
            print(output_dir / f"{stem}.ttf")
            print(output_dir / f"{stem}.otf")


if __name__ == "__main__":
    main()

