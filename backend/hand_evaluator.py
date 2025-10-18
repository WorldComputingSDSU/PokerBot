     
def evalutate_hand(hand):
   """
   hand_rank: A number representing the category
      - 1: Royal Flush
      - 2: Straight Flush
      - 3: Four of a Kind
      - 4: Full House
      - 5: Flush
      - 6: Straight
      - 7: Three of a Kind
      - 8: Two Pair
      - 9: Pair
      - 10: High Card
   """
   hand_rank = 0
   """
   high_card_value: The value of the strongest card in that hand (to compare ties)
      - "2": 2,
      - "3": 3,
      - "4": 4,
      - "5": 5,
      - "6": 6,
      - "7": 7,
      - "8": 8,
      - "9": 9,
      - "10": 10,
      - "J": 11,
      - "Q": 12,
      - "K": 13,
      - "A": 14
   """      
   high_card_value = 0
   """
   list_of_ranks: list of rank values in the hand
   """
   list_of_ranks = []
   """
   list_of_suita: list of suits in the hand
   """   
   list_of_suits = []
   for i in hand:
      list_of_ranks.append(i.getValue())
      list_of_suits.append(i.suit)




   return (hand_rank, high_card_value)

