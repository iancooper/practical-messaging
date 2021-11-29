# Primitives #

The AMQ model defines a number of primitives.

* Exchanges are routers, that forward messages from Producers to Queues
* Message Queues hold messages and forward them to consuming applications
* Bindings are the relationship between an Exchange and a Message Queue that tells the Exchange how to route messages to Queues

Resources that are defined as Durable in AMQP survive a server restart. (Resources that don't survive a restart are Transient). Note that a message on a queue only survives a restart if it is sent as Persistent, not if the Queue itself is Durable, which simply means that the forwarding destination survives a restart.