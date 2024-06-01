# Invalid Message Channel #

What happens when the message a consumer receives cannot be understood? For example the message is missing headers, or the body has an unexpected content type or does not match the expected schema.

Although the middleware has delivered the message to the receiver it cannot be passed to application code to process.

Further attempts to process the message will continue to result in failure because it is badly formed. The message risks becoming a 'poison pill' as the consumer will continue to try to read it from the channel. If there is a single consumer it will be blocked from reading other messages. If there is more than one consumer, a consumer will continue to 'choke' on that message.

But simply removing the message from the channel, by acking it but discarding it, risks that we will lose data. For example, it might be that a badly configured producer or consumer was using the wrong channel and the message was good.

The consumer  should move the message to an Invalid Message Channel, a special channel for messages that could not be processed by their receivers.

 Messages that cause application errors, but are well formed, should not be placed on the Invalid Message Channel, but treated as application errors.

 The Dead Letter Channel is for messages that cannot be delivered to the channel, and the Invalid Message Channel is for messages that were delivered, but cannot be understood.

 Some middleware, for example RabbitMQ confuses these terms, and uses Dead Letter Channel as an Invalid Message Channel, the destination for messages that the consumer rejects.

