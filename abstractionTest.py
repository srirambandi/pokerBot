from pypokerengine.players import BasePokerPlayer
from time import sleep
import random as rand
import pprint

class mctsPlayer(BasePokerPlayer):

    def __init__(self):
        # initialize hand counter to track the number of hands played
        self.handCount = 0
        # sum card values to determine if we have high, mid, or low cards
        self.valueDict = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
            "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14
        }

    #  take hole cards and return one of 8 abstract state buckets
    def preFlopAbstraction(self, holeCards):
        PRE_FLOP_CHART = [
            # A   K   Q   J   T   9   8   7   6   5   4  3  2
            [ 8,  8,  8,  8,  8,  7,  6,  5,  4,  4,  4, 4, 4], #A
            [ 8,  8,  8,  8,  8,  5,  4,  3,  3,  3,  2, 2, 2], #K
            [ 8,  6,  8,  8,  8,  5,  3,  2,  2,  2,  2, 2, 2], #Q
            [ 8,  5,  4,  8,  8,  5,  3,  2,  2,  2,  2, 2, 2], #J
            [ 6,  4,  3,  3,  8,  6,  3,  2,  2,  2,  2, 2, 2], #T
            [ 4,  1,  1,  1,  1,  8,  4,  2,  2,  2,  2, 2, 2], #9
            [ 4,  1,  1,  1,  1,  1,  8,  3,  2,  2,  2, 2, 2], #8
            [ 3,  1,  1,  1,  1,  1,  1,  8,  2,  2,  2, 2, 2], #7
            [ 3,  1,  1,  1,  1,  1,  1,  1,  7,  2,  2, 2, 2], #6
            [ 3,  1,  1,  1,  1,  1,  1,  1,  1,  7,  2, 2, 2], #5
            [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  6, 2, 2], #4
            [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, 5, 2], #3
            [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, 1, 4]  #2
        ]

        # assign ranks to cards
        RANK_ORDER = {
            "A": 0, "K": 1, "Q": 2, "J": 3, "T": 4, "9": 5,
            "8": 6, "7": 7, "6": 8, "5": 9, "4": 10, "3": 11, "2": 12
        }

        rank1 = holeCards[0][1]
        rank2 = holeCards[1][1]
        val1 = self.valueDict[rank1]
        val2 = self.valueDict[rank2]

        suited = False
        if holeCards[0][0] == holeCards[1][0]:  # Check if same suit
            suited = True

        if rank1 == rank2:  # Pairs
            row = RANK_ORDER[rank1]
            col = RANK_ORDER[rank2]
            return PRE_FLOP_CHART[row][col]
        elif suited:
            if val1 >= val2:
                row = RANK_ORDER[rank1]
                col = RANK_ORDER[rank2]
            else:
                row = RANK_ORDER[rank2]
                col = RANK_ORDER[rank1]
            return PRE_FLOP_CHART[row][col]
        else:
            if val1 <= val2:
                row = RANK_ORDER[rank1]
                col = RANK_ORDER[rank2]
            else:
                row = RANK_ORDER[rank2]
                col = RANK_ORDER[rank1]
            return PRE_FLOP_CHART[row][col]

    # for pairs, three of a kind & four of a kind
    # 1 if it exists
    # 0 if not
    def haveOfAKind(self, cards, quantity):
        if len(cards) < quantity:
            return (0, None)
        
        for i in range(len(cards)-(quantity-1)):
            count = 1
            for j in range(i+1, len(cards)):
                if cards[i][1] == cards[j][1]:
                    count += 1
            if count >= quantity:
                if self.valueDict[cards[i][1]] >= 10:
                    return (1, 'high')
                else:
                    return (1, 'low')
        # if we don't have the required quantity of cards, return 0
        return (0, None)

    # 1 if we have two pair
    # -1 if one card away from two pair, -2 if two cards away, -3 if three cards away
    def haveTwoPair(self, cards):
        # if we have two cards (preflop) we are always two cards away from two pair
        if len(cards) < 4:
            highCount = 0
            for card in cards:
                if self.valueDict[card[1]] >= 10:
                    highCount += 1

            if highCount > 1:
                return (-2, "highHigh")
            elif highCount == 1:
                return (-2, "highLow")
            else:
                return (-2, "lowLow")
            
        # track rank of each pair
        pairsRank = []

        # count occurrences of each rank
        rankCount = {}
        for card in cards:
            rank = card[1]
            if rank in rankCount:
                rankCount[rank] += 1
                if rankCount[rank] == 2:  # only add when it becomes a pair
                    pairsRank.append(self.valueDict[rank])
            else:
                rankCount[rank] = 1
            
        # count how many pairs we have
        pairCount = sum(1 for count in rankCount.values() if count >= 2)

        if pairCount >= 2:
            highPairCount = 0
            for rank in pairsRank:
                if rank >= 10:
                    highPairCount += 1
            if highPairCount > 1:
                return (1, "highHigh")
            elif highPairCount == 1:
                return (1, "highLow")
            else:
                return (1, "lowLow")
        elif pairCount == 1:
            if pairsRank[0] >= 10:
                return (-1, "highHigh")
            else:
                return (-1, "highLow")
        else:
            return (-2, "lowLow")  # we need two pairs

    # 1 if we have a straight
    # negative number representing how many cards away we are from making a straight
    def haveStraight(self, cards):
        if len(cards) < 5:
            return (-5, None)  # we need at least 5 cards to make a straight
        
        # extract unique ranks
        uniqueRanks = set()
        for card in cards:
            uniqueRanks.add(card[1])
        
        # check for Ace low straight (A-2-3-4-5)
        aceLowStraight = {"A", "2", "3", "4", "5"}
        missingForAceLow = aceLowStraight - uniqueRanks
        aceLowDistance = len(missingForAceLow)
        
        # sort cards by value
        uniqueValues = [self.valueDict[rank] for rank in uniqueRanks]
        uniqueValues.sort()
        
        # find longest consecutive sequence
        maxLength = 1
        currentLength = 1
        highCard = 0
        
        # convert to list to handle potential gaps
        values = list(uniqueValues)
        
        for i in range(1, len(values)):
            if values[i] == values[i-1] + 1:
                currentLength += 1
                highCard = max(highCard, values[i])
                maxLength = max(maxLength, currentLength)
            elif values[i] > values[i-1] + 1:
                # Found a gap
                currentLength = 1
                highCard = values[i]
        
        # Special check for Ace-low straight
        if aceLowDistance == 0:
            return (1, "low")  # A-2-3-4-5 is a low straight
        
        if maxLength >= 5:
            # Determine if it's a high straight
            if highCard >= 10:
                return (1, "high")
            else:
                return (1, "low")
        
        # Find distance to straight (cards needed)
        distance = 5 - maxLength
        
        # Return the minimum distance and classify as high or low
        if min(distance, aceLowDistance) == distance:
            if highCard >= 10:
                return (-distance, "high")
            else:
                return (-distance, "low")
        else:
            # Ace-low straight is typically considered low
            return (-aceLowDistance, "low")

    # 1 if we have a flush
    # negative number representing how many cards away we are from making a flush
    def haveFlush(self, cards):
        if len(cards) < 5:
            return (-5, None)  # we need at least 5 cards to make a flush
        
        suits = ["H", "D", "C", "S"]
        # count number of cards of each suit
        maxCount = 0
        bestSuit = None
        
        for suit in suits:
            count = 0
            for card in cards:
                if card[0] == suit:
                    count += 1
            if count > maxCount:
                maxCount = count
                bestSuit = suit
        
        if maxCount >= 5:
            # Determine if it's a high flush
            highCardCount = 0
            for card in cards:
                if card[0] == bestSuit and self.valueDict[card[1]] >= 10:
                    highCardCount += 1
            
            if highCardCount > 0:
                return (1, "high")
            else:
                return (1, "low")
        else:
            # Return negative distance
            return (-(5 - maxCount), None)  # flush quality not determined if we don't have it yet

    # 1 if we have a full house
    # negative number representing how many cards away we are from making a full house
    def haveFullHouse(self, cards):
        if len(cards) < 5:
            return (-5, None)  # we need at least 5 cards to make a full house
        
        # count occurrences of each rank
        rankCount = {}
        for card in cards:
            rank = card[1]
            if rank in rankCount:
                rankCount[rank] += 1
            else:
                rankCount[rank] = 1
        
        # sort ranks by count (descending)
        sortedRanks = sorted(rankCount.items(), key=lambda x: (-x[1], -self.valueDict[x[0]]))
        
        if len(sortedRanks) >= 2 and sortedRanks[0][1] >= 3 and sortedRanks[1][1] >= 2:
            # We have a full house, determine if high or low
            threeRank = sortedRanks[0][0]
            pairRank = sortedRanks[1][0]
            
            threeHigh = self.valueDict[threeRank] >= 10
            pairHigh = self.valueDict[pairRank] >= 10
            
            if threeHigh and pairHigh:
                return (1, "highHigh")
            elif threeHigh or pairHigh:
                return (1, "highLow")
            else:
                return (1, "lowLow")
        
        # calculate how many cards we need to make a full house
        if len(sortedRanks) >= 2:
            if sortedRanks[0][1] >= 3:
                # We have three of a kind, need another pair
                missingForPair = 2 - sortedRanks[1][1]
                threeHigh = self.valueDict[sortedRanks[0][0]] >= 10
                pairHigh = self.valueDict[sortedRanks[1][0]] >= 10
                
                if threeHigh and pairHigh:
                    return (-missingForPair, "highHigh")
                elif threeHigh or pairHigh:
                    return (-missingForPair, "highLow")
                else:
                    return (-missingForPair, "lowLow")
            elif sortedRanks[0][1] == 2 and sortedRanks[1][1] == 2:
                # We have two pairs, need one more card for three of a kind
                firstHigh = self.valueDict[sortedRanks[0][0]] >= 10
                secondHigh = self.valueDict[sortedRanks[1][0]] >= 10
                
                if firstHigh and secondHigh:
                    return (-1, "highHigh")
                elif firstHigh or secondHigh:
                    return (-1, "highLow")
                else:
                    return (-1, "lowLow")
            elif sortedRanks[0][1] == 2:
                # We have a pair, need one more for the pair and one more for three of a kind
                pairHigh = self.valueDict[sortedRanks[0][0]] >= 10
                
                if pairHigh:
                    return (-3, "highLow")
                else:
                    return (-3, "lowLow")
        elif len(sortedRanks) == 1:
            if sortedRanks[0][1] == 2:
                # We have one pair, need three more cards
                pairHigh = self.valueDict[sortedRanks[0][0]] >= 10
                
                if pairHigh:
                    return (-3, "highLow")
                else:
                    return (-3, "lowLow")
            elif sortedRanks[0][1] == 1:
                # We have one card of a kind, need four more cards
                cardHigh = self.valueDict[sortedRanks[0][0]] >= 10
                
                if cardHigh:
                    return (-4, "highLow")
                else:
                    return (-4, "lowLow")
        
        return (-5, None)  # worst case: need 5 cards to make a full house

    # 1 if we have a straight flush
    # negative number representing how many cards away we are from making a straight flush
    def haveStraightFlush(self, cards):
        if len(cards) < 5:
            return (-5, None)  # we need at least 5 cards to make a straight flush
        
        # check each suit
        suits = ["H", "D", "C", "S"]
        bestDistance = -5  # worst case
        bestQuality = None
        
        for suit in suits:
            # get all cards of this suit
            suitedCards = [card for card in cards if card[0] == suit]
            
            if len(suitedCards) >= 5:
                # We have enough cards of this suit for a straight flush
                # Check if we have a straight with these cards
                straightResult = self.haveStraight(suitedCards)
                if straightResult[0] == 1:
                    return (1, straightResult[1])  # we have a straight flush with the same quality
                elif straightResult[0] > bestDistance:
                    bestDistance = straightResult[0]
                    bestQuality = straightResult[1]
            else:
                # Not enough cards of this suit
                suitDistance = -(5 - len(suitedCards))
                if suitDistance > bestDistance:
                    bestDistance = suitDistance
                    # Quality is undetermined if we don't have enough cards
                    bestQuality = None
        
        return (bestDistance, bestQuality)

    # 1 if we have a royal flush
    # negative number representing how many cards away we are from making a royal flush
    def haveRoyalFlush(self, cards):
        if len(cards) < 5:
            return (-5, None)  # we need at least 5 cards to make a royal flush
        
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
                return (1, "high")  # Royal flush is always high
            
            distance = -missingCards
            if distance > bestDistance:
                bestDistance = distance
        
        return (bestDistance, "high")  # Royal flush is always categorized as high

    def getAbstractState(self, allCards, street):
        # handle preflop separately
        if street == "preflop":
            return self.preFlopAbstraction(allCards)

        # default bucket
        bucket = "highCardLow"

        # calculate what we have
        pair = self.haveOfAKind(allCards, 2)
        three = self.haveOfAKind(allCards, 3)
        four = self.haveOfAKind(allCards, 4)
        twoPair = self.haveTwoPair(allCards)
        straight = self.haveStraight(allCards)
        flush = self.haveFlush(allCards)
        fullHouse = self.haveFullHouse(allCards)
        straightFlush = self.haveStraightFlush(allCards)
        royalFlush = self.haveRoyalFlush(allCards)

        validBuckets = {
            "highCardLow": False, "highCardHigh": False,
            "pairLow": False, "pairHigh": False,
            "twoPairLowLow": False, "twoPairHighLow": False, "twoPairHighHigh": False,
            "threeLow": False, "threeHigh": False,
            "straightLow": False, "straightHigh": False,
            "straightLow-1": False, "straightHigh-1": False,
            "straightLow-2": False, "straightHigh-2": False,
            "flush": False, "flush-1": False, "flush-2": False,
            "fullHouseLowLow": False, "fullHouseHighLow": False, "fullHouseHighHigh": False,
            "fourLow": False, "fourHigh": False,
            "straightFlush": False, "straightFlush-1": False,
            "royalFlush": False
        }

        # highCard
        validBuckets["highCardLow"] = True
        for card in allCards:
            if self.valueDict[card[1]] >= 10:
                validBuckets["highCardHigh"] = True
                validBuckets["highCardLow"] = False
                break

        # pair
        if pair[0] == 1:
            if pair[1] == 'high':
                validBuckets["pairHigh"] = True
            else:
                validBuckets["pairLow"] = True

        # twoPair
        if twoPair[0] == 1:
            if twoPair[1] == 'highHigh':
                validBuckets["twoPairHighHigh"] = True
            elif twoPair[1] == 'highLow':
                validBuckets["twoPairHighLow"] = True
            else:
                validBuckets["twoPairLowLow"] = True

        # three of a kind
        if three[0] == 1:
            if three[1] == 'high':
                validBuckets["threeHigh"] = True
            else:
                validBuckets["threeLow"] = True
        
        # straight - FIX: Corrected how we check the straight result
        if straight[0] == 1:
            if straight[1] == 'high':
                validBuckets["straightHigh"] = True
            else:
                validBuckets["straightLow"] = True
        # straight-1
        elif straight[0] == -1 and (street == "turn" or street == "flop"):
            if straight[1] == 'high':
                validBuckets["straightHigh-1"] = True
            else:
                validBuckets["straightLow-1"] = True
        # straight-2
        elif straight[0] == -2 and street == "flop":
            if straight[1] == 'high':
                validBuckets["straightHigh-2"] = True
            else:
                validBuckets["straightLow-2"] = True

        # flush - FIX: Corrected how we check flush result
        if flush[0] == 1:
            validBuckets["flush"] = True
        # flush-1
        elif flush[0] == -1 and (street == "turn" or street == "flop"):
            validBuckets["flush-1"] = True
        # flush-2
        elif flush[0] == -2 and street == "flop":
            validBuckets["flush-2"] = True

        # fullHouse
        if fullHouse[0] == 1:
            if fullHouse[1] == 'highHigh':
                validBuckets["fullHouseHighHigh"] = True
            elif fullHouse[1] == 'highLow':
                validBuckets["fullHouseHighLow"] = True
            else:
                validBuckets["fullHouseLowLow"] = True

        # four of a kind
        if four[0] == 1:
            if four[1] == 'high':
                validBuckets["fourHigh"] = True
            else:
                validBuckets["fourLow"] = True

        # straightFlush - FIX: Corrected how we check straightFlush result
        if straightFlush[0] == 1:
            validBuckets["straightFlush"] = True
        # straightFlush-1
        elif straightFlush[0] == -1 and (street == "turn" or street == "flop"):
            validBuckets["straightFlush-1"] = True

        # royalFlush - FIX: Corrected how we check royalFlush result
        if royalFlush[0] == 1:
            validBuckets["royalFlush"] = True
            
        # go through the valid buckets and find the most valuable one
        if street == "flop":
            flopValueRanking = [
                "royalFlush", "straightFlush", "fourHigh", "fourLow",
                "fullHouseHighHigh", "fullHouseHighLow","fullHouseLowLow",
                "flush", "straightHigh", "straightLow", "threeHigh", "threeLow",
                "straightFlush-1", "flush-1", "twoPairHighHigh", "twoPairHighLow", "twoPairLowLow",
                "straightHigh-1", "straightLow-1", "pairHigh", "pairLow", "flush-2",
                "straightHigh-2", "straightLow-2", "highCardHigh", "highCardLow"
            ]
            # print(f"BUCKET VALUES: {validBuckets}")
            for i in flopValueRanking:
                if validBuckets[i]:
                    return i
                
        elif street == "turn":
            turnValueRanking = [
                "royalFlush", "straightFlush", "fourHigh", "fourLow",
                "fullHouseHighHigh", "fullHouseHighLow", "fullHouseLowLow",
                "flush", "straightHigh", "straightLow", "threeHigh", "threeLow",
                "twoPairHighHigh", "twoPairHighLow", "twoPairLowLow",
                "straightFlush-1", "flush-1", "straightHigh-1", "straightLow-1", 
                "pairHigh", "pairLow", "highCardHigh", "highCardLow"
            ]
            # print(f"BUCKET VALUES: {validBuckets}")
            for i in turnValueRanking:
                if validBuckets[i]:
                    return i
                
        else:  # river
            riverValueRanking = [
                "royalFlush", "straightFlush", "fourHigh", "fourLow",
                "fullHouseHighHigh", "fullHouseHighLow", "fullHouseLowLow",
                "flush", "straightHigh", "straightLow", "threeHigh","threeLow",
                "twoPairHighHigh", "twoPairHighLow","twoPairLowLow",
                "pairHigh", "pairLow", "highCardHigh", "highCardLow"
            ]
            # print(f"BUCKET VALUES: {validBuckets}")
            for i in riverValueRanking:
                if validBuckets[i]:
                    return i
        
        return "highCardLow"    # should never be reached, just in case

    # passes action onto poker engine
    # currently always raises if possible, otherwise calls
    def declareAction(self, validActions, holeCard, roundState):
        # increment the hand count
        self.handCount += 1

        allCards = holeCard + roundState["community_card"]
        street = roundState["street"]

        # get abstract state using cards and street
        abstractState = self.getAbstractState(allCards, street)

        # this is temporary. Later we will add code to use the abstract state in an implementation of MCTS
        return "raise" if "raise" in validActions else "call"

def main():
    # create an instance of the player
    player = mctsPlayer()

    # generate random cards
    suits = ["H", "D", "C", "S"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    communityCards = [(rand.choice(suits), rand.choice(ranks)) for _ in range(5)]
    holeCards = [(rand.choice(suits), rand.choice(ranks)) for _ in range(2)]


    # # manually set the hole and community cards for testing
    # communityCards = [('C', '3'), ('S', '5'), ('H', '4'), ('S', 'J'), ('H', '7')]
    # holeCards = [('S', 'A'), ('C', '2')]

    # example round state
    streetDict = {"preflop": 0, "flop": 3, "turn": 4, "river": 5}

    for street in streetDict:
        communityCardsShown = communityCards[:streetDict[street]]
        allCards = holeCards + communityCardsShown

        print(f"Street: {street}")
        print(f"Community Cards: {communityCardsShown}")
        print(f"Hole Cards: {holeCards}")

        # get abstract state
        abstractState = player.getAbstractState(allCards, street)
        print(f"Abstract State: {abstractState}\n")

main()