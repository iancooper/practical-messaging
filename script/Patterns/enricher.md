# Content Enricher #

The data source in a pipeline, the publisher, may not have all the data that the data sink, the consumer, needs to process the message.

Imagine that the publisher sends a new order with an account id, but to ship the order we need the customer's address details, which are held on their account. The shipping consumer needs the customer's address to be added to the order message, before it can process the message.

This scenario is particularly common in microservice architectures, where each microservice only holds data that pertains to its area of responsibility and not others, requiring the data in the publisher's message to be joined to data held by other miroservices.

A Content Enricher is a filter step that adds the required data to the message. 

In the above example, one system publishes the order, a filter step belonging to another system listens to that message and enriches the content with the address data, and the system that handles shipping now has the data that it needs to process the order.


