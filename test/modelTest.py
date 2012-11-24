#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
from mockito import *

from src import model

class GameModelFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = model.GameModelFactory.getInstance()

	def testCreateReturnsGameModelWithGivenId(self):
		gameId = 5428
		result = self.testObj.create(gameId)
		self.assertTrue(isinstance(result, model.GameModel))
		self.assertEqual(gameId, result.gameId)

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
		gameId = 864
		gameModel = testhelper.createMock(model.GameModel)
		query = testhelper.createMock(ndb.Query)
		when(query).get().thenReturn(gameModel)
		self.testObj._getGameIdQuery = lambda gid: query if gameId == gid else None
		result = self.testObj.getGameByGameId(gameId)
		self.assertEqual(gameModel, result)
