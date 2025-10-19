"""
File: get_player_action.py
Author: Luis Villalon
Created: 10/19/2025
Description: Handles terminal-based user input allowing the player to choose between actions "fold", "call", or "raise" each round.
"""

def getPlayerAction() -> tuple[str, float]:
   """
   Prompts the player to choose an action: "fold", "call", or "raise".

   Parameters:
      None

   Returns:
      tuple[str, float]: 
         The tuple represents the player action and associated amount.
         - ("FOLD", 0) or ("CALL", 0) when the player chooses fold or call.
         - ("RAISE", amount) when the player chooses to raise with a numeric amount.
   """
   while True:
      userInput = input("Choose an action: [f]old, [c]all, [r]aise\n").lower()
      if userInput == "f": 
         print("FOLD")
         return ("FOLD", 0)
      elif userInput == "c": 
         print("CALL")
         return ("CALL", 0)
      elif userInput == "r":
         while True:
            amount = input("Enter raise amount: ")
            if amount.isdigit():
               amount = int(amount)
               break
            else:
               print("Invalid input. Please enter a numeric whole value.")        
         print("RAISE:", amount)
         return ("RAISE", amount)
      else:
         print("Invalid input. Try again.")