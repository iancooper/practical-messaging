# Message Translator #

The publisher may not use a format for a message that is understood by all consumers. This may be a version issue -- a downstream consumer may not be ready to receive a message whose format has a breaking change. It may be an issue with schemas that are not under control of the engineering team, such as external system or legacy code.  

A message translator is a filter step that converts a message from one schema to another, so that the output can be received by consumers that accept the alternative format.

In many cases a translator is temporary, once the consumer can accept the schema of the publisher then the translator can be retired.

