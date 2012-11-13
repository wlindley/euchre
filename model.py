from google.appengine.ext import ndb

class PlayerModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)

class GameModel(ndb.Model):
	gameId = ndb.IntegerProperty(required=True)
	serializedGame = ndb.JsonProperty()
	playerId = ndb.StringProperty(repeated=True)

class GameIdModel(ndb.Model):
	nextGameId = ndb.IntegerProperty(default=0)
