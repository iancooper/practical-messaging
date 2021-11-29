# Competing Consumers #

If we wish to avoid a channel backing up, we must consume messages from the channel faster than they arrive. A simple algorithm helps with this. We compare the rate of arrival of messages with the rate of consumption of messages - how long before we ack or nack that message. If the rate of arrival exceeds the rate of consumption, we will back up. If this is not a burst of messages, and if we do not have a rate of consumption greater than that of arrival, we will not be able to eat our way through any backlog; we will now never catch up.

We may also need to process the message within a certain period from when they are published. If those messages come in bursts, but the processing of individual messages in the burst takes too long, we might not be able to process within that period.

The solution to both of these issues is to increase the number of consumers reading messages from the channel. The message queue must hand a message to only one consumer, so it must lock the message on the channel whilst it is being processed, and unlock it if it is returned to the channel. For example if the consumer fails. It must allow waiting consumers to read messages further down the channel if the message at the front is locked.

Competing consumers can create a problem with messages that need to be processed in sequence. Due to the requirement to lock and read past, consumers will not be able to guarantee that they will process messages on a channel in sequence. Indeed they may undo any sequence that the channel has already. In this case you cannot use competing consumers. 

Instead, if the rate of arrival exceeds the rate of consumption you must partition the messages using a consistent hashing algorithm such that you can preserve order within a partition and ensure that the rate of arrival of messages on a partition does not exceed the rate of consumption of messages from a single consumer of that partition.
