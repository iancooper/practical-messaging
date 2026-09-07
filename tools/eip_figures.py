#!/usr/bin/env python3
"""The 12 EIP figures that replace the Hohpe & Woolf images in outlines/DayOne.md.

One script for the whole set, so the figures stay a family: same canvas widths, same
label voice, same convention for what red means. Regenerate all of them with

    python3 tools/eip_figures.py            # -> resources/eip-*.drawio + .png
    python3 tools/eip_figures.py --list     # names only

Conventions held across the set, from styles.md:
  * carbon arrows carry flow, ink carries structure, and RED MARKS ONE IDEA per figure
  * every figure states its idea in a red note -- the sentence the presenter says out loud
  * a muted note names the pattern element where the name is the thing being taught
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK, CARBON      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")

FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


# ---- the section opener ------------------------------------------------------

@figure("eip-the-big-picture")
def the_big_picture():
    """§4's opener, *The Big Picture* -- the map the other twelve figures hang off.

    **It is a composition over this family's vocabulary, not new vocabulary.** Domain
    code, a messaging gateway, a channel, an endpoint with a pump: every one of those
    is drawn somewhere in the twelve, and this figure's whole job is to put them on one
    line so the room can see where each of the day's questions lands. Nothing here may
    invent a shape the rest of the section does not use.

    **It carries §4's build order, because the slide has nothing else on it.** The body
    is one sentence -- *a map of the messaging patterns we will cover across the day* --
    and the section's own `#note` says the ordering is the point: what is the unit, how
    do I send and receive one, how do I keep receiving, how do I stop losing them, what
    kind of broker am I on. So the itinerary is drawn, as a list rather than as a strip
    of columns: **five columns of 18pt text do not fit in 890 units.** Text does not
    scale when `compact` runs, so a five-column strip leaves 178 units a column and the
    shortest of these questions is wider than that. A list is not a compromise here, it
    is the only shape that fits the floor.

    **The message is opened up, because §4.1's own slide has no picture at all.**
    *Message Construction* is body text and a presenter note, so header-and-body is
    introduced here or nowhere.

    The marker this replaces also named a *channel adapter*. It is not drawn: the deck
    never teaches the pattern, and a shape on the map that no later slide picks up is a
    promise the section does not keep.
    """
    d = Diagram("The Big Picture", w=1440, h=700)
    d.note(720, 46, "every pattern today hangs off this one line", ANNOTATION, 21)

    d.group(40, 140, 440, 190, "the sending application")
    dom1 = d.box(68, 190, 175, 100, "Domain\ncode")
    gw = d.box(277, 190, 175, 100, "Messaging\nGateway")
    pipe = d.pipe(570, 216, 300, 76)
    msg = d.msg(700, 238, w=40, h=32)
    d.group(960, 140, 440, 190, "the receiving application")
    ep = d.box(988, 190, 175, 100, "Endpoint\n+ pump")
    dom2 = d.box(1197, 190, 175, 100, "Domain\ncode")

    d.arrow(dom1, gw, sides=("r", "l"))
    d.arrow(gw, pipe, sides=("r", "l"))
    d.arrow(pipe, ep, sides=("r", "l"))
    d.arrow(ep, dom2, sides=("r", "l"))
    d.note(720, 186, "a channel", INK, 18)

    # the unit, opened up. Tied to the envelope it magnifies rather than floated near
    # it, because a blow-up that is not joined to its original is just a second message
    header = d.box(150, 440, 220, 52, "header")
    d.box(150, 492, 220, 74, "body")
    # down the outside and in from the left, not straight down onto the box: a riser
    # landing on the header's top edge runs through the caption that names it, and a
    # tie is one of the things `lint_figures.py` cannot measure a note against
    d.attach(msg, header, sides=("b", "l"),
             via=[(720, 380), (100, 380), (100, 466)])
    d.note(260, 420, "a message", INK, 18)

    d.note(620, 436, "and this is the order we meet it in", COMMENT, 18,
           anchor="start")
    for i, (num, q) in enumerate((
            ("4.1", "what is a message?"),
            ("4.2", "how do I send one, and receive one?"),
            ("4.3", "how do I keep receiving?"),
            ("4.4", "how do I stop losing them?"),
            ("4.5", "what kind of broker am I on?"))):
        y = 486 + i * 36
        d.note(620, y, num, INK, 18, anchor="start")
        d.note(700, y, q, COMMENT, 18, anchor="start")

    # compacted here rather than in `figure()`: the other twelve are 460-600 units wide
    # and already read at 27-35 real points, so this is the one figure in the family
    # that needs it. 890 is where the 18pt diagram floor meets the 18pt body floor.
    return d.compact(890)


# ---- 4.2 Channels and endpoints ---------------------------------------------

@figure("eip-point-to-point")
def point_to_point():
    """Sender, channel, one receiver. The idea is exclusivity, not topology."""
    d = Diagram("Point-to-Point Channel", w=460, h=220)
    snd = d.box(24, 84, 108, 58, "Sender")
    pipe = d.pipe(180, 96, 108, 32)
    for i in range(3):
        d.msg(196 + i * 30, 105, w=20, h=14)
    rcv = d.box(332, 84, 108, 58, "Receiver")
    d.arrow(snd, pipe, sides=("r", "l"))
    d.arrow(pipe, rcv, sides=("r", "l"))
    d.note(234, 68, "each message goes to exactly one receiver", ANNOTATION, 17)
    d.note(234, 160, "point-to-point channel", INK, 14)
    d.note(234, 196, "add receivers and they still do not need to coordinate", COMMENT, 14)
    return d


@figure("eip-publish-subscribe")
def publish_subscribe():
    """One input channel, an output channel per subscriber, a copy on each."""
    d = Diagram("Publish-Subscribe Channel", w=470, h=300)
    pub = d.box(20, 126, 104, 58, "Publisher")
    inp = d.pipe(158, 140, 76, 30)
    d.msg(184, 148, w=20, h=14)
    d.arrow(pub, inp, sides=("r", "l"))
    subs, outs = [], []
    for i, y in enumerate((40, 126, 212)):
        out = d.pipe(276, y + 14, 60, 26)
        d.msg(294, y + 20, w=18, h=13, accent=True)
        sub = d.box(360, y, 96, 54, f"Subscriber {i + 1}")
        outs.append(out)
        subs.append(sub)
        d.arrow(inp, out, sides=("r", "l"))
        d.arrow(out, sub, sides=("r", "l"))
    d.note(196, 118, "one input", INK, 14)
    d.note(306, 288, "an output channel per subscriber", INK, 14)
    d.note(300, 22, "a copy for every subscriber", ANNOTATION, 17)
    return d


@figure("eip-datatype-channel")
def datatype_channel():
    """A channel per schema -- so the channel is what tells you the type."""
    d = Diagram("Datatype Channel", w=470, h=290)
    snd = d.box(20, 110, 104, 58, "Sender")
    rcv = d.box(352, 110, 100, 58, "Receiver")
    for y, label in ((54, "Query"), (126, "Price Quote"), (198, "Purchase Order")):
        pipe = d.pipe(182, y, 108, 26)
        d.msg(206, y + 6, w=18, h=13)
        d.arrow(snd, pipe, sides=("r", "l"))
        d.arrow(pipe, rcv, sides=("r", "l"))
        d.note(236, y + 44, label, COMMENT, 15)
    d.note(236, 30, "one schema per channel", ANNOTATION, 17)
    d.note(236, 272, "so the consumer never has to inspect a message to know how to read it",
           COMMENT, 14)
    return d


@figure("eip-message-endpoint")
def message_endpoint():
    """The seam between application code and the messaging system."""
    d = Diagram("Message Endpoint", w=470, h=266)
    d.group(20, 74, 168, 112, "your application")
    app = d.box(36, 108, 136, 54, "Domain\ncode")
    end = d.box(220, 108, 116, 54, "Message\nEndpoint", accent=True)
    pipe = d.pipe(370, 122, 84, 26)
    d.arrow(app, end, sides=("r", "l"))
    d.arrow(end, pipe, sides=("r", "l"))
    d.note(412, 166, "channel", INK, 14)
    d.note(235, 42, "the endpoint is where the application\n"
                    "interoperates with others via messaging", ANNOTATION, 17)
    d.note(278, 226, "it makes the message and sends it -- and on the way back,\n"
                     "takes the contents out and hands them over", COMMENT, 14)
    return d


@figure("eip-messaging-gateway")
def messaging_gateway():
    """The gateway sits inside the endpoint; only it knows the broker."""
    d = Diagram("Messaging Gateway", w=490, h=250)
    app = d.box(18, 106, 96, 56, "Domain\ncode")
    d.group(142, 76, 226, 116, "message endpoint")
    pump = d.box(156, 108, 92, 52, "Pump\n+ Mapper")
    gw = d.box(266, 108, 88, 52, "Messaging\nGateway", accent=True)
    mw = d.box(398, 106, 76, 56, "Broker")
    d.arrow(app, pump, sides=("r", "l"))
    d.arrow(pump, gw, sides=("r", "l"))
    d.arrow(gw, mw, sides=("r", "l"))
    d.note(244, 38, "the only component that knows which broker this is",
           ANNOTATION, 17)
    d.note(244, 226, "swap the broker and nothing to the left of the gateway changes",
           COMMENT, 14)
    return d


# ---- 4.3 The message pump ----------------------------------------------------

@figure("eip-polling-consumer")
def polling_consumer():
    """The consumer asks. Red is on the asking."""
    d = Diagram("Polling Consumer", w=580, h=250)
    pipe = d.pipe(34, 112, 118, 30)
    d.msg(64, 120, w=20, h=14)
    pump = d.box(412, 100, 128, 56, "Message\nPump")
    d.arrow(pump, pipe, "receive()", accent=True,
            via=[(476, 58), (93, 58)], sides=("t", "t"))
    d.arrow(pipe, pump, "a message, or nothing", sides=("r", "l"), ly=-2)
    d.note(93, 168, "channel", INK, 14)
    d.note(290, 216, "holds a thread even when the channel is empty --\n"
                     "but needs no connection held open", COMMENT, 14)
    d.note(290, 26, "the consumer asks", ANNOTATION, 17)
    return d


@figure("eip-event-driven-consumer")
def event_driven_consumer():
    """The broker calls. Red is on the call -- the mirror of Polling Consumer."""
    d = Diagram("Event-Driven Consumer", w=580, h=250)
    pipe = d.pipe(34, 112, 118, 30)
    d.msg(64, 120, w=20, h=14)
    pump = d.box(412, 100, 128, 56, "Message\nPump")
    d.arrow(pump, pipe, "register callback", dashed=True, muted=True,
            via=[(476, 58), (93, 58)], sides=("t", "t"))
    d.arrow(pipe, pump, "on message", accent=True, sides=("r", "l"), ly=-2)
    d.note(93, 168, "channel", INK, 14)
    d.note(290, 216, "no thread while idle -- but the connection stays open,\n"
                     "and the broker sets the pace", COMMENT, 14)
    d.note(290, 26, "the broker calls", ANNOTATION, 17)
    return d


@figure("eip-service-activator")
def service_activator():
    """The line between the messaging code and your code. Red IS the line."""
    d = Diagram("Service Activator", w=600, h=250)
    pipe = d.pipe(14, 112, 58, 28)
    d.group(94, 74, 236, 124, "messaging gateway -- written once")
    pump = d.box(108, 112, 96, 54, "Message\nPump")
    mapper = d.box(222, 112, 96, 54, "Message\nMapper")
    act = d.box(368, 112, 112, 54, "Service\nActivator", accent=True)
    d.group(508, 74, 84, 124, "your code")
    handler = d.box(518, 112, 66, 54, "Handler")
    d.arrow(pipe, pump, sides=("r", "l"))
    d.arrow(pump, mapper, sides=("r", "l"))
    d.arrow(mapper, act, sides=("r", "l"))
    d.arrow(act, handler, sides=("r", "l"))
    d.note(43, 158, "channel", INK, 14)
    d.note(400, 40, "the handler never learns it was a message", ANNOTATION, 17)
    d.note(300, 228, "a domain type in, a return or a throw out -- "
                     "no channel, no headers, no ack", COMMENT, 14)
    return d


@figure("eip-message-dispatcher")
def message_dispatcher():
    """Competing consumers. Red is on throughput, not on exclusivity."""
    d = Diagram("Competing Consumers", w=460, h=310)
    pipe = d.pipe(24, 134, 158, 40)
    for i in range(4):
        d.msg(44 + i * 30, 146, w=20, h=15)
    a = d.box(304, 44, 128, 56, "Consumer")
    b = d.box(304, 126, 128, 56, "Consumer")
    c = d.box(304, 208, 128, 56, "Consumer", accent=True)
    d.arrow(pipe, a, "1", sides=("r", "l"), ly=-2)
    d.arrow(pipe, b, "2", sides=("r", "l"), ly=-2)
    d.arrow(pipe, c, "3", accent=True, sides=("r", "l"), ly=-2)
    d.note(103, 208, "arriving faster than one\nconsumer can drain", COMMENT, 14)
    d.note(240, 24, "add consumers until you consume faster than they arrive",
           ANNOTATION, 17)
    d.note(240, 292, "the cost: lock-and-read-past means order is no longer preserved",
           COMMENT, 14)
    return d


# ---- 4.4 When the pump fails -------------------------------------------------

@figure("eip-invalid-message-channel")
def invalid_message_channel():
    """Delivered, not understood. The RECEIVER diverts -- that is the whole
    distinction from Dead Letter, so the divert starts at the receiver."""
    d = Diagram("Invalid Message Channel", w=470, h=300)
    snd = d.box(20, 70, 100, 54, "Sender")
    pipe = d.pipe(162, 84, 92, 26)
    d.msg(184, 90, w=18, h=13)
    rcv = d.box(306, 70, 128, 54, "Receiver")
    d.arrow(snd, pipe, sides=("r", "l"))
    d.arrow(pipe, rcv, sides=("r", "l"))
    inv = d.pipe(288, 210, 164, 28, accent=True)
    d.msg(316, 217, w=18, h=13, accent=True)
    d.arrow(rcv, inv, "cannot read it", accent=True, sides=("b", "t"), lx=-62)
    d.note(370, 264, "invalid message channel", INK, 14)
    d.note(235, 34, "it arrived -- the receiver just cannot understand it",
           ANNOTATION, 17)
    d.note(150, 188, "a well-formed message that\nmerely fails is an application\n"
                     "error, not an invalid one", COMMENT, 14)
    return d


@figure("eip-dead-letter-channel")
def dead_letter_channel():
    """Could not be delivered. The BROKER diverts, and the receiver never sees it."""
    d = Diagram("Dead Letter Channel", w=470, h=300)
    snd = d.box(20, 70, 100, 54, "Sender")
    pipe = d.pipe(168, 84, 108, 26)
    d.msg(192, 90, w=18, h=13)
    rcv = d.box(330, 70, 110, 54, "Receiver")
    d.arrow(snd, pipe, sides=("r", "l"))
    d.arrow(pipe, rcv, "never arrives", dashed=True, muted=True, sides=("r", "l"), lx=-24, ly=-18)
    dlq = d.pipe(156, 210, 164, 28, accent=True)
    d.msg(184, 217, w=18, h=13, accent=True)
    # the divert runs vertically, so a centred label is struck through by its own
    # arrow -- push it clear rather than nudge it
    d.arrow(pipe, dlq, "gave up after N tries", accent=True, sides=("b", "t"), lx=-88)
    d.note(238, 264, "dead letter channel", INK, 14)
    d.note(235, 34, "the broker could not deliver it, so the broker puts it aside",
           ANNOTATION, 17)
    d.note(385, 150, "the receiver never\nsaw this one", COMMENT, 14)
    return d


# ---- 6.2 Message design ------------------------------------------------------

@figure("eip-content-enricher")
def content_enricher():
    """The enricher moves the lookup. Red is on the lookup, because that is
    the callout: it did not go away."""
    d = Diagram("Content Enricher", w=480, h=332)
    src = d.box(16, 96, 116, 58, "Order\nAccountId")
    enr = d.box(184, 96, 116, 58, "Content\nEnricher")
    out = d.box(352, 96, 116, 58, "Order\n+ address")
    db = d.cylinder(198, 222, 90, 58, "Customer")
    d.arrow(src, enr, sides=("r", "l"))
    d.arrow(enr, out, sides=("r", "l"))
    d.arrow(enr, db, "read the address", accent=True, sides=("b", "t"), lx=64)
    d.note(242, 34, "the lookup did not go away -- it moved here", ANNOTATION, 17)
    d.note(74, 180, "incomplete", INK, 14)
    d.note(410, 180, "complete", INK, 14)
    d.note(240, 300, "and now the shipping consumer depends on the enricher too --\n"
                     "the same availability sum, one hop further away", COMMENT, 14)
    return d


def main(argv):
    if "--list" in argv:
        for name in FIGURES:
            print(name)
        return 0
    only = [a for a in argv if not a.startswith("--")]
    for name, fn in FIGURES.items():
        if only and name not in only:
            continue
        d = fn()
        drawio, png = d.save(os.path.join(OUT, name))
        print(f"  {name:<32} {d.w}x{d.h}  {os.path.getsize(png):>7,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
