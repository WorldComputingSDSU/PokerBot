"""
File: main.py
Author: Jacob Silva
Created: 11/05/2025
Description: Command-line entry point that runs one or more PokerBot rounds.
"""

from pathlib import Path
import sys
from itertools import combinations
from data_logger import PokerDataLogger

# Ensure repository root is on sys.path so ml package imports resolve when running this file directly.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from deck import cardDeck, emptyDeckError
from get_player_action import getPlayerAction
from bot_decision_with_eval import botDecisionWithEval
from hand_evaluator import evaluateHand
from print_hands import printHands
from data_logger import logGameResult
from ml.predict_win_rate import predictWinRate

HAND_RANK_LABELS = {
    0: "High Card",
    1: "One Pair",
    2: "Two Pair",
    3: "Three of a Kind",
    4: "Straight",
    5: "Flush",
    6: "Full House",
    7: "Four of a Kind",
    8: "Straight Flush",
    9: "Royal Flush",
}


def _best_hand_score(cards: list) -> tuple[int, int]:
    """
    Evaluate the strongest 5-card combination available and return (rank, high card).
    """
    if len(cards) <= 5:
        return evaluateHand(list(cards))

    best_score = (-1, -1)
    for combo in combinations(cards, 5):
        combo_score = evaluateHand(list(combo))
        if combo_score > best_score:
            best_score = combo_score
    return best_score


def _compare_hands(player_cards: list, bot_cards: list) -> tuple[str, tuple[int, int], tuple[int, int]]:
    """
    Determine the winner between the player and bot card pools.

    Returns:
        tuple: (winner label, player score tuple, bot score tuple)
    """
    player_score = _best_hand_score(player_cards)
    bot_score = _best_hand_score(bot_cards)

    if player_score > bot_score:
        return "Player", player_score, bot_score
    if player_score < bot_score:
        return "Bot", player_score, bot_score
    return "Tie", player_score, bot_score


def _format_action(action: tuple[str, float]) -> str:
    actionName, amount = action
    if actionName == "RAISE" and amount:
        return f"{actionName} {amount}"
    return actionName


def safe_draw(deck: cardDeck, n: int = 1):
    """
    Draw cards from the deck, reshuffling if the deck runs out mid-game.
    """
    try:
        return deck.draw(n)
    except emptyDeckError:
        # An empty deck mid-round just means we reshuffle and continue play.
        print("Deck empty — reshuffling...")
        deck.reset()
        return deck.draw(n)


def safe_burn(deck: cardDeck, n: int = 1) -> None:
    """
    Burn cards safely, reshuffling if the deck runs out mid-game.
    """
    try:
        deck.burn(n)
    except emptyDeckError:
        # Mirror draw handling so a short deck never stops the round.
        print("Deck empty — reshuffling...")
        deck.reset()
        deck.burn(n)


def _print_board(stage: str, community_cards: list) -> None:
    board_display = ", ".join(str(card) for card in community_cards) if community_cards else "[No Cards]"
    print(f"{stage}: {board_display}")


def play_round() -> str:
    """
    Execute a single round of the CLI game and display win rate estimates.

    Returns:
        str: Winner label.
    """
    deck = cardDeck()
    deck.shuffle()  # Fresh shuffle at the top of every hand keeps play random.

    print("\n--- New Round ---")

    playerHand = safe_draw(deck, 2)
    botHand = safe_draw(deck, 2)
    communityCards: list = []

    printHands(playerHand, botHand, hideBot=True)
    _print_board("Board", communityCards)

    # Show the player how the heuristic rates both hole-card sets.
    playerWinRate = predictWinRate(playerHand)
    botWinRate = predictWinRate(botHand)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    playerAction = getPlayerAction()
    playerActionStr = _format_action(playerAction)
    print(f"You chose: {playerActionStr}")

    botAction = botDecisionWithEval(botHand)
    botActionStr = _format_action(botAction)
    print(f"Bot action: {botActionStr}")


   # Jacob: Fixed game folding bug that would replay the rest of the game even after a fold
    if playerAction[0] == "FOLD":
        print("\nYou folded. Bot wins.")
        logGameResult(
            playerHand,
            botHand,
            communityCards,
            playerActionStr,
            botActionStr,
            "Bot",
        )
        return "Bot"

    if botAction[0] == "FOLD":
        print("\nBot folded. You win.")
        logGameResult(
            playerHand,
            botHand,
            communityCards,
            playerActionStr,
            botActionStr,
            "Player",
        )
        return "Player"

    # Flop
    safe_burn(deck)
    communityCards.extend(safe_draw(deck, 3))
    print("\n-- Flop --")
    _print_board("Flop", communityCards)
    # Re-evaluate odds as soon as new shared cards appear.
    playerWinRate = predictWinRate(playerHand + communityCards)
    botWinRate = predictWinRate(botHand + communityCards)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    # Turn
    safe_burn(deck)
    communityCards.append(safe_draw(deck))
    print("\n-- Turn --")
    _print_board("Turn", communityCards)
    playerWinRate = predictWinRate(playerHand + communityCards)
    botWinRate = predictWinRate(botHand + communityCards)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    # River
    safe_burn(deck)
    communityCards.append(safe_draw(deck))
    print("\n-- River --")
    _print_board("River", communityCards)
    # Final odds check now that the full board is exposed.
    playerWinRate = predictWinRate(playerHand + communityCards)
    botWinRate = predictWinRate(botHand + communityCards)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    winner, playerScore, botScore = _compare_hands(
        playerHand + communityCards,
        botHand + communityCards,
    )

    print("\n-- Showdown --")
    printHands(playerHand, botHand, hideBot=False)
    _print_board("Board", communityCards)
    # Translate the numeric hand strength into a friendly label for the CLI.
    print(f"Player hand rank: {HAND_RANK_LABELS.get(playerScore[0], 'Unknown')}")
    print(f"Bot hand rank: {HAND_RANK_LABELS.get(botScore[0], 'Unknown')}")
    print(f"Round winner: {winner}")

    logGameResult(
        playerHand=playerHand,
        botHand=botHand,
        communityCards=communityCards,
        playerAction=playerActionStr,
        botAction=botActionStr,
        winner=winner,
    )

    return winner


def main():
    """
    Entry point for PokerBot CLI.

    Prompts the user to being a logging session, initalizes a PokerDataLogger
    instance if requested, and manages the game loop until the player exits.

    Returns:
        None
    """
    print("Starting PokerBot CLI. Press Ctrl+C to exit.")

    # Prompt user to enable logging
    enableLogging = input("Would you like to start a logging session? [y/N]: ").strip.lower() == "y"
    logger = PokerDataLogger(enableLogging = enableLogging)

    try:
        while True:
            winner, roundData = play_round()

            # Append one row of round data if logging is enabled
            if enableLogging:
                logger.appendRound(roundData)
            
            choice = input("Play another round? [Y/n]\n").strip().lower()
            if choice == "n":
                break
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
