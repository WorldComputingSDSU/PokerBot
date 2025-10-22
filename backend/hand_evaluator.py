"""
File: hand_evaluator.py
Author: Luis Villalon
Created: 10/18/2025
Description: Determines the strength of poker hand.
"""

from collections import Counter     

def evaluateHand(hand: list) -> tuple[int, int]:
   """
   Evaluates the strength of a poker hand.

   Parameters:
      hand (list): List of Card objects representing the player's hand.

   Returns:
      tuple: (Numerical score representing the hand's strength, Numerical score of the strongest card in the hand)
   """
   handRank = 0 
   highCardValue = 0 
   listOfRanks = [] 
   listOfSuits = [] 
   hand.sort(key=lambda card: card.getValue()) # Sort (least to greatest) the cards based on their rank value returned by getValue()
   for i in hand:
      listOfRanks.append(i.getValue())
      listOfSuits.append(i.suit)
   rankCounts = Counter(listOfRanks) # Counts the number of times a rank appears in a hand
   isFlush = len(set(listOfSuits)) == 1 # Check for a Flush: five cards of the same suit, not in sequence
   isStraight = all(listOfRanks[i] + 1 == listOfRanks[i + 1] for i in range(len(listOfRanks) - 1)) # Check for a Straight: five non-suited cards in sequence
   isRoyal = listOfRanks == [10, 11, 12, 13, 14]
   if isFlush and isRoyal:
      handRank = 9
   elif isFlush and isStraight:
      handRank = 8
   elif 4 in rankCounts.values():
      handRank = 7
   elif 3 in rankCounts.values() and 2 in rankCounts.values():
      handRank = 6     
   elif isFlush:
      handRank = 5
   elif isStraight:
      handRank = 4
   elif 3 in rankCounts.values():
      handRank = 3        
   elif list(rankCounts.values()).count(2) == 2:
      handRank = 2
   elif 2 in rankCounts.values():
      handRank = 1      
   else:
      handRank = 0
   highCardValue = max(listOfRanks) # The highest ranking card in the hand
   return (handRank, highCardValue)