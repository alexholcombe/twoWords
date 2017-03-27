
#Take a long list of bigrams (probably created in R and designed to avoid two-letter words)
#Scramble them (for each trial)
#Break into two streams.   This will be used by the main program for the sequence.

from __future__ import print_function #use python3 style print

#read in the file of list of bigrams
stimFile = 'twoLetters-Cheryl.txt'
stimList = open(stimFile)
bigramList = [x.rstrip() for x in stimList.readlines()]
print('Read in', len(bigramList), 'strings')
print('bigramList = ',bigramList)

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
