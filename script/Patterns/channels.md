# Channels #

A producer and a consumer communicate via a channel. A producer sends to a particular channel and a consumer reads from a particular channel


When we talk about messaging patterns, a channel is a logical view of the system not a physical one.

It is the virtual pipe down which messages flow.

Because the pipe is virtual, it's presence is just a logical address to which messages can be sent, and from which they can be received: this may be called a topic or a routing key, depending on the middleware.

Different Message Oriented Middleware solutions may provide different physical implementations of channels, such as whether messages are stored on in memory, on sender and receiver, or in a distributed database. 

These details are hidden from producer and consumer who only need to know how to address a channel

A channel is one-way -- we don't want to consume our own messages. For bi-directional messaging we use two channels, one for the request, and one for the reply (the reply channel is usually communicated by the sender)

Messaging is  one-to-one (Point-to-point Channel) or one to many (Publish-Subscribe Channel)

