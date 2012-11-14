from google.appengine.ext import ndb

class PlayerModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)

class GameModel(ndb.Model):
	gameId = ndb.IntegerProperty(required=True)
	serializedGame = ndb.JsonProperty()
	playerId = ndb.StringProperty(repeated=True)

class GameIdModel(ndb.Model):
	nextGameId = ndb.IntegerProperty(default=0)

class GameModelFinder(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFinder()

	def getGamesForPlayerId(self, playerId):
		return None

class GameModelFactory(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFactory()

	def create(self, gameId):
		return GameModel(gameId=gameId)
