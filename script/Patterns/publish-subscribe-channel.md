# Publish-Subscribe Channel #

If in a point-to-point channel only one consumer receives a message, how do I broadcast a message so that many consumers receive the same message?

Publish the message on a Publish-Subscribe Channel, which delivers a copy of a particular message to each consumer.

A Publish-Subscribe Channel has a publisher who sends a message to one input channel which is then replicated onto many output channels, each belonging to a separate subscriber.

When an event is published into the channel, the Publish-Subscribe Channel delivers a copy of the message to each of the output channels.

Each output channel functions much as a point-to-point channel. On any output channel, a consumer is only allowed to receive a message once. The middleware must use locking and read past to ensure that with multiple listeners, only one listener consumes the message.

Publish-subscribe allows eavesdropping on a message; a firehose of all channels can act like a message store.

A message may be sent by one publisher and consumed separately by many consumers via a router, which we discuss later. Both the channel and router based approach are often short-handed as publish-subscribe.
