# Message Endpoint #

How does an application connect to a messaging channel to send and receive messages?

Our preference would be to separate the concerns of messaging, from the concerns of the domain. A developer should not need to understand the details of working with middleware, message formats, messaging channels, or any of the other details of communicating with other applications via messaging.

Application code just knows that it has data to send to another application, or is expecting data from another application.

It is the messaging endpoint code that takes that data, makes it into a message, and sends it on a particular messaging channel. It is the endpoint that receives a message, extracts the contents, and gives them to the application in a meaningful way.

A Message Endpoint abstracts the details of communication with messaging channels when sending or receiving messages. Message Endpoint code is custom to middleware's client API.