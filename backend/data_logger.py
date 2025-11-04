"""
File: data_logger.py
Author: Luis Villalon
Created: 11/04/2025
Description: Logs the outcomes of each completed poker round to a CSV file
             for later analysis and machine learning training.
"""

import csv
import os
from deck import Card

def logGameResult(playerHand: list, botHand: list, playerAction: str, botAction: str, winner: str) -> None:
   """
   Logs the result of a completed poker round to 'data/hands.csv'.

   Each row includes the player's hand, bot's hand, actions, and the round winner.

   Parameters:
      playerHand (list): List of Card objects representing the player's hand.
      botHand (list): List of Card objects representing the bot's hand.
      playerAction (str): The final action taken by the player ("FOLD", "CALL", or "RAISE").
      botAction (str): The final action taken by the bot ("FOLD", "CALL", or "RAISE").
      winner (str): Label indicating who won the round ("Player" or "Bot").

   Returns:
      None
   """

   # Ensure the data folder exists
   os.makedirs("data", exist_ok=True)
   file_path = os.path.join("data", "hands.csv")

   # Convert hands to string form
   playerHandStr = ", ".join(str(card) for card in playerHand)
   botHandStr = ", ".join(str(card) for card in botHand)

   # Check if file exists to decide if we need to write a header
   file_exists = os.path.isfile(file_path)

   # Write data to CSV file
   with open(file_path, mode="a", newline="", encoding="utf-8") as file:
      writer = csv.writer(file)
      if not file_exists:
         writer.writerow(["Player Hand", "Bot Hand", "Player Action", "Bot Action", "Winner"])
      writer.writerow([playerHandStr, botHandStr, playerAction, botAction, winner])


if __name__ == "__main__":
   # ====== TEST SECTION ======
   # Create some sample Card objects to simulate a round result
   playerHand = [
      Card("A", "Hearts"),
      Card("K", "Hearts"),
      Card("10", "Hearts"),
      Card("J", "Hearts"),
      Card("Q", "Hearts")
   ]

   botHand = [
      Card("9", "Clubs"),
      Card("9", "Spades"),
      Card("9", "Diamonds"),
      Card("3", "Hearts"),
      Card("3", "Clubs")
   ]

   playerAction = "RAISE"
   botAction = "CALL"
   winner = "Player"

   # Log the result
   logGameResult(playerHand, botHand, playerAction, botAction, winner)
   print("✅ Round result logged successfully! Check data/hands.csv.")
