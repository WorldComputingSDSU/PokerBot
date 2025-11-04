"""
File: get_player_action.py
Author: Luis Villalon
Created: 11/04/2025
Description: Contains a simple placeholder decision-making system for the bot.
             Randomly selects between "FOLD", "CALL", or "RAISE" using basic probability logic.
"""

import random

def botDecision() -> tuple[str, float]:
   """
   Generates a basic decision for the bot: "FOLD", "CALL", or "RAISE".

   The function randomly selects one of the three actions.
   If "RAISE" is selected, it also generates a random raise amount between 10 and 50.

   Parameters:
      None

   Returns:
      tuple[str, float]:
         A tuple representing the bot's decision and raise amount (if applicable).
         - ("FOLD", 0) or ("CALL", 0) when the bot chooses fold or call.
         - ("RAISE", amount) when the bot chooses to raise, with a random amount between 10 and 50.
   """
   options = ["FOLD", "CALL", "RAISE"]
   choice = random.choice(options)

   if choice == "RAISE":
      raise_amount = random.randint(10, 50)SHo
      return ("RAISE", raise_amount)
   else:
      return (choice, 0)