from pypokerengine.players import BasePokerPlayer
from time import sleep
import random as rand
import pprint

class PokerBotPlayer(BasePokerPlayer):

  # passes action onto poker engine
  # currently always raises if possible, otherwise calls
  def declare_action(self, valid_actions, hole_card, round_state):

    # print(f"CARDS:\t{hole_card}")

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
