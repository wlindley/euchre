from abc import ABCMeta
from abc import abstractmethod
import json
import util
import game
import euchre
import serializer
import model
import logging

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
			"addPlayer" : AddPlayerExecutable
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
		playerId = self._requestDataAccessor.get("playerId")
		team = int(self._requestDataAccessor.get("team"))
		if 1 < team or 0 > team:
			self._responseWriter.write(json.dumps({"success" : False}))
			return
		gameId = self._gameIdTracker.getGameId()
		gameModel = self._gameModelFactory.create(gameId)
		gameModel.playerId = [playerId]
		teamInfo = [[], []]
		teamInfo[team].append(playerId)
		gameModel.teams = json.dumps(teamInfo)
		gameModel.put()
		self._responseWriter.write(json.dumps({"success" : True, "gameId" : gameId}))

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
		gameDatas = [{"gameId" : model.gameId} for model in gameModels]
		self._responseWriter.write(json.dumps({"games" : gameDatas}))

class DefaultExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return DefaultExecutable(requestDataAccessor, responseWriter)

	def execute(self):
		self._responseWriter.write(json.dumps({}))

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
		gameId = self._requestDataAccessor.get("gameId")
		playerId = self._requestDataAccessor.get("playerId")
		team = self._requestDataAccessor.get("team")
		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel or playerId in gameModel.playerId or 1 < team or 0 > team:
			self._responseWriter.write(json.dumps({"success" : False}))
			return
		teamInfo = json.loads(gameModel.teams)
		if MAX_TEAM_SIZE <= len(teamInfo[team]):
			self._responseWriter.write(json.dumps({"success" : False}))
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
		self._responseWriter.write(json.dumps({"success" : True}))
