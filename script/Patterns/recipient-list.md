# Recipient List #

In a content-based router, the properties of the message determine which branch a message takes. We may want the publisher to be able to explicitly decide which branches to take, by means of a list of those channels who should receive the message.

A metaphor here is the To list of an email - we indicate the recipients of the email and it is routed to them.

We define a channel for each consumer. The Recipient List inspects an incoming message, determine the list of desired consumers, and forwards the message to all channels associated with consumers in the list.

It is possible to invert the recipient list to give control to the consumers. In a dynamic recipient list, consumers send a list of messages they wish to subscribe to, via a control channel, to the Recipient List. This allows them to filter the messages that they wish to receive. 

A dynamic Recipient List can be used to implement a Publish-Subscribe Channel if a messaging system provides only Point-to-Point Channels but no Publish-Subscribe Channels. The Recipient List would keep a list of all Point-to-Point Channels that are subscribed to a topic. The publisher indicates the topic when sending the message, and the Recipient List routes the message to channels subscribed to that topic. This provides an interception point, at the time of subscription, that can be used to provide control, such as authorization, of subscriptions to a topic

Exchanges in RabbitMQ and SNS subscriptions in AWS are examples of dynamic recipient lists.
