#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
from mockito import *

import google.appengine.ext.ndb

from src import model

class GameModelFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = model.GameModelFactory.getInstance()

	def testCreateReturnsGameModelWithGivenId(self):
		result = self.testObj.create()
		self.assertTrue(isinstance(result, model.GameModel))

class GameModelFinderTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = model.GameModelFinder.getInstance()

	def testGetGamesForPlayerIdReturnsGameModelsFromQuery(self):
		playerId = "12345"
		models = [testhelper.createMock(model.GameModel), testhelper.createMock(model.GameModel)]
		query = testhelper.createMock(ndb.Query)
		when(query).fetch(any(int)).thenReturn(models).thenReturn([])
		self.testObj._getQuery = lambda pid: query if playerId == pid else None
		result = self.testObj.getGamesForPlayerId(playerId)
		self.assertEqual(models, result)

	def testGetGameByGameIdReturnsCorrectGameModel(self):
		gameId = "864"
		gameModel = testhelper.createMock(model.GameModel)
		key = testhelper.createMock(ndb.Key)
		when(key).get().thenReturn(gameModel)
		self.testObj._getKeyByUrl = lambda url: key if gameId == url else None
		result = self.testObj.getGameByGameId(gameId)
		self.assertEqual(gameModel, result)

	def testDeleteGameReturnsFalseAndDoesNothingElseIfCannotFindGameModel(self):
		gameId = "8237"
		key = testhelper.createMock(ndb.Key)
		when(key).get().thenReturn(None)
		self.testObj._getKeyByUrl = lambda url: None
		result = self.testObj.deleteGame(gameId)
		self.assertFalse(result)

	def testDeleteGameDeletesSpecifiedGameAndReturnsTrue(self):
		gameId = "8237"
		gameModel = testhelper.createMock(model.GameModel)
		key = testhelper.createMock(ndb.Key)
		gameModel.key = key
		when(key).get().thenReturn(gameModel)
		self.testObj._getKeyByUrl = lambda url: key if gameId == url else None

		result = self.testObj.deleteGame(gameId)

		verify(key).delete()
		self.assertTrue(result)

class MatchmakingTicketFinderTest(testhelper.TestCase):
	def setUp(self):
		self.ticketModel = testhelper.createMock(model.MatchmakingTicketModel)
		self.ticketKey = testhelper.createMock(ndb.Key)
		self.ticketMetaKey = testhelper.createMock(ndb.Key)
		self.ticketQuery = testhelper.createMock(ndb.Query)

		self.playerId = "asdlkj432"
		self.ticketModel.playerId = self.playerId

		self.ticketModelSearchResults = [testhelper.createMock(model.MatchmakingTicketModel), testhelper.createMock(model.MatchmakingTicketModel), testhelper.createMock(model.MatchmakingTicketModel)]

		self._buildTestObj()
		self._doTraining()

	def _buildTestObj(self):
		self.testObj = model.MatchmakingTicketFinder.getInstance()

	def _doTraining(self):
		self.testObj._getQuery = lambda: self.ticketQuery
		when(model).MatchmakingTicketModel(key=self.ticketKey).thenReturn(self.ticketModel)
		when(google.appengine.ext.ndb).Key(model.RootModel, "matchmaking_tickets").thenReturn(self.ticketMetaKey)
		when(google.appengine.ext.ndb).Key(model.RootModel, "matchmaking_tickets", model.MatchmakingTicketModel, "matchmaking_ticket_" + self.playerId).thenReturn(self.ticketKey)
		when(self.ticketKey).get().thenReturn(self.ticketModel)

	def testIsPlayerInQueueReturnsTrueIfModelSaysSo(self):
		self.ticketModel.lookingForMatch = True
		self.assertTrue(self.testObj.isPlayerInQueue(self.playerId))

	def testIsPlayerInQueueReturnsFalseIfModelSaysSo(self):
		self.ticketModel.lookingForMatch = False
		self.assertFalse(self.testObj.isPlayerInQueue(self.playerId))

	def testIsPlayerInQueueReturnsFalseIfModelNotFound(self):
		when(self.ticketKey).get().thenReturn(None)
		self.assertFalse(self.testObj.isPlayerInQueue(self.playerId))

	def testAddPlayerToQueueUpdatesTicketModelIfItExists(self):
		self.ticketModel.lookingForMatch = False
		self.testObj.addPlayerToQueue(self.playerId)
		self.assertTrue(self.ticketModel.lookingForMatch)
		verify(self.ticketModel).put()

	def testAddPlayerToQueueDoesNotUpdateTicketModelIfPlayerInQueue(self):
		self.ticketModel.lookingForMatch = True
		self.testObj.addPlayerToQueue(self.playerId)
		verify(self.ticketModel, never).put()

	def testAddPlayerToQueueCreateModelIfItDoesNotExist(self):
		when(self.ticketKey).get().thenReturn(None)

		self.testObj.addPlayerToQueue(self.playerId)

		self.assertEqual(self.playerId, self.ticketModel.playerId)
		self.assertTrue(self.ticketModel.lookingForMatch)
		verify(self.ticketModel).put()

	def testGetMatchmakingGroupReturnsRequestedNumberOfPlayersIfAvailable(self):
		when(self.ticketQuery).fetch(3).thenReturn(self.ticketModelSearchResults)
		result = self.testObj.getMatchmakingGroup(3)
		self.assertEqual(self.ticketModelSearchResults, result)