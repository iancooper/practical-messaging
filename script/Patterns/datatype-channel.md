# Datatype Channel #

When a producer sends a message, how does the consumer know how to process it?

How does it know what the schema of the message body is, in order to deserialize the content and act upon it?

We can use a separate channel for each separate message schema, so that all messages on a particular channel share the same schema.

The producer, knowing what type the message is, publishes to an appropriate channel serializing the data to the message body.

The consumer, knowing what channel the message was received on, will know what its type is, and can deserialize the message body.

If a Datatype channel is not used, then the consumer will need to inspect the message to determine the type, using metadata in the message header or body, and then lookup how de-serialize messages of that type, before routing them to code that knows how to handle them.

This is unneeded complexity if a separate channel can be used.

The reason not to use a datatype channel is where there are messages that need to be processed in sequence but the messages have different schemas and they cannot be unified under a single schema.