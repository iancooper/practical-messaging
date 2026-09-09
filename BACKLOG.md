# Backlog — what is outstanding #

**An index, not a source of truth.** Every line points at where the real detail lives.
`REDEVELOPMENT-PLAN.md` is the source of truth for the decks; **`code-rewrites.md` is a separate
workstream with its own brief**. If this file and the plan disagree, **the plan wins and this file
is stale**. Kept as a table on purpose — counts in prose go stale silently,
and a table you can read the length of does not.

Last reconciled against the repo: **2026-09-09**, at commit `d43034f`.

**Where things stand.** Phases 1 and 2 are closed. Phase 3 — the deck builds — is most of the way
through: both decks build clean from `outlines/` with an empty overflow report, Day 1 **136 slides**
and Day 2 **153**, **90 figures** across eleven families plus **2 print cards**, lint clean,
`reads_at` **30 of 90**, and speaker notes ship into both `.pptx`. What is left is below.

---

## A. Next up — make the repo operable ##

**Ian, 2026-09-09:** *"We are building tools to allow us to regenerate the decks from outlines, draw
diagrams etc. We may want to return later, update outlines, rebuild. That seems like we need a
CLAUDE.md file, some commands that we can use to trigger operations and some skills that they
invoke. I think we should build it as the next step, after a fresh session starts."*

**This is the live job, and it is deliberately the first thing a fresh session does.** Today the
operating knowledge lives in `PROMPT.md`, which is untracked session state — so it is one `rm` away
from gone, and a new session has to read 980 lines of it before it can safely rebuild a figure.

| # | item | what it is | size | detail |
|---|---|---|---|---|
| **A1** | `CLAUDE.md` | The repo's operating instructions, **tracked**: read order, the build pipeline, the tool inventory, the two registers and the palette, and the rules that have each cost real rework — never edit `build/`, never put provenance in an outline, look at the PNG, rebuilds must be byte-identical, absolute paths, `lint_figures.py` takes over five minutes | M | `PROMPT.md` *Rules that must hold* + *Figure knowledge* are the raw material |
| **A2** | Slash commands | `.claude/commands/*.md` for the operations run every session: verify, rebuild the decks, preview slides, rebuild and inspect one figure, publish a review sheet | S | sketch in `PROMPT.md` *Do this next* |
| **A3** | Skills | `.claude/skills/*/SKILL.md` for the procedures the commands invoke — building a deck, drawing a figure, building a review sheet. The long-form knowledge that should not sit in every context window | M | as above |

---

## B. Deck and artwork ##

| # | item | why it is not done | size | detail |
|---|---|---|---|---|
| **B1** | Reshape `boundary-what-crosses` | **The one figure worth doing.** Reads at 82%; it is the load-bearing slide of both days and leaves a third of its stage empty. A row layout — app and store side by side, not stacked — takes it to 96%. `service()` now has exactly one caller, so it can be changed without touching another figure | M | plan §8 item 23e, *One figure stayed at 82%* |
| **B2** | The other five figures under 85% | **No action available.** While a figure's canvas and its stage are both height-fitted, the percentage reduces to `stage_height × 2.2 / 12.4` and the aspect cancels out: nothing improves until the drawing is wider than ~2.57 : 1. Only a content change moves them | — | plan §8 item 23e; the list is in `PROMPT.md` |
| **B3** | 30 of 90 figures under the 18pt floor | **18 are Ian's standing decision** — `bpmn_hotel`, `bpmn_shopping`, `paper_flow`; he scoped the re-sweep away from them. The other 12 are **clamp-bound**: a shape may not shrink below its own label, so the only lever is content, per figure | — | `PROMPT.md` *On Ian's desk* item 8 |
| **B4** | Day 1 image-dump sweep | Day 2 is clean — its 17-image entry was found and split. **Day 1 has never been checked** for the same thing | S | `PROMPT.md` *Sweeps still outstanding* |
| **B5** | The load-bearing-line sweep | The sentence that carries a slide keeps hiding in its presenter notes; it has been caught six times, twice by Ian. **Day 1 §4's sub-topics** are the unswept part — reviewed early, long dense notes | M | as above |
| **B6** | Stale cross-references | "discussed next" / "the next slide" notes break on any reorder. Must be **re-run after every structural change**, not once at the end | S | as above |
| **B8** | Day 1's exercise slots move | ⛔ **Blocked on `code-rewrites.md`, and recorded so it is not lost.** Ian's new exercise list (2026-09-09) makes exercise 1 need §4.3 and exercise 2 need §4.4 — but the *Exercise Material — Introduction & RMQ* pointer slide sits at the end of **§4.2**, which was right for the old Point-to-Point and Datatype exercises and is wrong for these. The Kafka slot at the end of §4.5 is still correct. **Do not edit `outlines/` for this until the rework lands** | S | `code-rewrites.md` §3.2 |
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
