#!/usr/bin/env python3
"""Slide number -> what is on it. The map between Ian's review and the outline.

    python3 tools/deck_index.py 1                 # the whole of Day 1
    python3 tools/deck_index.py 2 --slide 63      # one slide, with its outline text
    python3 tools/deck_index.py 1 --slide 56-59   # a run

**Ian reviews by slide number and pushes back by slide number, and the slide number
is not the outline entry number.** Day 1's 91 entries build 138 slides, because 32 of
them split into an argument and a picture (`build_deck.Deck.content_slide`), and the
two section-divider slides and the title slide are not entries at all. Counting `###`
in the outline therefore gives an answer that is wrong by about a third, and wrong by
a DIFFERENT amount at every point in the deck.

This runs the real layout and reports what came out, so the numbering is the built
deck's own and cannot drift from it. It writes nothing.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_deck as B                                           # noqa: E402
import outline as O                                              # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = {1: "outlines/DayOne.md", 2: "outlines/DayTwo.md"}


def index(day):
    """[(n, Laid)] for one day, 1-based, in deck order."""
    deck = O.parse(os.path.join(REPO, SOURCE[day]))
    return list(enumerate(B.Deck(deck, day).run().slides, 1))


def _span(arg):
    if arg is None:
        return None
    lo, _, hi = arg.partition("-")
    return int(lo), int(hi or lo)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("day", type=int, choices=(1, 2))
    ap.add_argument("--slide", help="one slide, or a run like 56-59")
    a = ap.parse_args(argv)

    want = _span(a.slide)
    rows = index(a.day)
    if want:
        rows = [(n, l) for n, l in rows if want[0] <= n <= want[1]]
        if not rows:
            print(f"no such slide in Day {a.day} ({len(index(a.day))} slides)")
            return 1

    for n, laid in rows:
        sl = laid.slide
        title = sl.title if sl is not None else f"[{laid.kind}]"
        sec = (sl.section if sl is not None else "") or ""
        figs = ", ".join(os.path.basename(f[0]) for f in laid.figures)
        mark = "↳" if laid.split and laid.kind == "figure" else " "
        print(f"{n:4d} {mark} {laid.kind:7s}  {str(sec)[:24]:24s}  {title}"
              + (f"   [{figs}]" if figs else ""))
        if want and sl is not None:
            if sl.group:
                print(f"       group: {sl.group}")
            for b in sl.blocks:
                text = b.src if b.kind == "image" else getattr(b, "text", "")
                if b.kind == "table":
                    text = " | ".join(b.head or []) + f"  (+{len(b.rows)} rows)"
                print(f"       {b.kind:8s} {O.plain(text)[:96]}")
            for note in sl.notes:
                print(f"       notes:   {O.plain(note.text)[:96]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
