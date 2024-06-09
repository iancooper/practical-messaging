# Polling Consumer #

In a Polling Consumer, the message pump makes an explicit call to check for the availability of messages to consume. This consumes a thread in the application, even if no messages are ready, but does not require a connection to be held open to the middleware.

