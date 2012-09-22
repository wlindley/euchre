#!/usr/bin/env python
import unittest
import mock
import euchre
import game

class CardTest(unittest.TestCase):
	def setUp(self):
		self.card1 = euchre.Card()
		self.card2 = euchre.Card()

	def testCardsWithSameSuitAndValueAreEqual(self):
		self.card1.suit = euchre.SUIT_HEARTS
		self.card1.value = 9
		self.card2.suit = euchre.SUIT_HEARTS
		self.card2.value = 9
		self.assertEqual(self.card1, self.card2)

	def testCardsWithDifferentSuitAndValueAreNotEqual(self):
		self.card1.suit = euchre.SUIT_HEARTS
		self.card1.value = 9
		self.card2.suit = euchre.SUIT_CLUBS
		self.card2.value = 6
		self.assertNotEqual(self.card1, self.card2)

	def testAssigningCardChangesSuit(self):
		self.card1.suit = euchre.SUIT_HEARTS
		self.card1.value = 9
		self.card1 = euchre.Card(euchre.SUIT_SPADES, 2)
		self.assertEqual(euchre.SUIT_SPADES, self.card1.suit)
		self.assertEqual(2, self.card1.value)

class DeckTest(unittest.TestCase):
	def setUp(self):
		self.deck = euchre.Deck()

	def testDeckHas52CardsByDefault(self):
		self.assertEqual(euchre.NUM_CARDS_IN_DECK, len(self.deck.remainingCards))

	def testDeckHas13CardsOfEachSuit(self):
		suitCounts = [0 for i in range(euchre.SUIT_HEARTS + 1)]
		for card in self.deck.remainingCards:
			suitCounts[card.suit] += 1
		self.assertEqual(0, suitCounts[0])
		for i in range(1, euchre.NUM_SUITS + 1):
			self.assertEqual(euchre.NUM_CARDS_IN_SUIT, suitCounts[i])

	def testShuffleChangesOrderOfCards(self):
		prevDeck = self.deck.remainingCards[:]
		self.deck.shuffle()
		self.assertNotEqual(prevDeck, self.deck.remainingCards)

	def testShuffleDoesNotAlwaysGiveSameResult(self):
		self.deck.shuffle()
		prevDeck = self.deck.remainingCards[:]
		self.deck.shuffle()
		self.assertNotEqual(prevDeck, self.deck.remainingCards)

	def testCanBuildDeckWithCardValueRange(self):
		minValue = 6
		maxValue = euchre.VALUE_JACK
		self.deck = euchre.Deck(minValue=minValue, maxValue=maxValue)
		cardsPerSuit = maxValue - minValue + 1
		self.assertEqual(cardsPerSuit * euchre.NUM_SUITS, len(self.deck.remainingCards))
		for card in self.deck.remainingCards:
			self.assertTrue(card.value >= minValue and card.value <= maxValue)

	def testDealingCardRemovesItFromDeck(self):
		initialNumCards = len(self.deck.remainingCards)
		dealtCards = self.deck.deal(1)
		self.assertEqual(1, len(dealtCards))
		self.assertEqual(initialNumCards - 1, len(self.deck.remainingCards))
		self.assertEqual(0, self.deck.remainingCards.count(dealtCards[0]))

	def testDealingManyCardRemovesThemFromDeck(self):
		cardsToDeal = 5
		initialNumCards = len(self.deck.remainingCards)
		dealtCards = self.deck.deal(cardsToDeal)
		self.assertEqual(cardsToDeal, len(dealtCards))
		self.assertEqual(initialNumCards - cardsToDeal, len(self.deck.remainingCards))
		for dealtCard in dealtCards:
			self.assertEqual(0, self.deck.remainingCards.count(dealtCard))

class HandTest(unittest.TestCase):
	def setUp(self):
		self.hand = euchre.Hand()

	def testHandContainsCardsAddedToIt(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 8), euchre.Card(euchre.SUIT_HEARTS, 3), euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_KING)]
		self.hand.add(cards)
		for card in cards:
			self.assertEqual(1, self.hand._cards.count(card))

	def testPlayingCardRemovesItFromHand(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 8), euchre.Card(euchre.SUIT_HEARTS, 3), euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_KING)]
		self.hand.add(cards)
		self.hand.play(cards[1])
		self.assertEqual(1, self.hand._cards.count(cards[0]))
		self.assertEqual(0, self.hand._cards.count(cards[1]))
		self.assertEqual(1, self.hand._cards.count(cards[2]))

	def testGetCardsReturnsListOfCardsInHand(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 8), euchre.Card(euchre.SUIT_HEARTS, 3), euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_KING)]
		self.hand.add(cards)
		cardList = self.hand.getCards()
		self.assertEqual(cards, cardList)

class TrickTest(unittest.TestCase):
	def setUp(self):
		self.trick = euchre.Trick()
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]

	def testAddingFirstCardSetsLedSuit(self):
		self.assertEqual(None, self.trick.ledSuit)
		self.trick.add(self.players[2], euchre.Card(euchre.SUIT_CLUBS, 5))
		self.assertEqual(euchre.SUIT_CLUBS, self.trick.ledSuit)

	def testAddingSecondCardDoesNotChangeLedSuit(self):
		self.trick.add(self.players[2], euchre.Card(euchre.SUIT_CLUBS, 5))
		self.trick.add(self.players[1], euchre.Card(euchre.SUIT_DIAMONDS, 8))
		self.assertEqual(euchre.SUIT_CLUBS, self.trick.ledSuit)

	def testPlayerPlayingMoreThanOneCardThrowsException(self):
		self.trick.add(self.players[0], euchre.Card(euchre.SUIT_CLUBS, 5))
		with self.assertRaises(game.GameRuleException):
			self.trick.add(self.players[0], euchre.Card(euchre.SUIT_DIAMONDS, 8))

	def testTrickIsCompleteOnce4PlayersHavePlayed(self):
		self.assertFalse(self.trick.isComplete())
		cards = [euchre.Card(euchre.SUIT_CLUBS, 5), euchre.Card(euchre.SUIT_DIAMONDS, 8), euchre.Card(euchre.SUIT_CLUBS, 4), euchre.Card(euchre.SUIT_DIAMONDS, 7)]
		for i in range(len(cards)):
			self.trick.add(self.players[i], cards[i])
		self.assertTrue(self.trick.isComplete())

class TrickEvaluatorTest(unittest.TestCase):
	def setUp(self):
		self.evaluator = euchre.TrickEvaluator()
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]

	def testCardOfTrumpSuitWinsAgainstNonTrumps(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_ACE), euchre.Card(euchre.SUIT_HEARTS, 2)]
		trick = euchre.Trick()
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		trumpSuit = euchre.SUIT_HEARTS
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[-1], trick.playedCards[winner])

	def testCardOfLedSuitWinsAgainstNonLed(self):
		cards = [euchre.Card(euchre.SUIT_HEARTS, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_ACE)]
		trick = euchre.Trick()
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		trumpSuit = euchre.SUIT_NONE
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[0], trick.playedCards[winner])

	def testHighestTrumpSuitCardWins(self):
		cards = [euchre.Card(euchre.SUIT_HEARTS, euchre.VALUE_ACE), euchre.Card(euchre.SUIT_SPADES, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING)]
		trick = euchre.Trick()
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		trumpSuit = euchre.SUIT_SPADES
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[-1], trick.playedCards[winner])

	def testHighestLedSuitCardWins(self):
		cards = [euchre.Card(euchre.SUIT_HEARTS, 2), euchre.Card(euchre.SUIT_HEARTS, 10), euchre.Card(euchre.SUIT_HEARTS, euchre.VALUE_KING), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_ACE)]
		trick = euchre.Trick()
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		trumpSuit = euchre.SUIT_CLUBS
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[-2], trick.playedCards[winner])

	def testLeftBowerBeatsLowerTrumps(self):
		cards = [euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_JACK), euchre.Card(euchre.SUIT_SPADES, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING)]
		trick = euchre.Trick()
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		trumpSuit = euchre.SUIT_SPADES
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[0], trick.playedCards[winner])

	def testRightBowerBeatsOtherTrumps(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_JACK), euchre.Card(euchre.SUIT_SPADES, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING)]
		trick = euchre.Trick()
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		trumpSuit = euchre.SUIT_SPADES
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[0], trick.playedCards[winner])

class RoundTest(unittest.TestCase):
	def setUp(self):
		self.trump = euchre.SUIT_CLUBS
		self.trickEvaluator = euchre.TrickEvaluator()
		self.trickEvaluator.setTrump(self.trump)
		self.deck = euchre.Deck(9)
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.round = euchre.Round(self.trickEvaluator, self.deck, self.players)

	def testStartingRoundDealsAllCardsToPlayersAndAllHaveSameHandSize(self):
		numCards = len(self.deck.remainingCards)
		self.round.startRound()
		self.assertEqual(len(self.players), len(self.round.hands))
		handSizes = [len(hand) for playerId, hand in self.round.hands.iteritems()]
		self.assertEqual(numCards, sum(handSizes))
		for handSize in handSizes:
			self.assertEqual(handSizes[0], handSize)

	def testStartingRoundTwiceDoesNotRedeal(self):
		self.round.startRound()
		curHands = [(playerId, hand[:]) for playerId, hand in self.round.hands.iteritems()]
		self.round.startRound()
		for i in range(len(curHands)):
			self.assertEqual(curHands[i][1], self.round.hands[curHands[i][0]])

	def testPlayingCardRemovesItFromPlayersHand(self):
		self.round.startRound()
		card = self.round.hands[self.players[0].playerId][0]
		self.round.playCard(self.players[0], card)
		self.assertEqual(0, self.round.hands[self.players[0].playerId].count(card))

	def testPlayerNotInRoundPlayingCardThrowsException(self):
		self.round.startRound()
		otherPlayer = game.Player("5")
		card = self.round.hands[self.players[1].playerId][0]
		with self.assertRaises(game.InvalidPlayerException):
			self.round.playCard(otherPlayer, card)

	def testPlayerPlayingCardNotInTheirHandThrowsException(self):
		self.round.startRound()
		card = self.round.hands[self.players[2].playerId][1]
		with self.assertRaises(game.GameRuleException):
			self.round.playCard(self.players[0], card)

	def testPlayingCardAddsItToCurrentTrick(self):
		self.round.startRound()
		mockTrick = mock.Mock(euchre.Trick)
		mockTrick.playedCards = {}
		self.round.curTrick = mockTrick
		card = self.round.hands[self.players[0].playerId][2]
		self.round.playCard(self.players[0], card)
		mockTrick.add.assert_called_with(self.players[0], card)

	def testPlayingLastCardInTrickStartsNewTrick(self):
		self.round.startRound()
		firstTrick = self.round.curTrick
		for player in self.players:
			self.round.playCard(player, self.round.hands[player.playerId][0])
		self.assertNotEqual(firstTrick, self.round.curTrick)
		self.assertEqual(1, self.round.prevTricks.count(firstTrick))

	def testCompletingTrickIncrementsScoreOfWinningPlayer(self):
		self.round.startRound()
		initialScores = self.round.scores.copy()
		for player in self.players:
			self.round.playCard(player, self.round.hands[player.playerId][0])
		winner = self.round._trickEvaluator.evaluateTrick(self.round.prevTricks[0])
		for player in self.players:
			prevScore = initialScores[player.playerId] if player.playerId in initialScores else 0
			curScore = self.round.scores[player.playerId] if player.playerId in self.round.scores else 0
			if winner == player.playerId:
				self.assertLess(prevScore, curScore)
			else:
				self.assertEqual(prevScore, curScore)

	def testRoundEndsWhenAtLeastOnePlayersHandIsEmpty(self):
		self.round.startRound()
		self.assertFalse(self.round.isComplete())
		while 0 < len(self.round.hands[self.players[0].playerId]):
			for player in self.players:
				self.round.playCard(player, self.round.hands[player.playerId][0])
		self.assertEqual(0, len(self.round.hands[self.players[0].playerId]))
		self.assertTrue(self.round.isComplete())

	def testAfterStartingRoundItIsPlayer0sTurn(self):
		self.round.startRound()
		self.assertEqual(self.players[0].playerId, self.round.getCurrentPlayerId())

	def testPlayingCardAdvancesPlayerTurn(self):
		self.round.startRound()
		self.round.playCard(self.players[0], self.round.hands[self.players[0].playerId][0])
		self.assertEqual(self.players[1].playerId, self.round.getCurrentPlayerId())

if __name__ == "__main__":
	unittest.main()
