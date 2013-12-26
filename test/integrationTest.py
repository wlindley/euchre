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

class FakeMatchmakingTicketFinder(object):
	def __init__(self):
		self.queue = []

	def isPlayerInQueue(self, playerId):
		return playerId in self.queue

	def addPlayerToQueue(self, playerId):
		self.queue.append(playerId)

	def getMatchmakingGroup(self, numPlayers):
		if len(self.queue) >= 3:
			group = self.queue[:3]
			self.queue = self.queue[3:]
			return group
		return []

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
		self.gameModel.readyToRemove = []
		self.gameModel.serializedGame = ""
		self.gameModel.key = testhelper.createMock(ndb.Key)

		self.gameModelFactory = testhelper.createSingletonMock(model.GameModelFactory)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		testhelper.createSingletonMock(model.MatchmakingTicketFinder)
		model.MatchmakingTicketFinder.instance = FakeMatchmakingTicketFinder()

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
		self.gameModelFinder.getGamesForPlayerId = lambda pid: [self.gameModel] if pid in self.gameModel.playerId else []

	def createExecutableBasics(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.session = testhelper.createSingletonMock(util.Session)
		self.facebook = testhelper.createSingletonMock(social.Facebook)

		self.response = None
		def handleResponse(response):
			self.response = response
		self.responseWriter.write = handleResponse

	def trainSignedInUser(self, user):
		when(self.facebook).getUser("me").thenReturn(user)

	def runCreateGame(self, user):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("team").thenReturn("0")
		exe = executable.CreateGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runAddPlayer(self, user, gameId, teamId):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("gameId").thenReturn(gameId)
		when(self.requestDataAccessor).get("team").thenReturn(teamId)
		exe = executable.AddPlayerExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runListGames(self, user):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		exe = executable.ListGamesExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runGetGameData(self, user, gameId):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("gameId").thenReturn(gameId)
		exe = executable.GetGameDataExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runMatchmaking(self, user):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		exe = executable.MatchmakingExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runGetMatchmakingStatus(self, user):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		exe = executable.GetMatchmakingStatusExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runAddRobots(self, user, gameId, robots):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("gameId").thenReturn(gameId)
		when(self.requestDataAccessor).get("types").thenReturn(json.dumps(robots))
		exe = executable.AddRobotsExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def runSelectTrump(self, user, gameId, suit):
		self.createExecutableBasics()
		self.trainSignedInUser(user)
		when(self.requestDataAccessor).get("gameId").thenReturn(gameId)
		when(self.requestDataAccessor).get("suit").thenReturn(suit)
		exe = executable.SelectTrumpExecutable.getInstance(self.requestDataAccessor, self.responseWriter, self.session)
		exe.execute()
		return self.response

	def fillGameWithPlayers(self):
		self.runCreateGame(self.users[0])
		for i in range(1, len(self.users)):
			self.runAddPlayer(self.users[i], self.gameId, int(i / 2))

	def fillGameWithRobots(self):
		self.users = []
		for i in range(4):
			self.users.append(self.createUser("euchre_robot_random_" + str(i)))
		self.fillGameWithPlayers()

	###TESTS###

	def testAdding4PlayersStartsGame(self):
		#actions
		self.fillGameWithPlayers()

		#verification
		gameSerializer = serializer.GameSerializer.getInstance()
		gameStatusRetriever = retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE)
		gameObj = gameSerializer.deserialize(self.gameModel.serializedGame)
		status = gameStatusRetriever.retrieveGameStatus(gameObj)
		self.assertEqual("trump_selection", status)

	def testListGamesShowsGameAfterItIsCreated(self):
		#actions
		self.runCreateGame(self.users[0])
		response = self.runListGames(self.users[0])

		#verification
		hydratedResponse = json.loads(response)
		self.assertEqual(1, len(hydratedResponse["games"]))
		self.assertEqual(self.gameId, hydratedResponse["games"][0]["gameId"])

	def testGetGameDataReturnsBasicExpectedValues(self):
		#actions
		self.fillGameWithPlayers()
		response = self.runGetGameData(self.users[0], self.gameId)

		#verification
		hydratedResponse = json.loads(response)
		self.assertEqual(self.gameId, hydratedResponse["gameId"])
		self.assertEqual(4, len(hydratedResponse["playerIds"]))
		self.assertEqual(2, len(hydratedResponse["teams"][0]))
		self.assertEqual(2, len(hydratedResponse["teams"][1]))
		self.assertEqual(5, len(hydratedResponse["round"]["hand"]))

	def testMatchmakingQueue(self):
		#actions
		self.runMatchmaking(self.users[0])
		response = self.runGetMatchmakingStatus(self.users[0])

		#verification
		hydratedResponse = json.loads(response)
		self.assertTrue(hydratedResponse["playerInQueue"])

	def testMatchmakingCreatesAndStartsGame(self):
		#actions
		preResponse = self.runListGames(self.users[0])
		for user in self.users:
			self.runMatchmaking(user)
		postResponse = self.runListGames(self.users[0])

		#verification
		hydratedPreResponse = json.loads(preResponse)
		hydratedPostResponse = json.loads(postResponse)
		self.assertEqual(0, len(hydratedPreResponse["games"]))
		self.assertEqual(1, len(hydratedPostResponse["games"]))

	def testRobotsWillFinishTrumpSelection(self):
		#actions
		self.runCreateGame(self.users[0])
		self.runAddRobots(self.users[0], self.gameId, [[None, "euchre_robot_random_1"], ["euchre_robot_random_2", "euchre_robot_random_3"]])
		self.runSelectTrump(self.users[0], self.gameId, euchre.SUIT_NONE)
		self.runSelectTrump(self.users[0], self.gameId, euchre.SUIT_HEARTS)

		#verification
		gameSerializer = serializer.GameSerializer.getInstance()
		gameStatusRetriever = retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE)
		gameObj = gameSerializer.deserialize(self.gameModel.serializedGame)
		status = gameStatusRetriever.retrieveGameStatus(gameObj)
		self.assertEqual("round_in_progress", status)

	def testRobotsCanFinishGame(self):
		#actions
		self.fillGameWithRobots()

		#verification
		gameSerializer = serializer.GameSerializer.getInstance()
		gameStatusRetriever = retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE)
		gameObj = gameSerializer.deserialize(self.gameModel.serializedGame)
		status = gameStatusRetriever.retrieveGameStatus(gameObj)
		self.assertEqual("complete", status)