---
description: Rebuild both decks from the outlines and report the overflow
argument-hint: "[1|2]"
allowed-tools: Bash, Read
---

Rebuild the `.pptx` decks from `outlines/` into `build/`, and report what the builder found.

Load the **`deck-build`** skill first — it carries the outline grammar, what the builder does
with each block, and how to answer an overflow.

```bash
cd /Users/ian.cooper/Documents/practical-messaging
python3 tools/build_deck.py            # both days; add --day $ARGUMENTS for one
```

`--report` measures and writes nothing, which is what you want when you only need the numbers.

**Read the output as four things, and say which of them changed:**

1. **Slide counts** — Day 1 **137**, Day 2 **153** as of 2026-09-09. An entry whose argument
   will not fit above its figure becomes two slides, so the count is larger than the entry count
   by design (78 entries split). A count that moved without an outline edit is a finding.
2. **The overflow report** — currently **empty**, and it is a **deliverable, not a diagnostic**.
   The builder never shrinks type to fit; it lays the slide out at the floor and prints what did
   not fit. A new overflow is a **content** decision and belongs to Ian, not a licence to cut.
   The skill has the five ways one has been answered before.
3. **Standing advisories, not failures** — the photo-panel slides, the 15 multi-figure entries
   (Ian ruled on them, plan §8 item 23e), and the figures under 85% of their Phase 2 size
   (`BACKLOG.md` B1 and B2). Report these only if a count moved.
4. **Warnings on stderr** — a clipped table column, or a `#group:` kicker running under the
   figure panel. **A clipped label looks like a short label**, so these are real and were added
   precisely because nothing downstream can see them.

**`build/` is gitignored and is never edited by hand.** If a slide is wrong, the fix is in
`outlines/` or in `tools/build_deck.py`.

**Building is not looking.** If anything about a slide's layout is in question, `/preview` it and
open the PNG — that is the only way to see a slide on this machine.
