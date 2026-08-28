# Practical Messaging — Day One

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day One is **the message**, end to end. Why we distribute, the coupling and integration styles that follow, then a build order for messaging code — messages, channels and endpoints, the message pump, guaranteed delivery, and queues vs. streams. It closes on the two decisions you make with all of that: which **exchange pattern** to build, and what to put **in the message**.

Prerequisites: We use RabbitMQ and Kafka for examples. You should have Docker (or an equivalent) installed — exercises ship a Docker Compose file to spin up RMQ and Kafka.

- Course content: https://github.com/iancooper/practical-messaging
- Exercise code: C#, Python, JavaScript, Go, Java repos under github.com/iancooper/Practical-Messaging-*

---

## Distributed Systems

*What we want, and what it costs.*

#note: **Rebuilt 2026-08-28, review items D1-1 … D1-6.** Three movements. **A — what we want** (2 slides).
**B — what independent deployability commits you to** (3 slides). **C — the price, and the second thing
we want** (2 slides, handing to §Coupling). The section now deliberately **stops at the problem** —
messaging is the answer, and §Coupling → §Integration Styles → §Messaging Patterns are where it gets
given. Ian: *we want independent deployability, but here are the problems, and then the next section is
about messaging as the answer.*

#note: **Left this section in the rebuild.** *Why Distribute?* — folded into the opener as one line
(D1-1: it did not earn its weight, and it buried the lead). *Fallacies of Distributed Computing* — cut;
its one distinct contribution, the where-we-answer-it column, is now a course map on §4 *The Big Picture*
(D1-5). The two **task-queue mechanism slides** — moved to §4.3, after *Competing Consumers*, which is
what they are a worked example of (D1-6: task queues are an *answer*, and this section no longer gives
answers). Earlier revisions cut *Product Mode* and the standalone *Example — Microservices* quote.

### Slide: Easy to Change, and Robust

You will hear four reasons to distribute a system — **performance and scalability**, **availability**,
**maintainability**, and applications that are **inherently distributed**. Strip the architecture words
away and two properties are what you are actually buying:

- **Easy to change** — ship a part without shipping the whole. *Independent deployability.*
- **Robust** — keep working when something you depend on is not. *Guaranteed delivery.*

Both are bought with the same mechanism: **messages**.

▎ Two properties, one mechanism. Everything in the next two days buys one of them with messages.

Presenter notes: **This is now the opening slide** (D1-1). *Why Distribute?* used to come first and spend
a slide on the four forces before getting here; the four forces are worth ten seconds, not a slide, and
leading with them buried the lead. Say the list, then say that all four reduce to two properties, and put
the two words on the board — they are the spine of both days. **Do not mention Reactive.** Day 2 pays this
off: the Reactive Manifesto (2014) names the second property **Resilient** and claims the first in its own
words — reactive systems are "easier to develop and amenable to change". Delegates should meet that on
Day 2 as recognition, not repetition. One force to keep in your pocket: **availability** is the one that
gets qualified later — redundancy *within* a service raises it, chaining services throws the gain away.
Do not resolve it here; *The Price of Distribution* settles it.

### Slide: Easy to Change — Independent Deployability

**What we want.** Ship a part without shipping the whole. One team decides its own release candidate and
is in production in hours.

**What is in the way.** As an organisation grows to many teams, a monolith fights you. Each team branches
to avoid contention; releasing means agreeing a date and merging, which collides with everyone else's
schedule. Teams pile onto a release to avoid re-merging and re-testing upstream changes. A release takes a
couple of weeks and distracts everyone.

**Microservices are one example of buying it** — team-sized services, each with its own release train.
Each team negotiates only internally; develop on master behind a feature switch per story and go straight
to production. Delivery becomes hours, not weeks.

- They are **not the only way** to get independent deployability.
- They are **not free** — the rest of this section is the bill.

▎ "Speed wins in the marketplace" — Adrian Cockcroft, former lead architect at Netflix.

▎ Independent deployability is the whole prize. Everything from here on is about not giving it back.

#image: timeline diagram — many teams on feature branches merging into a single monolith release over ~2 weeks
#image: diagram — a monolith decomposed into independently released microservices (Alpha, Beta, Gamma), delivering in hours

Presenter notes: **Reframed (D1-2): the property is the point; microservices are an example of it.** The
slide used to read "the answer: decompose into microservices", which made the section an argument for
microservices — dated in 2026, and not this section's goal. Show the two diagrams as a before/after pair.
On the monolith side: once teams line up they merge to master and resolve conflicts; more features → more
bugs → cost and schedule overruns (assume ~30% rework); we must re-test everything because we merged
potentially incompatible changes; all teams wait on any fix, even another team's. Feature switches help
drop changes, but database/schema changes (a monolith has a shared schema) make this hard, and rollback
forces everyone out — hence "roll forward only". On the microservice side: Continuous Delivery is table
stakes; we build microservices once we grow beyond a single "two-pizza" team. The second callout is the
load-bearing line of the section — §Coupling calls straight back to it.

### Slide: Microservice — Messages In, Private Data

Independent deployability needs a **process boundary**. The next three slides are what you have committed
to by drawing one.

- The only way to complete a task within a service is to **send it a message**. Each service has its own
  accepted message types, and its own data requirements for partners submitting work.
- Encapsulated within the service is **private data**. Requests to the service do not describe the shape
  of internal data.

#image: hand-drawn diagram — a microservice with private data receiving messages over a channel; database inside

Presenter notes: **Regrouped (D1-4)** — this and the next two slides are the independent-deployability
thread, and the task-queue material used to sit between them and break it. Now the thread runs
uninterrupted: the property, then the three things the boundary commits you to.

### Slide: Microservice — No Cross-Service Transactions

- Transactions (including 2PC) may occur *within* a microservice.
- Transactions cannot occur *between* services. If you operate independently from your business partners,
  you don't exchange transactions with them. Cross-organisational transactions are avoided to prevent
  lockup of *your* database when the *other* organisation makes a mistake. Without transactions, you
  communicate through multiple messages over time.

▎ No transaction spans two services. Consistency stops being something you declare and becomes something you design.

#image: hand-drawn diagram — two microservices exchanging messages over channels, each with its own database

Presenter notes: This is the load-bearing slide of the section. Everything the two days teach — outbox,
sagas, idempotence, choreography, compensation — exists because this sentence is true. Say so explicitly;
it gives delegates a spine to hang the rest of the course on.

### Slide: Collaboration — Orchestration and Choreography

- As services are independent, a collaboration comprises **orchestrations** — handlers, sagas or workflows
  *within* the services…
- …and the **choreography** — the flow of messages *between* services.

#image: hand-drawn diagram — a process of tasks sending a message via a channel to a receiver task; databases at each end

Presenter notes: Plant the two words now; Day 2 §Process Automation takes them apart properly, and the
Paper Flow exercise makes delegates feel the difference before either word is defined.

### Slide: Robust — Guaranteed Delivery

The second property, and it is the cheaper of the two.

- We want the work **not to be lost** when something we depend on is slow, overwhelmed, or down.
- **Store and forward.** The work waits somewhere durable until whoever does it is ready. The outage
  becomes a delay.
- **You do not need microservices for this one.** A single team with a single web application can have it
  on Monday — one team, one service, one queue. No reorganisation required.

▎ One team, one service, one queue. Robustness without reorganising the company.

Presenter notes: **Renamed from *Robust — Task Queues* (D1-3): guaranteed delivery is the point, and the
task queue is an example of it.** The *shape* of it — enqueue, throttle, competing consumers, and the 202
Accepted flow — moved to §4.3 (D1-6: task queues are an answer, and this section no longer gives answers).
What has to survive here is the inoculation: this slide exists so that nobody in the room can file the
whole course under "not for us, we're a monolith". Say the callout and move on; the mechanism is two hours
away and they will recognise it when it arrives.

### Slide: The Price of Distribution

Everything so far was the benefit. Here is the bill.

- **Every call is now a network call.** It can be slow, it can fail, and it can succeed while losing the
  reply.
- **You cannot use a transaction to make two services agree.** Consistency becomes something you design.
- **Your availability is now entangled with everyone you depend on** — and *how* it is entangled is a
  choice you make.

That last one is the one people get wrong:

- **Call a service and wait, and your availabilities multiply.** Four services at 99.9% leaves you at
  99.6% — before anything has actually failed.
- **Send a message and don't wait, and they don't multiply.** Guaranteed delivery means the message
  outlives their outage and is processed when they come back.

▎ Messaging doesn't remove the outage. It converts a failure into a delay.

Presenter notes: **This slide is now the glue and the close of the section (D1-5)** — it does the work
*Fallacies of Distributed Computing* was also doing, and does it better, with a number. Anyone who spotted
the availability tension in the opener gets their answer here: redundancy *within* a service raises
availability; chaining *temporally coupled* calls throws that gain away. Do the arithmetic on the board:
0.999⁴ = 0.996. Then be honest about the trade — the messaging version does not make the downstream outage
vanish, it buys an availability loss back as latency variance. That is usually a trade you can accept, and
it is the argument the whole course rests on. This is where *robust* stops being a slogan and gets a
number. **End the section here**, on the problem: hands directly to §Coupling, which asks "must we both be
up?"

## Coupling

*What architectural risks do we face from interoperability?*

### Slide: Coupling — Why It Matters

We have just argued that we split the monolith so teams can move independently. **Coupling is
what takes that back.** It decides two things we care about:

- **Can we deploy independently?** — or does my release require your release?
- **When a change lands, how far does it spread?** — who else has to be touched, tested, redeployed?

Coupling here is not a code-tidiness concern. It is a *delivery* and *availability* concern.

▎ Coupling is the tax you pay on every change, forever.

Presenter notes: Deliberate call-back to "Monoliths Do Not Scale To Many Teams". The point of
distributing was independent deployability; every kind of coupling that follows is a way of
losing it. Ask the room: when you last shipped a change, how many other teams did you have to
talk to? That number is the coupling.

### Slide: Axis 1 — What Are We Coupled *About*?

The contract between two parties. Highest coupling to lowest:

- **Content** — one party reaches into the other's internals. Across a network this shows up as
  depending on undocumented behaviour, a private endpoint, or someone else's table.
- **Common** — both share the same mutable store. Uncontrolled propagation of change; nobody
  owns the schema.
- **Control** — one party tells the other *what to do* rather than *what happened*. A
  what-to-do flag in the payload.
- **Stamp** — we share a composite structure and each use only part of it. A change to a field
  you never read can still break you.
- **Data** — we share only the elementary values we each actually need.

▎ Stamp coupling is the one you will meet every day.

#image: (s27) hand-drawn coupling scale from tight to loose — Content, Common, Control, Stamp, Data (data circled)

Presenter notes: This is Myers' structured-design scale, adapted to services — say so, and say
that **content coupling barely translates across a network boundary** rather than pretending it
does. Stamp coupling is the one that recurs all course: it is the argument for skinny messages
(§6.1 Fat and Skinny, at the end of today) and for tolerant readers (the *Managing Asynchronous
APIs* handout). Flag it now so both call-backs land.

### Slide: Axis 2 — Must We Both Be *Up*?

If both parties must be present for the communication to succeed, they are **temporally
coupled**: the availability of one becomes the availability of the other.

| | **Synchronous conversation** | **Asynchronous conversation** |
|---|---|---|
| Shape | Request → Reply | Store and forward |
| Both present? | Yes | No — pick it up later |
| Analogy | A phone call | Snail mail |
| Options | OpenAPI, GraphQL, gRPC, Thrift, SOAP | SQS, Kafka, AMQP 0-9-1 (RMQ), AMQP 1-0, MQTT, S3 |
| Temporal coupling | **Introduces it** | **Avoids it** |

▎ If my availability depends on yours, I have bought your outages.

Presenter notes: The arithmetic was done on "The Price of Distribution" (0.999⁴ = 0.996) — don't
repeat it, *name* it. What that slide showed as an availability problem is now revealed to be one
specific coupling: temporal. This is the axis that multiplies your outages, and breaking it is what
guaranteed delivery buys you.

#note: If this table is too dense on the rebuild, split it back into the original two slides
(Synchronous Conversation / Asynchronous Conversation) and keep this slide for the definition
alone. The contrast is worth one slide if it fits.

### Slide: Two Axes, Not One Scale

"Loose coupling" is not a single dial. What we are coupled *about* and whether we must both be
*up* move independently:

- **gRPC with a flat DTO** — data coupled, but temporally coupled.
- **A command message with a what-to-do flag** — control coupled, but temporally decoupled.
- **A shared database** — common coupled, and temporally decoupled.
- **An event carrying a whole entity** — stamp coupled, temporally decoupled.

▎ "Loosely coupled" is a question with two answers.

#image: NEW — a two-axis grid: *what are we coupled about?* (Content→Data) against *must we both
be up?* (temporally coupled ↔ decoupled), with the four examples above plotted on it

Presenter notes: This is the slide the next section pays off — Integration Styles plots File
Transfer, Shared Database, RPC and Messaging onto exactly this grid. It also explains why RPC's
verdict needs two words ("control **and** temporal") where the others need one.

## Integration Styles

*How do we communicate between microservices?*

*The four integration styles, after Hohpe & Woolf. Each slide pairs the style with the
conversation it implies and the coupling it buys.*

### Slide: File Transfer

One application writes a file; another reads it later. The file is the contract.

- **Asynchronous conversation**
- **Data coupling**

#image: (s32) File Transfer integration diagram — producer writes a file, consumer reads it

### Slide: Shared Database

Both applications read and write the same schema, typically through an ORM.

- **Asynchronous conversation**
- **Common coupling**

#image: (s33) Shared Database integration diagram — producer and consumer share a database via an ORM

### Slide: Remote Procedure Call

One application invokes an operation on another and waits for the result.

- **Synchronous conversation**
- **Control coupling** + **Temporal coupling**

#image: (s34) Remote Procedure Call diagram — client stub to server proxy, request/response

### Slide: Messaging

One application writes a message to a channel; another consumes it.

- **Asynchronous conversation**
- **Data coupling**

#image: (s35) Messaging integration diagram — producer writes a message to a channel, consumer reads it

### Slide: Integration Styles — Coupling Trade-offs

The four styles plotted on the grid from the previous section:

| Style | Coupled *about* | Must we both be *up*? |
|---|---|---|
| File Transfer | Data | No |
| Shared Database | Common | No |
| Remote Procedure Call | Control | **Yes** |
| Messaging | Data | No |

Two outliers — and each is an outlier on a *different* axis:

- **RPC is the only style that needs us both up.** That is the temporal axis, on its own.
- **Shared Database is the only style that couples us on common mutable state.** That is the
  "about" axis, on its own.
- **File Transfer and Messaging land in the same cell.** Coupling does not separate them —
  timeliness and granularity do.

▎ Only one of the four buys you an outage you didn't have.

#image: NEW — the two-axis grid from §Coupling, with the four integration styles plotted on it
(reuse the same grid artwork so the call-back is visual, not just verbal)

Presenter notes: This is why the previous section needed two axes rather than one scale — on a
single tight→loose dial, RPC and Shared Database would be neighbours, and the reason we reach for
messaging would be invisible. Note that Shared Database is *not* temporally coupled: the writer and
the reader need never be present at the same time. Its problem is the shared mutable schema, not
availability. Then set up the obvious question for the rest of the day: if File Transfer and
Messaging are equally loosely coupled, why build the whole course on messaging? Answer: timeliness
and granularity — which is where we go next.

---

## Messaging Patterns

*Integrating using events.* The pattern catalogue follows Hohpe & Woolf, *Enterprise Integration
Patterns*; the per-pattern prose lives in `script/Patterns/*.md` and should be merged onto these
slides during the rebuild.

#note: Ordered as a **build order**, not a catalogue order — the sequence someone from an HTTP
background needs in order to write messaging code and make it reliable. What is the unit? → how do I
send and receive one? → how do I keep receiving? → how do I stop losing them? → what kind of broker am
I on? → how do I process in stages?

### Slide: The Big Picture


A map of the messaging patterns we will cover across the day.


#image: messaging concepts diagram — application/gateway, channel adapter, channel, endpoint, and a message with header + body

#note: **Course map — the Fallacies of Distributed Computing (arrived here 2026-08-28, review item
D1-5).** The *Fallacies* slide was cut from §1 because it restated *The Price of Distribution*, which
makes the same argument better and with a number. Its one distinct contribution was the third column — a
map of where the course answers each fallacy — and that is a **build-order** artefact, not an opening-ten-
minutes artefact: it reads as a syllabus only to someone who already knows the syllabus. Fold it into
*The Big Picture* when 4a is reframed as a build order (plan §4, row 4a).

| Fallacy | What it costs you | Where we answer it |
|---|---|---|
| The network is reliable | Messages lost, duplicated, or delivered twice | Retries, idempotence, DLQ — *4.4 Guaranteed Delivery* |
| Latency is zero | Calls that block; chains that compound | Asynchronous conversation — *Coupling*, *Conversations* |
| Bandwidth is infinite | Oversized payloads, saturated links | Fat vs. skinny messages — §6 *Designing Messages* |
| The network is secure | Blindsided by what you never modelled | **Out of scope for this course** — flag it, don't pretend |
| Topology doesn't change | Endpoints that move; instances that come and go | Endpoints, discovery, competing consumers — *4.2*, *4.3* |
| There is one administrator | Conflicting policies; nobody owns the contract | Documenting the contract — the *Managing Asynchronous APIs* handout |
| Transport cost is zero | Serialisation, brokers and operations you didn't budget | Fat vs. skinny — §6 *Designing Messages*; broker choice — §4.5 *Queues and Streams* |
| The network is homogeneous | Schema and encoding mismatch across stacks | Tolerant readers and schema formats — the *Managing Asynchronous APIs* handout |

▎ Every one of these has a pattern later in the course. That is what the next two days are.

Attribution: first seven, L. Peter Deutsch, 1994; the eighth added by James Gosling, ~1997.

---

---

## 4.1 What Is a Message?

*What is a message?*

### Slide: Message Construction


A message has a **header** and a **body**.

- The **body** contains data for the consumer.
- The **header** contains metadata for any filter in the pipeline, and should indicate the format of the body.
- Break a large message into pieces as a **Message Sequence**, or use a **Claim Check**.

Presenter notes: Two processes communicating copy data — usually a byte stream — that we break into discrete units so we can tell where a message begins and ends (needed for competing consumers and pub-sub). A message = header (how to process) + body (content). Related concepts: Request-Reply (RPC over messaging, using Return Address + Correlation Identifier); Message Sequence (sequence id, position id, size/end indicator); Message Expiry / Dead Letter for slow messages; Canonical Data Format; and Format Indicator strategies — Version Number, Foreign Key, or embedded Format Document.

### Slide: Messaging and Events


Section marker: how "messaging" and "eventing" differ.

### Slide: Messaging vs. Eventing (Intent vs. Facts)


After Clemens Vasters. Two poles of message types:

- **Messaging** — Has intent. Request an answer (Query), transfer of control (Command), transfer of value. Part of a workflow/conversation. Concerned with the future.
- **Eventing** — Provides facts. Things you report on. No expectations. History/context. Concerned with the past.

### Slide: Discrete vs. Series (Eventing Types)


After Clemens Vasters. A second axis:

- **Discrete** — stateless handler, PUSH, independent, immediately actionable, part of a conversation.
- **Series** — stateful partition processor, PULL, context/offset, continuous, sequential, reports a condition, part of a monolog.

### Slide: Message Types


After Gregor Hohpe. Three core message types: **Command**, **Event (Notification)**, **Document**.

### Slide: Command / Document / Event Messages


- **Command Message** — reliably invoke a procedure in another application. Encapsulates a request as an object (GoF Command); usually sent Point-to-Point (one consumer).
- **Document Message** — reliably transfer a data structure between applications; the receiver decides what, if anything, to do with the data.
- **Event Message** — reliable, asynchronous event notification. The difference from a Document Message is timing and content — an event's contents are typically less important.

Presenter notes: RPC's advantage is synchrony (immediate, caller blocks) — but that's also its weakness: if the network is down or the remote process isn't listening, the call fails. Asynchronous command messages keep trying until the procedure is invoked. The command's state (parameters) is stored in the message.

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
- Unidirectional.
- One-to-One or One-to-Many.

Presenter notes: A channel is a *logical* view, not physical — the virtual pipe down which messages flow, addressed by a topic or routing key. Middleware may implement channels differently (in-memory, on sender/receiver, or a distributed DB) but that's hidden from producer/consumer. Channels are one-way (we don't consume our own messages); bi-directional messaging uses two channels (the reply channel usually communicated by the sender). Point-to-Point (one-to-one) or Publish-Subscribe (one-to-many). Not a bucket: a receiver knows what it wants and the sender knows what it is sending.

### Slide: Point-to-Point Channel


Only one consumer receives any message. With multiple consumers, the channel ensures only one succeeds, so receivers need not coordinate.


#image: (s49) EIP diagram — Point-to-Point Channel, sender to a single receiver  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/PointToPointChannel.html]

Presenter notes: The channel locks a message until the consumer acks/nacks or times out. On ack it is deleted; while locked, other consumers read past it. This lets us scale out with multiple consumers while only one gets each message. If timed-out messages return to the channel, consumers must tolerate duplicates. (EIP reference.)

### Slide: Publish-Subscribe Channel


Delivers a copy of each message to every subscriber. A publisher sends to one input channel, replicated onto many output channels, one per subscriber.


#image: (s51) EIP diagram — Publish-Subscribe Channel, publisher to multiple subscribers  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/PublishSubscribeChannel.html]

Presenter notes: Each output channel behaves like a point-to-point channel — a consumer receives a message once, and with multiple listeners the middleware uses locking + read-past. Pub-sub allows eavesdropping — a firehose of all channels can act like a message store. Both a channel-based and a router-based approach are often shorthanded as "publish-subscribe". (EIP reference.)

### Slide: Datatype Channel


Use a separate channel per message schema so all messages on a channel share the same schema.


#image: (s50) EIP diagram — Datatype Channel, a separate channel per message type (Query, Price Quote, Purchase Order)  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/DatatypeChannel.html]

Presenter notes: How does a consumer know how to deserialize a message? Knowing the channel tells it the type. Otherwise the consumer must inspect header/body to determine type and look up how to deserialize — unneeded complexity if a separate channel works. The reason *not* to use one: messages that must be processed in sequence but have different, non-unifiable schemas. (EIP reference.)

### Slide: Message Endpoint


How does an application connect to a channel to send and receive?


#image: (s55) EIP diagram — Message Endpoint connecting an application to a message channel  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageEndpoint.html]

Presenter notes: We want to separate messaging concerns from domain concerns — a developer shouldn't need to know middleware, formats, or channels. Application code just knows it has data to send or expects data. The **Message Endpoint** takes that data, makes a message, and sends it on a channel; on receipt it extracts contents and gives them to the application meaningfully. Endpoint code is custom to the middleware's client API. (EIP reference.)

### Slide: Messaging Gateway


Within the endpoint, encapsulate the middleware-access code in a **Messaging Gateway**, isolating all middleware dependencies into one component so the domain is isolated from messaging concerns.


#image: (s56) EIP diagram — Messaging Gateway between an application and the messaging system  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingGateway.html]

Presenter notes: Gateway vs. Endpoint: the endpoint *contains* the gateway but may also run a message pump, map messages to domain types, and call application code. The gateway only abstracts middleware interaction. An endpoint may support multiple middleware offerings, the gateway abstracting each so application code can switch middleware without changing. (EIP reference.)

---


### Slide: Exercise Material — Introduction & RMQ

Readme, videos, scripts & slides. Introduction to Exercises; Quick Start RabbitMQ — the AMQP 0-9-1
primitives (exchanges, bindings, queues) behind everything §4.2 just described abstractly.


#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)

---

---

## 4.3 The Message Pump

*How do I keep receiving — looping on the receiver.*

### Slide: The Message Pump


The code that takes a message from a channel and delivers it to application code, running in a loop until cancelled: **Get → Translate → Dispatch → Handle**.

Error routing:

- Failure to *deliver* (middleware) → Dead Letter Channel.
- Failure to *understand* (translate) → Invalid Message Channel.
- Failure to *dispatch* (unexpected/misconfiguration) → Error Log; unrecoverable exception → shut down (don't ack, to avoid losing data).
- Recoverable exception → requeue to a retry limit; beyond the limit, treat like an unrecoverable exception.

Presenter notes: The loop takes a message, translates the body into an app-understood type, looks up registered handlers for that type, and dispatches. Control passes from endpoint to application code. Unrecoverable app errors → ack to remove (replaying would repeat the failure) and log; processing may continue. Transient errors → requeue (usually with delay) up to a limit to avoid poison pills.

### Slide: Translate and Dispatch


Two registries drive the pump: a **Message Mapper Registry** (look up the mapper) and a **Handler Registry** (look up the handler).

Presenter notes: A **Message Mapper** converts domain objects to/from messages, so the domain need not know messaging formats and vice-versa. The endpoint registers mappers per channel and uses a datatype channel. Application code that runs in response is the **handler**, subscribed to the channels the endpoint listens on.

### Slide: Polling Consumer


The message pump makes an explicit call to check for messages. Consumes a thread even when idle, but needs no held-open connection to the middleware. (EIP reference.)


#image: (s60) EIP diagram — Polling Consumer explicitly checking a channel for messages  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/PollingConsumer.html]

### Slide: Event Driven Consumer


The pump registers a callback that the middleware invokes when a message is available. Doesn't consume a thread, but requires a held-open connection (or the app to serve middleware requests). (EIP reference.)


#image: (s61) EIP diagram — Event-Driven Consumer invoked by the middleware on message arrival  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/EventDrivenConsumer.html]

### Slide: Service Activator


Lets application code be invoked by callers *other* than the pump — useful for developer tests, or serving the same code over HTTP/gRPC.


#image: (s62) EIP diagram — Service Activator invoking a service for request-reply  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingAdapter.html]

Presenter notes: The activator invokes app code independent of the messaging endpoint — a synchronous, non-remote method call, usually via a service layer. It can be hard-coded to one service or use reflection to invoke the service indicated by the message, handling all messaging details so the service doesn't know it's invoked via messaging. Can be one-way (request only) or two-way (Request-Reply). (EIP reference.)

### Slide: Competing Consumers


To stop a channel backing up, consume faster than messages arrive by adding consumers.


#image: (s63) EIP diagram — Message Dispatcher / competing consumers distributing numbered messages to performers  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageDispatcher.html]

Presenter notes: Compare arrival rate to consumption rate (time to ack/nack). If arrival exceeds consumption and it isn't a burst, you never catch up. You may also need to process within a deadline. Solution: more consumers. The queue hands a message to only one consumer, locking it while processed, unlocking on failure, and letting waiting consumers read past locked messages. Caveat: competing consumers break in-sequence processing (lock + read-past de-orders). If order matters and arrival exceeds consumption, **partition** using consistent hashing so order is preserved within a partition and per-partition arrival ≤ single-consumer consumption. (EIP reference.)


### Slide: Worked Example — the Task Queue

The pump and competing consumers, as an application shape. **Offloading work from a request path.**

- The web server puts the work on a **queue** and returns immediately.
- The queue **stores** the work until we are ready to consume it — we can throttle to prevent surges.
- A backend application does the long-running or CPU-intensive work, freeing the web server to service
  new requests.
- We **scale out** the backend with competing consumers so the queue does not back up.

**What it buys:** the web server stays responsive when the backend is slow, overwhelmed, or down. The
work is not lost — it waits.

▎ One team, one service, one queue. Robustness without reorganising the company.

#image: hand-drawn architecture diagram — browser/web server enqueues work onto a channel; a backend Sender/Receiver maps messages to data; databases at each end

Presenter notes: **Moved here from §1 (review items D1-3 / D1-6, 2026-08-28).** §1 kept the *want* —
*Robust — Guaranteed Delivery* — and this is the mechanism, which belongs where the parts have names.
Everything the slide gestured at vaguely in the first ten minutes is now vocabulary they own: channel,
pump, competing consumers. Call the callback out loud — this is the slide from the first ten minutes,
and now they can read it. Ian's condition for keeping the task queue at all was that it earn its place in
Messaging Patterns; this is where it does.

### Slide: Task Queue — HTTP Flow

How this looks over HTTP — and most delegates have not used it.

- Return **202 Accepted** — we have your work request and we will not lose it. It is HTTP's own way of
  saying *store and forward*.
- Enqueue a work item for the request.
- Return a **Location** header so the caller can monitor progress: a link to the resource — 404 until it
  is created — and a link to a progress page backed by a KV store where we note progress.
- The backend does the work at a sustainable pace and updates the KV store as it goes.

#image: hand-drawn diagram of the task-queue HTTP flow — client, queue channel, backend worker, and a KV/progress store

Presenter notes: **Moved here from §1 (D1-6).** Ask who has returned a 202 in anger — usually a handful of
hands. This is one of the most immediately usable things in the course: it is guaranteed delivery with no
new infrastructure and no reorganisation, expressed in a protocol everyone in the room already ships.

#note: **Placement to settle in D1-8.** These two arrived from §1 and are parked at the end of §4.3
because the task queue *is* the pump plus competing consumers. D1-8 reworks §4.4 around the producer /
consumer split, and may want the 202 flow there instead — it is as much a guaranteed-delivery story as a
pump story. Decide it there, not here.

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
features — the last slide of this sub-section comes back to what is native versus what your framework
is quietly reimplementing for you. Delegates who have only used HTTP tend to assume the library is
telling them the truth.

### Slide: The Dual-Write Problem

No transaction spans both my write to the DB for an entity *and* my sending of a message.

- If the message send fails, downstream systems become inconsistent with upstream.
- If we reverse the operations and the message sends but the DB write fails, upstream is inconsistent.

#image: hand-drawn diagram — a sender writing an Entity to a database and a Message to a channel, with no shared transaction  [→ resources/Transactional No Outbox.png]

Presenter notes: Call straight back to §Distributed Systems — "No Cross-Service Transactions" said this
would happen; this is the first place it actually bites. There is no clever ordering that fixes it;
one of the two writes is always unprotected.

### Slide: Outbox

Instead of writing directly to the channel:

- Open a transaction, update the entity, and write the message to send to an **Outbox** table as *Pending*.
- Once sent, mark the message *Sent* in the Outbox.
- A background "sweeper" runs at an interval to flush any Pending items (over an age) from the Outbox.
- To reduce latency, also send from the application right after writing, with the sweeper as backup.

But look at what we just bought:

- We can fail *after* the send and *before* marking it Sent.
- The sweeper then finds it Pending and sends it again.

▎ The outbox guarantees at-least-once. Which is a polite way of saying: you will send duplicates.

#image: hand-drawn Outbox diagram — Entity and Outbox written in one DB transaction boundary, then relayed to a channel  [→ resources/Transactional With Outbox.png]

Presenter notes: Do not let this land as a footnote — it is the question the next slide exists to
answer. Ask the room what they would do about it before showing them. People from an HTTP background
often assume the framework has already solved it.

### Slide: Inbox (Idempotency)

The answer to the duplicates the Outbox just guaranteed.

If the message isn't idempotent (not side-effect free), use an **Inbox** to record messages *seen*
(working on) and *processed* (may fail).

- Producer-side reliability creates a consumer-side obligation — the two halves are one design.
- If the handler *is* naturally idempotent, you do not need an Inbox. Most aren't.

#image: hand-drawn Outbox→Inbox diagram — sender Outbox to channel to receiver Entity/Inbox for de-duplication  [→ resources/Inbox.png]

Presenter notes: Worth being explicit that the Inbox is consumer-side machinery answering a
producer-side consequence — that is why it sits here rather than with the consumer patterns. Exactly
once delivery does not exist; exactly once *processing* is what the Outbox/Inbox pair gives you.

### Slide: Log Tailing (Change Data Capture)

We may not have a database that supports ACID transactions across the Outbox and entity tables. So
tail the transaction log instead.

The naive version — and the one most CDC tooling makes trivially easy:

> transaction log → broker. Done.

The problem: **your table schema is now your published contract.** Every column rename is a breaking
change for consumers you have never met. And if the broker is down, the log tail blocks.

What to do instead — the log tail feeds an **anti-corruption layer**:

1. Read the transaction log.
2. Run the **mapper** — translate the row change into a *message*, in your published language.
3. Write that message to the **Outbox**.
4. Sweep the Outbox exactly as before.

▎ Change Data Capture without an anti-corruption layer publishes your schema. The write to the Outbox *is* the layer.

#image: hand-drawn log-tailing diagram — a transaction log read into an Outbox, translated to a message on a channel  [→ resources/Log Tailing.png]

Presenter notes: This is the discussion that always happens in the room and never makes it onto the
slide — put it on the slide. CDC tooling makes step-one-straight-to-broker so easy that teams adopt it
with no thought about coupling at all. Tie it back to §Coupling explicitly: publishing your table
schema is **common coupling wearing a message's clothes** — you have rebuilt Shared Database, only now
it is asynchronous and you cannot see the consumers. The mapper plus the Outbox write is what buys you
back the data coupling you wanted.

### Slide: State Change Capture

A low-cost alternative: send the message *before* writing the entity. If the message sends, delivery is
guaranteed. Read the message back from the channel and then update the entity. The main issue: you must
cope with **eventual consistency**, which isn't always simple.

#image: hand-drawn diagram — receiver side: a message from the channel written to an Entity in the database  [→ resources/State Change Capture.png]

### Slide: Dead Letter Channel

What does the middleware do with a message it cannot deliver to the intended channel? It may move it to
a **Dead Letter Channel** for later operator review, often after retrying delivery a number of times.

**Needs from the broker:** somewhere to put the undeliverable message, and a rule for when to give up.

#image: (s52) EIP diagram — Dead Letter Channel, an undeliverable message rerouted to a dead-letter channel  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html]

Presenter notes: Implementations vary (point-to-point or pub-sub). Note the common confusion between a
Dead Letter Channel and an Invalid Message Channel — discussed next. (EIP reference.)

### Slide: Invalid Message Channel

What happens when a *delivered* message cannot be understood (missing headers, wrong content type,
schema mismatch)?

**Needs from the broker:** the ability to take the message off the channel and put it somewhere else
*without* pretending it was processed.

#image: (s53) EIP diagram — Invalid Message Channel, receiver routes an unprocessable message aside  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/InvalidMessageChannel.html]

Presenter notes: The middleware delivered it, but app code can't process it. Retrying keeps failing — it
risks becoming a "poison pill", blocking a single consumer or being choked on by many. But silently
discarding risks data loss (maybe a misconfigured producer/consumer used the wrong channel and the
message was good). So move it to an **Invalid Message Channel**. Well-formed messages that merely cause
application errors are *not* invalid messages — treat those as application errors. Dead Letter =
couldn't be delivered; Invalid Message = delivered but not understood. Some middleware (e.g. RabbitMQ)
conflates the terms, using "dead letter" for rejected messages.

### Slide: Requeue with Delay

Transient failure is not the same as permanent failure. The downstream service is restarting; the
database is failing over. The message is fine — you just tried at a bad moment.

- If work isn't done/acked, make it available again to the next consumer.
- If it failed for a transient reason, **delay** to let that pass.
- After a number of re-queues, move to a dead-letter channel.

**Needs from the broker:** per-message acknowledgement, a redelivery mechanism, and a way to hold a
message back for a period.

#image: diagram — a queue with requeue and delay (stopwatch), moving to a dead-letter channel after N tries

#note: This is a *queue* capability, taught before we have formally drawn the queue/stream distinction.
That is deliberate — §4.5 then gets the reveal that streams have none of this. Say "queue" here and
promise the comparison.

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
it makes the queue-versus-stream distinction concrete *before* §4.5 draws it conceptually, and it
explains why the same reliability pattern costs very different amounts on different infrastructure.
Ask the room which broker they are on and what they assumed was native.

---

## 4.5 Queues and Streams

*What kind of broker am I on, and what does that change?*

#note: **Kafka Quick Start lands here** — `exercises/Quick-Start-Kafka.pptx`, merged in the way
`Quick-Start-RMQ.pptx` merges into §4.2. This is the second half of the exercise arc: §4.4 taught
reliability on a **queue** (RMQ, where most of it is native); §4.5 asks delegates to get the same
guarantees on a **stream**, where almost none of it is. *What Your Broker Actually Gives You* at the end
of §4.4 is the setup for exactly that.

### Slide: Queues Contain Tasks


Think of messages on a **queue** as **tasks** — requests to carry out an action; once done, delete the task.

- First consumer locks the next message while it processes it.
- A second consumer reads past any locked message and locks the next available one.
- We don't want anyone else to action a done task; a receiver of a done task discards it. If we can't action it, someone else must.


#image: diagram — a queue of message envelopes with Consumer One/Two and lock icons (lock and read-past)

### Slide: Queue Lifecycle — Ack, Fail, Requeue


- When done processing, we unlock — usually because we finished, sometimes because we failed.
- On success, delete the message from the queue; no one else can process it.
- On failure, others could succeed later, so make it available to lock again (often with a delay).
- After a number of re-queues, move it to a dead-letter channel — no one actioned the request in a reasonable time frame.


#image: diagram — competing consumers on a queue with lock, delete (eraser) and delay (stopwatch) icons

### Slide: Streams Contain Facts


Think of records on a **stream** as **facts** — records that a state change occurred.

- First consumer reads the next record and processes it; a second consumer reads the next and processes it (both can read the same records).
- Each consumer stores an **offset** marking how far it has read.
- On restart, a consumer reads the store to find the last record it processed.
- Facts are an "inverse database" — how current state was arrived at. Navigate offsets to compute a point-in-time position. We don't consume facts by reading; they persist.


#image: diagram — a stream log of message envelopes with an Offset Store and two consumers

### Slide: Scaling Queues and Streams


Section marker: how each model scales.

### Slide: Scaling Queues — Competing Consumers


Scale consumption of a queue by adding more consumers (lock, read-past, lock-next — as before).


#image: diagram — a queue with multiple competing consumers locking and reading past messages

### Slide: Scaling Streams — Partitions


To scale out we partition the stream so multiple consumers can read it.

- Each consumer manages offsets for their partition.
- For events that must be processed sequentially (e.g. all changes to one entity), use **consistent hashing** to push same-identifier messages to the same partition — scale while preserving order.


#image: diagram — a stream divided into partitions, each read by its own consumer, with offset stores

### Slide: Scaling Streams — Consumer Groups


For availability, only one consumer in a group reads from a partition at a time, but a consumer may read from more than one of the group's partitions.


#image: diagram — stream partitions with a consumer group; one consumer per partition at a time

### Slide: Archive and Replay


Section marker: can we re-read the past?

### Slide: Queues — No Archive and Replay


With queues we delete a message once the action completes, so there's no way to replay a work request — our only option is to ask the producer to resend.


#image: diagram — a queue where a processed message is deleted (eraser icon); nothing left to replay

### Slide: Streams — Archive and Replay


Straightforward, because nothing is deleted: reset the consumer's offset to re-read the stream.


#image: diagram — a stream log with an Offset Store; replay by resetting the consumer's offset

### Slide: Streams — No Requeue or DLQ


Because we don't lock items, we don't requeue (including requeue-with-delay). Strategies instead:

- Ignore and continue (load shedding).
- Retry (backpressure).
- Copy to another stream (a delay or DLQ stream).


#image: diagram — a stream log with an Offset Store; no locking, requeue, or DLQ

### Slide: Queues vs. Streams — Capability Matrix


Summary comparison across: Messaging (Discrete Event vs. Series Event), Ordering, Archive and Replay, and Requeue with Delay — for Queue vs. Stream.


#image: comparison grid of green-check / red-cross icons (queue vs stream across ordering, replay, requeue-with-delay, etc.)

### Slide: Exercise Material — Introduction to Kafka

Readme, slides. Quick Start Kafka — brokers, topics, partitions, consumer groups, offsets.

Then the exercises: **take the reliability you built on a queue and get the same guarantees on a
stream.** Nothing you relied on in §4.4 is native here.


#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)

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

- A message is sent over a **channel** — a virtual pipe (topic, routing key).
- A message has a **header** (metadata) and a **body** (data).
- A channel is **unidirectional** (one way) — a two-way conversation needs two channels.
- Prefer *requestor/provider* over *producer/consumer* for conversation patterns, because they indicate role.

**Example.** *Provider (Store Information)* manages stores for our ecommerce site. *Requestor (Search)*
registers a store and optimizes for fast lookup on key search terms. The message `changedstore()`
indicates new store details.

Presenter notes: The problem with producer/consumer is that the *consumer* of a message might be the one exposing operations (receiving a command), or the *producer* might be the one exposing operations (sending a notification). Thinking in requestor/provider makes the role clear — are you providing the API or using it? Note that the channel being one-way is what forces every pattern that follows: if you want an answer you need a second channel, and that is a decision with consequences.

### Slide: Messaging or Eventing?

The first question, before any pattern: **are you expressing intent, or reporting a fact?**

| | Messaging | Eventing |
|---|---|---|
| carries | **intent** — do this, tell me this | **facts** — this happened |
| examples | Command (transfer of control), Query (request an answer), transfer of value | Notification |
| expectations | part of a workflow or conversation | none — things you report on |
| concerned with | the **future** | the **past** |
| patterns | In-Only, In-Out | Out-Only |

▎ A message asks for something. An event announces something.

#image: two UML-style pattern diagrams — In-Only (fire-and-forget) and In-Out (request-reaction), requestor/provider  [→ resources/'Practical Messaging - Day 2 - 2024 - 25.png' + '...- 29.png' — exported slide images]
#image: UML-style diagram — the Out-Only (notification) pattern, requestor to provider  [→ resources/'Practical Messaging - Day 2 - 2024 - 27.png' — exported slide image]

Presenter notes: This is the first fork in the decision and it decides most of the rest. If you are expressing intent you are addressing someone — you know who should act, and that is behavioural coupling. If you are reporting a fact you are not addressing anyone — the subscriber list is not your concern, which is why eventing is the loosest coupling available. Tie back to Integration Styles: the same trade, one level down.

### Slide: The Four Exchange Patterns

Two questions give you all four. **Who speaks first** — the requestor, or the provider? And **is there
a message back?**

|  | no message back | a message back |
|---|---|---|
| **In** — requestor speaks first | **In-Only** (fire and forget) | **In-Out** (request-reaction) |
| **Out** — provider speaks first | **Out-Only** (notification) | **Out-In** (solicit-response) |

- *In* and *Out* are named from the **provider's** point of view: In = a message arrives, Out = a message leaves.
- Everything else in this section is one of these four, or a composition of them.

#image: NEW — the 2×2 exchange-pattern grid (who speaks first × is there a reply) with all four patterns named  [Phase 2 — new drawing]

### Slide: In-Only (Fire and Forget)

Under **In-Only**, the requestor sends a request to the provider but does not seek acknowledgment of
completion. Typically called *fire-and-forget*.

- Used where we are finished with our part in a flow and are **transferring control** — we need no response because we are done.
- **Example.** *Requestor (cashier)* has a paid-for basket it wants to turn into an order; *provider (order placement)* raises an order — `place order()`.

**What it commits you to**

- *Coupled about:* the command contract — you name an operation on someone else.
- *Must you both be up?* **No.** Store-and-forward; the provider can be down.
- Behavioural (control) coupling: you decided who should act.

### Slide: In-Only — What About Faults?

The requestor is not waiting for a response. So what guarantee does the provider make about **faults**?

**No Fault** — the provider makes no attempt to communicate triggered faults back. From the requestor's
perspective, faults are the provider's application issue. Consistency is repaired out-of-band, via logs
or error reports.

**Message Triggers Fault (Robust In-Only)** — the provider propagates faults from the operation back to
the triggering requestor on a **reverse channel**. There is no existing subsequent message to replace
with a fault, so we add one.

- Assumes the requestor can act on receipt of the fault, but it still takes no success response.
- **Example.** The cashier sends `place order()`; if order placement cannot place the order it raises `fault()`. The cashier does not acknowledge success, but on a fault may need to issue a refund.

Presenter notes: No Fault is "good enough" in many cases — say so, because teams reach for fault channels reflexively. The question to ask is: *is there an action the requestor would take?* If there is no action, a fault message is noise and a log line is the right answer. Robust In-Only earns its keep when the fault has a compensating action, like the refund.

### Slide: Out-Only (Notification)

Under **Out-Only**, the requestor subscribes to the provider; an operation is triggered by receipt of a
message, but it does not acknowledge the message back to the provider. Out-Only *is* the
Publish-Subscribe pattern: a provider is not aware of its consumers.

- **Example.** *Provider (Store Information)* manages stores and raises `changedstore()`. Multiple requestors subscribe: **Search** (fast lookup), **Availability** (factors for whether a store is open), **Pick-Up Locations** (where couriers pick up, and restrictions).
- Adding a fourth subscriber requires no change to the provider — that is the whole point.

**What it commits you to**

- *Coupled about:* the event schema, and nothing else. No operation is named.
- *Must you both be up?* **No.**
- The loosest coupling available — which is exactly why its fault story is the one on the next slide.

### Slide: Out-Only — Faults Are Not Available

With a notification, **No Fault is essentially forced** — and that is a consequence of the coupling, not
an oversight.

- **Example.** Search cannot add a store to its results after `changedstore()`, and makes no attempt to tell Store Information.
- The provider does not know its subscribers. There is nobody to tell.
- And if it *did* know, it would be coupled to them — you would have traded away the property you chose pub-sub for.

▎ You cannot have loose coupling and a fault path back. Pick one.

Presenter notes: This is the payoff of putting the coupling verdict on every slide — the fault story is not a separate topic bolted on, it falls out of the pattern you chose. Repair happens on the subscriber's side: retries, dead-letter queues and the reconciliation they already met in Guaranteed Delivery.

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

### Slide: In-Out — When the Reaction Is a Fault

Under **Fault Replaces Message (Robust In-Out)**, the provider propagates faults by switching to a fault
flow — replacing any message *after the first* with a fault. The requestor handles the error; the fault
replaces the expected response (`reaction()` → `fault()`).

- **Example.** The Pricer sends `take payment()` to a payment provider. On failure the payment provider signals `payment error()` back.
- The fault message should indicate **why** — a provider issue, an invalid card, insufficient funds — because the requestor has to choose the next move: ask for an alternate payment method, or cancel the order.

Presenter notes: Any message in the conversation after the first may indicate a fault instead of the normal outcome. The design rule is that a fault is a *response*, not an exception — it travels the same channel, carries the same correlation id, and is handled by the same code path.

### Slide: In-Out — When Nothing Comes Back

The requestor may not receive the expected response at all. What can it do?

- Set a **timeout** within which to receive a response.
- **Retry** if no response arrives within that window (`greet()` → `greet()` → `acknowledge()`).
- Because we might send twice, the provider operation must be **idempotent**, or the consumer must **de-duplicate** already-seen messages.

▎ A timeout does not tell you the request failed. It tells you that you do not know.

#image: icon — a stopwatch/timer (the retry timeout)

Presenter notes: Call back to Guaranteed Delivery — this is the Inbox pattern earning its keep. Retry is why de-duplication is not optional: at-least-once delivery and requestor-side retry are two independent sources of duplicates.

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

### Slide: Subscribe-Notify

In-Out **composed with** Out-Only: a requestor asks to subscribe to a provider, and then notifications
flow.

- `subscribe()` → the provider manages a list of subscribers → optional `confirm()` / `confirmed()` (note the role switch — the provider is now the requestor).
- Then Out-Only `notification()` messages flow; a `stop()` ends them.

**What it commits you to**

- Behavioural (control) coupling on the subscribe exchange — then the loose coupling of Out-Only for everything after it.
- The provider now holds **subscriber state**, which it did not in plain Out-Only.

Presenter notes: This is the pattern that shows the four are a *basis*, not a catalogue — real conversations are compositions. It is also the honest version of "pub-sub is loosely coupled": the subscription itself is coupled; the notifications are not.

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

### Slide: Out-In (Solicit-Response)

Under **Out-In**, a provider solicits a response from a subscriber and awaits confirmation; the
subscriber confirms receipt of the provider's solicitation.

- **Example.** *Provider (Delivery)* assigns delivery requests to drivers and queries whether a courier is available — `solicit()` — usually followed by notifications of available work. *Requestor (Courier)* offers to take jobs depending on location and busyness — `ready()`.
- Use it when the provider needs to know **who is willing** before it allocates work.

**What it commits you to**

- *Coupled about:* the solicitation contract. The provider must know subscribers exist, though not who they are.
- *Must you both be up?* **No** — but the solicitation has a useful lifetime. An answer that arrives too late is worthless, which is a **timeout** problem, not an availability one.

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

#image: the §2 two-axis grid re-plotted a third time — *what are we coupled about* × *must we both be up* — with the four exchange patterns plotted and Blocking In-Out alone in the temporally-coupled quadrant  [Phase 2 — reuse the §2/§3 grid artwork]

Presenter notes: Third appearance of the grid — §2 introduced it, §3 plotted the integration styles on it, and now the exchange patterns land on it too. The repetition is deliberate: it is the one picture that carries the argument of the day, and delegates should be able to draw it from memory by the end.

---

## Designing Messages

*What goes in a message, and how the receiver gets the rest.*

**Section goal:** given a message to design, choose what to put in it — and know how the receiver gets
whatever you left out, and what that costs in availability.

#note: **Moved from Day 2 (2026-08-28, review item D1-9).** Ian: this "better completes the picture on
how to send and receive, ahead of Day 2's switch to the higher level". §4 taught how to move a message
reliably, §5 which exchange to build with it; this is the last piece — what is actually *in* it. Day 2
then opens at the level of whole flows.

#note: **Versioning did not come with it.** The fourth sub-topic — Postel's Law, Tolerant Reader,
additive vs. breaking change — is **dropped as taught material**, covered by the *Managing Asynchronous
APIs* handout and signposted by a single pointer slide in the Day 2 wrap-up. Ian: *these are what we drop
to focus on the exercises.*

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

Presenter notes: This is the Day 1 argument arriving inside message design. The lookup is a synchronous call in the middle of a message flow, so availabilities multiply again — and only on the unlucky path, which is exactly what makes it hard to catch in testing.

### Slide: Content Enricher — Someone Else Does the Lookup

A **Content Enricher** is a filter step that adds required data the publisher did not include: it
listens on the channel, fetches what is missing, and republishes the message complete.

- A new order carries an `AccountId`, but shipping needs the customer's address. The enricher adds the
  address, and the shipping consumer then has what it needs.
- Especially common in microservices, where each service holds only its own data and something has to do
  the join.

▎ The enricher does not remove the lookup. It moves it — and the availability sum moves with it.

#image: EIP diagram — Content Enricher augmenting a message from an external resource  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/DataEnricher.html — **redraw**]

Presenter notes: **Retained from the old §4.6 Pipelines when the rest of that sub-topic became a handout**
(review item D1-9), because it is the drawn form of the slide before it. Make the callout the point:
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

**Why it holds up in practice**

- **Latency is not the problem people expect it to be.** Propagation is a broker hop — you are behind by
  milliseconds to seconds. And this is *reference* data: restaurants, customers, price lists. It changes
  rarely, and rarely in a way the next message depends on.
- **Versioning is what makes it safe.** Carry **id and version**. Then "I have not seen this yet" is
  distinguishable from "I have it", and a missing version becomes a **wait** rather than a wrong answer —
  which is the next slide.
- **You removed the temporal coupling rather than relocating it.** A stays up when B is down. Day 1 §1's
  argument arriving inside message design.

**Be honest about the trade, and about which way it runs.** ECST is **availability over consistency**,
deliberately and *boundedly*: you read a copy that is behind by the propagation delay, and you can measure
that number. The synchronous lookup is not the consistent option — it makes the same trade on a cache hit,
and then **reverses it on a miss**, when B is down and you are not.

**What it actually costs:** you are running a replica, so you own a subscription and you must be able to
**rebuild** it — replay the stream from the beginning. That is operational work, not a correctness risk.

**When to still reach for the lookup:** the data genuinely cannot be replicated — too large, too
sensitive, or it must be fresh at the instant you read it (an authorisation or a balance check). Then take
the coupling knowingly, and put a circuit breaker on it.

Presenter notes: **Reframed 2026-08-28 (review item D1-10).** The slide used to hedge — "replicas go stale, go wrong, and need rebuilding", teams adopt it "expecting it to be free". That over-states the risk. Ian's position, and it is the right one: in practice ECST is reliable, latency rarely causes an actual problem, and versioning the reference data closes the gap that remains. **Teach it as the recommendation.** The sharpest line in the room is the one about which way the trade runs — delegates arrive believing the synchronous lookup is the "correct" option and the cache is the shortcut, and it is the other way round. Ask what their p99 is on a cache miss when the upstream is degraded; nobody knows, which is the point.

### Slide: Reference Data — Worked Example

*Order Fulfilment → Courier Assignment:* the request omits the restaurant pickup address; we assume Courier Assignment obtained it from Restaurant Information.

- Look up the restaurant in the local cache by **id and version**.
- If we have the restaurant but **not that version**, apply **backpressure** and retry the order after a delay.

▎ A missing version is a wait. A missing *value* would have been a wrong answer.

Presenter notes: **This slide is the proof of the previous one's claim** — it is what "particularly if you version the reference data" actually looks like. Without the version you cannot tell "I have not seen this yet" from "I have it", so staleness is invisible and you have to guess; with it, the replica knows what it does not know. Backpressure here is the same idea they meet again on Day 2 in the reactive material.

---

#note: **D1-10 done 2026-08-28.** *Get It In Advance — ECST* is now written as the recommendation, not a
warning, and the sub-topic has a verdict: **prefer the copy, version it, and take the synchronous lookup
only where the data genuinely cannot be replicated.** The same over-emphasis was corrected in two other
places it had leaked to — §6.3's *Why ECST Needs Snapshots* ("only tolerable" → the snapshot is what makes
it work) and Day 2 §1's *FBP — Where Do Lookups Live?*.

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

Presenter notes: This is the join between the two halves of the section. **ECST works because of the snapshot event** — it is what makes the next two slides possible at all, and it is the reason the previous sub-topic could recommend ECST without hedging. The rule: publish complete new versions rather than deltas. (D1-10: this used to read "only tolerable", which under-sells it.)

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

---

## Closing

### Slide: Further Reading

Pointers for going deeper.

### Slide: Q&A

Questions and discussion.
