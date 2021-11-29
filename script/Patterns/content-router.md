# Content Based Router #

We may need a pipeline to branch. The condition that determines which path to take, may be based on the content of the message.

A Content-Based Router examines the message content and routes the message onto a different channel based on data contained in the message. The routing can be based on a number of criteria, such as existence of fields, specific field values, and so on.

The routing function should be easy to maintain, as the router can become a point of frequent maintenance. Some middleware uses rules-engines to support complex routing decisions. Be wary of moving too much decision making into middleware as this can become difficult to maintain or test.
