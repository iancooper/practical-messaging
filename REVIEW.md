# Review — Ian's first pass over the built decks #

**Ian, 2026-09-10, on the rendered Day 1 deck:** *"First, this a great first pass."* Then
twenty-six findings. This file is the **work list**, and it is worked top to bottom.

**Day 1 first, then a Day 2 pass** for the two findings that are not Day-1-specific — the text-box
split and the AI-isms. Ian reviews Day 2 by hand after that.

> **Read `BACKLOG.md` for everything else that is outstanding.** This file is only this review.
> When a row here closes it closes here; `BACKLOG.md` §H carries one line pointing at this file.

---

## How to find a slide by its number ##

Ian numbers by the **1-based slide number in the built `.pptx`**, which is not the outline entry
number — 91 Day 1 entries become 138 slides, because 32 of them split into an argument and a
picture. The index is:

```bash
python3 tools/deck_index.py 1        # 1-based slide no. -> kind, section, title, figure
python3 tools/deck_index.py 1 --slide 63
```

**Every number below is a slide number in the deck as Ian reviewed it** — commit `495fd20`,
Day 1 at 138 slides. They will move as this list is worked, which is why every row also names its
**outline anchor**, and the anchor is what to trust.

---

## §R0 — the builder. Three of these are Ian's, one is mine ##

These are not content, and every one of them lands on **both** decks. Do these first: two of the
Day 1 content rows below cannot be answered until R0-2 and R0-4 exist.

| # | the ask | size | state |
|---|---|---|---|
| **R0-1** | **Slide numbers, bottom left.** *"Let's put numbers in the bottom left of slides, so we can easily refer to them."* A chrome op on every slide but the title slide, drawn like the kicker. **This is what makes every other row in this file addressable**, so it goes first | S | ✅ |
| **R0-2** | **One text box per block, and let it wrap.** *"On #3, I note that a paragraph is split into three text boxes. This will make it hard to add animation for progressive disclosure… We also don't want to have a single text box per page, because that also defeats progressive disclosure, we want text box per paragraph, bullet, or heading."* `emit_pptx` currently writes **one text box per wrapped LINE** with `word_wrap = False` — the comment says *"the layout already wrapped, and letting PowerPoint re-wrap would put the deck somewhere the preview is not"*. The **table cells already take the other option** and re-wrap to the measured width; bodies should too. **⚑ This is also the fix for all four of Ian's "overflows"** — see R0-3 | M | ✅ |
| **R0-3** | **The four overflows are one bug, and it is R0-2's.** #4, #61, #63 and #72 are **all callouts**, all Caveat, and **all four wrap correctly in the preview**. They run off the slide in PowerPoint because the box is `Inches(W_IN)` wide with `word_wrap = False`: a line that is 11.7in of Caveat is wider than the slide in whatever face PowerPoint substitutes (**`BACKLOG.md` F2 — the fonts are not installed on Ian's machine**). Fix R0-2 and these four fix themselves. **Verify all four after R0-2 rather than editing the four lines** | — | ✅ |
| **R0-4** | **Progressive disclosure, grouped by idea.** *"We also want animation for that disclosure (you should be able to edit this), but grouped by idea, not naively one transition per paragraph."* python-pptx has no animation API, so this is `<p:timing>` XML written into the slide part. **Two decisions to put to Ian before building it** — (a) how a reveal group is *expressed*: a default grouping rule the builder infers, or an explicit marker in the outline; (b) whether the picture is its own step. **Ask before implementing** | L | ☐ |
| **R0-5** | **A fourth arrangement: text left, drawing right.** Not asked for by name, but **eight of Ian's rows need it** — #56/57, #58/59, #60/61, #62, #64/65, #68/69 — all the same instruction: *"shrink the diagram… put the text on the left"*. The builder has three arrangements today and the figure-leads one exists **because `styles.md`'s panel costs a drawing 47–63% of its label size**. Ian is overriding that for these slides knowingly. **Report what each one actually costs when the row is done**, per figure, and let him keep or revert it. **Built as `#layout: side`**, opt-in per entry, text 47% / drawing 53% of the content width. **What the six cost, and this is Ian's to keep or revert:** Dual-Write **49%**, Log Tailing **49%**, Invalid Message **69%**, Dead Letter **69%**, Outbox **71%**, State Change Capture **71%** — against 85–101% before. The two at 49% are wide 2021 imports fitted by width; the redrawn EIP pair hold up best | M | ✅ |

---

## §R1 — Day 1 content, in Ian's order ##

| # | slide(s) | outline anchor | the ask | size | state |
|---|---|---|---|---|---|
| **R1-1** | **#5** | `### Slide: Robust — Guaranteed Delivery` (:45) | *"'The other thing a boundary buys, and it is the cheaper of the two.' is stilted AI language, try to rewrite in my style. Broadly, try to remove AI-ism from text you generated as opposed to picked from original docs."* **Two jobs**: this line, and then a **sweep of Day 1 for prose that is ours rather than lifted**. `session-work/day1.txt` is the 2025 deck and is what "original docs" means — a line that appears there is his and stays | M | ☐ |
| **R1-2** | **#28 + #29** | `### Slide: Messaging and Events` (:301), `### Slide: Messaging vs. Eventing…` (:306) | *"On #28, I don't think this is doing enough work, it could be combined with #29. On #29, I think the comparison between Messaging and Eventing is better rendered as a table, see the original."* #28 is one sentence. Fold it in as the lead-in and **make #29 a table** | S | ✅ |
| **R1-3** | **#30** | `### Slide: Discrete vs. Series…` (:314) | *"I think Discrete vs Series would be better as a table."* Two bullets of paired attributes — they are a table pretending to be a list | S | ✅ |
| **R1-4** | **#31 + #32** | `### Slide: Message Types` (:322), `### Slide: Command / Document / Event Messages` (:327) | *"On #31, I don't think this is doing enough work and can be combined with #32."* Same shape as R1-2: #31 is one sentence naming the three, #32 defines them | S | ✅ |
| **R1-5** | **#41** | `### Slide: The Message Pump` (:419) | *"this was once visual, I think that works better than the text."* **It was**: 2025 deck slide 58 draws *Get → Translate → Dispatch → Handle* with the four error routes hanging off it (`session-work/day1.txt`). **A new figure**, and the error-routing prose becomes its labels | M | ☐ |
| **R1-6** | **#42** | `### Slide: Translate and Dispatch` (:433) | *"again this was once visual, I think it works better separate from #41 but needs to be visual."* 2025 deck slide 59 — the same four-stage pump with **Message Mapper Registry** and **Handler Registry** hanging off Translate and Dispatch. A second figure, deliberately **not** merged with R1-5's | M | ☐ |
| **R1-7** | **#47 → three slides** | `### Slide: Competing Consumers` (:494) | *"the split between how this works in streams and queues is full of AI-ism and badly described. We want three things."* **(a)** a general statement, and Ian wrote it: *"If the Rate of Arrival of messages (RoA) exceeds the Rate of Consumption (RoC) your channel will back up and the age of any message in the channel will increase. At some point the time a message waits in the channel will become unacceptable. You solve this problem by competing consumers, but the implementation differs between streams and queues."* **(b)** a queue slide with a diagram — *"locking (this item is being processed) and read-past, pick up the next item, but sacrifice ordering."* **(c)** a stream slide with a diagram — *"we partition by a key, and each partition has a consumer, and we retain ordering, but have no delay or read-past."* **⚑ Do R1-15 (§4.5) and this row together** — they are the same repetition seen from two ends | L | ✅ |
| **R1-8** | **#56 + #57** | `### Slide: The Dual-Write Problem` (:607) | *"shrink the diagram on #57 and combine with the text. It's too weird to read the words, then show the diagram here."* Needs **R0-5** | S | ✅ |
| **R1-9** | **#58 + #59** | `### Slide: Outbox` (:620) | *"move the text lines 'But look at what we just bought:' / 'We can fail after the send and before marking it Sent.' / 'The sweeper then finds it Pending and sends it again.' to presenter notes. Put the text on the left, and move the diagram from #59 here and shrink it… If needed move more of the text to notes to fit."* Needs **R0-5**. **⚑ The presenter note already says the duplicate is the question the Inbox answers** — check the move does not say it twice | S | ✅ |
| **R1-10** | **#60 + #61** | `### Slide: Log Tailing…` (:644) | *"move the diagram to the right on #60, text to the left on #60, shrink diagram, move some text to notes if needed. Split is weird."* Needs **R0-5**. The overflow half of this row is **R0-3** | S | ✅ |
| **R1-11** | **#62** | `### Slide: State Change Capture` (:674) | *"follow the changes on #58 and #60 and put diagram on the right (shrink) and text on left."* Already a single slide; it is the *arrangement* that changes. Needs **R0-5** | S | ✅ |
| **R1-12** | **#63 → two slides** | `### Slide: When the Handler Fails — Ack and Nack` (:686) | *"Split into two slides."* First keeps everything **through** *"…at-least-once stops being a slogan on the consumer side."* Second starts at *"But not acking is not a strategy, it is a question"* — **and is rewritten**, because Ian says the framing is wrong: *"On not ack we have options, not questions: **Requeue** ⇒ put this message back on the queue; **Reject** ⇒ don't process this message, drop it (either skip on a stream or delete on a queue). On a requeue we tend to set a policy for how many times, exceed that and you go to the DLQ. On a reject, if it is a badly formed message it goes to an invalid message queue. By policy we might send a well-formed message to the DLQ immediately on a reject."* **⚑ This changes what the next three slides are the answers to** — the `#note:` at :711 and the presenter note both say "three questions" and both need the same edit | M | ✅ |
| **R1-13** | **#64 + #65** | `### Slide: Invalid Message Channel` (:721) | *"Shrink the diagram, combine into one slide."* Needs **R0-5** | S | ✅ |
| **R1-14** | **#66, #67** | `### Slide: Requeue with Delay` (:739) | *"On #67, we should be clear that this is a queue, not a stream. On #66 we should note that only queues support requeue with delay via their locking mechanism. A stream must use another method to put a message onto the stream again, after a delay, such as a scheduler, and doing so will de-order the stream."* **The `#note:` at :752 already says "say queue here"** — Ian wants it *on the slide*, not in a build note. **New content**, and it is the stream half | S | ✅ |
| **R1-15** | **#68 + #69** | `### Slide: Dead Letter Channel` (:757) | *"Shrink the diagram, combine into one slide."* Needs **R0-5** | S | ✅ |
| **R1-16** | **#72** | `### Slide: What Your Broker Actually Gives You` (:794) | The overflow. **R0-3** — no content edit expected. Verify after R0-2 | — | ☐ |
| **R1-17** | **§4.5, all of it** | `## 4.5 Queues and Streams` (:837) | *"there is repetition here, between the competing consumers and error discussions in slides above. Perhaps this is not a separate section, but needs to be combined into the material above as 'how this works for queues, how this works for streams', otherwise this will flow badly on the day by repeating ideas."* **The largest row in the file.** §4.5 is 18 slides and 11 figures; the overlap is with §4.3's *Competing Consumers* (R1-7) and §4.4's error slides (R1-12 … R1-15). **⚑ Structural — re-run the cross-reference sweep after it** (`BACKLOG.md` B6), and **`exercises/Quick-Start-Kafka.pptx` is wired to land in §4.5** (the `#note:` at :841), so a dissolved §4.5 has to say where the Kafka exercise goes. **Put the proposed shape to Ian before cutting** | L | ✅ |
| **R1-18** | **#94–#96** | `### Slide: Messaging Participants` (:978), `### Slide: Messaging or Eventing?` (:996) | *"This repeats the conversation from earlier, around #29. Again, let's combine into the earlier conversation."* #96's table **is** #29's table. Note the section goal at :975 and the figure `conversation-messaging-or-eventing.png` — decide what survives where | M | ✅ |
| **R1-19** | **#99–#111** | `### Slide: In-Only…` (:1029) through `### Slide: Choosing an Exchange Pattern` (:1181) | *"On #99-101 we describe three of the patterns. On #103 to #109 we redescribe the patterns. **We miss a whole pattern.** After the table, we should talk about each pattern, with all the information for it, and then at the end summarize error flows #102, and choices #110 and #111."* The missing one is **Out-In** — #99–101 are In-Only, Out-Only, In-Out. **Target shape:** the 2×2 (#97/98), then **one block per pattern with everything about it folded in** — In-Out absorbs #103 (timeout), #105 (command or query), #107 (blocking); Out-Only absorbs #106 (subscribe-notify); Out-In absorbs #108/109 — then **Faults, by Pattern** (#102), then **Choosing** (#110/111) | L | ✅ |
| **R1-20** | **#120** | `### Slide: Get It On Demand — REST/RPC` (:1298) | *"we are missing a diagram here, and we have diagrams for content enricher, let's put the diagram back."* A new `eip_figures` drawing — the consumer calling back for the data it was not sent | M | ✅ |
| **R1-21** | **#123** | `### Slide: Get It In Advance — ECST…` (:1333) | *"we are missing a diagram here and we have a diagram for content enricher, let's put the diagram back."* A second new drawing — the state arriving **on** the event, so there is no call back | M | ✅ |

---

## §R2 — the Day 2 pass ##

**Ian: *"Some of these points (such as text splitting and AI-ism) will apply to day two, but let's do
Day One first, then make a pass at Day Two for these issues before I manually review."*** So §R2
starts only when §R1 is closed, and it is deliberately **narrow** — it is not a second full review.

| # | the ask | size | state |
|---|---|---|---|
| **R2-1** | **Text splitting** — R0-1, R0-2 and R0-4 are builder changes and land on Day 2 for free. **Verify, do not assume**: render Day 2 and look, and re-check the callouts in particular, because that is where every Day 1 overflow was | S | ☐ |
| **R2-2** | **AI-ism** — the same sweep as R1-1, over `outlines/DayTwo.md`. `session-work/day2.txt` is the 2025 deck and is the test of what is Ian's | M | ☐ |
| **R2-3** | **Whatever R0-5 settles** — Day 2 carries 72 placed figures and 47 split entries, so if text-left/figure-right is right for Day 1 it is a much bigger question on Day 2. **Ask; do not roll it out** | — | ☐ |

---

## What this review did NOT ask for ##

Recorded so it does not get done by accident, and so the next session does not re-derive it.

- **Nothing about the 2021 imports' register** (`BACKLOG.md` G1). Five of them are the figures in
  R1-8 … R1-11 and R1-14, and Ian's instruction there is to **shrink and reposition**, not redraw.
  G1 stays scoped-and-not-started.
- **Nothing about `styles.md`.** The palette, the type scale and the two registers are not in scope.
- **No new sections and no cuts to §1, §2, §3, §6.1 or §6.3** beyond R1-1's prose sweep.
