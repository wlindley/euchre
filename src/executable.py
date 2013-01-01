from abc import ABCMeta
from abc import abstractmethod
import json
import util
import game
import euchre
import serializer
import model
import logging
import retriever

logging.getLogger().setLevel(logging.DEBUG)

MAX_TEAM_SIZE = 2

class ExecutableFactory(object):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return ExecutableFactory(requestDataAccessor, responseWriter)

	def __init__(self, requestDataAccessor, responseWriter):
		self._requestDataAccessor = requestDataAccessor
		self._responseWriter = responseWriter
		self._executables = {
			"createGame" : CreateGameExecutable,
			"listGames" : ListGamesExecutable,
			"addPlayer" : AddPlayerExecutable,
			"getGameData" : GetGameDataExecutable,
			"selectTrump" : SelectTrumpExecutable,
			"playCard" : PlayCardExecutable
		}

	def createExecutable(self):
		action = self._requestDataAccessor.get("action")
		if action in self._executables:
			return self._executables[action].getInstance(self._requestDataAccessor, self._responseWriter)
		return DefaultExecutable.getInstance(self._requestDataAccessor, self._responseWriter)

class AbstractExecutable(object):
	__metaclass__ = ABCMeta

	def __init__(self, requestDataAccessor, responseWriter, *args, **kwargs):
		self._requestDataAccessor = requestDataAccessor
		self._responseWriter = responseWriter

	@abstractmethod
	def execute(self, *args, **kwargs):
		return None

	def _writeResponse(self, response):
		self._responseWriter.write(json.dumps(response, sort_keys=True))

class CreateGameExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return CreateGameExecutable(requestDataAccessor, responseWriter, util.GameIdTracker.getInstance(), model.GameModelFactory.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameIdTracker, gameModelFactory):
		super(CreateGameExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameIdTracker = gameIdTracker
		self._gameModelFactory = gameModelFactory

	def execute(self):
		playerId = self._requestDataAccessor.get("playerId")
		team = int(self._requestDataAccessor.get("team"))
		if 1 < team or 0 > team:
			self._writeResponse({"success" : False})
			return
		gameId = self._gameIdTracker.getGameId()
		gameModel = self._gameModelFactory.create(gameId)
		gameModel.playerId = [playerId]
		teamInfo = [[], []]
		teamInfo[team].append(playerId)
		gameModel.teams = json.dumps(teamInfo)
		gameModel.put()
		self._writeResponse({"success" : True, "gameId" : gameId})

class ListGamesExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return ListGamesExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), retriever.TurnRetriever.getInstance(), retriever.GameStatusRetriever.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder, gameSerializer, turnRetriever, gameStatusRetriever):
		super(ListGamesExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer
		self._turnRetriever = turnRetriever
		self._gameStatusRetriever = gameStatusRetriever

	def execute(self):
		playerId = self._requestDataAccessor.get("playerId")
		gameModels = self._gameModelFinder.getGamesForPlayerId(playerId)
		gameDatas = [self._buildGameData(playerId, gameModel) for gameModel in gameModels]
		self._writeResponse({"games" : gameDatas, "success" : True})

	def _buildGameData(self, playerId, gameModel):
		gameData = {
			"gameId" : gameModel.gameId,
			"playerIds" : gameModel.playerId
		}
		if None == gameModel.serializedGame or "" == gameModel.serializedGame:
			gameData["status"] = self._gameStatusRetriever.retrieveGameStatus(None)
			gameData["currentPlayerId"] = None
		else:
			gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
			gameData["status"] = self._gameStatusRetriever.retrieveGameStatus(gameObj)
			gameData["currentPlayerId"] = self._turnRetriever.retrieveTurn(gameObj)
		return gameData

class DefaultExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return DefaultExecutable(requestDataAccessor, responseWriter)

	def execute(self):
		self._writeResponse({})

class AddPlayerExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return AddPlayerExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder, gameSerializer):
		super(AddPlayerExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		try:
			gameId = int(self._requestDataAccessor.get("gameId"))
			team = int(self._requestDataAccessor.get("team"))
		except ValueError:
			logging.info("Non-integer gameId (%s) or team (%s) specified" % (self._requestDataAccessor.get("gameId"), self._requestDataAccessor.get("team")))
			self._writeResponse({"success" : False})
			return
		playerId = self._requestDataAccessor.get("playerId")
		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel or playerId in gameModel.playerId or 1 < team or 0 > team:
			logging.info("No game found for gameId %s or player %s is already in game or invalid team of %s specified" % (gameId, playerId, team))
			self._writeResponse({"success" : False})
			return
		teamInfo = json.loads(gameModel.teams)
		if MAX_TEAM_SIZE <= len(teamInfo[team]):
			logging.info("Player %s cannot join game %s because it is already full" % (playerId, gameId))
			self._writeResponse({"success" : False})
			return
		gameModel.playerId.append(playerId)
		teamInfo[team].append(playerId)
		gameModel.teams = json.dumps(teamInfo)
		if MAX_TEAM_SIZE == len(teamInfo[0]) and MAX_TEAM_SIZE == len(teamInfo[1]):
			players = [game.Player(pid) for pid in gameModel.playerId]
			gameObj = euchre.Game.getInstance(players, teamInfo)
			gameObj.startGame()
			gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		gameModel.put()
		self._writeResponse({"success" : True})

class GetGameDataExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return GetGameDataExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), retriever.TurnRetriever.getInstance(), retriever.HandRetriever.getInstance(), retriever.UpCardRetriever.getInstance(), retriever.DealerRetriever.getInstance(), retriever.GameStatusRetriever.getInstance(), retriever.LedSuitRetriever.getInstance(), retriever.CurrentTrickRetriever.getInstance(), retriever.TrumpRetriever.getInstance(), retriever.TeamRetriever.getInstance(), retriever.ScoreRetriever.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder, gameSerializer, turnRetriever, handRetriever, upCardRetriever, dealerRetriever, gameStatusRetriever, ledSuitRetriever, currentTrickRetriever, trumpRetriever, teamRetriever, scoreRetriever):
		super(GetGameDataExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer
		self._turnRetriever = turnRetriever
		self._handRetriever = handRetriever
		self._upCardRetriever = upCardRetriever
		self._dealerRetriever = dealerRetriever
		self._gameStatusRetriever = gameStatusRetriever
		self._ledSuitRetriever = ledSuitRetriever
		self._currentTrickRetriever = currentTrickRetriever
		self._trumpRetriever = trumpRetriever
		self._teamRetriever = teamRetriever
		self._scoreRetriever = scoreRetriever

	def execute(self):
		playerId = self._requestDataAccessor.get("playerId")
		try:
			gameId = int(self._requestDataAccessor.get("gameId"))
		except ValueError:
			self._writeResponse({"success" : False})
			return

		if "" == playerId:
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)

		if None == gameModel or None == gameModel.serializedGame or "" == gameModel.serializedGame:
			self._writeResponse({"success" : False})
			return

		response = {
			"success" : True
		}

		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
		response["playerIds"] = gameModel.playerId
		response["gameId"] = gameId
		response["status"] = self._gameStatusRetriever.retrieveGameStatus(gameObj)
		response["teams"] = self._teamRetriever.retrieveTeamLists(gameObj)
		response["scores"] = self._scoreRetriever.retrieveGameScores(gameObj)
		response["round"] = self._getRoundData(gameObj, playerId)
		self._writeResponse(response)

	def _getRoundData(self, gameObj, playerId):
		roundData = {}
		upCard = self._upCardRetriever.retrieveUpCard(gameObj)
		roundData["tricksTaken"] = self._scoreRetriever.retrieveRoundScores(gameObj)
		roundData["trump"] = self._trumpRetriever.retrieveTrump(gameObj)
		roundData["upCard"] = {"suit" : upCard.suit, "value" : upCard.value} if None != upCard else None
		roundData["dealerId"] = self._dealerRetriever.retrieveDealer(gameObj)
		roundData["hand"] = self._convertHand(self._handRetriever.getHand(playerId, gameObj))
		roundData["currentPlayerId"] = self._turnRetriever.retrieveTurn(gameObj)
		roundData["currentTrick"] = self._getCurrentTrickData(gameObj)
		return roundData

	def _getCurrentTrickData(self, gameObj):
		trickData = {}
		trickData["ledSuit"] = self._ledSuitRetriever.retrieveLedSuit(gameObj)
		trickData["playedCards"] = self._currentTrickRetriever.retrieveCurrentTrick(gameObj)
		return trickData

	def _convertHand(self, hand):
		return [{"suit" : card.suit, "value" : card.value} for card in hand]

class SelectTrumpExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return SelectTrumpExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder, gameSerializer):
		super(SelectTrumpExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		gameId = self._requestDataAccessor.get("gameId")
		playerId = self._requestDataAccessor.get("playerId")
		suit = self._requestDataAccessor.get("suit")

		if None == gameId or None == playerId:
			logging.info("Missing game id or player id")
			self._writeResponse({"success" : False})
			return

		if None == suit:
			suit = euchre.SUIT_NONE

		try:
			gameId = int(gameId)
			suit = int(suit)
		except ValueError:
			logging.info("Invalid game id (%s) or suit (%s)" % (gameId, suit))
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel:
			logging.info("Could not find game model for id %s" % gameId)
			self._writeResponse({"success" : False})
			return

		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
		try:
			gameObj.selectTrump(game.Player.getInstance(playerId), suit)
		except game.GameException as e:
			logging.info("Error while setting trump (player id: %s, game id: %s, suit: %s): %s" % (playerId, gameId, suit, e))
			self._writeResponse({"success" : False})
			return

		gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		gameModel.put()

		self._writeResponse({"success" : True})

class PlayCardExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return PlayCardExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder, gameSerializer):
		super(PlayCardExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		playerId = self._requestDataAccessor.get("playerId")
		gameId = self._requestDataAccessor.get("gameId")
		cardSuit = self._requestDataAccessor.get("suit")
		cardValue = self._requestDataAccessor.get("value")
		if None == playerId or None == gameId or None == cardSuit or None == cardValue:
			logging.info("One of the required parameters (player id, game id, card suit, and card value) was not specified")
			self._writeResponse({"success" : False})
			return
		try:
			gameId = int(gameId)
			cardSuit = int(cardSuit)
			cardValue = int(cardValue)
		except ValueError:
			logging.info("Error parsing integer for game id (%s), card suit (%s), or card value (%s)" % (gameId, cardSuit, cardValue))
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel:
			logging.info("Could not find game model for game id: %s" % gameId)
			self._writeResponse({"success" : False})
			return
		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)

		player = game.Player.getInstance(playerId)
		card = euchre.Card.getInstance(cardSuit, cardValue)
		try:
			gameObj.playCard(player, card)
		except game.GameException as e:
			logging.info("Error while player %s tried to play card %s in game %s: %s" % (player, card, gameId, e))
			self._writeResponse({"success" : False})
			return

		gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		gameModel.put()
		self._writeResponse({"success" : True})
