---
description: Verify the repo state in one pass — renderer, outlines, both decks, lint, legibility
allowed-tools: Bash, Read
---

Verify the whole repo in one pass and report what is true **now**. Do not trust a number in
`PROMPT.md`, `BACKLOG.md` or the plan without checking it here — those files go stale silently.

**Two of these are slow.** `lint_figures.py` takes **over five minutes**, longer than the Bash
default timeout, and `reads_at.py` about two. Start them in the background **first**, then run
the fast checks while they finish. Do not run them in the foreground and do not report them as
hanging.

```bash
cd /Users/ian.cooper/Documents/practical-messaging
```

1. **Start the slow pair in the background**, writing to your scratchpad:
   `python3 tools/lint_figures.py` and then `python3 tools/reads_at.py`.
2. **Fast checks**, in this order:
   - `git log --oneline -5 && git status --short`
   - `python3 tools/diagram.py --check` — expect `all good`
   - `python3 tools/outline.py` — the section/entry/image counts
   - `python3 tools/build_deck.py` — both decks, plus the overflow report
3. **Collect the slow pair** when they land.

Report a short table of **expected vs. actual**, and say plainly which line moved:

| check | expected |
|---|---|
| `git status` | clean but for `.DS_Store` and Ian's own untracked drops in `archive/` and `resources/` |
| `diagram.py --check` | `all good` — rsvg-convert, fontTools, Caveat, Plex Sans/Mono/Serif/Serif SemiBold |
| `outline.py` | Day 1 **91 entries / 49 images**, Day 2 **90 / 84** |
| `build_deck.py` | Day 1 **137 slides**, Day 2 **153**; **the overflow report is empty** |
| `lint_figures.py` | `no labels running out of their shape or onto another` |
| `reads_at.py` | **30 of 90** under the 18pt floor |

**A count that moved is the finding**, so say which and by how much rather than re-stating the
table. `build_deck.py` also prints three standing advisories that are **not** failures — the
photo-panel slides, the 15 multi-figure entries (Ian ruled on those), and the figures under 85%
of their Phase 2 size (`BACKLOG.md` B1 and B2). Mention them only if their counts changed.

If `lint_figures.py` is clean, that is **not** the same as the figures being right — it is blind
to rules, group borders and cylinder rims. Say so if the caller is about to conclude otherwise.
