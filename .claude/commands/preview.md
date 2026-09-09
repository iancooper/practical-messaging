---
description: Render slides to PNG and look at them — the only way to see a slide on this machine
argument-hint: <day> <slide numbers | all | over>
allowed-tools: Bash, Read
---

Render slides from `$ARGUMENTS` to `build/preview/` **and open the PNGs with the Read tool**.
There is no PowerPoint on this machine; this is the only way to obey *look at the picture* for a
deck of 290 slides. A command that renders and reports without looking has done half the job.

```bash
cd /Users/ian.cooper/Documents/practical-messaging
rm -f build/preview/*.png                                   # ⚑ not cleared between runs
python3 tools/build_deck.py --day <day> --preview <n[,n,…]|all|over>
```

**⚑ `--preview N` is ZERO-based, and so is the filename it writes (`dayD-0NN.png`).** To preview
the *n*th slide, pass `n - 1`. Enumerating slides 1-based to find one and then passing that
number renders its **neighbour**, which looks exactly like a layout that did not change. Say
which slide you actually rendered, by title, so the caller can check the off-by-one.

**`build/preview/` is not cleared between runs**, so a stale PNG from an earlier session sits
there under the name you are about to look for. The `rm` above is not optional.

`--preview over` renders every slide that overflows; `--preview all` renders the day.

**Then Read each PNG and say what is on it.** What this has caught, none of it visible in the
source: a bullet marker drawn on top of its own first letter; `.notdef` boxes because Plex Sans
has no `▪` and no `▎`; a double space at every bold boundary; three photographs that vanished
from a panel because the SVG data URI declared a JPEG as `image/png`; and `Out-Only` rendering
as `Out-` in a table whose whole argument is per-pattern.

To find a slide's index first: `python3 tools/outline.py outlines/DayOne.md --slide "Slide: X"`
dumps one entry, and the builder's own output lists titles in order.
