#!/usr/bin/env python
import testhelper
import unittest
import random
from mockito import *
from src import euchre
from src import game

class CardTest(testhelper.TestCase):
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

class DeckTest(testhelper.TestCase):
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

class TrickTest(testhelper.TestCase):
	def setUp(self):
		self.cardTranslator = testhelper.createSingletonMock(euchre.CardTranslator)
		self.trick = euchre.Trick.getInstance(euchre.SUIT_NONE)
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]

	def _makeCardTranslatorPassThrough(self):
		self.cardTranslator.translateCard = lambda card: card

	def testAddingFirstCardSetsLedSuit(self):
		card = euchre.Card(euchre.SUIT_CLUBS, 5)
		translatedCard = euchre.Card(euchre.SUIT_SPADES, 5)
		when(self.cardTranslator).translateCard(card).thenReturn(translatedCard)
		self.assertEqual(euchre.SUIT_NONE, self.trick.getLedSuit())
		self.trick.add(self.players[2], card)
		self.assertEqual(translatedCard.suit, self.trick.getLedSuit())

	def testAddingSecondCardDoesNotChangeLedSuit(self):
		self._makeCardTranslatorPassThrough()
		self.trick.add(self.players[2], euchre.Card(euchre.SUIT_CLUBS, 5))
		self.trick.add(self.players[1], euchre.Card(euchre.SUIT_DIAMONDS, 8))
		self.assertEqual(euchre.SUIT_CLUBS, self.trick.getLedSuit())

	def testPlayerPlayingMoreThanOneCardThrowsException(self):
		self._makeCardTranslatorPassThrough()
		self.trick.add(self.players[0], euchre.Card(euchre.SUIT_CLUBS, 5))
		with self.assertRaises(game.GameRuleException):
			self.trick.add(self.players[0], euchre.Card(euchre.SUIT_DIAMONDS, 8))

	def testTrickIsCompleteOnce4PlayersHavePlayed(self):
		self._makeCardTranslatorPassThrough()
		self.assertFalse(self.trick.isComplete())
		cards = [euchre.Card(euchre.SUIT_CLUBS, 5), euchre.Card(euchre.SUIT_DIAMONDS, 8), euchre.Card(euchre.SUIT_CLUBS, 4), euchre.Card(euchre.SUIT_DIAMONDS, 7)]
		for i in range(len(cards)):
			self.trick.add(self.players[i], cards[i])
		self.assertTrue(self.trick.isComplete())

class CardTranslatorTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = euchre.CardTranslator.getInstance(self.trumpSuit)

	def setUp(self):
		self.card = euchre.Card(random.randint(1, 4), random.randint(9, 14))
		self.trumpSuit = random.randint(1, 4)
		self._buildTestObj()

	def testReturnsCardIfNotTrumpSuit(self):
		self.trumpSuit = self.card.suit + 1
		self._buildTestObj()
		self.assertEqual(self.card, self.testObj.translateCard(self.card))

	def testCorrectsValueIfJackOfTrumpSuit(self):
		self.trumpSuit = self.card.suit
		self.card.value = euchre.VALUE_JACK
		self._buildTestObj()
		expectedCard = euchre.Card.getInstance(self.trumpSuit, euchre.VALUE_RIGHT_BOWER)
		self.assertEqual(expectedCard, self.testObj.translateCard(self.card))

	def testCorrectsSuitAndValueIfJackOfSisterTrumpSuit(self):
		self.trumpSuit = ((self.card.suit + 1) % 4) + 1
		self.card.value = euchre.VALUE_JACK
		self._buildTestObj()
		expectedCard = euchre.Card.getInstance(self.trumpSuit, euchre.VALUE_LEFT_BOWER)
		self.assertEqual(expectedCard, self.testObj.translateCard(self.card))

	def testSetTrumpUpdatesTrumpSuit(self):
		self.trumpSuit = ((self.card.suit + 1) % 4) + 1
		self.card.value = euchre.VALUE_JACK
		self.testObj = euchre.CardTranslator.getInstance(euchre.SUIT_NONE)
		self.assertEqual(self.card, self.testObj.translateCard(self.card))
		self.testObj.setTrump(self.trumpSuit)
		expectedCard = euchre.Card.getInstance(self.trumpSuit, euchre.VALUE_LEFT_BOWER)
		self.assertEqual(expectedCard, self.testObj.translateCard(self.card))

class TrickEvaluatorTest(testhelper.TestCase):
	def setUp(self):
		self.evaluator = euchre.TrickEvaluator.getInstance()
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]

	def testCardOfTrumpSuitWinsAgainstNonTrumps(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_ACE), euchre.Card(euchre.SUIT_HEARTS, 2)]
		trumpSuit = euchre.SUIT_HEARTS
		trick = euchre.Trick.getInstance(trumpSuit)
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[-1], trick.getPlayedCards()[winner])

	def testCardOfLedSuitWinsAgainstNonLed(self):
		cards = [euchre.Card(euchre.SUIT_HEARTS, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_ACE)]
		trumpSuit = euchre.SUIT_NONE
		trick = euchre.Trick.getInstance(trumpSuit)
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[0], trick.getPlayedCards()[winner])

	def testHighestTrumpSuitCardWins(self):
		cards = [euchre.Card(euchre.SUIT_HEARTS, euchre.VALUE_ACE), euchre.Card(euchre.SUIT_SPADES, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING)]
		trumpSuit = euchre.SUIT_SPADES
		trick = euchre.Trick.getInstance(trumpSuit)
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[-1], trick.getPlayedCards()[winner])

	def testHighestLedSuitCardWins(self):
		cards = [euchre.Card(euchre.SUIT_HEARTS, 2), euchre.Card(euchre.SUIT_HEARTS, 10), euchre.Card(euchre.SUIT_HEARTS, euchre.VALUE_KING), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_ACE)]
		trumpSuit = euchre.SUIT_CLUBS
		trick = euchre.Trick.getInstance(trumpSuit)
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[-2], trick.getPlayedCards()[winner])

	def testLeftBowerBeatsLowerTrumps(self):
		cards = [euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_JACK), euchre.Card(euchre.SUIT_SPADES, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING)]
		trumpSuit = euchre.SUIT_SPADES
		trick = euchre.Trick.getInstance(trumpSuit)
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[0], trick.getPlayedCards()[winner])

	def testRightBowerBeatsOtherTrumps(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_JACK), euchre.Card(euchre.SUIT_SPADES, 2), euchre.Card(euchre.SUIT_SPADES, 10), euchre.Card(euchre.SUIT_SPADES, euchre.VALUE_KING)]
		trumpSuit = euchre.SUIT_SPADES
		trick = euchre.Trick.getInstance(trumpSuit)
		for i in range(len(cards)):
			trick.add(self.players[i], cards[i])
		self.evaluator.setTrump(trumpSuit)
		winner = self.evaluator.evaluateTrick(trick)
		self.assertEqual(cards[0], trick.getPlayedCards()[winner])

	def testGetTrumpReturnsSetTrump(self):
		trumpSuit = random.randint(1, 4)
		self.evaluator.setTrump(trumpSuit)
		self.assertEqual(trumpSuit, self.evaluator.getTrump())

class RoundTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.round = euchre.Round.getInstance(self.players, self.hands, self.trump)

	def setUp(self):
		self.trump = euchre.SUIT_CLUBS
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.deck = euchre.Deck(9)
		self.hands = {}
		self.handSize = euchre.HAND_SIZE
		for player in self.players:
			self.hands[player.playerId] = self.deck.deal(self.handSize)
		self.cardTranslator = testhelper.createSingletonMock(euchre.CardTranslator)
		self.cardTranslator.translateCard = lambda card: card
		self._buildTestObj()

	def testGetScoreReturns0IfPlayerHasNotWonTrick(self):
		self.assertEqual(0, self.round.getScore(self.players[0].playerId))

	def testPlayingCardRemovesItFromPlayersHand(self):
		card = self.round._hands[self.players[0].playerId][0]
		self.round.playCard(self.players[0], card)
		self.assertEqual(0, self.round._hands[self.players[0].playerId].count(card))

	def testPlayerNotInRoundPlayingCardThrowsException(self):
		otherPlayer = game.Player("5")
		card = self.round._hands[self.players[1].playerId][0]
		with self.assertRaises(game.InvalidPlayerException):
			self.round.playCard(otherPlayer, card)

	def testPlayerPlayingCardNotInTheirHandThrowsException(self):
		card = self.round._hands[self.players[2].playerId][1]
		with self.assertRaises(game.GameRuleException):
			self.round.playCard(self.players[0], card)

	def testPlayingCardAddsItToCurrentTrick(self):
		mockTrick = testhelper.createSingletonMock(euchre.Trick)
		when(mockTrick).getPlayedCards().thenReturn({})
		self.round._curTrick = mockTrick
		card = self.round._hands[self.players[0].playerId][2]
		self.round.playCard(self.players[0], card)
		verify(mockTrick).add(self.players[0], card)

	def testPlayingLastCardInTrickStartsNewTrick(self):
		firstTrick = self.round.getCurrentTrick()
		for player in self.players:
			self.round.playCard(player, self.round._hands[player.playerId][0])
		self.assertNotEqual(firstTrick, self.round.getCurrentTrick())
		self.assertEqual(1, self.round.prevTricks.count(firstTrick))

	def testCompletingTrickIncrementsScoreOfWinningPlayer(self):
		initialScores = {}
		for player in self.players:
			initialScores[player.playerId] = self.round.getScore(player.playerId)
		for player in self.players:
			self.round.playCard(player, self.round._hands[player.playerId][0])
		winner = self.round._trickEvaluator.evaluateTrick(self.round.prevTricks[0])
		for player in self.players:
			prevScore = initialScores[player.playerId]
			curScore = self.round.getScore(player.playerId)
			if winner == player.playerId:
				self.assertLess(prevScore, curScore)
			else:
				self.assertEqual(prevScore, curScore)

	def testRoundEndsWhenCorrectNumberOfTricksIsPlayed(self):
		for i in range(self.handSize):
			self.round._nextTrick()
		self.assertTrue(self.round.isComplete())

	def testDefaultsToPlayer0sTurn(self):
		self.assertEqual(self.players[0].playerId, self.round._turnTracker.getCurrentPlayerId())

	def testPlayingCardAdvancesPlayerTurn(self):
		self.round.playCard(self.players[0], self.round._hands[self.players[0].playerId][0])
		self.assertEqual(self.players[1].playerId, self.round._turnTracker.getCurrentPlayerId())

	def testCompletingTrickSetsTurnToWinningPlayer(self):
		for player in self.players:
			self.round.playCard(player, self.round._hands[player.playerId][0])
		winner = None
		for player in self.players:
			if self.round.getScore(player.playerId) > 0:
				winner = player
		self.assertEqual(winner.playerId, self.round._turnTracker.getCurrentPlayerId())

	def testPlayerPlayerOutOfTurnThrowsException(self):
		with self.assertRaises(game.GameRuleException):
			self.round.playCard(self.players[1], self.round._hands[self.players[1].playerId][0])

	def testScoreIsCorrectAfterACompleteRound(self):
		trickEvaluator = euchre.TrickEvaluator.getInstance(self.trump)
		scores = {}
		for player in self.players:
			scores[player.playerId] = 0
		for i in range(self.handSize):
			curTrick = euchre.Trick.getInstance(0)
			for offset in range(len(self.players)):
				curPlayer = self.players[self.round._turnTracker._currentIndex]
				curCard = self.round._hands[curPlayer.playerId][0]
				curTrick.add(curPlayer, curCard)
				self.round.playCard(curPlayer, curCard)
			winner = trickEvaluator.evaluateTrick(curTrick)
			scores[winner] += 1
		for player in self.players:
			self.assertEqual(scores[player.playerId], self.round.getScore(player.playerId))

	def testSettingTrumpOnRoundSetsTrumpOnTheTrickEvaluator(self):
		trickEvaluator = testhelper.createSingletonMock(euchre.TrickEvaluator)
		trump = euchre.SUIT_HEARTS
		self._buildTestObj()
		self.round.setTrump(trump)
		verify(trickEvaluator).setTrump(trump)

	def testGetTurnTrackerReturnsTheTurnTracker(self):
		turnTracker = testhelper.createSingletonMock(game.TurnTracker)
		self._buildTestObj()
		self.assertEqual(turnTracker, self.round.getTurnTracker())

	def testNotFollowingSuitThrowsException(self):
		firstCard = self.round._hands[self.players[0].playerId][0]
		self.round.playCard(self.players[0], firstCard)
		offSuit = firstCard.suit + 1
		if offSuit > euchre.SUIT_HEARTS:
			offSuit = euchre.SUIT_CLUBS
		self.round._hands[self.players[1].playerId][0].suit = offSuit
		self.round._hands[self.players[1].playerId][1].suit = firstCard.suit
		with self.assertRaises(game.GameRuleException):
			self.round.playCard(self.players[1], self.round._hands[self.players[1].playerId][0])

	def testGetTrumpReturnsValueFromTrickEvaluator(self):
		trickEvaluator = testhelper.createSingletonMock(euchre.TrickEvaluator)
		trump = random.randint(1, 4)
		when(trickEvaluator).getTrump().thenReturn(trump)
		self._buildTestObj()
		self.assertEqual(trump, self.round.getTrump())

	def testGetHandsReturnsHands(self):
		self.assertEqual(self.hands, self.round.getHands())

	def testAddCardToHandAddsCardToCorrectPlayersHand(self):
		player = random.choice(self.players)
		card = self.deck.peekTop()
		self.assertEqual(0, self.round.getHands()[player.playerId].count(card))
		self.round.addCardToHand(player, card)
		self.assertEqual(1, self.round.getHands()[player.playerId].count(card))

	def testAddCardToHandRaisesExceptionIfPlayerIdNotInRound(self):
		player = game.Player("5")
		card = self.deck.peekTop()
		with self.assertRaises(game.InvalidPlayerException):
			self.round.addCardToHand(player, card)

	def testDiscardCardRemovesCardFromCorrectPlayersHandButNotBelowMaxHandSize(self):
		player = random.choice(self.players)
		self.round.addCardToHand(player, self.deck.peekTop())
		card = random.choice(self.hands[player.playerId])
		self.assertEqual(1, self.round.getHands()[player.playerId].count(card))
		self.round.discardCard(player, card)
		self.assertEqual(0, self.round.getHands()[player.playerId].count(card))

		card = random.choice(self.round.getHands()[player.playerId])
		with self.assertRaises(game.GameRuleException):
			self.round.discardCard(player, card)

	def testDiscardCardRaisesExceptionIfPlayerIdNotInRound(self):
		player = game.Player("5")
		card = self.deck.peekTop()
		with self.assertRaises(game.InvalidPlayerException):
			self.round.discardCard(player, card)

	def testDiscardCardRaisesExceptionIfCardNotInHand(self):
		player = self.players[1]
		self.round.addCardToHand(player, self.deck.peekTop())
		card = random.choice(self.hands[self.players[0].playerId])
		with self.assertRaises(game.GameRuleException):
			self.round.discardCard(player, card)

class TrumpSelectorTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.availableTrump = euchre.SUIT_SPADES
		self.turnTracker = game.TurnTracker(self.players)
		self.trumpSelector = euchre.TrumpSelector(self.turnTracker, self.availableTrump)

	def testSelectingTrumpCompletesProcess(self):
		self.trumpSelector.selectTrump(self.players[0], self.trumpSelector.getAvailableTrump())
		self.assertTrue(self.trumpSelector.isComplete())
		self.assertEqual(self.trumpSelector.getAvailableTrump(), self.trumpSelector.getSelectedTrump())

	def testCanOnlySelectAvailableTrumpIfItIsSet(self):
		with self.assertRaises(game.GameRuleException):
			self.trumpSelector.selectTrump(self.players[0], euchre.SUIT_CLUBS)

	def testOnlyActivePlayerCanSelectTrump(self):
		with self.assertRaises(game.GameRuleException):
			self.trumpSelector.selectTrump(self.players[1], self.availableTrump)

	def testAnySuitCanBeSelectedIfNoTrumpIsAvailable(self):
		self.trumpSelector._availableTrump = euchre.SUIT_NONE
		self.trumpSelector.selectTrump(self.players[0], euchre.SUIT_HEARTS)
		self.assertEqual(euchre.SUIT_HEARTS, self.trumpSelector.getSelectedTrump())

	def testSelectingSuitNoneAdvancesTurnWithoutSettingTrump(self):
		self.trumpSelector.selectTrump(self.players[0], euchre.SUIT_NONE)
		self.assertEqual(self.players[1].playerId, self.trumpSelector._turnTracker.getCurrentPlayerId())
		self.assertEqual(euchre.SUIT_NONE, self.trumpSelector.getSelectedTrump())

	def testIsCompleteIfAllPlayersDeclineToSelectATrump(self):
		for player in self.players:
			self.trumpSelector.selectTrump(player, euchre.SUIT_NONE)
		self.assertTrue(self.trumpSelector.isComplete())

	def testResetResetsTurnTrackerAndClearsAvailableTrump(self):
		for player in self.players:
			self.trumpSelector.selectTrump(player, euchre.SUIT_NONE)
		self.trumpSelector.reset()
		self.assertEqual(self.players[0].playerId, self.trumpSelector._turnTracker.getCurrentPlayerId())
		self.assertEqual(euchre.SUIT_NONE, self.trumpSelector.getAvailableTrump())

	def testResetClearsSelectedTrump(self):
		self.trumpSelector.selectTrump(self.players[0], self.trumpSelector.getAvailableTrump())
		self.trumpSelector.reset()
		self.assertEqual(euchre.SUIT_NONE, self.trumpSelector.getSelectedTrump())

	def testSelectingTrumpRecordsIdOfSelectingPlayer(self):
		self.assertEqual(None, self.trumpSelector.getSelectingPlayerId())
		self.trumpSelector.selectTrump(self.players[0], self.trumpSelector.getAvailableTrump())
		self.assertEqual(self.players[0].playerId, self.trumpSelector.getSelectingPlayerId())

	def testGetTurnTrackerReturnsTheTurnTracker(self):
		self.assertEqual(self.turnTracker, self.trumpSelector.getTurnTracker())

class SequenceTest(testhelper.TestCase):
	def _createPlayersAndHands(self):
		self.deck = euchre.Deck(euchre.MIN_4_PLAYER_CARD_VALUE)
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.hands = {}
		for player in self.players:
			self.hands[player.playerId] = self.deck.deal(euchre.HAND_SIZE)
		self.upCard = self.deck.peekTop()

	def _createSequence(self):
		self.sequence = euchre.Sequence.getInstance(self.players, self.hands, self.upCard)

	def _createSequenceWithRealObjects(self):
		self._createPlayersAndHands()
		self.trumpSelector = euchre.TrumpSelector(game.TurnTracker(self.players), self.players)
		self.trickEvaluator = euchre.TrickEvaluator()
		self.round = euchre.Round(game.TurnTracker(self.players), self.trickEvaluator, self.players, self.hands)
		self._createSequence()

	def _createSequenceWithMocks(self):
		self._createPlayersAndHands()
		self.trumpSelector = testhelper.createSingletonMock(euchre.TrumpSelector)
		self.trickEvaluator = testhelper.createSingletonMock(euchre.TrickEvaluator)
		self.round = testhelper.createSingletonMock(euchre.Round)
		when(self.round).getHands().thenReturn(self.hands)
		self._createSequence()

	def setUp(self):
		self._createSequenceWithMocks()

	def _train(self, availableTrump=None, selectedTrump=None, trumpSelectorComplete=None, roundComplete=None):
		if None != availableTrump:
			when(self.trumpSelector).getAvailableTrump().thenReturn(availableTrump)
		if None != selectedTrump:
			when(self.trumpSelector).getSelectedTrump().thenReturn(selectedTrump)
		if None != trumpSelectorComplete:
			when(self.trumpSelector).isComplete().thenReturn(trumpSelectorComplete)
		if None != roundComplete:
			when(self.round).isComplete().thenReturn(roundComplete)

	def testDefaultsToTrumpSelection(self):
		self._train(selectedTrump=euchre.SUIT_NONE, trumpSelectorComplete=False, roundComplete=False)
		self.assertEqual(euchre.Sequence.STATE_TRUMP_SELECTION, self.sequence.getState())

	def testStateIsTrumpSelection2IfNoTrumpIsSelectedInFirstProcess(self):
		self._train(euchre.SUIT_NONE, euchre.SUIT_NONE, False, False)
		self.assertEqual(euchre.Sequence.STATE_TRUMP_SELECTION_2, self.sequence.getState())

	def testCanSelectTrumpWhileInTrumpSelection2(self):
		self._train(euchre.SUIT_NONE, euchre.SUIT_NONE, False, False)
		player = self.players[0]
		trump = euchre.SUIT_HEARTS
		self.sequence.selectTrump(player, trump)
		verify(self.trumpSelector).selectTrump(player, trump)

	def testAdvancesToRoundWhenTrumpSelectionIsSuccessfullyCompleted(self):
		self._train(selectedTrump=euchre.SUIT_DIAMONDS, trumpSelectorComplete=True, roundComplete=False)
		self.assertEqual(euchre.Sequence.STATE_PLAYING_ROUND, self.sequence.getState())

	def testAdvancesToDiscardWhenTrumpSelectionIsSuccessfullyCompletedAndAPlayerHasTooManyCards(self):
		dealerId = self.players[random.randrange(0, len(self.players))].playerId
		self.hands[dealerId].append(self.upCard)
		when(self.round).getHands().thenReturn(self.hands)
		self._createSequence()
		self._train(selectedTrump=euchre.SUIT_DIAMONDS, trumpSelectorComplete=True, roundComplete=False)
		self.assertEqual(euchre.Sequence.STATE_DISCARD, self.sequence.getState())

	def testSelectTrumpCallsSelectTrumpOnTrumpSelector(self):
		self._train(euchre.SUIT_CLUBS, euchre.SUIT_NONE, False)
		player = self.players[0]
		trump = euchre.SUIT_CLUBS
		self.sequence.selectTrump(player, trump)
		verify(self.trumpSelector).selectTrump(player, trump)

	def testSelectTrumpThrowsExceptionIfTrumpSelectionIsComplete(self):
		self._train(roundComplete=True)
		with self.assertRaises(game.GameStateException):
			self.sequence.selectTrump(self.players[0], euchre.SUIT_SPADES)

	def testPlayCardThrowsExceptionIfRoundIsComplete(self):
		self._train(trumpSelectorComplete=True, roundComplete=True)
		with self.assertRaises(game.GameStateException):
			self.sequence.playCard(self.players[0], self.hands[self.players[0].playerId][0])

	def testPlayCardThrowsExceptionIfInStateDiscard(self):
		dealerId = self.players[random.randrange(0, len(self.players))].playerId
		self.hands[dealerId].append(self.upCard)
		when(self.round).getHands().thenReturn(self.hands)
		self._createSequence()
		self._train(selectedTrump=euchre.SUIT_DIAMONDS, trumpSelectorComplete=True, roundComplete=False)
		with self.assertRaises(game.GameStateException):
			self.sequence.playCard(self.players[0], self.hands[self.players[0].playerId][0])

	def testPlayCardCallsPlayCardOnRound(self):
		self._train(trumpSelectorComplete=True, roundComplete=False)
		player = self.players[0]
		card = self.hands[player.playerId][0]
		self.sequence.playCard(player, card)
		verify(self.round).playCard(player, card)

	def testAllPlayersPassingOnTrumpSelectionResetsTrumpSelector(self):
		self._train(euchre.SUIT_SPADES, euchre.SUIT_NONE, True)
		self.sequence.selectTrump(self.players[-1].playerId, euchre.SUIT_NONE)
		verify(self.trumpSelector).reset()

	def testTrumpSelectionNotResetIfTrumpSelected(self):
		self._train(availableTrump=euchre.SUIT_SPADES)
		when(self.trumpSelector).getSelectedTrump().thenReturn(euchre.SUIT_NONE).thenReturn(euchre.SUIT_SPADES)
		self._train(trumpSelectorComplete=True)
		self.sequence.selectTrump(self.players[-1].playerId, euchre.SUIT_SPADES)
		verify(self.trumpSelector, never).reset()

	def testFailingSecondTrumpSelectionMakesStateTrumpSelectionFailed(self):
		self._train(euchre.SUIT_NONE, euchre.SUIT_NONE, True)
		self.assertEqual(euchre.Sequence.STATE_TRUMP_SELECTION_FAILED, self.sequence.getState())

	def testCompletingTrumpSelectionSetsTrumpOnRound(self):
		trump = euchre.SUIT_DIAMONDS
		self._train(availableTrump=trump, trumpSelectorComplete=True)
		when(self.trumpSelector).getSelectedTrump().thenReturn(euchre.SUIT_NONE).thenReturn(trump)
		self.sequence.selectTrump(self.players[-1].playerId, trump)
		verify(self.round).setTrump(trump)

	def testScoreCurrentRoundCallsIntoScoreTracker(self):
		callingPlayerId = "12345"
		scoreTracker = testhelper.createSingletonMock(euchre.ScoreTracker)
		when(self.trumpSelector).getSelectingPlayerId().thenReturn(callingPlayerId)
		self.sequence.scoreCurrentRound(scoreTracker)
		verify(scoreTracker).recordRoundScore(self.round, callingPlayerId)

	def testGetRoundReturnsCurrentRound(self):
		self.assertEqual(self.round, self.sequence.getRound())

	def testGetTrumpSelectorReturnsCurrentTrumpSelector(self):
		self.assertEqual(self.trumpSelector, self.sequence.getTrumpSelector())

	def testGetUpCardReturnsUpCard(self):
		self._train(selectedTrump=euchre.SUIT_NONE, trumpSelectorComplete=False, roundComplete=False)
		self.assertEqual(self.upCard, self.sequence.getUpCard())

	def testGetUpCardReturnsNoneIfNotInCorrectState(self):
		self._train(euchre.SUIT_NONE, euchre.SUIT_NONE, False, False)
		self.assertEqual(None, self.sequence.getUpCard())

	def testAddCardToHandPassesThoughIfInTrumpSelection(self):
		self._train(selectedTrump=euchre.SUIT_NONE, trumpSelectorComplete=False, roundComplete=False)
		player = self.players[random.randrange(0, len(self.players))]
		self.sequence.addCardToHand(player, self.upCard)
		verify(self.round).addCardToHand(player, self.upCard)

	def testAddCardToHandRaisesExceptionIfNotInTrumpSelection(self):
		self._train(euchre.SUIT_NONE, euchre.SUIT_NONE, False, False) #TRUMP_SELECTION_2
		player = self.players[random.randrange(0, len(self.players))]
		with self.assertRaises(game.GameStateException):
			self.sequence.addCardToHand(player, self.upCard)

	def testDiscardCardPassesThoughIfInDiscardState(self):
		dealerId = self.players[random.randrange(0, len(self.players))].playerId
		self.hands[dealerId].append(self.upCard)
		when(self.round).getHands().thenReturn(self.hands)
		self._createSequence()
		self._train(selectedTrump=euchre.SUIT_DIAMONDS, trumpSelectorComplete=True, roundComplete=False)

		player = self.players[random.randrange(0, len(self.players))]
		self.sequence.discardCard(player, self.upCard)
		verify(self.round).discardCard(player, self.upCard)

	def testDiscardCardRaisesExceptionIfNotInDiscardState(self):
		self._train(selectedTrump=euchre.SUIT_DIAMONDS, trumpSelectorComplete=True, roundComplete=False)

		player = self.players[random.randrange(0, len(self.players))]
		with self.assertRaises(game.GameStateException):
			self.sequence.discardCard(player, self.upCard)

class ScoreTrackerTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [
			[self.players[0].playerId, self.players[2].playerId],
			[self.players[1].playerId, self.players[3].playerId]
		]
		self.callingPlayerId = self.players[0].playerId
		self.scoreTracker = euchre.ScoreTracker(self.players, self.teams)
		self.round = testhelper.createSingletonMock(euchre.Round)
		when(self.round).isComplete().thenReturn(True)

	def testRecordRoundScoreGrants1PointToMakersTeamIfTheyGetMajorityOfTricks(self):
		scores = {
			self.players[0].playerId : 2,
			self.players[1].playerId : 1,
			self.players[2].playerId : 1,
			self.players[3].playerId : 1
		}
		for key, val in scores.iteritems():
			when(self.round).getScore(key).thenReturn(val)
		self.scoreTracker.recordRoundScore(self.round, self.callingPlayerId)
		self.assertEqual(1, self.scoreTracker.getTeamScore(0))
		self.assertEqual(0, self.scoreTracker.getTeamScore(1))

	def testRecordRoundScoreGrants2PointsToMakersTeamIfTheyWinAllTricks(self):
		scores = {
			self.players[0].playerId : 2,
			self.players[1].playerId : 0,
			self.players[2].playerId : 3,
			self.players[3].playerId : 0
		}
		for key, val in scores.iteritems():
			when(self.round).getScore(key).thenReturn(val)
		self.scoreTracker.recordRoundScore(self.round, self.callingPlayerId)
		self.assertEqual(2, self.scoreTracker.getTeamScore(0))
		self.assertEqual(0, self.scoreTracker.getTeamScore(1))

	def testRecordRoundScoreGrants2PointsToDefendersTeamIfTheyGetMajorityOfTricks(self):
		scores = {
			self.players[0].playerId : 2,
			self.players[1].playerId : 3,
			self.players[2].playerId : 0,
			self.players[3].playerId : 0
		}
		for key, val in scores.iteritems():
			when(self.round).getScore(key).thenReturn(val)
		self.scoreTracker.recordRoundScore(self.round, self.callingPlayerId)
		self.assertEqual(0, self.scoreTracker.getTeamScore(0))
		self.assertEqual(2, self.scoreTracker.getTeamScore(1))

	def testRecordRoundScoreThrowsExceptionIfIncompleteRoundIsPassedIn(self):
		when(self.round).isComplete().thenReturn(False)
		with self.assertRaises(game.GameStateException):
			self.scoreTracker.recordRoundScore(self.round, self.callingPlayerId)

	def testGetTeamsReturnsTeams(self):
		self.assertEqual(self.teams, self.scoreTracker.getTeams())

class GameTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.game = euchre.Game.getInstance(self.players, self.teams)

	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [
			[self.players[0].playerId, self.players[2].playerId],
			[self.players[1].playerId, self.players[3].playerId]
		]
		self.scoreTracker = testhelper.createSingletonMock(euchre.ScoreTracker)

		for teamId in range(len(self.teams)):
			for playerId in self.teams[teamId]:
				when(self.scoreTracker).getTeamIdFromPlayerId(playerId).thenReturn(teamId)
		when(self.scoreTracker).getTeams().thenReturn(self.teams)

		self._buildTestObj()

	def testStartGameShufflesDeck(self):
		actualDeck = euchre.Deck.getInstance()
		deck = testhelper.createSingletonMock(euchre.Deck)
		when(deck).deal(5).thenReturn(actualDeck.deal(5)).thenReturn(actualDeck.deal(5)).thenReturn(actualDeck.deal(5)).thenReturn(actualDeck.deal(5))
		when(deck).peekTop().thenReturn(actualDeck.peekTop())
		self._buildTestObj()
		self.game.startGame()
		verify(deck).shuffle()

	def testStartGameDealsCards(self):
		prevFactory = self.game._sequenceFactory
		self.game._sequenceFactory = testhelper.createMock(euchre.SequenceFactory)
		hands = {}
		def verifyHandSize(players, hands, topCard):
			for player in self.players:
				self.assertEqual(euchre.HAND_SIZE, len(hands[player.playerId]))
			self.assertTrue(topCard.suit > euchre.SUIT_NONE)
			self.assertTrue(topCard.suit <= euchre.NUM_SUITS)
			return prevFactory.buildSequence(player, hands, topCard)
		self.game._sequenceFactory.buildSequence = verifyHandSize
		self.game.startGame()

	def testStartGameCreatesASequence(self):
		self.game.startGame()
		self.assertIsNotNone(self.game.getSequence())

	def testPassesCallsThroughToSequence(self):
		sequence = testhelper.createSingletonMock(euchre.Sequence)
		trumpSuit = euchre.SUIT_CLUBS
		player = self.players[0]
		card = euchre.Card(euchre.SUIT_DIAMONDS, 10)
		state = "foo"
		when(sequence).getState().thenReturn(state)
		self.game.startGame()
		self.game.selectTrump(player, trumpSuit)
		self.game.playCard(player, card)
		verify(sequence).selectTrump(player, trumpSuit)
		verify(sequence).playCard(player, card)
		self.assertEqual(state, self.game.getSequenceState())

	def testPlayCardCreatesANewSequenceShufflesDeckAndAdvancesDealerIfCurrentOneIsComplete(self):
		initialPlayers = self.players[:]
		secondSequencePlayers = self.players[1:] + [self.players[0]]
		actualDeck = euchre.Deck.getInstance()
		deck = testhelper.createSingletonMock(euchre.Deck)
		when(deck).deal(5).thenReturn(actualDeck.deal(5)).thenReturn(actualDeck.deal(5)).thenReturn(actualDeck.deal(5)).thenReturn(actualDeck.deal(5))
		when(deck).peekTop().thenReturn(actualDeck.peekTop())
		sequenceFactory = testhelper.createSingletonMock(euchre.SequenceFactory)
		firstSequence = testhelper.createMock(euchre.Sequence)
		secondSequence = testhelper.createMock(euchre.Sequence)
		when(sequenceFactory).buildSequence(any(), any(), actualDeck.peekTop()).thenReturn(firstSequence).thenReturn(secondSequence)
		self._buildTestObj()
		self.game.startGame()
		sequence = self.game.getSequence()
		when(sequence).getState().thenReturn(euchre.Sequence.STATE_COMPLETE)
		self.game.playCard(self.players[0], euchre.Card(euchre.SUIT_CLUBS, 9))
		self.assertNotEqual(sequence, self.game.getSequence())
		verify(deck, times=2).shuffle()
		verify(sequenceFactory).buildSequence(initialPlayers, any(), any())
		verify(sequenceFactory).buildSequence(secondSequencePlayers, any(), any())

	def testPlayCardScoresRoundWhenCurSequenceIsComplete(self):
		callingPlayerId = self.players[1].playerId
		sequence = testhelper.createSingletonMock(euchre.Sequence)
		trumpSelector = testhelper.createSingletonMock(euchre.TrumpSelector)
		when(sequence).getState().thenReturn(euchre.Sequence.STATE_COMPLETE)
		when(trumpSelector).getSelectingPlayerId().thenReturn(callingPlayerId)
		self._buildTestObj()
		self.game.startGame()
		self.game.playCard(self.players[0], euchre.Card(euchre.SUIT_HEARTS, euchre.VALUE_JACK))
		verify(sequence).scoreCurrentRound(self.scoreTracker)

	def testGetPlayersReturnsPlayers(self):
		self.assertEqual(self.players, self.game.getPlayers())

	def testGetTeamScoreReturnsValueFromScoreTracker(self):
		teamScores = [random.randint(0, 11), random.randint(0, 11)]
		when(self.scoreTracker).getTeamScore(0).thenReturn(teamScores[0])
		when(self.scoreTracker).getTeamScore(1).thenReturn(teamScores[1])
		self.assertEqual(teamScores[0], self.game.getTeamScore(0))
		self.assertEqual(teamScores[1], self.game.getTeamScore(1))

	def testGetTeamFromPlayerIdReturnsValueFromScoreTracker(self):
		for teamId in range(len(self.teams)):
			for playerId in self.teams[teamId]:
				self.assertEqual(teamId, self.game.getTeamFromPlayerId(playerId))

	def testGetTeamListsReturnValueFromScoreTracker(self):
		self.assertEqual(self.teams, self.game.getTeamLists())

	def testAddCardToHandPassesThrough(self):
		sequence = testhelper.createSingletonMock(euchre.Sequence)
		sequenceFactory = testhelper.createSingletonMock(euchre.SequenceFactory)
		when(sequenceFactory).buildSequence(any(), any(), any()).thenReturn(sequence)
		player = self.players[random.randrange(0, len(self.players))]
		card = euchre.Card.getInstance(suit=random.randint(1,4), value=random.randint(9,14))
		self.game.startGame()
		self.game.addCardToHand(player, card)
		verify(sequence).addCardToHand(player, card)

	def testDiscardCardPassesThrough(self):
		sequence = testhelper.createSingletonMock(euchre.Sequence)
		sequenceFactory = testhelper.createSingletonMock(euchre.SequenceFactory)
		when(sequenceFactory).buildSequence(any(), any(), any()).thenReturn(sequence)
		player = self.players[random.randrange(0, len(self.players))]
		card = euchre.Card.getInstance(suit=random.randint(1,4), value=random.randint(9,14))
		self.game.startGame()
		self.game.discardCard(player, card)
		verify(sequence).discardCard(player, card)

if __name__ == "__main__":
	unittest.main()
