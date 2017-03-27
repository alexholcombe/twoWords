
#Take a long list of bigrams (probably created in R and designed to avoid two-letter words)
#Scramble them (for each trial)
#Break into two streams.   This will be used by the main program for the sequence.

from __future__ import print_function #use python3 style print

#read in the file of list of bigrams
stimFile = 'twoLetters-Cheryl.txt'
stimListFile= open(stimFile)
bigramList = [x.rstrip() for x in stimListFile.readlines()]
print('Read in', len(bigramList), 'strings')
print('bigramList = ',bigramList)
stimListFile.close()

#Scramble 
import random
from copy import deepcopy

shuffled = deepcopy(bigramList)
random.shuffle(shuffled)

print('first 10 unshuffled=',bigramList[:10])
print('first 10 shuffled=',shuffled[:10])

#Break into two
firstLetters = list()
secondLetters = list()
for bigram in shuffled:
    firstLetter = bigram[0]
    secondLetter = bigram[1]
    firstLetters.append( firstLetter )
    secondLetters.append ( secondLetter ) 
   
print('first 10 firstLetters=',firstLetters[:10])
print('first 10 secondLetters=',secondLetters[:10])

#MAP ONTO THE EXISTING LIST OF LETTERS DRAWNL
#Create the existing list of letters drawn, as usually done in our twoWords program
numWordsInStream = 26
wordsUnparsed="a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x  ,y,z" 
wordList = wordsUnparsed.split(",") #split into list
for i in range(len(wordList)):
    wordList[i] = wordList[i].replace(" ", "") #delete spaces
 
 #Find the index of each desired letter into the list of letters already drawn
 