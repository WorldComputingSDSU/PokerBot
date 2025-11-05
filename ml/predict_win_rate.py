"""
File: predict_win_rate.py
Author: Jacob Silva
Created: 11/04/2025
Description: Placeholder ML model for estimating win probability based on hand strength.
"""

from itertools import combinations

from backend.hand_evaluator import evaluateHand  # matches your repo naming style


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


def predictWinRate(cards: list) -> float:
    """
    Placeholder for ML-based win rate prediction.

    Parameters:
        cards (list): playingCard objects available to the player (hole cards plus any community cards).

    Returns:
        float: Heuristic win rate between 0.05 and 0.99.
    """
    strength, high_card = _best_hand_score(cards)

    # Deterministic heuristic mapping covering every hand rank
    rank_to_rate = {
        0: 0.18,  # High Card
        1: 0.28,  # Pair
        2: 0.38,  # Two Pair
        3: 0.48,  # Three of a Kind
        4: 0.60,  # Straight
        5: 0.70,  # Flush
        6: 0.80,  # Full House
        7: 0.88,  # Four of a Kind
        8: 0.94,  # Straight Flush
        9: 0.97,  # Royal Flush
    }

    base_rate = rank_to_rate.get(strength, 0.5)
    kicker_adjust = max(0, min(1, (high_card - 2) / 12)) * 0.04  # subtle boost for higher cards
    win_rate = base_rate + kicker_adjust

    # Clamp to a sane range to avoid certainty claims
    return max(0.05, min(win_rate, 0.99))
