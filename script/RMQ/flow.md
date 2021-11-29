# Flow #

AMQP allows the AMQ model to be programmable by the protocol - clients can programmatically declare the infrastructure they need, instead of relying on administrators to do so.

The flow for configuring the server can be run either by the client or the server, or both. Components that have already been declared can be re-declared, provided that the the parameters of the configuration are the same. For example a Message Queue named Foo can be declared by both Producer and Consumer. Provided both declarations agree on parameters such as, is the queue durable, there will not be an error on the re-declaration.

* Create a Connection to RMQ. RMQ uses a multiplexed TCP/IP connection consisting of one or more channels. Connections are expensive and should be pooled, channels are cheap. All subsequent commands are sent on the channel.
* Declare an Exchange. An application needs one or more exchanges, which route messages to queues according to their type. * Declare a Queue. A consumer needs to declare the queue for the exchange to forward messages to.
* Bind the Queue. A queue is bound to the exchange, using a routing key to identify what traffic should be routed to the queue.
