# Local 0.53 — consistency grammar

Local 0.53 keeps the 0.52 skeleton and replaces arbitrary per-glyph
irregularity with a small set of repeatable human habits.

## Construction rules

1. **Forward curve phase**
   Rounded lowercase, bowls, and shoulders arrive slightly late in the same
   forward direction. Differences now belong to construction classes rather
   than a glyph-name hash.

2. **Related terminal cuts**
   The open exits of `e`, `c`, `r`, and `t` share one rising-right angle
   family. Reach varies with the available space; direction does not.

3. **Restrained lower gravity**
   Curved forms retain more visual mass below the midpoint, but the production
   setting is reduced from 0.042 to 0.038 so UI text stays calm at 14–20 px.

4. **Quieter Grotesk signatures**
   The Grotesk `l` keeps its readable foot with less reach. The Grotesk `q`
   tail remains directional without becoming a display gesture.

5. **Stronger Mono differentiation**
   Local Mono retains the slashed zero, fixed 616-unit cell, firmer `q` tail,
   and stronger ambiguity cues needed in code and terminals.

## Preserved invariants

- Family names remain `Local Grotesk` and `Local Mono`.
- Static styles remain Regular 400 and Bold 700.
- Variable `wght` remains 400–700.
- Shared line metrics remain `1000 / -250 / 0`.
- Local Mono printable ASCII remains exactly 616 units wide.
- Programming operators remain literal; no decorative ligatures are added.
- Nerd Font patching preserves every Local Mono core outline and metric.

## Intent

Consistency does not mean removing the fingerprints. It means that Local looks
as though one person drew every glyph with the same habits.
