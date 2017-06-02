#Alex Holcombe alex.holcombe@sydney.edu.au
#See the github repository for more information: https://github.com/alexholcombe/twoWords
from __future__ import print_function #use python3 style print
from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan, log, ceil
from copy import deepcopy
import copy
import time, sys, os, pylab, random, string
try:
    from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
except ImportError:
    print('Could not import from noiseStaircaseHelpers.py (you need that file to be in the same directory)')
try:
    import stringResponse
except ImportError:
    print('Could not import stringResponse.py (you need that file to be in the same directory)')
    
try:
    import letterLineupResponse
except ImportError:
    print('Could not import letterLineupResponse.py (you need that file to be in the same directory)')

tasks=['T1']; task = tasks[0]
#THINGS THAT COULD PREVENT SUCCESS ON A NEW MACHINE
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix

quitFinder = False #if checkRefreshEtc, quitFinder becomes True.
autopilot=False
demo=False #False
exportImages= False #quits after one trial
subject='Hubert' #user is prompted to enter true subject name
if autopilot: subject='auto'
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print('"data" directory does not exist, so saving data in present working directory')
    dataDir='.'
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=True
autoLogging=False
refreshRate = 60.;  #100
if demo:
    refreshRate = 60.;  #100

staircaseTrials = 25
prefaceStaircaseTrialsN = 20 #22
prefaceStaircaseNoise = np.array([5,20,20,20, 50,50,50,5,80,80,80,5,95,95,95]) #will be recycled / not all used, as needed
descendingPsycho = True #psychometric function- more noise means worse performance
threshCriterion = 0.58

numWordsInStream = 26 #Experiment will only work if all 26 letters are presented, otherwise error when you pick a letter that was not presented
wordsUnparsed="a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z" 
wordList = wordsUnparsed.split(",") #split into list
for i in range(len(wordList)):
    wordList[i] = wordList[i].replace(" ", "") #delete spaces
if len(wordList) > numWordsInStream:
    print("WARNING: you have asked for streams that have more stimuli than are in the wordList, so some will be duplicated")
#Later on, a list of indices into this list will be randomly permuted for each trial
print(wordList)
print(len(wordList))

bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [1.,1.,1.]
letterColor = [1.,1.,1.]
cueRadius = 3 #6 deg in Goodbourn & Holcombe
widthPix= 1920 #1280 #monitor width in pixels of Agosta
heightPix= 1080 #800 #monitor height in pixels
monitorwidth = 52.2 #38.7 #monitor width in cm
scrn=1 #0 to use main screen, 1 to use external screen connected to computer
fullscr=True #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 600; heightPix = 600
    monitorwidth = 13.0
    fullscr=False; scrn=0
    framesSaved=0
if demo:    
    scrn=0; fullscr=False
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
viewdist = 57. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
print('pixelperdegree=',pixelperdegree)
    
    
    
try:
    click=sound.Sound('406__tictacshutup__click-1-d.wav')
except: #in case file missing, create inferiro click manually
    logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
    click=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)


clickSound, badKeySound = stringResponse.setupSoundsForResponse()

# create a dialog from dictionary 
infoFirst = { 'Do staircase (only)': False, 'Check refresh etc':True, 'Fullscreen (timing errors if not)': False, 'Screen refresh rate':refreshRate }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='Dual-RSVP experiment OR staircase to find thresh noise level for performance criterion', 
    order=['Do staircase (only)', 'Check refresh etc', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating'},
    #fixed=['Check refresh etc'])#this attribute can't be changed by the user
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
doStaircase = infoFirst['Do staircase (only)']
checkRefreshEtc = infoFirst['Check refresh etc']
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']
if checkRefreshEtc:
    quitFinder = True 
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)

#letter size 2.5 deg
SOAms = 100 # 133 #Battelli, Agosta, Goodbourn, Holcombe mostly using 133
#Minimum SOAms should be 84  because any shorter, I can't always notice the second ring when lag1.   71 in Martini E2 and E1b (actually he used 66.6 but that's because he had a crazy refresh rate of 90 Hz)
letterDurMs = 80 #23.6  in Martini E2 and E1b (actually he used 22.2 but that's because he had a crazy refresh rate of 90 Hz)

ISIms = SOAms - letterDurMs
letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
cueDurFrames = letterDurFrames
ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
#have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
rateInfo = 'total SOA=' + str(round(  (ISIframes + letterDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + letterDurFrames) + ' frames, comprising\n'
rateInfo+=  'ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and letterDurFrames ='+str(letterDurFrames)+' or '+str(round( letterDurFrames*(1000./refreshRate), 2))+'ms'
logging.info(rateInfo); print(rateInfo)

trialDurFrames = int( numWordsInStream*(ISIframes+letterDurFrames) ) #trial duration in frames

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()
refreshMsg2 = ''
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    #print(runInfo)
    logging.info(runInfo)
    print('Finished runInfo- which assesses the refresh and processes of this computer') 
    #check screen refresh is what assuming it is ##############################################
    Hzs=list()
    myWin.flip(); myWin.flip();myWin.flip();myWin.flip();
    myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
    print('About to measure frame flips') 
    for i in range(50):
        myWin.flip()
        Hzs.append( myWin.fps() )  #varies wildly on successive runs!
    myWin.setRecordFrameIntervals(False)
    # end testing of screen refresh########################################################
    Hzs = np.array( Hzs );     Hz= np.median(Hzs)
    msPerFrame= 1000./Hz
    refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True
myWin.close() #have to close window to show dialog box

defaultNoiseLevel = 0.0 #to use if no staircase, can be set by user
trialsPerCondition = 10 #default value
dlgLabelsOrdered = list()
if doStaircase:
    myDlg = gui.Dlg(title="Staircase to find appropriate noisePercent", pos=(200,400))
else: 
    myDlg = gui.Dlg(title="RSVP experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name (default="Hubert"):', 'Hubert', tip='or subject code')
    dlgLabelsOrdered.append('subject')
if doStaircase:
    easyTrialsCondText = 'Num preassigned noise trials to preface staircase with (default=' + str(prefaceStaircaseTrialsN) + '):'
    myDlg.addField(easyTrialsCondText, tip=str(prefaceStaircaseTrialsN))
    dlgLabelsOrdered.append('easyTrials')
    myDlg.addField('Staircase trials (default=' + str(staircaseTrials) + '):', tip="Staircase will run until this number is reached or it thinks it has precise estimate of threshold")
    dlgLabelsOrdered.append('staircaseTrials')
    pctCompletedBreak = 101
else:
    myDlg.addField('\tPercent noise dots=',  defaultNoiseLevel, tip=str(defaultNoiseLevel))
    dlgLabelsOrdered.append('defaultNoiseLevel')
    myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
    dlgLabelsOrdered.append('trialsPerCondition')
    pctCompletedBreak = 20
    
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)

if checkRefreshEtc and (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.error(msgWrongResolution)
    print(msgWrongResolution)

dimGreyForDlgBox = 'DimGrey'
from distutils.version import LooseVersion
if LooseVersion(psychopy.__version__) < LooseVersion("1.84.2"):
    dimGreyForDlgBox = [-1.,1.,-1.] #color names stopped working along the way, for unknown reason
myDlg.addText('Note: to abort press ESC at a trials response screen', color=dimGreyForDlgBox) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()

if myDlg.OK: #unpack information entered in dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
   if doStaircase:
       if len(thisInfo[dlgLabelsOrdered.index('staircaseTrials')]) >0:
           staircaseTrials = int( thisInfo[ dlgLabelsOrdered.index('staircaseTrials') ] ) #convert string to integer
           print('staircaseTrials entered by user=',staircaseTrials)
           logging.info('staircaseTrials entered by user=',staircaseTrials)
       if len(thisInfo[dlgLabelsOrdered.index('easyTrials')]) >0:
           prefaceStaircaseTrialsN = int( thisInfo[ dlgLabelsOrdered.index('easyTrials') ] ) #convert string to integer
           print('prefaceStaircaseTrialsN entered by user=',thisInfo[dlgLabelsOrdered.index('easyTrials')])
           logging.info('prefaceStaircaseTrialsN entered by user=',prefaceStaircaseTrialsN)
   else: #not doing staircase
       trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
       print('trialsPerCondition=',trialsPerCondition)
       logging.info('trialsPerCondition =',trialsPerCondition)
       defaultNoiseLevel = int (thisInfo[ dlgLabelsOrdered.index('defaultNoiseLevel') ])
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()
if not demo: 
    allowGUI = False

myWin = openMyStimWindow() #reopen stim window. Had to close test window to allow for dialogue boxes
#set up output data file, log file, copy of program code, and logging
infix = '' #part of the filenames
if doStaircase:
    infix = 'staircase_'
fileName = os.path.join(dataDir, subject + '_' + infix+ timeAndDateStr)
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')
    saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
    os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
    logFname = fileName+'.log'
    ppLogF = logging.LogFile(logFname, 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout; logF = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.ERROR) #DEBUG means set  console to receive nearly all messges, INFO next level, EXP, DATA, WARNING and ERROR 

if fullscr and not demo and not exportImages:
    runInfo = psychopy.info.RunTimeInfo(
        # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
        #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
        #version="<your experiment version info>",
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=False, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        #randomSeed='set:42', ## a way to record, and optionally set, a random seed of type str for making reproducible random sequences
            ## None -> default 
            ## 'time' will use experimentRuntime.epoch as the value for the seed, different value each time the script is run
            ##'set:time' --> seed value is set to experimentRuntime.epoch, and initialized: random.seed(info['randomSeed'])
            ##'set:42' --> set & initialize to str('42'), and will give the same sequence of random.random() for all runs of the script
        )
    logging.info(runInfo)
logging.flush()

def detectDuplicates(myList):
    uniqueVals = set(myList)
    if len( list(uniqueVals) ) < len(myList):
        return True
    else: return False
    
def readFileAndScramble(numWordsInStream):
        #Abandoning use of this for Cheryl's experiment because too hard to find enough non-word bigrams for which letters not repeated in either stream
        stimFile = 'wordStimuliGeneration/twoLetters-Cheryl.txt'
        stimListFile= open(stimFile)
        bigramList = [x.rstrip() for x in stimListFile.readlines()]
        print('Read in', len(bigramList), 'strings')
        #print('bigramList = ',bigramList)
        stimListFile.close()
        #Scramble 
        shuffled = deepcopy(bigramList)
        
        shuffleUntilNoDuplicatesOfFirstOrSecondLetter = True
        duplicates = True #intiialise this as true so the loop will run at least once
        while shuffleUntilNoDuplicatesOfFirstOrSecondLetter and duplicates:
            random.shuffle(shuffled)
            #print('first 10 unshuffled=',bigramList[:10])
            #print('first 10 shuffled=',shuffled[:10])
            #Break into two
            firstLetters = list()
            secondLetters = list()
            for bigram in shuffled[:numWordsInStream]:
                firstLetter = bigram[0]
                secondLetter = bigram[1]
                firstLetters.append( firstLetter )
                secondLetters.append ( secondLetter ) 
            print("shuffled firstLetters=",firstLetters," secondLetters=",secondLetters)
            duplicates = detectDuplicates(firstLetters)
            if not duplicates:
                duplicates = detectDuplicates(secondLetters)
                
        print('first 20 shuffled firstLetters=',firstLetters[:20])
        print('first 20  shuffled secondLetters=',secondLetters[:20])
        return firstLetters, secondLetters

def findLtrInList(letter,wordList):
    try:
        idx = wordList.index(letter)
    except ValueError:
        print("Error! ", letter," not found in wordList")
    except Exception as e:
        print('Unexpected error',e)
    #print("Searched for ",letter," in the wordList and index returned was ",idx)
    return idx
    
def calcSequenceForThisTrial():
    print("lenWordlist",len(wordList))
    idxsIntoWordList = range(len(wordList)) #create a list of indexes of the entire word list: 0,1,2,3,4,5,...23
    print("idxsInto",idxsIntoWordList)
    readFromFile = False
    if readFromFile:
        #read in the file of list of bigrams. Doesn't work because  too hard to find enough non-word bigrams for which letters not repeated in either stream
        firstLetters, secondLetters = readFileAndScramble(numWordsInStream)
        #Now must determine what indexes into the wordList (list of letters pre-drawn) correspond to these
        idxsStream1 = list()
        print("idxsStream1FirstTime",idxsStream1)
        idxsStream2 = list()
        print("idxsStream2FirstTime",idxsStream2)
        for ltri in range(numWordsInStream): #Find where in the "wordList" each letter is, add it to idxsStream1
            letter = firstLetters[ltri]
            idx = findLtrInList(letter, wordList)
            idxsStream1.append(idx)
            print("idxsStream1SecondTime",idxsStream1)
        #print("final idxsStream1=",idxsStream1)
        for ltri in range(numWordsInStream): #Find where in the "wordList" each letter is, add it to idxsStream1
            letter = secondLetters[ltri]
            idx = findLtrInList(letter, wordList)
            idxsStream2.append(idx)
            print("idxsStream2SecondTime",idxsStream2)
    else: #if not readFromFile: #just create a shuffled index of all the possibilities
        np.random.shuffle(idxsIntoWordList) #0,1,2,3,4,5,... -> randomly permuted 3,2,5,...
        print("idxsintoWordList",idxsIntoWordList)
        idxsStream1 = copy.deepcopy(idxsIntoWordList) #first RSVP stream
        idxsStream1= idxsStream1[:numWordsInStream] #take the first numWordsInStream of the shuffled list
        idxsStream2 = copy.deepcopy(idxsIntoWordList)  #make a copy for the right stream, and permute them on the next list
        np.random.shuffle(idxsStream2)
        idxsStream2= idxsStream2[:numWordsInStream]  #take the first numWordsInStream of the shuffled list
        print("idxsStream1",idxsStream1)
        print("idxsStream2",idxsStream2)
    return idxsStream1, idxsStream2
    
textStimuliStream1 = list()
textStimuliStream2 = list() #used for second, simultaneous RSVP stream
def calcAndPredrawStimuli(wordList,cues, preCues,thisTrial): #Called before each trial 
    #textStimuliStream1 and 2 assumed to be global variables
    if len(wordList) < numWordsInStream:
        print('Error! Your word list must have at least ',numWordsInStream,'strings')
    #print('wordList=',wordList)
    textStimuliStream1[:] = [] #Delete all items in the list
    textStimuliStream2[:] = [] #Delete all items in the list
    for i in xrange( len(cues) ):
        eccentricity = thisTrial['wordEccentricity']
        if eccentricity < 2:  #kludge to deal with very low separation case where want just one cue - draw them both in the same place
            eccentricity = 0
        if i==0: 
            cues[i].setPos( [-eccentricity, 0] )
            preCues[i].setPos( [-eccentricity, 0] )
        else:  
            cues[i].setPos( [eccentricity, 0] )
            preCues[i].setPos( [eccentricity, 0] )
    for i in range(0,len(wordList)): #draw all the words. Later, the seq will indicate which one to present on each frame. The seq might be shorter than the wordList
       word = wordList[ i ]
       #flipHoriz, flipVert  textStim http://www.psychopy.org/api/visual/textstim.html
       #Create one bucket of words for the left stream
       textStimulusStream1 = visual.TextStim(myWin,text=word,height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging) 
       #Create a bucket of words for the right stream
       textStimulusStream2 = visual.TextStim(myWin,text=word,height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
       textStimulusStream1.setPos([-thisTrial['wordEccentricity'],0]) #left
       textStimuliStream1.append(textStimulusStream1) #add to list of text stimuli that comprise  stream 1
       textStimulusStream2.setPos([thisTrial['wordEccentricity'],0]) #right
       textStimuliStream2.append(textStimulusStream2)  #add to list of text stimuli that comprise stream 2
    
    #Use these buckets by pulling out the drawn words in the order you want them. For now, just create the order you want.
    idxsStream1, idxsStream2 = calcSequenceForThisTrial()

    return idxsStream1, idxsStream2, cues, preCues
    
#create click sound for keyboard
try:
    click=sound.Sound('406__tictacshutup__click-1-d.wav')
except: #in case file missing, create inferiro click manually
    logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
    click=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)

if showRefreshMisses:
    fixSizePix = 32 #2.6  #make fixation bigger so flicker more conspicuous
else: fixSizePix = 32
fixColor = [1,1,1]
if exportImages: fixColor= [0,0,0]
fixatnNoiseTexture = np.round( np.random.rand(fixSizePix/4,fixSizePix/4) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation

#Construct the fixation point.
fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False)
fixationBlank= visual.PatchStim(myWin, tex= -1*fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False) #reverse contrast
fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(1,-1,-1),size=4,units='pix',autoLog=autoLogging)
#Construct the holders for the experiment text that will appear on screen
respPromptStim = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
acceptTextStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=3,units='deg',autoLog=autoLogging)
requireAcceptance = True
nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)

#clickSound, badKeySound = stringResponse.setupSoundsForResponse()

screenshot= False; screenshotDone = False
stimList = []
#SETTING THE CONDITIONS, This implements the full factorial design!
cueSerialPositions = np.array([7,9,11,13,15])
for cueSerialPos in cueSerialPositions:
   for rightResponseFirst in [False,True]:
      for wordEcc in [0.8,6]:
        stimList.append( {'cueSerialPos':cueSerialPos, 'rightResponseFirst':rightResponseFirst,
                                    'leftStreamFlip':False, 'rightStreamFlip':False,
                                     'wordEccentricity':wordEcc } )

trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method. Duplicate the list of conditions trialsPerCondition times to create the full experiment
trialsForPossibleStaircase = data.TrialHandler(stimList,trialsPerCondition) #independent randomization, just to create random trials for staircase phase
numRightWrongEachCuepos = np.zeros([ len(cueSerialPositions), 1 ]); #summary results to print out at end

logging.info( 'numtrials=' + str(trials.nTotal) + ' and each trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' + '  task=' + task)

def numberToLetter(number): #0 = A, 25 = Z
    #if it's not really a letter, return @
    if number < 0 or number > 25:
        return ('@')
    else: #it's probably a letter
        try:
            return chr( ord('A')+number )
        except:
            return('@')

def letterToNumber(letter): #A = 0, Z = 25
    #if it's not really a letter, return -999
    #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT'S NOT PART OF AN ARRAY?
    try:
        #if len(letter) > 1:
        #    return (-999)
        if letter < 'A' or letter > 'Z':
            return (-999)
        else: #it's a letter
            return ord(letter)-ord('A')
    except:
        return (-999)

def wordToIdx(word,wordList, responseMustBeInWordList):
    #if it's not in the list of stimuli, return None
    try:
        #http://stackoverflow.com/questions/7102050/how-can-i-get-a-python-generator-to-return-none-rather-than-stopiteration
        firstMatchIdx = next((i for i, val in enumerate(wordList) if val.upper()==word), None) #return i (index) unless no matches, in which case return None
        #print('Looked for ',word,' in ',wordList,'\nfirstMatchIdx =',firstMatchIdx)
        return firstMatchIdx
    except:
        if responseMustBeInWordList:
            print('Unexpected error in wordToIdx with word=',word)
        return (None)
        
#print header for data file
print('experimentPhase\ttrialnum\tsubject\ttask\t',file=dataFile,end='')
print('noisePercent\tleftStreamFlip\trightStreamFlip\t',end='',file=dataFile)
if task=='T1':
    numRespsWanted = 2
dataFile.write('rightResponseFirst\t')
for i in range(numRespsWanted):
   dataFile.write('cueSerialPos'+str(i)+'\t')   #have to use write to avoid ' ' between successive text, at least until Python 3
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
   dataFile.write('responsePosRelative'+str(i)+'\t')
print('seq1\tseq2\t',end='', file=dataFile) #assuming 2 streams
print('timingBlips',file=dataFile)
#end of header

def  oneFrameOfStim( n,cues,cuesSerialPos,seq1,seq2,cueDurFrames,letterDurFrames,ISIframes,thisTrial,textStimuliStream1,textStimuliStream2,
                                       noise,proportnNoise,allFieldCoords,numNoiseDots ): 
#defining a function to draw each frame of stim.
#seq1 is an array of indices corresponding to the appropriate pre-drawn stimulus, contained in textStimuli
  SOAframes = letterDurFrames+ISIframes
  cueFrames = cuesSerialPos*SOAframes
  stimN = int( np.floor(n/SOAframes) )
  frameOfThisLetter = n % SOAframes #every SOAframes, new letter
  showLetter = frameOfThisLetter < letterDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
  thisStimIdx = seq1[stimN] #which letter, from A to Z (1 to 26), should be shown?
  #print ('stimN=',stimN, 'thisStimIdx=', thisStimIdx, ' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes) ) #DEBUGOFF
  if seq2 is not None:
    thisStim2Idx = seq2[stimN]
  #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
  for cue in cues:
    cue.setLineColor( bgColor )
  if type(cueFrames) not in [tuple,list,np.ndarray]: #scalar. But need collection to do loop based on it
    cueFrames = list([cueFrames])
  for i in xrange( len(cueFrames) ): #check whether it's time for any cue. Assume first cueFrame is for first cue, etc.
    thisCueFrame = cueFrames[i]
    if n>=thisCueFrame and n<thisCueFrame+cueDurFrames:
         cues[i].setLineColor( cueColor )

  if showLetter:
    textStimuliStream1[thisStimIdx].setColor( letterColor )
    textStimuliStream2[thisStim2Idx].setColor( letterColor )
  else: 
    textStimuliStream1[thisStimIdx].setColor( bgColor )
    textStimuliStream2[thisStim2Idx].setColor( bgColor )
  textStimuliStream1[thisStimIdx].flipHoriz = thisTrial['leftStreamFlip']
  textStimuliStream2[thisStim2Idx].flipHoriz = thisTrial['rightStreamFlip']
  textStimuliStream1[thisStimIdx].draw()
  textStimuliStream2[thisStim2Idx].draw()
  for cue in cues:
    cue.draw() #will be drawn in backgruond color if it's not time for that
  refreshNoise = False #Not recommended because takes longer than a frame, even to shuffle apparently. Or may be setXYs step
  if proportnNoise>0 and refreshNoise: 
    if frameOfThisLetter ==0: 
        np.random.shuffle(allFieldCoords) 
        dotCoords = allFieldCoords[0:numNoiseDots]
        noise.setXYs(dotCoords)
  if proportnNoise>0:
    noise.draw()
  return True 
# #######End of function definition that displays the stimuli!!!! #####################################
#############################################################################################################################
cues = list()
preCues = list()
for i in xrange(2):
    cue = visual.Circle(myWin, 
                     radius=cueRadius,#Martini used circles with diameter of 12 deg
                     lineColorSpace = 'rgb',
                     lineColor=bgColor,
                     lineWidth=6.0, #in pixels. Was thinner (2 pixels) in letter AB experiments
                     units = 'deg',
                     fillColorSpace = 'rgb',
                     fillColor=None, #beware, with convex shapes fill colors don't work
                     pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
                     interpolate=True,
                     autoLog=False)#this stim changes too much for autologging to be useful
    cues.append(cue)
    
    #Precue to potentially inform the participant where the letter streams will appear
    preCue = visual.Circle(myWin,  
                     radius=2,#Martini used circles with diameter of 12 deg
                     lineColorSpace = 'rgb',
                     lineColor=bgColor,
                     lineWidth=4.0, #in pixels. Was thinner (2 pixels) in letter AB experiments
                     units = 'deg',
                     fillColorSpace = 'rgb',
                     fillColor='white', #beware, with convex shapes fill colors don't work
                     pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
                     interpolate=True,
                     autoLog=False)#this stim changes too much for autologging to be useful
    preCues.append(preCue)

ltrHeight = 2.5 #Martini letters were 2.5deg high
#All noise dot coordinates ultimately in pixels, so can specify each dot is one pixel 
noiseFieldWidthDeg=ltrHeight *1.0
noiseFieldWidthPix = int( round( noiseFieldWidthDeg*pixelperdegree ) )

def timingCheckAndLog(ts,trialN):
    #check for timing problems and log them
    #ts is a list of the times of the clock after each frame
    interframeIntervs = np.diff(ts)*1000
    #print '   interframe intervs were ',around(interframeIntervs,1) #DEBUGOFF
    frameTimeTolerance=.3 #proportion longer than refreshRate that will not count as a miss
    longFrameLimit = np.round(1000/refreshRate*(1.0+frameTimeTolerance),2)
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded 150% of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0 and (not demo):
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                logging.error( 'trialnum='+str(trialN)+' '+longFramesStr )
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:
                            flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    flankingAlso = np.array(flankingAlso)
                    flankingAlso = flankingAlso[np.negative(np.isnan(flankingAlso))]  #remove nan values
                    flankingAlso = flankingAlso.astype(np.integer) #cast as integers, so can use as subscripts
                    logging.info( 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )  ) #because this is not an essential error message, as previous one already indicates error
                      #As INFO, at least it won't fill up the console when console set to WARNING or higher
    return numCasesInterframeLong
    #end timing check
    
trialClock = core.Clock()
numTrialsCorrect = 0; 
numTrialsApproxCorrect = 0;
numTrialsEachCorrect= np.zeros( numRespsWanted )
numTrialsEachApproxCorrect= np.zeros( numRespsWanted )

def do_RSVP_stim(thisTrial, cues, preCues, seq1, seq2, proportnNoise,trialN):
    #relies on global variables:
    #   textStimuli, logging, bgColor
    #  thisTrial should have 'cueSerialPos'
    global framesSaved #because change this variable. Can only change a global variable if you declare it
    cuesSerialPos = [] #will contain the serial positions in the stream of all the cues (corresponding to the targets)
    cuesSerialPos.append(thisTrial['cueSerialPos']) #stream1
    cuesSerialPos.append(thisTrial['cueSerialPos']) #stream2
    cuesSerialPos = np.array(cuesSerialPos)
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #gtenerating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
        (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)

    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I have consistent timing blip first time that draw ringInnerR for phantom contours
    for cue in cues:
        cue.setLineColor(bgColor)
        preDrawStimToGreasePipeline.extend([cue])
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    myWin.flip(); myWin.flip()
    #end preparation of stimuli
    
    core.wait(.1);
    trialClock.reset()
    fixatnPeriodMin = 0.3
    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+fixatnPeriodMin)   *refreshRate)  #random interval between 800ms and 1.3s
    ts = list(); #to store time of each drawing, to check whether skipped frames
    for i in range(fixatnPeriodFrames+20):  #prestim fixation interval
        #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
        #      fixation.draw()
        #else: fixationBlank.draw()
        for preCue in preCues:
            preCue.draw()
        fixationPoint.draw()
        myWin.flip()  #end fixation interval
    #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
    t0 = trialClock.getTime()

    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
        worked = oneFrameOfStim( n,cues,cuesSerialPos,seq1,seq2,cueDurFrames,letterDurFrames,ISIframes,thisTrial,textStimuliStream1,textStimuliStream2,
                                                     noise,proportnNoise,allFieldCoords,numNoiseDots ) #draw letter and possibly cue and noise on top
        if thisTrial['wordEccentricity'] > 2:  #kludge to avoid drawing fixation in super-near condition for Cheryl
            fixationPoint.draw()
        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1
        myWin.flip()
        t=trialClock.getTime()-t0;  ts.append(t);
    #end of big stimulus loop
    myWin.setRecordFrameIntervals(False);

    if task=='T1':
        respPromptStim.setText('What was circled?',log=False)   
    else: respPromptStim.setText('Error: unexpected task',log=False)
    postCueNumBlobsAway=-999 #doesn't apply to non-tracking and click tracking task
    #print('cuesSerialPos=',cuesSerialPos, 'cuesSerialPos.dtype =',cuesSerialPos.dtype, 'type(seq1)=',type(seq1))
    seq1 = np.array(seq1) #convert seq1 list to array so that can index it with multiple indices (cuesSerialPos)
    #print('seq1[cuesSerialPos]=', seq1[cuesSerialPos])
    seq2= np.array(seq2) #convert seq2 list to array so that can index it with multiple indices (cuesSerialPos)
    correctAnswerIdxsStream1 = np.array(    seq1[cuesSerialPos]    )
    correctAnswerIdxsStream2 = np.array(    seq2[cuesSerialPos]    )
    #print('correctAnswerIdxsStream1=',correctAnswerIdxsStream1)#, 'wordList[correctAnswerIdxsStream1[0]]=',wordList[correctAnswerIdxsStream1[0]])
    return cuesSerialPos,correctAnswerIdxsStream1,correctAnswerIdxsStream2,ts
    
def handleAndScoreResponse(passThisTrial,response,responseAutopilot,task,stimSequence,cueSerialPos,correctAnswerIdx):
    #Handle response, calculate whether correct, ########################################
    #responses are actual characters
    #correctAnswer is index into stimSequence
    #autopilot is global variable
    if autopilot or passThisTrial:
        response = responseAutopilot
    #print('handleAndScoreResponse correctAnswerIdxs=',correctAnswerIdxs,'\nstimSequence=',stimSequence, '\nwords=',wordList)
    correct = 0
    approxCorrect = 0
    posOfResponse = -999
    responsePosRelative = -999
    idx = correctAnswerIdx
    print('correctAnswerIdx = ',correctAnswerIdx) 
    correctAnswer = wordList[idx].upper()
    responseString=response
    responseString= responseString.upper()
    #print('correctAnswer=',correctAnswer ,' responseString=',responseString)
    if correctAnswer == responseString:
        correct = 1
    #print('correct=',correct)
    responseMustBeInWordList = True
    if len(stimSequence) != len(wordList):
        responseMustBeInWordList = False
    #stimSeqAsLetters = list()
    #for letter in stimSequence:
    #    stimSeqAsLetters.append(  chr( ord('A') + letter ) )
    #letterIdxOfAlphabet = ord(  responseString.upper() ) - ord( 'A')  
    #print("Sending to responseWordIdx stimSequence=",stimSequence," responseString=",responseString, "stimSeqAsLetters=",stimSeqAsLetters, "responseMustBeInWordList=",responseMustBeInWordList)
    responseWordIdx = wordToIdx(responseString.upper(),wordList, responseMustBeInWordList)
    print('responseWordIdx = ', responseWordIdx, ' stimSequence=', stimSequence)
    if responseWordIdx is None: #response is not in the wordList
        posOfResponse = -999
        logging.warn('Response was not present in the stimulus stream')
    else:
        posOfResponse= np.where( np.array(stimSequence)==responseWordIdx ) #Assumes that the response was in the stimulus sequence
        print("posOfResponse=",posOfResponse, "responseWordIdx=",responseWordIdx,"stimSequence=",stimSequence, "type(stimSequence)=",type(stimSequence))
        posOfResponse= posOfResponse[0] #list with two entries, want first which will be array of places where the response was found in the sequence
        if len(posOfResponse) > 1:
            logging.error('Expected response to have occurred in only one position in stream')
        elif len(posOfResponse) == 0:
            logging.error('Expected response to have occurred somewhere in the stream')
            raise ValueError('Expected response to have occurred somewhere in the stream')
        else:
            posOfResponse = posOfResponse[0] #first element of list (should be only one element long 
        responsePosRelative = posOfResponse - cueSerialPos
        approxCorrect = abs(responsePosRelative)<= 3 #Vul efficacy measure of getting it right to within plus/minus
    #print('wordToIdx(',responseString,',',wordList,')=',responseWordIdx,' stimSequence=',stimSequence,'\nposOfResponse = ',posOfResponse) #debugON
    #print response stuff to dataFile
    print('correctAnswer=',correctAnswer,' correct=',correct, 'responsePosRelative=',responsePosRelative)
    #header was answerPos0, answer0, response0, correct0, responsePosRelative0
    print(cueSerialPos,'\t', end='', file=dataFile)
    print(correctAnswer, '\t', end='', file=dataFile) #answer0
    print(responseString, '\t', end='', file=dataFile) #response0
    print(correct, '\t', end='',file=dataFile)   #correct0
    print(responsePosRelative, '\t', end='',file=dataFile) #responsePosRelative0

    return correct,approxCorrect,responsePosRelative
    #end handleAndScoreResponses

def play_high_tone_correct_low_incorrect(correct, passThisTrial=False):
    highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3, bits=8)
    low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3, bits=8)
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
        for i in range(2): 
            high.play();  low.play(); 
    else: #incorrect
        low.play()

def instructions():
    instrcolor = 'white'
    preInstructions = visual.TextStim(myWin, text = "Press a key to see the instructions",pos=(0, 0),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions1 = visual.TextStim(myWin, text = "Instructions",pos=(0, .8),colorSpace='rgb',color=(0,0,0),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions2 = visual.TextStim(myWin, text = "Please rest your eyes on the red dot at all times",pos=(0, -.2),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions3 = visual.TextStim(myWin, text = "Press Space to Continue",pos=(0, -.9), colorSpace='rgb',color=(0,0,0),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions4b = visual.TextStim(myWin, text = "On each trial, two letter streams will be presented with each letter flashing for a fraction of a second.",pos=(0, 0),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions5b = visual.TextStim(myWin, text = "Two letters will be targeted with white circle on each trial. Try to remember these letters.",pos=(0, 0),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )        
    Instructions6 = visual.TextStim(myWin, text = "After the letter streams, you will need to select the letters you just saw by clicking the letter on the screen. \nSome of the trials will require you to choose the left letter first \nOthers will require you to choose the right one first.", pos=(0,0), colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions7 = visual.TextStim(myWin, text = "Press a key to begin the experiment",pos=(0, 0), colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions9 = visual.TextStim(myWin, text = "If you have any questions, ask the experimentor now.",pos=(0, 0),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )
    Instructions10 = visual.TextStim(myWin, text = "If you don't know the letter, you can guess.",pos=(0, 0),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging )

    preInstructions.draw()
    myWin.flip()
    event.waitKeys()
    Instructions1.draw()
    Instructions2.draw()
    Instructions3.draw()
    fixationPoint.draw()
    myWin.flip()
    event.waitKeys()
    Instructions1.draw()
    Instructions4b.draw()
    Instructions3.draw()
    myWin.flip()
    event.waitKeys()
    Instructions1.draw()
    Instructions5b.draw()
    Instructions3.draw()
    myWin.flip()
    event.waitKeys()
    Instructions1.draw()
    Instructions6.draw()
    Instructions3.draw()
    myWin.flip()
    event.waitKeys()
    Instructions1.draw()
    Instructions3.draw()
    Instructions10.draw()
    myWin.flip()
    event.waitKeys()
    Instructions1.draw()
    Instructions9.draw()
    Instructions3.draw()
    myWin.flip()
    event.waitKeys()
    Instructions7.draw()
    myWin.flip()
    event.waitKeys()

changeToUpper = False #Chery's experiment
expStop=False
nDoneMain = -1 #change to zero once start main part of experiment
if doStaircase:
    #create the staircase handler
    useQuest = True
    if  useQuest:
        staircase = data.QuestHandler(startVal = 95, 
                              startValSd = 80,
                              stopInterval= 1, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                              nTrials = staircaseTrials,
                              #extraInfo = thisInfo,
                              pThreshold = threshCriterion, #0.25,    
                              gamma = 1./26,
                              delta=0.02, #lapse rate, I suppose for Weibull function fit
                              method = 'quantile', #uses the median of the posterior as the final answer
                              stepType = 'log',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                              minVal=1, maxVal = 100
                              )
        print('created QUEST staircase')
    else:
        stepSizesLinear = [.2,.2,.1,.1,.05,.05]
        stepSizesLog = [log(1.4,10),log(1.4,10),log(1.3,10),log(1.3,10),log(1.2,10)]
        staircase = data.StairHandler(startVal = 0.1,
                                  stepType = 'log', #if log, what do I want to multiply it by
                                  stepSizes = stepSizesLog,    #step size to use after each reversal
                                  minVal=0, maxVal=1,
                                  nUp=1, nDown=3,  #will home in on the 80% threshold
                                  nReversals = 2, #The staircase terminates when nTrials have been exceeded, or when both nReversals and nTrials have been exceeded
                                  nTrials=1)
        print('created conventional staircase')
        
    if prefaceStaircaseTrialsN > len(prefaceStaircaseNoise): #repeat array to accommodate desired number of easyStarterTrials
        prefaceStaircaseNoise = np.tile( prefaceStaircaseNoise, ceil( prefaceStaircaseTrialsN/len(prefaceStaircaseNoise) ) )
    prefaceStaircaseNoise = prefaceStaircaseNoise[0:prefaceStaircaseTrialsN]
    
    phasesMsg = ('Doing '+str(prefaceStaircaseTrialsN)+'trials with noisePercent= '+str(prefaceStaircaseNoise)+' then doing a max '+str(staircaseTrials)+'-trial staircase')
    print(phasesMsg); logging.info(phasesMsg)

    #staircaseStarterNoise PHASE OF EXPERIMENT
    corrEachTrial = list() #only needed for easyStaircaseStarterNoise
    staircaseTrialN = -1; mainStaircaseGoing = False
    while (not staircase.finished) and expStop==False: #staircase.thisTrialN < staircase.nTrials
        if staircaseTrialN+1 < len(prefaceStaircaseNoise): #still doing easyStaircaseStarterNoise
            staircaseTrialN += 1
            noisePercent = prefaceStaircaseNoise[staircaseTrialN]
        else:
            if staircaseTrialN+1 == len(prefaceStaircaseNoise): #add these non-staircase trials so QUEST knows about them
                mainStaircaseGoing = True
                print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise)
                staircase.importData(100-prefaceStaircaseNoise, np.array(corrEachTrial))
                printStaircase(staircase, descendingPsycho, briefTrialUpdate=False, printInternalVal=True, alsoLog=False)
            try: #advance the staircase
                printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
                noisePercent = 100. - staircase.next()  #will step through the staircase, based on whether told it (addResponse) got it right or wrong
                staircaseTrialN += 1
            except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
                print('stopping because staircase.next() returned a StopIteration, which it does when it is finished')
                break #break out of the trials loop
        #print('staircaseTrialN=',staircaseTrialN)
        idxsStream1, idxsStream2, cues, preCues = calcAndPredrawStimuli(wordList,cues,preCues, staircaseTrials)
        cuesSerialPos,correctAnswerIdxsStream1,correctAnswerIdxsStream2, ts  = \
                                        do_RSVP_stim(thisTrial, cues, preCues, idxsStream1, idxsStream2, noisePercent/100.,staircaseTrialN)
        numCasesInterframeLong = timingCheckAndLog(ts,staircaseTrialN)
        expStop,passThisTrial,responses,buttons,responsesAutopilot = \
                letterLineupResponse.doLineup(myWin,bgColor,myMouse,clickSound,badKeySound,possibleResps,showBothSides,sideFirstLeftRightCentral,autopilot) #CAN'T YET HANDLE MORE THAN 2 LINEUPS

        if not expStop:
            if mainStaircaseGoing:
                print('staircase\t', end='', file=dataFile)
            else: 
                print('staircase_preface\t', end='', file=dataFile)
             #header start      'trialnum\tsubject\ttask\t'
            print(staircaseTrialN,'\t', end='', file=dataFile) #first thing printed on each line of dataFile
            print(subject,'\t',task,'\t', round(noisePercent,2),'\t', end='', file=dataFile)
            correct,approxCorrect,responsePosRelative= handleAndScoreResponse(
                                                passThisTrial,responses,responseAutopilot,task,sequenceLeft,cuesSerialPos[0],correctAnswerIdx )
            #header then had seq1, seq2
            print(idxsStream1,'\t',idxsStream2,'\t', end='', file=dataFile) #print the indexes into the wordList
            print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
            core.wait(.06)
            if feedback: 
                play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
            print('staircaseTrialN=', staircaseTrialN,' noisePercent=',round(noisePercent,3),' T1approxCorrect=',T1approxCorrect) #debugON
            corrEachTrial.append(T1approxCorrect)
            if mainStaircaseGoing: 
                staircase.addResponse(T1approxCorrect, intensity = 100-noisePercent) #Add a 1 or 0 to signify a correct/detected or incorrect/missed trial
                #print('Have added an intensity of','{:.3f}'.format(100-noisePercent), 'T1approxCorrect =', T1approxCorrect, ' to staircase') #debugON
    #ENDING STAIRCASE PHASE

    if staircaseTrialN+1 < len(prefaceStaircaseNoise) and (staircaseTrialN>=0): #exp stopped before got through staircase preface trials, so haven't imported yet
        print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise[0:staircaseTrialN+1])
        staircase.importData(100-prefaceStaircaseNoise[0:staircaseTrialN], np.array(corrEachTrial)) 
    print('framesSaved after staircase=',framesSaved) #debugON

    timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
    msg = ('prefaceStaircase phase' if expStop else '')
    msg += ('ABORTED' if expStop else 'Finished') + ' staircase part of experiment at ' + timeAndDateStr
    logging.info(msg); print(msg)
    printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
    #print('staircase.quantile=',round(staircase.quantile(),2),' sd=',round(staircase.sd(),2))
    threshNoise = round(staircase.quantile(),3)
    if descendingPsycho:
        threshNoise = 100- threshNoise
    threshNoise = max( 0, threshNoise ) #e.g. ff get all trials wrong, posterior peaks at a very negative number
    msg= 'Staircase estimate of threshold = ' + str(threshNoise) + ' with sd=' + str(round(staircase.sd(),2))
    logging.info(msg); print(msg)
    myWin.close()
    #Fit and plot data
    fit = None
    try:
        intensityForCurveFitting = staircase.intensities
        if descendingPsycho: 
            intensityForCurveFitting = 100-staircase.intensities #because fitWeibull assumes curve is ascending
        fit = data.FitWeibull(intensityForCurveFitting, staircase.data, expectedMin=1/26., sems = 1.0/len(staircase.intensities))
    except:
        print("Fit failed.")
    plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshCriterion)
    #save figure to file
    pylab.savefig(fileName+'.pdf')
    print('The plot has been saved, as '+fileName+'.pdf')
    pylab.show() #must call this to actually show plot
else: #not staircase
    noisePercent = defaultNoiseLevel
    phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials. Letters will be drawn with superposed noise of ' + "{:.2%}".format(defaultNoiseLevel)
    print(phasesMsg); logging.info(phasesMsg)
    nDoneMain =0
    while nDoneMain < trials.nTotal and expStop==False: #MAIN EXPERIMENT LOOP
        if nDoneMain==0:
            msg='Starting main (non-staircase) part of experiment'
            logging.info(msg); print(msg)
            instructions()
        thisTrial = trials.next() #get a proper (non-staircase) trial
        sequenceStream1, sequenceStream2, cues, preCues = calcAndPredrawStimuli(wordList,cues,preCues, thisTrial)
        print('sequenceStream1=',sequenceStream1)
        print('sequenceStream2=',sequenceStream2)
        myWin.setMouseVisible(False)
        cuesSerialPos,correctAnswerIdxsStream1,correctAnswerIdxsStream2, ts  = \
                                                                    do_RSVP_stim(thisTrial, cues, preCues, sequenceStream1, sequenceStream2, noisePercent/100.,nDoneMain)
        print('correctAnswerIdxsStream1=',correctAnswerIdxsStream1,'correctAnswerIdxsStream2=',correctAnswerIdxsStream2)
        numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)
        #call for each response
        myMouse = event.Mouse()
        alphabet = list(string.ascii_lowercase)
        possibleResps = alphabet #possibleResps.remove('C'); possibleResps.remove('V')

        expStop = list(); passThisTrial = list(); responses=list(); responsesAutopilot=list()
        dL = [None]*numRespsWanted #dummy list for null values
        expStop = copy.deepcopy(dL); responses = copy.deepcopy(dL); responsesAutopilot = copy.deepcopy(dL); passThisTrial=copy.deepcopy(dL)
        responseOrder = range(numRespsWanted)
        showBothSides=True
        sideFirstLeftRightCentral = thisTrial['rightResponseFirst']
        #if thisTrial['rightResponseFirst']: #change order of indices depending on rightResponseFirst. response0, answer0 etc refer to which one had to be reported first
                #responseOrder.reverse()  #this is necessary if using text input rather than lineup response
                
        expStop,passThisTrial,responses,buttons,responsesAutopilot = \
              letterLineupResponse.doLineup(myWin,bgColor,myMouse,clickSound,badKeySound,possibleResps,showBothSides,sideFirstLeftRightCentral,autopilot) #CAN'T YET HANDLE MORE THAN 2 LINEUPS
        expStop = np.array(expStop).any(); passThisTrial = np.array(passThisTrial).any()
        if not expStop:
            print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile to indicate main part of experiment, not staircase
            print(nDoneMain,'\t', end='', file=dataFile)
            print(subject,'\t',task,'\t', round(noisePercent,3),'\t', end='', file=dataFile)
            print(thisTrial['leftStreamFlip'],'\t', end='', file=dataFile)
            print(thisTrial['rightStreamFlip'],'\t', end='', file=dataFile)
            print(thisTrial['rightResponseFirst'],'\t', end='', file=dataFile)
            i = 0
            eachCorrect = np.ones(numRespsWanted)*-999; eachApproxCorrect = np.ones(numRespsWanted)*-999
            for i in range(numRespsWanted): #scored and printed to dataFile in left first, right second order even if collected in different order
                if thisTrial['rightResponseFirst']:
                    if i==0:
                        sequenceStream = sequenceStream2; correctAnswerIdxs = correctAnswerIdxsStream2; 
                    else: sequenceStream = sequenceStream1; correctAnswerIdxs = correctAnswerIdxsStream1; 
                else: 
                    if i==0:
                        sequenceStream = sequenceStream1; correctAnswerIdxs = correctAnswerIdxsStream1; 
                    else: sequenceStream = sequenceStream2; correctAnswerIdxs = correctAnswerIdxsStream2; 
                correct,approxCorrect,responsePosRelative = (
                handleAndScoreResponse(passThisTrial,responses[i],responsesAutopilot,task,sequenceStream,thisTrial['cueSerialPos'],correctAnswerIdxs[i] ) )
                eachCorrect[i] = correct
                eachApproxCorrect[i] = approxCorrect
            #header then had seq1, seq2. Save them
            print(sequenceStream1,'\t',sequenceStream2,'\t', end='', file=dataFile) #print the indexes into the wordList
            print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
            print('correct=',correct,' approxCorrect=',approxCorrect,' eachCorrect=',eachCorrect, ' responsePosRelative=', responsePosRelative)
            numTrialsCorrect += eachCorrect.all() #so count -1 as 0
            numTrialsApproxCorrect += eachApproxCorrect.all()
            numTrialsEachCorrect += eachCorrect #list numRespsWanted long
            numTrialsEachApproxCorrect += eachApproxCorrect #list numRespsWanted long
                
            if(sum(eachCorrect)==2):
                allCorrect=True
            else:
                allCorrect=False
            
            if exportImages:  #catches one frame of response
                 myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
                 framesSaved +=1; core.wait(.1)
                 myWin.saveMovieFrames('images_sounds_movies/frames.png') #mov not currently supported 
                 expStop=True
            core.wait(.1)
            if feedback: play_high_tone_correct_low_incorrect(allCorrect, passThisTrial=False)
            nDoneMain+=1
            
            dataFile.flush(); logging.flush()
            print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal) #' trials.thisN=',trials.thisN
            if (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
                 ( trials.nTotal*pctCompletedBreak/100. ) ==1):  #dont modulus 0 because then will do it for last trial
                    nextText.setText('Press "SPACE" to continue!')
                    nextText.draw()
                    progressMsg = 'Completed ' + str(nDoneMain) + ' of ' + str(trials.nTotal) + ' trials'
                    NextRemindCountText.setText(progressMsg)
                    NextRemindCountText.draw()
                    myWin.flip() # myWin.flip(clearBuffer=True) 
                    waiting=True
                    while waiting:
                       if autopilot: break
                       elif expStop == True:break
                       for key in event.getKeys():      #check if pressed abort-type key
                             if key in ['space','ESCAPE']: 
                                waiting=False
                             if key in ['ESCAPE']:
                                expStop = True
                    myWin.clearBuffer()
            core.wait(.2); time.sleep(.2)
        #end main trials loop
timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
msg = 'Finishing at '+timeAndDateStr
print(msg); logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.error(msg)

if not doStaircase and (nDoneMain >0):
    msg = 'Of ' + str(nDoneMain)+' trials, on '+str(numTrialsCorrect*1.0/nDoneMain*100.)+'% of all trials all targets reported exactly correct'
    print(msg); logging.info(msg)
    msg= 'All targets approximately correct in '+ str( round(numTrialsApproxCorrect*1.0/nDoneMain*100,1)) + '% of trials'
    print(msg); logging.info(msg)
    for i in range(numRespsWanted):
        msg = 'stream'+str(i)+': '+str( round(numTrialsEachCorrect[i]*1.0/nDoneMain*100.,2) ) + '% correct'
        print(msg); logging.info(msg)
        msg = 'stream' + str(i) + ': '+ str( round(numTrialsEachApproxCorrect[i]*1.0/nDoneMain*100,2) ) +'% approximately correct'
        print(msg); logging.info(msg)

logging.flush(); dataFile.close()
myWin.close() #have to close window if want to show a plot
if quitFinder:
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)