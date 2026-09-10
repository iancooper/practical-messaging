# Practical Messaging — Day One

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day One is **the message**, end to end. It opens on the process boundary and what drawing one commits you to, then the coupling and integration styles that follow from it, then a build order for messaging code — messages, channels and endpoints, the message pump, guaranteed delivery, and queues vs. streams. It closes on the two decisions you make with all of that: which **exchange pattern** to build, and what to put **in the message**.

Prerequisites: We use RabbitMQ and Kafka for examples. You should have Docker (or an equivalent) installed — exercises ship a Docker Compose file to spin up RMQ and Kafka.

- Course content: https://github.com/iancooper/practical-messaging
- Exercise code: C#, Python, JavaScript, Go, Java repos under github.com/iancooper/Practical-Messaging-*

---

## The Process Boundary

*What sending messages between processes commits you to. Two slides, and then straight into coupling.*

### Slide: Messages In, Private Data, No Shared Transaction

We are going to spend two days sending messages between processes. Before anything else, **what does
drawing that boundary decide for you?**

- **The only way to get work done in another process is to send it a message.** Each service has its own
  accepted message types, and its own data requirements for partners submitting work.
- **The data behind the boundary is private.** A request does not describe the shape of the data inside;
  it describes the work. Nobody reads your tables.
- **No transaction spans two services.** Transactions — 2PC included — happen *within* a boundary, never
  across one. You do not exchange transactions with your business partners, because their mistake would
  lock your database. Without transactions you communicate through **multiple messages over time**.

▎ No transaction spans two services. Consistency stops being something you declare and becomes something
you design.

#image: diagram — two services either side of the process boundary: a message crosses on a channel each way, while a direct read of the other's tables and a transaction drawn across both stores are each crossed out on the line itself  [→ resources/boundary-what-crosses.png]

Presenter notes: **This is the load-bearing slide of both days, and it is the first one.** Everything
the course teaches — outbox, sagas, idempotence, choreography, compensation — exists because the third
bullet is true. Say that explicitly: it gives delegates a spine to hang the rest on. Keep it to five
minutes; it is a premise, not an argument, and the room does not need persuading that processes have
boundaries. **Do not argue for microservices** — the boundary is the subject, and whether you got it from
services, from a modular monolith with a queue between two components, or from talking to another company
is not this course's business. §Coupling picks it up immediately: the boundary has already taken the two
tightest coupling modes off the table, and *What's Left Is in the Message* is the bill for the rest.

### Slide: Robust — Guaranteed Delivery

The boundary costs you transactions. It buys you this — and this one is cheap.

- We want the work **not to be lost** when something we depend on is slow, overwhelmed, or down.
- **Store and forward.** The work waits somewhere durable until whoever does it is ready. **The outage
  becomes a delay.**
- **You do not need to reorganise anything to get this.** A single team with a single web application can
  have it on Monday.

▎ One team, one service, one queue. Robustness without reorganising the company.

Presenter notes: §4.4 Guaranteed Delivery is the spine of the afternoon, and this slide is the
**inoculation** — it exists
so nobody in the room can file the course under "not for us, we're a monolith". Say the callout and move
on; the mechanism is two hours away and they will recognise it when it arrives. **Do not say "the second
property"** — the two-properties framing now lives on Day 2, and this slide has to stand alone.

## Coupling

*What the process boundary bought you, and what you can still give back.*

### Slide: What the Process Boundary Already Bought You

The classic coupling scale runs Content → Common → Control → Stamp → Data, tightest first. **Drawing a
process boundary takes the top two off the table.**

- **Content** — one party reaches into the other's internals. Across a network this can only survive as a
  degenerate form: depending on undocumented behaviour, a private endpoint, someone else's table. There
  is no pointer into another process's memory.
- **Common** — both parties share the same mutable store. Uncontrolled propagation of change; nobody owns
  the schema. Separate processes with **private data** do not have one.

The opener said exactly this: *Messages In, Private Data, No Shared Transaction*. That slide was the
mechanism. This is what it bought you.

#image: the Myers coupling scale drawn vertically, tightest first, with the process boundary as a line across it — Content and Common above the line, struck through as *prevented*; Control, Stamp and Data below it, live  [→ resources/coupling-scale-boundary.png]

Presenter notes: **This slide opens the section cold**, so give it one sentence of framing before the
scale: **coupling decides whether we can deploy independently,
and how far a change spreads — it is a delivery and availability concern, not code tidiness.** Then the
good news: this is the first thing delegates get *back* from drawing a boundary. Say plainly that **content coupling barely translates across a network boundary** rather than
pretending the scale ports over unchanged; the honest version is more persuasive. The scale is Myers'
structured-design scale, adapted to services — say so.

### Slide: What's Left Is in the Message

You cannot avoid the other three. Every message you send picks one, whether or not you meant to.

- **Control** — you tell the other party *what to do* rather than *what happened*. A what-to-do flag in
  the payload. The receiver's behaviour is now your business.
- **Stamp** — you share a composite structure and each of you uses only part of it. A change to a field
  you never read can still break you.
- **Data** — you share only the elementary values you each actually need.

▎ Stamp coupling is the one you will meet every day.

▎ The boundary chose the first two for you. The message is where you choose the third.

Presenter notes: **This is the slide the rest of the course keeps coming back to.** Stamp coupling recurs
everywhere: it is the argument for skinny messages (§6.1 Fat and Skinny, at the end of today) and for
tolerant readers (the *Managing Asynchronous APIs* handout). Flag it now so both call-backs land. The
second callout is the one to write on the board — it is why §6 *Designing Messages* exists at all, and it
is why *Messaging* wins the comparison two slides from now.

### Slide: Must We Both Be Up?

There is a second axis, and interacting **between processes** is what forces it on you. If both parties
must be present for the communication to succeed, they are **temporally coupled**: the availability of one
becomes the availability of the other.

| | **Synchronous conversation** | **Asynchronous conversation** |
|---|---|---|
| Shape | Request → Reply | Store and forward |
| Both present? | Yes | No — pick it up later |
| Analogy | A phone call | Snail mail |
| Temporal coupling | **Introduces it** | **Avoids it** |

- **It is the axis that multiplies your outages.** Call a service and wait, and your availabilities
  multiply: four services at 99.9% leaves you at **99.6%**, before anything has actually failed.
- **Send a message and don't wait, and they don't.** Guaranteed delivery means the message outlives their
  outage and is processed when they come back.

▎ If my availability depends on yours, I have bought your outages.

Presenter notes: **Do the arithmetic on the board — 0.999⁴ = 0.996** — then be honest
about the trade: the messaging version does not make the downstream outage vanish, it buys an availability
loss back as latency variance. That is usually a trade you can accept, and it is the argument the whole
course rests on. Redundancy *within* a service raises availability; chaining temporally-coupled calls
throws the gain away. **This is where *robust* stops being a slogan and gets a number**, and breaking this
axis is what guaranteed delivery buys you. Note the asymmetry with the previous slide: the "about" axis you choose per message;
this one you choose per **style of integration**, which is the next section.

#note: If this table is too dense on the rebuild, split it back into the original two slides
(Synchronous Conversation / Asynchronous Conversation) and keep this slide for the definition alone. The
contrast is worth one slide if it fits.

### Slide: Two Axes, Not One Scale

"Loose coupling" is not a single dial. What we are coupled *about* and whether we must both be *up* move
independently:

- **gRPC with a flat DTO** — data coupled, but temporally coupled.
- **A command message with a what-to-do flag** — control coupled, but temporally decoupled.
- **A shared database** — common coupled, and temporally decoupled.
- **An event carrying a whole entity** — stamp coupled, temporally decoupled.

#image: a two-axis grid — *what are we coupled about?* (Content→Data) against *must we both be up?* — with the four examples above plotted on it  [→ resources/grid-coupling.png]

Presenter notes: This is the slide the next section pays off — Integration Styles plots File Transfer,
Shared Database, RPC and Messaging onto exactly this grid. It also explains why RPC's verdict needs two
words ("control **and** temporal") where the others need one. Note that the shared-database example sits
in the *prevented* half of the previous slide: you can only get there by choosing to, which is the point
the next section makes about it.

---

## Integration Styles

*Four ways to communicate between processes — and what each one gives back.*

#note: **Do not say "Reactive."** The preference argued here is paid off on Day 2, and it has to land
there as recognition. Argue it on coupling alone.

### Slide: File Transfer

One application writes a file; another reads it later. **The file is the contract.**

- **Asynchronous conversation** — nobody has to be up at the same time.
- **Data coupling** — if you keep the file format elementary.

**And the file is a message.** A batch of them, in a channel that happens to be a filesystem. Hold that
thought — the last slide of this section is about everything you did *not* get with it.

#image: (s32) File Transfer — a file sitting on the process boundary; the producer writes it, the consumer reads it later, and the file is the whole of the contract  [→ resources/style-file-transfer.png]

### Slide: Shared Database

Both applications read and write the same schema, typically through an ORM.

- **Asynchronous conversation** — the writer and the reader need never be present at the same time.
- **Common coupling** — and that is the problem.

▎ This is the one style that hands back what the boundary bought you.

**Nobody owns the schema.** A change propagates to every reader whether they wanted it or not, and you
are back to agreeing release dates across teams — which is exactly what the boundary was for.

#image: (s33) Shared Database — both applications on one schema, an ORM each, the schema straddling the process boundary and owned by neither side  [→ resources/style-shared-database.png]

Presenter notes: The sharpest verdict in the section. Be blunt: a shared database is
not a shortcut past the boundary, it is a decision to un-draw it. Note it is **not** temporally coupled —
its problem is the shared mutable schema, not availability. That is exactly why one axis was never enough.

### Slide: Remote Procedure Call

One application invokes an operation on another and waits for the result.

- **Synchronous conversation** — both parties must be up.
- **Control coupling** *and* **temporal coupling**.

#image: (s34) Remote Procedure Call — stub to proxy across the boundary and the result back, with the client blocked until it comes  [→ resources/style-rpc.png]

Presenter notes: You are telling the other party *what to do* — control coupling — and waiting while it
does it, which is where §Coupling's arithmetic bites: 0.999⁴ = 0.996. Be fair to it: RPC is the right answer when
you genuinely need the reply before you can continue, and Day 1 §5 *Conversations* has a whole slide on
Blocking In-Out. It is the default that is wrong, not the pattern.

### Slide: Messaging

One application writes a message to a channel; another consumes it.

- **Asynchronous conversation** — store and forward; the outage becomes a delay.
- **Coupled about… whatever you put in the message.** A command is control coupled. A whole-entity event
  is stamp coupled. A message carrying only what the receiver needs is data coupled.

▎ Messaging is the only style where the coupling is a decision, not a property of the style.

#image: (s35) Messaging — a message on a channel across the boundary, and the three things you might put in it, each with the coupling it buys  [→ resources/style-messaging.png]

Presenter notes: **The verdict cell used to read "data coupling", which was wrong and contradicted
§Coupling's own examples** — that section plots a command message as control coupled and a whole-entity
event as stamp coupled. Fixing it is what makes the argument: the other three styles fix your position on
the "about" axis; messaging leaves it open. That is not a hedge, it is the reason the rest of the course
exists — §5 *Conversations* is the temporal decision and §6 *Designing Messages* is the "about" decision,
and you only get to make either one here.

### Slide: Why Messaging

The four styles on the grid from §Coupling:

| Style | Coupled *about* | Must we both be *up*? | What it hands back |
|---|---|---|---|
| File Transfer | Data | No | Nothing — but you get nothing either |
| Shared Database | **Common** | No | The boundary itself |
| Remote Procedure Call | **Control** | **Yes** | Independent availability |
| Messaging | **Your choice** | No | Nothing |

**File Transfer and Messaging land in the same cell.** Coupling does not separate them — so what does?

▎ File transfer is messaging with everything useful left as an exercise.

- **Ordering** — a directory has none. You write it yourself, or you get whatever the filesystem lists.
- **Locking and competing consumers** — two readers on one directory will fight. A broker makes that a
  configuration option.
- **Delivery guarantees** — did the reader finish? Did it crash halfway? Nothing in the file says.
- **Granularity and timeliness** — a file is a batch, and a batch arrives when the batch is ready.

▎ Only one style keeps everything the process boundary bought you, and lets you choose the rest.

#image: the two-axis grid from §Coupling, same artwork, with the four integration styles on it — Messaging drawn as a span rather than a point, because its coupling is a choice  [→ resources/grid-integration-styles.png]

Presenter notes: **This is the section's goal slide: it has to end on *why messaging*.** Do not leave the
question — "if File Transfer and Messaging are equally loosely coupled, why build the whole course on
messaging?" — hanging for later. Answer it here: **file transfer is just messaging, without the support for locks, ordering and the rest**; everything the
broker does for you is something you would otherwise write. And the last callout is the whole argument of
the day in one line. **Do not name Reactive** — Day 2 needs it fresh.

## Messaging Patterns

*Integrating using events.* The pattern catalogue follows Hohpe & Woolf, *Enterprise Integration
Patterns*; the per-pattern prose lives in `script/Patterns/*.md` and should be merged onto these
slides during the rebuild.

#note: Ordered as a **build order**, not a catalogue order — the sequence someone from an HTTP
background needs in order to write messaging code and make it reliable. What is the unit? → how do I
send and receive one? → how do I keep receiving? → how do I stop losing them? → what kind of broker am
I on? The five questions are the five sub-topics, and `resources/eip-the-big-picture.png` draws them.

### Slide: The Big Picture


A map of the messaging patterns we will cover across the day.


#image: map — domain code, a messaging gateway, a channel with a message on it, and an endpoint at the far end; the message opened up into header and body, and §4's five questions in the order we meet them  [→ resources/eip-the-big-picture.png]

---

---

## 4.1 What Is a Message?

*Header and body, intent or fact — and whether the channel holds tasks or facts.*

### Slide: Message Construction


A message has a **header** and a **body**.

- The **body** contains data for the consumer.
- The **header** contains metadata for any filter in the pipeline, and should indicate the format of the body.
- Break a large message into pieces as a **Message Sequence**, or use a **Claim Check**.

Presenter notes: Two processes communicating copy data — usually a byte stream — that we break into discrete units so we can tell where a message begins and ends (needed for competing consumers and pub-sub). A message = header (how to process) + body (content). Related concepts: Request-Reply (RPC over messaging, using Return Address + Correlation Identifier); Message Sequence (sequence id, position id, size/end indicator); Message Expiry / Dead Letter for slow messages; Canonical Data Format; and Format Indicator strategies — Version Number, Foreign Key, or embedded Format Document.

### Slide: Messaging vs. Eventing (Intent vs. Facts)

Two words the industry uses interchangeably, and they are not the same thing. After Clemens Vasters,
two poles of message types.

| | Messaging | Eventing |
|---|---|---|
| carries | **intent** | **facts** |
| which looks like | a Command (transfer of control), a Query (request an answer), a transfer of value | a notification — something you report on |
| expectations | part of a workflow, part of a conversation | none |
| concerned with | the **future** | the **past** — history, context |

▎ A message asks for something. An event announces something.

Presenter notes: This is the first fork in every design decision that follows, and §Conversations turns
it into a choice of exchange pattern — intent gives you In-Only and In-Out, a fact gives you Out-Only.
If you are expressing intent you are addressing someone: you know who should act, and that is
behavioural coupling. If you are reporting a fact you are addressing nobody, the subscriber list is not
your concern, and that is the loosest coupling available.

### Slide: Discrete vs. Series (Eventing Types)

After Clemens Vasters again, a second axis — and this one is about events only.

| | Discrete | Series |
|---|---|---|
| handler | **stateless** | **stateful** partition processor |
| delivery | PUSH | PULL |
| position | independent | context, offset |
| shape | one thing, immediately actionable | continuous, sequential |
| what it says | something happened | a **condition** holds |
| part of | a conversation | a monolog |

Presenter notes: The row that pays off later is *position*. A discrete event stands alone, so anyone can
handle it and order does not matter; a series event only means anything in sequence, which is why the
stream in *Streams Contain Facts* keeps an offset, and why partitioning by key is the only way to
scale one. Point back at this table when you draw the partition in §4.3.

### Slide: Command / Document / Event Messages

After Gregor Hohpe. Three core message types: **Command**, **Document**, **Event**.

- **Command Message** — reliably invoke a procedure in another application. Encapsulates a request as an object (GoF Command); usually sent Point-to-Point (one consumer).
- **Document Message** — reliably transfer a data structure between applications; the receiver decides what, if anything, to do with the data.
- **Event Message** — reliable, asynchronous event notification. The difference from a Document Message is timing and content — an event's contents are typically less important.

Presenter notes: RPC's advantage is synchrony (immediate, caller blocks) — but that's also its weakness: if the network is down or the remote process isn't listening, the call fails. Asynchronous command messages keep trying until the procedure is invoked. The command's state (parameters) is stored in the message.

### Slide: Queues Contain Tasks

A channel carries one of two things, and which one it is changes almost everything that follows.
Messages on a **queue** are **tasks** — requests to carry out an action. Once the action is done, the
task is gone.

- The first consumer **locks** the next message while it processes it.
- A second consumer **reads past** any locked message and locks the next available one.
- Nobody else should action a done task; a receiver of one discards it. If we cannot action it, someone
  else must.

#image: diagram — a queue of envelopes: Consumer One locks the one at the head, Consumer Two reads past it and locks the next  [→ resources/qs-queue-tasks.png]

Presenter notes: The lock is the whole of a queue, and everything in §4.3 and §4.4 rests on it —
competing consumers, requeue with delay, dead-lettering, the retry count. Say it here so it is not a
surprise later: **a queue can hold a message back and hand it to someone else, and a stream cannot.**

### Slide: Streams Contain Facts

Records on a **stream** are **facts** — records that a state change occurred. Nothing is consumed by
reading and nothing is deleted.

- The first consumer reads the next record and processes it; a second consumer reads the next and
  processes it — and **both can read the same records**.
- Each consumer stores an **offset** marking how far it has read.
- On restart, a consumer reads the store to find the last record it processed.
- Facts are an "inverse database" — how the current state was arrived at. Navigate the offsets to
  compute a point-in-time position.

▎ A queue holds work to be done. A stream holds what happened. Everything else follows from that.

#image: diagram — an append-only log of numbered cells, two consumers reading all of it, each with its own offset store  [→ resources/qs-stream-facts.png]

Presenter notes: This is the *series* row of the previous table with a picture on it — stateful, PULL,
context and offset. There is no lock here and there is nothing to ack, which is why the whole of §4.4
has to be taught twice: once for a broker that can hold a message back, once for one that cannot.

---

---

## 4.2 Sending and Receiving

*How do I send a message, and how do I receive one?*

#note: RabbitMQ Quick Start lands here — exchanges, bindings and queues are the concrete
realisation of everything this sub-section describes abstractly. See `exercises/Quick-Start-RMQ.pptx`
and `script/RMQ/*.md`.

### Slide: Channels


A **channel** is a virtual pipe that connects producer and consumer.

- A logical address (topic or routing key).
- Messaging is a "pipe", not a "bucket".
- **Unidirectional.** Two-way traffic is **two channels**, and the sender names the reply channel.
- One-to-One or One-to-Many.

Presenter notes: A channel is a *logical* view, not physical — the virtual pipe down which messages flow, addressed by a topic or routing key. Middleware may implement channels differently (in-memory, on sender/receiver, or a distributed DB) but that's hidden from producer/consumer. Channels are one-way because we do not consume our own messages. Point-to-Point (one-to-one) or Publish-Subscribe (one-to-many). Not a bucket: a receiver knows what it wants and the sender knows what it is sending.

### Slide: Point-to-Point Channel


Only one consumer receives any message. With multiple consumers, the channel ensures only one succeeds, so receivers need not coordinate.


#image: (s49) diagram — Point-to-Point Channel, sender to a single receiver  [→ resources/eip-point-to-point.png]

Presenter notes: The channel locks a message until the consumer acks/nacks or times out. On ack it is deleted; while locked, other consumers read past it. This lets us scale out with multiple consumers while only one gets each message. If timed-out messages return to the channel, consumers must tolerate duplicates. (EIP reference.)

### Slide: Publish-Subscribe Channel


Delivers a copy of each message to every subscriber. A publisher sends to one input channel, replicated onto many output channels, one per subscriber.


#image: (s51) diagram — Publish-Subscribe Channel, one input channel replicated onto an output channel per subscriber  [→ resources/eip-publish-subscribe.png]

Presenter notes: Each output channel behaves like a point-to-point channel — a consumer receives a message once, and with multiple listeners the middleware uses locking + read-past. Pub-sub allows eavesdropping — a firehose of all channels can act like a message store. Both a channel-based and a router-based approach are often shorthanded as "publish-subscribe". (EIP reference.)

### Slide: Datatype Channel


Use a separate channel per message schema so all messages on a channel share the same schema.


#image: (s50) diagram — Datatype Channel, a separate channel per message type (Query, Price Quote, Purchase Order)  [→ resources/eip-datatype-channel.png]

Presenter notes: How does a consumer know how to deserialize a message? Knowing the channel tells it the type. Otherwise the consumer must inspect header/body to determine type and look up how to deserialize — unneeded complexity if a separate channel works. The reason *not* to use one: messages that must be processed in sequence but have different, non-unifiable schemas. (EIP reference.)

### Slide: Message Endpoint


How does an application connect to a channel to send and receive?


#image: (s55) diagram — Message Endpoint connecting an application to a message channel  [→ resources/eip-message-endpoint.png]

Presenter notes: We want to separate messaging concerns from domain concerns — a developer shouldn't need to know middleware, formats, or channels. Application code just knows it has data to send or expects data. The **Message Endpoint** takes that data, makes a message, and sends it on a channel; on receipt it extracts contents and gives them to the application meaningfully. Endpoint code is custom to the middleware's client API. (EIP reference.)

### Slide: Messaging Gateway


Within the endpoint, encapsulate the middleware-access code in a **Messaging Gateway**, isolating all middleware dependencies into one component so the domain is isolated from messaging concerns.


#image: (s56) diagram — the Messaging Gateway inside the endpoint, the only component that knows which broker this is  [→ resources/eip-messaging-gateway.png]

Presenter notes: Gateway vs. Endpoint: the endpoint *contains* the gateway but may also run a message pump, map messages to domain types, and call application code — which is what the picture shows. The gateway only abstracts middleware interaction. An endpoint may support multiple middleware offerings, the gateway abstracting each so application code can switch middleware without changing. (EIP reference.)

---


---

## 4.3 The Message Pump

*How do I keep receiving — looping on the receiver.*

### Slide: The Message Pump

The code that takes a message from a channel and delivers it to application code, running in a loop
until cancelled: **Get → Translate → Dispatch → Handle**.

**Each stage fails in its own way.** That is why a message which is never going to be handled has four
different places to end up.

#image: diagram — the four-stage pump in a loop, with each stage's failure routed away: deliver to a dead letter channel, understand to an invalid message channel, dispatch to an error log, and a thrown handler to a requeue with a limit  [→ resources/eip-message-pump.png]

Presenter notes: The loop takes a message, translates the body into a type the application understands,
looks up the handlers registered for that type, and dispatches. Control passes from the endpoint to
application code. **Walk the four risers on the picture and say what each one costs.** A failure to
dispatch means the application is misconfigured: log it, do **not** ack, and shut down, because acking
would lose the message and carrying on would lose the next one too. An unrecoverable application error is
the opposite — ack to remove it, because replaying it would fail the same way, and log it; processing
continues. A transient error is requeued, usually with a delay, up to a limit, and past the limit it is
treated as unrecoverable. That limit is the poison-pill guard.

### Slide: Translate and Dispatch

Two of those four stages are driven by a registry: **Translate** looks up a **Message Mapper**,
**Dispatch** looks up a **handler**.

- A **Message Mapper** converts between a message and a domain object.
- A **handler** is your code, subscribed to the channels the endpoint listens on.

#image: diagram — the same four-stage pump, with a Message Mapper Registry under Translate and a Handler Registry under Dispatch  [→ resources/eip-translate-and-dispatch.png]

Presenter notes: The endpoint registers mappers per channel, which is what a datatype channel is for. The mapper is the seam the exercises are checked against: if a handler's signature has a broker type in it, the mapper has not finished its job.

### Slide: Polling Consumer


The message pump makes an explicit call to check for messages. Consumes a thread even when idle, but needs no held-open connection to the middleware. (EIP reference.)


#image: (s60) diagram — Polling Consumer explicitly checking a channel for messages  [→ resources/eip-polling-consumer.png]

### Slide: Event Driven Consumer


The pump registers a callback that the middleware invokes when a message is available. Doesn't consume a thread, but requires a held-open connection (or the app to serve middleware requests). (EIP reference.)


#image: (s61) diagram — Event-Driven Consumer invoked by the middleware on message arrival  [→ resources/eip-event-driven-consumer.png]

### Slide: Service Activator

**The line between the messaging code and your code.**

Everything in this sub-topic so far — endpoint, pump, mapper, registries — is the **messaging gateway**.
The **handler** is your code. The Service Activator is the join, and its whole job is that the handler
**does not know the pump exists**.

- The pump has a message; the **Message Mapper** has already turned it into a domain object.
- The activator makes an ordinary **synchronous, in-process method call** into your code, usually through
  a service layer.
- The handler takes a domain type and returns, or throws. No channel, no broker, no headers, no ack.

▎ Your handler is not a message handler. It is a method that happens to be called by one.

- **Dispatch** is hard-coded to one service, or reflective on the message type — which is what the
  *Handler Registry* on *Translate and Dispatch* is for.
- **One-way** (request only) or **two-way** (Request-Reply).
- **Because nothing in the handler is messaging-aware, anything else can call it too** — a developer
  test, an HTTP endpoint, a gRPC service. Useful, and worth calling out; but it is a *consequence* of the
  separation, not the reason for it.

#image: (s62) diagram — the Service Activator as the line between the messaging gateway and the handler  [→ resources/eip-service-activator.png]

Presenter notes: **The point is the separation**, not the testability: the gateway owns everything about
messaging, and the handler is independent of it. Being able to invoke application code from callers other
than the pump — developer tests, for one — *follows* from that, and lands better as evidence for the
separation than as the headline. The sentence to say out loud is that the gateway handles all messaging
details **so the service does not know it is invoked via messaging at all.**

#note: **The exercises show this.** The handler signature in the exercise repos is the proof — a
plain method over a domain type, with nothing messaging-shaped in it. Point at the actual code in §4.2's
RMQ Quick Start rather than asserting it here; wire the specific file references in during Phase 3.

### Slide: Competing Consumers

If the **Rate of Arrival** of messages (RoA) exceeds the **Rate of Consumption** (RoC), your channel
backs up and the age of any message in it increases. At some point the time a message waits in the
channel becomes unacceptable.

You solve this by **competing consumers** — but *the implementation differs between queues and streams*,
and so does what it costs you.

#image: (s63) diagram — competing consumers draining a channel that is backing up  [→ resources/eip-message-dispatcher.png]

Presenter notes: Get the arithmetic said out loud: RoC is one over the time to handle a message and ack
or nack it, per consumer. If RoA exceeds RoC and it is not a burst, you never catch up — adding
consumers is the only lever, because the other two are someone else's code. Ask whether they also have a
**deadline**: a channel that drains eventually can still be useless. *Competing Consumers on a Queue*
and *on a Stream* are the same answer on the two brokers, and the difference between them is the whole
reason §4.1 made you choose one.
(EIP reference.)

### Slide: Competing Consumers on a Queue

Add consumers to the same queue. The broker's **lock** does the rest.

- A consumer takes the next message and **locks** it — *this item is being processed*.
- Another consumer **reads past** the locked one and picks up the next item.
- Nothing says which of them finishes first, so **you have sacrificed ordering** to get the throughput.

▎ Read-past buys you throughput. It spends your ordering to do it.

#image: diagram — three competing consumers on one queue, each holding a locked message, one still waiting  [→ resources/qs-queue-competing.png]

Presenter notes: This is the lock from §4.1 doing the work it exists for. Push on the ordering cost,
because rooms consistently under-rate it: two consumers, two messages for the same customer, and nothing
in the system decides which lands first. If they need ordering they do not need a bigger queue, they
need *Competing Consumers on a Stream*.

### Slide: Competing Consumers on a Stream

There is no lock, so there is no read-past. You scale by **partitioning**.

- **Partition by a key** — consistent hashing puts same-key records in the same partition.
- **Each partition has one consumer**, and each consumer keeps its own offset.
- Order holds inside a partition, so **you keep ordering** for everything that shares a key.
- The price: **no delay and no read-past.** A slow record holds up its partition, and there is nothing
  to skip it with.

▎ On a queue you spend ordering to buy throughput. On a stream you spend the read-past instead.

#image: diagram — a stream split into three partitions, one consumer and one offset store per partition  [→ resources/qs-stream-partitions.png]

Presenter notes: Choose the key deliberately: it has to be the thing whose order matters — the entity
id, not the message type — and it has to spread, or one partition takes all the traffic and you have
scaled nothing. Say what happens when a record will not process: on a queue someone else reads past it,
on a stream the partition stops. That is the same trade the room will meet again on the error slides in
§4.4, and it is why they are taught twice there.


### Slide: Worked Example — the Task Queue

The pump and competing consumers, as an application shape. **Offloading work from a request path.**

- The web server puts the work on a **queue** and returns immediately.
- The queue **stores** the work until we are ready to consume it — we can throttle to prevent surges.
- A backend application does the long-running or CPU-intensive work, freeing the web server to service
  new requests.
- We **scale out** the backend with competing consumers so the queue does not back up.

**What it buys:** the web server stays responsive when the backend is slow, overwhelmed, or down. The
work is not lost — it waits.

▎ This is the shape the opener promised. One team, one service, one queue — and here are its parts.

#image: architecture diagram — browser, web server and three competing consumers inside one service boundary, sharing one database, with the work waiting on a channel between them  [→ resources/task-queue-shape.png]

Presenter notes: The opener kept the *want* — *Robust — Guaranteed Delivery* — and this is the mechanism,
which belongs here, where the parts have names. Everything that slide gestured at vaguely in the first ten
minutes is now vocabulary the room owns: channel, pump, competing consumers. **Call the callback out
loud** — this is the promise from the first ten minutes, and now they can read how it is kept.

### Slide: Task Queue — HTTP Flow

How this looks over HTTP — and most delegates have not used it.

- Return **202 Accepted** — we have your work request and we will not lose it. It is HTTP's own way of
  saying *store and forward*.
- Enqueue a work item for the request.
- Return a **Location** header so the caller can monitor progress: a link to the resource — 404 until it
  is created — and a link to a progress page backed by a KV store where we note progress.
- The backend does the work at a sustainable pace and updates the KV store as it goes.

#image: diagram — the same shape over HTTP: the work path runs client → web server → channel → worker, and the client's read path returns to a progress KV store it never posted to  [→ resources/task-queue-http.png]

▎ §4.4 is how you keep that promise.

Presenter notes: Ask who has returned a 202 in anger — usually a handful of hands. This is one of the most immediately usable things in the course: guaranteed delivery with no new
infrastructure and no reorganisation, expressed in a protocol everyone in the room already ships. The
callout is the set-up for §4.4 — the web server has *promised* not to lose the work, and the very next
sub-topic is the fact that nothing so far actually guarantees it. **The exercise slot now sits between
the two**, so land the promise before they go to the keyboard and pick it up again when they come back:
they will have built the pump that is about to be shown to be unreliable.

---

### Slide: Exercise Material — Introduction & RMQ

Readme, videos, scripts & slides. Introduction to Exercises; Quick Start RabbitMQ — the AMQP 0-9-1
primitives (exchanges, bindings, queues) behind the channels of §4.2.

**Then build the thing you have just been shown:** a producer, and a consumer with a message pump —
mapper, handler registry, and a handler that knows nothing about messaging.

#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)  [→ resources/dont-panic.jpg]

Presenter notes: **Get RMQ up before they need it** — the compose file is in the pack and the pull is
slow on venue wifi, so say this before the break, not after it. The Quick Start covers exchanges,
bindings and queues, which is §4.2's channel material in AMQP's own vocabulary; it is precursor
reading, not an exercise. The exercise itself is this sub-topic made real, and the piece to watch for
is the last one: **a handler that takes a domain type and returns**, with the messaging kept on the
other side of the mapper. If their handler has a broker type in its signature, the mapper is not
finished.

---

---

## 4.4 Guaranteed Delivery

*How do I stop losing messages — on the way out, and on the way in?*

### Slide: Guaranteed Delivery

Coming from HTTP, a failed call is obvious: you get a status code, or a timeout, and you decide what
to do. Messaging hides the failure. The send returns, and you find out later — or never.

Two halves, and you need both:

- **Producer side** — did the message actually get out, given the entity write and the send are not
  in the same transaction?
- **Consumer side** — what happens to a message my code cannot process, and how do I stop it taking
  the consumer down with it?

▎ "Sent" is not "delivered", and "delivered" is not "processed".

Presenter notes: Set the expectation that these are *broker* capabilities before they are framework
features — *What Your Broker Actually Gives You*, at the end of this sub-section, comes back to what is
native versus what your framework is quietly reimplementing for you. Delegates who have only used HTTP tend to assume the library is
telling them the truth.

---

#group: The producer side — did the message get out?

### Slide: The Dual-Write Problem

No transaction spans both my write to the DB for an entity *and* my sending of a message.

- If the message send fails, downstream systems become inconsistent with upstream.
- If we reverse the operations and the message sends but the DB write fails, upstream is inconsistent.

#layout: side

#image: hand-drawn diagram — a sender writing an Entity to a database and a Message to a channel, with no shared transaction  [→ resources/Transactional No Outbox.png]

Presenter notes: Call straight back to the opener — *Messages In, Private Data, No Shared Transaction*
said this would happen; this is the first place it actually bites. There is no clever ordering that fixes it;
one of the two writes is always unprotected.

### Slide: Outbox

Instead of writing directly to the channel:

- Open a transaction, update the entity, and write the message to send to an **Outbox** table as *Pending*.
- Once sent, mark the message *Sent* in the Outbox.
- A background "sweeper" runs at an interval to flush any Pending items (over an age) from the Outbox.
- To reduce latency, also send from the application right after writing, with the sweeper as backup.

▎ The outbox guarantees at-least-once. Which is a polite way of saying: you will send duplicates.

#layout: side

#image: hand-drawn Outbox diagram — Entity and Outbox written in one DB transaction boundary, then relayed to a channel  [→ resources/Transactional With Outbox.png]

Presenter notes: **Say where the duplicate comes from, because it is no longer on the slide.** We can
fail *after* the send and *before* marking it Sent; the sweeper then finds it Pending and sends it
again. That is the whole of at-least-once, and it is what the callout means.
Do not let this land as a footnote — it is the question the **Inbox** exists to answer,
and *Inbox (Idempotency)* answers it, on the consumer side. Leave the duplicate hanging
deliberately: ask the room what they would do about it, take answers, and tell them you will come back to
it when we are on the consumer side, because that is where it gets fixed. People from an HTTP background
often assume the framework has already solved it.

### Slide: Log Tailing (Change Data Capture)

No ACID transaction across the Outbox and the entity tables? Tail the transaction log instead.

The naive version, and the one CDC tooling makes trivially easy:

> transaction log → broker. Done.

The problem: **your table schema is now your published contract.** Every column rename breaks
consumers you have never met.

What to do instead — the log tail feeds an **anti-corruption layer**: read the log, run the **mapper**,
write the *message* to the **Outbox**, and sweep exactly as before.

▎ Change Data Capture without an anti-corruption layer publishes your schema. The write to the Outbox *is* the layer.

#layout: side

#image: hand-drawn log-tailing diagram — a transaction log read into an Outbox, translated to a message on a channel  [→ resources/Log Tailing.png]

Presenter notes: **And if the broker is down the log tail blocks** — the naive version has a liveness
problem as well as a coupling one. **Walk the four steps against the picture** — read the transaction log; run the mapper,
which translates the row change into a message in your published language; write that message to the
Outbox; sweep the Outbox exactly as before. Step two is the whole of it.
This is the discussion that always happens in the room and never makes it onto the
slide — put it on the slide. CDC tooling makes step-one-straight-to-broker so easy that teams adopt it
with no thought about coupling at all. Tie it back to §Coupling explicitly: publishing your table
schema is **common coupling wearing a message's clothes** — you have rebuilt Shared Database, only now
it is asynchronous and you cannot see the consumers. The mapper plus the Outbox write is what buys you
back the data coupling you wanted.

### Slide: State Change Capture

A low-cost alternative: send the message *before* writing the entity. If the message sends, delivery is
guaranteed. Read the message back from the channel and then update the entity. The main issue: you must
cope with **eventual consistency**, which isn't always simple.

#layout: side

#image: hand-drawn diagram — receiver side: a message from the channel written to an Entity in the database  [→ resources/State Change Capture.png]

---

#group: The consumer side — what the pump cannot ack

### Slide: When the Handler Fails — Ack and Nack

The pump reads a message and calls your handler. **The handler throws.** Now what?

The pump has exactly one lever: **acknowledge** the message, or don't.

- **Ack** — I am done with this. The broker may forget it.
- **Nack** — I am not done. The broker keeps it, and will hand it to someone again.

Ack too early and a crash loses the message. Ack too late and a crash reprocesses it. **There is no third
option** — which is why at-least-once stops being a slogan on the consumer side.

Presenter notes: **Do not underestimate this conversation.** Run it as a discussion before showing
anything: ask what their consumer does today when the handler throws. The usual answers are "it logs and
moves on" — silent data loss — or "it retries forever" — the poison pill. Both are the thing the rest of
this sub-section exists to prevent, so take the answers before you offer any. This is the natural place
to define *poison message*.

### Slide: Not Acking — Requeue or Reject

Not acking is two decisions, not one. **Which one you take is a policy** — you set it in advance, and
most teams never do.

- **Requeue** — put the message back on the queue. Someone tries it again.
- **Reject** — do not process this message at all. **Delete** it on a queue; **skip** it on a stream.

Each of the two has to end somewhere:

- On a **requeue**, set a policy for how many attempts. Exceed it and the message goes to the **Dead
  Letter Channel**.
- On a **reject**, a **badly formed** message goes to the **Invalid Message Channel**.
- A **well-formed** message you reject may go straight to the **Dead Letter Channel** — by policy, and
  it is your policy.

▎ A message that is only ever nacked blocks the queue forever. Requeue and reject both have to end somewhere.

#image: diagram — a locked message and its three endings: deleted on success, unlocked on failure, dead-lettered after N tries  [→ resources/qs-queue-lifecycle.png]

#note: **Forward reference — say it out loud.** *Invalid Message Channel*, *Requeue with Delay* and
*Dead Letter Channel* all need **per-message acknowledgement**, and a stream does not have one.
*Streams — No Requeue or DLQ* pays that off and *What Your Broker Actually Gives You* makes it concrete.

Presenter notes: **This slide is what turns the next three from a list of patterns into two answers.**
Requeue is "not now"; reject is "not ever, not by me". The limit on a requeue and the destination of a
reject are both configuration, and teams routinely ship neither — which is how a poison message ends up
retried until someone notices the lag. Ask which of the two their broker does by default; most rooms
find out they have been requeueing forever.


### Slide: Invalid Message Channel

What happens when a *delivered* message cannot be understood (missing headers, wrong content type,
schema mismatch)?

**Needs from the broker:** the ability to take the message off the channel and put it somewhere else
*without* pretending it was processed.

▎ Dead Letter: we could not deliver it. Invalid Message: we delivered it and could not read it.

#layout: side

#image: (s53) diagram — Invalid Message Channel: the receiver routes aside a message it cannot understand  [→ resources/eip-invalid-message-channel.png]

Presenter notes: Retrying a message that cannot be read keeps failing — it becomes a "poison pill",
blocking one consumer or being choked on by many. But silently discarding it risks data loss: a
misconfigured producer may have put a perfectly good message on the wrong channel. So route it aside
rather than dropping it. **Some middleware conflates the two terms** — RabbitMQ calls rejected messages
"dead letter", which matters because the *Failing Well* exercise uses RMQ's own dead-letter exchange.

### Slide: Requeue with Delay — a Queue Capability

Transient failure is not the same as permanent failure. The downstream service is restarting; the
database is failing over. The message is fine — you just tried at a bad moment.

- If work isn't done/acked, make it available again to the next consumer.
- If it failed for a transient reason, **delay** to let that pass.
- After a number of re-queues, move to a dead-letter channel.

**Needs from the broker:** per-message acknowledgement, a redelivery mechanism, and a way to hold a
message back for a period. **The lock is what supplies all three, and only a queue has one** — which is
what the slide after Dead Letter Channel is about.

#image: diagram — a locked message at the head of a queue, unlocked and held back on a timer when it is not acked, and dead-lettered after N tries  [→ resources/qs-requeue-with-delay.png]

#note: §4.1 drew both models, so "queue" in this title is a distinction the room already has. The
stream half is its own slide two on, after Dead Letter Channel.

### Slide: Dead Letter Channel

What does the middleware do with a message it cannot deliver to the intended channel? It may move it to
a **Dead Letter Channel** for later operator review, often after retrying delivery a number of times.

**Needs from the broker:** somewhere to put the undeliverable message, and a rule for when to give up.

#layout: side

#image: (s52) diagram — Dead Letter Channel: the broker puts aside a message it could not deliver  [→ resources/eip-dead-letter-channel.png]

Presenter notes: Implementations vary (point-to-point or pub-sub). **This is the terminal state** — the
place a message goes when *Requeue with Delay* has run out of attempts, which is why it now follows rather
than precedes it. The line that separates it from the **Invalid Message Channel** is on that slide;
this is the one to point at when someone asks which of the two RabbitMQ means. (EIP reference.)

### Slide: Streams — No Requeue or DLQ

*Invalid Message Channel*, *Requeue with Delay* and *Dead Letter Channel* all needed the broker to hold
a message for you. A stream has no lock, so it has **no requeue**, no requeue-with-delay and no
dead-letter channel. What you have instead:

- **Ignore and continue** — load shedding. The record is gone and the partition moves on.
- **Retry in place** — backpressure. The partition stops until it succeeds.
- **Copy to another stream** — a delay stream or a DLQ stream, and a scheduler to feed it back.

The third one is the closest thing to requeue-with-delay, and it costs you the thing partitioning bought:
the record comes back at the **end**. **You have de-ordered the stream to get a retry.**

▎ On a queue the broker holds the message for you. On a stream, whatever holds it is code you wrote.

#image: diagram — a log and a consumer, with requeue, requeue-with-delay and dead-letter each struck out, and the three alternatives named  [→ resources/qs-stream-no-requeue.png]

Presenter notes: This is the slide that makes *What Your Broker Actually Gives You* land, and it is the
setup for the Kafka exercise: none of §4.4 is native here. Ask what their framework
does — most will find it retries in place by default, which means one bad record stops a partition and
the lag graph is the only symptom. The three alternatives are a choice about **which guarantee you are
willing to lose**: the record, the throughput, or the ordering.

### Slide: Inbox (Idempotency)

**One more thing the pump has to decide, and this one comes from the producer side: have I seen this
message before?**

The Outbox bought at-least-once, so duplicates are not a risk — they are a certainty. This is where you
pay for it.

If the message isn't idempotent (not side-effect free), use an **Inbox** to record messages *seen*
(working on) and *processed* (may fail).

- Producer-side reliability creates a consumer-side obligation — the two halves are one design.
- If the handler *is* naturally idempotent, you do not need an Inbox. Most aren't.

#image: hand-drawn Outbox→Inbox diagram — sender Outbox to channel to receiver Entity/Inbox for de-duplication  [→ resources/Inbox.png]

Presenter notes: **The Inbox is consumer-side machinery answering a producer-side consequence** — it is
part of the pump, but it only matters once we have the Outbox, which is why it sits here rather than
alongside it. Keep that callback.
Exactly-once **delivery** does not exist; exactly-once **processing** is what the Outbox/Inbox pair gives
you. It is the last item on this sub-section's list, and the only one that is not about failure.

---

### Slide: What Your Broker Actually Gives You

Everything in this sub-section is a *broker* capability first. Frameworks backfill the gaps — which is
fine, until you assume it is native and reason about failure as though it were.

| Capability | RabbitMQ (queue) | AWS SQS (queue) | Kafka (stream) |
|---|---|---|---|
| Per-message ack / lock | Ack / nack | Visibility timeout | **None** — offsets only |
| Dead letter | Dead-letter exchange, native | Redrive policy, native | **None** — framework writes a separate topic |
| Delay / retry | TTL + DLX, or delayed-message plugin | Delay queues + per-message delay, native | **None** — framework uses retry topics |
| Redelivery count | Header, by convention | Receive count, native | **None** — framework tracks it |
| Ordering | Per queue | FIFO queues only | Per partition |

▎ If your framework offers you a DLQ on Kafka, it built one. Know which of these you are relying on.

Presenter notes: This slide is the honest answer to "why does my library make this look so easy?" —
it puts a price on the queue-versus-stream distinction §4.1 drew, and it explains why the same
reliability pattern costs very different amounts on different infrastructure.
Ask the room which broker they are on and what they assumed was native. **The second exercise slot
follows this slide**, so this is the last thing they hear before making their own pump fail — which is
the right note to send them out on.

---

### Slide: Exercise Material — Failing Well

Take the pump you built and make it survive the ways this sub-topic says it will fail: a message that
**cannot be mapped**, and a message that **fails handling** *n* times. Use RMQ's own dead-letter
exchange rather than building one.

▎ Two different failures, two different answers — and the pump has to tell them apart.

#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)  [→ resources/dont-panic.jpg]

Presenter notes: **The callout is the whole exercise.** A body that will not map is never going to map,
so retrying it is a poison pill — it goes straight to the invalid message channel. A handler that
failed may simply have been unlucky, so it is requeued with delay and only dead-lettered when the count
runs out. That distinction is §4.3's *failure to understand versus failure to process*, and it is the
one thing to check they have got. **Have them watch the management console while it happens** — the
unacked count, the retry count, and the `x-death` header on what lands in the DLQ.

---

## 4.5 Queues and Streams

*The two things only one of them can do — and the summary you take away.*

**By now you have met both models and both halves of every mechanism.** What is left is the pair of
capabilities that has no counterpart on the other side, and the matrix that puts the whole comparison
on one page.

#note: **Kafka Quick Start lands here** — `exercises/Quick-Start-Kafka.pptx`, merged in the way
`Quick-Start-RMQ.pptx` merges into §4.2. This is the second half of the exercise arc: §4.3 and §4.4
taught every mechanism twice, once for a lock and once without one, and RMQ made the queue half real;
§4.5 asks delegates to get the same guarantees on a **stream**, where almost none of it is native.
*What Your Broker Actually Gives You* at the end of §4.4 is the setup for exactly that.

### Slide: Scaling Streams — Consumer Groups

You partitioned the stream in §4.3 and gave each partition a consumer. A **consumer group** is how the
broker keeps that assignment true while consumers come and go.

- Only **one consumer in a group** reads from a partition at a time — that is what protects the ordering
  partitioning bought you.
- A consumer may hold **more than one** of the group's partitions, so a group survives losing a member.

▎ Partitions decide the ordering. Consumer groups decide who is holding them right now.


#image: diagram — two partitions held by two consumers in a group, and a third consumer holding nothing  [→ resources/qs-stream-consumer-groups.png]

### Slide: Archive and Replay

Can we re-read the past? The two models answer differently, and the answer follows from what §4.1 said
each one **is**: a queue holds work to be done, and work that is done is gone.

### Slide: Queues — No Archive and Replay


With queues we delete a message once the action completes, so there's no way to replay a work request — our only option is to ask the producer to resend.


#image: diagram — a queue with the processed messages gone from the head end, and nothing left where they were  [→ resources/qs-queue-no-replay.png]

### Slide: Streams — Archive and Replay


Straightforward, because nothing is deleted: reset the consumer's offset to re-read the stream.


#image: diagram — a log with the consumer's offset marker moved backwards, the log itself unchanged  [→ resources/qs-stream-replay.png]

### Slide: Queues vs. Streams — Capability Matrix


Summary comparison across: Messaging (Discrete Event vs. Series Event), Ordering, Archive and Replay, and Requeue with Delay — for Queue vs. Stream.


#image: a queue-versus-stream matrix — what each carries, then ordering, archive and replay, requeue with delay, and lock-and-read-past, one tick and one cross on every row  [→ resources/qs-capability-matrix.png]

### Slide: Exercise Material — Introduction to Kafka

Readme, slides. Quick Start Kafka — brokers, topics, partitions, consumer groups, offsets.

Then the exercises: **take the reliability you built on a queue and get the same guarantees on a
stream.** Nothing you relied on in §4.4 is native here.


#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)  [→ resources/dont-panic.jpg]

---

---

## Conversations

*From single messages to conversations — choosing an exchange pattern.*

**Section goal:** given an interaction you need to build, choose between In-Only, Out-Only, In-Out and
Out-In — and know what each one commits you to in coupling terms.

### Slide: Messaging Participants

You can now send a message, receive it, and not lose it. Real interactions are rarely one message —
they are **conversations**, and the shape of the conversation is a design decision.

An application acts as either a **requestor** or a **provider**.

- Prefer *requestor/provider* over *producer/consumer* here, because they name the **role**: are you
  providing the API, or using it?
- A channel is **unidirectional**. **A two-way conversation needs two channels** — and that one fact
  forces every pattern in this section.

**Example.** *Provider (Store Information)* manages stores for our ecommerce site. *Requestor (Search)*
registers a store and optimizes for fast lookup on key search terms. The message `changedstore()`
indicates new store details.

Presenter notes: The problem with *producer/consumer* is that either one can be the side exposing
operations — the consumer receives a command, or the producer sends a notification — so the words tell
you nothing about who is offering the API. Say what the one-way channel costs: if you want an answer you
have to open a second channel, and that is a decision with consequences, not a detail.

### Slide: Messaging or Eventing?

The first question, before any pattern, and you met it in §4.1: **are you expressing intent, or
reporting a fact?** Here is what it decides.

| | intent — Messaging | a fact — Eventing |
|---|---|---|
| patterns available | In-Only, In-Out | Out-Only |
| who you are addressing | someone: you know who should act | nobody: the subscriber list is not yours |
| what you are coupled to | the request or command contract | the event schema |

#image: one pair of participants and three exchanges down them — In-Only and In-Out above the line, Out-Only below it with its arrow reversed, because the provider speaks first and is addressing nobody  [→ resources/conversation-messaging-or-eventing.png]

Presenter notes: They met the intent/fact split in §4.1; what is new here is the third column of
consequences, so do not re-teach the definition. Tie it back to Integration Styles instead — the same
trade, one level down: the loosest coupling on offer is the one where you do not know who is listening,
and you buy it by giving up any way to hear back. The figure makes the point physically: the arrow turns
round, and In-Out needs two of them because a channel only goes one way.

### Slide: The Four Exchange Patterns

Two questions give you all four. **Who speaks first** — the requestor, or the provider? And **is there
a message back?**

|  | no message back | a message back |
|---|---|---|
| **In** — requestor speaks first | **In-Only** (fire and forget) | **In-Out** (request-reaction) |
| **Out** — provider speaks first | **Out-Only** (notification) | **Out-In** (solicit-response) |

- *In* and *Out* are named from the **provider's** point of view: In = a message arrives, Out = a message leaves.
- Everything else in this section is one of these four, or a composition of them.

#image: the 2×2 exchange-pattern grid — who speaks first × is there a reply — with all four patterns named and glossed  [→ resources/grid-exchange-2x2.png]

#group: In-Only — fire and forget

### Slide: In-Only (Fire and Forget)

Under **In-Only**, the requestor sends a request to the provider but does not seek acknowledgment of
completion. Typically called *fire-and-forget*.

- Used where we are finished with our part in a flow and are **transferring control** — we need no response because we are done.
- **Example.** *Requestor (cashier)* has a paid-for basket it wants to turn into an order; *provider (order placement)* raises an order — `place order()`.

**What it commits you to**

- *Coupled about:* the command contract — you name an operation on someone else.
- *Must you both be up?* **No.** Store-and-forward; the provider can be down.
- Behavioural (control) coupling: you decided who should act.

#group: Out-Only — notification

### Slide: Out-Only (Notification)

Under **Out-Only**, the requestor subscribes to the provider; an operation is triggered by receipt of a
message, but it does not acknowledge the message back to the provider. Out-Only *is* the
Publish-Subscribe pattern: a provider is not aware of its consumers.

- **Example.** *Provider (Store Information)* manages stores and raises `changedstore()`. Multiple requestors subscribe: **Search** (fast lookup), **Availability** (factors for whether a store is open), **Pick-Up Locations** (where couriers pick up, and restrictions).
- Adding a fourth subscriber requires no change to the provider — that is the whole point.

**What it commits you to**

- *Coupled about:* the event schema, and nothing else. No operation is named.
- *Must you both be up?* **No.**
- The loosest coupling available — and, as *Faults, by Pattern* shows shortly, that is exactly why it
  has no fault path at all.

### Slide: Subscribe-Notify

In-Out **composed with** Out-Only: a requestor asks to subscribe to a provider, and then notifications
flow.

- `subscribe()` → the provider manages a list of subscribers → optional `confirm()` / `confirmed()` (note the role switch — the provider is now the requestor).
- Then Out-Only `notification()` messages flow; a `stop()` ends them.

**What it commits you to**

- Behavioural (control) coupling on the subscribe exchange — then the loose coupling of Out-Only for everything after it.
- The provider now holds **subscriber state**, which it did not in plain Out-Only.

Presenter notes: This is the pattern that shows the four are a *basis*, not a catalogue — real conversations are compositions. It is also the honest version of "pub-sub is loosely coupled": the subscription itself is coupled; the notifications are not.

#group: In-Out — request and reaction

### Slide: In-Out (Request-Reaction)

Under **In-Out**, the provider receives a request on one channel and returns a response — from the
triggered operation — on a *separate* channel.

- The requestor sets a **correlation id** (conversation id) in the request header; the provider returns it in the response header, so replies arriving over a separate channel can be matched to the request that caused them.
- **Example.** *Requestor (Basket)* sends `checkout()` — a command asking the cashier to price a basket. *Provider (Cashier)* takes payment for the agreed amount and turns the basket into an order, replying `successfulpayment()`.

**What it commits you to**

- *Coupled about:* both the request contract and the response contract.
- *Must you both be up?* **Not necessarily** — as long as you do not *block*. See Blocking In-Out.
- Behavioural (control) coupling, and now you hold **state**: something must remember what the correlation id refers to.

Presenter notes: The correlation id is the cheapest thing on the slide and the most consequential. The moment you need one you have a conversation with state in it — and something has to own that state across a process restart.

### Slide: Command or Query?

Command-Acknowledgement and Query-Result are the **same exchange pattern** — In-Out. What differs is the
**intent** of the message, and intent is what decides what you must design for.

| | Command-Acknowledgement | Query-Result |
|---|---|---|
| the requestor asks | *do this* | *tell me this* |
| example | Basket → Cashier: `checkout()` → `successfulpayment()` | Basket → Delivery: `getdeliveryfees()` → `deliverfee()` |
| provider state | changes | unchanged |
| retry is | unsafe without idempotency | naturally safe |

Both carry behavioural (control) coupling — you named the provider and the operation.

Presenter notes: Worth being explicit that the pattern catalogue does not distinguish these, and that is correct — as an exchange they are identical. It is the intent, back to *Messaging or Eventing*, that changes the design. Retry safety is the practical tell.

### Slide: In-Out — When Nothing Comes Back at All

The requestor may not receive the expected response at all. What can it do?

- Set a **timeout** within which to receive a response.
- **Retry** if no response arrives within that window (`greet()` → `greet()` → `acknowledge()`).
- Because we might send twice, the provider operation must be **idempotent**, or the consumer must **de-duplicate** already-seen messages.

#image: sequence — the requestor sends greet(), the timeout expires with nothing back, and the three things that are all still possible at that moment; then greet() again and an acknowledge()  [→ resources/conversation-timeout.png]

Presenter notes: Call back to Guaranteed Delivery — this is the Inbox pattern earning its keep. Retry is why de-duplication is not optional: at-least-once delivery and requestor-side retry are two independent sources of duplicates.

### Slide: Blocking In-Out (Request-Reply)

The requestor provides a unique **Reply-To** channel in the request header; the provider uses it for the
response, letting the requestor look up the suspended workflow — so a correlation id is not required.
**The requestor may block** on the Reply-To channel while awaiting the reply.

▎ Block, and you have rebuilt RPC on top of a message broker.

**What it commits you to**

- *Must you both be up?* **Yes.** This is the one pattern in the set that puts **temporal coupling** back.
- Availabilities multiply again — the thing we distributed to avoid, and spent Guaranteed Delivery breaking.
- You have paid the cost of a broker and kept the failure mode of a synchronous call.

**When it is still the right answer:** an interactive request where a human is waiting and there is no
useful "later" — the caller cannot do anything with a response that arrives in ten minutes.

Presenter notes: This is the callback slide for the whole day. Distributed Systems said availabilities multiply; Coupling named the axis; Integration Styles put messaging on the loose end of it; Guaranteed Delivery turned an outage into a delay. Blocking In-Out undoes all of it in one line of code. Delegates *will* reach for this because it looks like the code they already write — say so, and give them the legitimate case, so the answer is "when", not "never".

#group: Out-In — solicit and response

### Slide: Out-In (Solicit-Response)

Under **Out-In**, a provider solicits a response from a subscriber and awaits confirmation; the
subscriber confirms receipt of the provider's solicitation.

- **Example.** *Provider (Delivery)* assigns delivery requests to drivers and queries whether a courier is available — `solicit()` — usually followed by notifications of available work. *Requestor (Courier)* offers to take jobs depending on location and busyness — `ready()`.
- Use it when the provider needs to know **who is willing** before it allocates work.

**What it commits you to**

- *Coupled about:* the solicitation contract. The provider must know subscribers exist, though not who they are.
- *Must you both be up?* **No** — but the solicitation has a useful lifetime. An answer that arrives too late is worthless, which is a **timeout** problem, not an availability one.

#image: one provider soliciting two couriers down three lifelines — the first ready() lands inside the solicitation's lifetime, the second arrives after the clock and is worthless  [→ resources/conversation-out-in.png]

#group: Across all four patterns

### Slide: Faults, by Pattern

You have met all four. **You do not get to choose their fault stories — the coupling already chose.**

| pattern | what a fault can be | why |
|---|---|---|
| **Out-Only** | **Nothing. No Fault is forced.** | The provider does not know its subscribers. There is nobody to tell — and if it *did* know it would be coupled to them, and you would have traded away the property you chose pub-sub for. |
| **In-Only** | **No Fault**, or **Message Triggers Fault** (Robust In-Only) — a fault on a *reverse channel*, because there is no later message to replace | The requestor took no response, so a fault channel is an addition, not a substitution. Add one **only if there is an action to take**. |
| **In-Out** | **Fault Replaces Message** (Robust In-Out) — any message *after the first* becomes a fault instead of the normal outcome | There is already a response channel and a correlation id. The fault is a **response**, not an exception: same channel, same id, same code path. |
| **Out-In** | **Fault Replaces Message**, as for In-Out | Roles reversed, and nothing else — the provider waits. |

▎ You cannot have loose coupling and a fault path back. Pick one.

▎ The question is never "should we handle faults?" It is **"is there an action the requestor would take?"**

Presenter notes: **The fault story falls out of the coupling you already chose** — which is the payoff of putting a coupling verdict on
every pattern slide. Teach it top-down, loosest first, so the room sees the fault path *appear* as the
coupling tightens. **There is an example for each row, and they are yours to tell, not the room's to
read.** Search cannot add a store after `changedstore()` and makes no attempt to tell Store Information —
repair is Search's problem. The cashier sends `place order()`; if order placement fails it raises
`fault()`, because the cashier may need to issue a **refund**. The Pricer sends `take payment()`; the
payment provider signals `payment error()` — and the fault must say **why** (provider issue, invalid card,
insufficient funds), because the requestor has to choose between an alternate payment method and
cancelling the order. **The decision rule is the load-bearing line** — teams reach for fault channels
reflexively, and if there is no action the requestor would take, a fault message is noise and a log line
is the right answer. No Fault is "good enough" far more often than people admit; say so. Repair on the
Out-Only row happens subscriber-side — retries, DLQs and the reconciliation they met in §4.4.

### Slide: Choosing an Exchange Pattern

The decision, in order:

1. **Intent or fact?** Fact → Out-Only, and accept No Fault. Intent → keep going.
2. **Do you need an answer?** No → In-Only. Yes → In-Out.
3. **Who starts?** If the provider needs to canvass its subscribers → Out-In.
4. **Do you need the answer *now*?** Only then Blocking In-Out — and know what you just paid.

| pattern | coupled about | both up? | fault path |
|---|---|---|---|
| Out-Only | the event schema | no | none available |
| In-Only | the command contract | no | reverse channel, if there is an action to take |
| In-Out | request + response contracts | no, unless you block | fault replaces the response |
| Out-In | the solicitation contract | no | fault replaces the response |
| Blocking In-Out | request + response contracts | **yes** | fault replaces the response |

#image: the §2 two-axis grid a third time, same artwork — with the five exchange patterns on it and Blocking In-Out alone below the line  [→ resources/grid-exchange-patterns.png]

Presenter notes: Third appearance of the grid — §2 introduced it, §3 plotted the integration styles on it, and now the exchange patterns land on it too. The repetition is deliberate: it is the one picture that carries the argument of the day, and delegates should be able to draw it from memory by the end.

---

## Designing Messages

*What goes in a message, and how the receiver gets the rest.*

**Section goal:** given a message to design, choose what to put in it — and know how the receiver gets
whatever you left out, and what that costs in availability.

---

## 6.1 Fat and Skinny Messages

*Normalising the message: inline it, reference it, or replicate it.*

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

---

## 6.2 Reference Data

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

#image: diagram — Provider A serving a hit from its reference cache, and on a miss making a synchronous request()/reply() round trip to Provider B  [→ resources/eip-get-on-demand.png]

Presenter notes: This is the Day 1 argument arriving inside message design. The lookup is a synchronous call in the middle of a message flow, so availabilities multiply again — and only on the unlucky path, which is exactly what makes it hard to catch in testing.

### Slide: Content Enricher — Someone Else Does the Lookup

A **Content Enricher** is a filter step that adds required data the publisher did not include: it
listens on the channel, fetches what is missing, and republishes the message complete.

- A new order carries an `AccountId`, but shipping needs the customer's address. The enricher adds the
  address, and the shipping consumer then has what it needs.
- Especially common in microservices, where each service holds only its own data and something has to do
  the join.

▎ The enricher does not remove the lookup. It moves it — and the availability sum moves with it.

#image: diagram — Content Enricher augmenting a message from an external resource  [→ resources/eip-content-enricher.png]

Presenter notes: **This is the drawn form of the slide before it.** Make the callout the point:
teams reach for an enricher believing it decouples them, when all it has done is put a third party in the
chain — A now depends on the enricher *and* B. Same arithmetic, one hop further away, and now it fails
somewhere nobody owns.

### Slide: Get It In Advance — ECST (Event-Carried State Transfer)

Provider B **publishes** its state changes; Provider A subscribes and keeps a local copy. A never makes a
synchronous call to read it.

- The upstream provider raises a **notification** when its own entity state changes (Out-Only / pub-sub).
- The downstream provider subscribes and writes to its local cache (`cache write()`); every request then
  reads locally.
- There is **no miss path**, so there is no synchronous call in the middle of a message flow.

▎ This is the default. Prefer it to the synchronous lookup.

#image: diagram — Provider B publishing state changes on an Out-Only channel, Provider A writing them to a local copy, and no call back to anyone  [→ resources/eip-ecst.png]

Presenter notes: **Teach this as the recommendation, not a warning.** Land the mechanism first and let
the room notice what is missing from it: there is no miss path at all, so there is no synchronous call
anywhere in the flow. The two slides that follow are the *why* and the *cost* — do not pre-empt them here.

### Slide: Why It Holds Up in Practice

- **Latency is not the problem people expect it to be.** Propagation is a broker hop — you are behind by
  milliseconds to seconds. And this is *reference* data: restaurants, customers, price lists. It changes
  rarely, and rarely in a way the next message depends on.
- **Versioning is what makes it safe.** Carry **id and version**. Then "I have not seen this yet" is
  distinguishable from "I have it", and a missing version becomes a **wait** rather than a wrong answer —
  which the worked example shows.
- **You removed the temporal coupling rather than relocating it.** A stays up when B is down. Day 1
  §Coupling's *Must We Both Be Up?* arriving inside message design.

Presenter notes: In practice ECST is reliable, latency rarely causes an actual problem, and versioning
the reference data closes the gap that remains. Do not hedge it with "replicas go stale, go wrong, and
need rebuilding" — that over-states the risk. Reference data is the case where the numbers are on our
side, and each bullet is one of the three reasons why.

### Slide: Be Honest About the Trade — and Which Way It Runs

ECST chooses **availability over consistency** on purpose, and by an amount you can measure: you read a
copy that is behind by the propagation delay. The synchronous lookup is not the consistent
option — it makes the same trade on a cache hit, and then **reverses it on a miss**, when B is down and
you are not.

**What it actually costs:** you are running a replica, so you own a subscription and you must be able to
**rebuild** it — replay the stream from the beginning. That is operational work, not a correctness risk.

**When to still reach for the lookup:** the data genuinely cannot be replicated — too large, too
sensitive, or it must be fresh at the instant you read it (an authorisation or a balance check). Then take
the coupling knowingly, and put a circuit breaker on it.

Presenter notes: The sharpest line in the room is the one about which way the trade runs — delegates arrive believing the synchronous lookup is the "correct" option and the cache is the shortcut, and it is the other way round. Ask what their p99 is on a cache miss when the upstream is degraded; nobody knows, which is the point.

### Slide: Reference Data — Worked Example

*Order Fulfilment → Courier Assignment:* the request omits the restaurant pickup address; we assume Courier Assignment obtained it from Restaurant Information.

- Look up the restaurant in the local cache by **id and version**.
- If we have the restaurant but **not that version**, apply **backpressure** and retry the order after a delay.

▎ A missing version is a wait. A missing *value* would have been a wrong answer.

Presenter notes: **This slide is the proof of the previous one's claim** — it is what "particularly if you version the reference data" actually looks like. Without the version you cannot tell "I have not seen this yet" from "I have it", so staleness is invisible and you have to guess; with it, the replica knows what it does not know. Backpressure here is the same idea they meet again on Day 2 in the reactive material.

---

---

## 6.3 Event Shape

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

Presenter notes: This is the join between the two halves of the section. **ECST works because of the snapshot event** — it is what makes the next two slides possible at all, and it is the reason the previous sub-topic could recommend ECST without hedging. The rule: publish complete new versions rather than deltas.

### Slide: If Later, Stream

**If Later** lets us use a versioned Summary Event to ignore ordering errors.

- Consumer reads v1 of 12345 and handles it; reads v3 and applies it (later than v1); reads v2 and **discards** it (earlier than the already-applied v3).
- Even on a stream, non-blocking retry or guaranteed delivery via an outbox can produce out-of-order messages; If-Later also lets us shed load.
- We *cannot* use If-Later with a Domain Event — those must all be applied. With Domain Events we can only use a blocking retry and cannot shed load.

#image: diagram — a stream of versioned envelopes read left to right (12345 v1, v3, v2), a consumer applying write-if-later, and v2 discarded because v3 is already later  [→ resources/if-later-stream.png]

Presenter notes: Publish complete new versions rather than deltas, then apply "write if later" — with v0, we can write v2 even without seeing v1, because v2 is later and either overwrites or includes v1's changes; we can then safely discard v1.

### Slide: If Later, Queue

If-Later also lets messages be processed out-of-order with a queue and competing consumers.

- One consumer expects/writes v1 while another writes v2; **read-past** lets them proceed.
- A queue normally processes messages (not events), so this applies only where we use a queue.
- If a message *must* be ordered (e.g. a series of commands), use requeue-with-delay or a sequencer to re-order.

#image: diagram — a queue of versioned envelopes with two competing consumers: A takes v1, B reads past and takes v2, and both write the same replica  [→ resources/if-later-queue.png]

### Slide: Public and Private Providers

An approach to Pub-Sub where a **public** provider communicates with collaborators in other domains via a **Summary Event** aggregated from the domain events of **private** providers.

- Private providers raise granular `event()`s.
- The public provider republishes a versioned `summary()` with metadata describing the cause(s) of changes.

Presenter notes: This is how both event shapes coexist — deltas inside a domain, where ordering is cheap and the consumers are yours; snapshots across the boundary, where neither is true. It is the same public/private split as an Open Host Service.

---

---

## Closing

### Slide: Further Reading

Pointers for going deeper.

### Slide: Q&A

Questions and discussion.
