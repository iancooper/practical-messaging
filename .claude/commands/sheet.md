---
description: Build a review sheet for a batch of artwork — offered to Ian, never published unasked
argument-hint: <what the batch is>
allowed-tools: Bash, Read, Write, Edit, Artifact, AskUserQuestion
---

Build a review sheet for `$ARGUMENTS` — the batch of figures Ian cannot see, because **he cannot
review PNGs in a terminal and he reviews by looking**. Every finding on this work so far has
arrived through one of these.

Load the **`review-sheet`** skill — it carries what the page has to do, why each constraint
exists, and the seven sheets already published.

### ⚑ Ask before you publish. Every time.

A publish puts a web page on claude.ai, and that is Ian's call, not yours. The first attempt at
one of these was **refused by the auto-mode classifier** — *"the user never asked for a review
web page"* — and that refusal was **correct**. Do not route around it.

The pattern that works: **offer the sheet in the same `AskUserQuestion` as the decision it
illustrates.** Both 2026-09-07 sheets were approved that way before they were built.

If he has not said yes, build the file and stop with the path. Do not call `Artifact`.

### Then

1. **Draft the page** — `artifact-design` first, then the skill's checklist: every PNG inlined as
   a base64 data URI (the CSP blocks local files and external images), `styles.md`'s own palette
   and faces so the red on the page is the red in the figures, an **address on every claim**
   (`A4·1`, `B2·2`) he can quote back, and a plate that stays light in **both** themes, because
   a printed card cannot be dark-moded.
2. **Publish only on his say-so**, then give him the URL and the addresses.
3. **When findings come back, apply them and republish the same artifact** — pass its `url` and
   `action: "read"` it first. Scratchpads are per-session, so "republish the same path" only
   works inside one session; from a fresh one you need the URL.
4. **Record the sheet and its state** in the `review-sheet` skill's own table and `BACKLOG.md` F3.

**His answer often exceeds the options offered** — read it as prose, not as a selection.
