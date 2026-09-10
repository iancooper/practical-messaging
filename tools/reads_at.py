#!/usr/bin/env python3
"""What every label actually reads at, in the room, on a 16:9 slide.

    python3 tools/reads_at.py                    # every family, worst figure each
    python3 tools/reads_at.py --all              # every figure
    python3 tools/reads_at.py bpmn_hotel paper_flow
    python3 tools/reads_at.py --floor 14         # a different bar

**Why this exists.** `lint_figures.py` measures labels against *shapes*: it catches a
name running out of its box. It says nothing about whether a room can read the box.
The deck's legibility rule lives in `REDEVELOPMENT-PLAN.md` §8 items 9 and 10, and it
has two halves that are easy to apply by eye and easy to get wrong:

  1. **x-height, not point size.** Plex Sans and Plex Mono are 0.516em against Caveat's
     0.400, so **13pt of Plex reads as 17pt of Caveat**. A survey that ranks families by
     the number in `size=` names BPMN as the worst offender when it is the only family
     that was already at the floor. Everything here is quoted in **Caveat-equivalent
     points**, which is the scale the 18pt floor is written in.

  2. **Aspect, not width.** A 16:9 slide leaves about **2.2 : 1** of usable area. A
     figure wider than that is fitted by width, and its labels read at
     `size x 890 / w`. **Anything squarer is fitted by HEIGHT**, its effective width is
     `2.2 x h`, and the width it was drawn at stops mattering entirely.

So the number that counts is

    reads_at = caveat_equivalent_size  x  890 / max(w, 2.2 x h)

and 890 is simply where that comes out at 18 for a figure already wider than 2.2:1.

**⚑ This is why "compacted to 890" is not the same as "reads at 18".** The 2026-09-07
sweep targeted width alone, and width alone is only half the rule. Run this before
claiming a family is done.
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import X_HEIGHT, HAND, PLAIN                        # noqa: E402

FAMILIES = ("eip_figures", "coupling_grids", "if_later", "queues_streams",
            "integration_styles", "app_shapes", "conversations", "bpmn_hotel",
            "bpmn_shopping", "paper_flow", "flow_reactive", "asyncapi_figures")

# The usable area of a 16:9 slide once the title and the margins are off it. Wider
# than this is fitted by width; squarer is fitted by height. Plan §8 item 10.
SLIDE_ASPECT = 2.2

# The canvas width at which an 18pt label reads at 18 real points, given the above.
REFERENCE_W = 890

FLOOR = 18.0        # Caveat points -- the deck's body floor, plan §8 item 12


def _face(d, n):
    if n["kind"] == "note":
        return n.get("font") or d.font
    return d.font


def measure(d):
    """(effective width, fitted-by, [(reads_at, label), ...]) for one built figure.

    `d` must already have been through `_legible()`, which both serialisers do -- it is
    called here as well because it is idempotent and a figure measured before the floor
    has run is measured at the size the author typed rather than the size that ships.
    """
    d._legible()
    by_width = d.w / d.h >= SLIDE_ASPECT
    eff = d.w if by_width else SLIDE_ASPECT * d.h
    out = []
    for n in d.groups + d.nodes:
        if not n.get("label"):
            continue
        face = _face(d, n)
        # X_HEIGHT covers the two faces the deck sets labels in; Plex Mono shares Plex
        # Sans's x-height exactly, so an unknown face defaults to that rather than to
        # Caveat's -- guessing the hand face would flatter the number.
        caveat = n.get("size", 14) * X_HEIGHT.get(face, X_HEIGHT[PLAIN]) / X_HEIGHT[HAND]
        out.append((caveat * REFERENCE_W / eff, str(n["label"]).split("\n")[0]))
    out.sort()
    return eff, ("width" if by_width else "HEIGHT"), out


def main(argv):
    show_all = "--all" in argv
    floor = FLOOR
    if "--floor" in argv:
        floor = float(argv[argv.index("--floor") + 1])
    fams = [a for a in argv if not a.startswith("--") and a in FAMILIES] or FAMILIES

    total = under = 0
    print(f"{'figure':<36} {'canvas':>11} {'asp':>5} {'fit':>6} {'worst':>8}  label")
    for f in fams:
        module = importlib.import_module(f)
        print(f"-- {f}")
        rows = []
        for name, build in module.FIGURES.items():
            d = build()
            _eff, fit, labels = measure(d)
            total += 1
            under += labels[0][0] < floor - 0.05
            rows.append((labels[0][0], name, d.w, d.h, fit, labels[0][1]))
        rows.sort()
        for reads, name, w, h, fit, label in (rows if show_all else rows[:1]):
            flag = " " if reads >= floor - 0.05 else "!"
            print(f"{flag}{name:<35} {w:>5}x{h:<5} {w / h:>5.2f} {fit:>6} "
                  f"{reads:>6.1f}pt  {label[:34]}")
    print(f"\n{under} of {total} figures have a label under {floor:.0f}pt "
          f"Caveat-equivalent in the room.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
