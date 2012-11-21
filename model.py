from google.appengine.ext import ndb

class PlayerModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)

class GameModel(ndb.Model):
	gameId = ndb.IntegerProperty(required=True)
	serializedGame = ndb.JsonProperty(default='')
	playerId = ndb.StringProperty(repeated=True)
	teams = ndb.JsonProperty()

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

	PAGE_SIZE = 10
	MAX_PAGES = 5

	def getGamesForPlayerId(self, playerId):
		query = self._getQuery(playerId)
		models = []
		results = query.fetch(GameModelFinder.PAGE_SIZE)
		numPages = 0
		while 0 < len(results) and GameModelFinder.MAX_PAGES > numPages:
			models.extend(results)
			results = query.fetch(GameModelFinder.PAGE_SIZE)
			numPages += 1;
		return models

	def _getQuery(self, playerId):
		return GameModel.query(GameModel.playerId == playerId)

	def getGameByGameId(self, gameId):
		return self._getGameIdQuery(gameId).get()

	def _getGameIdQuery(self, gameId):
		return GameModel.query(GameModel.gameId == gameId)
