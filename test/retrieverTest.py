#!/usr/bin/env python
import testhelper
import json
import random
from mockito import *

from src import euchre
from src import model
from src import game
from src import retriever

class DealerRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = retriever.DealerRetriever.getInstance()

	def testRetrieveDealerReturnsCorrectResult(self):
		gameObj = testhelper.createMock(euchre.Game)
		players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		when(gameObj).getPlayers().thenReturn(players)

		actualResult = self.testObj.retrieveDealer(gameObj)
		self.assertEqual(players[0].playerId, actualResult)

class HandRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [["1", "2"], ["3", "4"]]
		self.game = euchre.Game.getInstance(self.players, self.teams)
		self.testObj = retriever.HandRetriever.getInstance()

	def testGetHandReturnsCorrectData(self):
		playerId = "2"
		self.game.startGame()
		expectedHand = self.game._curSequence._round.hands[playerId]
		result = self.testObj.getHand(playerId, self.game)
		self.assertEqual(expectedHand, result)

	def testGetHandReturnsEmptyListWhenGameNotStarted(self):
		playerId = "1"
		result = self.testObj.getHand(playerId, self.game)
		self.assertEqual([], result)

	def testGetHandReturnsEmptyListWhenPlayerIdNotInGame(self):
		playerId = "8"
		self.game.startGame()
		result = self.testObj.getHand(playerId, self.game)
		self.assertEqual([], result)

class TurnRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [["1", "2"], ["3", "4"]]
		self.sequence = testhelper.createSingletonMock(euchre.Sequence)
		self.trumpTurnTracker = testhelper.createMock(game.TurnTracker)
		self.roundTurnTracker = testhelper.createMock(game.TurnTracker)
		self.round = testhelper.createSingletonMock(euchre.Round)
		self.trumpSelector = testhelper.createSingletonMock(euchre.TrumpSelector)
		when(self.sequence).getRound().thenReturn(self.round)
		when(self.sequence).getTrumpSelector().thenReturn(self.trumpSelector)
		when(self.round).getTurnTracker().thenReturn(self.roundTurnTracker)
		when(self.trumpSelector).getTurnTracker().thenReturn(self.trumpTurnTracker)
		self.game = euchre.Game.getInstance(self.players, self.teams)
		self.testObj = retriever.TurnRetriever.getInstance()

	def testReturnsCorrectDataDuringTrumpSelection(self):
		currentPlayer = "3"
		when(self.trumpTurnTracker).getCurrentPlayerId().thenReturn(currentPlayer)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION)
		self.game.startGame()
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(currentPlayer, result)

	def testReturnsCorrectDataDuringTrumpSelection2(self):
		currentPlayer = "2"
		when(self.trumpTurnTracker).getCurrentPlayerId().thenReturn(currentPlayer)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION_2)
		self.game.startGame()
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(currentPlayer, result)

	def testReturnsCorrectDataDuringGamePlay(self):
		currentPlayer = "4"
		when(self.roundTurnTracker).getCurrentPlayerId().thenReturn(currentPlayer)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_PLAYING_ROUND)
		self.game.startGame()
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(currentPlayer, result)

	def testReturnsNoneIfGameNotStarted(self):
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(None, result)

	def testReturnsNoneIfSequenceIsInAnotherState(self):
		self.game.startGame()
		when(self.roundTurnTracker).getCurrentPlayerId().thenReturn("1")
		when(self.trumpTurnTracker).getCurrentPlayerId().thenReturn("2")
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_INVALID)
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(None, result)

class UpCardRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = retriever.UpCardRetriever.getInstance()

	def testRetrieveUpCardReturnsCorrectData(self):
		expectedCard = euchre.Card(euchre.SUIT_SPADES, 10)

		gameObj = testhelper.createMock(euchre.Game)
		sequence = testhelper.createMock(euchre.Sequence)
		when(gameObj).getSequence().thenReturn(sequence)
		when(sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION)
		when(sequence).getUpCard().thenReturn(expectedCard)

		result = self.testObj.retrieveUpCard(gameObj)
		self.assertEqual(expectedCard, result)

	def testRetrieveUpCardReturnsNoneIfSequenceNotInCorrectState(self):
		expectedCard = euchre.Card(euchre.SUIT_SPADES, 10)

		gameObj = testhelper.createMock(euchre.Game)
		sequence = testhelper.createMock(euchre.Sequence)
		when(gameObj).getSequence().thenReturn(sequence)
		when(sequence).getState().thenReturn(euchre.Sequence.STATE_PLAYING_ROUND)
		when(sequence).getUpCard().thenReturn(expectedCard)

		result = self.testObj.retrieveUpCard(gameObj)
		self.assertEqual(None, result)

class GameStatusRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.game = mock(euchre.Game)
		self.sequence = mock(euchre.Sequence)
		when(self.game).getSequence().thenReturn(self.sequence)
		self.testObj = retriever.GameStatusRetriever.getInstance()

	def testRetrieveStatusReturnsCorrectValueWhenGameIsNull(self):
		self.assertEqual("waiting_for_more_players", self.testObj.retrieveGameStatus(None))

	def testRetrieveStatusReturnsTrumpSelectionWhenSequenceIsInTrumpSelection(self):
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION)
		self.assertEqual("trump_selection", self.testObj.retrieveGameStatus(self.game))

	def testRetrieveStatusReturnsTrumpSelection2WhenSequenceIsInTrumpSelection2(self):
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION_2)
		self.assertEqual("trump_selection_2", self.testObj.retrieveGameStatus(self.game))

	def testRetrieveStatusReturnsRoundInProgressWhenSequenceIsInPlayingRound(self):
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_PLAYING_ROUND)
		self.assertEqual("round_in_progress", self.testObj.retrieveGameStatus(self.game))

class LedSuitRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.game = mock(euchre.Game)
		self.sequence = mock(euchre.Sequence)
		self.round = mock(euchre.Round)
		self.trick = mock(euchre.Trick)
		self.ledSuit = random.randint(1, 4)

		when(self.game).getSequence().thenReturn(self.sequence)
		when(self.sequence).getRound().thenReturn(self.round)
		when(self.round).getCurrentTrick().thenReturn(self.trick)
		when(self.trick).getLedSuit().thenReturn(self.ledSuit)
		
		self.testObj = retriever.LedSuitRetriever.getInstance()

	def testRetrieveLedSuitReturnsExpectedResult(self):
		self.assertEqual(self.ledSuit, self.testObj.retrieveLedSuit(self.game))

	def testRetrieveLedSuitReturnsNoneWhenCurrentTrickIsNone(self):
		when(self.round).getCurrentTrick().thenReturn(None)
		self.assertEqual(None, self.testObj.retrieveLedSuit(self.game))

class CurrentTrickRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.game = mock(euchre.Game)
		self.sequence = mock(euchre.Sequence)
		self.round = mock(euchre.Round)
		self.trick = mock(euchre.Trick)
		self.cards = {"1234" : euchre.Card(euchre.SUIT_HEARTS, 10), "4567" : euchre.Card(euchre.SUIT_HEARTS, 12), "7890" : euchre.Card(euchre.SUIT_HEARTS, 11), "0123" : euchre.Card(euchre.SUIT_HEARTS, 14)}
		self.expectedResult = {}
		for playerId, card in self.cards.iteritems():
			self.expectedResult[playerId] = {"suit" : card.suit, "value" : card.value}

		when(self.game).getSequence().thenReturn(self.sequence)
		when(self.sequence).getRound().thenReturn(self.round)
		when(self.round).getCurrentTrick().thenReturn(self.trick)
		when(self.trick).getPlayedCards().thenReturn(self.cards)

		self.testObj = retriever.CurrentTrickRetriever.getInstance()

	def testRetrieveCurrentTrickReturnsExpectedResult(self):
		self.assertEqual(self.expectedResult, self.testObj.retrieveCurrentTrick(self.game))

	def testRetrieveCurrentTrickReturnsEmptyDictionaryIfCurrentTrickIsNone(self):
		when(self.round).getCurrentTrick().thenReturn(None)
		self.assertEqual({}, self.testObj.retrieveCurrentTrick(self.game))
