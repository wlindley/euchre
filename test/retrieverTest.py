#!/usr/bin/env python
import testhelper
import json
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
