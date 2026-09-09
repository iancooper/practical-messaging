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

## 3. The exercise list Ian wants — settled 2026-09-09 ##

> *"My intent is to reduce the number of exercises. Post agentic engineering, it's less valuable to
> walk you step by step through creating channels, etc."*

| # | exercise | what it builds |
|---|---|---|
| **1** | **Message Pump** | a producer and a consumer, with a **message pump** on the consumer. Show the **command handler** and the **message mapper** |
| **2** | **Invalid messages** | add **DLQ** support to the pump — use RMQ's built-in — for a message rejected *n* times, or a failed mapping |
| **3** | **RMQ → Kafka** | make the consumer also a **Kafka producer**, and add a **Kafka consumer**: a command sent to RMQ results in a Kafka event |
| **4** | *(optional)* **Lookup** | a Kafka producer and consumer fill a **lookup** used by the command handler |

**Ian: *"We will call out the relevant patterns, channel, message etc"*** — so Point-to-Point,
Publish-Subscribe, Datatype Channel, Message Endpoint, Messaging Gateway, Competing Consumers and
Pipes and Filters keep their slides and lose their exercises. **The deck does not shrink; the code
does.**

**⚑ Record the rationale, not just the list.** *Post agentic engineering* is the reason, and it is
exactly the kind of reason that gets lost and then someone helpfully re-adds a step-by-step channel
exercise. Filling in marked-out code was worth 45 minutes when typing it was the slow part. It is not
any more.

### 3.1 What this fixes, checked against the outlines ###

**⚑ Exercise 1 is §4.3 made real, one term at a time.** Every noun in it is taught in Day 1 §4.3
*The Message Pump*, in that order, and this was checked against `outlines/DayOne.md` rather than
assumed:

| exercise 1 asks for | the deck teaches it at |
|---|---|
| the pump | §4.3 *The Message Pump* — *"Get → Translate → Dispatch → Handle"* |
| the **message mapper** | §4.3 *Translate and Dispatch* — *"a **Message Mapper Registry** and a **Handler Registry**"*; *"a Message Mapper converts domain objects to/from messages"* |
| the **command handler** | §4.3 *Service Activator* — *"the **handler** is your code… your handler is not a message handler, it is a method that happens to be called by one"* |
| producer and consumer together | §4.3 *Messaging Gateway* — *"endpoint, pump, mapper, registries — is the messaging gateway"* |

**Exercise 2 closes most of the §4.4 gap.** Day 1 §4.4 *Guaranteed Delivery* is **new** in the rebuilt
deck (D1-8) and, under the old list, eleven slides had one exercise between them. Exercise 2 covers
*When the Handler Fails — Ack and Nack*, *Invalid Message Channel*, *Requeue with Delay* and *Dead
Letter Channel* — the whole consumer-side half.

**And Pipes and Filters coming off the list agrees with a cut already made.** Day 1 §4.6 *Pipelines*
was cut to a routing handout (plan §10), so `pipes-and-filters-exercise.pptx` had already lost the
section it belonged to. The new list and the deck now say the same thing.

### 3.2 ⚑ What it changes about Day 1 — one real misalignment ###

**The RMQ exercise slot is in the wrong place for these exercises, and was in the right place for the
old ones.** Day 1 has exactly two exercise pointer slides:

| slide | sits at | wanted by |
|---|---|---|
| *Exercise Material — Introduction & RMQ* | **end of §4.2 Sending and Receiving** | old exercises: Point-to-Point and Datatype Channel, which **are** §4.2 material |
| *Exercise Material — Introduction to Kafka* | **end of §4.5 Queues and Streams** | exercise 3, which needs all of §4.5 — **still correct** |

Under the new list, **exercise 1 needs §4.3 and exercise 2 needs §4.4** — both of which come *after*
the slot that introduces them. As it stands the deck would hand out an exercise asking delegates to
build a message pump one sub-topic before it teaches what a message pump is.

**The recommendation is three slots, not two**, and it costs two pointer slides (~2 min in the timing
model, which rates a pointer at 1.0):

| after | exercise | why there |
|---|---|---|
| §4.3 The Message Pump | **1** | every term in it has just been taught |
| §4.4 Guaranteed Delivery | **2** | ack / nack / requeue / DLQ are §4.4's own vocabulary |
| §4.5 Queues and Streams | **3** *(+ 4 as take-home)* | unchanged from today |

**The alternative — one block after §4.4 — makes §4.1 → §4.4 about 93 minutes of continuous lecture
before anyone touches a keyboard.** Splitting it gives 41 minutes, hands on, 38 minutes, hands on.
That is the trade, and it is Ian's to call; the precursor material (*Introduction to Exercises*,
*Quick Start RMQ*) still wants handing out at §4.2, because the Quick Start is about AMQP primitives
and that is what §4.2 teaches.

**⚑ Nothing has been changed in `outlines/` for this.** The deck should not chase a rework that has
not landed. When the list is built, the edit is: move / split the §4.2 pointer slide, and re-check
its presenter notes.

### 3.3 Three connections worth making deliberately ###

1. **⚑ Exercise 3 *is* the dual-write problem.** A handler that consumes a command from RMQ and
   produces an event to Kafka is the exact scenario §4.4 spends four slides on — *The Dual-Write
   Problem*, *Outbox*, *Log Tailing*, *State Change Capture*. Those four are the half of §4.4 that
   **still has no exercise** after exercise 2. So either the exercise notes say plainly *"you have
   just built the thing §4.4 warned you about"*, or exercise 3 gains a step that makes it fail and
   then fixes it with an outbox. **Doing neither means the deck teaches a problem the exercises then
   quietly commit.**
2. **The §4.5 slide makes a promise exercise 3 only half keeps.** It reads: *"take the reliability you
   built on a queue and get the same guarantees on a stream. **Nothing you relied on in §4.4 is native
   here.**"* Exercise 3 as described has them *produce* to Kafka; it does not obviously have them
   discover that requeue and DLQ are not there. Either add the step, or soften the sentence — but
   they should agree.
3. **Exercise 4 is a three-way callback, and it is optional, so nothing may depend on it.** A lookup
   filled by a Kafka consumer and read by the handler is Day 1 §6.2 *Reference Data* (on-demand vs
   in-advance), Day 2 §Flow *FBP — Where Do Lookups Live?* (the `flow-lookup-asking` /
   `flow-lookup-table` pair), **and** the Paper Flow exercise's Catalogue Maker. If it runs, Day 2 can
   say *"you built this yesterday"*. **If it is optional, no slide may assume it happened.**

### 3.4 What falls out of `exercises/` ###

| file | under the new list |
|---|---|
| `point-to-point-exercise.pptx` | dead |
| `datatype-channel-exercise.pptx` | dead — though the **datatype channel is where the mapper bites**, so exercise 1 can call it out |
| `pipes-and-filters-exercise.pptx` | dead; its section was already cut to a handout |
| `consumers.pptx` | folds into exercise 1 — it was the Polling/Event Consumer exercise |
| `invalid-message-channel-exercise.pptx` | **rewritten** as exercise 2 |
| `Introduction-To-Exercises.pptx` | **kept, and needs edits** — see below |
| `Quick-Start-RMQ.pptx`, `Quick-Start-Kafka.pptx` | kept |
| `Quick-Start-SNS-SQS.pptx` | still orphaned — see §4 |

**The video loop breaks, and one slide says so out loud.** `Introduction-To-Exercises.pptx` slide 6
is *"Watch a messaging patterns video / If there is an associated exercise / Do the exercise /
Repeat"*. With twenty videos and four exercises that loop is gone. The videos are still worth having
as reference — but that slide, and the *Exercises* and *Steps* slides around it, now describe a
course that does not exist.

### 3.5 ⚑ The open question this list raises, and it is the big one ###

**Does the fill-in-the-blanks format survive?** Today an exercise is *"code that is missing, replaced
by comments; you provide the appropriate code, as indicated by the comments"*, on a branch, in five
languages. Ian's four items do not read like that — *"write a producer and consumer"*, *"add support
for DLQ to the pump"* are **whole-component tasks**, which is what *post agentic engineering* implies.

That is not a smaller version of the same repo, it is a different shape of one, and it decides
everything else: how many branches, whether solutions still exist as a parallel branch, and **whether
five languages is still the right bet or the moment to cut**. Settle it before touching code.

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

**⚑ The new list changes the shape, not obviously the total.** Five or six small step-by-step
exercises become **three substantial ones and an optional fourth** — and exercise 1 alone (producer,
consumer, pump, handler, mapper) is larger than any exercise on the old list. Fewer exercises is not
automatically less time. What it does change is **granularity**: with three exercises there are three
natural stopping points instead of six, which makes the block harder to cut short if the morning
overruns. Whoever runs it next should time **each exercise**, not just the two blocks.

## 6. What is already settled, and what is not ##

**Settled by Ian:**

- The coding exercises are **Day 1**, and their rework is **this separate work item**.
- Day 2's code sections in `README DAY TWO.md` are **out of the deck workstream's scope**, left untouched.
- RMQ is the teaching middleware, for the no-cloud-account reason.
- The Paper Flow exercise is **not** code, is finished, and is not this brief's business.

- **The exercise list**, 2026-09-09 — §3. Four exercises, one optional; *post agentic engineering*
  is the reason; the dropped patterns keep their slides.

**Open, and needs Ian:**

1. **Where is the code?** Repo, branches, and whether the five languages are still all maintained.
2. **⚑ Does the fill-in-the-blanks format survive?** §3.5. This is the one that decides the repo's
   shape, and therefore the size of everything else.
3. **Three slots or one block?** §3.2 — three keeps the rhythm, one block puts ~93 minutes of lecture
   in front of the first keyboard. His call, and it is a deck edit either way.
4. **Does exercise 3 carry the outbox**, or just name it? §3.3 item 1 — as described it *is* the
   dual-write scenario, and that half of §4.4 has no exercise otherwise.
5. **Do the videos get re-recorded, or retired to reference?** Twenty of them, named on the slides,
   and the "watch a video, do the exercise, repeat" loop no longer exists.
6. **Is `consumers.pptx` the missing `conversations.pptx`,** or are they two different things?
7. **Is `Quick-Start-SNS-SQS.pptx` alive?**

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
