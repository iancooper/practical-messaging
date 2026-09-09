# Backlog — what is outstanding #

**An index, not a source of truth.** Every line points at where the real detail lives.
`REDEVELOPMENT-PLAN.md` is the source of truth for the decks; **`code-rewrites.md` is a separate
workstream with its own brief**. If this file and the plan disagree, **the plan wins and this file
is stale**. Kept as a table on purpose — counts in prose go stale silently,
and a table you can read the length of does not.

Last reconciled against the repo: **2026-09-09**, after B1 and B4-B6. **§B is closed except B2/B3,
which have no action available; §C, the two handouts, is what is left.**

**Where things stand.** Phases 1 and 2 are closed. Phase 3 — the deck builds — is most of the way
through: both decks build clean from `outlines/` with an empty overflow report, Day 1 **138 slides**
and Day 2 **153**, **90 figures** across eleven families plus **2 print cards**, lint clean,
`reads_at` **30 of 90**, and speaker notes ship into both `.pptx`. **Day 1's figures now sit at a
median 91% of their Phase 2 label size with two under 85%, Day 2 at 96% with three.** What is left
is below.

---

## A. ✅ Closed — the repo is operable ##

**Ian, 2026-09-09:** *"We are building tools to allow us to regenerate the decks from outlines, draw
diagrams etc. We may want to return later, update outlines, rebuild. That seems like we need a
CLAUDE.md file, some commands that we can use to trigger operations and some skills that they
invoke. I think we should build it as the next step, after a fresh session starts."*

**Done.** The operating knowledge is now **tracked**, and split three ways: `CLAUDE.md` is what is
true whether or not anything is invoked, a command is a verb you type, and a skill is the procedure
it loads. `PROMPT.md` stays what it always was — session state, untracked — but nothing load-bearing
lives only there any more.

| # | item | state |
|---|---|---|
| **A1** | `CLAUDE.md` | ✅ Tracked at the repo root. Read order, the pipeline, the tool inventory, the two registers and the palette, 14 rules that each cost real rework, and the working notes for this machine |
| **A2** | Slash commands | ✅ `.claude/commands/` — `/verify` (one pass, slow checks backgrounded) · `/build` · `/preview` (renders **and looks**) · `/figure` (rebuild, lint, `reads_at`, **and show the PNG**) · `/sheet` (offered, never published unasked) |
| **A3** | Skills | ✅ `.claude/skills/` — `deck-build` (the grammar, the builder, answering an overflow) · `figure-drawing` (the API, the legibility arithmetic, the composition test, what lint cannot see) · `review-sheet` (the five requirements, the etiquette, the seven sheets) |

**One thread stays open**, and it is recorded in the `review-sheet` skill rather than here: there is
still **no committed generator** for a review sheet. Each one has been written into a scratchpad and
died with the session. The next one written should go in `tools/` and be committed.

---

## B. Deck and artwork ##

| # | item | why it is not done | size | detail |
|---|---|---|---|---|
| **B1** | ✅ Reshape `boundary-what-crosses` | **Done 2026-09-09.** Application beside store, mirrored through the line: 1.57 : 1 becomes 2.60 : 1 and **82% becomes 96%**, the stage's own width and the cap. Nothing cut — three bullets, both refusals, both crosses. The trade is that §1's boundary rule now reads shorter than §3's | — | plan §8 item 23e, *One figure was at 82%* |
| **B2** | The other five figures under 85% | **No action available.** While a figure's canvas and its stage are both height-fitted, the percentage reduces to `stage_height × 2.2 / 12.4` and the aspect cancels out: nothing improves until the drawing is wider than ~2.57 : 1. Only a content change moves them | — | plan §8 item 23e; the list is in `PROMPT.md` |
| **B3** | 30 of 90 figures under the 18pt floor | **18 are Ian's standing decision** — `bpmn_hotel`, `bpmn_shopping`, `paper_flow`; he scoped the re-sweep away from them. The other 12 are **clamp-bound**: a shape may not shrink below its own label, so the only lever is content, per figure | — | `PROMPT.md` *On Ian's desk* item 8 |
| **B4** | ✅ Day 1 image-dump sweep | **Done 2026-09-09, and it is a clean negative.** Day 1 carries 49 images across 91 entries and **no entry holds more than one** — the defect Day 2's *Paper Workflow Illustrations* had cannot exist here. Day 2 still has 18 multi-image entries, all of them ruled on in plan §8 item 23e | — | plan §8 item 23e |
| **B5** | ✅ The load-bearing-line sweep, Day 1 §4 | **Done 2026-09-09.** Six candidates across §4.1–§4.4; §4.5 carries no presenter notes at all, so nothing can hide there. **Four promoted** — *Channels*, *Translate and Dispatch*, *Competing Consumers*, *Invalid Message Channel*. **Two were false positives the figures already answered**, and only rendering the slides showed it | — | plan §8 item 24 |
| **B6** | ✅ Stale cross-references, re-run | **Done 2026-09-09**, after B5. Four wrong: two on Day 1 (*the next slide is the bill*, which pointed at the wrong slide; *the last slide of this sub-section*, which the exercise slot displaced) and two on Day 2 (a count of five that is now seven, and *the next two slides* that are the second and third). All four now **name the slide** rather than count from it. **Re-run this after any structural change** | — | plan §8 item 24 |
| **B8** | ✅ Day 1's exercise slots | **Done 2026-09-09.** Ian ruled three slots; the RMQ pointer moved off §4.2 to close §4.3, and *Exercise Material — Failing Well* now closes §4.4. Day 1 is 91 entries, **137 slides** | — | `code-rewrites.md` §3.2 |
| **B7** | `(sNN)` markers vs the 2025 decks | The 2025 decks in `archive/` hold the same 112 images byte-for-byte as the 2024 one the markers were derived from, **but the slide text has never been diffed** — so whether the markers are stale is open | S | `PROMPT.md`, *Checked, so do not re-report it* |

---

## C. Handouts — Phase 3, not started ##

Both are **cut content that was promised a home**, so neither is optional: a deck that says "this is
in your pack" and ships no pack is worse than one that never said it.

| # | item | state | size | detail |
|---|---|---|---|---|
| **C1** | *Managing Asynchronous APIs* | Source is the QCon London 2026 deck (43 slides, `session-work/qcon-asyncapi.txt`). It is a **40-minute conference narrative** and needs a one-page index up front to read as reference rather than as a talk | M | plan §6 |
| **C2** | The routing-patterns handout | Four open sub-tasks: assemble from `script/Patterns/*.md` (near-1:1 with the cut slides, and written as prose already); decide artwork — redraw the 8 EIP figures or cite Hohpe & Woolf with attribution, which a handout may legitimately do and the deck could not; frame it as reference; and signpost it from the deck | L | plan §10 |

---

## D & E — moved out to `code-rewrites.md` ##

**Ian, 2026-09-09:** *"Let's move D, E out. We can handle the code rewrites separately… I will pick up
with the agent and old code locations. The timings will form part of that."*

| was | now |
|---|---|
| **D.** Day 1 coding-exercise rework | `code-rewrites.md` — a standalone brief for another agent |
| **E.** Timing (T-2 … T-5, and the unmeasured code blocks) | the same file, §5 |

**Why the timing went with it rather than staying here.** The two Day 1 code blocks are **160 minutes
of a 390-minute day, estimated and never measured**. T-2 … T-5, the four parked deck cuts, are worth
about **24 minutes between them**. Whatever the rewrite does to the exercises dominates every
deck-side lever, so the deck cuts stay parked until the exercise duration is known — cutting teaching
to pay for an estimate nobody has checked is the wrong order.

**Nothing in `exercises/` or `videos/` is the deck workstream's to change.** If a rename or a
restructure happens over there, `outlines/DayOne.md` names the exercise decks and videos by title and
will need the matching edit — that comes back here as a request, not as an edit made from that side.

---

## F. On Ian's desk — not ours to do ##

| # | item | state |
|---|---|---|
| **F1** | Export the order-taking photograph | *phone / card machine / order pad*, Day 2 §Flow, *Three different media, one notation*. He offered. **The last class-A marker in either deck**, and the only `#image:` line left anywhere. Checked: it is in neither the 2024 nor the 2025 deck |
| **F2** | `cp tools/fonts/*.ttf ~/Library/Fonts/` | **Live, not future.** The built decks name IBM Plex Serif / Sans / Mono and Caveat, and **PowerPoint substitutes until they are installed** — so the first thing he sees would not be the deck we built. His machine, his call |
| **F3** | Three review sheets awaiting him | **The Artwork Sheet** (56 figures, part-reviewed — two findings came back and were applied, the rest he has not been through), **The Legibility Floor**, **Muted Is For Lines**. Sheet 7 (*Four Composed, Two Printed*) has been reviewed and both its calls answered |
| **F4** | Two unlinked files he dropped in | `resources/Folder Stack.jpg` and `resources/Manila Envelope.jpg`. Folder Stack is a **cleaner file than the one on *The Desk*** but did not come from his deck, and one watermarked Getty comp has already been found in this set — so a swap is his call. Manila Envelope matches plan §8 6a's interdepartment envelope and is linked nowhere. **Ask before wiring either in** |
| **F5** | RPC's red | **Closed unless he reopens it.** Raised twice on *Four Answers, One Stage* and answered neither time; he approved the pass around it. Will not be raised a third time |

---

## What is closed ##

Recorded so nothing here gets re-opened by accident.

| | |
|---|---|
| **Phase 1** | Every review item D1-1…D1-11, D2-1…D2-10, T-0 and T-1, each with its own commit and a rationale block in plan §9 or §11 |
| **Phase 2** | 90 figures across eleven families; `[external]` is 0; both days have 0 pending markers; Day 1 fully annotated. Only F1 remains |
| **The timing pass** | Plan §11, done and closed |
| **The seven overflowing slides** | Five splits, three cuts; the report is empty and nothing was shrunk |
| **The multi-figure question** | Plan §8 item 23e. Four composed, **one of which Ian split back on review** — and that reversal is the sharpest finding of the exercise |
| **The two delegate reference cards** | Plan §8 item 8. One per pack, both built |
| **The Paper Flow exercise** | Plan §7, built and wired |
| **The tooling job (§A)** | `CLAUDE.md`, five commands and three skills. The operating knowledge is tracked now, not session state |
