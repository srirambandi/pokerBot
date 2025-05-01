from enum import Enum


class NatureAction(Enum):
    SMALL_BLIND = "small_blind"
    BIG_BLIND = "big_blind"
    DEAL_HOLE_CARDS = "deal_hole_cards"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class PlayerAction(Enum):
    CALL = "call"
    RAISE = "raise"
    FOLD = "fold"


class MCTSNodeState(object):
    def __init__(self, hole_cards, community_cards, player_turn):
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.player_turn = player_turn


class MCTSNode(object):
    def __init__(self, state: MCTSNodeState, parent=None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value = 0
        self.is_end_game = False


class MCTSTree(object):
    def __init__(self):
        self.create_tree()

    def create_tree(self):
        root_state = MCTSNodeState(hole_cards=None, community_cards=None, player_turn=0)
        self.root = MCTSNode(state=root_state)
        self.root.children = {
            "small_blind": MCTSNode(state=MCTSNodeState(hole_cards=None, community_cards=None, player_turn=1), parent=self.root),
            "big_blind": MCTSNode(state=MCTSNodeState(hole_cards=None, community_cards=None, player_turn=1), parent=self.root),
        }
