# Point-to-Point Channel #

With a Point-to-Point Channel only one consumer receives any message. If the channel has multiple consumers, the channel ensures that only one of them succeeds, so the receivers do not have to coordinate with each other.

The channel typically locks a message, either until the locking consumer acks or nacks it, or until the consumer times out on responding and the message is made available again.

If the message is acked, it is deleted from the queue.

Whilst the message is locked, other consumers read past the locked message.

Thus the application can scale out by having multiple consumers receive messages concurrently, but only a single consumer receives any one message.

If the channel chooses to return messages to the channel following a timeout, consumers may have to be prepared to receive duplicate messages, or abandon processing messages, before they time out.
