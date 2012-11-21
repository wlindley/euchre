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

	def testCallsStartGameExecutableWhenActionIsStartGame(self):
		self._runTestForAction("startGame", "StartGameExecutable")

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
		self.testObj = executable.CreateGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteCreatesGameModelWithCorrectGameId(self):
		self.responseWriter.write.side_effect = lambda s: json.loads(s)["gameId"] == self.gameId
		self.testObj.execute()
		self.assertTrue(self.gameModel.put.called)
		self.assertTrue(self.responseWriter.write.called)

	def testExecuteCreatesGameModelWithSpecifiedPlayerIds(self):
		playerId = "1"
		self.requestDataAccessor.get.side_effect = lambda k: playerId if "playerId" == k else mock.DEFAULT
		self.testObj.execute()
		self.assertEqual(playerId, self.gameModel.playerId[0])

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

class StartGameExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.playerIds = ["1", "2", "3", "4"]
		self.teams = [["1", "2"], ["3", "4"]]
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.serializer = testhelper.createSingletonMock(serializer.GameSerializer)
		self.game = testhelper.createSingletonMock(euchre.Game)
		self.gameId = 12589
		self.requestDataAccessor.get.side_effect = lambda k: self.gameId if "gameId" == k else mock.DEFAULT
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.serializedGame = ""
		self.gameModel.playerId = self.playerIds
		self.gameModel.teams = json.dumps(self.teams)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModelFinder.getGameByGameId.side_effect = lambda gid: self.gameModel if self.gameId == gid else None
		self.serializedGame = "some serialized game"
		self.serializer.serialize.side_effect = lambda g: self.serializedGame if self.game == g else "incorrect game"

		self.testObj = executable.StartGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteCreatesGameCallsStartAndSerializesIt(self):
		self.testObj.execute()
		self.assertTrue(self.game.startGame.called)
		self.assertEqual(json.dumps(self.serializedGame), self.gameModel.serializedGame)
		self.assertTrue(self.gameModel.put.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : True}))

	@mock.patch("euchre.Game.getInstance")
	def testExecuteCreatesCorrectGame(self, mockObject):
		players = [game.Player(pid) for pid in self.playerIds]
		self.testObj.execute()
		euchre.Game.getInstance.assert_called_with(players, self.teams)

	def testExecuteDoesNotStartGameIfSerializedGameAlreadyPresentOnModel(self):
		otherSerializedGame = "another serialized game"
		self.gameModel.serializedGame = json.dumps(otherSerializedGame)
		self.testObj.execute()
		self.assertEqual(json.dumps(otherSerializedGame), self.gameModel.serializedGame)
		self.assertFalse(self.gameModel.put.called)
		self.assertFalse(self.game.startGame.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : False}))

	def testExecuteDoesNotStartGameIfThereAreLessThan4Players(self):
		self.gameModel.serializedGame = ""
		self.playerIds = ["1", "2"]
		self.teams = [["1"], ["2"]]
		self.gameModel.playerId = self.playerIds
		self.gameModel.teams = json.dumps(self.teams)
		self.testObj.execute()
		self.assertEqual("", self.gameModel.serializedGame)
		self.assertFalse(self.gameModel.put.called)
		self.assertFalse(self.game.startGame.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : False}))

	def testExecuteDoesNothingIfGameIdDoesNotExist(self):
		self.requestDataAccessor.get.side_effect = lambda k: self.gameId + 1 if "gameId" == k else mock.DEFAULT
		self.testObj.execute()
		self.assertEqual("", self.gameModel.serializedGame)
		self.assertFalse(self.gameModel.put.called)
		self.assertFalse(self.game.startGame.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : False}))
