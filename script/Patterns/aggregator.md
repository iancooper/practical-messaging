# Aggregator #

A Splitter lets us break out a single message into parts, multiple messages that can be processed individually. It may be necessary to recombine these parts for further processing.

For example, when we use a Splitter to break up a batch job, we want to know when the batch completes, because all of the parts of the batch have completed. We also want to know if some parts of a batch completed, but others did not. 

An Aggregator collects and stores individual messages until a complete set of related messages has been received. Then, the Aggregator publishes a single message distilled from the individual messages.

An Aggregator depends on being able to correlate messages, usually by adding a correlation id to the message headers, to easily allow messages to be recombined. With a batch, it can also be useful for the aggregator to know how many messages were i the batch, so that the aggregator knows when it has seen all the messages.
