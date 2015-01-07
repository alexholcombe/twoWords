from psychopy import event

def collectStringResponse(numCharsWanted,respPrompt,myWin,responseDebug=False): 
    '''respPrompt should be a stimulus with a draw() method
    '''
    event.clearEvents() #clear the keyboard buffer
    expStop = False
    passThisTrial = False
    respStr = ''
    responses=[]
    numResponses = 0
    while numResponses < numCharsWanted and not expStop:
        #print 'numResponses=', numResponses #debugOFF
        noResponseYet=True
        thisResponse=''
        while noResponseYet: #collect one response
           respPrompt.draw()
           #respStr= 'Y'
           #print 'respStr = ', respStr, ' type=',type(respStr) #debugOFF
           respText.setText(respStr,log=False)
           respText.draw()
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
                  if key in ['A', 'C', 'B', 'E', 'D', 'G', 'F', 'I', 'H', 'K', 'J', 'M', 'L', 'O', 'N', 'Q', 'P', 'S', 'R', 'U', 'T', 'W', 'V', 'Y', 'X', 'Z']:
                      noResponseYet = False
           if autopilot:
               noResponseYet = False
               for key in event.getKeys():    #check if pressed abort-type key. But in autopilot so not in a loop, so have to get lucky
                      key = key.upper()
                      thisResponse = key
                      if key in ['ESCAPE']:
                            expStop = True
        #click to provide feedback that response collected. Eventually, draw on screen
        click.play()
        if thisResponse or autopilot:
            responses.append(thisResponse)
            numResponses += 1 #not just using len(responses) because want to work even when autopilot, where thisResponse is null
        respStr = ''.join(responses) #converts list of characters (responses) into string
        #print 'responses=',responses,' respStr = ', respStr #debugOFF
        respText.setText(respStr,log=False); respText.draw(); myWin.flip() #draw again, otherwise won't draw the last key
        
    responsesAutopilot = np.array(   numRespsWanted*list([('A')])        )
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
    respPrompt = visual.TextStim(window,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)

    responseDebug=False; responses = list(); responsesAutopilot = list();
    numCharsWanted = 2
    expStop,passThisTrial,responses,responsesAutopilot = \
                collectStringResponse(numCharsWanted,respPrompt,window,responseDebug=True)