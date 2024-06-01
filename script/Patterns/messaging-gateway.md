# Messaging Gateway #

Within our Message Endpoint, we encapsulate the code that accesses the middleware in a Messaging Gateway. In this way, we isolate all the dependencies on the middleware into one component -- the Gateway. 

Our domain code is isolated from messaging concerns.

What is the difference between a Gateway and an Endpoint? The Endpoint contains the Gateway, but may also contain code to run a message pump, to map messages to domain types, call application code in the domain. In this model, the Gateway only abstracts the interaction with middleware, it does not provide the other features of a Message Endpoint.

We might create an endpoint that supports multiple middleware offerings. The gateway abstracts their individual implementation details, so that the endpoint code, which interacts with application code, can switch between different types of middleware, without the application code needing to change.
