from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from pokerBotPlayer import PokerBotPlayer
from pokerBotPlayer_0_2_0 import PokerBotPlayer_0_2_0


#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=10)



config.register_player(name="Rando", algorithm=RandomPlayer())
config.register_player(name="Raiser", algorithm=RaisedPlayer())
# config.register_player(name="pokerBot_0_2_0", algorithm=PokerBotPlayer_0_2_0())
config.register_player(name="pokerBot", algorithm=PokerBotPlayer())




game_result = start_poker(config, verbose=1)

