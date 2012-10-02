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
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.turnTracker = game.TurnTracker(self.players)
		self.trickEvaluator = euchre.TrickEvaluator(self.trump)
		self.trickEvaluator.setTrump(self.trump)
		self.deck = euchre.Deck(9)
		self.hands = {}
		self.handSize = euchre.HAND_SIZE
		for player in self.players:
			self.hands[player.playerId] = self.deck.deal(self.handSize)
		self.round = euchre.Round(self.turnTracker, self.trickEvaluator, self.players, self.hands)

	def testGetScoreReturns0IfPlayerHasNotWonTrick(self):
		self.round.startRound()
		self.assertEqual(0, self.round.getScore(self.players[0].playerId))

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
		mockTrick = mock.create_autospec(euchre.Trick)
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
		initialScores = {}
		for player in self.players:
			initialScores[player.playerId] = self.round.getScore(player.playerId)
		for player in self.players:
			self.round.playCard(player, self.round.hands[player.playerId][0])
		winner = self.round._trickEvaluator.evaluateTrick(self.round.prevTricks[0])
		for player in self.players:
			prevScore = initialScores[player.playerId]
			curScore = self.round.getScore(player.playerId)
			if winner == player.playerId:
				self.assertLess(prevScore, curScore)
			else:
				self.assertEqual(prevScore, curScore)

	def testRoundEndsWhenCorrectNumberOfTricksIsPlayed(self):
		self.round.startRound()
		for i in range(self.handSize):
			self.round._nextTrick()
		self.assertTrue(self.round.isComplete())

	def testAfterStartingRoundItIsPlayer0sTurn(self):
		self.round.startRound()
		self.assertEqual(self.players[0].playerId, self.round._turnTracker.getCurrentPlayerId())

	def testPlayingCardAdvancesPlayerTurn(self):
		self.round.startRound()
		self.round.playCard(self.players[0], self.round.hands[self.players[0].playerId][0])
		self.assertEqual(self.players[1].playerId, self.round._turnTracker.getCurrentPlayerId())

	def testCompletingTrickSetsTurnToWinningPlayer(self):
		self.trickEvaluator.setTrump(euchre.SUIT_DIAMONDS)
		self.round.startRound()
		for player in self.players:
			self.round.playCard(player, self.round.hands[player.playerId][0])
		winner = None
		for player in self.players:
			if self.round.getScore(player.playerId) > 0:
				winner = player
		self.assertEqual(winner.playerId, self.round._turnTracker.getCurrentPlayerId())

	def testPlayerPlayerOutOfTurnThrowsException(self):
		self.round.startRound()
		with self.assertRaises(game.GameRuleException):
			self.round.playCard(self.players[1], self.round.hands[self.players[1].playerId][0])

	def testScoreIsCorrectAfterACompleteRound(self):
		self.round.startRound()
		trickEvaluator = euchre.TrickEvaluator(self.trump)
		scores = {}
		for player in self.players:
			scores[player.playerId] = 0
		for i in range(self.handSize):
			curTrick = euchre.Trick()
			for offset in range(len(self.players)):
				curPlayer = self.players[self.round._turnTracker._currentIndex]
				curCard = self.round.hands[curPlayer.playerId][0]
				curTrick.add(curPlayer, curCard)
				self.round.playCard(curPlayer, curCard)
			winner = trickEvaluator.evaluateTrick(curTrick)
			scores[winner] += 1
		for player in self.players:
			self.assertEqual(scores[player.playerId], self.round.getScore(player.playerId))

class TrumpSelectorTest(unittest.TestCase):
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

class SequenceTest(unittest.TestCase):
	def _createPlayersAndHands(self):
		self.deck = euchre.Deck(euchre.MIN_4_PLAYER_CARD_VALUE)
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.hands = {}
		for player in self.players:
			self.hands[player.playerId] = self.deck.deal(euchre.HAND_SIZE)

	def _createSequence(self):
		self.sequence = euchre.Sequence(self.trumpSelector, self.round, self.players)

	def _createSequenceWithRealObjects(self):
		self._createPlayersAndHands()
		self.trumpSelector = euchre.TrumpSelector(game.TurnTracker(self.players), self.players)
		self.trickEvaluator = euchre.TrickEvaluator()
		self.round = euchre.Round(game.TurnTracker(self.players), self.trickEvaluator, self.players, self.hands)
		self._createSequence()

	def _createSequenceWithMocks(self):
		self._createPlayersAndHands()
		self.trumpSelector = mock.create_autospec(euchre.TrumpSelector)
		self.trickEvaluator = mock.create_autospec(euchre.TrickEvaluator)
		self.round = mock.create_autospec(euchre.Round)
		self._createSequence()

	def setUp(self):
		self._createSequenceWithMocks()

	def testDefaultsToTrumpSelection(self):
		self.trumpSelector.isComplete.return_value = False
		self.trumpSelector.getSelectedTrump.return_value = None
		self.assertEqual(euchre.Sequence.STATE_TRUMP_SELECTION, self.sequence.getState())

	def testAdvancesToRoundWhenTrumpSelectionIsSuccessfullyCompleted(self):
		self.trumpSelector.isComplete.return_value = True
		self.trumpSelector.getSelectedTrump.return_value = euchre.SUIT_DIAMONDS
		self.assertEqual(euchre.Sequence.STATE_PLAYING_ROUND, self.sequence.getState())

class ScoreTrackerTest(unittest.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = {
			0 : [self.players[0].playerId, self.players[2].playerId],
			1 : [self.players[1].playerId, self.players[3].playerId]
		}
		self.callingPlayerId = self.players[0].playerId
		self.scoreTracker = euchre.ScoreTracker(self.players, self.teams)
		self.round = mock.create_autospec(euchre.Round)
		self.round.isComplete.return_value = True

	def testRecordRoundScoreGrants1PointToMakersTeamIfTheyGetMajorityOfTricks(self):
		scores = {
			self.players[0].playerId : 2,
			self.players[1].playerId : 1,
			self.players[2].playerId : 1,
			self.players[3].playerId : 1
		}
		self.round.getScore.side_effect = lambda playerId: scores[playerId]
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
		self.round.getScore.side_effect = lambda playerId: scores[playerId]
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
		self.round.getScore.side_effect = lambda playerId: scores[playerId]
		self.scoreTracker.recordRoundScore(self.round, self.callingPlayerId)
		self.assertEqual(0, self.scoreTracker.getTeamScore(0))
		self.assertEqual(2, self.scoreTracker.getTeamScore(1))

	def testRecordRoundScoreThrowsExceptionIfIncompleteRoundIsPassedIn(self):
		self.round.isComplete.return_value = False
		with self.assertRaises(game.GameStateException):
			self.scoreTracker.recordRoundScore(self.round, self.callingPlayerId)

class GameTest(unittest.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.game = euchre.Game()

if __name__ == "__main__":
	unittest.main()
