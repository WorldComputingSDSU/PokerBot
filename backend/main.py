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
import random

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

def _print_stacks_and_pot(playerBalance: int, botBalance: int, pot: int) -> None:
    print(f"Stacks -> You: {playerBalance} | Bot: {botBalance} | Pot: {pot}")


def play_round(
    playerBalance: int,
    botBalance: int,
    playerIsSmallBlind: bool,
    smallBlind: int = 5,
    bigBlind: int = 10,
) -> tuple[str, dict, int, int]:
    """
    Execute a single round of the CLI game with blinds, pot, and chip tracking.

    Returns:
        winner (str)
        roundData (dict)
        updatedPlayerBalance (int)
        updatedBotBalance (int)
    """
    deck = cardDeck()
    deck.shuffle()

    print("\n--- New Round ---")

    # --- round state ---
    pot = 0
    playerInHand = True
    botInHand = True

    # These track how much each player has put in this STREET,
    # so we know what "call" means.
    playerCommitted = 0
    botCommitted = 0

    # Deal hole cards
    playerHand = safe_draw(deck, 2)
    botHand = safe_draw(deck, 2)
    communityCards: list = []

    roundData = {}
    # Tracking vars for later logging
    playerFlopAction = botFlopAction = ""
    playerTurnAction = botTurnAction = ""
    playerRiverAction = botRiverAction = ""

    # --- Post blinds and decide who acts first preflop ---
    if playerIsSmallBlind:
        # Player SB, Bot BB
        print("This hand: You are SMALL BLIND (5). Bot is BIG BLIND (10).")
        sbAmount = min(smallBlind, playerBalance)
        bbAmount = min(bigBlind, botBalance)

        playerBalance -= sbAmount
        botBalance -= bbAmount
        pot += sbAmount + bbAmount

        playerCommitted = sbAmount
        botCommitted = bbAmount

        firstToAct = "player"
    else:
        # Bot SB, Player BB
        print("This hand: Bot is SMALL BLIND (5). You are BIG BLIND (10).")
        sbAmount = min(smallBlind, botBalance)
        bbAmount = min(bigBlind, playerBalance)

        botBalance -= sbAmount
        playerBalance -= bbAmount
        pot += sbAmount + bbAmount

        botCommitted = sbAmount
        playerCommitted = bbAmount

        firstToAct = "bot"

    printHands(playerHand, botHand, hideBot=True)
    _print_board("Board", communityCards)
    _print_stacks_and_pot(playerBalance, botBalance, pot)

    # Show preflop win-rate estimates (hole cards only)
    playerWinRate = predictWinRate(playerHand)
    botWinRate = predictWinRate(botHand)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    # --- helper to award pot and finish immediately when somebody folds ---
    def _finish_on_fold(folder: str, stageWinner: str) -> tuple[str, dict, int, int]:
        nonlocal playerBalance, botBalance, pot, roundData

        if stageWinner == "Player":
            playerBalance += pot
        elif stageWinner == "Bot":
            botBalance += pot
        # pot goes to winner, then clears
        potLocal = pot
        pot = 0

        print(f"\n{folder} folded. {stageWinner} wins the pot of {potLocal} chips.")
        _print_stacks_and_pot(playerBalance, botBalance, pot)

        # Build minimal roundData for logging
        roundData = _build_round_data(
            playerHand,
            botHand,
            communityCards,
            playerPreflopAction=playerActionStr,
            botPreflopAction=botActionStr,
            winner=stageWinner,
            playerScore=None,
            botScore=None,
            playerFlopAction=playerFlopAction,
            botFlopAction=botFlopAction,
            playerTurnAction=playerTurnAction,
            botTurnAction=botTurnAction,
            playerRiverAction=playerRiverAction,
            botRiverAction=botRiverAction,
        )

        # Also log to hands.csv (existing function)
        logGameResult(
            playerHand,
            botHand,
            communityCards,
            playerActionStr,
            botActionStr,
            stageWinner,
        )

        return stageWinner, roundData, playerBalance, botBalance

    # --- PRE-FLOP BETTING ROUND (single decision each, in order) ---

    def _take_action(
        actor: str,
        amountToCall: int,
        balance: int,
        committed: int,
        cardsForBotDecision: list | None = None,
    ) -> tuple[str, int, int, bool]:
        """
        Actor makes a decision: FOLD / CALL / RAISE.
        Returns (actionStr, newBalance, newCommitted, foldedFlag).
        """
        nonlocal pot

        if actor == "player":
            print(f"\n--- Your turn (Preflop) ---")
            print(f"Amount to call: {amountToCall} | Your stack: {balance} | Pot: {pot}")
            actionName, raiseAmount = getPlayerAction()
        else:
            print(f"\n--- Bot turn (Preflop) ---")
            # Bot uses eval; if cardsForBotDecision provided, use it.
            if cardsForBotDecision is None:
                cardsForBotDecision = botHand
            actionName, raiseAmount = botDecisionWithEval(cardsForBotDecision)

        actionStr = _format_action((actionName, raiseAmount))
        print(f"{'You' if actor=='player' else 'Bot'} chose: {actionStr}")

        if actionName == "FOLD":
            return actionStr, balance, committed, True

        if actionName == "CALL":
            toPut = min(amountToCall, balance)
            balance -= toPut
            pot += toPut
            committed += toPut
        elif actionName == "RAISE":
            # Raise means call + extra raiseAmount
            toPut = min(amountToCall + raiseAmount, balance)
            balance -= toPut
            pot += toPut
            committed += toPut

        return actionStr, balance, committed, False

    # Who acts first this street?
    if firstToAct == "player":
        # Player acts vs bot's big blind
        amountToCall = max(0, botCommitted - playerCommitted)
        playerActionStr, playerBalance, playerCommitted, playerFolded = _take_action(
            "player", amountToCall, playerBalance, playerCommitted
        )
        if playerFolded:
            return _finish_on_fold("Player", "Bot")

        # Bot responds
        amountToCall = max(0, playerCommitted - botCommitted)
        botActionStr, botBalance, botCommitted, botFolded = _take_action(
            "bot", amountToCall, botBalance, botCommitted
        )
        if botFolded:
            return _finish_on_fold("Bot", "Player")

    else:
        # Bot acts first vs player's big blind
        amountToCall = max(0, playerCommitted - botCommitted)
        botActionStr, botBalance, botCommitted, botFolded = _take_action(
            "bot", amountToCall, botBalance, botCommitted
        )
        if botFolded:
            return _finish_on_fold("Bot", "Player")

        amountToCall = max(0, botCommitted - playerCommitted)
        playerActionStr, playerBalance, playerCommitted, playerFolded = _take_action(
            "player", amountToCall, playerBalance, playerCommitted
        )
        if playerFolded:
            return _finish_on_fold("Player", "Bot")

    print("\n--- End of Preflop Betting ---")
    _print_stacks_and_pot(playerBalance, botBalance, pot)

    # From here on, we keep betting much simpler: 1 action each per street, still
    # ending the hand immediately if someone folds.

    # ------------- FLOP -------------
    safe_burn(deck)
    communityCards.extend(safe_draw(deck, 3))
    print("\n-- Flop --")
    _print_board("Flop", communityCards)

    playerWinRate = predictWinRate(playerHand + communityCards)
    botWinRate = predictWinRate(botHand + communityCards)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    playerCommitted = botCommitted = 0  # reset street bets

    # Player acts first on postflop in this simple model
    print("\n--- Your turn (Flop) ---")
    print(f"Your stack: {playerBalance} | Pot: {pot}")
    actionName, raiseAmt = getPlayerAction()
    playerFlopAction = _format_action((actionName, raiseAmt))
    print(f"You chose: {playerFlopAction}")

    if actionName == "FOLD":
        return _finish_on_fold("Player", "Bot")

    if actionName == "CALL":
        # Simple "check/call": no extra bet if nobody bet
        pass
    elif actionName == "RAISE":
        toPut = min(raiseAmt, playerBalance)
        playerBalance -= toPut
        pot += toPut
        playerCommitted += toPut

    print("\n--- Bot turn (Flop) ---")
    actionName, raiseAmt = botDecisionWithEval(botHand + communityCards)
    botFlopAction = _format_action((actionName, raiseAmt))
    print(f"Bot action: {botFlopAction}")

    if actionName == "FOLD":
        return _finish_on_fold("Bot", "Player")

    if actionName == "CALL":
        if playerCommitted > 0:
            toPut = min(playerCommitted, botBalance)
            botBalance -= toPut
            pot += toPut
            botCommitted += toPut
    elif actionName == "RAISE":
        # Bot raises on top of whatever you put in (if anything)
        base = playerCommitted
        extra = raiseAmt
        toPut = min(base + extra, botBalance)
        botBalance -= toPut
        pot += toPut
        botCommitted += toPut

    print("\n--- End of Flop Betting ---")
    _print_stacks_and_pot(playerBalance, botBalance, pot)

    # ------------- TURN -------------
    safe_burn(deck)
    communityCards.append(safe_draw(deck))
    print("\n-- Turn --")
    _print_board("Turn", communityCards)

    playerWinRate = predictWinRate(playerHand + communityCards)
    botWinRate = predictWinRate(botHand + communityCards)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    playerCommitted = botCommitted = 0

    print("\n--- Your turn (Turn) ---")
    print(f"Your stack: {playerBalance} | Pot: {pot}")
    actionName, raiseAmt = getPlayerAction()
    playerTurnAction = _format_action((actionName, raiseAmt))
    print(f"You chose: {playerTurnAction}")

    if actionName == "FOLD":
        return _finish_on_fold("Player", "Bot")

    if actionName == "RAISE":
        toPut = min(raiseAmt, playerBalance)
        playerBalance -= toPut
        pot += toPut
        playerCommitted += toPut

    print("\n--- Bot turn (Turn) ---")
    actionName, raiseAmt = botDecisionWithEval(botHand + communityCards)
    botTurnAction = _format_action((actionName, raiseAmt))
    print(f"Bot action: {botTurnAction}")

    if actionName == "FOLD":
        return _finish_on_fold("Bot", "Player")

    if actionName == "CALL":
        if playerCommitted > 0:
            toPut = min(playerCommitted, botBalance)
            botBalance -= toPut
            pot += toPut
            botCommitted += toPut
    elif actionName == "RAISE":
        base = playerCommitted
        extra = raiseAmt
        toPut = min(base + extra, botBalance)
        botBalance -= toPut
        pot += toPut
        botCommitted += toPut

    print("\n--- End of Turn Betting ---")
    _print_stacks_and_pot(playerBalance, botBalance, pot)

    # ------------- RIVER -------------
    safe_burn(deck)
    communityCards.append(safe_draw(deck))
    print("\n-- River --")
    _print_board("River", communityCards)

    playerWinRate = predictWinRate(playerHand + communityCards)
    botWinRate = predictWinRate(botHand + communityCards)
    print(f"Estimated player win rate: {playerWinRate:.2f}")
    print(f"Estimated bot win rate: {botWinRate:.2f}")

    playerCommitted = botCommitted = 0

    print("\n--- Your turn (River) ---")
    print(f"Your stack: {playerBalance} | Pot: {pot}")
    actionName, raiseAmt = getPlayerAction()
    playerRiverAction = _format_action((actionName, raiseAmt))
    print(f"You chose: {playerRiverAction}")

    if actionName == "FOLD":
        return _finish_on_fold("Player", "Bot")

    if actionName == "RAISE":
        toPut = min(raiseAmt, playerBalance)
        playerBalance -= toPut
        pot += toPut
        playerCommitted += toPut

    print("\n--- Bot turn (River) ---")
    actionName, raiseAmt = botDecisionWithEval(botHand + communityCards)
    botRiverAction = _format_action((actionName, raiseAmt))
    print(f"Bot action: {botRiverAction}")

    if actionName == "FOLD":
        return _finish_on_fold("Bot", "Player")

    if actionName == "CALL":
        if playerCommitted > 0:
            toPut = min(playerCommitted, botBalance)
            botBalance -= toPut
            pot += toPut
            botCommitted += toPut
    elif actionName == "RAISE":
        base = playerCommitted
        extra = raiseAmt
        toPut = min(base + extra, botBalance)
        botBalance -= toPut
        pot += toPut
        botCommitted += toPut

    print("\n--- End of River Betting ---")
    _print_stacks_and_pot(playerBalance, botBalance, pot)

    # ------------- SHOWDOWN -------------

    winner, playerScore, botScore = _compare_hands(
        playerHand + communityCards,
        botHand + communityCards,
    )

    print("\n-- Showdown --")
    printHands(playerHand, botHand, hideBot=False)
    _print_board("Board", communityCards)
    print(f"Player hand rank: {HAND_RANK_LABELS.get(playerScore[0], 'Unknown')}")
    print(f"Bot hand rank: {HAND_RANK_LABELS.get(botScore[0], 'Unknown')}")

    # Award pot to winner (split on tie is left as an easy extension)
    if winner == "Player":
        playerBalance += pot
    elif winner == "Bot":
        botBalance += pot

    print(f"Round winner: {winner}")
    _print_stacks_and_pot(playerBalance, botBalance, 0)

    logGameResult(
        playerHand=playerHand,
        botHand=botHand,
        communityCards=communityCards,
        playerAction=playerActionStr,
        botAction=botActionStr,
        winner=winner,
    )

    roundData = _build_round_data(
        playerHand,
        botHand,
        communityCards,
        playerActionStr,
        botActionStr,
        winner,
        playerScore,
        botScore,
        playerFlopAction,
        botFlopAction,
        playerTurnAction,
        botTurnAction,
        playerRiverAction,
        botRiverAction,
    )

    return winner, roundData, playerBalance, botBalance

def _build_round_data(
    playerHand: list,
    botHand: list,
    communityCards: list,
    playerPreflopAction: str,
    botPreflopAction: str,
    winner: str,
    playerScore: tuple = None,
    botScore: tuple = None,
    playerFlopAction: str = "",
    botFlopAction: str = "",
    playerTurnAction: str = "",
    botTurnAction: str = "",
    playerRiverAction: str = "",
    botRiverAction: str = "",
) -> dict:
    """
    Build a dictionary of round information for CSV logging.

    Parameters:
        playerHand (list): Player's two hole cards.
        botHand (list): Bot's two hole cards.
        communityCards (list): Shared community cards.
        playerPreflopAction (str): Player's preflop action.
        botPreflopAction (str): Bot's preflop action.
        winner (str): Round winner label.
        playerScore (tuple): Player's evaluated hand rank and high card (optional).
        botScore (tuple): Bot's evaluated hand rank and high card (optional).
        playerFlopAction (str): Player's flop action (optional).
        botFlopAction (str): Bot's flop action (optional).
        playerTurnAction (str): Player's turn action (optional).
        botTurnAction (str): Bot's turn action (optional).
        playerRiverAction (str): Player's river action (optional).
        botRiverAction (str): Bot's river action (optional).

    Returns:
        dict: A single row of round data for logging.
    """
    playerStrength = HAND_RANK_LABELS.get(playerScore[0], "Unknown") if playerScore else ""
    botStrength = HAND_RANK_LABELS.get(botScore[0], "Unknown") if botScore else ""

    roundData = {
        "Player Hand": ", ".join(str(card) for card in playerHand),
        "Bot Hand": ", ".join(str(card) for card in botHand),
        "Player Strength": playerStrength,
        "Bot Strength": botStrength,
        "Player Preflop Action": playerPreflopAction,
        "Bot Preflop Action": botPreflopAction,
        "Player Flop Action": playerFlopAction,
        "Bot Flop Action": botFlopAction,
        "Player Turn Action": playerTurnAction,
        "Bot Turn Action": botTurnAction,
        "Player River Action": playerRiverAction,
        "Bot River Action": botRiverAction,
        "Player Balance": "",
        "Winner": winner,
    }

    return roundData



def main():
    """
    Entry point for PokerBot CLI.

    Now manages player/bot chip balances, blinds, and turn order.
    """
    print("Starting PokerBot CLI. Press Ctrl+C to exit.")

    # Prompt user to enable logging (existing behavior)
    enableLogging = input("Would you like to start a logging session? [y/N]: ").strip().lower() == "y"
    logger = PokerDataLogger(enableLogging=enableLogging)

    # --- NEW: chip stacks + blinds + starting position ---
    playerBalance = 1000
    botBalance = 1000
    SMALL_BLIND = 5
    BIG_BLIND = 10

    # Randomly choose who is small blind / acts first preflop in the first round
    # True  -> player is small blind / acts first
    # False -> bot is small blind / acts first
    playerIsSmallBlind = random.choice([True, False])

    try:
        while True:
            print("\n====================================")
            print(f"New hand starting...")
            print(f"Your stack: {playerBalance} chips | Bot stack: {botBalance} chips")
            print("------------------------------------")

            # Play a single round; pass stacks + whose turn it is
            winner, roundData, playerBalance, botBalance = play_round(
                playerBalance=playerBalance,
                botBalance=botBalance,
                playerIsSmallBlind=playerIsSmallBlind,
                smallBlind=SMALL_BLIND,
                bigBlind=BIG_BLIND,
            )

            # Persist player's ending balance into the logging row
            roundData["Player Balance"] = playerBalance

            # Append one row of round data if logging is enabled
            if enableLogging:
                logger.appendRound(roundData)

            print("------------------------------------")
            print(f"End of hand. Stacks -> You: {playerBalance} | Bot: {botBalance}")
            print("Next hand: blinds will rotate.\n")

            # Rotate blinds / starting position each round
            playerIsSmallBlind = not playerIsSmallBlind

            # Stop if someone is broke (optional, but nice)
            if playerBalance <= 0:
                print("You are out of chips. Game over.")
                break
            if botBalance <= 0:
                print("Bot is out of chips. You win the match!")
                break

            choice = input("Play another round? [Y/n]\n").strip().lower()
            if choice == "n":
                break
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
