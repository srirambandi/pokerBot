from pypokerengine.players import BasePokerPlayer
from time import sleep
import random as rand
import pprint

class mctsPlayer2(BasePokerPlayer):


  def __init__(self):
    # initialize hand counter to track the number of hands played
    self.hand_count = 0
    # sum card values to determine if we have high, mid, or low cards
    self.valueDict = {
      "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
      "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14
    }

  # TODO take hole cards and return one of 8 abstract state buckets
  def preFlopAbstraction(self, holeCards):
    return 1


  # for pairs, three of a kind & four of a kind
  # 1 if it exists
  # 0 if not
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveOfAKind(self, hole_cards, quantity, community_cards): # quantity = 2 for pairs, 3 for three of a kind, 4 for four of a kind
    # Helper function to count ranks in a list of cards
    def count_ranks(cards):
        rank_counts = {}
        for _, rank in cards:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        return rank_counts
    
    # First check if community cards alone can form the hand
    comm_rank_counts = count_ranks(community_cards)
    if any(count >= quantity for count in comm_rank_counts.values()):
        return (0, None)  # Hand exists without hole cards, so return 0
    
    # Combine all cards
    all_cards = hole_cards + community_cards
    all_rank_counts = count_ranks(all_cards)
    
    # Check if we can form the hand with hole cards
    for rank, count in all_rank_counts.items():
        if count >= quantity:
            # Verify at least one card comes from hole cards
            hole_ranks = [card[1] for card in hole_cards]
            if rank in hole_ranks:
                return (1, 'high' if self.valueDict[rank] >= 10 else 'low')
    
    # Calculate how many cards are missing because we know we cannot form the hand
    max_count = max(all_rank_counts.values()) if all_rank_counts else 0
    return (-(quantity - max_count), None)
  

  # 1 if we have two pair
  # -1 if we are one card away from two pair, -2 if we are two cards away, -3 if we are three cards away
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveTwoPair(self, hole_cards, community_cards):
    def count_pairs(cards):
        rank_counts = {}
        pair_ranks = []
        for _, rank in cards:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        pair_ranks = [self.valueDict[r] for r, cnt in rank_counts.items() if cnt >= 2]
        return sorted(pair_ranks, reverse=True)
    
    # Check if community cards alone can form two pair
    comm_pairs = count_pairs(community_cards)
    if len(comm_pairs) >= 2:
        return (0, None)  # Hand exists without hole cards, so return 0
    
    # Combine all cards
    all_cards = hole_cards + community_cards
    all_pairs = count_pairs(all_cards)
    
    # Check if we can form the hand with hole cards
    if len(all_pairs) >= 2:
        # Verify at least one pair uses a hole card
        hole_ranks = [card[1] for card in hole_cards]
        valid_pairs = 0
        high_pairs = 0
        
        # Count how many pairs involve hole cards and how many are high
        for pair_rank in all_pairs[:2]:  
            if pair_rank in [self.valueDict[r] for r in hole_ranks]:
                valid_pairs += 1
            if pair_rank >= 10:
                high_pairs += 1
        
        if valid_pairs > 0:
            if high_pairs == 2:
                return (1, "highHigh")
            elif high_pairs == 1:
                return (1, "highLow")
            else:
                return (1, "lowLow")
    
    # Calculate how many cards are missing because we know we cannot form the hand
    current_pairs = len(all_pairs)
    missing_pairs = max(0, 2 - current_pairs)
    
    # Determine the quality of existing partial pairs
    if current_pairs == 1:
        pair_type = "highHigh" if all_pairs[0] >= 10 else "highLow"
    else:
        # Count high cards in hole cards to estimate potential
        high_count = sum(1 for card in hole_cards if self.valueDict[card[1]] >= 10)
        if high_count >= 2:
            pair_type = "highHigh"
        elif high_count == 1:
            pair_type = "highLow"
        else:
            pair_type = "lowLow"
    
    return (-missing_pairs, pair_type)
    

  # 1 if we have a straight
  # negative number representing how many cards away we are from making a straight
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveStraight(self, hole_cards, community_cards):
    def check_straight(cards):
        # Extract unique ranks
        unique_ranks = set(card[1] for card in cards)
        
        # Check for Ace-low straight 
        ace_low_straight = {"A", "2", "3", "4", "5"}
        missing_for_ace_low = ace_low_straight - unique_ranks
        ace_low_distance = len(missing_for_ace_low)
        
        # Sort card values
        unique_values = sorted({self.valueDict[rank] for rank in unique_ranks})
        
        # Find longest consecutive sequence
        max_length = 1
        current_length = 1
        high_card = unique_values[0] if unique_values else 0
        
        for i in range(1, len(unique_values)):
            if unique_values[i] == unique_values[i-1] + 1:
                current_length += 1
                high_card = unique_values[i]
                max_length = max(max_length, current_length)
            elif unique_values[i] > unique_values[i-1] + 1:
                current_length = 1
        
        return {
            'max_length': max_length,
            'high_card': high_card,
            'ace_low_distance': ace_low_distance,
            'regular_distance': 5 - max_length
        }

    # Check if community cards alone can form a straight
    comm_result = check_straight(community_cards)
    if comm_result['max_length'] >= 5 or comm_result['ace_low_distance'] == 0:
        return (0, None)  # Straight exists without hole cards

    # Combine all cards
    all_cards = hole_cards + community_cards
    all_result = check_straight(all_cards)
    
    # Check if we can make a straight with hole cards
    if all_result['max_length'] >= 5 or all_result['ace_low_distance'] == 0:
        # Verify at least one card in the straight comes from hole cards
        hole_ranks = {card[1] for card in hole_cards}
        all_ranks = {card[1] for card in all_cards}
        
        # Regular straight
        if all_result['max_length'] >= 5:
            straight_ranks = set()
            unique_values = sorted({self.valueDict[rank] for rank in all_ranks})
            for i in range(len(unique_values)-4):
                if unique_values[i+4] - unique_values[i] == 4:
                    straight_ranks.update(
                        rank for rank in all_ranks 
                        if self.valueDict[rank] in unique_values[i:i+5]
                    )
                    break

        # Ace-low straight
        elif all_result['ace_low_distance'] == 0:
            straight_ranks = {"A", "2", "3", "4", "5"}
        
        # Check if any straight card is from hole cards
        if straight_ranks & hole_ranks:
            high_card = all_result['high_card']
            if high_card >= 10 or 'A' in straight_ranks:  
                return (1, "high" if high_card >= 10 else "low")
    
    # Calculate how many cards are missing because we know we cannot form the hand
    distance = min(all_result['regular_distance'], all_result['ace_low_distance'])
    
    # Determine if potential straight would be high or low
    if all_result['high_card'] >= 10:
        return (-distance, "high")
    else:
        return (-distance, "low")


  # 1 if we have a flush
  # negative number representing how many cards away we are from making a flush
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveFlush(self, hole_cards, community_cards):
    def evaluate_flush(cards):
        suit_counts = {"H": 0, "D": 0, "C": 0, "S": 0}
        suit_cards = {"H": [], "D": [], "C": [], "S": []}
        
        for card in cards:
            suit = card[0]
            suit_counts[suit] += 1
            suit_cards[suit].append(card)
        
        best_suit = max(suit_counts, key=suit_counts.get)
        max_count = suit_counts[best_suit]
        
        if max_count >= 5:
            high_count = sum(1 for card in suit_cards[best_suit] 
                         if self.valueDict[card[1]] >= 10)
            return (max_count, best_suit, high_count)
        return (max_count, None, 0)
    
    # Check if community cards alone can form a flush
    comm_count, comm_suit, comm_high = evaluate_flush(community_cards)
    if comm_count >= 5:
        return (0, None)  # Flush exists without hole cards
    
    # Combine all cards
    all_cards = hole_cards + community_cards
    all_count, all_suit, all_high = evaluate_flush(all_cards)
    
    if all_count >= 5:
        # Verify at least one card in flush comes from hole cards
        hole_suits = [card[0] for card in hole_cards]
        if all_suit in hole_suits:
            return (1, "high" if all_high > 0 else "low")
    
    # Calculate how many cards are missing because we know we cannot form the hand
    distance = 5 - all_count
    
    # Determine potential flush quality based on hole cards
    hole_high = sum(1 for card in hole_cards 
                   if card[0] == all_suit and self.valueDict[card[1]] >= 10)
    
    quality = "high" if hole_high > 0 else "low" if all_suit else None
    
    return (-distance, quality)


  # 1 if we have a full house
  # negative number representing how many cards away we are from making a full house
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveFullHouse(self, hole_cards, community_cards):
    def evaluate_full_house(cards):
        rank_counts = {}
        for _, rank in cards:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        # Sort by count then by rank value
        sorted_ranks = sorted(rank_counts.items(), 
                             key=lambda x: (-x[1], -self.valueDict[x[0]]))
        
        has_full_house = (len(sorted_ranks) >= 2 and 
                         sorted_ranks[0][1] >= 3 and 
                         sorted_ranks[1][1] >= 2)
        
        if has_full_house:
            three_rank, pair_rank = sorted_ranks[0][0], sorted_ranks[1][0]
            three_high = self.valueDict[three_rank] >= 10
            pair_high = self.valueDict[pair_rank] >= 10
            
            if three_high and pair_high:
                return (True, "highHigh")
            elif three_high or pair_high:
                return (True, "highLow")
            else:
                return (True, "lowLow")
        
        # Calculate how close we are to a full house
        if len(sorted_ranks) >= 2:
            if sorted_ranks[0][1] >= 3:
                missing = max(0, 2 - sorted_ranks[1][1])
                quality = "highHigh" if self.valueDict[sorted_ranks[0][0]] >= 10 else "highLow"
            elif sorted_ranks[0][1] == 2 and sorted_ranks[1][1] == 2:
                missing = 1
                quality = ("highHigh" if self.valueDict[sorted_ranks[0][0]] >= 10 or 
                          self.valueDict[sorted_ranks[1][0]] >= 10 else "highLow")
            else:
                missing = 3
                quality = "highLow" if self.valueDict[sorted_ranks[0][0]] >= 10 else "lowLow"
        else:
            missing = 5
            quality = "lowLow"
        
        return (False, missing, quality)
    
    # Check if community cards alone can form a full house
    comm_has, *comm_result = evaluate_full_house(community_cards)
    if comm_has:
        return (0, None) # Full house exists with community cards, return 0
    
    # Combine all cards
    all_cards = hole_cards + community_cards
    all_has, *all_result = evaluate_full_house(all_cards)
    
    if all_has:
        # Verify at least one card in the full house comes from hole cards
        hole_ranks = {card[1] for card in hole_cards}
        three_rank = next(r for r, cnt in all_result[0].items() if cnt >= 3)
        pair_rank = next(r for r, cnt in all_result[0].items() if cnt >= 2 and r != three_rank)
        
        if three_rank in hole_ranks or pair_rank in hole_ranks:
            return (1, all_result[1])
    
    # Calculate how many cards are missing because we know we cannot form the hand
    missing, quality = all_result if not all_has else (0, all_result[1])
    return (-missing, quality)


  # 1 if we have a straight flush
  # negative number representing how many cards away we are from making a straight flush
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveStraightFlush(self, hole_cards, community_cards):
    def evaluate_suit(suit_cards):
        if len(suit_cards) < 5:
            return (-(5 - len(suit_cards)), None)
        
        straight_result = self.haveStraight(suit_cards)
        if straight_result[0] == 1:
            return (1, straight_result[1])
        return straight_result
    
    # Check if community cards alone can form a straight flush
    for suit in ["H", "D", "C", "S"]:
        suited_comm = [card for card in community_cards if card[0] == suit]
        if len(suited_comm) >= 5:
            comm_result = self.haveStraight(suited_comm)
            if comm_result[0] == 1:
                return (0, None)  # Straight flush exists in community cards, return 0
    
    # Combine all cards
    best_result = (-5, None)
    
    for suit in ["H", "D", "C", "S"]:
        suited_all = [card for card in hole_cards + community_cards if card[0] == suit]
        current_result = evaluate_suit(suited_all)
        
        if current_result[0] == 1:
            # Verify at least one card comes from hole cards
            suited_hole = [card for card in hole_cards if card[0] == suit]
            if len(suited_hole) > 0:
                return (1, current_result[1])  
            else:
                best_result = max(best_result, (0, None))
        else:
            best_result = max(best_result, current_result)
    return best_result

  # 1 if we have a royal flush
  # negative number representing how many cards away we are from making a royal flush
  # Updated this function to also return 0 if the hand can be made with community cards
  def haveRoyalFlush(self, hole_cards, community_cards):
    def evaluate_royal_flush(suit_cards):
        royal_ranks = {"T", "J", "Q", "K", "A"}
        suit_ranks = {card[1] for card in suit_cards}
        missing = royal_ranks - suit_ranks
        return len(missing)
    
    # Check if community cards alone can form a royal flush
    for suit in ["H", "D", "C", "S"]:
        suited_comm = [card for card in community_cards if card[0] == suit]
        if len(suited_comm) >= 5:
            missing = evaluate_royal_flush(suited_comm)
            if missing == 0:
                return (0, None)  # Royal flush exists without hole cards, return 0
    
    # 2. Combine all cards
    best_missing = 5
    best_suit = None
    
    for suit in ["H", "D", "C", "S"]:
        suited_all = [card for card in hole_cards + community_cards if card[0] == suit]
        if len(suited_all) >= 5:
            missing = evaluate_royal_flush(suited_all)
            if missing < best_missing:
                best_missing = missing
                best_suit = suit
    
    # Determine return value
    if best_missing == 0:
        # Verify at least one card comes from hole cards
        suited_hole = [card for card in hole_cards if card[0] == best_suit]
        if any(card[1] in {"T", "J", "Q", "K", "A"} for card in suited_hole):
            return (1, "high")  # Royal flush with hole card contribution
        else:
            return (0, None)  # Royal flush exists but only from community cards
    
    return (-best_missing, "high")  # Return how many cards are missing

  def getAbstractState(self, allCards, street):

    # handle preflop separately
    if street == "preflop":
      return self.preFlopAbstraction(allCards)

    # default bucket
    bucket = "highCardLow"

    # highCardHigh
    for card in allCards:
      if self.valueDict[card[1]] >= 10:
        bucket = "highCardHigh"
        break

    # calulate what we have
    pair = self.haveOfAKind(allCards, 2)
    three = self.haveOfAKind(allCards, 3)
    four = self.haveOfAKind(allCards, 4)
    twoPair = self.haveTwoPair(allCards)
    straight = self.haveStraight(allCards)
    flush = self.haveFlush(allCards)
    fullHouse = self.haveFullHouse(allCards)
    straightFlush = self.haveStraightFlush(allCards)
    royalFlush = self.haveRoyalFlush(allCards)


    # pair
    if pair[0] == 1:
      if pair[1] == 'high':
        bucket = "pairHigh"
      else:
        bucket = "pairLow"


    # twoPair
    if twoPair[0] == 1:
      if twoPair[1] == 'highHigh':
        bucket = "twoPairHighHigh"
      elif twoPair[1] == 'highLow':
        bucket = "twoPairHighLow"
      else:
        bucket = "twoPairLowLow"


    # three of a kind
    if three[0] == 1:
      if three[1] == 'high':
        bucket = "threeHigh"
      else:
        bucket = "threeLow"
    

    # straight
    if straight == 1:
      if straight[0] == 'high':
        bucket = "straightHigh"
      else:
        bucket = "straightLow"
    # straight-1
    elif straight[0] == -1 and street == "turn" or street == "flop":
      if straight[1] == 'high':
        bucket = "straightHigh-1"
      else:
        bucket = "straightLow-1"
    # staight-2
    elif straight[0] == -2 and street == "flop":
      if straight[1] == 'high':
        bucket = "straightHigh-2"
      else:
        bucket = "straightLow-2"


    # flush
    if flush == 1:
      bucket = "flush"
    # flush-1
    elif flush == -1 and street == "turn" or street == "flop":
      bucket = "flush-1"
    # flush-2
    elif flush == -2 and street == "flop":
      bucket = "flush-2"


    # fullHouse
    if fullHouse == 1:
      if fullHouse[1] == 'highHigh':
        bucket = "fullHouseHighHigh"
      elif fullHouse[1] == 'highLow':
        bucket = "fullHouseHighLow"
      else:
        bucket = "fullHouseLowLow"

    # four of a kind
    if four[0] == 1:
      if four[1] == 'high':
        bucket = "fourHigh"
      else:
        bucket = "fourLow"


    # straightFlush
    if straightFlush == 1:
      bucket = "straightFlush"
    # straightFlush-1
    elif straightFlush == -1 and street == "turn" or street == "flop":
      bucket = "straightFlush-1"

    # royalFlush
    if royalFlush == 1:
      bucket = "royalFlush"
      
    
    return bucket






  # passes action onto poker engine
  # currently always raises if possible, otherwise calls
  def declare_action(self, valid_actions, hole_card, round_state):

    # increment the hand count
    self.hand_count += 1

    allCards = hole_card + round_state["community_card"]
    street = round_state["street"]

    #get of abstract state using cards and street
    abstractState = self.getAbstractState(allCards, street)

    # this is temporary. Later we will add code to use the abstract state in an implementation of MCTS
    return "raise" if "raise" in valid_actions else "call"
  





      

  def receive_game_start_message(self, game_info):
    # print("------------GAME_INFO----------")
    # pprint.pprint(game_info)
    # print("-------------------------------")
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    # print("------------ROUND_UPDATE----------")
    # pprint .pprint(round_state)
    # print("-------------------------------")
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

def setup_ai():
  return mctsPlayer2()
