import random
from typing import Dict, List

from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.hand_evaluator import HandEvaluator


def calculate_equity(
    hole_cards: List[Card],
    community_cards: List[Card],
    num_opponents: int,
    simulations: int = 10000
) -> Dict[str, float]:
    used_ids = {c.to_id() for c in hole_cards + community_cards}
    wins = ties = losses = 0

    for _ in range(simulations):
        rem_ids = [cid for cid in range(1, 53) if cid not in used_ids]
        deck = Deck(deck_ids=rem_ids)
        random.shuffle(deck.deck)
        sim_comm = community_cards[:]
        for _ in range(5 - len(sim_comm)):
            sim_comm.append(deck.draw_card())

        opp_scores = []
        for _ in range(num_opponents):
            h1 = deck.draw_card()
            h2 = deck.draw_card()
            opp_scores.append(HandEvaluator.eval_hand([h1, h2], sim_comm))

        my_score = HandEvaluator.eval_hand(hole_cards, sim_comm)
        best_opp = max(opp_scores) if opp_scores else -1

        if my_score > best_opp:
            wins += 1
        elif my_score == best_opp:
            ties += 1
        else:
            losses += 1

    total = wins + ties + losses
    return { 'win': wins/total, 'tie': ties/total, 'loss': losses/total }


def hand_type_distribution(
    hole_cards: List[Card],
    community_cards: List[Card],
    simulations: int = 10000
) -> Dict[str, float]:
    if len(hole_cards) != 2:
        raise ValueError("Require exactly two hole cards")
    if not (0 <= len(community_cards) <= 5):
        raise ValueError("Community cards must be length 0–5")

    types = list(HandEvaluator.HAND_STRENGTH_MAP.values())
    counts: Dict[str, int] = {t: 0 for t in types}

    used_ids = {c.to_id() for c in hole_cards + community_cards}
    missing = 5 - len(community_cards)

    for _ in range(simulations):
        rem_ids = [cid for cid in range(1, 53) if cid not in used_ids]
        deck = Deck(deck_ids=rem_ids)
        random.shuffle(deck.deck)

        sim_comm = community_cards[:]
        for _ in range(missing):
            sim_comm.append(deck.draw_card())

        info = HandEvaluator.gen_hand_rank_info(hole_cards, sim_comm)
        hand_name = info['hand']['strength']
        counts[hand_name] += 1

    return {hand: count/simulations for hand, count in counts.items()}
