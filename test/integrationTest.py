#!/usr/bin/env python
import testhelper
import unittest
from mockito import *
from google.appengine.ext import ndb
import json

from src import executable
from src import social
from src import model
from src import util
from src import retriever
from src import serializer
from src import euchre

class IntegrationTest(testhelper.TestCase):
	def setUp(self):
		self._currentPlayerId = 0

		self.users = []
		for i in range(4):
			self.users.append(self.createUser())

		self.gameId = "23097324kjasdfl234098"
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.playerId = []
		self.gameModel.teams = json.dumps([[], []])
		self.gameModel.key = testhelper.createMock(ndb.Key)
		self.gameModelFactory = testhelper.createSingletonMock(model.GameModelFactory)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)

		self.doTraining()

	def createUser(self, playerId=None, name=None):
		if None == playerId:
			playerId = str(self._currentPlayerId)
			self._currentPlayerId += 1
		if None == name:
			name = "Foobar Bingbaz"
		return social.User.getInstance(playerId, name)

	def doTraining(self):
		when(self.gameModel.key).urlsafe().thenReturn(self.gameId)
		when(self.gameModel).put().thenReturn(self.gameModel.key)
		when(self.gameModelFactory).create().thenReturn(self.gameModel)
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)

	def createExecutableBasics(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.session = testhelper.createSingletonMock(util.Session)
		self.facebook = testhelper.createSingletonMock(social.Facebook)

	def trainSignedInUser(self, user):
		when(self.facebook).getUser("me").thenReturn(user)

	def runCreateGame(self, user):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("team").thenReturn("0")
		exe = executable.CreateGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()

	def runAddPlayer(self, user, gameId, teamId):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("gameId").thenReturn(gameId)
		when(self.requestDataAccessor).get("team").thenReturn(teamId)
		exe = executable.AddPlayerExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()

	def testAdding4PlayersStartsGame(self):
		#actions
		self.runCreateGame(self.users[0])
		for i in range(1, len(self.users)):
			self.runAddPlayer(self.users[i], self.gameId, int(i / 2))

		#verification
		gameSerializer = serializer.GameSerializer.getInstance()
		gameStatusRetriever = retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE)
		gameObj = gameSerializer.deserialize(self.gameModel.serializedGame)
		status = gameStatusRetriever.retrieveGameStatus(gameObj)
		self.assertEqual("trump_selection", status)