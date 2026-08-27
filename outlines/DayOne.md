# Practical Messaging — Day One

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day One covers the *messaging* fundamentals: why we distribute, the coupling and integration styles that follow, and the catalogue of messaging patterns — messages, channels, endpoints, the message pump, pipelines, transformation, queues vs. streams, transactional messaging, versioning and documentation, and observability.

Prerequisites: We use RabbitMQ and Kafka for examples. You should have Docker (or an equivalent) installed — exercises ship a Docker Compose file to spin up RMQ and Kafka.

- Course content: https://github.com/iancooper/practical-messaging
- Exercise code: C#, Python, JavaScript, Go, Java repos under github.com/iancooper/Practical-Messaging-*

---

## Distributed Systems

*The problems messaging solves.*

#note: Three movements. **A — why we're distributed at all** (slides 1–3, premise: move through it).
**B — what you now have to live with** (slides 4–8, the payload). **C — the price** (slides 9–10,
which hands off to §Coupling). Cut in this revision: *Product Mode* (org design, left over from when
microservices needed justifying) and the standalone *Example — Microservices* quote slide (folded into
"Microservices Let Us Scale an Organisation").

### Slide: Why Distribute?

Once upon a time computer systems were stand-alone; they ran on one machine. Modern design tends to be distributed, with parts running on different computing nodes. Four forces drive this:

- **Performance and Scalability** — As systems succeed we must scale them to meet demand. A distributed system lets us scale *out* by adding nodes to spread load, and scale *up* parts of the offering with more expensive hardware.
- **Availability** — The "problem of one": a single node means failure stops the system. Redundant nodes let us keep serving — perhaps degraded — until we replace the failed node. This makes systems fault tolerant.
- **Maintainability** — Large monoliths are hard to maintain: you must test the whole to release any part, developers can't grasp the whole, and you get the "banyan tree" anti-pattern — duplication, and, with bad coupling, a "big ball of mud". Splitting into parts creates components that can be developed, QA'd and released independently.
- **Inherent Distribution** — Some applications are inherently distributed: business systems spanning divisions across regions, peer-to-peer content sharing, and so on.

Presenter notes: The availability claim here gets qualified on "The Price of Distribution" — redundancy
*within* a service raises availability, but chaining services can throw that gain straight back. Don't
resolve it yet; let anyone who spots it sit with it.

### Slide: Monoliths Do Not Scale To Many Teams

As an organisation grows to many teams, monoliths suffer. Each team branches to avoid contention; releasing means agreeing a date and merging, which collides with other teams' schedules. Teams pile onto a release to avoid re-merging and re-testing upstream changes.


#image: timeline diagram — many teams on feature branches merging into a single monolith release over ~2 weeks

Presenter notes: Once teams line up, they merge to master and resolve conflicts. More features → more bugs → cost and schedule overruns (assume ~30% rework). We must re-test everything because we merged potentially incompatible changes. All teams now wait on any fixes, even another team's. Feature switches help drop changes, but database/schema changes (a monolith has a shared schema) make this hard. Release typically takes a couple of weeks and distracts teams. Rollback is complicated because it forces everyone out — hence "roll forward only".

### Slide: Microservices Let Us Scale an Organisation

Decomposing into team-sized microservices removes these difficulties. Each team negotiates only internally to decide a release candidate. Develop on master behind a feature switch per story to minimise integration cost and go straight to production. Delivery time can be hours, not weeks.

▎ "Speed wins in the marketplace" — Adrian Cockcroft, former lead architect at Netflix.


#image: diagram — a monolith decomposed into independently released microservices (Alpha, Beta, Gamma), delivering in hours

Presenter notes: Continuous Delivery is now "table stakes" for digital companies — you can't beat the competition with a slow release schedule. To ship features as soon as they are done we build microservices, once we grow beyond a single "two-pizza" team. **Independent deployability is the whole prize** — everything from here on is about not giving it back. §Coupling calls straight back to this slide.

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

### Slide: Worked Example — Task Queues

Offloading work from a request path — the shape of the answer, before we name any of the parts.

- The web server puts the work on a queue.
- The queue stores work until we are ready to consume it — we can throttle to prevent surges.
- A backend application performs long-running or CPU-intensive work, freeing the web server to service new requests.
- We scale out the backend using competing consumers so the queue does not back up.


#image: hand-drawn architecture diagram — browser/web server enqueues work onto a channel; a backend Sender/Receiver maps messages to data; databases at each end

#note: This slide deliberately uses vocabulary — *channel*, *competing consumers* — that nothing has
defined yet. It is a teaser, not a definition; say so, and promise the pattern names later
(competing consumers is §Messaging Patterns → The Message Pump).

### Slide: Task Queue — HTTP Flow

How this looks over HTTP:

- We return **202 Accepted** — we have your work request and won't lose it.
- We enqueue a work item for the request.
- We return a **Location** header so you can monitor progress (link to the resource — 404 until created; and a link to a progress page backed by a KV store where we note progress).
- The backend app does the work at a sustainable pace and updates the KV store as required.


#image: hand-drawn diagram of the task-queue HTTP flow — client, queue channel, backend worker, and a KV/progress store

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
argument the whole course rests on. Hands directly to §Coupling, which asks "must we both be up?".

### Slide: Fallacies of Distributed Computing

The classic eight — and where this course answers each.

| Fallacy | What it costs you | Where we answer it |
|---|---|---|
| The network is reliable | Messages lost, duplicated, or delivered twice | Guaranteed delivery, retries, idempotence, DLQ — *Channels*, *Queues and Streams* |
| Latency is zero | Calls that block; chains that compound | Asynchronous conversation — *Coupling*, Day 2 *Conversations* |
| Bandwidth is infinite | Oversized payloads, saturated links | Fat vs. skinny messages — Day 2 |
| The network is secure | Blindsided by what you never modelled | **Out of scope for this course** — flag it, don't pretend |
| Topology doesn't change | Endpoints that move; instances that come and go | Endpoints, discovery, competing consumers |
| There is one administrator | Conflicting policies; nobody owns the contract | Documenting the contract — *Managing Asynchronous APIs* |
| Transport cost is zero | Serialisation, brokers and operations you didn't budget | Fat vs. skinny, broker choice — Day 2 |
| The network is homogeneous | Schema and encoding mismatch across stacks | Schemas, tolerant readers — *Managing Asynchronous APIs* |

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

## Managing Asynchronous APIs

### Slide: Versioning — Postel's Law

▎ Be strict when sending and tolerant when receiving.

Robustness Principle (Postel's Law) — Jon Postel, RFC 1958: implementations must follow specs precisely when sending, and tolerate faulty input from the network.

### Slide: Additive Change — Tolerant Reader (Ignore New Fields)

Adding fields (e.g. `latitude`/`longitude`, not required) is non-breaking. A **Tolerant Reader** ignores new fields it doesn't understand.

Presenter notes: A general rule — *adding* things does not cause a versioning conflict, as long as a new version is convertible from an old one. When old versions are read, upcast them to the latest before handling, so a handler only knows the latest version. Add new non-nullable fields with a **default value** (as with a new DB column). Additive changes → new messages process on old consumers; new consumers default missing values from older messages; may use an Enricher.

### Slide: Additive Change — Default Missing Fields

The other side of tolerant reading: a new consumer reading an old message **defaults missing fields** (e.g. Default Latitude: 0, Default Longitude: 0). Note the added fields are *not required*.

### Slide: Breaking Change

Renaming/splitting fields (e.g. `customerName` → `firstName` + `surName`) and making new fields required is a **breaking change**.

- We might code around it, but we must *know* a required field is missing and new fields exist instead.
- For that we rely on a **version in the header** and the ability to process the new version alongside old ones, running out the old until the new replaces it.

Presenter notes: Breaking changes → create a **new message type**. Source systems may need to send original *and* new, or source the missing info via a Message Translator in the pipeline.

### Slide: Documentation — Endpoints

An **endpoint** is where messages are sent or received, defining everything required for the exchange — *where* messages go, *how* they're sent, and *what* they look like. (Reference: WCF fundamental concepts.)

### Slide: Documentation — Discovery Problems

Two symmetric questions that motivate documenting async APIs:

- **Consumer side (Restaurant Availability):** How do I know who exposes the data I need? How do I find the endpoint to consume from? (Search every GitHub repo? Ask on Slack/Teams?)
- **Producer side (Restaurant Management):** Who consumes the messages I send? Whom do I have a contract with? (Search repos for my message name? Ask on Slack/Teams?)


#image: shape diagram (consumer side) — 'how do I find the endpoint I need?' with GitHub and Slack logos
#image: shape diagram (producer side) — 'who consumes the messages I send?' with GitHub and Slack logos

### Slide: Asynchronous Endpoints Need Documenting

Our async APIs need documenting just like any other API (HTTP, etc.). We need to document:

- The **message** — it is the contract.
- The **channel** — where the message flows.
- The **protocol** — how to send/receive.
- **Who** sends and receives — to understand flow.

### Slide: Endpoint — Documenting the Contract

An endpoint is where/how messages are sent and what they look like — the promises we make. Its parts:

- **Channel** — the logical pipe over which messages flow; our address.
- **Message** — data we send or receive (Metadata/headers + Data/payload). We agree the headers, and the encoding and schema of the body.
- **Binding** — how we implement the channel: transport and encoding (e.g. AMQP and text/plain). In principle a channel can have multiple bindings.

### Slide: AsyncAPI

Introducing AsyncAPI as the standard for documenting message-driven APIs.


#image: screenshot — the AsyncAPI 'Why AsyncAPI?' feature-cards webpage

### Slide: AsyncAPI Elements (V3)

- **Application** — running code with operations: producer (sends) / consumer (receives).
- **Operations** — send or receive messages over channels.
- **Channels** — where messages flow.
- **Message** — must have a payload, may have headers (protocol- or application-specific).
- **Server** — has a protocol by which messages are exchanged.
- **Bindings** — protocol-specific information.

### Slide: AsyncAPI Document Structure (V3)

- **AsyncAPI Object** — the root; identifies the application.
- **Info Object** — metadata for this specification.
- **Servers Object** — connection details for the server.
- **Channels Object** — the channels used by the application.
- **Operation Object** — an operation (publish or subscribe) on a channel.
- **Components Object** — reusable components.
- **Tags Object** — user-defined tags.

### Slide: AsyncAPI (V3) and Endpoint ABCs

Mapping AsyncAPI objects to the endpoint building blocks: Operation → **Endpoint**; Channels → **Channel**; Bindings → **Binding**; Message → **Message** (Metadata/headers + Data/payload).

### Slide: AsyncAPI — Info Object (example)

Example `info:` block — contact (Paramore Brighter), Apache 2.0 license, description, title ("Brighter Sample App"), version 1.0.0, and tags.

### Slide: AsyncAPI — Servers Object (example)

Example `development:` server — a Kafka broker for local dev at `localhost:9092`, protocol `kafka`.

### Slide: AsyncAPI — Channels (V3, example)

Example `greeting:` channel — address `goparamore.io.greeting`, summary/description, `servers` ref, `messages` ref, and Kafka `bindings` (partitions: 20, replicas: 3).

### Slide: AsyncAPI — Operations (V3, example)

Example `sendGreeting:` operation — `action: send`, summary/description, `channel` ref, and Kafka bindings.

### Slide: AsyncAPI — Components (example)

Example `components.messages.greeting` — name, title, summary, `contentType: application/json`, `traits` (commonHeaders), and `payload` ref to `schemas.greetingContent` (a JSON object with a `greeting` string).

### Slide: JSON Schema (AsyncAPI Schema Object)

Payload schemas via JSON Schema — `$schema`, `$id`, `title`, `description`, `type`, `properties`. Example: a `greeting` object with a `greeting` string property.

### Slide: Avro

An alternative encoding. Complex types: records, enums, arrays, maps, unions, fixed. Records carry: name, namespace, doc, alias, and fields (each with name, doc, type, default).

### Slide: Avro (example + capabilities)

Example record schema for `greeting` with a single string field. Encodings: JSON, Binary. Languages: C, C++, C#, Java, Perl, Python, Ruby, and others.

### Slide: Protobuf

Another encoding. Example: `syntax = "proto3"; message Greeting { string greeting = 1; }`.

### Slide: Protobuf (capabilities)

Encodings: Binary. Languages: Dart, C++, C#, Java, Kotlin, Python, Ruby, Go, Objective-C, and others.

### Slide: Schema Registry

A schema registry (e.g. Confluent) manages and evolves schemas centrally. (Reference: Confluent Schema Registry docs.)


#image: screenshot — a Confluent Schema Registry diagram with Kafka, producers and consumers

### Slide: Cloud Events

A standard event envelope. **Metadata** (required + optional attributes) + **Payload** (data).

- Required: `id` (unique identifier), `source` (production context — together unique), `specversion` (CE version), `type` (name + version).
- Optional: `datacontenttype` (MIME type), `dataschema` (URI of payload schema), `subject` (qualifies source), `time` (timestamp).

### Slide: CloudEvents — Protocol Binding (Binary vs. Structured)

- **Binary** — uses the protocol's native approach to metadata.
- **Structured** — adds headers to the payload (envelope).

Bindings include: amqp 1-0, avro, http, http-webhooks, kafka, mqtt, nats, protobuf, websockets.

### Slide: Protocol Binding — Worked Example

A Kafka message shown both ways: **Binary** (CloudEvents attributes as `ce_*` headers, Avro value) vs. **Structured** (`content-type: application/cloudevents+json`, the CloudEvent as the JSON value).

### Slide: AsyncAPI Object — Identifying Apps

Use a specification file per app (a producer or consumer), identified by `id` (e.g. `https://github.com/brightercommand/greetings/`).

### Slide: Tooling — VS Code

Authoring/preview of AsyncAPI in VS Code.


#image: screenshot — VS Code editing AsyncAPI YAML with the rendered AsyncAPI preview

### Slide: Tooling — Backstage

Cataloguing async APIs in Backstage.


#image: screenshot — a Backstage software-catalog docs page for an API entity

### Slide: Tooling — Event Catalog

Event Catalog (github.com/boyney123/eventcatalog) for documenting events.


#image: screenshot — the EventCatalog visualiser showing a Basket Service publishing an event

### Slide: Tooling — AsyncAPI Studio

AsyncAPI Studio for authoring and visualising specs.


#image: screenshot — AsyncAPI Studio rendering the Brighter Sample App spec

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
