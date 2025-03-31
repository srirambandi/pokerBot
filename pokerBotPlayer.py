from pypokerengine.players import BasePokerPlayer
from time import sleep
import random as rand
import pprint

class PokerBotPlayer(BasePokerPlayer):

  # for pairs, three of a kind & four of a kind
  # 1 if it exists
  # 0 if all cards are uncovered and it does not exist
  # TODO if not there but cards are uncovered, return the probability
  def haveOfAKind(self, cards, quantity):   # quantity = 2 for pairs, 3 for three of a kind, 4 for four of a kind
    if len(cards) < quantity:
      return 0.0
    
    for i in range(len(cards)):
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
    
    pairCount = 0
    for i in range(len(cards)):
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          pairCount += 1
          break

    if pairCount == 2:
      return 1.0
    else:
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
    for i in range(len(cards)-4):
      for j in range(i+1, len(cards)):
        if valueDict[cards[i+1][1]] == valueDict[cards[i][1]] + 1:
          streak += 1
          if streak == 5:
            return 1.0
        else:
          streak = 1
    return 0.0
  

  # 1 if we have a flush
  # 0 if all cards are uncovered and no flush
  # TODO if no flush rn but cards are covered, return the probability
  def haveFlush(self, cards):
    if len(cards) < 5:
      return 0.0
    
    hearts = 0
    diamonds = 0
    clubs = 0
    spades = 0
    for i in range(len(cards)):
      if cards[i][0] == "H":
        hearts += 1
      elif cards[i][0] == "D":
        diamonds += 1
      elif cards[i][0] == "C":
        clubs += 1
      elif cards[i][0] == "S":
        spades += 1

    if hearts >= 5 or diamonds >= 5 or clubs >= 5 or spades >= 5:
      return 1.0

  
  # 1 if we have a full house
  # 0 if all cards are uncovered and no full house
  # TODO if no full house rn but cards are covered, return the probability
  def haveFullHouse(self, cards):
    if len(cards) < 5:
      return 0.0
    
    # find three of a kind
    threeRank = None
    for i in range(len(cards)):
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
      count = 1
      for j in range(i+1, len(cards)):
        if cards[i][1] == cards[j][1]:
          count += 1
      if count >= 3:
        threeRank = cards[i][1]
    
    return 0.0
    
  # TODO implement straight flush
  def haveStraightFlush(self, cards):
    return 0.0
  
  # TODO implement royal flush
  def haveRoyalFlush(self, cards):
    return 0.0



  # passes action onto poker engine
  # currently always raises if possible, otherwise calls
  def declare_action(self, valid_actions, hole_card, round_state):

    print(f"CARDS:\t{hole_card}")
    # print(f"ROUND_STATE:\t{round_state}")

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
    straightFlush = 0.0
    royalFlush = 0.0

    # find probabilities of different hands using only community cards
    pairC = self.haveOfAKind(round_state["community_card"], 2)
    threeC = self.haveOfAKind(round_state["community_card"], 3)
    fourC = self.haveOfAKind(round_state["community_card"], 4)
    twoPairC = self.haveTwoPair(round_state["community_card"])
    straightC = self.haveStraight(round_state["community_card"], valueDict)
    flushC = self.haveFlush(round_state["community_card"])
    fullHouseC = self.haveFullHouse(round_state["community_card"])
    straightFlushC = 0.0
    royalFlushC = 0.0

    # totalVal: 21-28 RAISE (if possible)
    if totalVal >= 21:
        for i in valid_actions:
            if i["action"] == "raise":
                action = i["action"]
                return action  # action returned here is sent to the poker engine
      

    # totalVal: 13-20 CALL
    if 13 <= totalVal <= 20:
        return "call"  # action returned here is sent to the poker engine
            
    # totalVal: 4-12 FOLD
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
