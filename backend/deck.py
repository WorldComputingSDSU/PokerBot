"""
File: deck.py
Author: Jacob Silva
Created: 10/12/2025
Description: Contains the Card and Deck classes
"""

import random

class Card:
   """
   Represents a single playing card rank and suit (10 of Hearts)
   """
   def __init__(self, rank, suit):
      self.rank = rank
      self.suit = suit

   def __str__(self):
      """
      Return a readable version of card for CLI printout
      """
      return f"{self.rank} of {self.suit}"

   def __repr__(self):
      """
      Return a developer readable version of card for ranking printout
      """
      return f"Card('{self.rank}', '{self.suit}')"

   def getValue(self):
      """
      Return the value of the card as an integer. The value is based on the rank of the card.
      For example, a "2" is worth 2 points, while a "K" is worth 13 points.
      """
      rankValues = {
         "2": 2,
         "3": 3,
         "4": 4,
         "5": 5,
         "6": 6,
         "7": 7,
         "8": 8,
         "9": 9,
         "10": 10,
         "J": 11,
         "Q": 12,
         "K": 13,
         "A": 14
      }
      return rankValues.get(self.rank,0)


   class Deck:
      """
      Represents a deck of 52 playing cards
      handles shuffling and drawing cards
      """

      def __init__(self):
         suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
         ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
         self.cards = [Card(rank, suit) for rank in ranks for suit in suits]

      def shuffle(self):
         """ shuffle the deck randomly"""
         random.shuffle(self.cards)

      def draw(self, n=1):
         """ draw n cards from the deck
         returns a list if n > 1, otherwise returns a single card
         """
         if len(self.cards) < n:
            raise ValueError("Not enough cards in the deck")
         drawn = [self.cards.pop() for _ in range(n)]
         return drawn[0] if n == 1 else drawn
      
      def burn(self, n=1):
         """ burn n cards from the deck"""
         if len(self.cards) < n:
            raise ValueError("Not enough cards in the deck")
         for _ in range(n):
            self.cards.pop()

      def reset(self):
         """ reset the deck and shuffle"""
         self.__init__()
         self.shuffle()


