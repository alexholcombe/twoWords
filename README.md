# twoWords
Psychopy experiment involving report of two simultaneously-presented words

Originally created for Word Thrills and Experiment Skills.

Does RSVP, and flashes one really large circle around both streams.

You provide it with a list of words/strings, and it independently samples from them to create the two streams.

Branched off of my [Attentional Blink code](https://github.com/alexholcombe/attentional-blink)

Issues

* Have approximately correct spit out to data file.
* Add Kim's single-shot code for reading in list of words from a file.
* After reading in, it's treated as two streams, so need to link them somehow to achieve nonword bigrams. Read in long list of non-word bigrams. On each trial, scramble them and then break into the two individual letters.

* Add pre-cues.
* Change cue size appropriately? Maybe separate circles in widely-spaced case.