# Install Psychopy

Go to the [Psychopy download page](http://sourceforge.net/projects/psychpy/files/)

On the page somewhere you should see something like `Looking for the latest version? Download StandalonePsychoPy-[version number]-OSX.dmg (137.7 MB)`. It says OSX in my case because I'm using a Mac, but if you're using Windows it should recognise you instead want the Windows version. Also it won't say `version number`, instead it'll say the actual version number.

After your web browser downloads the StandalonePsychopy disk image, find it on your computer and double-click it. Then install it somewhere, e.g. your Applications Folder.

To test that it works correctly, double-click on Psychopy and run some of its demos.
On the menu bar at top, go to Demos->stimuli->textStimuli.py
To run it, click the green man at top.

You should see something like:
![alt text](https://github.com/alexholcombe/twoWords/blob/master/text_stimuli_screenshot.jpg "Screencap of textStimuli.py run")

If running on a laptop, the frames per second (fps) at bottom left of the screen should be close to 60 most of the time, like >55. It went down to 51 for me briefly because the actual act of taking the screenshot required CPU cycles that would otherwise have been used by Psychopy.

When you open a demo, its code appears in the Coder window. To see an example simple enough so you can understand the code, try Demos->basic->hello_world.py

Next steps: try [running the twoWords.py program](https://github.com/alexholcombe/twoWords/blob/master/Honours_HowToRun.md)

