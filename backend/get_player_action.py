"""
File: get_player_action.py
Author: Luis Villalon
Created: 10/19/2025
Description: Handles terminal-based user input allowing the player to choose between actions "fold", "call", or "raise" each round.
"""

def getPlayerAction() -> tuple[str, float]:
   """
   Prompts the player to choose an action: fold, call, or raise.

   Returns:
      tuple[str, float]:
         - ("FOLD", 0) or ("CALL", 0) for fold/call.
         - ("RAISE", amount) when the player raises.
   """
   try:
      choice = input("Choose [f]old [c]all [r]aise: ").strip().lower()
      if choice not in {"f", "c", "r"}:
         raise ValueError("Invalid input. Please choose 1, 2, or 3.")

      if choice == "f":
         print("FOLD")
         return ("FOLD", 0)
      if choice == "c":
         print("CALL")
         return ("CALL", 0)

      # Handle raise workflow
      amount_input = input("Enter raise amount: ").strip()
      if not amount_input.isdigit() or int(amount_input) <= 0:
         raise ValueError("Invalid raise amount. Please enter a positive whole number.")

      amount = int(amount_input)
      print("RAISE:", amount)
      return ("RAISE", amount)

   except ValueError as err:
      print(err)
      # Recursively prompt again until the user supplies a valid choice.
      return getPlayerAction()
