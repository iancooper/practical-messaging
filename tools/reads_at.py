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

**⚑ And the canvas is only half of THAT.** Every number above is what a figure reads at
**if it gets the whole stage**, 12.4in. Twenty-one slides do not give it the whole stage:
`#layout: side` puts the text beside the picture and leaves it about 6.1in, so those
figures reach the room at roughly **half** the printed number — and until 2026-09-13 this
tool reported 18.0pt for every one of them, with nothing in the output to say which rows
were fiction (BACKLOG G12). Ian has ruled the `side` band fine (`styles.md`), so the
**room** column is information, not a queue of defects; what was wrong was printing a
number nobody should act on and not saying so.

So there are two numbers per figure and both are printed:

    at full   what it reads at on a full-width stage -- a property of the DRAWING
    room      what it reads at on the narrowest slide it is actually placed on, which
              is `build_deck`'s own fraction, so the two cannot disagree

**A figure is not always on a slide.** Nine are handout-only and are fitted to a 154mm
text block instead, three are placed nowhere, and the montage's arrow overlays carry no
labels at all. None of those can be measured against a slide floor, so they are named and
**excluded from the count** rather than silently counted at a width they never get. The
summary says how many.

`--no-deck` skips the two deck layouts and prints the 12.4in numbers alone. It is faster
and it is the behaviour that caused G12, so the output says so.
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


DAYS = {"1": "outlines/DayOne.md", "2": "outlines/DayTwo.md"}


def placements():
    """`{figure-name: [(day, slide, fraction-of-the-reference-stage), ...]}`, both decks.

    **The fraction is the builder's own, not a second copy of the arithmetic.**
    `Laid.reads_at()` already answers *what fraction of its Phase 2 size does this picture
    survive at here*, and it is the number the build report prints as a percentage. Taking
    it whole means there is one formula rather than two that can disagree — and the first
    draft of this function proved the point by restating it wrongly, scaling by the
    rendered WIDTH when a figure squarer than 2.2:1 is fitted by HEIGHT and its effective
    width is the larger `2.2 x h`. That understated every squarer figure.

    It also means nothing here re-reads `#layout:`. `side` is only one of the things that
    narrows a picture — `#layout: figure`, a photograph sharing the panel and a multi-figure
    entry all move it too, and the layout knows about all of them.

    Keyed on the resource stem, because that is what a family names its output: a figure
    `x` is written to `resources/x.png` and the outline links it as `resources/x.png`."""
    import build_deck as B
    out = {}
    for day, md in DAYS.items():
        deck = B.Deck(B.O.parse(os.path.join(B.REPO, md)), day).run()
        for n, laid in enumerate(deck.slides, 1):
            for src, _pw, frac in laid.reads_at():
                stem = os.path.splitext(os.path.basename(src))[0]
                out.setdefault(stem, []).append((day, n, frac))
    return out


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

    where = {} if "--no-deck" in argv else placements()

    total = under = 0
    offstage = []
    # **The header says `at full`, not `at 12.4`.** The reference stage is the builder's
    # `REFERENCE_IN` and nothing here holds a copy of it any more -- the `room` column is
    # the builder's own fraction -- so naming the number in a column head would be the one
    # place it could go stale.
    print(f"{'figure':<34} {'canvas':>11} {'asp':>5} {'fit':>6} "
          f"{'at full':>8} {'room':>7}  {'on':<9} label")
    for f in fams:
        module = importlib.import_module(f)
        print(f"-- {f}")
        rows = []
        for name, build in module.FIGURES.items():
            d = build()
            _eff, fit, labels = measure(d)
            # **A figure can legitimately have no labels at all**, and this crashed
            # on the first one that did -- the montage's eight transparent arrow
            # overlays, which are pure geometry stacked over another figure. There is
            # no smallest label to report, and it does not count against the floor
            # either way, so it is named and skipped rather than silently dropped.
            if not labels:
                rows.append((None, name, d.w, d.h, fit, None, "", "— no labels"))
                continue
            full = labels[0][0]

            # **The narrowest placement is the one that counts**, because a figure on
            # two slides is only as legible as its worst. `spots` empty means the deck
            # never places it -- a handout figure or an orphan -- and there is no slide
            # width to measure it at, so it is reported and left out of the count
            # rather than counted at a stage it never gets.
            spots = where.get(name)
            if where and not spots:
                offstage.append(name)
                rows.append((None, name, d.w, d.h, fit, full, "offstage",
                             labels[0][1]))
                continue
            if spots:
                day, slide, frac = min(spots, key=lambda s: s[2])
                room = full * frac
                tag = f"D{day} s{slide}" + ("+" if len(spots) > 1 else "")
            else:
                room, tag = full, ""      # --no-deck: the 12.4in number, said plainly
            total += 1
            under += room < floor - 0.05
            rows.append((room, name, d.w, d.h, fit, full, tag, labels[0][1]))

        rows.sort(key=lambda r: (r[0] is None, r[0]))
        for room, name, w, h, fit, full, tag, label in (rows if show_all else rows[:1]):
            fullstr = f"{full:>7.1f}pt" if full is not None else f"{'—':>9}"
            if room is None:
                print(f" {name:<33} {w:>5}x{h:<5} {w / h:>5.2f} {fit:>6} "
                      f"{fullstr} {'—':>7}  {tag:<9} {label[:30]}")
                continue
            flag = " " if room >= floor - 0.05 else "!"
            print(f"{flag}{name:<33} {w:>5}x{h:<5} {w / h:>5.2f} {fit:>6} "
                  f"{fullstr} {room:>5.1f}pt  {tag:<9} {label[:30]}")

    scope = "on the narrowest slide each is placed on" if where else \
            "AT THE FULL STAGE, which almost no slide gives them (--no-deck)"
    print(f"\n{under} of {total} figures have a label under {floor:.0f}pt "
          f"Caveat-equivalent\n  {scope}.")
    if offstage:
        print(f"  {len(offstage)} figure(s) are on no slide and are NOT counted — "
              f"a handout figure is fitted to 154mm, not to a stage:")
        print("    " + ", ".join(sorted(offstage)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
