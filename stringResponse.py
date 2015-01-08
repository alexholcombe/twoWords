from psychopy import event
import numpy as np
import string
from copy import deepcopy

def drawString(responses,respStim):
        respStr = ''.join(responses) #converts list of characters (responses) into string
        #print 'responses=',responses,' respStr = ', respStr #debugOFF
        respStim.setText(respStr,log=False)
        respStim.draw(); 
        
def collectStringResponse(numCharsWanted,respPromptStim,respStim,acceptTextStim,myWin,clickSound,requireAcceptance,autopilot,responseDebug=False): 
    '''respPromptStim should be a stimulus with a draw() method
    '''
    event.clearEvents() #clear the keyboard buffer
    expStop = False
    passThisTrial = False
    responses=[]
    numResponses = 0
    accepted = True
    if requireAcceptance: #require user to hit ENTER to finalize response
        accepted = False

    while not expStop and numResponses < numCharsWanted and not accepted:
    # (numResponses < numCharsWanted and not expStop) or not accepted:
    #while (numResponses < numCharsWanted and not expStop) or not accepted:
        print 'numResponses=', numResponses #debugOFF
        print 'expStop=',expStop
        print 'accepted=',accepted
        noResponseYet = True
        thisResponse=''
        while noResponseYet: #loop until a valid key is hit. 
           respPromptStim.draw()
           drawString(responses,respStim)
           myWin.flip()
           for key in event.getKeys():       #check if pressed any key
                  #Possible problem is that if user manages to hit more than one key between frame flips, it will be driven by the last one
                  key = key.upper()
                  thisResponse = key
                  if key in ['ESCAPE']:
                      expStop = True
                      noResponseYet = False
#                  if key in ['SPACE']: #observer opting out because think they moved their eyes
#                      passThisTrial = True
#                      noResponseYet = False
                  if key in string.ascii_letters or key in ['BACKSPACE','DELETE']:
                      noResponseYet = False
           if autopilot:
               noResponseYet = False
               for key in event.getKeys():    #check if pressed abort-type key. But in autopilot so not in a loop, so have to get lucky
                      key = key.upper()
                      thisResponse = key
                      if key in ['ESCAPE']:
                            expStop = True
        #Collected one response. Eventually, draw on screen
        if thisResponse or autopilot:
            click = False
            if key in string.ascii_letters:
                responses.append(thisResponse)
                numResponses += 1 #not just using len(responses) because want to work even when autopilot, where thisResponse is null
                click = True
            if key in ['BACKSPACE','DELETE']:
                if len(responses) >0:
                    responses.pop()
                    numResponses -= 1
            if click:
                clickSound.play()
        drawString(responses,respStim)
        myWin.flip() #draw again, otherwise won't draw the last key
        
        if numResponses == numCharsWanted:  #ask participant to HIT ENTER TO ACCEPT
            waitingForAccept = True
            while waitingForAccept and not expStop:
                acceptTextStim.draw()
                respStim.draw()
                for key in event.getKeys():
                    key = key.upper()
                    if key in ['ESCAPE']:
                        expStop = True
                        #noResponseYet = False
                    elif key in ['ENTER','RETURN']:
                        waitingForAccept = False
                        accepted = True
                    elif key in ['BACKSPACE','DELETE']:
                        waitingForAccept = False
                        numResponses -= 1
                        responses.pop()
                        drawString(responses,respStim)
                        myWin.flip() #draw again, otherwise won't draw the last key
                myWin.flip() #end of waitingForAccept loop
                
    responsesAutopilot = np.array(   numCharsWanted*list([('A')])   )
    responses=np.array( responses )
    #print 'responses=', responses,' responsesAutopilot=', responsesAutopilot #debugOFF
    return expStop,passThisTrial,responses,responsesAutopilot
# #######End of function definition that collects responses!!!! #####################################

if __name__=='__main__':  #Running this file directly, must want to test functions in this file
    from psychopy import monitors, visual, event, data, logging, core, sound, gui
    window = visual.Window()
    msg = visual.TextStim(window, text='press a key\n<esc> to quit')
    msg.draw()
    window.flip()
    autoLogging=False
    autopilot = False
    #create click sound for keyboard
    try:
        clickSound=sound.Sound('406__tictacshutup__click-1-d.wav')
    except:
        logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
        clickSound=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)
    
    respPromptStim = visual.TextStim(window,pos=(0, -.7),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    acceptTextStim = visual.TextStim(window,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
    respStim = visual.TextStim(window,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)

    responseDebug=False; responses = list(); responsesAutopilot = list();
    numCharsWanted = 4
    respPromptStim.setText('Enter your ' + str(numCharsWanted) + '-character response')
    requireAcceptance = True
    expStop,passThisTrial,responses,responsesAutopilot = \
                collectStringResponse(numCharsWanted,respPromptStim,respStim,acceptTextStim,window,clickSound,requireAcceptance,autopilot,responseDebug=True)
    print('responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)