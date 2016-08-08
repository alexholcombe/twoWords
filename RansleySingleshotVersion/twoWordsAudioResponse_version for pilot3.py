#Alex Holcombe alex.holcombe@sydney.edu.au
#See the github repository for more information: https://github.com/alexholcombe/twoWords
from __future__ import print_function, division
from psychopy import monitors, visual, event, data, logging, core, sound, gui, microphone
from matplotlib import pyplot
import psychopy.info
import scipy
import numpy as np
from math import atan, log, ceil
import copy
import time, sys, os #, pylab
try:
    from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
except ImportError:
    print('Could not import from noiseStaircaseHelpers.py (you need that file to be in the same directory)')
try:
    import stringResponse
except ImportError:
    print('Could not import stringResponse.py (you need that file to be in the same directory)')
try:
    import recordVocalResponseKRedit
except ImportError:
    print('Could not import recordVocalResponse.py (you need that file to be in the same directory)')

# test speeds:  17,35,50,66,84,99,115,130 
wordDur1 = 17 #Fast 35
wordDur2 = 17 #Slow 50

#Setting up vocal response parameters
responseMode = 'voice'
buffer = 128  # smaller = short play latency, but higher chance of choppy sound playback
rate = 48000  # needs to be 40000 or higher.  Changing this doesn't seem to work.
sound.init(buffer=buffer, rate=rate)
autoLogging=False
logging.console.setLevel(logging.EXP) #DEBUG means set the console to receive nearly all messges, INFO is for everything else, INFO, EXP, DATA, WARNING and ERROR 

# initial set up:
dataPath='dataRaw'
if os.path.isdir('dataRaw'):
    if os.path.isdir(dataPath+os.sep+'recordings'):
        recordingPath = dataPath + os.sep + 'recordings'
    else:
        print ('No "recordings" dir exists, so saving data in dataRaw')
        recordingPath = dataPath
else:
    print (dataPath,' directory does not exist, so saving data and recordings in present working directory')
    dataPath='.'
    recordingPath='.'
#
    
#switchOn doesn't do much, but takes up to several seconds.
#Supposed to be able to set the sampling rate 
# Set up microphone, must be 16000 or 8000 Hz for speech recognition
desiredSampleRate=16000
microphone.switchOn(sampleRate=desiredSampleRate)
sampleRate = sound.pyoSndServer.getSamplingRate()
if (round(sampleRate)==round(desiredSampleRate)):
    print ('Successfully set sample rate to ',sampleRate)
else:
    print ('Attempted to set sampleRate to = ', desiredSampleRate, ' but is now reported as ', sampleRate, '. Alex hasnt found a way to fix this but it just means you cant use speech recognition')
mic = microphone.AdvAudioCapture() #Initialise class to get ready for recording with automatic markerTone to assess timing

markerToneDur = 0.05
markerToneVol = .4 # 0.03 works fine and is inaudible
markerFreq = 19000 #19000
mic.setMarker(tone=markerFreq, secs=markerToneDur, volume= markerToneVol)
(hz,duration,volume) = mic.getMarkerInfo()
print ("According to mic, the marker hz=",hz," duration=",duration," volume=",volume)

units='deg '   
wordEccentricity=  0.3 #4
tasks=['T1']; task = tasks[0]
#THINGS THAT COULD PREVENT SUCCESS ON A STRANGE MACHINE
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix
quitFinder = False #if checkRefreshEtc, quitFinder becomes True
autopilot=False
demo=False #False
exportImages= False #quits after one trial
subject='PX' #user is prompted to enter true subject name
if autopilot: subject='auto'
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=True 
autoLogging=False
if demo:
    refreshRate = 60.;  #100

numWordsInStream = 1

staircaseTrials = 25
prefaceStaircaseTrialsN = 20 #22
prefaceStaircaseNoise = np.array([5,20,20,20, 50,50,50,5,80,80,80,5,95,95,95]) #will be recycled / not all used, as needed
threshCriterion = 0.58

bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [-.7,-.7,-.7] #originally [1.,1.,1.]
letterColor = [1,1,1] #[1.,1.,1.]
cueRadius = 6 #6 deg in Goodbourn & Holcombe
widthPix= 1600 #1920 #monitor width in pixels of Agosta  [1280]
heightPix= 900 #1080 #800 #monitor height in pixels [800]
monitorwidth = 52.5 #38.7 #monitor width in cm [was 38.7]
scrn=1 
#0 to use main screen, 1 to use external screen connected to computer #for some reason this works when it is the other way around. 
fullscr=False #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 600; heightPix = 600
    monitorwidth = 13.0
    fullscr=False; scrn=1
    framesSaved=0
if demo:    
    scrn=1; fullscr=False
    widthPix = 800; heightPix = 600
    monitorname='EIZO'
    allowGUI = True
viewdist = 57 #50. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
print('pixelperdegree=',pixelperdegree)

ltrHeight =  0.7 #0.9 #0.4 #2.5 #Martini letters were 2.5deg high



# create a dialog from dictionary 
infoFirst = { 'Do staircase (only)': False, 'Check refresh etc':True, 'Fullscreen (timing errors if not)': fullscr,
                'Screen refresh rate': 60 }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='AB experiment OR staircase to find thresh noise level for T1 performance criterion', 
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

monitorname = 'EIZO'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    #assumes widthPix, heightPix, allowGUI exists, bgColor, fullscr, scrn,waitBlank
    print("Trying to open window of size=",widthPix," , ",heightPix)
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    print("Opened window,",myWin," of size ",myWin.size)
    return myWin
myWin = openMyStimWindow()
#identify the hardware microphone in use:
circle = visual.Circle(myWin, 5, fillColor='grey', lineColor='grey', lineColorSpace='rgb', fillColorSpace='rgb', edges=64, autoLog=autoLogging)
names, idx = sound.pyo.pa_get_input_devices()
inp = sound.pyo.pa_get_default_input()
msg = 'Ensure speaker vol > 0\n\nAny key to start...\n\nUsing input="%s"' % names[idx.index(inp)]
startMessage = visual.TextStim(myWin, msg, color=letterColor, colorSpace='rgb', height=ltrHeight, autoLog=autoLogging)
circle.draw()
startMessage.draw()
myWin.flip()
if 'escape' in event.waitKeys():
  print("User quit during sound setup, via ESCAPE")
  core.quit()

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
    myWin.allowGUI =True

### 

myWin.close() #have to close window to show dialog box

group = '1' #to use if no staircase, can be set by user
trialsPerCondition = 1 #default value
dlgLabelsOrdered = list()
if doStaircase:
    myDlg = gui.Dlg(title="Staircase to find appropriate noisePercent", pos=(200,400))
else: 
    myDlg = gui.Dlg(title="RSVP experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name (default="PX"):', 'PX', tip='or subject code')
    dlgLabelsOrdered.append('subject')
if doStaircase:
    prefaceStaircaseTrialsN = 5
    easyTrialsCondText = 'Num preassigned noise trials to preface staircase with (default=' + str(prefaceStaircaseTrialsN) + '):'
    myDlg.addField(easyTrialsCondText, tip=str(prefaceStaircaseTrialsN))
    dlgLabelsOrdered.append('easyTrials')
    myDlg.addField('Staircase trials (default=' + str(staircaseTrials) + '):', tip="Staircase will run until this number is reached or it thinks it has precise estimate of threshold")
    dlgLabelsOrdered.append('staircaseTrials')
    pctCompletedBreak = 101
else:
    myDlg.addField('\tParticipant Group',  group, tip=str(group))
    dlgLabelsOrdered.append('group')
    myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
    dlgLabelsOrdered.append('trialsPerCondition')
    pctCompletedBreak = 55
    
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)

if checkRefreshEtc and (not demo) and (myWin.size != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.error(msgWrongResolution)
    print(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen', color=[-1.,1.,-1.]) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()

if myDlg.OK: #unpack information from dialogue box
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
       group = thisInfo[dlgLabelsOrdered.index('group')]
       trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
       print('trialsPerCondition=',trialsPerCondition)
       logging.info('trialsPerCondition =',trialsPerCondition)
       defaultNoiseLevel = 0 #int (thisInfo[ dlgLabelsOrdered.index('defaultNoiseLevel') ])
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()
if not demo: 
    allowGUI = False
print(group)

test = '0'

speedSeq = ['slow','fast','slow','fast']

if (group=='1'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['1','3','5','7']

if (group=='2'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['3','5','7','1']

if (group=='3'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['5','7','1','3']

if (group=='4'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['7','1','3','5']
    
if (group=='5'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['2','4','6','8']

if (group=='6'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['4','6','8','2']

if (group=='7'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['6','8','2','4']

if (group=='8'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['8','2','4','6']

if (group=='9'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['1','3','5','7']

if (group=='10'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['3','5','7','1']

if (group=='11'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['5','7','1','3']

if (group=='12'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['7','1','3','5']
    
if (group=='13'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['2','4','6','8']

if (group=='14'):
    conditionSeq = ['long','long','short','short']
    whichWordsSeq = ['4','6','8','2']

if (group=='15'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['6','8','2','4']

if (group=='16'):
    conditionSeq = ['short','short','long','long']
    whichWordsSeq = ['8','2','4','6']

for counter in range(4):
    condition = conditionSeq[counter]
    whichWords = whichWordsSeq[counter]
    speed = speedSeq[counter]
    

    #condition = 'long'
    #whichWords = '1'
    
    #speed = 'slow'
    
    if (condition == 'short'):
        rec_duration =  2
    else:
        rec_duration =  4
        
    if (whichWords == '1'):
            wordFile1 = "W1.txt"
            wordFile2 = "W2.txt"
            targetFile = "TargetList1.txt"
    if (whichWords == '2'):
            wordFile1 = "W2.txt"
            wordFile2 = "W1.txt"
            targetFile = "TargetList2.txt"
    if (whichWords == '3'):
            wordFile1 = "W3.txt"
            wordFile2 = "W4.txt"
            targetFile = "TargetList3.txt"
    if (whichWords == '4'):
            wordFile1 = "W4.txt"
            wordFile2 = "W3.txt"
            targetFile = "TargetList4.txt"            
    if (whichWords == '5'):
            wordFile1 = "W5.txt"
            wordFile2 = "W6.txt"
            targetFile = "TargetList5.txt"
    if (whichWords == '6'):
            wordFile1 = "W6.txt"
            wordFile2 = "W5.txt"
            targetFile = "TargetList6.txt"            
    if (whichWords == '7'):
            wordFile1 = "W7.txt"
            wordFile2 = "W8.txt"
            targetFile = "TargetList7.txt"
    if (whichWords == '8'):
            wordFile1 = "W8.txt"
            wordFile2 = "W7.txt"
            targetFile = "TargetList8.txt"

    if (test!='0'):
        condition = 'short'
        rec_duration =  1.8
        wordFile1 = "test" + test + ".txt"
        wordFile2 = "test" + test + "b.txt"
        targetFile = "TestTargets" + test +".txt"
    print(wordFile1)
    
    # reads word in from external source
    wordList1 = open(wordFile1)
    wordList2 = open(wordFile2)
    TargetList = open(targetFile)
    wordList1 = [x.rstrip() for x in wordList1.readlines()]
    wordList2 = [x.rstrip() for x in wordList2.readlines()]
    TargetList = [x.rstrip() for x in TargetList.readlines()]
    lettersUnparsed = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z".upper()
    
    for i in range(len(wordList1)):
        wordList1[i] = wordList1[i].replace(" ", "") #delete spaces
    
    for i in range(len(wordList2)):
        wordList2[i] = wordList2[i].replace(" ", "") #delete spaces
    

    for i in range(len(TargetList)):
        TargetList[i] = TargetList[i].replace(" ", "") #delete spaces

    
    if (test=='0'):
        if (speed == 'fast'):
            #wordList1 = wordList1[0:int((len(wordList1)/2))]
            #wordList2 = wordList2[0:int((len(wordList2)/2))]
            #TargetList = TargetList[0:int((len(TargetList)/2))]
            #print(wordList1)
            #print(len(wordList1))
            wordDur = wordDur1
        elif (speed == 'slow'):
            #wordList1 = wordList1[int((len(wordList1)/2)):len(wordList1)]
            #wordList2 = wordList2[int((len(wordList2)/2)):len(wordList2)]
            #TargetList = TargetList[int((len(TargetList)/2)):len(TargetList)]
            wordDur = wordDur2


#####shuffles wordlist for each participant.
    print(wordList1)
    print(wordList2)
    print(TargetList)
    print(len(wordList1))
    print(len(TargetList))
    tl = np.column_stack((wordList1, wordList2,TargetList))
    np.random.shuffle(tl[10:,:])
    print(tl)
    wordList1 = tl[:,0]
    wordList2 = tl[:,1]
    TargetList = tl[:,2]
    print(wordList1)
    print(wordList2)
    print(TargetList)

    
    #set location of stimuli
    #letter size 2.5 deg
    SOAms = wordDur #Battelli, Agosta, Goodbourn, Holcombe mostly using 133   #KR: was 233
    #Minimum SOAms should be 84  because any shorter, I can't always notice the second ring when lag1.   71 in Martini E2 and E1b (actually he used 66.6 but that's because he had a crazy refresh rate of 90 Hz)
    letterDurMs =  wordDur #85
    #Was 17. 23.6  in Martini E2 and E1b (actually he used 22.2 but that's because he had a crazy refresh rate of 90 Hz = 0
    ISIms = SOAms - letterDurMs
    letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
    cueDurFrames = letterDurFrames
    ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
    #have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
    rateInfo = 'total SOA=' + str(round(  (ISIframes + letterDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + letterDurFrames) + ' frames, comprising\n'
    rateInfo+=  'ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and letterDurFrames ='+str(letterDurFrames)+' or '+str(round( letterDurFrames*(1000./refreshRate), 2))+'ms'
    logging.info(rateInfo); print(rateInfo)
    
    trialDurFrames = int( numWordsInStream*(ISIframes+letterDurFrames) ) #trial duration in frames
    
    onsets = []; offsets = []; inferredOnsets = []
    #rec_duration =  3.8 #1.8 for short #2.8 for both #3.8 for long
    stimClock = core.Clock()
    durs=list()


    if counter== 0:
        myWin = openMyStimWindow()
        
    #set up output data file, log file,  copy of program code, and logging
    infix = ''
    if doStaircase:
        infix = 'staircase_'
    fileName = subject + '_' + infix+ timeAndDateStr+ '_' + str(counter)
    fileNameWithPath = os.path.join(dataPath, fileName)
    if not demo and not exportImages:
        dataFile = open(fileNameWithPath+'.txt', 'w')
        saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileNameWithPath + '.py'
        os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
        logFname = fileNameWithPath+'.log'
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
    
    
    
    textStimuliStream1 = list()
    textStimuliStream2 = list() #used for second, simultaneous RSVP stream
    def calcAndPredrawStimuli(wordList1,wordList2,nDoneMain):
        global textStimuliStream1, textStimuliStream2
        del textStimuliStream1[:]
        del textStimuliStream2[:]
        if len(wordList1) < numWordsInStream:
            print('Error! Your word list must have at least ',numWordsInStream,'strings')
        #for i in (0): #draw the words that will be used on this trial, the first numWordsInStream of the shuffled list
        word1 = wordList1[ nDoneMain ]#     #[ idxsIntoWordList[i] ]
        word2 = wordList2[ nDoneMain ]
        textStimulusStream1 = visual.TextStim(myWin,text=word1,height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='right',alignVert='center',units='deg',font='Arial',autoLog=autoLogging)
        textStimulusStream2 = visual.TextStim(myWin,text=word2,height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='left',alignVert='center',units='deg',font='Arial',autoLog=autoLogging)
        textStimulusStream1.setPos([-wordEccentricity,0]) #left
        textStimuliStream1.append(textStimulusStream1)
        textStimulusStream2.setPos([wordEccentricity,0]) #right
        textStimuliStream2.append(textStimulusStream2)
            
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
    redfixColor = [0,1,1]
    
    if exportImages: fixColor= [0,0,0]
    fixatnNoiseTexture = np.round( np.random.rand(fixSizePix/4,fixSizePix/4) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    
    fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False)
    fixationBlank= visual.PatchStim(myWin, tex= -1*fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False) #reverse contrast
    fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(letterColor),size=2,units='pix',autoLog=autoLogging)
    redfixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=('white'),size=2,units='pix',autoLog=autoLogging)
    
    respPromptStim = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(letterColor),alignHoriz='center', alignVert='center',height=.05,units='norm',autoLog=autoLogging)
    acceptTextStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(letterColor),alignHoriz='center', alignVert='center',height=.05,units='norm',autoLog=autoLogging)
    acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
    respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(letterColor),alignHoriz='center', alignVert='center',height=1,units='deg',autoLog=autoLogging)
    #clickSound, badKeySound = stringResponse.setupSoundsForResponse()
    requireAcceptance = False
    nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (letterColor),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (letterColor),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    HalfWayText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (letterColor),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    screenshot= False; screenshotDone = False
    stimList = []
    #SETTING THE CONDITIONS
    cuePositions =  np.array([0]) # [4,10,16,22] used in Martini E2, group 2
    #Implement the fully factorial part of the design by creating every combination of the following conditions
    for cuePos in cuePositions:
       #for Target in [False,True]:
          for bothWordsFlipped in [False]:
            for probe in [condition]:
                for indication in [False]:
                    stimList.append( {'cuePos':cuePos, 'leftStreamFlip':bothWordsFlipped, 
                                        'rightStreamFlip':bothWordsFlipped, 'probe':probe, 'indication':indication} )
    
    trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method
    trialsForPossibleStaircase = data.TrialHandler(stimList,trialsPerCondition) #independent randomization, just to create random trials for staircase phase
    numRightWrongEachCuepos = np.zeros([ len(cuePositions), 1 ]); #summary results to print out at end
    
    
    
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
        #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT' SNOT PART OF AN ARRAY?
        try:
            #if len(letter) > 1:
            #    return (-999)
            if letter < 'A' or letter > 'Z':
                return (-999)
            else: #it's a letter
                return ord(letter)-ord('A')
        except:
            return (-999)
    
    def wordToIdx(word,wordList):
        #if it's not in the list of stimuli, return -999
        try:
            #http://stackoverflow.com/questions/7102050/how-can-i-get-a-python-generator-to-return-none-rather-than-stopiteration
            firstMatchIdx = next((i for i, val in enumerate(wordList) if val.upper()==word), None) #return i (index) unless no matches, in which case return None
            #print('Looked for ',word,' in ',wordList,'\nfirstMatchIdx =',firstMatchIdx)
            return firstMatchIdx
        except:
            print('Unexpected error in wordToIdx with word=',word)
            return (None)
            
    maxNumRespsWanted = 1
    
    #print header for data file
    print('experimentPhase\ttrialnum\tsubject\tspeed\t',file=dataFile,end='')
    print('whichWords\tTarget\tprobe' + 
           '\twordLeft\twordRight\tonset\toffset\tinferredOnset\tanswer0\ttimingblips',file=dataFile)
    
    #for i in range(maxNumRespsWanted):
    #   dataFile.write('cuePos'+str(i)+'\t')   #have to use write to avoid ' ' between successive text, at least until Python 3
    #   dataFile.write('answer'+str(i)+'\t')
    #   dataFile.write('response'+str(i)+'\t')
    #   dataFile.write('correct'+str(i)+'\t')
    #   dataFile.write('responsePosRelative'+str(i)+'\t')
    #    print('timingBlips',file=dataFile)
    #end of header
        
    def  oneFrameOfStim( n,cue,seq1,seq2,cueDurFrames,letterDurFrames,ISIframes,thisTrial,textStimuliStream1,textStimuliStream2,
                                           noise,proportnNoise,allFieldCoords,numNoiseDots): 
    #defining a function to draw each frame of stim.
    #seq1 is an array of indices corresponding to the appropriate pre-drawn stimulus, contained in textStimuli
    
      
      SOAframes = letterDurFrames+ISIframes
      cueFrames = thisTrial['cuePos']*SOAframes  #cuesPos is global variable
      stimN = int( np.floor(n/SOAframes) )
      frameOfThisLetter = n % SOAframes #earvery SOAframes, new letter
      showLetter = frameOfThisLetter < letterDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
      
      #print 'n=',n,' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes)  #DEBUGOFF
      thisStimIdx = seq1[stimN] #which letter, from A to Z (1 to 26), should be shown?
      if seq2 is not None:
        thisStim2Idx = seq2[stimN]
      #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
      cue.setLineColor( bgColor )
      if type(cueFrames) not in [tuple,list,np.ndarray]: #scalar. But need collection to do loop based on it
        cueFrames = list([cueFrames])
      for cueFrame in cueFrames: #check whether it's time for any cue
          if n>=cueFrame and n<cueFrame+cueDurFrames:
             cue.setLineColor( cueColor )
    
      if showLetter:
        textStimuliStream1[thisStimIdx].setColor( letterColor, 'rgb' )
        textStimuliStream2[thisStim2Idx].setColor( letterColor, 'rgb' )
      else: 
        textStimuliStream1[thisStimIdx].setColor( bgColor, 'rgb' )
        textStimuliStream2[thisStim2Idx].setColor( bgColor, 'rgb' )
      textStimuliStream1[thisStimIdx].flipHoriz = thisTrial['leftStreamFlip']
      textStimuliStream2[thisStim2Idx].flipHoriz = thisTrial['rightStreamFlip']
      textStimuliStream1[thisStimIdx].draw()
      textStimuliStream2[thisStim2Idx].draw()
      cue.draw()
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
      thisProbe = thisTrial['probe']
      
    cue = visual.Circle(myWin, 
                     radius=cueRadius,#Martini used circles with diameter of 12 deg
                     lineColorSpace = 'rgb',
                     lineColor=bgColor,
                     lineWidth=4.0, #in pixels. Was thinner (2 pixels) in letter AB experiments
                     units = 'deg',
                     fillColorSpace = 'rgb',
                     fillColor=None, #beware, with convex shapes fill colors don't work
                     pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
                     interpolate=True,
                     autoLog=False)#this stim changes too much for autologging to be useful
                     
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
    numTrialsEachCorrect= np.zeros( maxNumRespsWanted )
    numTrialsEachApproxCorrect= np.zeros( maxNumRespsWanted )
    debugClock = core.Clock()
    
    indicator1 = visual.TextStim(myWin, text = u"    ",pos=(wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
    indicator2 = visual.TextStim(myWin, text = u"    ",pos=(-wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
    #indicator = visual.TextStim(myWin, text = thisProbe, pos=(0, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
    indicator3 = visual.TextStim(myWin, text = u"       ",pos=(0, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
    
    noiseTexture = scipy.random.rand(128,128)*2.0-1
    
    myMask = ["%","&","@","$"]
    np.random.shuffle(myMask)
    mask1 = "".join(myMask)
    np.random.shuffle(myMask)
    mask2 = "".join(myMask)

    #post-mask
    myPatch1 = visual.TextStim(myWin, text = mask1,pos=(wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='left',alignVert='center',units='deg',autoLog=autoLogging )
    myPatch2 = visual.TextStim(myWin, text = mask2,pos=(-wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='right',alignVert='center',units='deg',autoLog=autoLogging )

    #myPatch1 = visual.TextStim(myWin, text = u"#$%&",pos=(wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='left',alignVert='center',units='deg',autoLog=autoLogging )
    
    #myPatch2 = visual.TextStim(myWin, text = u"%&@$",pos=(-wordEccentricity, 0),height=ltrHeight,colorSpace='rgb',color=letterColor,alignHoriz='right',alignVert='center',units='deg',autoLog=autoLogging )
    #myPatch1.phase += (1 / 128.0, 0.5 / 128.0)  # increment by (1, 0.5) pixels per frame
    #myPatch2.phase += (1 / 128.0, 0.5 / 128.0)  # increment by (1, 0.5) pixels per frame
    
    line1b= np.array([ [-0.175,-0.15], [0.175,-0.15]])#, [0.0,-0.05], [0.0,-0.1], [0.2,0], [0.0,0.1],  [0.0,0.05] ])
    probetop= line1b * (ltrHeight*6)
    line2b= np.array([ [-0.175,0.15], [0.175,0.15]])#, [0.0,-0.05], [0.0,-0.1], [0.2,0], [0.0,0.1],  [0.0,0.05] ])
    probebottom= line2b * (ltrHeight*6)
    
    
    RespProbeTop = visual.ShapeStim(myWin, fillColor=None, vertices=probetop, closeShape=True, interpolate=True, opacity=0.9, autoLog=False) 
    RespProbeTop2 = visual.ShapeStim(myWin, fillColor=None, vertices=probetop, closeShape=True, interpolate=True, opacity=0.9,  autoLog=False) 
    RespProbeBottom = visual.ShapeStim(myWin, fillColor=None, vertices=probebottom, closeShape=True, interpolate=True, opacity=0.9, autoLog=False) 
    RespProbeBottom2 = visual.ShapeStim(myWin, fillColor=None, vertices=probebottom, closeShape=True, interpolate=True, opacity=0.9, autoLog=False) 
    
    
    def do_RSVP_stim(thisTrial, seq1, seq2, proportnNoise,trialN,thisProbe):
        global startRecordingTime, stimClock, soundFileName
        #relies on global variables:
        #   textStimuli, logging, bgColor
        #  thisTrial should have 'cuePos'
        global framesSaved #because change this variable. Can only change a global variable if you declare it
        global debugClock
        cuesPos = [] #will contain the positions in the stream of all the cues (targets)
    
        cuesPos.append(thisTrial['cuePos'])
        cuesPos = np.array(cuesPos)
        noise = None; allFieldCoords=None; numNoiseDots=0
        if proportnNoise > 0: #gtenerating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
            (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)
    
        preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I have consistent timing blip first time that draw ringInnerR for phantom contours
        cue.setLineColor(bgColor)
        preDrawStimToGreasePipeline.extend([cue])
        for stim in preDrawStimToGreasePipeline:
            stim.draw()
        myWin.flip(); myWin.flip()
        #end preparation of stimuli
        
        core.wait(.1)
        trialClock.reset()
        indicatorPeriodMin = 0.3 #was 0.3
        indicatorPeriodFrames = int(indicatorPeriodMin*refreshRate)
        fixatnPeriodMin = 0.1
        fixatnPeriodFrames = int(   (np.random.rand(1)/2.+fixatnPeriodMin)   *refreshRate)  #random interval between 800ms and 1.3s
        ts = list(); #to store time of each drawing, to check whether skipped frames
    
        for i in range(fixatnPeriodFrames+20):  #prestim fixation interval
            #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
            #      fixation.draw()
            #else: fixationBlank.draw()
            fixationPoint.draw()
            myWin.flip()  #end fixation interval
        #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
        t0 = trialClock.getTime()
    
        midDelay = 0.5 #0.5
        
        midDelayFrames = int(midDelay *refreshRate)
        #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
        for i in range(midDelayFrames):
             fixationPoint.draw()
             myWin.flip()
        
        if thisTrial['indication']:
            #if thisProbe=='both':
                for i in range(indicatorPeriodFrames+20):
                    fixationPoint.draw()
                    indicator1.draw()
                    indicator2.draw()
                    myWin.flip()
        else:
              for i in range(indicatorPeriodFrames+20):
                    fixationPoint.draw()
                    indicator3.draw()
                    myWin.flip()
    
        midDelay2 = 0.05 #0.5
        midDelay2Frames = int(midDelay2 *refreshRate)
        #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
        for i in range(midDelay2Frames):
             fixationPoint.draw()
             myWin.flip()
        for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
                worked = oneFrameOfStim( n,cue,seq1,seq2,cueDurFrames,letterDurFrames,ISIframes,thisTrial,textStimuliStream1,textStimuliStream2,
                                                             noise,proportnNoise,allFieldCoords,numNoiseDots ) #draw letter and possibly cue and noise on top
                redfixationPoint.draw()
                if exportImages:
                    myWin.getMovieFrame(buffer='back') #for later saving
                    framesSaved +=1
                myWin.flip()
                t=trialClock.getTime()-t0;  ts.append(t);
                
        for i in range(midDelay2Frames):
             fixationPoint.draw()
             myWin.flip()
        stimClock.reset()
        startRecordingTime= stimClock.getTime()
        soundFileName = mic.record(rec_duration)  # start recording and return immediately
        # at this point, python thinks ~1ms has elapsed since the recording started
        # but the file will contain more
        # Uses onset time (epoch) to provide a number to distinguish filename and log.
        # adding a noise mask
        thisProbe = thisTrial['probe']
        
        if thisProbe == 'long':
            noiseMaskMin = 0.035 #0.20  #0.035
        else: noiseMaskMin = 0.035# .20   #0.035
            
        noiseMaskFrames = int(noiseMaskMin *refreshRate)
        for i in range(noiseMaskFrames):
             redfixationPoint.draw()
             myPatch1.draw()  #temporarily commented out for oscilloscope purposes
             myPatch2.draw()
             myWin.flip()
        #end drawing of noise mask
        debugClock.reset()
        #Now draw the post-stimulus probe
        if thisProbe == 'long':
            probeDelay = 1
        else: probeDelay = 0.0
        
        probeDelayFrames = int(probeDelay *refreshRate)
        for i in range(probeDelayFrames):
             redfixationPoint.draw()
             myWin.flip()
               
        #end of big stimulus loop
        myWin.setRecordFrameIntervals(False);
        
        postCueNumBlobsAway=-999 #doesn't apply to non-tracking and click tracking task
        
        correctAnswerIdxsStream1 = np.array( seq1[cuesPos] )
        correctAnswerIdxsStream2 = np.array( seq2[cuesPos] )
        #print('correctAnswerIdxsStream1=',correctAnswerIdxsStream1, 'wordList[correctAnswerIdxsStream1[0]]=',wordList[correctAnswerIdxsStream1[0]])
        return cuesPos,correctAnswerIdxsStream1,correctAnswerIdxsStream2,ts
    
    
    
    #################################################################################################################################################################################################################
    
    
    
    
    def handleAndScoreResponse(passThisTrial,response,responseAutopilot,task,stimSequence,cuePos,correctAnswerIdx,wordList):
        #Handle response, calculate whether correct, ########################################
        #responses are actual characters
        #correctAnswer is index into stimSequence
        #autopilot is global variable
        if autopilot or passThisTrial:
            response = responseAutopilot
        correct = 0
        #approxCorrect = 0
        #posOfResponse = -999
        #responsePosRelative = -999
        idx = correctAnswerIdx
        correctAnswer = wordList[nDoneMain].upper()
        responseString= ''.join(['%s' % char for char in response])
        responseString= responseString.upper()
        #print('correctAnswer=',correctAnswer ,' responseString=',responseString)
        if correctAnswer == responseString:
            correct = 1
        #print('correct=',correct)
        responseWordIdx = wordToIdx(responseString,wordList)
        #if responseWordIdx is None: #response is not in the wordList
         #   posOfResponse = -999
          #  logging.warn('Response was not present in the stimulus stream')
        #else:
         #   posOfResponse= np.where( responseWordIdx==stimSequence )
          #  posOfResponse= posOfResponse[0] #list with two entries, want first which will be array of places where the response was found in the sequence
           # if len(posOfResponse) > 1:
            #    logging.error('Expected response to have occurred in only one position in stream')
           # posOfResponse = posOfResponse[0] #first element of list (should be only one element long 
           # responsePosRelative = posOfResponse - cuePos
           # approxCorrect = abs(responsePosRelative)<= 3 #Vul efficacy measure of getting it right to within plus/minus
        #print('wordToIdx(',responseString,',',wordList,')=',responseWordIdx,' stimSequence=',stimSequence,'\nposOfResponse = ',posOfResponse) #debugON
        #print response stuff to dataFile
        #header was answerPos0, answer0, response0, correct0, responsePosRelative0
    #    print(cuePos,'\t', end='', file=dataFile)
        print(correctAnswer, '\t', end='', file=dataFile) #answer0
        print(responseString, '\t', end='', file=dataFile) #response0
        print(correct, '\t', end='',file=dataFile) 
        #print(probe, '\t', end='',file=dataFile)#correct0
       # print(responsePosRelative, '\t', end='',file=dataFile) #responsePosRelative0
    
        return correct
        #end handleAndScoreResponses
        staircase1.addResponse(correct)
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
        staircaseTrialN = -1; mainStaircaseGoing = False;    expStop = False
        while (not staircase.finished) and not expStop: #staircase.thisTrialN < staircase.nTrials
            if staircaseTrialN+1 < len(prefaceStaircaseNoise): #still doing easyStaircaseStarterNoise
                staircaseTrialN += 1
                thisIncrement = prefaceStaircaseNoise[staircaseTrialN]
                noisePercent = 0
            else:
                if staircaseTrialN+1 == len(prefaceStaircaseNoise): #add these non-staircase trials so QUEST knows about them
                    mainStaircaseGoing = True
                    print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise)
                    staircase.importData(100-prefaceStaircaseNoise, np.array(corrEachTrial))
                    printStaircase(staircase, descendingPsycho, briefTrialUpdate=False, printInternalVal=True, alsoLog=False)
                try: #advance the staircase
                    printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
                    noisePercent = 0 - staircase.next()  #will step through the staircase, based on whether told it (addResponse) got it right or wrong
                    thisIncrement = prefaceStaircaseNoise[staircaseTrialN]
    
                    staircaseTrialN += 1
                except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
                    print('stopping because staircase.next() returned a StopIteration, which it does when it is finished')
                    break #break out of the trials loop
            #print('staircaseTrialN=',staircaseTrialN)
            if task=='T1':
                respPromptStim.setText('Kim did they get it right?',log=False)   
            else: 
                respPromptStim.setText('Error: unexpected task',log=False)
            print('wordList=',wordList1,'wordList2=',wordList2,'staircaseTrialN=',staircaseTrialN)
            calcAndPredrawStimuli(wordList1,wordList2,staircaseTrialN)
            cuesPos,correctAnswerIdxsStream1,correctAnswerIdxsStream2, ts  = \
                                            do_RSVP_stim(cuePos, idxsStream1, idxsStream2, noisePercent/100.,staircaseTrialN)
            speedupMessages = [   'time after mask until left do_RSVP_stim' +  str( debugClock.getTime() )   ]
            debugClock.reset()
            numCasesInterframeLong = timingCheckAndLog(ts,staircaseTrialN)
            speedupMessages.append([   'timingCheckAndLog:' +  str( debugClock.getTime() )   ])
            debugClock.reset()
            expStop,passThisTrial,responses,responsesAutopilot = \
                    recordVocalResponseKRedit.recordVocalResponse(idxsStream1, idxsStream2)
            expStop,passThisTrial,responses,responsesAutopilot = \
                    stringResponse.collectStringResponse(numRespsWanted,respPromptStim,respStim,acceptTextStim,myWin,clickSound,badKeySound,
                                                                                   requireAcceptance,autopilot,responseDebug=False)
            speedupMessages.append([   'collectStringResponse:' +  str( debugClock.getTime() )   ])
            debugClock.reset()
    
            if not expStop:
                if mainStaircaseGoing:
                    print('staircase\t', end='', file=dataFile)
                else: 
                    print('staircase_preface\t', end='', file=dataFile)
                 #header start      'trialnum\tsubject\ttask\t'
                print(staircaseTrialN,'\t', end='', file=dataFile) #first thing printed on each line of g
                print(subject,'\t',task,'\t', round(noisePercent,2),'\t', end='', file=dataFile)
                correct,approxCorrect,responsePosRelative= handleAndScoreResponse(
                                                    passThisTrial,responses,responseAutopilot,task,sequenceLeft,cuesPos[0],correctAnswerIdx,wordList )
                speedupMessages.append([   'handleAndScoreResponse:' +  str( debugClock.getTime() )   ])
                debugClock.reset()
                print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
                speedupMessages.append([   'printing of numCasesInterframeLong to file:' +  str( debugClock.getTime() )   ])
                debugClock.reset()
                core.wait(.06)
                if feedback: 
                    play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
                print('staircaseTrialN=', staircaseTrialN,' noisePercent=',round(noisePercent,3),' T1approxCorrect=',T1approxCorrect) #debugON
                corrEachTrial.append(T1approxCorrect)
                if mainStaircaseGoing: 
                    staircase.addResponse(T1approxCorrect, intensity = 100-noisePercent) #Add a 1 or 0 to signify a correct/detected or incorrect/missed trial
                    #print('Have added an intensity of','{:.3f}'.format(100-noisePercent), 'T1approxCorrect =', T1approxCorrect, ' to staircase') #debugON
        #ENDING STAIRCASE PHASE
        #print(speedupMessages)
        if staircaseTrialN+1 < len(prefaceStaircaseNoise) and (staircaseTrialN>=0): #exp stopped before got through staircase preface trials, so haven't imported yet
            print('Importing ',corrEachTrial,' and intensities ',prefaceStaircaseNoise[0:staircaseTrialN+1])
            staircase.importData(100-prefaceStaircaseNoise[0:staircaseTrialN], np.array(corrEachTrial)) 
        print('framesSaved after staircase=',framesSaved) #debugON
    
        timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())
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
            print("Fit failed. (But QUEST probably still returned its estimate of threshold)")
        plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshCriterion)
        #save figure to file
        pylab.savefig(fileNameWithPath+'.pdf')
        print('The plot has been saved, as '+fileNameWithPath+'.pdf')
        pylab.show() #must call this to actually show plot
    else: #not staircase
        noisePercent = 0 #defaultNoiseLevel
        phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials.'# Letters will be drawn with superposed noise of ' + "{:.2%}".format(defaultNoiseLevel)
        print(phasesMsg); logging.info(phasesMsg)
        nDoneMain =0
        
        expStop = False
        while nDoneMain < trials.nTotal and not expStop: #MAIN EXPERIMENT LOOP while nDoneMain < len(wordList1) and not expStop:
            if nDoneMain==0:
                msg='Starting main (non-staircase) part of experiment'
                logging.info(msg); print(msg)
            thisTrial = trials.next() #get a proper (non-staircase) trial
            print(thisTrial)            
    
            calcAndPredrawStimuli(wordList1,wordList2,nDoneMain)
            thisProbe = thisTrial['probe']
            if thisProbe=='both':
              numRespsWanted = 1
            else: numRespsWanted = 1
            
            #Determine which words will be drawn
            idxsStream1 = np.arange( len(wordList1) ) #indexes for RSVP stream
            #np.random.shuffle(idxsStream1)
            correspondingWordsAtLeftAndRight = True
            if correspondingWordsAtLeftAndRight:
                idxsStream2 = copy.deepcopy(idxsStream1)
            else:
                idxsIntoWordList2 = np.arange( len(wordList2) )
                #np.random.shuffle(idxsStream2)
        
            cuesPos,correctAnswerIdxsStream1,correctAnswerIdxsStream2, ts  = \
                                                                        do_RSVP_stim(thisTrial, idxsStream1, idxsStream2, noisePercent/100.,nDoneMain,thisProbe)
    
            if nDoneMain>0:
                    speedupMessages.append([   'from end of trial to beginning of next:' +  str( 1000*debugClock.getTime() )   ])
                    debugClock.reset()
                    #print(speedupMessages)
            speedupMessages = [   'time after mask until left do_RSVP_stim' +  str( 1000*debugClock.getTime() )   ]
            debugClock.reset()
            numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)
            speedupMessages.append([   'timingCheckAndLog:' +  str( 1000*debugClock.getTime() )   ])
            debugClock.reset()
            #call for each response####################################
            #numCharsInResponse = len(wordList1[1])
            
            Target = TargetList[nDoneMain] 
            dL = [None]*numRespsWanted #dummy list for null values
            responses = copy.deepcopy(dL); responsesAutopilot = copy.deepcopy(dL); passThisTrial=copy.deepcopy(dL)
    
            x = 3.8 * wordEccentricity*(2-1) #put it 3 times farther out than stimulus, so participant is sure which is left and which right
            x2 = 3.8 * wordEccentricity*(0*2-1)
            RespProbeDurFrames = 100
            if thisProbe == 'both':
                #responseOrder = [0,1]
    
                for RespProbeFrame in xrange(RespProbeDurFrames):
                    if (Target=='R'): #change order of indices depending on Target. response0, answer0 etc refer to which one had to be reported first
                    #        responseOrder.reverse()
    
                        #RespProbe = visual.ShapeStim(myWin, lineColor='white', lineWidth=2.0, fillColor=None, vertices=arrowVertices, closeShape=True, pos= (x,0), interpolate=True, opacity=0.9, autoLog=False) 
                        RespProbeTop.pos = (x,0)
                        RespProbeTop.lineWidth=1
                        RespProbeTop.lineColor=letterColor
                        RespProbeTop2.lineWidth=1
                        RespProbeTop2.lineColor='grey'
                        RespProbeTop2.pos = (x2,0)
    
                        RespProbeBottom.pos = (x,0)
                        RespProbeBottom.lineWidth=1
                        RespProbeBottom.lineColor=letterColor
                        RespProbeBottom2.lineWidth=1
                        RespProbeBottom2.lineColor='grey'
                        RespProbeBottom2.pos = (x2,0)
                        answer0 = wordList2[ nDoneMain ]
                        answer1 = wordList1[ nDoneMain ]
                    else:
                        RespProbeTop.pos = (x,0)
                        RespProbeTop.lineWidth=1
                        RespProbeTop.lineColor=letterColor
                        RespProbeTop2.lineWidth=1
                        RespProbeTop2.lineColor=letterColor
                        RespProbeTop2.pos = (x2,0)
                        RespProbeBottom.pos = (x,0)
                        RespProbeBottom.lineWidth=1
                        RespProbeBottom.lineColor=letterColor
                        RespProbeBottom2.lineWidth=1
                        RespProbeBottom2.lineColor=letterColor
                        RespProbeBottom2.pos = (x2,0)
                        answer0= wordList1[ nDoneMain ]
                        answer1= wordList2[ nDoneMain ]
                    RespProbeTop.draw()
                    RespProbeTop2.draw()
                    RespProbeBottom.draw()
                    RespProbeBottom2.draw()
                    myWin.flip()
                    if not mic.recorder.running:
                       finishRecordingTime = stimClock.getTime()
            else: #thisProbe is not "both"
                for RespProbeFrame in xrange(RespProbeDurFrames):
                    if (Target=='R'): #change order of indices depending on LeftTarget. response0, answer0 etc refer to which one had to be reported first
                        #x = 9* wordEccentricity*(1*2-1) #put it 3 times farther out than stimulus, so participant is sure which is left and which right
                        #RespProbe = visual.TextStim(myWin,"____",pos=(x,0),colorSpace='rgb',height=2,color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )                    RespProbe.lineWidth=3
                        RespProbeBottom.lineWidth=1
                        RespProbeTop.lineColor=letterColor
                        RespProbeTop.pos = (x,0)
                        RespProbeTop.draw()
                        
                        RespProbeBottom.lineWidth=1
                        RespProbeBottom.lineColor=letterColor
                        RespProbeBottom.pos = (x,0)
                        RespProbeBottom.draw()
                        myWin.flip()
                        answer0 = wordList2[ nDoneMain ]
                        answer1 = wordList2[ nDoneMain ]
    
                        
                    else:
                        #x = 9* wordEccentricity*(0*2-1) #put it 3 times farther out than stimulus, so participant is sure which is left and which right
                        #RespProbe = visual.TextStim(myWin,"____",pos=(x,0),colorSpace='rgb',height=2,color=letterColor,alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging )
                        RespProbeTop.lineWidth=1
                        RespProbeTop.lineColor=letterColor
                        RespProbeTop.pos = (x2,0)
                        RespProbeTop.draw()
    
                        RespProbeBottom.lineWidth=1
                        RespProbeBottom.lineColor=letterColor
                        RespProbeBottom.pos = (x2,0)
                        RespProbeBottom.draw()
                        myWin.flip() 
                        answer0 = wordList1[ nDoneMain ]
                        answer1 = wordList1[ nDoneMain ]
                        
                    #speedupMessages.append([   'collectStringResponse:' +  str( 1000*debugClock.getTime() )   ])
                    debugClock.reset()
                    passThisTrial = np.array(passThisTrial).any()
                    if not mic.recorder.running:
                       finishRecordingTime = stimClock.getTime()
                
            if mic.recorder.running: # wait for the recording to finish:
                while mic.recorder.running:
                    core.wait(.01, 0)
                finishRecordingTime = stimClock.getTime()
                #msgRecordingFinished.draw()
                myWin.flip()
            # When in the audio file did the onset tone start and stop?
            # GET ALEX TO CHECK THIS BIT
            onset, offset = mic.getMarkerOnset(chunk=64, secs=markerToneDur+1.2)  # increase secs if miss the markers  Alex originally set this to +.3 Chunk was 64  Changed secs to +1.2
            onsets.append(onset)
            offsets.append(offset)
            recordingDur = finishRecordingTime-startRecordingTime
            durs.append(recordingDur)
            #Maybe microphone took awhile to start recording. Then need to add that delay to the response time will calculate within the recording
            inferredOnset = offset-markerToneDur
            inferredOnsets.append(inferredOnset)
            print("Relative to file start, marker onset= %.3f, offset= %.3f, difference = %.3f (expected %.3f), suggesting marker actually began at %.3f, recordingDuration= %.3f (requested %.3f)" 
                        % (onset, offset, offset-onset, markerToneDur, inferredOnset, recordingDur, rec_duration))
            for key in event.getKeys():       #check if pressed ESCAPE
                    key = key.upper()
                    if key in ['ESCAPE']:
                        expStop = True
            NdonePlusOne = nDoneMain + 1            
            newName = fileName + '_' + str(NdonePlusOne)+'.wav'
            os.rename(soundFileName,recordingPath+os.sep+newName)
            print("End of trial", nDoneMain)
                
            if not expStop:
                    print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile to indicate main part of experiment, not staircase
                    print(nDoneMain,'\t', end='', file=dataFile)
                    print(subject,'\t', end='', file=dataFile)
                    print(speed,'\t', end='', file=dataFile)
                    print(whichWords,'\t', end='', file=dataFile)
                    #print(thisTrial['leftStreamFlip'],'\t', end='', file=dataFile)
                    #print(thisTrial['rightStreamFlip'],'\t', end='', file=dataFile)
                    print(Target,'\t', end='', file=dataFile)
                    print(thisTrial['probe'],'\t', end='', file=dataFile)
                   
                    
                    wordLeft = wordList1[nDoneMain].upper()
                    wordRight = wordList2[nDoneMain].upper()
                    print(wordLeft, '\t', end='', file=dataFile) #answer0
                    print(wordRight, '\t', end='', file=dataFile) #answer0
                    print(onset,'\t',offset,'\t',inferredOnset,'\t',end='',file=dataFile)
                    print(answer0,'\t', end='', file=dataFile)
                    print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
                    #print('correct=',correct,'eachCorrect=',eachCorrect)
                    #numTrialsCorrect += eachCorrect.all() #so count -1 as 0
                    #numTrialsEachCorrect += eachCorrect #list numRespsWanted long
                        
                    if exportImages:  #catches one frame of response
                         myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
                         framesSaved +=1; core.wait(.1)
                         myWin.saveMovieFrames('images_sounds_movies/frames.png') #mov not currently supported 
                         expStop=True
                    #core.wait(.1)
                    #if feedback: play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
                    nDoneMain+=1
                    speedupMessages.append([   'end of trial:' +  str( 1000*debugClock.getTime() )   ])
                    debugClock.reset()
                    #dataFile.flush(); logging.flush()
                    print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal) #' trials.thisN=',trials.thisN
                    #nextText.setText('Press "SPACE" to continue!')
                    if (nDoneMain== 61): # len(wordList1)/2 ):
                            HalfWayText.setText('Please Take a Break for a Few Minutes.  When You Are Ready, Press "SPACE" to continue!')
                            HalfWayText.draw()
                            myWin.flip()
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
    
    
                    elif (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
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
                    speedupMessages.append([   '*definitely* the end of  the trial:' +  str( 1000*debugClock.getTime() )   ])
                    debugClock.reset()
                    core.wait(.1);  time.sleep(.1)
                    print("expStop = ",expStop)
                    NextTrialMsg=  visual.TextStim(myWin, "Press a key to continue", pos=(0, -.2), color=letterColor, height=ltrHeight, autoLog=autoLogging)
                    NextTrialMsg.draw()
                    myWin.flip()
                    event.waitKeys() #wait for keypress to continue
                   
    #end main trials loop
    timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())
    msg = 'Finishing at '+timeAndDateStr
    print(msg); logging.info(msg)
    if expStop:
        msg = 'user aborted experiment on ESCAPE keypress with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
        print(msg); logging.error(msg)
        break
    
    if not doStaircase and (nDoneMain >0):
        print('Of ',nDoneMain,' trials, on ',numTrialsCorrect*1.0/nDoneMain*100., '% of all trials all targets reported exactly correct',sep='')
        for i in range(numRespsWanted):
            print('stream',i,': ',round(numTrialsEachCorrect[i]*1.0/nDoneMain*100.,2), '% correct',sep='')
    dataFile.flush()
    logging.flush(); dataFile.close()
    if counter!= 3:
        endSetMsg1= visual.TextStim(myWin, "End of Set.  Press a key to continue", pos=(0, -.2), color=letterColor, height=ltrHeight, autoLog=autoLogging)
        endSetMsg1.draw()
        myWin.flip()
        event.waitKeys()
    else:
        endSetMsg2= visual.TextStim(myWin, "All finished.  Press a key to end the program", pos=(0, -.2), color=letterColor, height=ltrHeight, autoLog=autoLogging)
        endSetMsg2.draw()
        myWin.flip()
        event.waitKeys()
        myWin.close() #have to close window if want to show a plot