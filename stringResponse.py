from psychopy import event
import numpy as np
import string

def collectStringResponse(numCharsWanted,respPromptStim,respStim,myWin,clickSound,requireAcceptance,autopilot,responseDebug=False): 
    '''respPromptStim should be a stimulus with a draw() method
    '''
    event.clearEvents() #clear the keyboard buffer
    expStop = False
    passThisTrial = False
    respStr = ''
    responses=[]
    numResponses = 0
    accepted = True
    if requireAcceptance: #require user to hit ENTER to finalize response
        accepted = False
    while numResponses < numCharsWanted and not accepted and not expStop:
        #print 'numResponses=', numResponses #debugOFF
        noResponseYet=True
        thisResponse=''
        while noResponseYet: #collect one response
           respPromptStim.draw()
           #respStr= 'Y'
           #print 'respStr = ', respStr, ' type=',type(respStr) #debugOFF
           respStim.setText(respStr,log=False)
           respStim.draw()
           if numResponses == numCharsWanted:
            #ask participant to HIT ENTER TO ACCEPT
           myWin.flip()
           for key in event.getKeys():       #check if pressed abort-type key
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
        #click to provide feedback that response collected. Eventually, draw on screen
        clickSound.play()
        if thisResponse or autopilot:
            if key in string.ascii_letters:
                responses.append(thisResponse)
                numResponses += 1 #not just using len(responses) because want to work even when autopilot, where thisResponse is null
            if key in ['BACKSPACE','DELETE']:
                if len(responses) >0:
                    responses.pop()
                    numResponses -= 1
        
        respStr = ''.join(responses) #converts list of characters (responses) into string
        #print 'responses=',responses,' respStr = ', respStr #debugOFF
        respStim.setText(respStr,log=False); respStim.draw(); myWin.flip() #draw again, otherwise won't draw the last key
        
    responsesAutopilot = np.array(   numCharsWanted*list([('A')])        )
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
    
    respPromptStim = visual.TextStim(window,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    respStim = visual.TextStim(window,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)

    responseDebug=False; responses = list(); responsesAutopilot = list();
    numCharsWanted = 4
    respPromptStim.setText('Enter your ' + str(numCharsWanted) + '-character response')

    expStop,passThisTrial,responses,responsesAutopilot = \
                collectStringResponse(numCharsWanted,respPromptStim,respStim,window,clickSound,autopilot,responseDebug=True)
    print('responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)