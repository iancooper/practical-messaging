#!/usr/bin/env python3
"""Measure every figure's labels against the shapes around them.

    python3 tools/lint_figures.py            # all nine families
    python3 tools/lint_figures.py bpmn_hotel paper_flow

Two checks, both of which found real defects the eye did not, during the label-size
sweep of 2026-09-07:

  * **a centred label wider than the shape it sits in** -- the label runs out of its
    own box. `Pay for the Booking` stopped fitting its task at 17pt; `IIP` was one
    unit proud of its packet.
  * **an edge label landing on a node** -- including on the node the edge *ends at*,
    which is where it usually happens, because a right-angled route puts the label
    right up against its destination. `room free` landed on the message marker of the
    task it labels; `the payment` sat on the boundary bar it crosses.

Neither is caught by `diagram.py`'s glyph warning, and neither is visible in the
source. **Run this after any size or geometry change**, then still look at the PNG:
this measures overlap, it does not have taste.

A hit is a report, not a failure -- some overlaps are fine, and the margin below is
deliberately generous. Exit status is 0 unless a family fails to build.
"""

import collections
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import _Outliner, HAND, PLAIN                       # noqa: E402

FAMILIES = ("eip_figures", "coupling_grids", "if_later", "queues_streams",
            "integration_styles", "bpmn_hotel", "bpmn_shopping", "paper_flow",
            "flow_reactive")

# node kinds that belong to the BPMN vocabulary and so are set in Plex Sans
BPMN_KINDS = {"task", "event", "gateway", "choreo", "pool", "lane"}

# a label may come this close to a shape before it is reported
MARGIN = 5


def _advance(text, face, size):
    _, adv = _Outliner.outline(text, face, size, 0, 0, "middle",
                               weight=490 if face == PLAIN else None)
    return adv


def check(families=FAMILIES):
    """Yield (family, figure, kind, description) for every measured collision."""
    for fam in families:
        module = importlib.import_module(fam)
        for name, build in module.FIGURES.items():
            d = build()
            d._legible()          # sizes are only final once the floor has run

            for n in d.nodes:
                if n["kind"] == "note" or not n.get("label"):
                    continue
                if n.get("label_pos") != "center" or not n.get("w"):
                    continue
                face = PLAIN if n["kind"] in BPMN_KINDS else d.font
                for line in str(n["label"]).split("\n"):
                    adv = _advance(line, face, n["size"])
                    if adv > n["w"] - 2 * MARGIN:
                        yield (fam, name, "overflow",
                               f'{n["kind"]} label "{line}" is {adv:.0f} wide in '
                               f'{n["w"]}')

            for e in d.edges:
                if not e.get("label"):
                    continue
                mx, my = d._mid(d._points(e))
                size = d._edge_pt(e)
                bpmn = e.get("bpmn")
                face = d.font if bpmn else HAND
                adv = _advance(e["label"], face, size)
                x0 = mx + e.get("lx", 0) - adv / 2
                x1 = x0 + adv
                base = my - (6 if bpmn else 7) + e.get("ly", 0)
                # the outline's own box: roughly the ascender down to the descender
                y0, y1 = base - size * 0.78, base + size * 0.22
                for n in d.nodes:
                    if n["kind"] in ("note", "rule") or not n.get("w"):
                        continue
                    if (x0 < n["x"] + n["w"] + MARGIN and x1 > n["x"] - MARGIN
                            and y0 < n["y"] + n["h"] + MARGIN
                            and y1 > n["y"] - MARGIN):
                        what = str(n.get("label", "")).replace("\n", " ") or n["kind"]
                        yield (fam, name, "collision",
                               f'edge label "{e["label"]}" lands on {what}')
                        break


def main(argv):
    families = [a for a in argv if not a.startswith("-")] or list(FAMILIES)
    hits = collections.defaultdict(list)
    for fam, name, kind, detail in check(families):
        hits[(fam, name)].append((kind, detail))
    for (fam, name), items in sorted(hits.items()):
        print(f"{fam}/{name}")
        for kind, detail in items:
            print(f"    {kind:10} {detail}")
    total = sum(len(v) for v in hits.values())
    print(f"\n{total} in {len(hits)} figures"
          if total else "\nno labels running out of their shape or onto another")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
