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
      return -4  # we need at least 4 cards to make two pair
		
		# count occurrences of each rank
    rankCount = {}
    for card in cards:
      rank = card[1]
      if rank in rankCount:
        rankCount[rank] += 1
      else:
        rankCount[rank] = 1
		
    # count how many pairs we have
    pairCount = sum(1 for count in rankCount.values() if count >= 2)

    if pairCount >= 2:
      return 1.0  # we have at least two pairs
    elif pairCount == 1:
      return -1  # we need one more pair
    else:
      return -2  # we need two pairs
    

  # 1 if we have a straight
  # 0 if all cards are uncovered and no straight
  # TODO if no straight rn but cards are covered, return the probability
  def haveStraight(self, cards, valueDict):
    if len(cards) < 5:
      return -5  # we need at least 5 cards to make a straight
    
    # extract unique ranks
    uniqueRanks = set()
    for card in cards:
      uniqueRanks.add(card[1])
    
    # check for Ace low straight (A-2-3-4-5)
    aceLowStraight = {"A", "2", "3", "4", "5"}
    missingForAceLow = aceLowStraight - uniqueRanks
    aceLowDistance = len(missingForAceLow)
    
    # sort cards by value
    uniqueValues = [valueDict[rank] for rank in uniqueRanks]
    uniqueValues.sort()
    
    # find longest consecutive sequence
    maxLength = 1
    currentLength = 1
    
    # convert to list to handle potential gaps
    values = list(uniqueValues)
    
    for i in range(1, len(values)):
      if values[i] == values[i-1] + 1:
        currentLength += 1
        maxLength = max(maxLength, currentLength)
      elif values[i] > values[i-1] + 1:
        # Found a gap
        currentLength = 1
    
    if maxLength >= 5:
      return 1.0  # we have a straight
    
    # Find distance to straight (cards needed)
    distance = 5 - maxLength
    
    # Return the minimum distance (either for the regular straight or ace-low straight)
    return -min(distance, aceLowDistance)
  

  # 1 if we have a flush
  # 0 if all cards are uncovered and no flush
  # TODO if no flush rn but cards are covered, return the probability
  def haveFlush(self, cards):
    if len(cards) < 5:
      return -5  # we need at least 5 cards to make a flush
    
    suits = ["H", "D", "C", "S"]
    # count number of cards of each suit
    maxCount = 0
    for suit in suits:
      count = sum(1 for card in cards if card[0] == suit)
      maxCount = max(maxCount, count)
      
    if maxCount >= 5:
      return 1.0  # we have a flush
    else:
      return -(5 - maxCount)  # return negative distance to making a flush
	

  # 1 if we have a full house
  # negative number representing how many cards away we are from making a full house
  def haveFullHouse(self, cards):
    if len(cards) < 5:
      return -5  # we need at least 5 cards to make a full house
    
    # count occurrences of each rank
    rankCount = {}
    for card in cards:
      rank = card[1]
      if rank in rankCount:
        rankCount[rank] += 1
      else:
        rankCount[rank] = 1
    
    # sort counts in descending order
    counts = sorted(rankCount.values(), reverse=True)
    
    if len(counts) >= 2 and counts[0] >= 3 and counts[1] >= 2:
      return 1.0  # we have a full house
    
    # calculate how many cards we need to make a full house
    if len(counts) >= 2:
      if counts[0] >= 3:
        # We have three of a kind, need another pair
        if counts[1] == 1:
          return -1  # need one more card for the pair
        else:
          return -2  # need two cards for the pair
      elif counts[0] == 2 and counts[1] == 2:
        return -1  # we have two pairs, need one more card for three of a kind
      elif counts[0] == 2:
        return -3  # we have a pair, need one more for the pair and one more for three of a kind
    elif len(counts) == 1:
      if counts[0] == 2:
        return -3  # we have one pair, need three more cards
      elif counts[0] == 1:
        return -4  # we have one card of a kind, need four more cards
    
    return -5  # worst case: need 5 cards to make a full house


  # 1 if we have a straight flush
  # negative number representing how many cards away we are from making a straight flush
  def haveStraightFlush(self, cards, valueDict):
    if len(cards) < 5:
      return -5  # we need at least 5 cards to make a straight flush
    
    # check each suit
    suits = ["H", "D", "C", "S"]
    bestDistance = -5  # worst case
    
    for suit in suits:
      # get all cards of this suit
      suitedCards = [card for card in cards if card[0] == suit]
      
      if len(suitedCards) >= 5:
        # We have enough cards of this suit for a straight flush
        # Check if we have a straight with these cards
        straightResult = self.haveStraight(suitedCards, valueDict)
        if straightResult == 1.0:
          return 1.0  # we have a straight flush
        elif straightResult > bestDistance:
          bestDistance = straightResult  # update the best distance so far
      else:
        # Not enough cards of this suit
        suitDistance = -(5 - len(suitedCards))
        if suitDistance > bestDistance:
          bestDistance = suitDistance  # update the best distance so far
    
    return bestDistance


  # 1 if we have a royal flush
  # negative number representing how many cards away we are from making a royal flush
  def haveRoyalFlush(self, cards):
    if len(cards) < 5:
      return -5  # we need at least 5 cards to make a royal flush
    
    # check each suit
    suits = ["H", "D", "C", "S"]
    bestDistance = -5  # worst case
    
    for suit in suits:
      royalRanks = ["T", "J", "Q", "K", "A"]
      # Check which royal cards we have for this suit
      missingCards = 0
      for rank in royalRanks:
        if not any(card[0] == suit and card[1] == rank for card in cards):
          missingCards += 1
      
      if missingCards == 0:
        return 1.0  # we have a royal flush
      
      distance = -missingCards
      if distance > bestDistance:
        bestDistance = distance  # update the best distance so far
    
    return bestDistance

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
    # print(f"ROUND_STATE:\t{round_state}")

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

    street = round_state["street"]
    streetDict = {
        "preflop": 5, "flop": 2, "turn": 1, "river": 0
    }
    faceDownCount = streetDict[street]

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
        # TODO dont fold if there are covered cards and we are close to a good hand
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
