# Default Exchange #

A default exchange simplifies the typical direct exchange scenario. A queue that does not supply a routing key when binding to a default exchange binds with the queue name as the routing key. The producer then sends to the queue name and the default exchange routes to the queue.

All messaging in RMQ uses an intermediary exchange, but the behavior of the Point-to-Point channel, which we will discuss later, pattern can be emulated using a direct exchange with the routing key of the queue name, or more simply by using the default exchange.