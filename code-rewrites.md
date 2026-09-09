# Code exercises — a brief for whoever picks this up #

**This is a hand-off, not a plan.** It is everything the deck-redevelopment work learned about the
coding exercises while deliberately not touching them, written down so a fresh agent does not have to
rediscover it. **Ian holds the missing half** — the exercise code itself, which is not in this repo —
and will supply it along with the old code locations.

**Scope: the Day 1 coding exercises, and the timing question they dominate.** Everything else about
this course — the two decks, `outlines/`, the figures, the handouts, the Paper Flow exercise — is a
separate, active workstream tracked in `BACKLOG.md` and `REDEVELOPMENT-PLAN.md`. **Do not edit
`outlines/`, `tools/`, `resources/` or `styles.md` from this brief** without saying so first; those
are live and someone else is working in them.

**Ian settled the split himself:** *"The coding exercises are Day One. They likely get a rework and the
coding changes **are** the separate work item."* And earlier: *"Day One includes some coding exercises
for RMQ and Kafka. Those are a separate task. But for Day Two, please do work on these"* — which is why
the Paper Flow exercise is built and closed while none of this is.

---

## 1. What is in this repo ##

| what | where | state |
|---|---|---|
| Precursor decks | `exercises/Introduction-To-Exercises.pptx`, `Quick-Start-RMQ.pptx`, `Quick-Start-Kafka.pptx` | 2024 vintage; **Intro and RMQ were refreshed Oct 2025**, Kafka not since Oct 2024 |
| Pattern exercise decks | `exercises/{point-to-point,datatype-channel,invalid-message-channel,pipes-and-filters}-exercise.pptx`, `consumers.pptx` | all **June 2024**, untouched by the redevelopment |
| An orphan | `exercises/Quick-Start-SNS-SQS.pptx` | referenced by **neither** README — see §4 |
| Reading order | `exercises/README DAY ONE.md`, `README DAY TWO.md` | **the entry point for delegates**, and both have broken links — see §4 |
| Pattern videos | `videos/*.mp4`, 20 files | mirrored from GitHub; one has a typo in its own filename |
| Prose scripts | `script/Patterns/*.md`, `script/RMQ/*.md` | near-1:1 with the pattern slides. **`script/Patterns/` is also earmarked as the body of a routing handout** (plan §10) — check with that work before rewriting it |
| Docker | `dockercomposefiles/docker-compose-{rmq,kafka}.yaml` | |

**Day 2's code sections live in `README DAY TWO.md` and were deliberately left alone.** That file also
carries the **Paper Flow** section, which is finished, in scope for the other workstream, and **must not
be disturbed** — it is the top block of the file and is clearly marked.

## 2. What is NOT in this repo — Ian supplies it ##

**The exercise code.** From `Introduction-To-Exercises.pptx`, which is the only place any of this is
written down:

- The exercises are **in GitHub**, with the videos.
- **Five languages: C#, Go, Java, JavaScript, Python.**
- **The master branch is blank; solutions and exercises are separate branches.** A delegate works on the
  exercise branch with solutions open in a browser as a hint.
- Each exercise is **code with holes in it**, marked by comments saying what to implement.
- There is *"a simple Messaging Gateway that mediates access to RMQ"* and a console app for sending.
- Deliberately **not production code** — *"they omit most of the error handling production code would
  need; they trade maintainability for focus"*.
- RMQ is the middleware *"because it does not require cloud accounts"*; run via the compose file, with
  the management console open to watch what happens.

**Five languages is the single biggest fact in this brief.** Any change to an exercise is five changes,
and any new exercise is five implementations. Cost every proposal that way before offering it.

## 3. The gap that matters — §4.4 has no exercise ##

**The deck was rebuilt around a section the exercises predate.** Day 1 §4 is now a *build order*, and
**§4.4 Guaranteed Delivery is new** (plan §11, D1-8). It teaches: the dual-write problem, Outbox, Log
Tailing / CDC, State Change Capture, ack and nack when the handler fails, Invalid Message Channel,
Requeue with Delay, Dead Letter Channel, Inbox / idempotency, and what your broker actually gives you.

**`README DAY ONE.md` offers exercises for:** Point-to-Point, Datatype Channel, Invalid Message Channel,
Polling/Event Consumer, and Pipes and Filters (optional). **That is one slide of §4.4 out of eleven.**
Outbox, Inbox, CDC and ack/nack — the spine of the afternoon — have no exercise at all.

**And the Kafka slide makes a promise about it.** Day 1 §4.5's *Exercise Material — Introduction to
Kafka* now reads:

> Then the exercises: **take the reliability you built on a queue and get the same guarantees on a
> stream.** Nothing you relied on in §4.4 is native here.

That sentence was written for the rebuilt deck. **Whether any current exercise does that is unknown and
untested** — the exercise decks are all June 2024 and §4.4 did not exist then. **Check it first**: it is
the cheapest way to find out how far the code has drifted from what the room is now told it will do.

## 4. Broken references — checked against the filesystem, not guessed ##

Run on 2026-09-09. These are real, and they are what a delegate hits first.

| README | says | actually | |
|---|---|---|---|
| Day 1 | `Quick Start Rabbit MQ (RMQ).pptx` | `Quick-Start-RMQ.pptx` | |
| Day 1 | `datatype-exercise.pptx` | `datatype-channel-exercise.pptx` | |
| Day 1 | `invalid-message-channel.pptx` | `invalid-message-channel-exercise.pptx` | |
| Day 1 | `publish-subscribe-channel.mp4` | `publish-subcribe-channel.mp4` | **the typo is in the video's own filename** |
| Day 2 | `Quick Start Rabbit Kafka.pptx` | `Quick-Start-Kafka.pptx` | the name is also garbled — "Rabbit Kafka" |
| Day 2 | `conversations.pptx`, for the ECST exercise | **no such file.** `consumers.pptx` exists and is referenced by no README | **ask Ian** — these may or may not be the same deck |

`pub-sub-stream-exercise.pptx` and `request-reply-exercise.pptx` are also absent but are marked
`[Not Available]` in the README, so those are **expected**, not defects.

**Orphaned:** `Quick-Start-SNS-SQS.pptx` is in `exercises/` and mentioned by neither README. Either it
is dead and should go, or SNS/SQS is a variant delivery that has lost its wiring. **Ask.**

## 5. Timing — the exercises dominate every other lever ##

**Moved here from the deck backlog on Ian's instruction, because it is this work's to answer.**

| | |
|---|---|
| Teaching day | 09:00–17:00, 1h lunch, 2 × 15m breaks → **390 min** |
| Day 1 exercises | RMQ (§4.2) + Kafka (§4.5) ≈ **160 min** — **Ian's estimate, never measured** |
| Day 1 total | **419 of 390** — over by 29 |
| Day 2 total | **354 of 390** — 36 spare |
| The pair | **773 of 780.** Ian closed the timing pass: Day 1 running into the top of Day 2 is how the course already runs |

**⚑ 160 minutes is 41% of Day 1 and rests on nothing.** The lecture model (`session-work/timing.py`) is
calibrated against one observed section and is trusted to ±20%; the exercise figure is not modelled at
all. **Measuring it, or changing it, moves more than every deck-side option combined:**

| lever | worth |
|---|---:|
| **The exercise blocks** | **160 min, ±unknown** |
| T-2 … T-5, four deck cuts, parked | ~24 min total |

So: **T-2 … T-5 stay parked until the exercise duration is known.** They are recorded in plan §11 and
should not be worked as timing fixes — cutting 24 minutes of teaching to pay for an estimate nobody has
checked is the wrong order. If the rewrite shortens the exercises at all, Day 1's overrun disappears and
they are moot; if it lengthens them, four small merges will not save it and the conversation is a
different one.

**Do this on the next delivery, whatever else happens: time the two blocks.** It is the single
highest-value action available anywhere in this project, and it costs a stopwatch.

## 6. What is already settled, and what is not ##

**Settled by Ian:**

- The coding exercises are **Day 1**, and their rework is **this separate work item**.
- Day 2's code sections in `README DAY TWO.md` are **out of the deck workstream's scope**, left untouched.
- RMQ is the teaching middleware, for the no-cloud-account reason.
- The Paper Flow exercise is **not** code, is finished, and is not this brief's business.

**Open, and needs Ian:**

1. **Where is the code?** Repo, branches, and whether the five languages are still all maintained.
2. **Is `consumers.pptx` the missing `conversations.pptx`,** or are they two different things?
3. **Is `Quick-Start-SNS-SQS.pptx` alive?**
4. **Does the rework extend to §4.4** — new exercises for Outbox / Inbox / ack-nack / CDC — or is it a
   refresh of what exists? Five languages makes that a large difference.
5. **Do the videos get re-recorded?** Twenty of them, and they are named on the slides.

## 7. Rules that carry over ##

These come from the deck workstream, where each cost real rework. They apply here too.

1. **Test the assumption before reporting a blocker.** This project has already made **four** wrong
   "it's missing / it's impossible" reports to Ian, every one a stale note nobody retested. Check the
   date on a claim and the state of the tooling before repeating it. Two minutes of proving beats a
   round trip.
2. **A reference with a name on it is not proof the thing exists.** Six of the README's links are
   broken and read as fine — see §4. Check the file opens.
3. **Cost it in five languages.** See §2.
4. **The deck and the exercises must move together.** The slides name the exercise decks and videos by
   title, and the outlines' presenter notes describe what the exercises do. **If a rename or a
   restructure lands here, `outlines/DayOne.md` needs the matching edit** — raise it with the deck
   workstream rather than editing the outlines from this brief.
5. **Never put provenance in an outline.** Presenter notes become the deck's speaker notes and ship to
   whoever presents. Reasoning belongs in a commit message.

---

*Written 2026-09-09 from the deck-redevelopment work, at commit `d43034f`. Nothing in `exercises/` or
`videos/` was changed to produce it — this is what was observed, not what was done.*
