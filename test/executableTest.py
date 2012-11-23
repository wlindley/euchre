#!/usr/bin/env python
import testhelper
import json
import mock

from src import executable
from src import util
from src import model
from src import euchre
from src import game
from src import serializer

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

	def testCallsAddPlayerExecutableWhenActionIsAddPlayer(self):
		self._runTestForAction("addPlayer", "AddPlayerExecutable")

class CreateGameExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.playerId = "1"
		self.team = 0
		self.gameId = 251
		self.requestData = {"gameId" : self.gameId, "playerId" : self.playerId, "team" : self.team}
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.requestDataAccessor.get.side_effect = lambda key: self.requestData[key] if key in self.requestData else ''
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameIdTracker = testhelper.createSingletonMock(util.GameIdTracker)
		self.gameIdTracker.getGameId.return_value = self.gameId
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		self.gameModelFactory = testhelper.createSingletonMock(model.GameModelFactory)
		self.gameModelFactory.create.side_effect = lambda k: self.gameModel if self.gameId == k else mock.DEFAULT
		self.testObj = executable.CreateGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteCreatesGameModelWithCorrectData(self):
		expectedTeams = [[], []]
		expectedTeams[self.team].append(self.playerId)
		self.testObj.execute()
		self.assertEqual(self.gameId, self.gameModel.gameId)
		self.assertEqual(self.playerId, self.gameModel.playerId[0])
		self.assertEqual(json.dumps(expectedTeams), self.gameModel.teams)
		self.assertTrue(self.gameModel.put.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : True, "gameId" : self.gameId}))

	def testExecuteDoesNothingIfTeamIsTooLarge(self):
		self.team = self.requestData["team"] = 2
		self.testObj.execute()
		self.assertFalse(self.gameIdTracker.getGameId.called)
		self.assertFalse(self.gameModelFactory.create.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : False}))

	def testExecuteDoesNothingIfTeamIsTooSmall(self):
		self.team = self.requestData["team"] = -1
		self.testObj.execute()
		self.assertFalse(self.gameIdTracker.getGameId.called)
		self.assertFalse(self.gameModelFactory.create.called)
		self.responseWriter.write.assert_called_with(json.dumps({"success" : False}))

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

class AddPlayerExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.gameId = 12843
		self.existingPlayerIds = ["1", "2"]
		self.existingTeams = [["1"], ["2"]]
		self.requestData = {"gameId" : self.gameId}
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.requestDataAccessor.get.side_effect = lambda key: self.requestData[key] if key in self.requestData else ''
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		self.gameModel.playerId = self.existingPlayerIds
		self.gameModel.teams = json.dumps(self.existingTeams)
		self.gameModel.serializedGame = ''
		self.gameModelFinder.getGameByGameId.side_effect = lambda gid: self.gameModel if self.gameId == gid else None
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)

		self.testObj = executable.AddPlayerExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def _trainPlayerIdAndTeam(self, playerId, team):
		self.requestData["playerId"] = playerId
		self.requestData["team"] = team
		expectedPlayerIds = self.existingPlayerIds[:]
		expectedPlayerIds.append(playerId)
		expectedTeams = [self.existingTeams[0][:], self.existingTeams[1][:]]
		if team in range(len(expectedTeams)):
			expectedTeams[team].append(playerId)
		return expectedPlayerIds, expectedTeams

	def _assertResponseResult(self, success):
		self.responseWriter.write.assert_called_with(json.dumps({"success" : success}))

	def _assertGameModelUnchanged(self):
		self.assertEqual(self.existingPlayerIds, self.gameModel.playerId)
		self.assertEqual(json.dumps(self.existingTeams), self.gameModel.teams)
		self.assertFalse(self.gameModel.put.called)

	@mock.patch("src.euchre.Game.getInstance")
	def testExecuteAddsPlayerToTeamAndGame(self, mockObj):
		expectedPlayerIds, expectedTeams = self._trainPlayerIdAndTeam("3", 0)
		self.testObj.execute()
		self.assertEqual(expectedPlayerIds, self.gameModel.playerId)
		self.assertEqual(json.dumps(expectedTeams), self.gameModel.teams)
		self.assertTrue(self.gameModel.put.called)
		self.assertFalse(euchre.Game.getInstance.called)
		self._assertResponseResult(True)

	def testExecuteDoesNothingIfPlayerAlreadyInGame(self):
		self._trainPlayerIdAndTeam("1", 1)
		self.testObj.execute()
		self._assertGameModelUnchanged()
		self._assertResponseResult(False)

	def testExecuteDoesNothingIfInvalidGameId(self):
		self._trainPlayerIdAndTeam("3", 1)
		self.requestData["gameId"] += 1
		self.testObj.execute()
		self._assertGameModelUnchanged()
		self._assertResponseResult(False)

	def testExecuteDoesNothingIfTeamTooLarge(self):
		self._trainPlayerIdAndTeam("3", 2)
		self.testObj.execute()
		self._assertGameModelUnchanged()
		self._assertResponseResult(False)

	def testExecuteDoesNothingIfTeamTooSmall(self):
		self._trainPlayerIdAndTeam("3", -1)
		self.testObj.execute()
		self._assertGameModelUnchanged()
		self._assertResponseResult(False)

	def testExecuteDoesNothingIfTeamIsFull(self):
		team = 0
		self.existingPlayerIds.append("3")
		self.existingTeams[team].append("3")
		self.gameModel.playerId = self.existingPlayerIds
		self.gameModel.teams = json.dumps(self.existingTeams)
		self._trainPlayerIdAndTeam("4", team)
		self.testObj.execute()
		self._assertGameModelUnchanged()
		self._assertResponseResult(False)

	@mock.patch("src.euchre.Game.getInstance")
	def testExecuteCreatesStartsAndSerializesGameIfAddingFourthPlayer(self, mockObj):
		self.existingPlayerIds.append("3")
		self.existingTeams[0].append("3")
		self.gameModel.playerId = self.existingPlayerIds
		self.gameModel.teams = json.dumps(self.existingTeams)
		expectedPlayerIds, expectedTeams = self._trainPlayerIdAndTeam("4", 1)
		expectedPlayers = [game.Player(pid) for pid in expectedPlayerIds]
		gameObj = testhelper.createMock(euchre.Game)
		euchre.Game.getInstance.side_effect = lambda players, teams: gameObj if expectedPlayers == players and expectedTeams == teams else None
		serializedGame = "correct game serialized"
		self.gameSerializer.serialize.side_effect = lambda g: serializedGame if gameObj == g else "incorrect game serialized"

		self.testObj.execute()

		self.assertTrue(gameObj.startGame.called)
		self.assertEqual(serializedGame, self.gameModel.serializedGame)
		self.assertTrue(self.gameModel.put.called)
		self._assertResponseResult(True)
