#!/usr/bin/env python
import json
import mock
import testhelper
import executable
import util
import model
import euchre
import game
import serializer

class ExecutableFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.testObj = executable.ExecutableFactory.getInstance(self.requestDataAccessor, self.responseWriter)

	def _runTestForAction(self, action, executableClassName):
		executableObj = testhelper.createSingletonMock(executable.__dict__[executableClassName])
		self.requestDataAccessor.get.side_effect = lambda k: action if "action" == k else mock.DEFAULT
		result = self.testObj.createExecutable()
		self.assertEqual(executableObj, result)

	def testCallsDefaultWhenActionIsMissing(self):
		self._runTestForAction("", "DefaultExecutable")

	def testCallsCreateGameWhenActionIsCreateGame(self):
		self._runTestForAction("createGame", "CreateGameExecutable")

	def testCallsListGamesWhenActionIsListGames(self):
		self._runTestForAction("listGames", "ListGamesExecutable")

class CreateGameExecutable(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameId = 251
		self.gameIdTracker = testhelper.createSingletonMock(util.GameIdTracker)
		self.gameIdTracker.getGameId.return_value = self.gameId
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		self.gameModelFactory = testhelper.createSingletonMock(model.GameModelFactory)
		self.gameModelFactory.create.side_effect = lambda k: self.gameModel if self.gameId == k else mock.DEFAULT
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		self.testObj = executable.CreateGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteCreatesGameModelWithCorrectGameId(self):
		self.responseWriter.write.side_effect = lambda s: json.loads(s)["gameId"] == self.gameId
		self.testObj.execute()
		self.assertTrue(self.gameModel.put.called)
		self.assertTrue(self.responseWriter.write.called)

	def testExecuteCreatesGameModelWithSpecifiedPlayerIds(self):
		playerIds = ["1", "2", "3", "4"]
		self.requestDataAccessor.get.side_effect = lambda k: playerIds if "players" == k else mock.DEFAULT
		self.testObj.execute()
		self.assertEqual(playerIds, self.gameModel.playerId)

	@mock.patch("euchre.Game.getInstance")
	def testExecuteCreatesGameWithCorrectPlayersAndTeams(self, mockObject):
		playerIds = ["1", "2", "3", "4"]
		players = [game.Player(pid) for pid in playerIds]
		teams = [[playerIds[0], playerIds[1]], [playerIds[2], playerIds[3]]]
		requestData = {"players" : playerIds, "teams" : teams}
		self.requestDataAccessor.get.side_effect = lambda k: requestData[k] if k in requestData else mock.DEFAULT
		
		self.testObj.execute()

		euchre.Game.getInstance.assert_called_with(players, teams)

	def testExecuteStoresSerializedGameInGameModel(self):
		gameObj = testhelper.createSingletonMock(euchre.Game)
		serializedGame = "some serialized game"
		self.gameSerializer.serialize.side_effect = lambda obj: serializedGame if gameObj == obj else "incorrect serialized game"

		self.testObj.execute()

		self.assertEqual(serializedGame, self.gameModel.serializedGame)

class ListGamesExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.testObj = executable.ListGamesExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteReturnsCorrectGameIds(self):
		playerId = "2854"
		self.requestDataAccessor.get.side_effect = lambda k: playerId if "playerId" == k else mock.DEFAULT
		gameModels = [testhelper.createMock(model.GameModel), testhelper.createMock(model.GameModel)]
		gameModels[0].gameId = "1000"
		gameModels[1].gameId = "4000"
		self.gameModelFinder.getGamesForPlayerId.side_effect = lambda pid: gameModels if playerId == pid else mock.DEFAULT
		
		self.testObj.execute()

		self.responseWriter.write.assert_called_with(json.dumps({"gameIds" : [gameModels[0].gameId, gameModels[1].gameId]}))

class DefaultExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.testObj = executable.DefaultExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteReturnsEmptyObjectAsResponse(self):
		self.testObj.execute()
		self.responseWriter.write.assert_called_with(json.dumps({}))
