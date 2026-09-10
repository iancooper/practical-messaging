# Managing Asynchronous APIs #

**A reference, not a talk.** The two days taught you what to put in a message and how to move it
reliably. This is the part that comes after: **how you publish what your endpoints are, and how you
change a message you have already published.**

It is reference material for when you get back to your desk. Nothing in here is a decision to rehearse
in the room, which is why it is on paper rather than on a slide.

Adapted from *Managing Asynchronous APIs at Enterprise Scale*, QCon London 2026.

---

## The index ##

The slide that handed you this listed three things. Here is where each one lives.

| the slide said | it is here |
|---|---|
| **Describing endpoints** — the ABCs; AsyncAPI, CloudEvents, xRegistry, and the tooling | [The ABCs of an endpoint](#the-abcs-of-an-endpoint) · [1. Discovery](#discovery) |
| **Versioning** — Postel's Law and the Tolerant Reader; additive vs. breaking change; why a breaking change means a new message type | [Versioning](#versioning-changing-a-message-you-have-already-published) |
| **Schema and registries** — JSON Schema vs. Avro vs. Protobuf; registries and compatibility modes | [2. Governance](#governance) |

**And the shape of the argument**, if you would rather read it end to end:

| | | answers |
|---|---|---|
| | [Why this becomes a problem](#why-this-becomes-a-problem) | What ad hoc costs once you are past a few teams |
| **1** | [Discovery](#discovery) | *What events exist? Who produces them? Who consumes them? What do they look like?* |
| **2** | [Governance](#governance) | *Are schemas consistent, compatible, and evolving safely?* |
| **3** | [Provisioning](#provisioning) | *How do I get from a spec to running infrastructure, reliably and repeatably?* |
| | [The virtuous cycle](#the-virtuous-cycle) | Why the three are one system and not three tools |
| | [MeX at Just Eat Takeaway](#case-study-mex-at-just-eat-takeaway) | The three pillars, in production, at 603 services |
| | [What is still hard](#what-is-still-hard) | The honest list |

---

## The ABCs of an endpoint ##

Everything here rests on one decomposition. **An endpoint is three things**, and each of the three has a
different owner, a different rate of change, and a different failure mode:

| | | |
|---|---|---|
| **A** | **Address** (channel) | The logical pipe over which messages flow |
| **B** | **Binding** | Protocol-specific detail — transport and encoding |
| **C** | **Contract** (message) | Metadata (headers) and data (payload) |

> **ENDPOINT = Address + Binding + Contract**

Keep the three separate in your head and the rest of this handout is a set of answers to *who looks
after each one*. Collapse them — "the topic" meaning all three at once — and every problem below looks
like the same undifferentiated mess.

---

## Why this becomes a problem ##

### At small scale, ad hoc works ###

It genuinely does, and it is worth being honest about that before prescribing anything:

- Teams know endpoints by word of mouth — who publishes, who consumes.
- Message flows are understood through whiteboard conversations.
- Teams manage their own infrastructure, or raise a ticket for changes.
- Choreography is tractable because there are few participants.

### At scale, it breaks ###

| what breaks | how it shows up |
|---|---|
| **Hard-to-discover endpoints** | Nobody knows what exists or who owns it |
| **No contracts** | Evolving a message risks breaking consumers you do not know about |
| **No schema governance** | Poorly enforced, no compatibility guarantees |
| **Infrastructure drift** | Messaging config diverges from intent |
| **DR requires redeployment** | The disaster recovery strategy is "redeploy and hope" |

**These are three problems, not five**, and that is the whole structure of what follows: you cannot
*find* things, you cannot *change* things safely, and you cannot *rebuild* things. Discovery,
Governance, Provisioning.

---

## 1. Discovery ##

> *How do we find and understand the async APIs in our estate?*

### The two questions nobody can answer ###

**As a consumer, how do I find the event I need?** Do I search every GitHub repo hoping somebody
documented it? Post on Slack asking who publishes it? Read a wiki page last updated eighteen months
ago?

**As a producer, who depends on me?** I want to evolve my event, and I might break consumers I do not
know about. Do I search all the repos for my message name? Ask on Slack?

Both questions have the same answer, and it is not a better wiki.

### Prior art: we have already solved this once ###

For **synchronous** APIs we have OpenAPI, GraphQL and gRPC — mature description formats. What they
describe is exactly the ABCs: the URI is the address, the protocol is the binding, the schema is the
contract.

Asynchronous APIs need the same three things described: **channel or topic** (address), **protocol**
(binding), **message schema** (contract). There is nothing special about async here. It just never got
the same treatment.

### AsyncAPI ###

A specification for describing asynchronous APIs — analogous to OpenAPI for REST. Six concepts:

| | |
|---|---|
| **Application** | Running code that sends or receives messages |
| **Channel** | A named destination where messages flow, with an address |
| **Operation** | An action: *send* or *receive*, over a channel |
| **Message** | Data (payload) + metadata (headers), with schema references |
| **Server** | Connection details and protocol — Kafka, AMQP, MQTT… |
| **Bindings** | Protocol-specific config — partitions, replicas… |

```yaml
asyncapi: 3.0.0
info:
  title: Restaurant Events
  version: 1.0.0
channels:
  restaurantHoursChanged:
    address: jet.restaurant.hours
    messages:
      hoursChanged:
        $ref: '#/components/schemas/HoursChanged'
```

**Tooling to try first:** the **AsyncAPI VS Code extension** gives you syntax highlighting, validation
and a live preview pane against a real spec. It is the cheapest possible way to find out whether this
is for you.

### xRegistry ###

Where AsyncAPI describes **one application's** API, **xRegistry** catalogues **many across an
organisation** — a CNCF specification for managing metadata about messaging endpoints, schemas and
message definitions. Think of it as the registry layer sitting above the individual specs: AsyncAPI
specs, schema definitions and CloudEvents definitions all live under it.

**xRegistry is the specification; EventCatalog and Backstage are the implementations people actually
use today.**

### CloudEvents ###

A CNCF specification that separates **metadata** (headers) from **data** (payload), so an event can
describe itself.

| required | | optional | |
|---|---|---|---|
| `id` | Unique identifier | `datacontenttype` | MIME type |
| `source` | Production context | `dataschema` | URI to the payload schema |
| `specversion` | CloudEvents version | `subject` | Qualifies the source |
| `type` | Event name + version | `time` | Timestamp |

**Why this matters for discovery** — three things fall out of it:

- **Inspect at runtime.** The metadata carries `source` and `type`, so you can inspect events as they
  flow through the system rather than reading documentation about them.
- **Route by type.** A topic carrying several event schemas can route to handlers on event type. Dapr
  and Brighter both do this.
- **Self-describing events.** Every event carries enough metadata to identify itself with no external
  documentation at all.

**Bindings.** Supported over Kafka, AMQP, HTTP, MQTT, NATS, WebSockets and more, in two shapes:

| | how | looks like |
|---|---|---|
| **Binary** | Uses the protocol's own metadata mechanism | headers: `ce_type`, `ce_source`, `ce_id`; value: the payload |
| **Structured** | Wraps everything in a single envelope | value: `{ specversion, type, source, data: {…} }` |

⚑ **Some protocols have limited header space** — SNS is the one you will hit — and the fallback is the
structured binding with CloudEvents JSON in the body.

### Discovery: summary ###

| | |
|---|---|
| **AsyncAPI** | Makes async APIs describable and machine-readable |
| **xRegistry** | Provides a catalogue layer for managing specs across the organisation |
| **CloudEvents** | Makes events self-describing with standard metadata |

Together these answer: *What events exist? Who produces them? Who consumes them? What do they look
like?*

**Tooling:** EventCatalog, Backstage, AsyncAPI Studio.

---

## 2. Governance ##

> *How do we ensure schemas are consistent, compatible, and evolving safely?*

### The governance problem ###

**At scale you cannot rely on human coordination to keep schemas compatible.**

- No compatibility guarantees — a producer changes a schema and breaks consumers silently.
- The schema is documentation on a team page, not a gate in the pipeline.
- Consumer-driven contract tools like **PACT do not really work for messaging**: there is no HTTP
  server to stand up against. What you do have are other interception points — middleware, `jq`, and
  CLI tooling like `kcat` or the AWS CLI.

⚑ **The failure mode to watch for is analytical consumers.** Teams talk to their transactional
neighbours and forget the analytics side, then break them. It is a very common cause of incidents and
rollbacks, and it persists because *the team that breaks it is not the team that suffers*.

### Contract coupling is the necessary coupling ###

    Producer          Open Host Service           Consumer
    (Supplier)  ---  (the published schema)  ---  (Customer)

In an event-driven system **the message schema is the contract** between producer and consumer. The
supplier agrees to support an external model — the published schema — and the customer depends on it.
Provided both honour the contract, **either side can change independently.**

This is not coupling to be eliminated. It is the coupling that makes the collaboration possible. Day 1
put it in the same terms: the boundary chooses your first two couplings, and the message is where you
choose the third.

### Schema formats ###

| format | encoding | evolution | ecosystem | notes |
|---|---|---|---|---|
| **JSON Schema** | Text (JSON) | Manual | AsyncAPI, HTTP APIs | Human-readable, widely supported |
| **Avro** | Binary / JSON | Built in | Kafka ecosystems | Compact, strong typing. Tooling can be an issue |
| **Protobuf** | Binary only | Field numbering | gRPC, language-neutral | Compact, language-neutral |

### Schema registries ###

| | |
|---|---|
| **Producer** | Registers schemas when publishing |
| **Registry** | Stores versioned schemas centrally, and **enforces compatibility rules** |
| **Consumer** | Retrieves schemas to deserialise |

The point of the middle row: **you cannot publish a schema that violates the compatibility rules.** The
schema stops being a description and becomes a gate.

### Compatibility modes ###

| mode | means | who upgrades first |
|---|---|---|
| **Backward** | The new schema can read old data | Consumers |
| **Forward** | The old schema can read new data | Producers |
| **Full** | Both | Safest, most restrictive |
| **None** | No compatibility checking | Use with caution |

**Pick the mode from the order you can actually deploy in.** That is the whole decision, and it is a
deployment question rather than a schema one.

---

## Versioning: changing a message you have already published ##

**This section is the deck's, not the conference talk's.** It is the material Day 2 gives thirty
seconds to and defers here, and it answers the question the compatibility modes above only half answer:
*modes tell you whether a change is structurally safe; they do not tell you how to write a consumer
that survives change at all.*

### Postel's Law ###

> **Be conservative in what you send, and liberal in what you accept.**

Two different instructions to two different halves of your system, and the asymmetry is the point.

**Be strict when sending.** Validate hard, on the producer side, in the pipeline. A producer that emits
a sloppy message has externalised its bug to everybody downstream, and it will not be the one that
finds it.

**Be tolerant when receiving.** Which is the next section, and the harder half.

⚑ **Tolerance is not always available.** A Flink pipeline writing to Iceberg tables has a fixed schema
at the far end; it cannot shrug at an unexpected field. Where you cannot be tolerant, you have to be
strict on both sides and accept the coordination cost — but know that you are paying it.

### The Tolerant Reader ###

A **Tolerant Reader** takes only what it needs from a message and ignores everything else. Concretely:

- **Read the fields you use. Do not deserialise into a type that must match the whole message.** The
  default behaviour of most deserialisers is the opposite of this, and it is where the breakage comes
  from: an unexpected field throws, and a message you did not need to care about takes you down.
- **Do not depend on field order, and do not depend on fields you do not read.**
- **Do not validate more than you consume.** A consumer that rejects a message for a field it never
  looks at has invented a breaking change on the producer's behalf.
- **Default what is missing where you sensibly can**, and fail loudly where you cannot.

This is the same argument as **skinny messages** from Day 1 §6.1, arriving from the other end. Skinny
messages reduce what you *send*, so there is less to break. Tolerant readers reduce what you *depend
on*, so less breaks you. **Do both and stamp coupling stops setting your release schedule.**

### Safe and breaking changes ###

| change | safe? | notes |
|---|---|---|
| **Add an optional field** | ✅ | Safe under backward and forward compatibility |
| **Remove a field** | ❌ | Deprecate first, remove only after consumers have migrated |
| **Rename a field** | ❌ | Effectively remove + add. Treat it as breaking |
| **Change a type** | ❌ | Almost always breaking |

**Additive change is the only change that is free.** Everything else is a migration with a schedule,
and the schedule is set by the slowest consumer — including the analytical consumer you forgot about.

### Why a breaking change means a new message type ###

When you genuinely cannot make a change additively, the instinct is to publish *v2 of the same
message* on the same channel. **Do not.** A channel that carries two incompatible shapes has stopped
telling the consumer what it is going to get, and every consumer now has to inspect a message to find
out how to read it.

Day 1 §4.2 already named the alternative: the **Datatype Channel** — one schema per channel, so the
channel *is* the type. A breaking change is therefore a **new message type on its own channel**, and
migration becomes something you can see and manage:

1. Publish the new type alongside the old. Both channels are live.
2. Consumers migrate one at a time, on their own schedule.
3. When the old channel has no consumers left — and the catalogue from §1 is how you *know* that —
   retire it.

**This is why Discovery comes first in this handout.** Step 3 is impossible without it, and "deprecate
first, then remove" is advice you cannot follow if you do not know who is listening.

### …except where ordering will not let you ###

**There is a case where you cannot split the channel, and Day 1 named it.** A **domain or delta event**
stream — `BasketItemAdded`, `BasketItemRemoved` — has to be *ordered on one channel* and its events
have different schemas, so it cannot be a Datatype Channel in the first place (Day 1 §6.3). Give each
event type its own channel and you have thrown away the ordering the consumer was relying on, which is
a worse break than the one you were avoiding.

Where that is your situation, **the version has to travel in the message instead of in the channel** —
and §1 already handed you the mechanism. CloudEvents' `type` attribute is specified as *event name +
version*, precisely so that a channel carrying several schemas can still say what each message is, and
consumers can route on type. That is the same "route by type" that Dapr and Brighter do.

So the rule has two halves, and which one applies is decided by **ordering**:

| if the channel… | then a breaking change is… | and the consumer… |
|---|---|---|
| **carries one schema** (snapshot events, commands, most request-reply) | a **new message type on a new channel** | subscribes to the channel it wants |
| **must carry several, in order** (domain / delta events) | a **new version in the message `type`** | routes on type, and ignores versions it does not handle |

The versioning strategies are that same choice restated: **topic-per-version** against
**single-topic-with-evolution**, plus semantic versioning of the schemas either way. Ordering is what
decides it — not preference.

### Governance: summary ###

- A standardised schema format across the platform.
- **Schema review as part of the API review process** — a human gate, once.
- **The schema registry integrated into CI/CD** — changes validated before merge, a machine gate, every
  time.
- **Runtime enforcement for producers.**
- Postel's Law on both sides: strict senders, tolerant readers.

---

## 3. Provisioning ##

> *How do we go from a spec to running infrastructure, reliably and repeatably?*

### The provisioning problem ###

| | |
|---|---|
| **Manual provisioning** | Topics, queues and subscriptions raised as tickets, validated by hand |
| **Configuration drift** | Partitions, retention policies and replication factors diverge from intent |
| **Naming complexity** | Collision-avoidance schemes poorly documented, and confusing to configure by hand |
| **No source of truth** | No single place that says *what should exist* |
| **DR = redeploy** | Disaster recovery is "redeploy everything and hope" |

At scale, manual provisioning does not keep up. Teams wait on TicketOps, and the waiting is what creates
the workarounds.

### Specification, not tickets ###

| before — TicketOps | after — spec-driven |
|---|---|
| 1. Document what exists | 1. Define what **should** exist |
| 2. Raise a ticket to change it | 2. Generate from the spec |
| 3. Manually validate | 3. Validate automatically |
| 4. Hope it matches intent | 4. **The spec IS the source of truth** |

**The AsyncAPI spec already contains the ABCs** — address (channels), bindings (protocols), contracts
(schemas). Once you notice that, the spec stops being documentation *about* the system and becomes the
definition *of* it. Four things then generate from it:

### What generates from the spec ###

**Code.** AsyncAPI ships a generator framework (React/Nunjucks templates) that turns a parsed spec into
producer stubs, consumer handlers, DTOs and serialisation logic.

> ⚑ **Worth knowing before you adopt the framework:** an AsyncAPI document is just JSON, so loading and
> parsing it yourself is about as easy as using the generator, and it leaves you free to emit a second
> document describing the infrastructure. That is the route MeX took.

**Schema registration.** A CI/CD step extracts the schemas the spec references — `components/schemas`
or external `$ref`s — validates compatibility and registers them:

    AsyncAPI spec
      -> extract schemas
         -> validate compatibility
            -> register
               -> deploy

Compatibility is checked **in the deployment pipeline**, not once deployed.

**Infrastructure.** The bindings carry the protocol-specific information: for Kafka, partition count,
replication factor and retention policy; for AMQP, exchange type, queue configuration and routing keys.
Infrastructure-as-code driven **by the API spec**, rather than by separate Terraform or Pulumi
definitions that can quietly disagree with it. **Drift detection** then means comparing what the spec
says should exist with what actually does.

**Documentation.** Generated HTML published into the catalogue (EventCatalog, Backstage), so the docs
stay in sync because they are generated from the same source. No more stale wiki pages.

### Provisioning: summary ###

| | |
|---|---|
| **Spec-driven** | Infrastructure defined by the spec, not by tribal knowledge or tickets |
| **Code generation** | Enforces consistency, removes error-prone boilerplate |
| **Auto registration** | Schema registration is automatic and validated |
| **DR is tractable** | If the spec is the source of truth, you can reproduce the infrastructure |
| **Architect visibility** | You can see what should exist, and you have the leverage to ensure it does |

---

## The virtuous cycle ##

The three pillars are one system, and they feed each other:

    better specs
      -> better governance
         -> more reliable provisioning
            -> more trustworthy discovery
               -> better specs, and round again

One AsyncAPI spec drives all three. **Discovery** — generated docs that a person, or an agent, can
read. **Governance** — schemas validated and versioned. **Provisioning** — bindings and channels
driving infrastructure and code.

Which is why adopting one pillar on its own tends to disappoint: a catalogue nobody generates goes
stale, and a registry nobody provisions from is a second source of truth.

---

## Case study: MeX at Just Eat Takeaway ##

**MessageExchange** — the three pillars, in production. Teams define their messaging needs in AsyncAPI
3.0.0 specs; MeX compiles them and deploys the infrastructure across AWS and Confluent Cloud.

| | | | |
|---|---|---|---|
| **603** service specs | **2,048** message schemas | **625** auto-generated pipelines | **7+** AWS regions |
| **4** platforms | **22K+** commits / year | **20+** regular contributors | |

### The pipeline ###

    AsyncAPI YAML specs
      |
      v
    C# Templater ("Mextrapolater")
      |
      v
    JSON artifact (Artifactory)
      |
      +--> Go CLI (mex deploy) --> AWS SNS / SQS / IAM
      |                        --> Confluent Kafka / ACLs
      |                        --> Schema Registry + Vault
      |
      +--> marmot-populate     --> Marmot data catalog

**The architectural decision worth stealing: separate compilation from deployment.** The Templater
compiles all 603 specs into one versioned JSON artifact. The Go CLI deploys *from that artifact*. The
catalogue populates *from the same artifact*. Single source of truth, several independent consumers —
and the two halves can then evolve independently.

Up to **five Pulumi inline stacks per service**, for blast-radius isolation.

### Discovery in practice: the Marmot catalog ###

After deployment, `marmot-populate` reads the same artifact and creates catalogue entries:

| | what is recorded |
|---|---|
| **Services** | Ownership, version, team, links to specs |
| **Kafka topics** | Retention, cleanup, schemas, cluster details |
| **SNS topics** | FIFO flag, per-environment AWS metadata |
| **SQS queues** | Retention, visibility, max receive count |

…plus **lineage**: service → topic (producer), topic → service (consumer), SNS → SQS (fan-out). Any
engineer can search, browse ownership, inspect schemas and trace data flows **without reading a spec
file**. The lineage graph — the whole messaging topology, drawn — is the feature people actually come
for.

Marmot is open source: **marmotdata.io** · github.com/marmotdata/marmot

### Governance in practice: schema validation ###

The Templater extracts schemas from the specs and builds subject definitions using a naming strategy
(TopicName, TopicRecordName, RecordName); Pulumi registers the subjects and sets compatibility levels
per subject (BACKWARD, FORWARD, FULL_TRANSITIVE, NONE).

**Subjects are locked by default**, and the toggle is the mechanism worth copying:

    READONLY  ->  READWRITE       ->  READONLY
    (default)     (during deploy)     (after deploy)

Only the MeX pipeline can write schemas, so nothing changes a schema out of band. On top of that,
**broker-side validation** — `confluent.value.schema.validation` on the Kafka topics — means the broker
itself rejects messages that do not conform to the registered schema. **Producers cannot publish a
message that violates the schema**, whatever their code believes. Consumers get `DeveloperRead` role
bindings so they can fetch schemas at runtime.

---

## What is still hard ##

The honest list. None of this is solved.

### Contracts and semantics ###

- **Consumer-driven contracts.** Schema compatibility checks tell you a schema is *structurally* safe.
  They tell you nothing about how consumers actually use the data. Pact-style equivalents remain
  unsatisfactory across messaging protocols.
- **Inputs → outputs.** There is no way to trace how *receiving* one message causes a service to *send*
  another, except by convention — `RaiseOrder` → `OrderRaised`. AsyncAPI describes choreography between
  services, not orchestration within one.
- **Semantic compatibility.** Technical compatibility does not give you semantic compatibility across a
  team boundary. Two teams can agree on a schema and still disagree about what a field means.

### Tooling and adoption ###

- **Adoption** is a cultural change, not a tooling one. Getting teams to write and maintain specs is the
  hard part, and no generator fixes it.
- **The observability gap.** Specs describe *intent*. You still need runtime observability to see what
  is actually happening — which is the other thing Day 2 signposts rather than teaches.
- **Convergence.** xRegistry and AsyncAPI are converging, but are not yet fully integrated.
- **Tooling maturity.** Generators and registries are improving, but not all of them are
  production-ready for every protocol.

---

## Takeaways ##

1. **Treat async APIs with the same rigour as sync APIs.** If you would document a REST endpoint,
   document your event channels.
2. **Specs are not just documentation — they are the source of truth.** Use them to drive code
   generation, schema registration and infrastructure provisioning.
3. **Governance is a pipeline gate, not a wiki page.** Schema registries with compatibility modes make
   evolution safe and auditable.
4. **Be strict when sending and tolerant when receiving.** It is the one line that changes behaviour on
   Monday morning.
5. **This is what gives architects what they need:** visibility into the event-driven estate, leverage
   to enforce standards, and control over the infrastructure.

---

## Resources ##

| | |
|---|---|
| **asyncapi.com** | The specification, the generator, AsyncAPI Studio and the VS Code extension |
| **cloudevents.io** | The CloudEvents specification and its protocol bindings |
| **xregistry.io** | The registry specification |
| **eventcatalog.dev** | A catalogue implementation to try first |
| **marmotdata.io** | The open-source data catalog from the case study |

**Where the ideas came from.** *Open Host Service* and *Published Language* are Eric Evans,
*Domain-Driven Design*. **Postel's Law** is Jon Postel, RFC 761. The **Tolerant Reader** is Martin
Fowler (martinfowler.com/bliki/TolerantReader.html).

**Related material in your pack**

| | |
|---|---|
| *Routing Patterns* | the eight patterns for getting a message to the right place |
| Day 1 §4.2 | the **Datatype Channel** — one schema per channel, which is why a breaking change is a new type |
| Day 1 §6.1 | **fat and skinny messages** — the other half of the tolerant-reader argument |
| Day 2, *Observability* | the runtime half of the gap this handout ends on |
