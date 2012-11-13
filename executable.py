from abc import ABCMeta
from abc import abstractmethod
import json
import util
import game
import euchre

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

	def createExecutable(self):
		action = self._requestDataAccessor.get("action")
		if "createGame" == action:
			return CreateGameExecutable.getInstance(self._requestDataAccessor, self._responseWriter)
		return None

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
		return CreateGameExecutable(requestDataAccessor, responseWriter, util.GameIdTracker.getInstance(), util.GameModelFactory.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, gameIdTracker, gameModelFactory):
		super(CreateGameExecutable, self).__init__(requestDataAccessor, responseWriter)
		self._gameIdTracker = gameIdTracker
		self._gameModelFactory = gameModelFactory

	def execute(self):
		gameId = self._gameIdTracker.getGameId()
		playerIds = self._requestDataAccessor.get("players")
		players = [game.Player(pid) for pid in playerIds]
		teams = self._requestDataAccessor.get("teams")
		gameObj = euchre.Game.getInstance(players, teams)
		gameModel = self._gameModelFactory.create(gameId)
		gameModel.playerId = playerIds
		gameModel.put()
		self._responseWriter.write(json.dumps({"gameId" : gameId}))
