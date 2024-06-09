# Event Driven Consumer #

In an Event Driven consumer, the message pump registers a callback with the middleware, and it is called when a message is available to be read, and passed the message. This does not consume a thread in the application, but it does require the connection between the client and the middleware server to be held open or for the application to serve requests from the middleware.
