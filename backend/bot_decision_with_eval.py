"""
File: bot_decision_with_eval.py
Author: Luis Villalon
Created: 11/04/2025
Description: Implements a smarter decision-making system for the bot.
             The bot evaluates its hand using evaluateHand() and adjusts
             its probabilities for folding, calling, or raising based on
             specific hand types.
"""

import random
from hand_evaluator import evaluateHand

def botDecisionWithEval(botHand: list) -> tuple[str, float]:
   """
   Makes a decision for the bot based on the strength of its evaluated hand.

   The bot analyzes its hand using evaluateHand() and selects actions with
   probabilities that depend on hand rank:
      - Weak hands (High Card, One Pair): mostly fold or call
      - Medium hands (Two Pair, Three of a Kind, Straight): mostly call
      - Strong hands (Flush, Full House, Four of a Kind, Straight Flush, Royal Flush): raise

   Parameters:
      botHand (list): List of Card objects representing the bot's current hand.

   Returns:
      tuple[str, float]:
         A tuple representing the bot's action and raise amount (if applicable).
         - ("FOLD", 0) for folding
         - ("CALL", 0) for calling/checking
         - ("RAISE", amount) for raising with a random amount between 20–100
   """
   (handRank, highCardValue) = evaluateHand(botHand)
   decision = ("CALL", 0)  # default fallback

   # Define decision logic for each rank
   if handRank == 0:  # High Card
      if random.random() < 0.8:
         decision = ("FOLD", 0)
      else:
         decision = ("CALL", 0)

   elif handRank == 1:  # One Pair
      if random.random() < 0.6:
         decision = ("FOLD", 0)
      else:
         decision = ("CALL", 0)

   elif handRank == 2:  # Two Pair
      if random.random() < 0.2:
         decision = ("FOLD", 0)
      else:
         decision = ("CALL", 0)

   elif handRank == 3:  # Three of a Kind
      if random.random() < 0.3:
         decision = ("CALL", 0)
      else:
         decision = ("RAISE", random.randint(20, 50))

   elif handRank == 4:  # Straight
      if random.random() < 0.2:
         decision = ("CALL", 0)
      else:
         decision = ("RAISE", random.randint(30, 70))

   elif handRank == 5:  # Flush
      decision = ("RAISE", random.randint(40, 80))

   elif handRank == 6:  # Full House
      decision = ("RAISE", random.randint(60, 100))

   elif handRank == 7:  # Four of a Kind
      decision = ("RAISE", random.randint(70, 120))

   elif handRank == 8:  # Straight Flush
      decision = ("RAISE", random.randint(90, 150))

   elif handRank == 9:  # Royal Flush
      decision = ("RAISE", random.randint(150, 200))

   return decision
