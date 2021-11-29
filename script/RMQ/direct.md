# Direct Exchange #

In a direct exchange, a publisher specifies a routing key for a message, and a binding specifies queues that want messages with that routing key. Typically, in a direct exchange, the routing key is the name of the queue that the publisher wishes to publish to, and there is one queue. But a direct exchange may dispatch the message to a list of recipients if more than one is bound.

