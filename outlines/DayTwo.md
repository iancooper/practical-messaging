# Practical Messaging — Day Two

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day Two moves from the single message to the **flow**. It opens on message design — fat vs. skinny messages and reference data, how state propagates through delta and snapshot events, and how a published message is versioned safely. It then shifts to flow — why call-and-return breaks at service scale, how paper offices ran without it, dataflow and flow-based programming, and reactive architectures — puts delegates through a **paper-modelling exercise**, and closes on process automation — BPMN, orchestration vs. choreography, durable execution, and workflow engines.

*Message-exchange patterns and fault repair now live on Day One, in `## Conversations`. Managing Asynchronous APIs is a takeaway handout; only its versioning material is taught, in `## Versioning` below.*

---

## Fat and Skinny Messages

*Sub-topic of **Designing Messages** — what goes in a message, how the receiver gets the rest, and what
happens when it changes.*

**Section goal:** given a message to design, choose what to put in it — and know how the receiver gets
whatever you left out, and what that costs in availability.

### Slide: What Goes in a Message?

The decision is **per field, not per message**. For every piece of data the provider needs in order to
act, there are three choices:

- **Inline it** — put the value in the message.
- **Reference it** — put an id in the message; the provider looks the data up.
- **Replicate it** — the provider already holds a copy, kept fresh out-of-band.

▎ Designing a message is a normalisation problem.

- A **fat** message is fully denormalised. A **skinny** message is fully normalised. Neither extreme is usually right.
- The rest of this section is the rule that decides per field, and the price of each answer.

Presenter notes: Delegates already have this mental model from database design — they have just never applied it to messages. Normalise by default; denormalise deliberately for the lookups that hurt; and own the staleness you have created. That is the whole section in three sentences.

### Slide: Fat Message

With a **Fat Message**, the requestor sends across all the *external* information a provider may need to perform the operation.

- The requestor provides all external information the provider needs to act.
- The resulting document message may be large (a **Claim Check** can help).
- **Example.** *Order Fulfilment → Courier Assignment:* the request provides delivery and pickup address, size, weights, etc. of the order.

**What it buys you:** the provider needs nobody else in order to act. No lookup, no cache, no second system that has to be up.

### Slide: Fat Message — Transitive Dependencies

A purchase-order message that inlines customer and restaurant data shows the cost.

- The order data has the **lifetime of the message** — its schema changes if the purchase order changes. That is fine; it is *our* data.
- Customer data is a **transitive dependency** — its lifetime is the Customer's. A Customer schema change may force a message change.
- Restaurant data is likewise a transitive dependency on the Restaurant schema.

▎ Inline someone else's data and you have inherited their release schedule.

Presenter notes: This is the slide that motivates the rule two slides later. The message did not just get bigger — it acquired two more reasons to change, and both are owned by other teams.

### Slide: Skinny Message

With a **Skinny Message**, the requestor provides only information unique to the event, and assumes the provider has, or can obtain, the other information.

- The resulting notification message is normally skinny.
- **Example.** *Order Notification → Courier Assignment:* notifies that there is an order, inlining only order-unique data — not reference data like weights or addresses. Courier Assignment must source the missing information from elsewhere.

**What it costs you:** the provider can no longer act alone. Something else has to supply the rest — which is the next sub-topic.

### Slide: The Lifetime Rule

▎ If the data does not share the message's lifetime, put an id in the message, not the data.

The purchase-order message carries `CustomerId` and `RestaurantId` instead of inlined data.

- Data that shares the message's lifetime → **inline it**.
- Data with its own lifetime → **reference it** by id; assume the requestor obtains the data out-of-band.
- These ids must be looked up with other providers (Customer, Restaurant).

**Then be pragmatic.** Exactly as with a database, you may **denormalise** — inline a common lookup so you do not pay for it on every message.

- Do it for the lookups that actually hurt, not by default.
- The moment you copy someone else's data into your message you own a **stale copy**, and you have taken on their schema.
- The rule is the default; a denormalisation is a decision you should be able to justify.

Presenter notes: Just like a Db, we allow optimisation by inlining some common lookups — so "it depends", and be pragmatic, *on top of the rule*. The rule stops the choice being arbitrary; the pragmatism stops it being dogma. Ask which lookups in their own systems would justify it.

---

## Reference Data

*How the provider gets what the message did not carry.*

### Slide: Reference Data

The requestor assumes **Provider A** has a local cache of data from **Provider B** that it can use to look up the identifiers in a skinny message.

- Data that leaves Provider B via an API is **Reference Data**: immutable, versioned, stale.
- Immutable and versioned because a copy that can change shape under its holder cannot be cached safely.
- It can be cached locally to Provider A to avoid frequent lookups (`cache lookup()`).

### Slide: Get It On Demand — REST/RPC

On a cache miss, Provider A fetches the data from Provider B synchronously.

- Look up missing data in the local reference-data cache (may specify identity *and* version).
- On a miss, request from Provider B and store it in the cache (`request()` / `reply()` / `cache write()`).

**What it costs you**

- On a hit: **availability over consistency** — you serve possibly-stale data and stay up.
- On a miss: **consistency over availability** — and A's uptime becomes the uptime of **A *and* B**. If B fails, A fails.

▎ A cache miss is a temporal coupling you did not plan for.

Presenter notes: This is the Day 1 argument arriving inside message design. The lookup is a synchronous call in the middle of a message flow, so availabilities multiply again — and only on the unlucky path, which is exactly what makes it hard to catch in testing.

### Slide: Get It In Advance — ECST (Event-Carried State Transfer)

Provider B pushes state changes to A ahead of time, so A rarely needs a synchronous lookup.

- The upstream provider raises a **notification** when its own entity state changes (Out-Only / pub-sub).
- The downstream provider subscribes and writes to its local cache (`cache write()`); later requests hit the cache.

**What it costs you:** **availability over consistency** — accept stale data rather than risk failure due to a partition. You are always reading a copy that is behind.

Presenter notes: ECST is the answer to the previous slide's miss path — you stop having misses. The price is that you are now running a replica of someone else's data, and replicas go stale, go wrong, and need rebuilding. Say that out loud: teams adopt ECST expecting it to be free.

### Slide: Reference Data — Worked Example

*Order Fulfilment → Courier Assignment:* the request omits the restaurant pickup address; we assume Courier Assignment obtained it from Restaurant Information.

- Look up the restaurant in the local cache by **id and version**.
- If we have the restaurant but **not that version**, apply **backpressure** and retry the order after a delay.

Presenter notes: The id-and-version lookup is the detail that makes this work. Without the version you cannot tell "I have not seen this yet" from "I have it"; with it, a missing version becomes a *wait* rather than a wrong answer. Backpressure here is the same idea they met in the reactive material.

---

## Event Shape

*What shape of event lets the receiver keep a copy — and what guarantees that buys.*

### Slide: Domain or Delta Event

An approach to Pub-Sub where the provider communicates **granular** state changes to its requestors.

- Messages are usually named as a past participle after the causing command (e.g. `BasketItemRemoved`, `BasketItemAdded`).
- Cannot use a **Datatype Channel** — domain events for the observable must be *ordered on the same channel* and have different schemas. This burdens the requestor to multiplex handling of the events.

### Slide: Summary or Snapshot Event

An approach to Pub-Sub where the provider communicates a **summary** of state changes.

- The message is **versioned** and contains metadata describing the cause(s) of changes; usually named after the observable (e.g. `BasketChanged`).
- *Can* use a Datatype Channel — there is just one schema for a snapshot of the observable.

### Slide: Why ECST Needs Snapshots

You cannot replicate someone else's state from deltas unless you receive **every one of them, in order**.

- With **Domain/Delta events**, a missed or reordered message leaves the replica permanently wrong — and nothing in the stream tells you. You must apply them all, you can only use blocking retry, and you cannot shed load.
- With **Summary/Snapshot events**, each message is complete in itself. A missed one is repaired by the next one to arrive.

▎ Choose the delta and you have chosen strict ordering. Choose the snapshot and you have bought it back.

Presenter notes: This is the join between the two halves of the section. ECST is only tolerable because of the snapshot event — it is what makes the next two slides possible at all. The rule: publish complete new versions rather than deltas.

### Slide: If Later, Stream

**If Later** lets us use a versioned Summary Event to ignore ordering errors.

- Consumer reads v1 of 12345 and handles it; reads v3 and applies it (later than v1); reads v2 and **discards** it (earlier than the already-applied v3).
- Even on a stream, non-blocking retry or guaranteed delivery via an outbox can produce out-of-order messages; If-Later also lets us shed load.
- We *cannot* use If-Later with a Domain Event — those must all be applied. With Domain Events we can only use a blocking retry and cannot shed load.

#image: diagram — a stream of versioned message envelopes (12345 v1..v3) read by a consumer applying 'if later'

Presenter notes: Publish complete new versions rather than deltas, then apply "write if later" — with v0, we can write v2 even without seeing v1, because v2 is later and either overwrites or includes v1's changes; we can then safely discard v1.

### Slide: If Later, Queue

If-Later also lets messages be processed out-of-order with a queue and competing consumers.

- One consumer expects/writes v1 while another writes v2; **read-past** lets them proceed.
- A queue normally processes messages (not events), so this applies only where we use a queue.
- If a message *must* be ordered (e.g. a series of commands), use requeue-with-delay or a sequencer to re-order.

#image: diagram — a queue of versioned message envelopes with two competing consumers and read-past

### Slide: Public and Private Providers

An approach to Pub-Sub where a **public** provider communicates with collaborators in other domains via a **Summary Event** aggregated from the domain events of **private** providers.

- Private providers raise granular `event()`s.
- The public provider republishes a versioned `summary()` with metadata describing the cause(s) of changes.

Presenter notes: This is how both event shapes coexist — deltas inside a domain, where ordering is cheap and the consumers are yours; snapshots across the boundary, where neither is true. It is the same public/private split as an Open Host Service.

---

## Versioning

*What happens when the message changes.*

### Slide: Versioning — Postel's Law

▎ Be strict when sending and tolerant when receiving.

Robustness Principle (Postel's Law) — Jon Postel, RFC 1958: implementations must follow specs precisely when sending, and tolerate faulty input from the network.

### Slide: Additive Change

Adding fields (e.g. `latitude`/`longitude`, not required) is non-breaking — and it has to work from both ends:

- **New message, old consumer** — a **Tolerant Reader** ignores new fields it doesn't understand.
- **Old message, new consumer** — the consumer **defaults the missing fields** (Default Latitude: 0, Default Longitude: 0).
- The added fields must be *not required*. Add new non-nullable fields with a **default value**, as you would a new DB column.

Presenter notes: A general rule — *adding* things does not cause a versioning conflict, as long as a new version is convertible from an old one. When old versions are read, upcast them to the latest before handling, so a handler only ever knows the latest version. Additive changes → new messages process on old consumers; new consumers default missing values from older messages; may use an Enricher.

### Slide: Breaking Change

Renaming/splitting fields (e.g. `customerName` → `firstName` + `surName`) and making new fields required is a **breaking change**.

- We might code around it, but we must *know* a required field is missing and new fields exist instead.
- For that we rely on a **version in the header** and the ability to process the new version alongside old ones, running out the old until the new replaces it.

Presenter notes: Breaking changes → create a **new message type**. Source systems may need to send original *and* new, or source the missing info via a Message Translator in the pipeline.

### Slide: What You Inlined Is What You Version

The versioning cost of a message was decided back on the first sub-topic, by what you chose to put in it.

- **Inlined data** — you re-version your message whenever *their* schema changes. A fat message inherits every transitive dependency's breaking changes.
- **Referenced data** — you version only your own fields. An id is the most stable thing you can carry.
- **Replicated data** — this is *why* reference data is immutable and versioned: a copy that changes shape under its holder cannot be cached safely.

▎ Every field you inline is a field someone else can break for you.

Presenter notes: Close the loop. The lifetime rule was never only about message size — it was about how many other teams can force you to publish a new message version. Ask the room: which of your current messages would you have to re-version if a team you have never met changed a column?

#note: the rest of the old Day 1 §Managing Asynchronous APIs — AsyncAPI, JSON Schema/Avro/Protobuf, schema registries, CloudEvents and tooling — is now the **takeaway handout**, built from the QCon London 2026 deck. Mention it here and hand it out; do not teach it.

---

## Flow and Reactive Programming

*The second section of Day Two. Four movements: **A — how you draw systems now** (call and return, at
object scale and at service scale, ending in the distributed monolith). **B — how the office did it**
(paper workflows; this is the exercise's *see one*). **C — the formalism** (dataflow, then flow-based
programming; the same flows again as a graph). **D — the name** (Reactive, which is what you have been
building since yesterday morning).*

**Section goal:** stop drawing your system as call-and-return, and start drawing it as flow — and know
what that buys.

#note: This section is **load-bearing for the Paper Flow exercise**, which runs immediately after it.
Movement B teaches the desk / in-tray / out-tray notation delegates will draw in, movement B's error
slides teach the vocabulary the failure cards use, and movement C's worked example is the third
artefact they are asked to produce. Round 0 of the exercise is a *recap* of B and C, not a first
telling — so B and C must actually tell it.

---

### Slide: Flow and Reactive Programming

Section marker.

▎ Everything in this section is one question: *what is in charge?*

---

### Slide: Object-Oriented Programming

A class has a **role** with **responsibilities**; we capture responsibilities as behaviours; we
encapsulate the data those behaviours need inside the object; roles may be inherited via dynamic
dispatch.

#image: hand-drawn OO diagram — a class with role/responsibilities, encapsulated data, inheritance via dynamic dispatch, message passing

Presenter notes: Deliberately uncontroversial — everyone in the room has this. It is here to be named, because the next three slides are about what happens when you scale it up.

### Slide: Call and Return, and the God Object

- **Call and return.** `main` is the entry point. It invokes objects, which invoke other objects and
  return to their caller. Control is passed down a stack and handed back.
- **The god object.** The danger is one object — `Cart`, usually — that controls all the others. High
  behavioural coupling: it knows the whole use case, so it changes whenever any step of the use case
  changes.

▎ Somebody has to be in charge, and in call and return it is always `main`.

#image: hand-drawn call-and-return diagram — Main invoking Cart, Restaurant, Account, Menu, Payment, Order, Delivery objects

Presenter notes: A system passes control between classes to meet a use case, via message passing — "call and return" from `main` on down. Hold the phrase *knowledge of the whole process lives in one place*; movement D and the exercise's round 4 both come back to it.

### Slide: SOA Is OO at Macro Scale

**SOA** creates OO-like components: a service has a role and responsibilities exposed as
operations, and encapsulates the data those operations need. This is the Web Services approach — OO
as an architectural principle.

- Same idea, bigger unit: role, responsibilities, encapsulated data.
- We are taking the view that **microservices are SOA 3.0** — most of the best practice still applies.

▎ "A service should represent a self-contained functionality that corresponds to a real-world business
activity." — Nicolai Josuttis, *SOA in Practice*

#image: hand-drawn service-orientation diagram — a WSDL service with endpoint, binding, operations, input/output messages

Presenter notes: SOA takes objects to a macro scale. The Josuttis quote is the standard against which the next slide fails: he says align the service with a *business activity*. The next slide shows what you get when you align it with an *entity* instead.

#note: The Josuttis quote used to sit orphaned in the middle of the paper-workflow images (old s58) and
again in Process Automation. It belongs here, where it is the yardstick for Feature Envy.

### Slide: Feature Envy — You Built a Distributed Monolith

- We expose significant **resources** and the operations you can perform on them — usually CRUD.
  Entity services: `Cart`, `Restaurant`, `Account`, `Menu`, `Payment`, `Order`, `Delivery`.
- **Feature envy.** Domain logic has to coordinate across those resources, so it ends up on the client,
  in the API gateway, or in the `Cart` service — anywhere but in the individual services.
- Because we made OO large, we reached for call and return via a `main` method at the API gateway.

▎ The gateway is `main`. You have distributed the objects and kept the god object.

#image: hand-drawn entity-services diagram — Device → API Gateway → Cart, Restaurant, Account, Menu, Payment, Order, Delivery

Presenter notes: This is the slide the movement exists for. The distributed monolith is not a failure of nerve, it is what call-and-return *becomes* when you distribute it — and it gives back exactly the independent deployability Day 1 §1 called "the whole prize". End on the deck's own question: **is there a better paradigm?** Do not answer it yet — the next slide answers it with a photograph.

#note: **Cut from here: *SOA — Faults Propagate*.** Day 1 §1 now owns fault propagation (availabilities
multiply under temporal coupling) and makes the argument better. The idea is not lost — it returns in
movement D as the thing **bulkheads** fix, which is where it does work rather than repeating Day 1.

---

### Slide: Paper Workflows

▎ "My life looked good on paper — where, in fact, almost all of it was being lived." — Martin Amis

Before computers, offices ran large distributed systems on paper. They handled concurrency, failure,
recovery and scale — and there was **no `main`**. Nobody held the whole process. Every desk did one
thing, and it did it because something arrived in its in-tray.

▎ The office was a distributed system with no god object. It worked for two hundred years.

Presenter notes: This is the answer to "is there a better paradigm?" — and the answer is older than the question. The rest of the movement is spent extracting the notation from it, because delegates are about to draw in it.

### Slide: The Frame

#image: photo — mailroom pigeonhole shelves stuffed with sorted mail and parcels
#image: photo — a worker pushing a mail-delivery cart through an office
#image: photo — an office desk with overflowing IN and OUT trays and a phone

In a mail room, **the frame** was the rack of pigeonholes: mail was sorted into it by floor, then a
worker took a cart round and delivered it.

- The frame creates **channels** you post to.
- Contents are delivered to whoever subscribes to that pigeonhole.
- The sender does not wait, and does not know who collects.

▎ That is a broker. We have been building one since Day 1.

Presenter notes: Direct callback to Day 1 §4 — channels, endpoints, the message pump. Say the words *this is a broker* out loud; the physical picture is what makes the pattern stick for people who have only ever seen it as a Docker container.

### Slide: The Desk — In-Tray, Out-Tray, File

**The notation for the rest of the day.** A desk is drawn as a box with three things:

- an **in-tray** — work that has arrived and not yet been done;
- an **out-tray** — work finished here and not yet collected;
- a **file** — what this desk knows, written down, because the clerk goes home at five.

Rules of the notation:

- A heavy vertical bar is an **organisational boundary**.
- Numbered steps show sequence. Red dashed arrows are paper moving; solid arrows are phone or fax.
- **Every hand-off goes out-tray to in-tray.** Nobody shouts across the office.

Two devices worth naming, because they are patterns you already know:

- **The order wheel.** A new order is clipped on and the wheel turned from the server's side to the
  kitchen's; completed orders turn back. Orders are made and returned **in sequence** — a queue, with
  the ordering guarantee made out of plywood.
- **The carbon-copy memo.** Writing on it creates a copy underneath. You keep a copy of everything you
  send; and you can read a file's message history to reconstruct its current state. That is the
  **outbox**, and it is event sourcing.

#image: photo — a large stack of manila file folders and papers
#image: photo — an order wheel in a restaurant kitchen
#image: photo — a multi-part carbon-copy (NCR) form pad

Presenter notes: **New slide.** The notation was previously never taught — it was demonstrated in passing across a dozen unlabelled photographs. It has to be explicit now, because delegates draw in it within the hour and the exercise's hard rule (*every hand-off through a tray*) is what makes the fracture planes visible. The out-tray-to-in-tray rule is the whole exercise in one line.

### Slide: Worked Flow — Restaurant Onboarding

**Just Paper Takeaway.** Signing up a new restaurant, as paper: the value stream first, then the flow.

- Who the desks are: Restaurant Owner, Sales Team, Fax Operator, Chef, Catalogue Maker.
- Where the organisational boundary falls.
- Every hand-off annotated *Put X in Outbox* / *Take X from Inbox*.

#image: value-stream map — restaurant onboarding  [→ resources/Restaurant Onboarding Value Stream.drawio.png]
#image: flow diagram — restaurant onboarding  [→ resources/Restaurant Onboarding.drawio.png]

Presenter notes: **This is the *see one*.** Walk it slowly — it is the diagram delegates reproduce for the hotel in round 1, and the one round 0 recaps. Point at the boundary bar and at two trays explicitly; those are the only two pieces of notation they need to start.

### Slide: Worked Flows — Order, Placement, Confirmation

The same notation across the rest of the takeaway domain, faster now the notation is known.

- **Customer Order** — the customer orders; note the order taking is phone, card machine and order pad.
- **Order Placement** — the order reaches the restaurant.
- **Order Confirmation** — the restaurant confirms back.

#image: value-stream map — order flow  [→ resources/Order Flow Value Stream.drawio.png]
#image: flow diagram — customer order  [→ resources/Customer Order.drawio.png]
#image: photo — order taking (phone / card machine / order pad)
#image: flow diagram — order placement  [→ resources/Order Placement.drawio.png]
#image: flow diagram — order confirmation  [→ resources/Order Confirmation.drawio.png]
#image: montage of the four flow diagrams together

Presenter notes: Pace changes here — one diagram at a time but briskly. Land the montage: four flows, no central coordinator, and no desk knows more than its own step.

### Slide: How Do We Deal with Errors?

Paper had failure modes, and it had answers, and they are our answers.

| what goes wrong | what the office did | what we call it |
|---|---|---|
| the request goes missing | resend the fax | retry, In-Out-Retry |
| we don't know if it arrived | if no receipt, retry sending | at-least-once |
| we need to know what we sent | make a carbon copy before you send | the **outbox** |
| we need it after we go home | file the copy | durable state |
| it arrived twice | check the file before acting | idempotency, the **inbox** |

#image: flow diagram — restaurant onboarding errors  [→ resources/Restaurant Onboarding Errors.drawio.png]
#image: screenshot — a Fax Call Log table with error status codes highlighted
#image: flow diagram — customer order errors  [→ resources/Customer Order Errors.drawio.png]
#image: flow diagram — order placement errors  [→ resources/Order Placement Errors.drawio.png]

Presenter notes: This is the **failure vocabulary the exercise's failure cards use** — deliberately the same words, so round 3 is recall and not invention. The carbon copy *is* the outbox; the resend *is* the retry. The Fax Call Log is the good bit: a real error-status table, i.e. someone had to build observability for paper too.

#note: *ACID takes place at a desk; BASE takes place across desks* is **deliberately not spent here** —
it is the punch line of round 0 of the Paper Flow exercise. Do not use it in this section.

#note: **Cut from here: *Two Axes — Discrete/Series and Skinny/Fat*.** §1 *What Goes in a Message?* and
§1 *Event Shape* now own that material and treat it properly; a recap in the middle of the paper build
interrupts the argument and serves the section goal not at all.

---

### Slide: Data Flow Programming

**Dataflow programming** conceptualises a program as a directed graph: operations are **nodes**,
connected by **arcs** through which data flows. A node performs its operation when its input data is
available — not when someone calls it.

- Nothing is in charge. There is no `main`.
- You already use one: the Unix command line. Pipes and filters.

▎ In call and return, control moves and data sits still. In dataflow, data moves and control sits still.

#image: hand-drawn dataflow graph — nodes/vertices connected by arcs, with operation and data annotations

Presenter notes: Perhaps the oldest expression of the reactive approach, and the formal version of the paper flow they have just watched. Unlike OO — where state is co-located with behaviour in the node — data *moves between* transformations along arcs. The desk is a node; the tray is an arc.

### Slide: Nodes, Ports and Firing

A node is a **black box** with **ports**.

- It is **activated** — *fired* — when a packet arrives on an input port's arc.
- It computes.
- As a black box, it reports what happened by raising an event on an **output port**, which others may
  react to.
- Generally a node is **single-threaded**. Concurrency comes from having many nodes, not from one node
  doing many things.

**Packets are just data.** No special requirements — primitive or compound values travelling between
ports.

▎ It is *reactive* because it fires in response to an event.

#image: hand-drawn diagram — a dataflow node as a black box with input/output ports (activate → process → push)
#image: hand-drawn diagram — two nodes passing data packets between ports

### Slide: Capacity, Backpressure and Node Lifetime

- **Node lifetime.** In classic dataflow a node lives from activation until it has pushed its answer.
  Push = something arrived and there is work to do. Pull = a sink asked for work.
- **Capacity.** We do not activate a node to read input if there is no space on its output. Links with
  infinite capacity exist only in theory.
- Therefore: **backpressure**. A full buffer means either slow the producer, or drop data.

#image: hand-drawn diagram — an arc/link pipe with buffers for pipelining; push/pull, synchronous/asynchronous

Presenter notes: Arcs connect nodes; buffered arcs allow asynchrony — a node can push its output onto the buffer while the downstream node is still busy, which is what enables parallelism. Throughput is then limited by the slowest node. None of this is *required* for dataflow: a synchronous, unbuffered, single-threaded pipeline is a valid dataflow program. Push is a hot source you listen to (mouse clicks); pull means nothing is generated until a sink pulls the chain. Introduce backpressure and load-shedding as the two available answers here — movement D turns them into a decision.

### Slide: Flow-Based Programming

▎ "Everything flows and nothing stays." — Heraclitus

**Flow-Based Programming (FBP)** is a subclass of dataflow. Where dataflow *may* be synchronous, FBP
always is not:

- **Always asynchronous.**
- **Multiple input ports** per component.
- **Bounded buffers**, and therefore backpressure when they fill. A component can test whether it can
  send to `out`, and decide whether to halt or ignore.
- **Node lifetime:** a component keeps running while there is work on an input queue, and **suspends**
  rather than terminates when there is none.

#image: hand-drawn FBP diagram — a component with in/out ports, an information packet, and a connector
#image: hand-drawn FBP diagram — packet lifetime and process-and-wait annotations
#image: hand-drawn FBP diagram — multiple writers on an in-port, single writer on an out-port, multiple ports

Presenter notes: Merged from three slides. The deltas from dataflow are the whole content — do not re-teach dataflow. Suspend-not-terminate is the one to dwell on: it is the message pump from Day 1 §4.3, described from the other side.

### Slide: FBP — Initial Information Packets

An **IIP** is a packet a component receives at start-up rather than from an upstream component —
configuration, or a starting value. Control packets bracket a stream into groups.

#image: hand-drawn FBP diagram — an initial information packet (iip_in) and control-packet bracketing

Presenter notes: MQTT **retained messages** are a way of emulating the IIP idea — the broker holds the last value on a topic so a late subscriber gets state immediately rather than waiting for the next publish. Same problem: how does a node that just started know anything?

### Slide: FBP — Where Do Lookups Live?

A component needs data it was not sent. Two answers, and it is the same choice as §1 *Reference Data*.

- **Ask for it.** Add a lookup port: query out, pause, response in. The component stops until the answer
  comes back — **the walk of shame**. On-demand, and now you are temporally coupled to whoever answers.
- **Build it in advance.** A **Build Lookup** node listens to the stream that owns the data and
  maintains a table the working component reads locally. In-advance, and now you own a stale copy.

▎ Same decision as reference data, drawn as a graph: fetch it when you need it, or hold a copy that
might be wrong.

#image: hand-drawn FBP diagram — components A and B; does A need data from another node?
#image: hand-drawn FBP diagram — components A and B with lookup ports (query / pause / response) — the 'walk of shame'
#image: hand-drawn FBP diagram — a 'Build Lookup' node listening to A, pre-caching a lookup table for B

Presenter notes: Promoted out of the old *FBP — Capacity* slide, where three substantive diagrams were buried under a heading about buffers. This is the direct callback to Day 2 §1 *Reference Data* — on-demand versus in-advance, and the CAP cost of each. Delegates met the decision in prose yesterday morning and in a picture now.

### Slide: Worked Example — the Fax Workflow in FBP

**The same flows you have just seen on paper, drawn as a graph.** Request/response with an external
participant who is a fax machine.

- **Storage.** A component takes work from the `request_details` port but cannot forward to
  `restaurant_details` without an answer from `fax_in` — so we store the workflow state, in case we
  crash before the response arrives.
- **Correlation.** To match the response to that saved state we send a **correlation id** on the packet
  to `fax_out`; the restaurant returns it on the packet from `fax_in`; we use it to look up the stored
  workflow.
- **Lookup.** We build a store from packets raised by another component, to act as the lookup table for
  information needed to process a request.

▎ You have now seen this workflow twice: once as paper, once as a graph. It was the same workflow both
times.

#image: hand-drawn FBP 'Onboard Restaurant' flow  [→ resources/flowbased_onboard_restaurant.png, resources/FBP Onboard Restaurant.drawio]
#image: hand-drawn FBP 'Order Food' flow  [→ resources/flowbased_order_food.excalidraw, resources/FBP Order Food.drawio]
#image: hand-drawn FBP 'Order Food Errors' flow  [→ resources/flowbased_order_food_errors.png, resources/FBP Order Food Failure.drawio]
#image: hand-drawn FBP 'Order Placement' flow  [→ resources/flowbased_order_placement.png, resources/FBP Order Placement.drawio]
#image: hand-drawn FBP overall 'Order Flow'  [→ resources/flowbased_order_all.png]
#image: hand-drawn FBP diagram — nodes as processes connected by Message-Oriented Middleware (MoM)

Presenter notes: **The summit of movements B and C, and the third artefact the exercise asks for.** Note that storage, correlation and lookup are the three things the paper flow also had — the file, the reference number written on the fax, and the catalogue. Nothing new was invented; it was named. Close on the MoM diagram: make the arcs middleware and the nodes processes, and this is a distributed system — which is the hinge into Reactive. *Putting It Together* at the end of the day annotates this same example.

---

### Slide: Reactive Architectures

Section marker. Reactive derives from **reactive programming**, not from OO.

### Slide: The Reactive Manifesto

Published September 2014 by Jonas Bonér, with Erik Meijer, Martin Odersky, Greg Young, Martin Thompson,
Roland Kuhn, James Ward and Guillaume Bort. It defines an architectural style — **Reactive
Applications**. Write applications that:

- **react to events** — the event-driven nature enables everything else;
- **react to load** — scalability rather than single-user performance;
- **react to failure** — resilient systems that recover at all levels;
- **react to users** — combine the above into an interactive experience.

Four traits: **Responsive** (responds in a timely manner), **Resilient** (stays responsive in the
presence of failure), **Elastic** (stays responsive under varying workload), **Message Driven** (relies
on asynchronous message passing). — reactivemanifesto.org

**You have met two of these already, under other names.**

- **Resilient** is what we called **robust** on Day 1: stay working when something you depend on is not.
- And *easy to change* is in the manifesto's own words: "Systems built as Reactive Systems are more
  flexible, loosely-coupled and scalable. This makes them easier to develop and **amenable to
  change**."
- **Elastic** and **Responsive** are the two Day 1 did not have names for.
- **Message Driven** is the mechanism — the same one, all the way through.

▎ Two properties, one mechanism. Somebody wrote it down in 2014.

Presenter notes: **This is the payoff of the Day 1 §1 plant, and Day 1 deliberately never said the word "Reactive" so that this lands as recognition rather than repetition.** Do not present the manifesto as new information; present it as the delegates' own two properties, already published, with two more added. Ask the room which two they already had before showing the mapping. Also: **not just the actor model** — these ideas have expression well beyond it, and following Helland, many implementations are possible.

### Slide: Reactive Traits — Value, Form, Means

A useful way to read the four traits:

- **Responsive** is the **value** — the thing the user actually gets.
- **Resilient** and **Elastic** are the **form** — the shape that delivers it under failure and load.
- **Message Driven** is the **means** — how the form is achieved.

**Attribution.** This is a **gloss, not manifesto text.** The manifesto names the four traits and says
Message Driven is the foundation the others rest on, but it never assigns value / form / means. The
split is how Bonér has presented it in talks, and it is a defensible reading — say so on the slide
rather than letting it read as a quotation.

Presenter notes: Fixed attribution — the old slide showed four words and three labels with no source, which reads as if quoting. If you would rather not carry someone else's gloss, this is the most cuttable slide in the movement; the manifesto slide above stands on its own.

### Slide: Message Passing

**Message passing** is an asynchronous method of communication: both parties need not be simultaneously
present. Mail is delivered to a **mailbox** of some form, for later retrieval.

#image: hand-drawn diagram — a component with incoming and outgoing message arrows (asynchronous message passing)

Presenter notes: Message passing invokes behaviour on a computer. In contrast to calling a program by name, it uses an object model to separate the general function from the specific implementation — the invoker sends a message and relies on the object to select and execute the code. The justifications fall into two categories: encapsulation and distribution. Point back at the frame: a mailbox is a pigeonhole.

### Slide: Microservices Are Reactive Architectures

We separate data from behaviour, activate a component in response to work being on a queue, process it,
and send an outgoing message. That is a node with ports. That is a desk with trays.

- A component's inputs are commands and events; its outputs are events.
- Nobody holds the whole process. There is no gateway `main`.

▎ **Day 1 called independent deployability "the whole prize". This is how you stop giving it back.**

#image: hand-drawn message-passing diagram — a component with in-request / out-request / out-result ports (command vs event)

Presenter notes: **Close the Day 1 loop explicitly** — name *Easy to Change — Independent Deployability* from Day 1 §1 out loud. The through-line to draw on the board: call and return puts knowledge of the whole use case in one place, so one place has to change every time the use case does; flow puts each step in its own component reacting to its own input, so a new step is a new subscriber. Reactive architectures derive from reactive programming, not OO — "everything flows".

### Slide: Partitioning and Dataflow

- **Partition to exploit parallelism** — find the tasks that could run concurrently and give each its
  own component.
- **Coordinate dataflow** — "orchestrate a continuous steady flow of information", dividing the system
  by **behaviour**, not by structure.

▎ Divide by verb, not by noun. Entity services divide by noun — that is Feature Envy.

#image: hand-drawn FBP diagram — Checkout and Take Payment components with purchase / priced / payment-due messages

Presenter notes: The direct answer to movement A. Reactive inherits from dataflow: conceive the application as a graph of nodes operating on data flowing through it. It shines for data-driven applications composed from components in workflows — let components subscribe to each other's event streams and consume published facts asynchronously, on demand.

### Slide: Bulkheads

In a synchronous conversation both parties must be up, so a fault **propagates** back up the chain and
we are brittle. In an asynchronous conversation it does not: the work queues up instead.

- The sender sends and returns immediately, whether or not the receiver is up.
- Messages wait until the receiver asks for them; results go to a queue for collection.
- The failure is contained in one compartment — a **bulkhead**.

▎ The outage became a delay, not a failure. Again.

#image: hand-drawn FBP diagram — Take Payment crossed out; work queues up on a fault (the bulkhead)

Presenter notes: This slide absorbs the cut *SOA — Faults Propagate* — the fault propagation claim is made here, where it is immediately answered, instead of standing alone. And the callout is the Day 1 §1 central argument arriving for the third time: availabilities multiply only under temporal coupling; store-and-forward breaks the chain. This requires storage and retransmission — usually Message-Oriented Middleware.

### Slide: When the Pipe Fills — Backpressure or Load-Shedding

Buffers are finite, so when a consumer cannot keep up something has to give. There are exactly two
answers, and it is a **decision**, not a default.

| | **Backpressure** | **Load-shedding** |
|---|---|---|
| what happens | slow the producer down | discard messages |
| what you lose | latency | data |
| choose when | data loss is unacceptable and extra latency is tolerable | volume is high and you only need a sample |
| example | blocking retry against a database you cannot reach | 1,000 metrics a second when 10 meets the SLA |

- **Backpressure** is the producer feeling backward pressure from the pipe, forcing it to slow until the
  pressure alleviates. Blocking retry creates it as a side effect: retrying a connection slows
  consumption, which fills the queue, which slows the producer.
- **Load-shedding** can discriminate — prioritise, and discard only the less valuable data.

#image: hand-drawn message-passing diagram — push vs pull, with backpressure annotations on the ports
#image: hand-drawn message-passing diagram — load-shedding, dropping messages on a fault

Presenter notes: Merged from two slides. The idea was introduced as a mechanism back in *Capacity, Backpressure and Node Lifetime*; here it becomes the choice. Worth asking the room which one their current system does — the answer is usually "neither, it falls over", which is a third option nobody chooses on purpose.

### Slide: Putting Reactive Together

The pieces, and how they compose.

- **Message passing** decouples in time — the bulkhead.
- **Backpressure and load-shedding** handle a consumer that cannot keep up.
- **Circuit breaker** handles a downstream that is failing rather than slow: stop consuming, stop
  hammering it, resume when it recovers.
- **Scale out, not up** — a supervisor fans work out to worker instances; that is elasticity, and it is
  competing consumers from Day 1 §4.3.

▎ Responsive under failure, responsive under load. The traits are these mechanisms.

#image: hand-drawn message-passing diagram — circuit breaker: stop consuming on a fault
#image: hand-drawn 'scale out not up' diagram — a Supervisor fanning out to Worker instances
#image: hand-drawn 'scale out not up' diagram — Supervisor to Workers with scale-out and fault regions

Presenter notes: The circuit-breaker and scale-out diagrams used to be orphaned images under a "recap" heading and were never really taught. Give them a sentence each. Land the callout: Resilient and Elastic are not aspirations, they are the four mechanisms on this slide.

### Slide: Now Do One

You have seen the takeaway flow three ways: **as paper**, **as errors on paper**, and **as a graph**.

Now draw the hotel's.

#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)

Presenter notes: Hand-off into the **Paper Flow** exercise (~75 minutes), which runs immediately after this section — see REDEVELOPMENT-PLAN §7 for the run-of-show. Round 0 recaps Restaurant Onboarding, its error variant and its FBP re-expression, and lands *ACID at a desk, BASE across desks*. Delegates must **not** meet BPMN before the exercise: they invent a notation, and Process Automation then formalises it.

#note: Was *Exercise Material — Flow* ("Readme, slides") — a slide pointing at an exercise that was
never wired into the running order. It is now the bridge into Paper Flow.

---

## Process Automation

### Slide: What is a Microservice? (SOA 3.0)

"SOA is focused on business processes… a service should represent a self-contained functionality that corresponds to a real-world business activity." — Nicolai M. Josuttis, *SOA in Practice*.

Presenter notes: We treat microservices as SOA 3.0, so most best practice still applies. The key is service **alignment with a business process or activity** — this workstream is about how that alignment improves productivity (not just fault-tolerance through isolation). Amplified next by the entity-service anti-pattern.

#note: **Collision with §2.** The Josuttis quote is now a callout on §2 *SOA Is OO at Macro Scale*, where it is the yardstick the Feature Envy slide fails against. Decide during the Process Automation review which of the two keeps it — it should not be read out twice in one day.

### Slide: BPMN

**BPMN** (Business Process Management and Notation) is a visual language for diagramming business processes clearly, in a standardized and comprehensive way.

- A **start event** begins a flow; an **end event** terminates it (and may throw a message).
- **Sequence flow** arrows show the path of execution.
- An **event** begins, ends, or interrupts a flow; a **task** is where work gets done.

#image: BPMN diagram — an 'Order Food' process (Enter Location, Choose Restaurant, Add Menu Choices, Checkout) ending with a message event  [→ resources/BPMN Ordering Flow.drawio.png]

### Slide: BPMN — Basic Elements

A BPMN diagram consists of: **Start Event**, **End Event**, **Sequence Flow**, **Activity** (Task / Sub-process), **Event**, and **Gateway**.

#image: BPMN diagram — start event, task, gateway splitting to two parallel tasks, merge gateway, end event  [→ resources/BPMN Elements.drawio.png]

### Slide: BPMN — Tasks

A **task** is an atomic activity (cannot be broken down further):

- Generic, Service (uses a service), Receive (waits for a message), Send (sends a message), User (human completion via software), Manual (human completion not via software), Business Rule (rules engine), Script (executes code).
- Markers: Loop, Transaction.

#image: BPMN legend — task/activity icon variants (service, message, user, manual, business rule, script, loop, transaction)  [→ resources/Task Types.drawio.png]

### Slide: BPMN — Events

An **event** happens within a flow — starts it, ends it, or interrupts it:

- None, Message, Time, Signal, Compensation, Conditional, Escalation, Parallel, Cancel.

#image: BPMN legend — event-circle variants (message, timer, signal, escalation, compensation, cancel, etc.)  [→ resources/Event Types.drawio.png]

### Slide: BPMN — Gateways

A **gateway** controls how sequence flow branches and converges:

- Exclusive (one alternative path), Inclusive (alternatives, possibly parallel), Parallel (split/join), Complex (complex expression), Event (an event picks the path).

#image: BPMN legend — gateway-diamond variants (exclusive, inclusive, parallel, complex, event-based)  [→ resources/Gateway Types.drawio.png]

### Slide: BPMN — Connecting Objects

- **Sequence Flow** and **Message Flow** connect activities.

### Slide: Workflow Patterns

*Workflow Patterns* — van der Aalst, ter Hofstede, Kiepuszewski, Barros (2000): 5 basic + 15 advanced patterns. *Workflow Control-Flow Patterns: A Revised View* — van der Aalst, Mulyar, Russell, ter Hofstede (2007): 23 new patterns.

### Slide: Pattern 1 — Sequence

One activity follows another. BPMN: connect two tasks with a sequence-flow arrow. Easy to model and execute. Example (Customer): Browse Pizza → Add Pizza to Basket.


#image: BPMN diagram — two user tasks: Browse Pizzas → Add Pizza to Basket

### Slide: Pattern 2 — Parallel Split

One path splits into two or more concurrent branches. BPMN: a **Parallel Gateway** (+) forks. Example: Assign Courier + Cook Pizza.


#image: BPMN diagram — Accept Order, a parallel gateway splitting to Cook Pizza and Assign Courier

### Slide: Pattern 3 — Synchronization (Join)

Wait until multiple concurrent branches complete. BPMN: a **Parallel Gateway** joins. Example: Assign Courier + Cook Pizza.


#image: BPMN diagram — Cook Pizza and Assign Courier merging into a parallel join gateway

### Slide: Pattern 4 — Exclusive Choice

Choose one path based on a condition. BPMN: an **Exclusive Gateway** (X) with condition expressions. Example: Check Availability → Accept Order **X** Reject Order.


#image: BPMN diagram — a message start, Check Stock, exclusive gateway to Reject or Accept Order

### Slide: Pattern 5 — Simple Merge

Merge non-concurrent paths back into one. BPMN: a converging sequence flow — no gateway needed if no synchronization is required. Example: multiple paths lead to Eat Pizza.


#image: BPMN diagram — timer/message events for Pizza Received, Check Delivery Status, Eat Pizza

### Slide: Process = Orchestration

A **Process** describes a sequence/flow of activities. In BPMN it is a graph of flow elements (a sequence flow of activities, events, gateways).

A Process is an **orchestration**:

- The sequence flow represents control of a process.
- The **token** represents state for an instance.
- Generally a process orchestration lives within an address space (not distributed) — an embedded workflow or an external process manager.

#image: BPMN diagram — a Checkout Basket process (Create Basket, Validate Choice, Price Basket, Validate Delivery/Payment)  [→ resources/Shopping Flow As Sequence.drawio.png]

### Slide: What is Orchestration?

Focused on a single participant's perspective.

- Like writing your own script.
- Includes control flow, state, and decisions.
- All logic is local to the orchestrator.
- Often implemented via state machines or workflow engines.

### Slide: Tokens

- A **token** represents an instance of a process.
- A token flows down the process; it is the state of the process for that instance.

#image: BPMN collaboration — Customer and Shopping pools with message flows (Begin Shopping, Basket Price, Valid Basket)  [→ resources/Shopping Flow with Pools.drawio.png]

### Slide: Pizza Example — BPMN Orchestration (Customer Pool)

The customer journey as an orchestration.




#image: BPMN diagram — the Customer-lane pizza-ordering flow with reorder, rejection, delivery-status timer, cancellation  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: In the demo we emulate this with HTTP calls (same as web/mobile). It's "in process" — we manage the token and its state through the flow. We show where we wait to receive a message. Debugging: we pause awaiting a message from another system, and can't see how the received values were set, or why we do/don't receive a message — for that we'd need the sender.

### Slide: Pizza Example — BPMN Orchestration (Pizza Shop Pool)

The pizza shop as an orchestration, initiated by a message.




#image: BPMN diagram — the Pizza Shop pool with Kitchen and Dispatch lanes (cooking and courier assignment)  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: We send messages to act (message icon) and wait to receive messages (start and end). Same debugging blind-spot — to debug the flow to the customer we'd need breakpoints in both, which is fine if we own both, but not if they belong to different teams (we'd have to deploy their code).

### Slide: Pizza Example — BPMN Orchestration (Courier Pool)

The courier as an orchestration, initiated by a message.




#image: BPMN diagram — the Courier lane, Check Availability gateway to Reject/Accept Job, collect and deliver  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: Same pattern — send messages to act, wait to receive. To debug the flow to the pizza shop and customer we'd need breakpoints in all of them.

### Slide: Pizza Example — Pools and Lanes




#image: BPMN diagram — a large multi-lane (Customer/Kitchen/Dispatch/Courier) collaboration with cross-lane message flows  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: Multiple pools (Pizza Shop, Courier, Customer App) with message flows (App→Shop order; Shop→Courier pickup request; Courier→Shop ready; Shop→Courier pizza ready). We want to examine the *interaction* from a neutral perspective, but modelling it as one pool with lanes doesn't work well — some tasks reference interaction (waiting for delivery, collecting money), others are oblivious to partners (baking, eating). It is not semantically correct because message events always refer to messages received from *outside*.

### Slide: Collaboration and Choreography

- A **Collaboration** has multiple participants.
- The message exchange between participants in a collaboration is a **Choreography** — generally the flow of messages between participants; within each orchestrated process there are message events caught or raised.
- Processes *react* to what happens in the choreography — no one owns it (it has no tokens or state of its own).

#image: BPMN collaboration — Customer and Shopping pools with message flows  [→ resources/Shopping Flow with Pools.drawio.png]

### Slide: What is Collaboration?

Focused on how participants interact.

- Interaction might be within a workflow engine — but this creates coupling, and both participants must run in the engine.
- Interaction might be via an API — from an event-driven perspective, we are most interested in this model.

### Slide: Pools and Lanes

- A **Pool** is a participant in a collaboration (a role or an organization). Not required for the main internal pool (the modeler's own org); required for other organizations' processes.
- A **Lane** distinguishes sequences of activities within a pool. White box = can see process; black box = cannot.
- Activities within the pool are organised by sequence flow.

#image: BPMN collaboration — Customer and Shopping pools with labelled pools/lanes and message flows  [→ resources/Shopping Flow with Pools.drawio.png]

### Slide: Pizza Shop Collaboration

A collaboration diagram for the pizza-shop example.

#image: BPMN diagram — three pools (Customer, Pizza Shop, Courier) in a full collaboration with many message flows  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

### Slide: Choreography and Conversation

- A **Choreography** describes a sequence/flow of activities *between* participants — a graph of flow elements (a message flow of activities, events, gateways).
- A **Conversation** is a logical association of messages that can all be correlated. **Correlation Keys** associate messages in the same conversation (may be existing message data); the first task in a conversation *must* populate the conversation id.

#image: BPMN diagram — a horizontal flow with Customer/Shopping lane labels per task and message events  [→ resources/Shopping Choreography.drawio.png]

### Slide: What is Choreography?

Focused on interactions across multiple participants.

- Like describing a dance — no single owner of the flow.
- Defines who talks to whom, in what order.
- No centralized control.
- Cannot access shared internal data/state.

### Slide: Pizza Example — BPMN Choreography

The pizza-order choreography — the flow of messages between participants.




#image: BPMN choreography diagram — the pizza-order flow as message events across Customer, Pizza Shop, Courier  [no source in resources/ — resources/Shopping Choreography.drawio.png is the *shopping-basket* choreography (Begin Shopping / Add Item / Basket Price), not the pizza one]

Presenter notes: Even this simple interaction produces a set of messages flowing between participants. Choreography is what happens "between" — it has no explicit owner. When flow leaves your application (or workflow engine) it "goes blind": the **event horizon**. You understand your workflow — it's in your code — but debugging becomes hard because at times nothing happens that's supposed to, and you struggle to know why.

### Slide: Messaging and Eventing (Orchestration vs. Choreography)

A common EDA notion: *messaging (commands) is orchestration; eventing is choreography.*

- It is **not** a helpful rule.
- Choreography is the flow of control and information *between* orchestrations — frequently out of process, and can use messaging or eventing as required.
- An orchestration is a sequence with attendant session state (token) — frequently not distributed, within an executable process. A **routing slip** is a distributed orchestration that uses message attributes as the engine of application state.

### Slide: Event Chaining

A sensible balance of orchestrated bounded contexts and choreography between them reduces event chaining. But **Event Pinball** can still be a problem between orchestrated services.

- **In-Out (or Robust In-Only):** explicit transfer of control reduces the "pinball effect" — creates causality by awaiting a response (send a *command* and wait for a response, not an event).
- **Out-Only:** often better at the *termination* of a workflow, or to broadcast intermediate states with no expectation of response.

### Slide: Allocating Responsibility for Collaborations

- **Commands / Messaging** — transfer of control/data; typically delegating responsibility for part of a workflow. In-Out (expected to return); In-Only (not expected to return, but may on error → Robust In-Only).
- **Events** — communicate the outcome of a workflow (complete, or a milestone broadcast). Out-Only (no expected return).
- **Workflow code is glue** — glue does not execute the domain (it is not the behaviour); it *calls* something that has the behaviour.

### Slide: Orchestration vs. Choreography — Summary

| Aspect | Orchestration | Choreography |
|---|---|---|
| Control | Centralized (one participant) | Decentralized (shared) |
| BPMN Shape | Inside a Pool | Between Pools |
| Perspective | One party's process | Multi-party message exchange |
| Data Access | Internal | Shared messages |
| Execution Tool | API calls, handlers, workflow engine | Messaging protocol |
| Example | Pizza Shop coordinates cook + courier | Customer + Shop + Courier interact |

Presenter notes: Implementation paths depend on model type — embedded logic (orchestration) vs. API contracts/events (choreography). Clear boundaries → better automation decisions and a clearer division between messaging and eventing.

---

### Slide: Tentative Operations

A conversation that spans more than a request and a response: the requestor may not know whether the provider can succeed, and may not want to proceed without knowing.

- `reserve()` — the requestor asks if the operation is possible and reserves the resources; the provider reserves the resource (usually with a timeout) and awaits commit or rollback (`reservation()`).
- On success → `commit()` → `acknowledge()` (allocate the reserved capacity).
- On failure → `rollback()` → `freed()` (free the reserved capacity).

### Slide: Tentative Operations — Example

- **Basket → Warehouse:** `reserve()` stock (Fault-Replaces-Message could apply if out of stock).
- Warehouse reserves the stock with a timeout so others can buy it if we don't.
- If the customer pays before the limit → `commit()` → `acknowledge()` (allocate stock).
- If the basket doesn't complete → `rollback()` → `freed()`.

Presenter notes: This is the bridge into durable execution. Reserve/commit/rollback is a conversation with a *lifetime* — someone has to remember the reservation exists, honour its timeout, and drive it to commit or rollback even across a restart. That requirement is what the rest of this section is about.

### Slide: Durable Execution

Long-running processes must:

- Survive restarts.
- Handle retries and failures.
- Resume after waiting (e.g. for payment or a courier).

Durable execution = we **persist activity state** to indicate which steps are complete, when we're awaiting an event, etc.

### Slide: Activities and Resources

Broadly, a software component manages **activities** and **resources** (Pat Helland).

- **Resources:** domain concepts we manage — restaurants, couriers, customers.
- **Activities:** one or more sequences for our interaction with resources.
- As the token moves through the sequence we update resources *and* the activity (to indicate progress).
- The implementation question: **where does activity state live, and who updates it?**

### Slide: Activities and Resources — Worked Example

- **Cashier → Pricer:** `get pricing details()` → `item price()` (waiting for response).
- **Cashier → Payment Provider:** `take payment()` → `payment taken()` (waiting for response).
- **Activity** (usually a service task) — glue code that calls domain logic internally or messages another app; could be a framework, a bespoke state machine, or pipes and filters.
- **Resources** — code/data managing shared items coordinated across activities (inventory widgets, truck space) — our domain model.
- Our workflow stores the token state (where are we in the flow?), and there is a choreography — the messages we exchange with other participants running their own flows.

Presenter notes: Per Helland — each entity must remember state about its partners on a partner-by-partner basis; call this an **activity**. An entity may have many activities if it interacts with many partners.

### Slide: Handlers + Activity State Updates

Handlers process events (change resources) and update activity state.

- Durable because state is stored (e.g. a database), but control flow is **implicit** — activity state is often implicit (e.g. within an aggregate).
- Great for simple workflows, but logic becomes scattered across handlers.
- Becomes complex with split/join/choice/merge (not a sequence), and with retry / circuit breakers / compensation.
- Relies on **guaranteed delivery** (store work for retry unless ack'd) and **Transactional Messaging (Outbox)**.

Presenter notes: Baseline automation. E.g. an `OrderReceivedHandler` looks up the order and sets state = Preparing. Handlers process events and update persistent state; durable via stored state, but control flow is implicit — logic scatters across handlers.

### Slide: Handlers — Illustration

A diagram of the handler-based approach.


#image: C# code screenshot — an async order handler using a transaction, postbox and the outbox pattern

### Slide: (Fault) Handlers + Activity State Updates

How do we handle **compensation** flows with handlers?

- **Fault Message:** for reliable In-Only, a dedicated fault channel is required (used only for compensation); for In-Out, the response-channel message should indicate fault, not success.
- May retry the handler, and only after X failures run the fallback.
- On fault, run a "fallback handler" that initiates compensating action — reverse actions so far; write an "undo" for each "do".
- A straightforward approach: send a fault message back upstream and undo on receipt.

Presenter notes: The **Saga** pattern — long-running transactions in distributed systems; when you can't roll back, you undo. Name from a 1980s paper on long-lived DB transactions. BPMN supports this via compensation events linking tasks with undo tasks; a workflow engine executes the necessary undo actions. (Ruecker, *Practical Process Automation*.)

### Slide: State Machine + Activity State Updates

When handler interaction becomes complex, make the activity **explicit**.

- A **State Machine** represents the activity and triggers actions on transitions.
- Transitions are caused by receiving a message.
- The handler loads the state machine for the conversation id, triggers the transition denoted by the message, and runs the associated code.
- Save the new state and ack the message.

Presenter notes: States e.g. Received → Preparing → Ready → OutForDelivery → Delivered; transitions triggered by events/commands; implemented via the state pattern, switch statements, or a library (e.g. Stateless); durable via persisted state + event log. Benefits: predictable, easier to visualize/test, avoids duplication across handlers. Drawback: no concurrency or waiting logic.

### Slide: State Machine — Illustration

A diagram of the state-machine approach.


#image: C# code screenshot — an OrderStateMachine (MassTransit) with Initially/During states and transitions

### Slide: (Fault) State Machine + Activity State Updates

How do we handle compensation with a state machine?

- The "saga" pattern in messaging frameworks is typically a state machine — it guarantees that on a fault, the machine transitions back to "safe".
- Implementations run all fault transitions to safe *before* acking the fault message.
- May retry the transition, and only after X failures run compensation.
- On fault, transition to a faulted state and initiate a compensating flow to "safe" (reverse actions; write an "undo" for each "do").
- Requires **durable execution** — if we fault partway, on restart we resume.

Presenter notes: As above — the Saga undoes rather than rolls back; BPMN compensation events link tasks with undo tasks. (Ruecker, *Practical Process Automation*.)

### Slide: Routing Slip + Activity State Updates

To **distribute** steps in the sequence, transport the activity state *in the message*.

- A **routing slip** is an envelope carrying activity state (next step, context, etc.) — "Message As the Engine of Application State".
- The handler updates state when work is done, forwards according to the slip, then acks.
- Complex if "next" is dynamic routing (the code must understand how to execute).
- Complex because you distribute the steps — hard to observe (OpenTelemetry).

### Slide: (Fault) Routing Slip + Activity State Updates

How do we handle compensation with a routing slip?

- "Next" is now the *fault* next from this step — what we need to reverse.
- Context is "faulted".
- The handler updates state when work is done, forwards according to the slip, then acks.

### Slide: Workflow Engines + Activity State Updates

When we want more than state transitions (split, join, merge, choice), use a **workflow engine**.

- Explicitly models a sequence of activities and gateways; may support BPMN (or a proprietary language) with visual modelling.
- A step receives the token; the step is **glue** — invokes domain action, calls another service, sends a message.
- A **job scheduler** provides durable execution; typically any instance can resume a paused job (distributed).
- A step may wait for an event or timer to resume — the handler equivalent, or triggered by the handler calling the engine.

Presenter notes: External orchestrators — Temporal, Camunda, Azure Logic Apps, AWS Step Functions. Support wait states (await PizzaReady), parallel branches, timeouts, retries, visual modeling. Durable by design (execution state + workflow history stored); suited to complex, distributed systems. Example steps: StartCookingPizza → WaitForPizzaReady → DispatchCourier → WaitForPickup → MarkAsDelivered.

### Slide: (Fault) Workflow Engines + Activity State Updates

How do we handle compensation with a workflow engine?

- Is the error a **business** error or a **technical** error?
- A **retry** frequently handles technical faults. If retry fails and a catch is present, a fallback runs; with no catch, the workflow rolls back to the last wait state or terminates.
- A known **business** error (e.g. card declined) is usually modelled explicitly as a branch via a gateway.

### Slide: Embedded vs. External Workflow Engines

Weighing engines embedded in a service against external orchestrators.

### Slide: Workflow Engines — Lessons from SOA

Presenter notes: External orchestration is not an anti-pattern, but requires care. Keep core domain logic inside services; let the workflow engine coordinate *outcomes*, not fine-grained steps; consider choreography or local orchestration for autonomy.

### Slide: Smart Endpoints, Dumb Pipes

ESB products often include sophisticated routing, choreography, transformation, and business rules. The microservice community favours the alternative: **smart endpoints and dumb pipes**. (martinfowler.com/articles/microservices.html)

Presenter notes: Microservices promote smart services and minimal messaging infrastructure. External workflow engines risk **anaemic services** — all domain logic moves out, and services become passive executors of workflow directives.

### Slide: Implementing Workflow Patterns

How the basic patterns map onto the three implementation styles:

| Pattern | Handlers Only | State Machine | Workflow Engine |
|---|---|---|---|
| Sequence | Chain message handlers | State transitions (A→B→C) | Sequential steps |
| Parallel Split | Trigger multiple handlers | ⚠️ Complex manual coordination | Parallel branches with fork/join |
| Synchronization | Wait for multiple states | ⚠️ Hard without orchestration | Join after parallel branches |
| Compensation | Fallback handler | Saga | Implicit |
| Exclusive Choice | Conditional in handler | State transition on input | Conditional branching |
| Simple Merge | Trigger single follow-up | Re-entrant transition or rehydration | Multiple incoming flows, OR gateway |

---

## Putting It Together

### Slide: Putting It Together

Section marker: revisiting the fax/pizza workflow through the lens of the patterns, annotating each interaction with its messaging/eventing exchange pattern.

### Slide: Fax Workflow — Annotated (Storage & Correlation)

The flow-based fax workflow, now labelled with exchange patterns:

- **Storage:** store workflow state in case we crash before receiving a response.
- **Correlation:** use a correlation id sent to `fax_out` and returned via `fax_in` to look up the stored workflow.
- Interactions annotated: Messaging (In-Only, In-Only, Out-Only, In-Out) and Eventing.

#image: (s167) collaboration diagram — restaurant onboarding (fax/phone steps, new catalogue)  [→ resources/Restaurant Onboarding.drawio.png]
#image: (s168) FBP 'Onboard Restaurant' flow, annotated with Messaging/Eventing (In-Only/Out-Only/In-Out)  [→ resources/flowbased_onboard_restaurant.png]

### Slide: Lookup Store — Annotated

Building a lookup store from IPs raised by another component, annotated: Messaging (Out-Only, In-Only, In-Only, In-Out) and Eventing.

#image: (s169) collaboration diagram — order taking (phone order, card machine, eventual consistency)  [→ resources/Customer Order.drawio.png]
#image: (s170) FBP 'Order Food' flow, annotated with exchange patterns  [→ resources/flowbased_order_food.excalidraw]

### Slide: Fault Path — Annotated

The workflow's fault path annotated as Messaging with **Message Triggers Fault**.

#image: (s171) collaboration diagram — order-taking errors (invalid card, outbox)  [→ resources/Customer Order Errors.drawio.png]
#image: (s172) FBP 'Order Food Errors' flow, annotated with Message-Triggers-Fault  [→ resources/flowbased_order_food_errors.png]

### Slide: Full Flow — Annotated

The complete flow annotated with its mix of Messaging (In-Only, In-Out ×3) and Eventing (Out-Only) exchanges.

#image: (s173) collaboration diagram — order placement (fax operators create/accept order, book driver)  [→ resources/Order Placement.drawio.png]
#image: (s174) FBP 'Order Placement' flow, annotated with exchange patterns  [→ resources/flowbased_order_placement.png]

### Slide: Putting It Together — Recap

Final visual recap tying the exchange patterns back to the worked example.

#image: (s175) composite — an 'Order Confirmation' collaboration diagram plus thumbnails of the other flows  [→ resources/Order Confirmation.drawio.png + related]
#image: (s176) FBP overall 'Order Flow' — Qualify Restaurant through Cook Food and Book Courier  [→ resources/flowbased_order_all.png]

---

## Next Steps

### Slide: Further Reading — Reactive Microservices

*Reactive Microservices Architecture* — Jonas Bonér. (jonasboner.com/resources/Reactive_Microservices_Architecture.pdf)


#image: book cover — 'Reactive Microservices Architecture' by Jonas Bonér (O'Reilly)

### Slide: Further Reading — Practical Process Automation

*Practical Process Automation* — Bernd Ruecker. (processautomationbook.com)


#image: book cover — 'Practical Process Automation' by Bernd Ruecker (O'Reilly)

### Slide: Further Reading — EDA Visuals

Serverless Land — event-driven architecture visuals. (serverlessland.com/event-driven-architecture/visuals)


#image: screenshot — the Serverless Land 'EDA Visuals' page of event-driven architecture cards

### Slide: Further Reading — Enterprise Integration Patterns

Gregor Hohpe. (enterpriseintegrationpatterns.com/gregor.html)


#image: book cover — 'Enterprise Integration Patterns' by Gregor Hohpe and Bobby Woolf

### Slide: Q&A

Questions and discussion.
