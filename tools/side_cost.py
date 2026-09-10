#!/usr/bin/env python3
"""What `#layout: side` would cost a slide that does not have it yet.

**`build_deck.py` reports the cost of every `side` slide that already exists.** It cannot
answer the question that actually gets asked, which is the other way round: *if I put the
text beside this picture, how small does the picture get?* This does that, by laying the
deck out twice -- once as it stands, once with `layout = "side"` forced on -- and reading
`reads_at()` off both.

**Ian, 2026-09-10, on rolling `side` out to Day 2:** *do not; ask per slide.* This is the
tool that answers the asking. Day 1's six were agreed one at a time and Day 2's will be
too, so the counterfactual is a standing question, not a one-off.

    python3 tools/side_cost.py 2              # every eligible entry on Day 2
    python3 tools/side_cost.py 2 --slide 57   # one slide, by its 1-based SLIDE number
    python3 tools/side_cost.py 1 --all        # include entries that do not split today

**Eligible** means the entry currently becomes two slides -- the argument then the picture,
which is the split Ian calls weird -- **and carries exactly one figure**, because
`_side_slide` is guarded on `len(figs) == 1`. An entry with two or three figures cannot use
the arrangement at all, and there are 15 of those on Day 2.

**Read the percentage against 85%, not against 100%.** It is the figure's size as a fraction
of what Phase 2 measured its labels at, so 50% means the label is half the size the 18pt
floor was set from. The six Ian accepted on Day 1 landed at 49, 49, 69, 69, 71 and 71% --
so a low number is a cost to weigh, not a veto. **Two things it will not tell you**: BPMN is
already at the floor (rule 6), so a given percentage hurts it more than any other family;
and a slide that also carries photographs shares the half-stage, which is why *The Frame*
falls to 26% when the arrangement alone would not do that.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_deck as B                                            # noqa: E402

DAYS = {"1": "outlines/DayOne.md", "2": "outlines/DayTwo.md"}


def figures_of(sl):
    """The drawn figures on an entry. Photographs do not count -- `reads_at` ignores
    them, and `_is_photo` reads the extension, so a `src` that never resolved is not
    one either."""
    return [b for b in sl.blocks
            if b.kind == "image" and b.src and not B.Deck._is_photo(b)]


def measure(day, want_all=False):
    """**Keyed on the entry's position, never on its title.** Day 2 has three titles
    that occur twice -- *The Reactive Manifesto*, *Handlers + Activity State Updates*,
    *State Machine + Activity State Updates* -- so a title-keyed lookup silently reports
    one instance's numbers against the other's slide number, and nothing downstream can
    tell. The two parses walk the same file, so the index is stable across both."""
    md = os.path.join(B.REPO, DAYS[day])

    # -- as it stands. Record what each figure reads at, and which entries split.
    parsed_now = B.O.parse(md)
    at = {id(sl): i for i, sl in enumerate(parsed_now.slides)}
    base = B.Deck(parsed_now, day).run()
    now, splits, number = {}, set(), {}
    for n, laid in enumerate(base.slides, 1):
        if laid.slide is None:               # a section marker carries no entry
            continue
        i = at[id(laid.slide)]
        number.setdefault(i, n)
        if laid.split:
            splits.add(i)
        for src, _w, frac in laid.reads_at():
            now[(i, src)] = frac

    # -- and again, with the arrangement forced on everything that could take it.
    parsed = B.O.parse(md)
    eligible = [(i, sl) for i, sl in enumerate(parsed.slides)
                if len(figures_of(sl)) == 1 and (want_all or i in splits)]
    for _i, sl in eligible:
        sl.layout = "side"
    where = {id(sl): i for i, sl in enumerate(parsed.slides)}
    side = {where[id(l.slide)]: l for l in B.Deck(parsed, day).run().slides
            if l.kind == "side" and l.slide is not None}

    rows = []
    for i, sl in eligible:
        laid = side.get(i)
        if laid is None:                     # guarded out -- a photograph slide, say
            continue
        for src, w, frac in laid.reads_at():
            rows.append(dict(slide=number.get(i, 0), title=sl.title,
                             fig=os.path.basename(src), was=now.get((i, src)),
                             now=frac, width=w, over=laid.overflow))
    return rows


def main(argv):
    day = next((a for a in argv[1:] if a in DAYS), None)
    if day is None:
        print(__doc__.split("\n\n")[0])
        print("\nusage: python3 tools/side_cost.py {1|2} [--slide N] [--all]")
        return 2
    one = argv[argv.index("--slide") + 1] if "--slide" in argv else None
    rows = measure(day, want_all="--all" in argv)
    if one is not None:
        rows = [r for r in rows if str(r["slide"]) == one or
                str(r["slide"] + 1) == one]     # the figure slide, or its argument
        if not rows:
            print(f"slide {one} is not an eligible entry on Day {day} — it does not "
                  f"split, or it carries no figure or more than one.\n"
                  f"`python3 tools/deck_index.py {day} --slide {one}` says what it is.")
            return 1

    print(f"\nDay {day}: what `#layout: side` would cost, per entry "
          f"({len(rows)} eligible)\n")
    print(f"{'slide':>5} {'full':>6} {'side':>6} {'delta':>6} {'width':>7} "
          f"{'over':>6}  figure / title")
    for r in sorted(rows, key=lambda r: r["now"]):
        d = f"{(r['now'] - r['was']) * 100:+.0f}" if r["was"] else "    ?"
        flag = "<" if r["now"] < 0.85 else " "
        print(f"{r['slide']:5d} {(r['was'] or 0) * 100:5.0f}% {r['now'] * 100:5.0f}% "
              f"{d:>6} {r['width']:6.1f}in {r['over']:5.2f} {flag} "
              f"{r['fig'][:32]:<34} {r['title'][:38]}")
    if not rows:
        return 0
    under = sum(1 for r in rows if r["now"] < 0.85)
    over = [r for r in rows if r["over"] > 0.01]
    med = sorted(r["now"] for r in rows)[len(rows) // 2]
    print(f"\n    median if applied to all of these: {med * 100:.0f}%")
    print(f"    under 85%: {under} of {len(rows)}")
    print(f"    text would no longer fit beside the picture: {len(over)} of {len(rows)}"
          + (" — move it to the presenter notes" if over else ""))
    for r in sorted(over, key=lambda r: -r["over"]):
        print(f"      {r['over']:5.2f}in over   {r['title'][:52]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
