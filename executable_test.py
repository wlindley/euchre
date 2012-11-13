#!/usr/bin/env python
import json
import mock
import testhelper
import executable
import util
import model
import euchre
import game

class ExecutableFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.testObj = executable.ExecutableFactory.getInstance(self.requestDataAccessor, self.responseWriter)

	def testCallsCreateGameWhenActionIsCreateGame(self):
		createGameExecutable = testhelper.createSingletonMock(executable.CreateGameExecutable)
		action = "createGame"
		self.requestDataAccessor.get.side_effect = lambda k: action if "action" == k else mock.DEFAULT
		result = self.testObj.createExecutable()
		self.assertEqual(createGameExecutable, result)

class CreateGameExecutable(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameId = 251
		self.gameIdTracker = testhelper.createSingletonMock(util.GameIdTracker)
		self.gameIdTracker.getGameId.return_value = self.gameId
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		self.gameModelFactory = testhelper.createSingletonMock(util.GameModelFactory)
		self.gameModelFactory.create.side_effect = lambda k: self.gameModel if self.gameId == k else mock.DEFAULT
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
