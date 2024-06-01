# The Message Pump #

NEXT

The Message Pump is the name given to the code that takes a message from a channel, and delivers it to application code. The pump runs in a loop, until cancelled.

NEXT

The loop takes messages from the channel, and then translates the data in the message body into a type that can be understood by the application code.

NEXT

The pump then looks up application code registered to handle messages of that type, and sends the translated message to that application code to be handled.

NEXT

Control passes from the Message Endpoint to application code, which executes in response to receipt of the message and handles it.

NEXT

When errors occur in the middleware, whilst attempting to deliver the message to the endpoint, the message can be moved to a Dead-Letter Channel.

NEXT 

When errors occur translating a message, then the message can be moved to an Invalid Message Channel.

NEXT

If errors occur dispatching a message to application code, it should be logged, and an exception thrown, as the application has been incorrectly configured. The message should not be acked and the application should be shut down, to avoid losing data.

NEXT

If errors occur in the application code, and those errors are not recoverable, then the message should be acked to remove it from the channel, as replaying it would have the same consequences, and the error should be logged. Processing may be able to continue with subsequent messages.

NEXT

If the message could be retried, because the condition causing the error is transient, then the message can be put back onto channel (usually with a delay) to retry. An upper limit on the number of retries is usually placed, to avoid poison pill messages. Ideally, messages that exceed the retry limit, should be handled the same way as an unrecoverable exception

NEXT - Translate and Dispatch 

A Messaging Mapper converts domain objects into a message as required by the messaging channel. 

It also provides the reverse capability, create or update a domain objects based on an incoming messages.

Because of this mediator, the domain does not need to know about messaging formats and vice-versa

--PAUSE
 
Typically, the endpoint allows registration of message mappers for channels, and uses a data type channel.

The application code that executes in response to a message it typically called a handler. Typically, handlers are subscribed to channels that the endpoint is configured to listen on.

NEXT - Polling Consumer

In a Polling Consumer, the message pump makes an explicit call to check for the availability of messages to consume. This consumes a thread in the application, even if no messages are ready, but does not require a connection to be held open to the middleware.

NEXT - Event Driven Consumer

In an Event Driven consumer, the message pump registers a callback with the middleware, and it is called when a message is available to be read, and passed the message. This does not consume a thread in the application, but it does require the connection between the client and the middleware server to be held open or for the application to serve requests from the middleware.
