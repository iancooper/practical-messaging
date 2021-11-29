# Dynamic Router #

A content-based router can be difficult to maintain, because the router has to know about the possible branches in the path, thus creating a need to re-configure that router if the topology of the system changes.

A dynamic routers solves this problem by using a rules-engine to send messages to destinations which can be configured at run time.

A control channel allows configuration of the routing to be set by consumers. As a consumer starts up, it registers with the router to indicate the rules under which it should be sent messages. The Dynamic Router runs the rules over a message on receipt and determines the destination.  

Because consumers supply the rules under which the message should be routed to them, the dynamic router must determine what happens if two rules conflict, indicating that a message should be forwarded to more than one channel. Common strategies include last one wins. It is possible to route to all valid routes, but this is often actually another pattern: the recipient list.


