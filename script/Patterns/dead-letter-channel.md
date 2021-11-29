# Dead Letter Channel #

What does the middleware do with a message a publisher sends, that it cannot deliver to the intended channel?

It may choose to move the message onto a Dead Letter Channel, which can later be reviewed by the operator. Often, the middleware will attempt redelivery of the message to channel a number of times, before it moves it to a dead letter channel.

Implementations vary. For example, a dead letter channel might be a point-to-point channel that can be read by one consumer, or a publish-subscribe channel that can be read by many consumers.

There is confusion between a dead letter channel, and an invalid message channel (the next pattern we will look at). We will discuss that issue further when considering that pattern.
