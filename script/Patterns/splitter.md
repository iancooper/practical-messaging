# Splitter #

It may be that filters in the pipeline correspond with parts of a message, and it may be more efficient to split a message into multiple messages, derived from those dependencies, and send those new messages to those filters.

A splitter takes one input message, and breaks it into multiple output messages.

For example, different line items in an order, may need be handled by different consumers, and a splitter can route each line item in the order to the correct consumer.

It may also be useful where there is a batch of work in the original message. It can be difficult to observe the progress of a batch, it is either all waiting to be done, or done. Splitting the batch up allows us to observe the progress on the parts of the batch more easily, by the simple expedient of monitoring the number of messages waiting to be processed in the channel.


