# The Service Activator #

Whilst the message pump outlined directs calls to application code in response to messages, it is valuable for that code to be invoked by other callers. This is particularly useful to support writing developer tests against the handler, but can also allow the same code to service requests received via different protocols for example HTTP or GRPC.

A Service Activator is the pattern by which the endpoint code invokes application code to handle the message, but that application code is independent of the messaging endpoint. This can be synchronous and non-remote a method call - usually exposed by a service layer. The activator can be hard-coded to always invoke the same service, or can use reflection to invoke the service indicated by the message. The activator handles all of the messaging details and invokes the service like any other client, such that the service doesn’t know it’s being invoked through messaging.

A Service Activator can be one-way (request only) or two-way (Request-Reply).

