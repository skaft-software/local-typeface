#!/usr/bin/env python3
"""Create a deterministic archive from the public Local 0.53 repository."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "Local-Type-System-0.53"
ARCHIVE = ROOT / "build/release" / f"{PACKAGE}.zip"
ZIP_TIMESTAMP = (2026, 7, 29, 0, 0, 0)
INCLUDE = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "NOTICE.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "Makefile",
    ROOT / "requirements-dev.txt",
    ROOT / "SHA256SUMS.txt",
    ROOT / "LICENSES",
    ROOT / "fonts",
    ROOT / "sources",
    ROOT / "specimens",
    ROOT / "web",
)


def files(include_checksum: bool = True) -> list[Path]:
    selected: list[Path] = []
    for path in INCLUDE:
        if path.is_file():
            selected.append(path)
        elif path.is_dir():
            selected.extend(item for item in path.rglob("*") if item.is_file())
        else:
            raise FileNotFoundError(path)
    return sorted(
        path
        for path in selected
        if (include_checksum or path.name != "SHA256SUMS.txt")
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )


def checksums() -> None:
    lines = []
    for path in files(include_checksum=False):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    (ROOT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")


def main() -> None:
    checksums()
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(
        ARCHIVE,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as output:
        for path in files():
            relative = Path(PACKAGE) / path.relative_to(ROOT)
            info = zipfile.ZipInfo(relative.as_posix(), ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())
    print(ARCHIVE)
    print(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
