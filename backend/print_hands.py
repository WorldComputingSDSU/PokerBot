"""
File: print_hands.py
Author: Luis Villalon
Created: 10/18/2025
Description: Displays the player's and bot's cards in the terminal in a readable format after each round.
"""

def printHands(playerHand: list, botHand: list, hideBot: bool = False):
   """
   Displays the player's and bot's cards in the terminal in a readable format after each round.

   Parameters:
      playerHand (list): List of Card objects representing the player's hand.
      botHand (list): List of Card objects representing the bot's hand.
      hideBot (bool): Boolean variable representing whether or not the bot's hand should be displayed.

   Returns:
      None
   """    
   print("Your hand:", ", ".join(str(card) for card in playerHand))   
   if hideBot:
      print("Bot hand: [Hidden Card],", botHand[1])
   else:
      print("Bot hand:", ", ".join(str(card) for card in botHand))
