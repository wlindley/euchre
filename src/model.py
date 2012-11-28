from google.appengine.ext import ndb

class PlayerModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)

class GameModel(ndb.Model):
	gameId = ndb.IntegerProperty(required=True)
	serializedGame = ndb.JsonProperty(default='')
	playerId = ndb.StringProperty(repeated=True)
	teams = ndb.JsonProperty()
	version = ndb.IntegerProperty(default=1)

class GameIdModel(ndb.Model):
	nextGameId = ndb.IntegerProperty(default=0)

class GameModelFactory(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFactory()

	def create(self, gameId):
		return GameModel(gameId=gameId)

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
		return self._getGameIdQuery(gameId).get()

	def _getGameIdQuery(self, gameId):
		return GameModel.query(GameModel.gameId == gameId)
