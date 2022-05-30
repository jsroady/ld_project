#!/usr/bin/env python3
# *-* coding: UTF-8 *-*
# Authors: Jessica Roady & Kyra Goud


import argparse
import nltk
from nltk.corpus import wordnet as wn
"""
***packages you will need to download***
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
from nltk import word_tokenize, pos_tag, ne_chunk
"""

def findWord(userInput, text):
  """
  still to do - check with other code
  """
  if userInput in text:
      return True
  else:
      return False

def getRelationship(synsets1,synsets2):
  compared1 = synsets1
  compared2 = synsets2
  for x in compared1:
      for y in compared2:
          score = x.wup_similarity(y)
          score = score if score else 0
          print(x, y, score)
          return(x, y, score)

def printDefinition(word1):
  """
  people should be able to choose which one it is then
  """
  print(word1.definition())
  return(word1)

def manuallyChooseDefinition():
  """
  method to choose noun
  """
  word1 = input("What word do you want? ")
  listOfSynset = wn.synsets(word1)
  synsets = wn.synsets(word1)
  print(synsets)
  option = input(("What option is it? " ))
  meaning = listOfSynset[int(option)-1]
  #todo get babelfy meaning and get it to compare to description. match the best
  return meaning, synsets

def getLowestSynset(meaning1,meaning2):
  """
  method can only be used when word 1 and 2 are in format 'maria.n.01' with the method: manuallyChooseDefinition - this will later become non manual
  """
  print(meaning1.lowest_common_hypernyms(meaning2))
  return (meaning1.lowest_common_hypernyms(meaning2))

def main():
  meaning1,synsets1 = manuallyChooseDefinition()
  meaning2,synsets2 = manuallyChooseDefinition()
  getRelationship(synsets1,synsets2)
  getLowestSynset(meaning1,meaning2)

if __name__ == '__main__':
    main()