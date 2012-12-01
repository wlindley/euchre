#!/usr/bin/env python
import testhelper
import json
from mockito import *

import src.euchre

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
		when(self.requestDataAccessor).get("action").thenReturn(action)
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

	def testCallsGetGameDataExecutableWhenActionIsGetGameData(self):
		self._runTestForAction("getGameData", "GetGameDataExecutable")

class CreateGameExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.playerId = "1"
		self.team = 0
		self.gameId = 251
		self.requestData = {"gameId" : self.gameId, "playerId" : self.playerId, "team" : str(self.team)}
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		for key, val in self.requestData.iteritems():
			when(self.requestDataAccessor).get(key).thenReturn(val)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameIdTracker = testhelper.createSingletonMock(util.GameIdTracker)
		when(self.gameIdTracker).getGameId().thenReturn(self.gameId)
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		self.gameModelFactory = testhelper.createSingletonMock(model.GameModelFactory)
		when(self.gameModelFactory).create(self.gameId).thenReturn(self.gameModel)
		self.testObj = executable.CreateGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteCreatesGameModelWithCorrectData(self):
		expectedTeams = [[], []]
		expectedTeams[self.team].append(self.playerId)
		self.testObj.execute()
		self.assertEqual(self.gameId, self.gameModel.gameId)
		self.assertEqual(self.playerId, self.gameModel.playerId[0])
		self.assertEqual(json.dumps(expectedTeams), self.gameModel.teams)
		verify(self.gameModel).put()
		verify(self.responseWriter).write(json.dumps({"success" : True, "gameId" : self.gameId}))

	def testExecuteDoesNothingIfTeamIsTooLarge(self):
		self.team = self.requestData["team"] = 2
		when(self.requestDataAccessor).get("team").thenReturn(str(self.team))
		self.testObj.execute()
		verifyZeroInteractions(self.gameIdTracker)
		verifyZeroInteractions(self.gameModelFactory)
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteDoesNothingIfTeamIsTooSmall(self):
		self.team = self.requestData["team"] = -1
		when(self.requestDataAccessor).get("team").thenReturn(str(self.team))
		self.testObj.execute()
		verifyZeroInteractions(self.gameIdTracker)
		verifyZeroInteractions(self.gameModelFactory)
		verify(self.responseWriter).write(json.dumps({"success" : False}))

class ListGamesExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.handRetriever = testhelper.createSingletonMock(util.HandRetriever)
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		self.testObj = executable.ListGamesExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteReturnsCorrectGameData(self):
		playerId = "2854"
		when(self.requestDataAccessor).get("playerId").thenReturn(playerId)

		serializedGames = ["serialized game 1", "serialized game 2"]
		gameIds = ["1000", "4000"]
		gameModels = [testhelper.createMock(model.GameModel), testhelper.createMock(model.GameModel)]
		for i in range(len(gameModels)):
			gameModels[i].gameId = gameIds[i]
			gameModels[i].serializedGame = serializedGames[i]
		when(self.gameModelFinder).getGamesForPlayerId(playerId).thenReturn(gameModels)

		games = [testhelper.createMock(euchre.Game), testhelper.createMock(euchre.Game)]
		hands = [[euchre.Card(suit=euchre.SUIT_HEARTS, value=9), euchre.Card(suit=euchre.SUIT_CLUBS, value=10)], [euchre.Card(suit=euchre.SUIT_SPADES, value=11), euchre.Card(suit=euchre.SUIT_DIAMONDS, value=8)]]
		for i in range(len(games)):
			when(self.gameSerializer).deserialize(serializedGames[i]).thenReturn(games[i])
			when(self.handRetriever).getHand(playerId, games[i]).thenReturn(hands[i])
		
		self.testObj.execute()

		expectedResponse = {
			"success" : True,
			"games" : []
		}

		for i in range(len(gameModels)):
			hand = [{"suit" : c.suit, "value" : c.value} for c in hands[i]]
			expectedResponse["games"].append({
				"gameId" : gameModels[i].gameId,
				"hand" : hand
			})

		verify(self.responseWriter).write(json.dumps(expectedResponse))

class DefaultExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.testObj = executable.DefaultExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteReturnsEmptyObjectAsResponse(self):
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({}))

class AddPlayerExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.gameId = 12843
		self.existingPlayerIds = ["1", "2"]
		self.existingTeams = [["1"], ["2"]]
		self.requestData = {"gameId" : self.gameId}
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		when(self.requestDataAccessor).get("gameId").thenReturn(str(self.gameId))
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		self.gameModel.playerId = self.existingPlayerIds
		self.gameModel.teams = json.dumps(self.existingTeams)
		self.gameModel.serializedGame = ''
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)

		self.testObj = executable.AddPlayerExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def _trainPlayerIdAndTeam(self, playerId, team):
		when(self.requestDataAccessor).get("playerId").thenReturn(playerId)
		when(self.requestDataAccessor).get("team").thenReturn(team)
		expectedPlayerIds = self.existingPlayerIds[:]
		expectedPlayerIds.append(playerId)
		expectedTeams = [self.existingTeams[0][:], self.existingTeams[1][:]]
		if team in range(len(expectedTeams)):
			expectedTeams[team].append(playerId)
		return expectedPlayerIds, expectedTeams

	def _assertResponseResult(self, success):
		verify(self.responseWriter).write(json.dumps({"success" : success}))

	def _assertGameModelUnchanged(self):
		self.assertEqual(self.existingPlayerIds, self.gameModel.playerId)
		self.assertEqual(json.dumps(self.existingTeams), self.gameModel.teams)
		verify(self.gameModel, never).put()

	def testExecuteAddsPlayerToTeamAndGame(self):
		testhelper.replaceClass(src.euchre, "Game", testhelper.createSimpleMock())
		expectedPlayerIds, expectedTeams = self._trainPlayerIdAndTeam("3", 0)
		when(self.requestDataAccessor).get("team").thenReturn("0")
		self.testObj.execute()
		self.assertEqual(expectedPlayerIds, self.gameModel.playerId)
		self.assertEqual(json.dumps(expectedTeams), self.gameModel.teams)
		verify(self.gameModel).put()
		verifyZeroInteractions(src.euchre.Game)
		self._assertResponseResult(True)

	def textExecuteDoesNotBlowUpIfBadIntegerIsPassed(self):
		self.requestDataAccessor = testhelper.createMock(util.RequestDataAccessor)
		when(self.requestDataAccessor).get("gameId").thenReturn("1.283")
		when(self.requestDataAccessor).get("team").thenReturn(".5")
		when(self.requestDataAccessor).get("playerId").thenReturn("12345")
		self.testObj = executable.AddPlayerExecutable.getInstance(self.requestDataAccessor, self.responseWriter)
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteDoesNothingIfPlayerAlreadyInGame(self):
		self._trainPlayerIdAndTeam("1", 1)
		self.testObj.execute()
		self._assertGameModelUnchanged()
		self._assertResponseResult(False)

	def testExecuteDoesNothingIfInvalidGameId(self):
		self._trainPlayerIdAndTeam("3", 1)
		self.requestData["gameId"] += 1
		when(self.requestDataAccessor).get("gameId").thenReturn(self.requestData["gameId"])
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

	def testExecuteCreatesStartsAndSerializesGameIfAddingFourthPlayer(self):
		self.existingPlayerIds.append("3")
		self.existingTeams[0].append("3")
		self.gameModel.playerId = self.existingPlayerIds
		self.gameModel.teams = json.dumps(self.existingTeams)
		expectedPlayerIds, expectedTeams = self._trainPlayerIdAndTeam("4", 1)
		expectedPlayers = [game.Player(pid) for pid in expectedPlayerIds]
		gameObj = testhelper.createMock(euchre.Game)
		testhelper.replaceClass(src.euchre, "Game", testhelper.createSimpleMock())
		when(src.euchre.Game).getInstance(expectedPlayers, expectedTeams).thenReturn(gameObj)
		serializedGame = "correct game serialized"
		when(self.gameSerializer).serialize(gameObj).thenReturn(serializedGame)

		self.testObj.execute()

		verify(gameObj).startGame()
		self.assertEqual(serializedGame, self.gameModel.serializedGame)
		verify(self.gameModel).put()
		self._assertResponseResult(True)

class GetGameDataExecutableTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameId = 12345
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.gameId = self.gameId
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)
		self.playerId = "09876"
		when(self.requestDataAccessor).get("gameId").thenReturn(self.gameId)
		when(self.requestDataAccessor).get("playerId").thenReturn(self.playerId)
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		self.turnRetriever = testhelper.createSingletonMock(util.TurnRetriever)
		self.gameObj = testhelper.createMock(euchre.Game)
		self.serializedGame = "a serialized game"
		self.gameModel.serializedGame = self.serializedGame
		when(self.gameSerializer).deserialize(self.serializedGame).thenReturn(self.gameObj)
		self.sequence = testhelper.createMock(euchre.Sequence)
		when(self.gameObj).getSequence().thenReturn(self.sequence)

		self.testObj = executable.GetGameDataExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testReturnsWaitingForMorePlayersIfNotEnoughPeopleHaveJoined(self):
		playerIds = [self.playerId, "2"]
		self.gameModel.playerId = playerIds

		self.testObj.execute()

		expectedResponse = {
			"success" : True,
			"status" : "waiting_for_players",
			"playerIds" : playerIds
		}
		verify(self.responseWriter).write(json.dumps(expectedResponse))

	def testReturnsPlayersTurnAndTrumpSelectionStatusWhenTrumpSelectionInProgress(self):
		playerIds = [self.playerId, "2", "3", "4"]
		self.gameModel.playerId = playerIds
		currentPlayerId = playerIds[2]
		when(self.turnRetriever).retrieveTurn(self.gameObj).thenReturn(currentPlayerId)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION)

		self.testObj.execute()

		expectedResponse = {
			"success" : True,
			"status" : "trump_selection",
			"playerIds" : playerIds,
			"currentPlayerId" : currentPlayerId
		}
		verify(self.responseWriter).write(json.dumps(expectedResponse))

	def testReturnsPlayersTurnAndTrumpSelectionStatusWhenSecondTrumpSelectionInProgress(self):
		playerIds = [self.playerId, "2", "3", "4"]
		self.gameModel.playerId = playerIds
		currentPlayerId = playerIds[2]
		when(self.turnRetriever).retrieveTurn(self.gameObj).thenReturn(currentPlayerId)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION_2)

		self.testObj.execute()

		expectedResponse = {
			"success" : True,
			"status" : "trump_selection_2",
			"playerIds" : playerIds,
			"currentPlayerId" : currentPlayerId
		}
		verify(self.responseWriter).write(json.dumps(expectedResponse))

	def testReturnsPlayersTurnAndTrumpSelectionStatusWhenRoundInProgress(self):
		playerIds = [self.playerId, "2", "3", "4"]
		self.gameModel.playerId = playerIds
		currentPlayerId = playerIds[2]
		when(self.turnRetriever).retrieveTurn(self.gameObj).thenReturn(currentPlayerId)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_PLAYING_ROUND)

		self.testObj.execute()

		expectedResponse = {
			"success" : True,
			"status" : "round_in_progress",
			"playerIds" : playerIds,
			"currentPlayerId" : currentPlayerId
		}
		verify(self.responseWriter).write(json.dumps(expectedResponse))

	def testReturnsFailureWhenPlayerIdIsInvalid(self):
		when(self.requestDataAccessor).get("playerId").thenReturn("")
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testReturnsFailureWhenGameIdIsInvalid(self):
		when(self.requestDataAccessor).get("gameId").thenReturn("foo")
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testReturnsFailureWhenGameNotFound(self):
		when(self.requestDataAccessor).get("gameId").thenReturn(self.gameId + 1)
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : False}))
