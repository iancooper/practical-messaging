#!/usr/bin/env python3
"""Figures for the *Managing Asynchronous APIs* handout.

    python3 tools/asyncapi_figures.py           # -> resources/asyncapi-*.drawio + .png
    python3 tools/asyncapi_figures.py --list    # names only

**A twelfth family, and a small one.** It exists because the handout is not the deck
and not EIP: `eip_figures.py` is the twenty-one Hohpe & Woolf replacements, and a
virtuous cycle is neither a pattern of theirs nor a slide of ours. Putting it there
would have made that module's docstring a lie for the sake of saving a file.

**Handout figures, so no `compact()`** -- the same as the eight routing figures at the
end of `eip_figures.py`. A handout figure is held at reading distance rather than read
across a room, and it prints through `handouts/print.css`, which caps a figure by
HEIGHT at 92mm because the pack's figures run 1.26 : 1 to 3.04 : 1.

Conventions are the family's, from styles.md: carbon carries flow, ink names things,
comment green is what we say about them, and **one idea in red**.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")

FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


@figure("asyncapi-virtuous-cycle")
def virtuous_cycle():
    """The handout's closing argument, drawn: the three pillars are one system.

    **Red is the RETURN**, not the spec. The section's own sting is the last
    paragraph -- *adopting one pillar on its own tends to disappoint* -- so the
    load-bearing thing in the picture is the arc that closes the loop, and the
    three forward arrows are ordinary carbon flow. Red the spec box instead and
    the figure argues "one source of truth", which is §3's idea, not this one.

    **Laid out as a row, not a ring.** A ring of four is square, and a square
    figure is fitted by its height in both destinations that matter -- the slide
    stage and the handout's 92mm cap -- so it would render smaller while saying
    the same thing. The row also keeps the spec at the left where the reading
    starts, which is the half of "one spec drives all three" worth keeping.

    The stage labels under each box are the ASCII staircase's four lines, which
    this figure replaces: better specs, better governance, more reliable
    provisioning, more trustworthy discovery.
    """
    d = Diagram("The Virtuous Cycle", w=560, h=318)

    # 560 wide, not the 852 the first draft used. A handout figure is fitted to the
    # 154mm text block, so PRINTED LETTER SIZE IS 154 / w -- the canvas width is the
    # only lever on it, and at 852 this read at ~9pt against ~14 for the routing
    # figures. The floor is set by measured advances, not by eye: "Provisioning" is
    # 72.3 units at 18pt so a box may not go below ~85, and the foot comment's long
    # line is 460.7. Everything here is the narrowest those two allow.
    stages = (
        (30,  "AsyncAPI\nspec",  "one source"),
        (160, "Governance",      "schemas validated\nand versioned"),
        (290, "Provisioning",    "infrastructure\nfrom the spec"),
        (420, "Discovery",       "a catalogue that\nis actually current"),
    )
    boxes = []
    for x, name, under in stages:
        b = d.box(x, 80, 96, 56, name)
        boxes.append(b)
        # y=172, not the box bottom + a few: `note` block-centres on y, so a TWO-line
        # note at 18pt reaches ~22 units above it, and the first draft laid all three
        # of these straight across the bottom border of the box they belong to.
        d.note(x + 48, 172, under, INK, 14)

    for a, b in zip(boxes, boxes[1:]):
        d.arrow(a, b, sides=("r", "l"))

    # The closing arc, routed OUTSIDE everything -- out of Discovery's right edge,
    # under the row, and back into the spec's left. The first draft dropped it out of
    # Discovery's bottom and up into the spec's bottom, which put a red stroke through
    # "a catalogue that is actually current" and through "one source"; the source
    # looked fine and the linter is blind to both, because neither is an edge label on
    # a shape. Four vias, one per corner -- two would give a trapezoid.
    d.arrow(boxes[-1], boxes[0], "and round again", accent=True,
            via=[(544, 108), (544, 244), (16, 244), (16, 108)], sides=("r", "l"))

    d.note(280, 26, "the return is the point -- each turn makes the next spec better",
           ANNOTATION, 17)
    d.note(280, 286, "adopt one pillar alone and it decays: a catalogue nobody generates\n"
                     "goes stale, and a registry nobody provisions from is a second source of truth",
           COMMENT, 14)
    return d


def main(argv):
    if "--list" in argv:
        for name in FIGURES:
            print(name)
        return 0
    only = [a for a in argv if not a.startswith("--")]
    for name, fn in FIGURES.items():
        if only and name not in only:
            continue
        d = fn()
        drawio, png = d.save(os.path.join(OUT, name))
        print(f"  {name:<32} {d.w}x{d.h}  {os.path.getsize(png):>7,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
