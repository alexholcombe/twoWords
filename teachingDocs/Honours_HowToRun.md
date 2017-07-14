# twoWords
After you start Psychopy, you need to open
twoWords.py which you can find here on this github project page.

Additional files needed for full functioning of the program are:
* stringResponse.py
* noiseStaircaseHelpers.py

After you click Run (the green man at top of Psychopy), a few dialog boxes will pop up. If you accept all the default values in those boxes, the experiment will begin.

Its factorial design is 2 (words flipped or no) x 2 (respond first right/left) x 5 (serial position cued).

The dependent variables spit out (when all the trials are completed, or when you hit ESC to abort early) are:

* stream0 %correct
* stream0 %approximately correct
* stream1 %correct
* stream1 %approximately correct

But rather than overall performance, you probably want to see accuracy broken down by one or more of the factors, such as whether the words are flipped.

To do so, I write code in [R](http://www.r-project.org/). But you may want to use something that doesn't require programming. Like Microsoft Excel.

You'll have to work from the raw data file. Each time you run the program, it actually produces 3 files.  The beginning of the name of each file indicates the participant's name, date, and time.

* The .py file is just a copy of the program that generated the data (in case you change the program later, you will have this for reference)
* The .log file contains various info and diagnostics about how the session went.
* The .txt file is the actual data.

Its format is tab-delimited columns, with one row for each trial.

Pivottable