#!/usr/bin/env python
import testhelper
import json
import random
from mockito import *

import src.euchre

from src import executable
from src import util
from src import model
from src import euchre
from src import game
from src import serializer
from src import retriever

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

	def testCallsSelectTrumpExecutableWhenActionIsSelectTrump(self):
		self._runTestForAction("selectTrump", "SelectTrumpExecutable")

	def testCallsPlayCardExecutableWhenActionIsPlayCard(self):
		self._runTestForAction("playCard", "PlayCardExecutable")

	def testCallsDiscardExecutableWhenActionIsDiscard(self):
		self._runTestForAction("discard", "DiscardExecutable")

	def testCallsGetNameExecutableWhenActionIsGetName(self):
		self._runTestForAction("getName", "GetNameExecutable")

	def testCallsRemoveCompletedGameExecutableWhenActionIsDismissCompletedGame(self):
		self._runTestForAction("dismissCompletedGame", "RemoveCompletedGameExecutable")

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
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		self.turnRetriever = testhelper.createSingletonMock(retriever.TurnRetriever)
		self.testObj = executable.ListGamesExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def testExecuteReturnsCorrectGameData(self):
		NUM_GAMES = 4
		playerId = "2854"
		when(self.requestDataAccessor).get("playerId").thenReturn(playerId)
		participatingPlayerIds = [playerId, "54321", "8976", "12345"]
		teams = [[playerId, "54321"], ["8976", "12345"]]

		serializedGames = []
		gameIds = []
		gameModels = []
		games = []
		sequences = []
		currentTurns = []
		for i in range(NUM_GAMES):
			serializedGames.append("serialized game %s" % i)
			gameIds.append(str(i * 1000))
			gameModels.append(testhelper.createMock(model.GameModel))
			games.append(testhelper.createMock(euchre.Game))
			sequences.append(testhelper.createMock(euchre.Sequence))
			currentTurns.append(participatingPlayerIds[i % len(participatingPlayerIds)])
		sequenceStates = [euchre.Sequence.STATE_TRUMP_SELECTION, euchre.Sequence.STATE_PLAYING_ROUND, euchre.Sequence.STATE_TRUMP_SELECTION_2, euchre.Sequence.STATE_TRUMP_SELECTION]
		statuses = ["trump_selection", "round_in_progress", "trump_selection_2", "waiting_for_more_players"]
		currentTurns[3] = None

		when(self.gameModelFinder).getGamesForPlayerId(playerId).thenReturn(gameModels)

		for i in range(NUM_GAMES):
			gameModels[i].playerId = participatingPlayerIds
			gameModels[i].teams = json.dumps(teams)
			gameModels[i].gameId = gameIds[i]
			gameModels[i].serializedGame = serializedGames[i]
			when(self.gameSerializer).deserialize(serializedGames[i]).thenReturn(games[i])
			when(games[i]).getSequence().thenReturn(sequences[i])
			when(sequences[i]).getState().thenReturn(sequenceStates[i])
			when(self.turnRetriever).retrieveTurn(games[i], playerId).thenReturn(currentTurns[i])
		gameModels[3].playerId = gameModels[3].playerId[:2]
		gameModels[3].teams = json.dumps([teams[0]])
		gameModels[3].serializedGame = ""
		
		self.testObj.execute()

		expectedResponse = {
			"success" : True,
			"games" : []
		}

		for i in range(NUM_GAMES):
			expectedResponse["games"].append({
				"gameId" : gameModels[i].gameId,
				"teams" : teams,
				"status" : statuses[i],
				"currentPlayerId" : currentTurns[i]
			})
		expectedResponse["games"][3]["teams"] = [teams[0]]

		verify(self.responseWriter).write(json.dumps(expectedResponse, sort_keys=True))

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
		when(src.euchre.Game).getInstance(any(list), expectedTeams).thenReturn(gameObj)
		serializedGame = "correct game serialized"
		when(self.gameSerializer).serialize(gameObj).thenReturn(serializedGame)

		self.testObj.execute()

		verify(gameObj).startGame()
		self.assertEqual(serializedGame, self.gameModel.serializedGame)
		verify(self.gameModel).put()
		self._assertResponseResult(True)

	def testExecuteInterleavesPlayersFromDifferentTeamsWhenStartingAGame(self):
		self.existingPlayerIds.append("3")
		self.existingTeams[0].append("3")
		self.gameModel.playerId = self.existingPlayerIds
		self.gameModel.teams = json.dumps(self.existingTeams)
		expectedPlayerIds, self.expectedTeams = self._trainPlayerIdAndTeam("4", 1)

		gameObj = testhelper.createMock(euchre.Game)
		self.wasCalled = False
		def verifyPlayerOrderAndMembership(players, teams):
			self.wasCalled = True
			self.assertNotEqual(players[0].playerId in teams[0], players[1].playerId in teams[0])
			self.assertNotEqual(players[1].playerId in teams[0], players[2].playerId in teams[0])
			self.assertNotEqual(players[2].playerId in teams[0], players[3].playerId in teams[0])
			self.assertNotEqual(players[3].playerId in teams[0], players[0].playerId in teams[0])
			for i in range(4):
				self.assertTrue(players[i].playerId in teams[0] or players[i].playerId in teams[1])
			self.assertEqual(self.expectedTeams, teams)
			return gameObj

		testhelper.replaceClass(src.euchre, "Game", testhelper.createSimpleMock())
		src.euchre.Game.getInstance = verifyPlayerOrderAndMembership

		self.testObj.execute()

		self.assertTrue(self.wasCalled)

class GetGameDataExecutableTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = executable.GetGameDataExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

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
		self.turnRetriever = testhelper.createSingletonMock(retriever.TurnRetriever)
		self.handRetriever = testhelper.createSingletonMock(retriever.HandRetriever)
		self.gameObj = testhelper.createMock(euchre.Game)
		self.serializedGame = "a serialized game"
		self.gameModel.serializedGame = self.serializedGame
		when(self.gameSerializer).deserialize(self.serializedGame).thenReturn(self.gameObj)
		self.sequence = testhelper.createMock(euchre.Sequence)
		when(self.gameObj).getSequence().thenReturn(self.sequence)

		self.upCard = euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_ACE)
		self.upCardRetriever = testhelper.createSingletonMock(retriever.UpCardRetriever)
		when(self.upCardRetriever).retrieveUpCard(self.gameObj).thenReturn(self.upCard)

		self.dealer = "123456"
		self.dealerRetriever = testhelper.createSingletonMock(retriever.DealerRetriever)
		when(self.dealerRetriever).retrieveDealer(self.gameObj).thenReturn(self.dealer)

		self.gameStatus = "gamiest of statuses"
		self.gameStatusRetriever = testhelper.createSingletonMock(retriever.GameStatusRetriever)
		when(self.gameStatusRetriever).retrieveGameStatus(self.gameObj).thenReturn(self.gameStatus)

		self.ledSuit = random.randint(1, 4)
		self.ledSuitRetriever = testhelper.createSingletonMock(retriever.LedSuitRetriever)
		when(self.ledSuitRetriever).retrieveLedSuit(self.gameObj).thenReturn(self.ledSuit)

		self.currentTrick = "lots of trick data"
		self.currentTrickRetriever = testhelper.createSingletonMock(retriever.CurrentTrickRetriever)
		when(self.currentTrickRetriever).retrieveCurrentTrick(self.gameObj).thenReturn(self.currentTrick)

		self.trump = random.randint(1, 4)
		self.trumpRetriever = testhelper.createSingletonMock(retriever.TrumpRetriever)
		when(self.trumpRetriever).retrieveTrump(self.gameObj).thenReturn(self.trump)

		self.playerIds = [self.playerId, "65432", "21098", "87654"]
		self.teams = [0, 0, 1, 1]
		random.shuffle(self.teams)
		self.expectedTeams = [[], []]
		self.teamRetriever = testhelper.createSingletonMock(retriever.TeamRetriever)
		for i in range(len(self.playerIds)):
			when(self.teamRetriever).retrieveTeamByPlayerId(self.gameObj, self.playerIds[i]).thenReturn(self.teams[i])
			self.expectedTeams[self.teams[i]].append(self.playerIds[i])
		when(self.teamRetriever).retrieveTeamLists(self.gameObj).thenReturn(self.expectedTeams)

		self.gameScores = [random.randint(0, 11), random.randint(0, 11)]
		self.roundScores = [random.randint(0, 5), random.randint(0, 5)]
		self.scoreRetriever = testhelper.createSingletonMock(retriever.ScoreRetriever)
		when(self.scoreRetriever).retrieveGameScores(self.gameObj).thenReturn(self.gameScores)
		when(self.scoreRetriever).retrieveRoundScores(self.gameObj).thenReturn(self.roundScores)

		self.trickLeader = self.playerIds[random.randrange(0, len(self.playerIds))]
		self.trickLeaderRetriever = testhelper.createSingletonMock(retriever.TrickLeaderRetriever)
		when(self.trickLeaderRetriever).retrieveTrickLeader(self.gameObj).thenReturn(self.trickLeader)

		self.hand = [euchre.Card(suit=random.randint(1, 4), value=random.randint(9, 14)), euchre.Card(suit=random.randint(1, 4), value=random.randint(9, 14))]
		when(self.handRetriever).retrieveHand(self.playerId, self.gameObj).thenReturn(self.hand)

		when(self.turnRetriever).retrieveTurn(self.gameObj, self.playerId).thenReturn(self.playerId)

		self.previousTrick = "the most previous of tricks"
		self.previousTrickRetriever = testhelper.createSingletonMock(retriever.PreviousTrickRetriever)
		when(self.previousTrickRetriever).retrievePreviousTrick(self.gameObj).thenReturn(self.previousTrick)

		self._buildTestObj()

	def _verifyCorrectResponse(self):
		expectedUpCard = None
		if None != self.upCard:
			expectedUpCard = {"suit" : self.upCard.suit, "value" : self.upCard.value}
		verify(self.responseWriter).write(json.dumps({
			"success" : True,
			"playerIds" : self.playerIds,
			"gameId" : self.gameId,
			"status" : self.gameStatus,
			"teams" : self.expectedTeams,
			"scores" : self.gameScores,
			"round" : {
				"tricksTaken" : self.roundScores,
				"trump" : self.trump,
				"upCard" : expectedUpCard,
				"dealerId" : self.dealer,
				"hand": [{"suit" : card.suit, "value" : card.value} for card in self.hand],
				"currentPlayerId" : self.playerId,
				"currentTrick" : {
					"ledSuit" : self.ledSuit,
					"playedCards" : self.currentTrick,
					"leaderId" : self.trickLeader
				}
			},
			"previousTrick" : self.previousTrick
		}, sort_keys=True))

	def testReturnsCorrectDataWhenCalledWithValidData(self):
		self.gameModel.playerId = self.playerIds

		self.testObj.execute()

		self._verifyCorrectResponse()

	def testReturnsCorrectDataWhenCalledWithValidDataAndUpCardIsNone(self):
		self.upCard = None
		retriever.UpCardRetriever.instance = None
		self.upCardRetriever = testhelper.createSingletonMock(retriever.UpCardRetriever)
		when(self.upCardRetriever).retrieveUpCard().thenReturn(self.upCard)
		self._buildTestObj()
		
		self.gameModel.playerId = self.playerIds

		self.testObj.execute()

		self._verifyCorrectResponse()

	def testReturnsFailureWhenGameNotStartedYet(self):
		self.gameModel.serializedGame = ""
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

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

class SelectTrumpExecutableTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = executable.SelectTrumpExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)

		self.gameId = 45678
		self.playerId = "1230982304"
		self.suit = euchre.SUIT_HEARTS
		when(self.requestDataAccessor).get("gameId").thenReturn(str(self.gameId))
		when(self.requestDataAccessor).get("playerId").thenReturn(self.playerId)
		when(self.requestDataAccessor).get("suit").thenReturn(str(self.suit))

		self.player = game.Player.getInstance(self.playerId)

		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModel = testhelper.createMock(model.GameModel)
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)

		self.game = testhelper.createSingletonMock(euchre.Game)
		self.sequenceState = euchre.Sequence.STATE_TRUMP_SELECTION
		when(self.game).getSequenceState().thenReturn(self.sequenceState)

		self.serializedGame = "a super serialized game"
		self.postSerializedGame = "a slightly different serialized game"
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		when(self.gameSerializer).deserialize(self.serializedGame).thenReturn(self.game)
		when(self.gameSerializer).serialize(self.game).thenReturn(self.postSerializedGame)

		self.upCard = euchre.Card(suit=random.randint(1, 4), value=random.randint(9, 14))
		self.upCardRetriever = testhelper.createSingletonMock(retriever.UpCardRetriever)
		when(self.upCardRetriever).retrieveUpCard(self.game).thenReturn(self.upCard)

		self.dealerId = "09876543"
		self.dealerPlayer = game.Player.getInstance(self.dealerId)
		self.dealerRetriever = testhelper.createSingletonMock(retriever.DealerRetriever)
		when(self.dealerRetriever).retrieveDealer(self.game).thenReturn(self.dealerId)

		testhelper.replaceClass(src.game, "Player", testhelper.createSimpleMock())
		when(src.game.Player).getInstance(self.playerId).thenReturn(self.player)
		when(src.game.Player).getInstance(self.dealerId).thenReturn(self.dealerPlayer)

		self._buildTestObj()

	def _verifyCorrectResponse(self, expectedSuit):
		self.assertEqual(self.postSerializedGame, self.gameModel.serializedGame)
		inorder.verify(self.game).getSequenceState() #just to satisfy the way inorder works
		inorder.verify(self.game).addCardToHand(self.dealerPlayer, self.upCard)
		inorder.verify(self.game).selectTrump(self.player, expectedSuit)
		inorder.verify(self.gameModel).put()
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteCorrectlySelectsTrumpWhenValidDataIsPassedIn(self):
		self.gameModel.serializedGame = self.serializedGame

		self.testObj.execute()

		self._verifyCorrectResponse(self.suit)

	def testExecuteCorrectlySelectsSuitNoneWhenSelectedSuitIsNoneAndDoesNotAddCard(self):
		when(self.requestDataAccessor).get("suit").thenReturn(None)
		self.gameModel.serializedGame = self.serializedGame

		self.testObj.execute()

		self.assertEqual(self.postSerializedGame, self.gameModel.serializedGame)
		inorder.verify(self.game).getSequenceState() #just to satisfy the way inorder works
		inorder.verify(self.game).selectTrump(self.player, euchre.SUIT_NONE)
		inorder.verify(self.gameModel).put()
		verify(self.game, never).addCardToHand(any(), any())
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteDoeNotAddCardIfInTrumpSelection2(self):
		self.sequenceState = euchre.Sequence.STATE_TRUMP_SELECTION_2
		when(self.game).getSequenceState().thenReturn(self.sequenceState)
		self.gameModel.serializedGame = self.serializedGame

		self.testObj.execute()

		self.assertEqual(self.postSerializedGame, self.gameModel.serializedGame)
		inorder.verify(self.game).getSequenceState() #just to satisfy the way inorder works
		inorder.verify(self.game).selectTrump(self.player, self.suit)
		inorder.verify(self.gameModel).put()
		verify(self.game, never).addCardToHand(any(), any())
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteWritesFailureIfPlayerIdIsMissing(self):
		when(self.requestDataAccessor).get("playerId").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameIdIsMissing(self):
		when(self.requestDataAccessor).get("gameId").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenGameIdIsInvalid(self):
		when(self.requestDataAccessor).get("gameId").thenReturn("bar")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameModelNotFound(self):
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameSerializer)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenThereIsAGameExceptionWhileSelectingTrump(self):
		self.gameModel.serializedGame = self.serializedGame
		when(self.game).selectTrump(self.player, self.suit).thenRaise(game.GameException("some exception"))
		self.testObj.execute()
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

class PlayCardExecutableTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = executable.PlayCardExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)

		self.gameId = 45678
		self.playerId = "1230982304"
		self.cardValue = random.randrange(9, 15)
		self.cardSuit = random.randrange(1, euchre.NUM_SUITS + 1)
		when(self.requestDataAccessor).get("gameId").thenReturn(str(self.gameId))
		when(self.requestDataAccessor).get("playerId").thenReturn(self.playerId)
		when(self.requestDataAccessor).get("suit").thenReturn(str(self.cardSuit))
		when(self.requestDataAccessor).get("value").thenReturn(str(self.cardValue))

		self.player = game.Player(self.playerId)
		testhelper.replaceClass(src.game, "Player", testhelper.createSimpleMock())
		when(src.game.Player).getInstance(self.playerId).thenReturn(self.player)

		self.card = euchre.Card(self.cardSuit, self.cardSuit)
		testhelper.replaceClass(src.euchre, "Card", testhelper.createSimpleMock())
		when(src.euchre.Card).getInstance(self.cardSuit, self.cardValue).thenReturn(self.card)

		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModel = testhelper.createMock(model.GameModel)
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)

		self.game = testhelper.createSingletonMock(euchre.Game)
		self.serializedGame = "a super serialized game"
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		when(self.gameSerializer).deserialize(self.serializedGame).thenReturn(self.game)

		self._buildTestObj()

	def testExecuteCorrectlyPlaysCardWhenValidDataIsPassedIn(self):
		postSerializedGame = "a slightly different serialized game"
		when(self.gameSerializer).serialize(self.game).thenReturn(postSerializedGame)
		self.gameModel.serializedGame = self.serializedGame

		self.testObj.execute()

		self.assertEqual(postSerializedGame, self.gameModel.serializedGame)
		inorder.verify(self.game).playCard(self.player, self.card)
		inorder.verify(self.gameModel).put()
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteWritesFailureIfPlayerIdIsMissing(self):
		when(self.requestDataAccessor).get("playerId").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameIdIsMissing(self):
		when(self.requestDataAccessor).get("gameId").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenGameIdIsInvalid(self):
		when(self.requestDataAccessor).get("gameId").thenReturn("bar")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfSuitIsMissing(self):
		when(self.requestDataAccessor).get("suit").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenSuitIsInvalid(self):
		when(self.requestDataAccessor).get("suit").thenReturn("bing")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfValueIsMissing(self):
		when(self.requestDataAccessor).get("value").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenValueIsInvalid(self):
		when(self.requestDataAccessor).get("value").thenReturn("baz")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameModelNotFound(self):
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameSerializer)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenThereIsAGameExceptionWhilePlayingCard(self):
		self.gameModel.serializedGame = self.serializedGame
		when(self.game).playCard(self.player, self.card).thenRaise(game.GameException("some exception"))
		self.testObj.execute()
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

class DiscardExecutableTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = executable.DiscardExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)

		self.gameId = 45678
		self.playerId = "1230982304"
		self.cardValue = random.randrange(9, 15)
		self.cardSuit = random.randrange(1, euchre.NUM_SUITS + 1)
		when(self.requestDataAccessor).get("gameId").thenReturn(str(self.gameId))
		when(self.requestDataAccessor).get("playerId").thenReturn(self.playerId)
		when(self.requestDataAccessor).get("suit").thenReturn(str(self.cardSuit))
		when(self.requestDataAccessor).get("value").thenReturn(str(self.cardValue))

		self.player = game.Player(self.playerId)
		testhelper.replaceClass(src.game, "Player", testhelper.createSimpleMock())
		when(src.game.Player).getInstance(self.playerId).thenReturn(self.player)

		self.card = euchre.Card(self.cardSuit, self.cardSuit)
		testhelper.replaceClass(src.euchre, "Card", testhelper.createSimpleMock())
		when(src.euchre.Card).getInstance(self.cardSuit, self.cardValue).thenReturn(self.card)

		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModel = testhelper.createMock(model.GameModel)
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)

		self.game = testhelper.createSingletonMock(euchre.Game)
		self.serializedGame = "a super serialized game"
		self.postSerializedGame = "a slightly different serialized game"
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		when(self.gameSerializer).deserialize(self.serializedGame).thenReturn(self.game)
		when(self.gameSerializer).serialize(self.game).thenReturn(self.postSerializedGame)

		self._buildTestObj()

	def testExecuteCallsDiscardOnGameAndWritesSuccess(self):
		self.gameModel.serializedGame = self.serializedGame
		self.testObj.execute()
		self.assertEqual(self.postSerializedGame, self.gameModel.serializedGame)
		inorder.verify(self.game).discardCard(self.player, self.card)
		inorder.verify(self.gameModel).put()
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteWritesFailureIfPlayerIdIsMissing(self):
		when(self.requestDataAccessor).get("playerId").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameIdIsMissing(self):
		when(self.requestDataAccessor).get("gameId").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenGameIdIsInvalid(self):
		when(self.requestDataAccessor).get("gameId").thenReturn("bar")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfSuitIsMissing(self):
		when(self.requestDataAccessor).get("suit").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenSuitIsInvalid(self):
		when(self.requestDataAccessor).get("suit").thenReturn("bing")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfValueIsMissing(self):
		when(self.requestDataAccessor).get("value").thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenValueIsInvalid(self):
		when(self.requestDataAccessor).get("value").thenReturn("baz")
		self.testObj.execute()
		verifyZeroInteractions(self.gameModelFinder)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameModelNotFound(self):
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(None)
		self.testObj.execute()
		verifyZeroInteractions(self.gameSerializer)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenThereIsAGameExceptionWhilePlayingCard(self):
		self.gameModel.serializedGame = self.serializedGame
		when(self.game).discardCard(self.player, self.card).thenRaise(game.GameException("some exception"))
		self.testObj.execute()
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

class GetNameExecutableTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = executable.GetNameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)

		self.playerId = "123456"
		when(self.requestDataAccessor).get("playerId").thenReturn(str(self.playerId))

		self._buildTestObj();

	def testExecuteReturnsExpectedData(self):
		expectedName = "Player " + self.playerId
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : True, "playerId" : self.playerId, "name" : expectedName}, sort_keys=True))

	def testExecuteWritesFailureIfPlayerIdIsMissing(self):
		when(self.requestDataAccessor).get("playerId").thenReturn(None)
		self.testObj.execute()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

class RemoveCompletedGameExecutableTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = executable.RemoveCompletedGameExecutable.getInstance(self.requestDataAccessor, self.responseWriter)

	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)

		self.gameId = 15
		when(self.requestDataAccessor).get("gameId").thenReturn(self.gameId)

		self.playerId = "a2bc345"
		when(self.requestDataAccessor).get("playerId").thenReturn(self.playerId)

		self.playerIds = [self.playerId, "432sb", "ad938", "23amr9"]

		self.gameModelFinder = testhelper.createSingletonMock(model.GameModelFinder)
		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.playerId = self.playerIds
		self.gameModel.readyToRemove = []
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(self.gameModel)

		self.game = testhelper.createSingletonMock(euchre.Game)
		self.serializedGame = "a super serialized game"
		self.gameModel.serializedGame = self.serializedGame
		self.gameSerializer = testhelper.createSingletonMock(serializer.GameSerializer)
		when(self.gameSerializer).deserialize(self.serializedGame).thenReturn(self.game)
		when(self.game).isGameComplete().thenReturn(True)

		self._buildTestObj()

	def _verifyReadyToRemoveDidNotChange(self):
		self.assertEqual([], self.gameModel.readyToRemove)
		verify(self.gameModel, never).put()

	def testExecuteWritesFailureIfGameIsNotComplete(self):
		when(self.game).isGameComplete().thenReturn(False)
		self.testObj.execute()
		self._verifyReadyToRemoveDidNotChange()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteAddsIdToRemoveListIfGameIsComplete(self):
		self.assertFalse(self.playerId in self.gameModel.readyToRemove)
		self.testObj.execute()
		self.assertTrue(self.playerId in self.gameModel.readyToRemove)
		verify(self.gameModel).put()
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteDeletesGameIfEveryInGameIsReadyToRemoveIt(self):
		self.gameModel.readyToRemove = self.playerIds[1:]
		self.testObj.execute()
		verify(self.gameModelFinder).deleteGame(self.gameId)
		verify(self.gameModel, never).put()
		verify(self.responseWriter).write(json.dumps({"success" : True}))

	def testExecuteDoesNotAddIdIfItIsAlreadyPresent(self):
		expectedReadyToRemove = [self.playerId]
		self.gameModel.readyToRemove = expectedReadyToRemove
		self.testObj.execute()
		self.assertEqual(expectedReadyToRemove, self.gameModel.readyToRemove)
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteDoesNotAddIdIfItIsNotAPlayer(self):
		self.gameModel.playerId = self.playerIds[1:] + ["dali324"]
		self.testObj.execute()
		self._verifyReadyToRemoveDidNotChange()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameModelNotFound(self):
		when(self.gameModelFinder).getGameByGameId(self.gameId).thenReturn(None)
		self.testObj.execute()
		self._verifyReadyToRemoveDidNotChange()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfGameIdIsMissing(self):
		when(self.requestDataAccessor).get("gameId").thenReturn(None)
		self.testObj.execute()
		self._verifyReadyToRemoveDidNotChange()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureIfPlayerIdIsMissing(self):
		when(self.requestDataAccessor).get("playerId").thenReturn(None)
		self.testObj.execute()
		self._verifyReadyToRemoveDidNotChange()
		verify(self.responseWriter).write(json.dumps({"success" : False}))

	def testExecuteWritesFailureWhenGameIdIsInvalid(self):
		when(self.requestDataAccessor).get("gameId").thenReturn("bar")
		self.testObj.execute()
		self._verifyReadyToRemoveDidNotChange()
		verify(self.responseWriter).write(json.dumps({"success" : False}))