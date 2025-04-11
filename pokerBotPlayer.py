from pypokerengine.players import BasePokerPlayer
from time import sleep
import random as rand
import pprint

class PokerBotPlayer(BasePokerPlayer):

  # initialize hand counter to track the number of hands played
  def __init__(self):
    self.hand_count = 0

  # for pairs, three of a kind & four of a kind
  # 1 if it exists
  # 0 if all cards are uncovered and it does not exist
  # TODO if not there but cards are uncovered, return the probability
  def haveOfAKind(self, cards, quantity):   # quantity = 2 for pairs, 3 for three of a kind, 4 for four of a kind
    if len(cards) < quantity:
      return 0.0
    
    for i in range(len(cards)-(quantity-1)):
      count = 1
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          count += 1
      if count == quantity:
        return 1.0
    return 0.0
  

  # 1 if we have two pair
  # 0 if all cards are uncovered and no two pair
  # TODO if no two pair rn but cards are covered, return the probability
  def haveTwoPair(self, cards):
    if len(cards) < 4:
      return 0.0
    
    # find first pair
    pairRank = None
    for i in range(len(cards)-1):
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          pairRank = cards[i][1]
          break
    
    if pairRank == None:
      return 0.0
    
    # find second pair
    for i in range(len(cards)-1):
      if cards[i][1] == pairRank:
        continue
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          return 1.0
    
    return 0.0
    

  # 1 if we have a straight
  # 0 if all cards are uncovered and no straight
  # TODO if no straight rn but cards are covered, return the probability
  def haveStraight(self, cards, valueDict):
    if len(cards) < 5:
      return 0.0
    
    # sort cards by value
    cards.sort(key=lambda x: valueDict[x[1]])

    streak = 1
    for i in range(len(cards)-1):
      # skip if same card
      if cards[i][1] == cards[i+1][1]:
        continue
      # check if next card is consecutive
      elif valueDict[cards[i+1][1]] == valueDict[cards[i][1]] + 1:
        streak += 1
        if streak == 5:
          return 1.0
      else:
        streak = 1

    # check for ace low straight (A-2-3-4-5)
    # ? could this be done more efficiently?
    if any(card[1] == "A" for card in cards) and \
        any(card[1] == "2" for card in cards) and \
        any(card[1] == "3" for card in cards) and \
        any(card[1] == "4" for card in cards) and \
        any(card[1] == "5" for card in cards):
        return 1.0
    
    return 0.0
  

  # 1 if we have a flush
  # 0 if all cards are uncovered and no flush
  # TODO if no flush rn but cards are covered, return the probability
  def haveFlush(self, cards):
    if len(cards) < 5:
      return 0.0
    
    suits = ["H", "D", "C", "S"]
    # count number of cards of each suit
    for suit in suits:
      count = 0
      for i in range(len(cards)):
        if cards[i][0] == suit:
          count += 1
      if count >= 5:
        return 1.0
      
    return 0.0

  
  # 1 if we have a full house
  # 0 if all cards are uncovered and no full house
  # TODO if no full house rn but cards are covered, return the probability
  def haveFullHouse(self, cards):
    if len(cards) < 5:
      return 0.0
    
    # find three of a kind
    threeRank = None
    for i in range(len(cards)-2):
      count = 1
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          count += 1
      if count >= 3:
        threeRank = cards[i][1]

    # fail if no three of a kind
    if threeRank is None:
      return 0.0
    
    # find pair separate from the three of a kind
    for i in range(len(cards)):
      if cards[i][1] == threeRank:
        continue
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          return 1.0
    
    return 0.0


  # 1 if we have a straight flush
  # 0 if all cards are uncovered and no straight flush
  # TODO if no straight flush rn but cards are covered, return the probability
  def haveStraightFlush(self, cards, valueDict):
    if len(cards) < 5:
        return 0.0
    
    # check each suit
    suits = ["H", "D", "C", "S"]
    for suit in suits:
        # get all cards of this suit
        suitedCards = [card for card in cards if card[0] == suit]
        
        # need at least 5 cards of same suit
        if len(suitedCards) >= 5:
            # sort cards by rank
            suitedCards.sort(key=lambda x: valueDict[x[1]])
            
            # check for straight
            streak = 1
            for i in range(len(suitedCards) - 1):
                # skip if same card
                if valueDict[suitedCards[i+1][1]] == valueDict[suitedCards[i][1]]:
                  continue
                # check if next card is consecutive
                elif valueDict[suitedCards[i+1][1]] == valueDict[suitedCards[i][1]] + 1:
                    streak += 1
                    if streak >= 5:
                        return 1.0
                else:
                    streak = 1
            
            # check for ace low straight (A-2-3-4-5)
            # ? could this be done more efficiently?
            if any(card[1] == "A" for card in suitedCards) and \
               any(card[1] == "2" for card in suitedCards) and \
               any(card[1] == "3" for card in suitedCards) and \
               any(card[1] == "4" for card in suitedCards) and \
               any(card[1] == "5" for card in suitedCards):
                return 1.0
    
    return 0.0
  
  
  # 1 if we have a royal flush
  # 0 if all cards are uncovered and no royal flush
  # TODO if no royal flush rn but cards are covered, return the probability
  def haveRoyalFlush(self, cards):
    if len(cards) < 5:
        return 0.0
    
    # check each suit
    suits = ["H", "D", "C", "S"]
    for suit in suits:
        # check if we have 10, J, Q, K, A all of the same suit
        if all(f"{suit}{rank}" in [f"{card[0]}{card[1]}" for card in cards] 
               for rank in ["T", "J", "Q", "K", "A"]):
            return 1.0
    
    return 0.0

  # determine if it does not cost extra to stay in the hand
  def can_call_for_free(self, valid_actions):
    for action in valid_actions:
        if action["action"] == "call":
            amount = action.get("amount", None)
            if amount == 0:
                return True
    return False

  # basic bluffing function that randomly bluffs every 20 hands
  def basic_bluff(self, valid_actions):
      if self.hand_count % 2 == 0:
          if rand.random() < .7:  # 70% chance to bluff, we may change this
              for action in valid_actions:
                  if action["action"] == "raise":
                      return action  
          for action in valid_actions:
              if action["action"] == "call":
                  return action
          return None

  # passes action onto poker engine
  # currently always raises if possible, otherwise calls
  def declare_action(self, valid_actions, hole_card, round_state):

    # increment the hand count
    self.hand_count += 1

    print(f"CARDS:\t{hole_card}")
    #print(f"ROUND_STATE:\t{round_state}")

    # calls the basic bluff function to check if we should bluff
    bluff_action = self.basic_bluff(valid_actions)
    if bluff_action:
        return bluff_action["action"]

    # sum card values to determine if we have high, mid, or low cards
    valueDict = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
        "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14
    }

    # sum the values of the 2 hole cards
    rank1 = hole_card[0][1]
    rank2 = hole_card[1][1]
    val1 = valueDict[rank1]
    val2 = valueDict[rank2]
    totalVal = val1 + val2

    allCards = hole_card + round_state["community_card"]

    # find probabilities of different hands
    pair = self.haveOfAKind(allCards, 2)
    three = self.haveOfAKind(allCards, 3)
    four = self.haveOfAKind(allCards, 4)
    twoPair = self.haveTwoPair(allCards)
    straight = self.haveStraight(allCards, valueDict)
    flush = self.haveFlush(allCards)
    fullHouse = self.haveFullHouse(allCards)
    straightFlush = self.haveStraightFlush(allCards, valueDict)
    royalFlush = self.haveRoyalFlush(allCards)

    ourHands = [1.0, pair, three, four, twoPair, straight, flush, fullHouse, straightFlush, royalFlush]

    # find probabilities of different hands using only community cards
    pairC = self.haveOfAKind(round_state["community_card"], 2)
    threeC = self.haveOfAKind(round_state["community_card"], 3)
    fourC = self.haveOfAKind(round_state["community_card"], 4)
    twoPairC = self.haveTwoPair(round_state["community_card"])
    straightC = self.haveStraight(round_state["community_card"], valueDict)
    flushC = self.haveFlush(round_state["community_card"])
    fullHouseC = self.haveFullHouse(round_state["community_card"])
    straightFlushC = self.haveStraightFlush(round_state["community_card"], valueDict)
    royalFlushC = self.haveRoyalFlush(round_state["community_card"])

    # array holding probabilities of different hands using only community cards
    # first element is 1.0 because we can always make a high card hand
    communityHands = [1.0, pairC, threeC, fourC, twoPairC, straightC, flushC, fullHouseC, straightFlushC, royalFlushC]

    # find best hand for us and community
    for i in range(len(ourHands)):
      if ourHands[i] == 1.0:
        ourBestHand = i
      if communityHands[i] == 1.0:
        communityBestHand = i


    # totalVal: 21-28 RAISE (if possible)
    if 24 <= totalVal or ourBestHand > communityBestHand:
        for i in valid_actions:
            if i["action"] == "raise":
                action = i["action"]
                return action  # action returned here is sent to the poker engine
      

    # totalVal: 19-24 CALL
    if 19 <= totalVal <= 24 or self.can_call_for_free(valid_actions):
        return "call"  # action returned here is sent to the poker engine
            
    # totalVal: 4-19 FOLD
    # ? What is the best threshold for folding? 4? 10? 14? Pros fold about 70% preflop
    else:
        return "fold"  # action returned here is sent to the poker engine

              


  def receive_game_start_message(self, game_info):
    print("------------GAME_INFO----------")
    pprint.pprint(game_info)
    print("-------------------------------")
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
  return pokerBotPlayer()
