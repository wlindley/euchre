from google.appengine.ext import ndb

CURRENT_GAME_MODEL_VERSION = 3

class PlayerModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)

class GameModel(ndb.Model):
	serializedGame = ndb.JsonProperty(default='')
	playerId = ndb.StringProperty(repeated=True)
	teams = ndb.JsonProperty()
	version = ndb.IntegerProperty(default=1)
	readyToRemove = ndb.StringProperty(repeated=True)

class MatchmakingTicketModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)
	lookingForMatch = ndb.BooleanProperty(default=True)
	searchStartTime = ndb.DateTimeProperty(auto_now_add=True)

class GameModelFactory(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFactory()

	def create(self):
		return GameModel(version=CURRENT_GAME_MODEL_VERSION)

class GameModelFinder(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFinder()

	FETCH_SIZE = 50

	def getGamesForPlayerId(self, playerId):
		query = self._getQuery(playerId)
		models = query.fetch(GameModelFinder.FETCH_SIZE)
		return models

	def _getQuery(self, playerId):
		return GameModel.query(GameModel.playerId == playerId)

	def getGameByGameId(self, gameId):
		return self._getKeyByUrl(gameId).get()

	def _getGameIdQuery(self, gameId):
		return GameModel.query(GameModel.gameId == gameId)

	def _getKeyByUrl(self, urlsafe):
		return ndb.Key(urlsafe=urlsafe)

	def deleteGame(self, gameId):
		key = self._getKeyByUrl(gameId)
		if None == key:
			return False
		key.delete()
		return True

class MatchmakingTicketFinder(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return MatchmakingTicketFinder()

	def isPlayerInQueue(self, playerId):
		raise Exception("Not Yet Implemented")

	def addPlayerToQueue(self, playerId):
		raise Exception("Not Yet Implemented")

	def getMatchmakingGroup(self, numPlayers):
		raise Exception("Not Yet Implemented")