# Pipes and Filters #

When we publish a message, we may need to do work before the eventual subscriber of that message takes action against our domain. We might need to encrypt/decrypt a message, we might need to enrich the content of the message from other data stores,  or we might need to transform the message from one format to another.

Pipes and filters is a pattern for dividing the transformation of data between origin and destination into steps that can be combined together. A data source at the head of the pipe begins the flow, and a data sink at the tail of the pipe receives the transformed output. Filters transform the data as it flows through the pipe.

We can treat the publisher as the data source, the final consumer as the data sink. and consumers that read, transformed, and publish that message before it reaches the sink as filters.

The structure of pipes and filters is straightforward. Each filter receives a message on an inbound channel and publishes it on an outbound channel. The pipe connects one filter to the next, sending output messages from one filter to the next.  Because each filter uses the same approach they can be composed into a chain. This allows simple, easily testable filters to be composed into arbitrarily complex applications.

A processing pipeline lets us work in parallel, because a filter can take more work off the queue to process when done, instead of blocking whilst the rest of the pipeline completes. This is known as a processing pipeline because messages flow through the filters like liquid through a pipe. A processing pipeline helps to increase throughput. A processing pipeline's throughput is limited by the slowest point in the chain. We could use multi-threading within that filter, but the alternative is to use competing consumers to parallelize the work of a stage. This allows one of many consumers to complete the work of that stage and is simpler to program and debug than using multi-threading. 


