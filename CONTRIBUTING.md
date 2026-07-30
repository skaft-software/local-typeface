# Contributing

Local is developed in public, but changes to letterforms need to preserve the
family’s reading texture and shared system metrics.

Before proposing an outline change:

1. Open the relevant SFD master in `sources/fontforge`.
2. Keep Local Mono’s printable ASCII widths at exactly 616 units.
3. Keep both families on the shared `1000 / -250 / 0` line metrics.
4. Include a proof showing the changed glyph in words, paragraphs, code, and
   its ambiguity group.
5. Run `make build` and the available validation checks.

Please do not submit transformations based on proprietary font binaries.
Any new source material must have compatible redistribution terms and must be
documented in `NOTICE.md`.

