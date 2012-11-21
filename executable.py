from abc import ABCMeta
from abc import abstractmethod
import json
import util
import game
import euchre
import serializer
import model

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
			"startGame" : StartGameExecutable
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
		gameId = self._gameIdTracker.getGameId()
		playerIds = [self._requestDataAccessor.get("playerId")]
		players = [game.Player(pid) for pid in playerIds]
		teams = self._requestDataAccessor.get("teams")
		gameModel = self._gameModelFactory.create(gameId)
		gameModel.playerId = playerIds
		gameModel.put()
		self._responseWriter.write(json.dumps({"gameId" : gameId}))

class ListGamesExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return ListGamesExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder):
		super(ListGamesExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder

	def execute(self):
		playerId = self._requestDataAccessor.get("playerId")
		gameModels = self._gameModelFinder.getGamesForPlayerId(playerId)
		gameIds = [model.gameId for model in gameModels]
		self._responseWriter.write(json.dumps({"gameIds" : gameIds}))

class StartGameExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return StartGameExecutable(requestDataAccessor, responseWriter, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance())

	REQUIRED_NUM_PLAYERS = 4 
	def __init__(self, requestDataAccessor, responseWriter, gameModelFinder, gameSerializer):
		super(StartGameExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		gameId = self._requestDataAccessor.get("gameId")
		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel or '' != gameModel.serializedGame or StartGameExecutable.REQUIRED_NUM_PLAYERS != len(gameModel.playerId):
			self._responseWriter.write(json.dumps({"success" : False}))
			return
		playerIds = gameModel.playerId
		teams = json.loads(gameModel.teams)
		gameObj = euchre.Game.getInstance([game.Player(pid) for pid in playerIds], teams)
		gameObj.startGame()
		gameModel.serializedGame = json.dumps(self._gameSerializer.serialize(gameObj))
		gameModel.put()
		self._responseWriter.write(json.dumps({"success" : True}))

class DefaultExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return DefaultExecutable(requestDataAccessor, responseWriter)

	def execute(self):
		self._responseWriter.write(json.dumps({}))
