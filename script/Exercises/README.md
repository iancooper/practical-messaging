# Read Me First #

This is the order to work through this material. Some exercises are marked [Optional] and do not come with a slide deck, but if you have extra time, feel free to look at them. The code is marked up for what you need to implement to understand how RMQ provides those patterns. You may prefer to skip these, and return to them, if you have time.

## Precursors ##

These have speaker notes accompanying the slides

Introduction-To-Exercises.pptx 
Quick Start Rabbit MQ (RMQ).pptx

## Patterns and Exercises ##

## Channels ##
channels.mp4

### Point-to-Point ###

point-to-point_channel.mp4
point-to-point-exercise.pptx
Exercise: Point To Point

### Data Type Channel ###

datatype-channel.mp4
datatype-exercise.pptx
Exercise: Datatype Channel 

### Publish-Subscribe Channel ###

publish-subscribe-channel.mp4
[Optional] Publish Subscribe 

### Invalid Message Channel ###

dead-letter-channel.mp4
Invalid Message Channel.mp4
invalid-message-channel.pptx
Exercise: Invalid Message Channel

## Endpoints ##

message-endpoint.mp4
messaging-gateway.mp4

## Message Pump ##

message-pump.mp4
service-activator.mp4
competing-consumers.mp4

Exercise: Polling Consumer (C# & Python)/Event Consumer (JS)

## Pipelines ##

pipes-and-filters.mp4
content-based-router.mp4
dynamic-router.mp4
recipient-list.mp4
splitter.mp4
aggregator.mp4
resequencer.mp4
message-translator.mp4
content-enricher.mp4
pipes0and-filters-exercise.pptx
Exercise: Pipes and Filters

## Other Exercises ##

These examples show some useful patterns, but are all optional.

Guaranteed Delivery -- flags to make RMQ persist messages
Request-Reply -- sends a message and then blocks waiting for a reply. Can also use a correlation id, and non-blocking approach in production code
Routing Slip -- Message understands it's flow down the pipeline.



