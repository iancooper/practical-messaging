# Practical Messaging — Day One

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day One covers the *messaging* fundamentals: why we distribute, the coupling and integration styles that follow, and the catalogue of messaging patterns — messages, channels, endpoints, the message pump, pipelines, transformation, queues vs. streams, transactional messaging, versioning and documentation, and observability.

Prerequisites: We use RabbitMQ and Kafka for examples. You should have Docker (or an equivalent) installed — exercises ship a Docker Compose file to spin up RMQ and Kafka.

- Course content: https://github.com/iancooper/practical-messaging
- Exercise code: C#, Python, JavaScript, Go, Java repos under github.com/iancooper/Practical-Messaging-*

---

## Distributed Systems

*The problems messaging solves.*

#note: Three movements. **A — what we actually want** (slides 1–5: the two properties, each made
concrete). **B — what you now have to live with** (slides 6–8, the payload). **C — the price**
(slides 9–10, which hands off to §Coupling). Cut in earlier revisions: *Product Mode* and the
standalone *Example — Microservices* quote slide. This revision reframes the opening away from
justifying microservices and onto the two properties messaging buys — see *Easy to Change, and
Robust*.

### Slide: Why Distribute?

Once upon a time computer systems were stand-alone; they ran on one machine. Modern design tends to be distributed, with parts running on different computing nodes. Four forces drive this:

- **Performance and Scalability** — As systems succeed we must scale them to meet demand. A distributed system lets us scale *out* by adding nodes to spread load, and scale *up* parts of the offering with more expensive hardware.
- **Availability** — The "problem of one": a single node means failure stops the system. Redundant nodes let us keep serving — perhaps degraded — until we replace the failed node. This makes systems fault tolerant.
- **Maintainability** — Large monoliths are hard to maintain: you must test the whole to release any part, developers can't grasp the whole, and you get the "banyan tree" anti-pattern — duplication, and, with bad coupling, a "big ball of mud". Splitting into parts creates components that can be developed, QA'd and released independently.
- **Inherent Distribution** — Some applications are inherently distributed: business systems spanning divisions across regions, peer-to-peer content sharing, and so on.

Underneath all four, two properties are what we are really buying. The next slide names them.

Presenter notes: The availability claim here gets qualified on "The Price of Distribution" — redundancy
*within* a service raises availability, but chaining services can throw that gain straight back. Don't
resolve it yet; let anyone who spots it sit with it.

### Slide: Easy to Change, and Robust

Strip away the architecture words and two properties are left:

- **Easy to change** — ship a part without shipping the whole. *Independent deployability.*
- **Robust** — keep working when something you depend on is not. *Guaranteed delivery.*

How you get them:

- **Microservices are one way to buy the first.** They are not the only way, and they are not free — the rest of this section is the bill.
- **Task queues buy the second without microservices at all** — one team, one service, one queue. No reorganisation required.
- Both are bought with the same mechanism: **messages**.

▎ Two properties, one mechanism. Everything in the next two days buys one of them with messages.

Presenter notes: This replaces the microservices-justification framing the deck used to open with. In 2026 nobody in the room needs persuading that microservices exist; what they need is a reason to care about messaging that does not require them to reorganise their company first. Plant the two words and move on — **do not** mention Reactive yet. Day 2 pays it off: the Reactive Manifesto (2014) names the second property **Resilient**, and claims the first in its own words — reactive systems are "easier to develop and amenable to change". The delegates should meet that on Day 2 as a recognition, not a repeat.

### Slide: Easy to Change — Independent Deployability

**The problem.** As an organisation grows to many teams, monoliths suffer. Each team branches to avoid contention; releasing means agreeing a date and merging, which collides with other teams' schedules. Teams pile onto a release to avoid re-merging and re-testing upstream changes. A release takes a couple of weeks and distracts everyone.

**The answer.** Decomposing into team-sized microservices removes these difficulties. Each team negotiates only internally to decide a release candidate. Develop on master behind a feature switch per story to minimise integration cost and go straight to production. Delivery time becomes hours, not weeks.

▎ "Speed wins in the marketplace" — Adrian Cockcroft, former lead architect at Netflix.

▎ Independent deployability is the whole prize. Everything from here on is about not giving it back.

#image: timeline diagram — many teams on feature branches merging into a single monolith release over ~2 weeks
#image: diagram — a monolith decomposed into independently released microservices (Alpha, Beta, Gamma), delivering in hours

Presenter notes: Show the two diagrams as a before/after pair. On the monolith side: once teams line up they merge to master and resolve conflicts; more features → more bugs → cost and schedule overruns (assume ~30% rework); we must re-test everything because we merged potentially incompatible changes; all teams wait on any fix, even another team's. Feature switches help drop changes, but database/schema changes (a monolith has a shared schema) make this hard, and rollback forces everyone out — hence "roll forward only". On the microservice side: Continuous Delivery is table stakes for digital companies; you can't beat the competition with a slow release schedule; we build microservices once we grow beyond a single "two-pizza" team. The second callout is the load-bearing line of the movement — §Coupling calls straight back to it.

### Slide: Robust — Task Queues

**You do not need microservices for this one.** A single team with a single web application can have it on Monday.

Offloading work from a request path — the shape of the answer, before we name any of the parts.

- The web server puts the work on a queue.
- The queue stores work until we are ready to consume it — we can throttle to prevent surges.
- A backend application performs long-running or CPU-intensive work, freeing the web server to service new requests.
- We scale out the backend using competing consumers so the queue does not back up.

**What it buys:** the web server stays responsive when the backend is slow, overwhelmed, or down. The work is not lost — it waits.

▎ One team, one service, one queue. Robustness without reorganising the company.

#image: hand-drawn architecture diagram — browser/web server enqueues work onto a channel; a backend Sender/Receiver maps messages to data; databases at each end

#note: This slide deliberately uses vocabulary — *channel*, *competing consumers* — that nothing has
defined yet. It is a teaser, not a definition; say so, and promise the pattern names later
(competing consumers is §Messaging Patterns → The Message Pump).

Presenter notes: This slide used to sit after the microservice anatomy, where it read as a microservices pattern — the opposite of its point. Its job is to show messaging paying off *without* the organisational change, so that nobody in the room can file the whole course under "not for us, we're a monolith".

### Slide: Task Queue — HTTP Flow

How this looks over HTTP — and most delegates have not used this.

- We return **202 Accepted** — we have your work request and won't lose it. It is HTTP's own way of saying *store and forward*.
- We enqueue a work item for the request.
- We return a **Location** header so you can monitor progress (link to the resource — 404 until created; and a link to a progress page backed by a KV store where we note progress).
- The backend app does the work at a sustainable pace and updates the KV store as required.

#image: hand-drawn diagram of the task-queue HTTP flow — client, queue channel, backend worker, and a KV/progress store

Presenter notes: Ask who has returned a 202 in anger. Usually a handful of hands. This is the most immediately usable thing in the first hour of the course.

### Slide: Microservice — Messages In, Private Data

- The only way to complete tasks within a service is by sending it a message. Each service has its own accepted message types and specific data requirements for partners submitting work.
- Encapsulated within the service is private data. Requests to the service do not describe the shape of internal data.


#image: hand-drawn diagram — a microservice with private data receiving messages over a channel; database inside

### Slide: Microservice — No Cross-Service Transactions

- Transactions (including 2PC) may occur *within* a microservice.
- Transactions cannot occur *between* services. If you operate independently from your business partners, you don't exchange transactions with them. Cross-organizational transactions are avoided to prevent lockup of *your* database when the *other* organization makes a mistake. Without transactions, you communicate through multiple messages over time.

▎ No transaction spans two services. Consistency stops being something you declare and becomes something you design.


#image: hand-drawn diagram — two microservices exchanging messages over channels, each with its own database

Presenter notes: This is the load-bearing slide of the section. Everything the two days teach —
outbox, sagas, idempotence, choreography, compensation — exists because this sentence is true. Say
so explicitly; it gives delegates a spine to hang the rest of the course on.

### Slide: Collaboration — Orchestration and Choreography

- As services are independent, a collaboration comprises **orchestrations** (handlers, sagas, or workflows) *within* the services…
- …and the **choreography** — the flow of messages *between* services.


#image: hand-drawn diagram — a process of tasks sending a message via a channel to a receiver task; databases at each end

Presenter notes: Plant the two words now; Day 2 §Process Automation takes them apart properly.

### Slide: The Price of Distribution

Everything so far was the benefit. Here is the bill.

- **Every call is now a network call.** It can be slow, it can fail, and it can succeed while losing the reply.
- **You cannot use a transaction to make two services agree.** Consistency becomes something you design.
- **Your availability is now entangled with everyone you depend on** — and *how* it is entangled is a choice you make.

That last one is the one people get wrong:

- **Call a service and wait, and your availabilities multiply.** Four services at 99.9% leaves you at 99.6% — before anything has actually failed.
- **Send a message and don't wait, and they don't multiply.** Guaranteed delivery means the message outlives their outage and is processed when they come back.

▎ Messaging doesn't remove the outage. It converts a failure into a delay.

Presenter notes: This is where the availability claim from "Why Distribute?" gets settled — anyone who
spotted the tension gets their answer here. Redundancy *within* a service raises availability; chaining
*temporally coupled* calls throws that gain away. Do the arithmetic on the board: 0.999⁴ = 0.996. Then
be honest about the trade — the messaging version doesn't make the downstream outage vanish, it buys an
availability loss back as latency variance. That is usually a trade you can accept, and it is the
argument the whole course rests on. This is also where *robust* stops being a slogan and gets a number.
Hands directly to §Coupling, which asks "must we both be up?".

### Slide: Fallacies of Distributed Computing

The classic eight — and where this course answers each.

| Fallacy | What it costs you | Where we answer it |
|---|---|---|
| The network is reliable | Messages lost, duplicated, or delivered twice | Retries, idempotence, DLQ — *4.4 Guaranteed Delivery* |
| Latency is zero | Calls that block; chains that compound | Asynchronous conversation — *Coupling*, *Conversations* |
| Bandwidth is infinite | Oversized payloads, saturated links | Fat vs. skinny messages — Day 2 *Designing Messages* |
| The network is secure | Blindsided by what you never modelled | **Out of scope for this course** — flag it, don't pretend |
| Topology doesn't change | Endpoints that move; instances that come and go | Endpoints, discovery, competing consumers — *4.2*, *4.3* |
| There is one administrator | Conflicting policies; nobody owns the contract | Documenting the contract — the *Managing Asynchronous APIs* handout |
| Transport cost is zero | Serialisation, brokers and operations you didn't budget | Fat vs. skinny — Day 2 *Designing Messages*; broker choice — *4.5 Queues and Streams* |
| The network is homogeneous | Schema and encoding mismatch across stacks | Tolerant readers — Day 2 *Versioning*; schema formats in the handout |

▎ Every one of these has a pattern later in the course. That is what the next two days are.

Presenter notes: (First seven: L. Peter Deutsch, 1994; the eighth added by James Gosling ~1997.)
Applications written with little network error-handling stall or wait forever during outages, consuming
resources, and may fail to retry when the network returns. Ignoring latency/packet loss invites unbounded
traffic and dropped packets; ignoring bandwidth creates bottlenecks; complacency about security gets you
blindsided; topology changes affect bandwidth and latency; multiple administrators create conflicting
policies; hidden build/maintenance costs are non-negligible; assuming homogeneity reproduces the first
three fallacies. Use the third column as a course map — it tells delegates the list is not a lament, it
is a syllabus.

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
(Day 2 — Fat & Skinny) and for tolerant readers (Managing Asynchronous APIs). Flag it now so
both call-backs land.

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

## 4.6 Pipelines

*Processing a message in stages.*

#note: Routing patterns stay in the deck as content, but hands-on exercise time moves to reliable
messaging over queue and stream — we do not need delegates to *build* routers, we need them to build
reliable consumers. Exercises to be revisited on that basis.

### Slide: Pipes and Filters


Divide the transformation of data between origin and destination into composable steps. A data **source** begins the flow, a data **sink** receives the output, and **filters** transform data as it flows.


#image: (s65) EIP diagram — a Pipes and Filters chain (e.g. Decrypt → Authenticate → De-Dup)  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/PipesAndFilters.html]

Presenter notes: Between publish and the eventual subscriber we may encrypt/decrypt, enrich, or transform. Treat the publisher as source, final consumer as sink, and intermediate read-transform-publish consumers as filters. Each filter reads from an inbound channel and publishes to an outbound one; pipes connect them, so simple, testable filters compose into complex applications. A processing pipeline works in parallel (a filter takes more work while the rest of the pipeline runs), increasing throughput — limited by the slowest stage. Parallelize a slow stage with competing consumers (simpler than multi-threading). (EIP reference.)

### Slide: Message Translator


A filter step that converts a message from one schema to another so consumers accepting a different format can receive it.


#image: (s73) EIP diagram — Message Translator converting an incoming message to a different schema  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageTranslator.html]

Presenter notes: The publisher's format may not be understood by all consumers — a versioning issue (a downstream consumer not ready for a breaking change) or schemas outside the team's control (external/legacy). Often temporary: retire the translator once the consumer accepts the publisher's schema. (EIP reference.)

### Slide: Content Enricher


A filter step that adds required data to a message the publisher didn't include.


#image: (s74) EIP diagram — Content Enricher augmenting a message from an external resource  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/DataEnricher.html]

Presenter notes: E.g. a new order carries an account id, but shipping needs the customer's address from their account — the enricher listens, adds the address, and the shipping consumer then has what it needs. Especially common in microservices, where each service holds only its own data, requiring joins to data held elsewhere. (EIP reference.)

---

### Slide: Content Based Router


Examine message content and route onto a different channel based on data in the message (field existence, specific values, etc.).


#image: (s66) EIP diagram — Content-Based Router directing an order to widget vs gadget inventory  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/ContentBasedRouter.html]

Presenter notes: A pipeline may need to branch on content. Keep the routing function easy to maintain — the router becomes a maintenance hot-spot. Some middleware offer configurable rules engines; beware pushing too much decision-making into middleware (hard to maintain/test). (EIP reference.)

### Slide: Dynamic Router


Solves the content-based router's maintenance problem by using a rules engine whose destinations are configured at run time.


#image: (s67) EIP diagram — Dynamic Router with a control channel and dynamic rule base  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/DynamicRouter.html]

Presenter notes: A **control channel** lets consumers register the rules under which they should receive messages as they start up. The router runs the rules on receipt to pick a destination. Conflicting rules → strategies like "last one wins"; routing to all valid routes is really the Recipient List. (EIP reference.)

### Slide: Recipient List


The publisher explicitly decides which branches a message takes via a list of recipients — like an email **To** list.


#image: (s68) EIP diagram — Recipient List forwarding to recipient channels A–D  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/RecipientList.html]

Presenter notes: Define a channel per recipient; the Recipient List inspects the message, determines recipients, and forwards to all their channels. Invert it (a *dynamic* recipient list) to let consumers subscribe via a control channel — this can implement Publish-Subscribe on middleware that offers only Point-to-Point, and can add control such as authorization. RabbitMQ exchanges and AWS SNS subscriptions are examples. (EIP reference.)

### Slide: Splitter


Takes one input message and breaks it into multiple output messages.


#image: (s69) EIP diagram — Splitter breaking one order into individual order items  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/Sequencer.html]

Presenter notes: Filters may correspond to parts of a message; splitting and routing parts to the right consumers can be more efficient (e.g. order line items to different consumers). Also useful for batches — splitting lets you observe progress by monitoring the number of messages still waiting, instead of "all-or-nothing". (EIP reference.)

### Slide: Aggregator


Collects and stores related messages until a complete set is received, then publishes a single distilled message.


#image: (s70) EIP diagram — Aggregator combining related items into a single message  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/Aggregator.html]

Presenter notes: The inverse of a Splitter — recombine parts (e.g. know when a split batch completes, or that some parts completed and others didn't). Depends on correlating messages (usually a correlation id in headers); knowing the batch size helps the aggregator know when it has seen everything. (EIP reference.)

### Slide: Resequencer


Uses an internal buffer to store out-of-sequence messages until a complete sequence is obtained, then publishes them in order.


#image: (s71) EIP diagram — Resequencer reordering out-of-sequence numbered messages  [external — Hohpe & Woolf EIP figure: https://www.enterpriseintegrationpatterns.com/patterns/messaging/Resequencer.html]

Presenter notes: Conditional/parallel steps, retries, and competing consumers can all de-order messages. The resequencer tracks the next-expected sequence number: it checks its buffer first, else reads another message; if it's the expected one it processes it, otherwise it buffers it. Eventually a buffered message becomes next and is released. (EIP reference.)

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

## Observability

### Slide: Observability — Overview

Why observability matters for asynchronous systems.


#image: screenshot — the OpenTelemetry homepage with its telescope illustration

### Slide: OpenTelemetry Tracing

Tracing a flow across asynchronous endpoints:

- Begin a **span** when we initiate a flow.
- Serialize the span **context** into the message headers when we send.
- Begin a **child span** in the receiver.

### Slide: Traces in Practice

Visualising distributed traces across services.


#image: screenshots — GitHub OpenTelemetry messaging-spans semantic-conventions docs

---

## Closing

### Slide: Further Reading

Pointers for going deeper.

### Slide: Q&A

Questions and discussion.
