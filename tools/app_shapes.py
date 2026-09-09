#!/usr/bin/env python3
"""The three Day 1 drawings that show an *application*, not a pattern -- plan §8 class D.

    python3 tools/app_shapes.py                     # rebuild all three
    python3 tools/app_shapes.py boundary-what-crosses
    python3 tools/app_shapes.py --list

**Why these three are one family.** Everywhere else Day 1 draws a *pattern* -- one idea,
stripped to the two or three shapes that carry it. These draw a **shape you could
build**: processes with private data, talking over channels. §1's figure is the premise;
§4.3's pair is the first time the deck says *this is what it looks like in your
codebase*. What ties them is the reading, not the code: a dashed container is a
process, a box inside it is the application, and a cylinder inside it is data only that
process can reach. **`service()` is `boundary-what-crosses`'s alone** -- the task-queue
pair draws its boxes and its one shared cylinder directly, because its whole callout is
that there is no boundary there to draw.

**The boundary vocabulary is already taught, and this family must not invent a third
version of it.** Two families draw it already:

  * `coupling_grids.coupling-scale-boundary` -- a heavy ink rule *across* Myers' scale,
    with Content and Common struck out above it.
  * `integration_styles._frame()` -- a dashed container per process, and a **vertical
    ink rule** between them labelled *the process boundary*.

So the settled reading is **dashed box = a process, ink rule = the boundary between
two of them**, and this family uses exactly that. §1 comes *before* §3 in the deck, so
`boundary-what-crosses` is where the room meets the glyph for the first time; §3 then
reuses it without re-teaching it.

**§1's three bullets are one figure, not two.** They were `boundary-one-service` and
`boundary-two-services` until Ian ruled on the multi-figure entries (plan §8 item 23e),
and the second was the first one with a service added -- so the apparatus that had to
be drawn twice to say it, the rule and two containers and two stores, was most of the
drawing. Composed, it is drawn once, and **laid out in a row** so that the one drawing
fills the stage it is given rather than a third of it (`service`, and plan §8 item 23e):

  * a **message** crosses, on a channel each way -- the first bullet, and the only
    thing that is not refused;
  * a **read of another service's tables** is refused, crossed **on the rule**. What
    stops the reach is the boundary, not the database: a cross on the store would say
    *this database is locked*, which is a different and much weaker claim. It is the
    same claim `coupling-scale-boundary` makes as a scale and `style-shared-database`
    makes as a counter-example;
  * a **transaction across both** is refused, crossed on the same rule. A transaction
    is a scope, so it is drawn as one -- a red dashed container over the two stores,
    not instead of them, because each store has to stay inside the process that owns
    it.

**Both refusals land on the line, and that is the single red idea.** One line decides
both, which is what makes them one picture rather than two.

Hand-drawn register, like the rest of Day 1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

# Every figure here is compacted to this width before it is written. The label floor is
# in canvas units and the figure is scaled to fit its slide, so a wide canvas is not
# more detail -- it is smaller type in the room. 890 is where the 18pt diagram floor
# meets the deck's 18pt body floor at full slide width.
TARGET_W = 890

# The glyph is `integration_styles`'s -- the same ink rule, named the same way, because
# §1 and §3 argue about the same line. **The coordinates are not, and that is new.**
# §3's four styles stack an application over its store and come out square; this one
# lays the two out in a row (see `service`) and is two and a half times as wide, so the
# rule stands in a much wider drawing and MID moves with it. Shared vocabulary, not
# shared numbers -- and the line reads shorter here than it does in §3, which is the
# price of the row layout and was worth paying. Plan §8 item 23e.
MID = 710
BT = 76                           # where the boundary rule starts, under its own name


def figure(name):
    """Register a figure -- and compact it on the way out.

    **The compaction belongs here, not in `main()`.** Put it in `main()` and
    `lint_figures.py` measures the geometry as it was written rather than as it is
    rendered, and a label sitting on a stroke stays invisible for as long as the two
    disagree.
    """
    def wrap(fn):
        def build():
            return fn().compact(TARGET_W)
        build.__doc__ = fn.__doc__
        build.__name__ = fn.__name__
        FIGURES[name] = build
        return fn
    return wrap


def service(d, x, y, w, h, process, app, store, inboard, app_w=280, app_h=92,
            store_w=180, store_h=68, app_dy=48, store_dy=192):
    """A process: a dashed container, the application inside it, and the store that
    only it can reach -- drawn as a **row**, application and store side by side.

    **Row rather than stack, and it is arithmetic rather than taste.** A figure is
    fitted to its stage by whichever of width and height runs out first, and the
    stage on a figure slide is 2.57 : 1. Stacked, this drawing was 1.57 : 1: it was
    fitted by its *height*, gave back a third of the width, and every label landed at
    82% of the size Phase 2 measured it at. Laid out in a row it is 2.6 : 1, fills the
    stage, and lands at 96%. Below 2.57 : 1 nothing improves at all, so this is one
    change and not a series of them. Plan §8 item 23e has the working.

    **The store is drawn inside the container, always.** That is the whole argument of
    §1, and a figure that puts a database outside the box it belongs to has conceded it
    before the presenter opens their mouth. It cost a first draft of `two-services`,
    where the red transaction scope was drawn as a container holding both stores --
    which is a tidy picture of the wrong claim.

    **`inboard` says which side the boundary is on, and the two services mirror
    through it.** The application faces the line, because the application is the half
    that talks across it; the store sits at the far end, because the point of the
    figure is that nothing reaches it. There is no tie between the two: containment
    already says who owns the store, and a tie drawn across the row would run through
    the red scope's own label. Returns (app, store)."""
    d.group(x, y, w, h, process)
    if inboard == "r":
        ax, sx = x + w - 20 - app_w, x + 60
    else:
        ax, sx = x + 20, x + w - 60 - store_w
    box = d.box(ax, y + app_dy, app_w, app_h, app)
    cyl = d.cylinder(sx, y + store_dy, store_w, store_h, store)
    return box, cyl


def boundary(d, bottom):
    """The vertical ink rule, named above it. `bottom` is the figure's decision, not
    the frame's: the line has to reach whatever crosses it and stop before the caption
    that names the apparatus. Nothing may be centred on MID inside its span."""
    d.note(MID, 66, "the process boundary", INK, 18)
    d.rule(MID, BT, 0, INK, 2.6, h=bottom - BT)


@figure("boundary-what-crosses")
def boundary_what_crosses():
    """§1 *Messages In, Private Data, No Shared Transaction* -- **the load-bearing
    slide of both days, and now one picture rather than two.** Composed from what
    were `boundary-one-service` and `boundary-two-services`.

    **The slide has three bullets and the figure now has all three.** A message is
    the only way in; the data behind the line is private; no transaction spans it.
    Drawn apart, the second figure was the first one with a service added, so the
    reader had to carry the boundary across a click and re-find it -- and the
    apparatus that was duplicated to do it (the rule, two containers, two stores) is
    most of the drawing. Composed, it is drawn once and only the two refusals are
    drawn twice.

    **It is laid out in a row, and that is the whole of the 2026-09-09 change.**
    Composed but still stacked -- an application over its store, twice -- the drawing
    was 1.57 : 1 against a stage of 2.57 : 1, so it was fitted by its height, gave
    back a third of the stage's width, and every label on the most important slide of
    both days landed at **82%** of the size Phase 2 had measured it at. Application
    beside store, mirrored through the line, it is 2.60 : 1 and lands at **96%** --
    the stage's own width, and the cap. Nothing was cut to pay for it: the three
    bullets, both refusals and both crosses are where they were. Plan §8 item 23e.

    **What it cost, so that nobody re-discovers it as a defect.** §3's four
    `integration_styles` figures stack an application over its store and come out
    square; this one no longer matches them, so the boundary rule reads shorter here
    than it does there. The glyph is the same and the label is the same, and the two
    sections are half a day apart. That was the trade.

    **The outsider is now a peer service, and that is a better claim.** The first
    figure refused *another process* -- an anonymous outsider -- reaching into the
    Orders store. Shipping reaching into Orders' tables is the same refusal against
    the case the room actually argues for, because the two services are already on
    the drawing and already talking.

    **Both refusals are crossed on the rule itself, and that is the one idea.** What
    stops the reach is not the database and what stops the transaction is not the
    transaction manager: it is the line, in both cases, and the two crosses land on
    it. Putting a cross on the store instead would say *this database is locked*,
    which is a different and much weaker claim -- and the whole figure exists to say
    that one line decides both. `paper-guest-cycle` reds four hand-offs for one idea
    on the same grounds.

    **Its three foot comments are gone, and the callout is why.** The slide's own
    callout is *"No transaction spans two services. Consistency stops being something
    you declare and becomes something you design"*, which is what all three said. The
    space they were using is what the second refusal is drawn in.
    """
    d = Diagram("Messages In, Private Data, No Shared Transaction", w=1480, h=480)
    d.note(MID, 26, "the boundary refuses everything except the message",
           ANNOTATION, 21)
    boundary(d, 422)

    # A row apiece, mirrored through the line: the application against the boundary,
    # the store at the far end of its own container. Both stores stay INSIDE the
    # process that owns them -- a figure that puts a database outside its box has
    # conceded §1 before the presenter opens their mouth.
    ordering, orders = service(d, 40, 84, 600, 280, "the Ordering service",
                               "Ordering", "Orders", "r")
    shipping, _ = service(d, 780, 84, 600, 280, "the Shipping service",
                          "Shipping", "Shipments", "l")

    # **Two channels, not one.** A channel is one-way -- the fact §Conversations
    # spends a slide on -- and drawing it here costs nothing and saves that slide an
    # assertion. Both runs are horizontal and anchored to bare points rather than to
    # the boxes' midpoints: `sides=("r", "l")` puts both arrows on the same edge
    # centre and the pair comes out as a bowtie.
    out = d.pipe(665, 140, 90, 38)
    d.msg(699, 150, w=22, h=18)
    back = d.pipe(665, 184, 90, 38)
    d.msg(699, 194, w=22, h=18)
    d.arrow((620, 159), out, sides=(None, "l"))
    d.arrow(out, (800, 159), sides=("r", None))
    d.arrow((800, 203), back, sides=(None, "r"))
    d.arrow(back, (620, 203), sides=("l", None))

    # Refusal one: the read. A transaction is a scope and this is not -- it is one
    # service reaching for another's tables -- so it is an arrow, and it is stopped
    # where it meets the line rather than where it arrives.
    #
    # **It goes the long way round on purpose, and both drafts are why.** Dropped
    # straight down out of the Shipping box it runs through the red transaction scope
    # -- which reads as the read being part of the transaction -- and in the stacked
    # draft it ran through the Shipments cylinder, hidden, because the cylinder's fill
    # is painted over it. Neither is anything `lint_figures.py` measures. Routed
    # outside everything it can be confused with, it is unambiguous, it uses margin
    # that was empty anyway, and the shape of the route is itself the claim: there is
    # no way in that does not cross the line. The row layout shortens it -- Orders is
    # now at the near end of the run rather than the far side of its own container.
    #
    # **It leaves the Shipping box at 181 and not at 197, and the reason is the eye.**
    # 197 is where the return channel enters the box on the other side, so a red run
    # leaving seven units off it reads as a continuation of the blue arrow. 181 is
    # midway between the two channels and cannot be mistaken for either.
    #
    # **⚑ `lx` and `ly` are in FINAL canvas units, not the ones written here.** They
    # are added after `compact()`'s `k`, so a nudge means something different at every
    # scale -- and the label is inside `_extent`, so an over-large `ly` quietly makes
    # the figure TALLER and gives back the aspect the row layout was drawn for. Thirty
    # is the label clear of the run by nine and the figure at 2.60 : 1; thirty-three
    # is 2.54 : 1 and under the cap.
    d.arrow((1080, 181), orders, "read its tables", accent=True, dashed=True,
            via=[(1470, 181), (1470, 408), (190, 408)],
            sides=(None, "b"), lx=-370, ly=30)
    d.icon(MID, 408, "cross", accent=True, r=14)

    # Refusal two: the scope that cannot be had, drawn ACROSS the two services rather
    # than in place of them. Its top edge is 42 units above the stores rather than
    # level with them: a group's own label is set at the top LEFT, and level it lay
    # straight across the Orders cylinder -- which `lint_figures.py` cannot see,
    # because it measures notes against nodes and a group's label is neither.
    #
    # **The row layout is what lets this box hold the stores and nothing else.**
    # Stacked, a full-width band at the stores' height was the only place it could go
    # and it had the applications six units above it. In a row the applications sit a
    # whole band clear, and the scope encloses exactly the two things a transaction
    # would have to span.
    #
    # **And the 42 units are why `service` sets `app_dy` to 48.** The label band has
    # to hold the application clear of BOTH labels above it -- the container's own,
    # which on the right-hand service sits directly over the inboard application, and
    # this one, which sits directly under it. Neither collision is visible to
    # `lint_figures.py`: a group's label is neither a note nor a node.
    #
    # **"one transaction", not "one transaction across both".** A group's label is
    # set at its top LEFT, and text does not scale when `compact()` shrinks the
    # drawing -- so the longer label was 174 fixed units inside a container only
    # 600*k wide. The box visibly spans both services, so the picture already says
    # *across both*; the words did not need to.
    d.group(72, 234, 1276, 144, "one transaction", accent=True)
    d.icon(MID, 306, "cross", accent=True, r=16)
    return d


@figure("task-queue-shape")
def task_queue_shape():
    """§4.3 *Worked Example — the Task Queue*. The pump and competing consumers as an
    application shape, and the first time the deck draws something you could build.

    **One dashed container round the whole thing, and one database.** The slide's
    callout is *one team, one service, one queue — robustness without reorganising the
    company*, and that is a claim about where the boundary is **not**. §1 has just spent
    two figures on a boundary between two services with a store each; this is the same
    vocabulary saying the opposite thing, so the two halves share a store and sit inside
    one container. Drawing a boundary here would teach the room to reach for a new
    service every time a request is slow, which is exactly what the callout denies.

    Red is on the **return**, because that is what is bought. The queue is not the
    point; the queue is how.

    **The gaps between the boxes are load-bearing, not whitespace.** Every arrow here
    is labelled, an arrow label is centred on its own run, and it does not scale when
    `compact` runs -- so a 150-unit label needs a 190-unit gap or `lint_figures.py`
    reports it sitting on the box it leaves. That is what set the x positions.
    """
    d = Diagram("The Task Queue", w=1500, h=700)
    d.note(750, 46, "the web server returns before the work is done — "
                    "and the work is not lost, it waits", ANNOTATION, 21)

    d.group(25, 100, 1450, 480, "one service, one team — no new boundary")
    d.box(60, 206, 170, 96, "Browser")
    web = d.box(400, 200, 210, 108, "Web Server")
    pipe = d.pipe(900, 210, 220, 84)
    for i in range(4):
        d.msg(918 + i * 50, 236, w=30, h=24)
    workers = [d.box(1210, y, 200, 84, "Worker") for y in (146, 242, 338)]
    store = d.cylinder(760, 460, 240, 96, "one database")

    d.arrow((230, 228), (400, 228), "a request")
    d.arrow((400, 282), (230, 282), "returns now", accent=True)
    d.arrow(web, pipe, "enqueue the work", sides=("r", "l"), ly=-8)
    for w in workers:
        d.arrow(pipe, w, sides=("r", "l"))
    # both halves reach the same store -- that IS the "one service" claim, and it is
    # why the store sits between them rather than under the web server
    d.attach(web, store, sides=("b", "l"), via=[(505, 508)])
    d.attach(workers[2], store, sides=("b", "r"), via=[(1310, 508)])

    d.note(1010, 190, "a channel", INK, 18)
    # A name, so ink -- and it sits ABOVE the three boxes. Under them it was centred on
    # the same x as the tie running down to the store, which put a dashed hairline
    # between the two words. `lint_figures.py` cannot see that: it measures notes
    # against nodes, and an edge is neither.
    d.note(1310, 120, "competing consumers", INK, 18)
    d.note(750, 618, "the web server stays responsive when the backend is slow, "
                     "overwhelmed or down —", COMMENT, 18)
    d.note(750, 646, "add consumers until you drain faster than the work arrives",
           COMMENT, 18)
    return d


@figure("task-queue-http")
def task_queue_http():
    """§4.3 *Task Queue — HTTP Flow*. The same shape again, in the protocol everyone in
    the room already ships.

    **What the picture adds that the bullets cannot is that there are two paths.** The
    client posts to one place and comes back to a *different* one, while the work
    travels a path the client never sees. Drawing the four steps in a row would just
    restate the slide -- which is the failure the 2021 exports were full of -- so the
    work path runs across the top, the client's read path runs along the bottom, and
    the KV store is the only thing both of them touch.

    Red is on the 202, because that is the promise, and §4.4 opens by pointing out that
    nothing so far actually keeps it.

    **The worker's two outputs leave downwards and are told apart by route, not by
    label.** A vertical run puts its own label straight through itself -- `_mid` takes
    the middle segment -- so the one that needs saying gets a horizontal leg to say it
    on, and the one that does not is captioned underneath what it produces.
    """
    d = Diagram("The Task Queue over HTTP", w=1440, h=650)
    d.note(720, 46, "202 says: we have your work, and we will not lose it",
           ANNOTATION, 21)

    # **The client-to-web gap is 250 units and not 170 because two labels share it.**
    # `POST the work` and `202 + Location` are each about 92 units of type that does
    # not scale, and at the effective-width target the old gap came out 94 units wide
    # in the render -- both labels touching both boxes. This figure is fitted by its
    # HEIGHT (1.9 : 1), so horizontal room is the one thing it can spend for nothing:
    # widening it costs no legibility at all. Reach for that before shortening a label.
    client = d.box(60, 176, 190, 100, "Client")
    web = d.box(500, 176, 210, 100, "Web Server")
    pipe = d.pipe(860, 186, 220, 84)
    d.msg(892, 212, w=30, h=24)
    d.msg(952, 212, w=30, h=24)
    worker = d.box(1170, 176, 200, 100, "Worker")
    # 124 tall, not 92: a cylinder's rim costs 16 units of its interior and this one
    # carries two lines. At the effective-width target the body was 35 units for 38
    # units of type. The extra height is free -- the foot comment, not these, sets
    # this figure's content height.
    kv = d.cylinder(780, 414, 220, 124, "progress\n(a KV store)")
    order = d.cylinder(1160, 414, 220, 124, "the order itself")

    d.arrow((250, 200), (500, 200), "POST the work")
    d.arrow((500, 252), (250, 252), "202 + Location", accent=True)
    d.arrow(web, pipe, "enqueue it", sides=("r", "l"), ly=-8)
    d.arrow(pipe, worker, sides=("r", "l"))
    d.arrow(worker, kv, "notes progress as it goes", sides=("b", "t"),
            via=[(1200, 340), (890, 340)])
    d.arrow(worker, order, sides=("b", "t"))
    d.arrow(client, kv, "GET the progress page", sides=("b", "l"), via=[(155, 476)])

    d.note(970, 168, "a work item, waiting", INK, 18)
    d.note(1270, 582, "created at a sustainable pace —\n404 until it exists",
           COMMENT, 18)
    d.note(400, 600, "guaranteed delivery with no new infrastructure,\n"
                     "in a protocol the room already ships", COMMENT, 18)
    return d


def main(argv):
    if "--list" in argv:
        for n in FIGURES:
            print(n)
        return 0
    only = [a for a in argv if not a.startswith("--")]
    for name, fn in FIGURES.items():
        if only and name not in only:
            continue
        dg = fn()
        _, png = dg.save(os.path.join(OUT, name))
        print(f"  {name:<26} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
