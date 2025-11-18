"""
File: data_logger.py
Author: Luis Villalon
Created: 11/04/2025
Description: Logs the outcomes of each completed poker round to a CSV file
             for later analysis and machine learning training.
Updated: 11/17/2025
Author: Luis Villalon
Description: Handles creation and management of per-session CSV logs for PokerBot.
             Prompts use for logging preference and records each completed round
             with detailed player/bot data for later analysis or ML training.
"""

import csv
import os
from deck import playingCard
from datetime import datetime

class PokerDataLogger:
   """
   Creates and manages a per-session CSV log for PokerBot rounds.
   
   When logging is enabled, a timestamped file (poker_bot_MMDD_HH_MM.csv)
   is created under the /data directory with the appropriate header row.
   Each completed round is appended as one row.

   Attributes:
      enableLogging (bool): Whether logging is active for the current session.
      filePath (str): Absolute path to the active CSV file. 
   """
   
   def __init__(self, enableLogging: bool = False):
      """
      Initialize the PokerDataLogger and create a CSV file if logging is enabled.

      Parameters:
         enableLogging (bool): True to start a new logging session, False to disable.
      """
      self.enableLogging = enableLogging
      self.filePath = None

      if enableLogging:
         # Build a unique timestamped filename: poker_bot_MMD_HH_MM.csv
         timestemp = datetime.now().strftime("%m%d_%H_%M")
         os.makedirs("data", exist_ok=True)
         self.filePath = os.path.join("data", f"poker_bot_{timestamp}.csv")
         self._writeHeader()

   def _writeHeader(self) -> None:
      """
      Write the header row to the CSV file once when the file is created.

      Returns:
         None
      """
       header = [
         "Player Hand", "Bot Hand",
         "Player Strength", "Bot Strength",
         "Player Preflop Action", "Bot Preflop Action",
         "Player Flop Action", "Bot Flop Action",
         "Player Turn Action", "Bot Turn Action",
         "Player River Action", "Bot River Action",
         "Player Balance", "Winner"
      ]

      with open(self.filePath, mode="w", newline="", encoding="utf-8") as file:
         writer = csv.writer(file)
         writer.writerow(header)

   def appendRound(self, row: dict) -> None:
      """
      Append a single round of data to the CSV file.

      Parameters: 
         row (dict): Dictionary containing round data keyed by header names.

      Returns: 
         None
      """
      if not self.enableLogging or not self.filePath:
         return
      
      with open(self.filePath, mode="a", newline="", encoding="utf-8") as file:
         writer = csv.writer(file)
         writer.writerow([
            row.get("Player Hand", ""),
            row.get("Bot Hand", ""),
            row.get("Player Strength", ""),
            row.get("Bot Strength", ""),
            row.get("Player Preflop Action", ""),
            row.get("Bot Preflop Action", ""),
            row.get("Player Flop Action", ""),
            row.get("Bot Flop Action", ""),
            row.get("Player Turn Action", ""),
            row.get("Bot Turn Action", ""),
            row.get("Player River Action", ""),
            row.get("Bot River Action", ""),
            row.get("Player Balance", ""),
            row.get("Winner", "")            
         ])

def logGameResult(playerHand: list, botHand: list, communityCards: list, playerAction: str, botAction: str, winner: str) -> None:
   """
   Logs the result of a completed poker round to 'data/hands.csv'.

   Each row includes the player's hand, bot's hand, community cards, actions, and the round winner.

   Parameters:
      playerHand (list): List of playingCard objects representing the player's hand.
      botHand (list): List of playingCard objects representing the bot's hand.
      communityCards (list): List of shared community playingCard objects.
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
         writer.writerow(["Player Hand", "Bot Hand", "Community Cards", "Player Action", "Bot Action", "Winner"])
      communityStr = ", ".join(str(card) for card in communityCards)
      writer.writerow([playerHandStr, botHandStr, communityStr, playerAction, botAction, winner])
