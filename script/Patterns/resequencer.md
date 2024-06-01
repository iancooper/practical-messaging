# Resequencer #

If the pipeline has conditional or parallel filter steps, some messages may complete the pipeline before others. If the messages were published in order, that order may now be lost. 

In the presence of errors, a filter step might be retried, which may move the retried message out of order.

If we have competing consumers reading from a channel, they will de-order the messages arriving on that channel.

If we need to re-order messages we can use a Resequencer. A Resequencer uses an internal buffer to store out-of-sequence messages until a complete sequence is obtained. The in-sequence messages are then published to the output channel. 

-- PAUSE 

The Resequencer needs to store the sequence number of the next expected message. A Resequencer first looks in its own buffer, to see if it has already read that message from the channel. If not, it reads another message from the channel. If that is the expected message it processes it, otherwise it puts it into the buffer. The process then repeats. Eventually, a message waiting in the buffer will be the next message, and will be freed.
